"""Generate training pairs for the TRIDENT inner layer by working backwards.

The inner layer turns a conversation into a block of labelled lines. Collecting
that pairing the obvious way means writing utterances first and hoping the
label is right. Going the other way is easier to keep correct: the label is the
seed, built by template from an (area, concern) pair the dataset already
trusts, and a large model is asked what a person would have typed to get it.

    (Taito, Tokyo) + Cafes
        -> AreaWithConcern: Taito, Tokyo, Cafes          the label, by template
        -> "台東区の喫茶店一覧"                            invented by the model

Nothing about the utterance is trusted yet, so each one is put back through
TRIDENT's own inner layer, driven by the same large model, with the real prompt
and its retrieved examples. What comes out is judged on two things:

  the area must match the seed
      A wrong place passes an Overpass check easily, because Osaka has cafes
      too. Area matching is what catches it, and it is reliable: in a six-way
      test every reconstruction recovered "Taito, Tokyo", including from
      "台東でカフェを探して", where the prefecture is not written down.

  the concern must actually find something
      The concern is free to drift. "Cafes" comes back as "Coffee shops" or
      "Cafe" more often than not, and all three are fair readings. Rather than
      arbitrate, hand the AreaWithConcern line to the deep layer and run the
      query: a concern that returns features is a concern worth learning.

This inherits a known bias. A correct answer that legitimately finds nothing —
mosques in Taito, airports in a small city — is rejected, and a model trained
only on what returns features learns to avoid rare concerns. Those pairs are
kept separately rather than thrown away, so the bias is a choice and not an
accident.

Usage:
    uv run python src/generate_inner_pairs.py --limit 3 --variants 6
"""

from __future__ import annotations

import argparse
import json
import re
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import httpx

from nominatim import get_osm_relation_id

TEACHER_URL = "http://10.108.45.102:8080/v1/chat/completions"
TRIDENT_URL = "http://127.0.0.1:3399"
OVERPASS_URL = "http://127.0.0.1:30112/api/interpreter"

DEFAULT_TIMEOUT = 300.0

# Enough to seed a reconstruction. The emoji and colour barely steer the
# utterance, so a fallback is fine where the concern is not listed.
CONCERN_STYLE: dict[str, tuple[str, str]] = {
    "Cafes": ("coffee", "brown"),
    "Restaurants": ("fork_and_knife", "pink"),
    "Hotels": ("hotel", "lightblue"),
    "Hospitals": ("hospital", "red"),
    "Schools": ("school", "orange"),
    "Parks": ("park", "green"),
    "Libraries": ("books", "purple"),
    "Bakeries": ("bread", "wheat"),
    "Pharmacies": ("pill", "lightgreen"),
    "Convenience stores": ("convenience_store", "skyblue"),
}
DEFAULT_STYLE = ("round_pushpin", "gray")

# Vocabulary that only appears in the internal format. An utterance carrying it
# is the label with a verb bolted on, and teaches the model nothing.
LEAK_TOKENS = (
    "areawithconcern",
    "emojiforconcern",
    "colorforconcern",
    "titleofmap",
    "confirmhelpful",
)

