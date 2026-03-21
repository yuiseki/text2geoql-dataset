"""Generate Overpass QL with Nominatim area grounding and Taginfo tag validation.

This is v2 of the generation pipeline. It does NOT modify generate_overpassql.py
and is safe to develop while a batch using v1 is running.

Key additions over v1:
  1. Nominatim area resolution — resolves the area in the TRIDENT instruction to
     an OSM area(id:...) and injects an "Important note" into the prompt so the
     LLM uses precise area IDs instead of name-string area filters.
  2. Taginfo tag validation — after LLM generation, extracts ["key"="value"] pairs
     from the query and checks each against Taginfo. If any classifier tag has
     < min_count uses, the entry is recorded as invalid_tag without calling Overpass.
     This catches typos (e.g. "aerport") and wrong namespaces early.
"""

import re

import nominatim
import taginfo
from generate_overpassql import (
    OLLAMA_MODEL,
    DEFAULT_TEMPERATURE,
    DEFAULT_NUM_PREDICT,
    build_prompt,
    generate_overpassql,
    save_overpassql,
)
from meta import FailureMeta, GenerationMeta, model_to_slug
from overpass import fetch_elements

# Keys that carry descriptive attributes, not type classifiers — skip validation
_SKIP_VALIDATION_PREFIXES = ("name", "addr:", "ref", "contact:", "phone", "website",
                              "email", "opening_hours", "description", "note", "source",
                              "fixme", "check_date", "survey:date")

V2_SUFFIX = "-v2"


# ── Parsing helpers ───────────────────────────────────────────────────────────


def parse_full_area(instruct: str) -> str:
    """Extract the full area name from a TRIDENT AreaWithConcern instruction.

    >>> parse_full_area("AreaWithConcern: Shinjuku, Tokyo, Japan; Hotels")
    'Shinjuku, Tokyo, Japan'
    >>> parse_full_area("AreaWithConcern: Seoul, South Korea; Restaurants")
    'Seoul, South Korea'
    >>> parse_full_area("AreaWithConcern: Japan; Airports")
    'Japan'
    >>> parse_full_area("AreaWithConcern: Gangnam-gu, Seoul, South Korea; Cafes")
    'Gangnam-gu, Seoul, South Korea'
    """
    # Format: "AreaWithConcern: <area>; <concern>"
    after_colon = instruct.split(": ", 1)[1]  # "<area>; <concern>"
    return after_colon.split("; ")[0].strip()


def extract_tags_from_query(query: str) -> list[tuple[str, str]]:
    """Extract all ["key"="value"] tag pairs from an Overpass QL query.

    >>> extract_tags_from_query('nwr["amenity"="hospital"](area.inner);')
    [('amenity', 'hospital')]
    >>> extract_tags_from_query('[out:json][timeout:30];\\nout geom;')
    []
    """
    pattern = r'\["([^"]+)"="([^"]+)"\]'
    return re.findall(pattern, query)


# ── Area hint construction ────────────────────────────────────────────────────


def build_area_hint(area_id: int, area_name: str) -> str:
    """Build the Important note string to inject into the prompt.

    Includes a concrete Overpass QL snippet so the LLM learns the exact
    area(id:...) syntax (not area[id:...] which is invalid).

    >>> hint = build_area_hint(3601234567, "Shinjuku, Tokyo, Japan")
    >>> "3601234567" in hint and "Shinjuku, Tokyo, Japan" in hint
    True
    >>> "area(id:3601234567)" in hint
    True
    >>> ".searchArea" in hint
    True
    """
    return (
        f'Important note: For the area "{area_name}", '
        f"use the following exact Overpass QL syntax for the area filter: "
        f"area(id:{area_id})->.searchArea; "
        f"Then use (area.searchArea) instead of name-based area filters."
    )


def fix_area_id_syntax(query: str) -> str:
    """Correct the common LLM mistake of area[id:X] → area(id:X).

    The LLM sometimes generates area[id:...] (tag-filter syntax) instead of
    area(id:...) (element-selector syntax). This post-processor fixes it.

    >>> fix_area_id_syntax('area[id:3601234567]->.inner;')
    'area(id:3601234567)->.inner;'
    >>> fix_area_id_syntax('area(id:3601234567)->.inner;')
    'area(id:3601234567)->.inner;'
    """
    return re.sub(r'area\[id:(\d+)\]', r'area(id:\1)', query)


# ── Taginfo validation ────────────────────────────────────────────────────────


def _should_skip_validation(key: str) -> bool:
    """Return True if this key should be skipped during tag validation."""
    return any(key.startswith(prefix) for prefix in _SKIP_VALIDATION_PREFIXES)


def validate_query_tags(
    query: str,
    *,
    min_count: int = 1_000,
    taginfo_endpoint: str = taginfo.DEFAULT_ENDPOINT,
) -> list[str]:
    """Return list of "key=value" strings for tags that fail Taginfo validation.

    Tags whose keys start with name/addr:/ref/etc. are skipped as they are
    descriptive attributes rather than type classifiers.

    Returns an empty list if all classifier tags are valid.
    """
    invalid: list[str] = []
    for key, value in extract_tags_from_query(query):
        if _should_skip_validation(key):
            continue
        if not taginfo.validate_tag(key, value, min_count=min_count, endpoint=taginfo_endpoint):
            invalid.append(f"{key}={value}")
    return invalid