# Two things have to be spelled out, and both were learned by measuring.
#
# The count. Asked only for "half Japanese, half English", the teacher
# returned exactly two utterances every time, one of each.
#
# That the place must be named. Left to itself it writes "このあたりのカフェ",
# "cafes in this area", "coffee nearby" and "near Shibuya Station" — all
# perfectly ordinary things to type into a map app, and none of them
# recoverable, because the area they refer to is not in the words. Those were
# the largest single loss in a twenty-seed run, and no amount of leniency in
# the checking can fix an utterance that does not say where.
REVERSE_SYSTEM_TEMPLATE = (
    "You reconstruct the human utterance that a map assistant was answering. "
    "You are given the assistant's internal map definition. "
    "Output EXACTLY {n} utterances as a JSON array of {n} objects, each "
    '{{"lang":"ja"|"en","utterance":"..."}}. Count them before you answer. '
    "Every utterance must be in {lang_name}. "
    "Each utterance must be what an ordinary person would type into a map app, "
    "and each must differ from the others in wording, length and politeness. "
    "Every utterance MUST name the place from the Area line, spelled the same "
    "way it appears there. Do not translate it, do not use another name for "
    "it, and do not replace it with a landmark, a station or a district "
    "inside it. "
    "Name enough of it that a stranger to the region could tell which place "
    "is meant: if the Area line says a ward inside a city, write the city too. "
    '"Chuo Ward" and "chuo-ku" alone are not enough, because several cities '
    "have one. "
    "Do not widen it either: if the Area line names a city, do not write the "
    "prefecture instead. "
    "Never write an utterance that relies on where the person is standing: no "
    '"nearby", no "near me", no "this area", no "このあたり", no "近く". '
    "It MUST NOT contain the words Area, AreaWithConcern, Emoji, Color, or any "
    "part of the internal format."
)


LANG_NAMES = {"ja": "Japanese", "en": "English"}


def reverse_system_prompt(variants: int, lang: str = "ja") -> str:
    return REVERSE_SYSTEM_TEMPLATE.format(
        n=variants, lang_name=LANG_NAMES.get(lang, "Japanese")
    )


@dataclass(frozen=True)
class Seed:
    """One (area, concern) pair the dataset already trusts."""

    area: str
    concern: str

    @property
    def area_parts(self) -> list[str]:
        return [part.strip() for part in self.area.split(",") if part.strip()]


def build_intermediate(seed: Seed) -> str:
    """The label, assembled rather than generated."""
    emoji, color = CONCERN_STYLE.get(seed.concern, DEFAULT_STYLE)
    return "\n".join(
        [
            f"TitleOfMap: {seed.concern} in {seed.area}",
            f"Area: {seed.area}",
            f"AreaWithConcern: {seed.area}, {seed.concern}",
            f"EmojiForConcern: {seed.concern}, {emoji}",
            f"ColorForConcern: {seed.concern}, {color}",
        ]
    )


# Kana and CJK. Enough to tell which language an unlabelled utterance is in.
_JAPANESE = re.compile(r"[\u3040-\u30ff\u4e00-\u9fff]")


def _guess_lang(utterance: str) -> str:
    return "ja" if _JAPANESE.search(utterance) else "en"


def _as_item(raw: object) -> dict[str, str] | None:
    """One utterance, however the teacher chose to shape it.

    Asked for objects, it returns a bare array of strings about as often as it
    obeys, and rejecting those cost a whole batch. The language label is the
    only thing lost, and the script gives it back.
    """
    if isinstance(raw, str):
        utterance = raw.strip()
        return {"lang": _guess_lang(utterance), "utterance": utterance} if utterance else None
    if not isinstance(raw, dict):
        return None
    utterance = str(raw.get("utterance", "")).strip()
    if not utterance:
        return None
    lang = str(raw.get("lang", "")).strip().lower()
    return {
        "lang": lang if lang in ("ja", "en") else _guess_lang(utterance),
        "utterance": utterance,
    }


def _salvage(reply: str, pattern: str) -> list[dict[str, str]]:
    out = []
    for chunk in re.findall(pattern, reply):
        try:
            item = _as_item(json.loads(chunk))
        except json.JSONDecodeError:
            continue
        if item:
            out.append(item)
    return out


def parse_utterances(reply: str) -> list[dict[str, str]]:
    """Read the teacher's JSON array, tolerating whatever it wraps around it.

    A reply cut off by max_tokens leaves the array unclosed, and json.loads
    rejects the whole thing. Losing a batch that way cost every utterance for
    one seed in the first run, so fall back to reading the objects one by one.
    """
    if not reply:
        return []
    match = re.search(r"\[[\s\S]*\]", reply)
    parsed: object = None
    if match:
        try:
            parsed = json.loads(match.group(0))
        except json.JSONDecodeError:
            parsed = None
    if parsed is None:
        # Objects first. Falling back to bare strings in the same pass would
        # pick up the keys and values inside those objects.
        salvaged = _salvage(reply, r"\{[^{}]*\}")
        return salvaged or _salvage(reply, r"\"(?:[^\"\\\\]|\\\\.)*\"")
    out = []
    for raw in parsed if isinstance(parsed, list) else []:
        item = _as_item(raw)
        if item:
            out.append(item)
    return out


# A concern that finds a fraction of what the seed finds is not the map the
# person asked for, even though it is not empty. "Coffee shops" found 4 in
# Shinjuku where "Cafes" found 343.
SUSPICIOUS_RATIO = 0.1


def is_suspicious(count: int, seed_count: int) -> bool:
    """Whether a non-empty result is too small next to the seed concern."""
    if count <= 0 or seed_count <= 0:
        return False
    return count < seed_count * SUSPICIOUS_RATIO


def dedupe(items: list[dict[str, str]]) -> list[dict[str, str]]:
    """Drop repeated utterances, keeping the first.

    The teacher returns the same phrasing more than once at temperature 0.9,
    and a duplicate is a wasted round trip through inner, deep and Overpass.
    """
    seen: set[str] = set()
    out = []
    for item in items:
        key = item["utterance"].strip().lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(item)
    return out


def looks_like_leak(utterance: str) -> bool:
    """True when the utterance is the label wearing a disguise."""
    lowered = utterance.lower()
    return any(token in lowered for token in LEAK_TOKENS)


def _normalise(part: str) -> str:
    return part.strip().lower()


def area_matches(written: str, seed: Seed) -> bool:
    """Whether an AreaWithConcern line names the seed's area, in order.

    The concern follows the areas, so only the leading parts are compared.
    """
    body = re.sub(r"^AreaWithConcern\s*:?\s*", "", (written or "").strip())
    parts = [_normalise(p) for p in body.split(",")]
    expected = [_normalise(p) for p in seed.area_parts]
    return bool(body) and parts[: len(expected)] == expected


AreaResolver = "Callable[[str], int | None]"


# OSM writes 札幌市 as name:en "Sapporo", so "Sapporo City" matches no
# boundary and the pair is rejected as a wrong place. Same rule as TRIDENT's
# grounding, which had to learn this too.
_AREA_SUFFIXES = (" City", "-shi", " Ward", "-ku", " Prefecture", "-ken")


_SUFFIX_LEVEL = {
    " city": "settlement",
    "-shi": "settlement",
    " ward": "settlement",
    "-ku": "settlement",
    " district": "settlement",
    "-gu": "settlement",
    " prefecture": "state",
    "-ken": "state",
}


def build_area_searches(name: str) -> list[dict[str, str]]:
    """The Nominatim queries to try for an area string, most specific first.

    Free text is not enough. "Isogo, Yokohama" finds nothing, while
    city=Isogo&state=Yokohama returns the same relation the seed resolves to,
    and rejecting the pair as a wrong place was the largest single loss in a
    twenty-seed run. TRIDENT's grounding learned the same lesson separately.
    """
    parts = [p.strip() for p in (name or "").split(",") if p.strip()]
    if not parts:
        return []
    attempts: list[dict[str, str]] = []

    if len(parts) > 1:
        structured = {"city": parts[0], "state": parts[1]}
        if len(parts) > 2:
            structured["country"] = parts[-1]
        attempts.append(structured)

    head = parts[0]
    for suffix, level in _SUFFIX_LEVEL.items():
        if head.lower().endswith(suffix):
            stripped = head[: -len(suffix)].strip()
            if stripped:
                attempts.append({"q": stripped, "featureType": level})
            break

    attempts.append({"q": name.strip()})
    return attempts


def strip_area_suffix(name: str) -> str:
    """Drop a level-naming suffix from the innermost part of an area string."""
    parts = [p.strip() for p in (name or "").split(",")]
    if not parts or not parts[0]:
        return name.strip()
    head = parts[0]
    for suffix in _AREA_SUFFIXES:
        if head.lower().endswith(suffix.lower()):
            stripped = head[: -len(suffix)].strip()
            if stripped:
                parts[0] = stripped
                break
    return ", ".join(parts)