# ── Prompt building with Nominatim ────────────────────────────────────────────


def build_prompt_v2(
    instruct: str,
    data_dir: str = "./data",
    nominatim_endpoint: str = nominatim.DEFAULT_ENDPOINT,
) -> tuple[str, int | None]:
    """Build a Few-Shot prompt enhanced with a Nominatim area ID hint.

    Returns (prompt_str, area_id_or_None).
    When Nominatim resolves the area, the prompt includes an Important note
    with the area(id:...) value. When resolution fails, falls back to the v1
    prompt unchanged.
    """
    area_name = parse_full_area(instruct)
    relation_id = nominatim.get_osm_relation_id(area_name, endpoint=nominatim_endpoint)

    base_prompt = build_prompt(instruct, data_dir)

    if relation_id is None:
        return base_prompt, None

    area_id = nominatim.relation_to_area_id(relation_id)
    hint = build_area_hint(area_id, area_name)

    # Inject the hint just before the final "Input:" line
    enhanced_prompt = base_prompt.replace(
        f"Input:\n{instruct}\n\nOutput:",
        f"{hint}\nInput:\n{instruct}\n\nOutput:",
    )
    return enhanced_prompt, area_id


# ── Main pipeline ─────────────────────────────────────────────────────────────


def run_v2(
    base_path: str,
    data_dir: str = "./data",
    tmp_root: str = "./tmp",
    model: str = OLLAMA_MODEL,
    temperature: float = DEFAULT_TEMPERATURE,
    num_predict: int = DEFAULT_NUM_PREDICT,
    num_ctx: int | None = None,
    nominatim_endpoint: str = nominatim.DEFAULT_ENDPOINT,
    taginfo_endpoint: str = taginfo.DEFAULT_ENDPOINT,
    taginfo_min_count: int = 1_000,
) -> None:
    """Generation pipeline with Nominatim grounding and Taginfo validation.

    Output files use a '-v2' suffix to avoid collision with v1 outputs while
    the v1 batch is still running.
    """
    slug = model_to_slug(model) + V2_SUFFIX
    print("")
    print(f"base_path: {base_path}  model: {model} (v2)")

    save_path = f"{base_path}/output-{slug}.overpassql"
    if __import__("os").path.exists(save_path):
        print("OverpassQL (v2) already saved!")
        return

    not_found_path = f"{base_path}/not-found-{slug}.json"
    if __import__("os").path.exists(not_found_path):
        print("not-found (v2) already recorded!")
        return

    instruct_file = f"{base_path}/input-trident.txt"
    instruct = open(instruct_file).read().strip()
    print("instruct:", instruct)

    prompt, area_id = build_prompt_v2(
        instruct, data_dir=data_dir, nominatim_endpoint=nominatim_endpoint
    )
    if area_id is not None:
        print(f"Nominatim resolved area_id: {area_id}")
    else:
        print("Nominatim: no area_id resolved, using name-based filter")

    overpassql, failure_reason = generate_overpassql(
        prompt,
        model=model,
        temperature=temperature,
        num_predict=num_predict,
        num_ctx=num_ctx,
    )

    if overpassql is None:
        print(f"LLM generation failed: {failure_reason}")
        FailureMeta.create(model=model, reason=failure_reason, query=None).save(not_found_path)  # type: ignore[arg-type]
        return

    # Post-process: fix area[id:X] → area(id:X) if LLM used wrong syntax
    overpassql = fix_area_id_syntax(overpassql)

    print("Generated OverpassQL:\n===")
    print(overpassql)
    print("===")

    # Taginfo validation — catch bad tags before hitting Overpass
    invalid_tags = validate_query_tags(
        overpassql,
        min_count=taginfo_min_count,
        taginfo_endpoint=taginfo_endpoint,
    )
    if invalid_tags:
        reason = f"invalid_tag:{','.join(invalid_tags)}"
        print(f"Taginfo validation failed: {reason}")
        FailureMeta.create(model=model, reason=reason, query=overpassql).save(not_found_path)
        return

    import os
    import hashlib
    query_hash = hashlib.md5(overpassql.encode("utf-8")).hexdigest()
    tmp_path = os.path.join(tmp_root, query_hash)
    if os.path.exists(os.path.join(tmp_path, f"output-{slug}.overpassql")):
        print("OverpassQL (v2) already exists in tmp!")
        return

    try:
        elements = fetch_elements(overpassql)
        n = len(elements)
    except Exception as e:
        print(f"Overpass API error: {e}")
        FailureMeta.create(model=model, reason="api_error", query=overpassql).save(not_found_path)
        return

    print("number of elements:", n)

    if n > 0:
        # Save with v2 slug directly — save_overpassql uses meta.model_slug (no -v2 suffix)
        os.makedirs(base_path, exist_ok=True)
        with open(save_path, "w") as f:
            f.write(overpassql + "\n")
        meta = GenerationMeta.create(
            model=model,
            temperature=temperature,
            num_predict=num_predict,
            element_count=n,
        )
        meta_path = os.path.join(base_path, f"output-{slug}.meta.json")
        meta.save(meta_path)
        print(save_path)
    else:
        FailureMeta.create(model=model, reason="zero_results", query=overpassql).save(not_found_path)
        print(not_found_path)