def broader_than_seed(written: str, seed: Seed) -> bool:
    """Whether a reading names a level above the seed rather than a wrong place.

    「京都府にある水族館」 comes back as "Kyoto Prefecture" against a seed of
    "Kyoto, Kyoto Prefecture, Japan". The reading is right and the utterance is
    natural; the seed is simply narrower than what was said. Discarding the
    pair throws away a good one, so it is separated here and the label is moved
    to match the utterance when the training set is assembled.

    Only the seed's own chain counts. Osaka is not a level above Kyoto.
    """
    target = _normalise(written)
    if not target:
        return False
    outer = [_normalise(part) for part in seed.area_parts[1:]]
    return target in outer


def same_place(written: str, seed_area: str, resolve) -> bool:
    """Whether two area strings name the same administrative relation.

    String equality is too strict. "札幌のカフェを教えて" produces
    "Sapporo" against a seed of "Sapporo, Hokkaido", and no one says the
    prefecture out loud. The seed is the redundant one; comparing the
    relations each name resolves to settles it without loosening the check
    enough to let Osaka through.
    """
    if _normalise(written) == _normalise(seed_area):
        return True
    written_id = resolve(written)
    if written_id is None:
        return False
    return written_id == resolve(seed_area)


def area_with_concern_line(inner_output: str) -> str:
    for line in (inner_output or "").split("\n"):
        if line.strip().startswith("AreaWithConcern"):
            return line.strip()
    return ""


@dataclass
class PairResult:
    """One utterance, and how far it got."""

    seed_area: str
    seed_concern: str
    lang: str
    utterance: str
    inner_output: str = ""
    area_with_concern: str = ""
    overpass_query: str = ""
    element_count: int = 0
    seed_element_count: int = 0
    suspicious: bool = False
    verdict: str = "pending"
    note: str = ""

    def as_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items()}


def area_part(area_with_concern: str, seed: Seed) -> str:
    """The area half of an AreaWithConcern line, as many parts as the seed has.

    The concern trails the areas and has no marker, so the seed's shape is
    what says where to cut.
    """
    body = re.sub(r"^AreaWithConcern\s*:?\s*", "", (area_with_concern or "").strip())
    parts = [p.strip() for p in body.split(",") if p.strip()]
    if not parts:
        return ""
    # Never take the last part: that is the concern.
    take = min(len(seed.area_parts), max(len(parts) - 1, 1))
    return ", ".join(parts[:take])


# What OSM itself calls the place, in every language it records. The check
# that a generated utterance names a real place rests on these.
_NAME_KEYS = ("name", "name:en", "name:ja", "name:ko", "official_name", "alt_name")


# OSM records 小金井市 and 磯子区; people write 小金井 and 磯子. Dropping the
# suffix has to stop before the name becomes a common word: 港区 shortened to
# 港 would match 空港 and every harbour in the sentence.
_JA_SUFFIXES = ("都", "道", "府", "県", "市", "区", "町", "村", "郡")
_MIN_JA_STEM = 2


def name_forms(name: str) -> set[str]:
    """A place name and the shorter forms a person might write instead."""
    cleaned = (name or "").strip()
    if not cleaned:
        return set()
    forms = {cleaned}

    english = strip_area_suffix(cleaned)
    if english and english != cleaned:
        forms.add(english)

    if cleaned[-1] in _JA_SUFFIXES:
        stem = cleaned[:-1]
        if len(stem) >= _MIN_JA_STEM:
            forms.add(stem)
    return forms


def official_names(relation_id: int) -> set[str]:
    """Every name OSM records for a relation, plus the bare English form.

    "Isogo Ward" is what the map says; "Isogo" is what a person writes. Both
    have to count, or every English utterance is rejected.
    """
    try:
        response = httpx.get(
            "https://nominatim.yuiseki.net/lookup",
            params={"osm_ids": f"R{relation_id}", "format": "jsonv2", "namedetails": 1},
            timeout=60,
        )
        if not response.is_success:
            return set()
        payload = response.json()
    except Exception:
        return set()
    if not payload:
        return set()
    details = payload[0].get("namedetails") or {}

    names: set[str] = set()
    for key in _NAME_KEYS:
        if details.get(key):
            names |= name_forms(details[key])
    return {n for n in names if n}


def utterance_names_place(utterance: str, names: set[str]) -> bool:
    """Whether the utterance actually contains one of the place's names.

    The teacher invents place names. It wrote 磯谷区 for 磯子区 and
    "ソウル北エリア" for 강북구, and both survived every other check because
    the inner layer read through the mistake and produced the right area. The
    label was right and the utterance was wrong, which is the shape of a pair
    that teaches a false name.

    With no names to compare against, the answer is no: an unverifiable
    utterance is not a verified one.
    """
    if not names:
        return False
    lowered = (utterance or "").lower()
    return any(name.lower() in lowered for name in names)


def resolve_area(name: str) -> int | None:
    """Resolve an area string to an OSM relation, trying each shape in turn."""
    for params in build_area_searches(name):
        try:
            if "q" in params and len(params) == 1:
                found = get_osm_relation_id(params["q"])
            else:
                found = _search_relation(params)
        except Exception:
            continue
        if found is not None:
            return found
    return None


def _search_relation(params: dict[str, str]) -> int | None:
    query = {"format": "jsonv2", **params}
    response = httpx.get(
        "https://nominatim.yuiseki.net/search", params=query, timeout=60
    )
    if not response.is_success:
        return None
    for result in response.json():
        if result.get("osm_type") == "relation" and result.get("category") == "boundary":
            return int(result["osm_id"])
    return None


@dataclass
class Counts:
    accepted: int = 0
    broader_than_seed: int = 0
    invented_name: int = 0
    deep_gap: int = 0
    zero_results: int = 0
    wrong_area: int = 0
    leaked: int = 0
    no_area_line: int = 0
    failed: int = 0
    by_verdict: dict = field(default_factory=dict)

    def record(self, verdict: str) -> None:
        setattr(self, verdict, getattr(self, verdict, 0) + 1)
        self.by_verdict[verdict] = self.by_verdict.get(verdict, 0) + 1


def _post(url: str, payload: dict, timeout: float) -> dict:
    response = httpx.post(url, json=payload, timeout=timeout)
    response.raise_for_status()
    return response.json()


def reverse_generate(
    seed: Seed, variants: int, *, lang: str = "ja", timeout: float = DEFAULT_TIMEOUT
) -> list[dict[str, str]]:
    """Ask the teacher what a person would have typed to get this label.

    One language per call. Asked for both at once it returned seven English
    utterances and no Japanese, however the split was worded.
    """
    payload = {
        "model": "gvt-llm",
        "temperature": 0.9,
        "max_tokens": 120 * variants + 300,
        "messages": [
            {"role": "system", "content": reverse_system_prompt(variants, lang)},
            {"role": "user", "content": build_intermediate(seed)},
        ],
    }
    reply = _post(TEACHER_URL, payload, timeout)["choices"][0]["message"]["content"]
    items = [i | {"lang": lang} for i in parse_utterances(reply)]
    return dedupe(items)[:variants]


def reverse_generate_both(
    seed: Seed, variants: int, *, timeout: float = DEFAULT_TIMEOUT
) -> list[dict[str, str]]:
    """Half in each language, generated separately so the split holds."""
    half = max(variants // 2, 1)
    out = []
    for lang in ("ja", "en"):
        try:
            out.extend(reverse_generate(seed, half, lang=lang, timeout=timeout))
        except Exception as error:
            print(f"  {lang} generation failed: {error}")
    return out


def ask_inner(utterance: str, *, timeout: float = DEFAULT_TIMEOUT) -> str:
    """Read the utterance with TRIDENT's own inner layer and its real prompt."""
    reply = (
        "Ability: overpass-api\n"
        "Reply: I copy. I'm generating maps based on OpenStreetMap data. "
        "Please wait a while..."
    )
    payload = {"pastMessages": [utterance, reply]}
    return _post(f"{TRIDENT_URL}/api/ai/inner", payload, timeout).get("inner", "")


def ask_deep(area_with_concern: str, *, timeout: float = DEFAULT_TIMEOUT) -> str:
    payload = {"query": area_with_concern}
    return _post(f"{TRIDENT_URL}/api/ai/deep", payload, timeout).get("deep", "")


def count_elements(query: str, *, timeout: float = DEFAULT_TIMEOUT) -> int:
    response = httpx.post(OVERPASS_URL, content=query.encode(), timeout=timeout)
    response.raise_for_status()
    return len(response.json().get("elements", []))


def seed_control_count(seed: Seed, *, timeout: float = DEFAULT_TIMEOUT) -> int:
    """How many features the seed concern finds in the seed area.

    The yardstick for everything generated from this seed: it says whether an
    empty result is the utterance's fault, and how small is too small. One
    call per seed, not per utterance.
    """
    line = f"AreaWithConcern: {seed.area}, {seed.concern}"
    try:
        query = ask_deep(line, timeout=timeout)
        return count_elements(query, timeout=timeout) if query.strip() else 0
    except Exception:
        return 0


def evaluate(
    seed: Seed,
    item: dict[str, str],
    *,
    seed_count: int = 0,
    seed_names: set[str] | None = None,
    timeout: float = DEFAULT_TIMEOUT,
) -> PairResult:
    """Take one reconstructed utterance as far as it will go."""
    result = PairResult(
        seed_area=seed.area,
        seed_concern=seed.concern,
        lang=item.get("lang", "unknown"),
        utterance=item["utterance"],
    )

    if looks_like_leak(result.utterance):
        result.verdict = "leaked"
        result.note = "utterance repeats the internal format"
        return result

    # Before anything else: does the utterance name a place that exists? The
    # inner layer reads through a misspelling and produces the right area, so
    # every later check passes and a false name enters the data.
    if seed_names is not None and not utterance_names_place(
        result.utterance, seed_names
    ):
        result.verdict = "invented_name"
        result.note = f"none of {sorted(seed_names)[:3]} appear"
        return result

    try:
        result.inner_output = ask_inner(result.utterance, timeout=timeout)
        result.area_with_concern = area_with_concern_line(result.inner_output)
        if not result.area_with_concern:
            result.verdict = "no_area_line"
            return result

        # A wrong place still finds cafes, so this is the guard that matters.
        # Compared by relation rather than by string: "Sapporo" and
        # "Sapporo, Hokkaido" are the same place and the shorter one is what
        # a person actually says.
        written_area = area_part(result.area_with_concern, seed)
        if not same_place(written_area, seed.area, resolve_area):
            # A reading one level up is not a wrong place. The utterance said
            # the wider thing, so the label belongs to the utterance, not the
            # seed. Kept and relabelled when the training set is assembled.
            if broader_than_seed(written_area, seed):
                result.verdict = "broader_than_seed"
                result.note = f"read as {written_area!r}, a level above the seed"
                return result
            result.verdict = "wrong_area"
            result.note = f"read as {written_area!r}"
            return result

        result.overpass_query = ask_deep(result.area_with_concern, timeout=timeout)
        if not result.overpass_query.strip():
            result.verdict = "failed"
            result.note = "deep returned nothing"
            return result

        result.element_count = count_elements(result.overpass_query, timeout=timeout)
        result.seed_element_count = seed_count
        if result.element_count > 0:
            result.verdict = "accepted"
            result.suspicious = is_suspicious(result.element_count, seed_count)
            if result.suspicious:
                result.note = f"seed concern finds {seed_count}"
            return result

        # Nothing came back. That is only the utterance's fault if the seed
        # concern would have found something here. When the seed works and the
        # drifted concern does not, the inner reading was fine and the deep
        # layer could not express it: keep the pair and record the gap.
        if seed_count > 0:
            result.verdict = "deep_gap"
            result.note = f"seed concern finds {seed_count}"
        else:
            result.verdict = "zero_results"
            result.note = "seed concern finds nothing here either"
    except Exception as error:  # a hang or a 500 is a result, not a crash
        result.verdict = "failed"
        result.note = f"{type(error).__name__}: {error}"
    return result


# A spread of administrative levels: special wards, designated cities and the
# prefecture that contains them. Concerns behave differently at each.
DEFAULT_AREAS = [
    "Taito, Tokyo",
    "Shinjuku, Tokyo",
    "Sapporo, Hokkaido",
    "Sendai, Miyagi",
    "Nagoya, Aichi",
    "Kobe, Hyogo",
    "Fukuoka, Fukuoka",
    "Naha, Okinawa",
]

CONCERNS_PATH = Path(__file__).resolve().parent.parent / "good_concerns.yaml"
CONCERNS_DIR = Path(__file__).resolve().parent.parent / "data" / "concerns"

# "AreaWithConcern: Taito, Tokyo, Japan; Cafes". A few entries lead with
# "Area:" instead, for a named feature rather than a category.
_TRIDENT_LINE = re.compile(r"^\s*(?:AreaWithConcern|Area)\s*:\s*(.+?)\s*;\s*(.+?)\s*$")


def parse_trident_input(line: str) -> Seed | None:
    """Read one input-trident.txt line into a seed."""
    matched = _TRIDENT_LINE.match(line or "")
    if not matched:
        return None
    area, concern = matched.group(1).strip(), matched.group(2).strip()
    return Seed(area, concern) if area and concern else None


def load_validated_seeds(root: Path = CONCERNS_DIR) -> list[Seed]:
    """Every (area, concern) pair that already produced a working query.

    18,231 directories hold an input; 4,599 hold a generated .overpassql
    beside it. Only the latter are known to survive the trip through deep and
    Overpass, and seeding from the rest wastes the run: a first attempt built
    the cross product of concerns and areas instead, and twelve of twenty
    seeds turned out to describe nothing that exists there. Taito has no
    airport.
    """
    seeds = []
    for directory in sorted({p.parent for p in Path(root).rglob("output-*.overpassql")}):
        input_path = directory / "input-trident.txt"
        if not input_path.exists():
            continue
        seed = parse_trident_input(input_path.read_text().splitlines()[0] if
                                   input_path.read_text().strip() else "")
        if seed:
            seeds.append(seed)
    return sorted(seeds, key=lambda s: (s.concern, s.area))


def load_concerns(path: Path) -> list[str]:
    """The concern names from good_concerns.yaml, in file order.

    Each line is "Name: path/to/tag". Parsed by hand rather than with a YAML
    reader so the file's comments and grouping stay irrelevant.
    """
    names = []
    for line in Path(path).read_text().splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or ":" not in stripped:
            continue
        name = stripped.split(":", 1)[0].strip()
        if name:
            names.append(name)
    return names


def completed_seeds(path: Path) -> set[tuple[str, str]]:
    """Which seeds a partly written output file already covers.

    A nine-hour run that dies at hour eight should resume, not restart, so
    every pair is flushed as it is produced and read back here. The last line
    of a killed run is usually half written; that line is skipped and the rest
    still counts.
    """
    path = Path(path)
    if not path.exists():
        return set()
    done: set[tuple[str, str]] = set()
    with path.open() as handle:
        for line in handle:
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            area, concern = row.get("seed_area"), row.get("seed_concern")
            if area and concern:
                done.add((area, concern))
    return done


def remaining_seeds(seeds: list[Seed], done: set[tuple[str, str]]) -> list[Seed]:
    return [s for s in seeds if (s.area, s.concern) not in done]


def build_seeds(concerns: list[str], areas: list[str], count: int) -> list[Seed]:
    """Walk both lists at once, so a short run still samples both dimensions.

    Taking the first N concerns against one area would measure one area; the
    cross product in order would measure one concern. Advancing both together
    covers each as far as the count allows.
    """
    if not concerns or not areas:
        return []
    return [
        Seed(areas[i % len(areas)], concerns[i % len(concerns)])
        for i in range(count)
    ]


DEFAULT_SEEDS = [
    Seed("Taito, Tokyo", "Cafes"),
    Seed("Shinjuku, Tokyo", "Cafes"),
    Seed("Sapporo, Hokkaido", "Cafes"),
]


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--limit", type=int, default=len(DEFAULT_SEEDS))
    parser.add_argument(
        "--seeds",
        type=int,
        default=0,
        help="Take this many seeds from the validated pairs in data/concerns "
        "instead of the built-in trio.",
    )
    parser.add_argument(
        "--stride",
        type=int,
        default=1,
        help="Take every Nth validated seed, to spread a short run across the "
        "whole set rather than the first concern alphabetically.",
    )
    parser.add_argument("--variants", type=int, default=6)
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT)
    parser.add_argument("--out-dir", default="tmp")
    parser.add_argument(
        "--out",
        default="",
        help="Append to this file and skip seeds it already covers. Without "
        "it each run writes a fresh timestamped file.",
    )
    args = parser.parse_args()

    if args.seeds > 0:
        validated = load_validated_seeds()
        stride = max(args.stride, 1)
        seeds = validated[::stride][: args.seeds]
        print(f"{len(validated)} validated pairs available; "
              f"taking {len(seeds)} every {stride}")
    else:
        seeds = DEFAULT_SEEDS[: args.limit]
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        done = completed_seeds(out_path)
        if done:
            before = len(seeds)
            seeds = remaining_seeds(seeds, done)
            print(f"resuming: {len(done)} seeds already in {out_path}, "
                  f"{len(seeds)} of {before} left")
    else:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
        out_path = out_dir / f"inner-pairs-{stamp}.jsonl"

    counts = Counts()
    results: list[PairResult] = []
    started = time.monotonic()
    handle = out_path.open("a")

    for seed in seeds:
        print(f"\n### {seed.area} / {seed.concern}")
        try:
            items = reverse_generate_both(seed, args.variants, timeout=args.timeout)
        except Exception as error:
            print(f"  reverse generation failed: {error}")
            continue
        seed_count = seed_control_count(seed, timeout=args.timeout)
        seed_relation = resolve_area(seed.area)
        seed_names = official_names(seed_relation) if seed_relation else set()
        print(f"  seed concern finds {seed_count}; {len(items)} utterances kept "
              f"of {args.variants} asked for")
        for item in items:
            result = evaluate(
                seed,
                item,
                seed_count=seed_count,
                seed_names=seed_names,
                timeout=args.timeout,
            )
            counts.record(result.verdict)
            results.append(result)
            # Flushed per pair: a killed run keeps everything up to the kill.
            handle.write(json.dumps(result.as_dict(), ensure_ascii=False) + "\n")
            handle.flush()
            mark = " !" if result.suspicious else "  "
            print(
                f"  {result.verdict:<11}{mark}{result.element_count:>6}  "
                f"{result.utterance[:36]:<38} -> {result.area_with_concern[17:45]}"
            )

    handle.close()

    elapsed = time.monotonic() - started
    total = len(results)
    suspicious = sum(1 for r in results if r.suspicious)
    print(f"\n{'verdict':<15}{'n':>5}  share")
    for verdict, n in sorted(counts.by_verdict.items(), key=lambda kv: -kv[1]):
        print(f"{verdict:<15}{n:>5}  {n / total:.0%}" if total else verdict)
    if suspicious:
        print(f"\n{suspicious} accepted pairs found under "
              f"{int(SUSPICIOUS_RATIO * 100)}% of what the seed concern finds")
    if total:
        per_seed = elapsed / len(seeds) if seeds else 0
        print(
            f"\n{elapsed / 60:.1f} min for {len(seeds)} seeds "
            f"({per_seed:.0f} s each, {elapsed / total:.0f} s per pair)"
        )
    print(f"\nwrote {out_path}")


if __name__ == "__main__":
    main()
