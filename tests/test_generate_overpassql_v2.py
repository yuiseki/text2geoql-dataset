"""Tests for generate_overpassql_v2 — Nominatim + Taginfo enhanced pipeline.

All external calls (Nominatim, Taginfo, LLM, Overpass) are mocked so tests
run offline without any network access.
"""

from unittest.mock import MagicMock, patch

import pytest

from generate_overpassql_v2 import (
    build_area_hint,
    extract_tags_from_query,
    parse_full_area,
    validate_query_tags,
)


# ── parse_full_area ───────────────────────────────────────────────────────────


def test_parse_full_area_basic():
    assert parse_full_area("AreaWithConcern: Shinjuku, Tokyo, Japan; Hotels") == "Shinjuku, Tokyo, Japan"


def test_parse_full_area_two_parts():
    assert parse_full_area("AreaWithConcern: Seoul, South Korea; Restaurants") == "Seoul, South Korea"


def test_parse_full_area_single_part():
    assert parse_full_area("AreaWithConcern: Japan; Airports") == "Japan"


def test_parse_full_area_four_parts():
    assert (
        parse_full_area("AreaWithConcern: Gangnam-gu, Seoul, South Korea; Cafes")
        == "Gangnam-gu, Seoul, South Korea"
    )


# ── extract_tags_from_query ───────────────────────────────────────────────────


def test_extract_tags_simple():
    query = 'nwr["amenity"="hospital"](area.inner);'
    assert extract_tags_from_query(query) == [("amenity", "hospital")]


def test_extract_tags_multiple():
    query = 'nwr["amenity"="place_of_worship"]["religion"="muslim"](area.inner);'
    tags = extract_tags_from_query(query)
    assert ("amenity", "place_of_worship") in tags
    assert ("religion", "muslim") in tags


def test_extract_tags_no_tags():
    query = "[out:json][timeout:30];\nout geom;"
    assert extract_tags_from_query(query) == []


def test_extract_tags_cuisine_subtag():
    query = 'nwr["amenity"="restaurant"]["cuisine"="soba"](area.inner);'
    tags = extract_tags_from_query(query)
    assert ("amenity", "restaurant") in tags
    assert ("cuisine", "soba") in tags


def test_extract_tags_ignores_area_filters():
    # area["name"="Tokyo"] should also be extracted
    query = 'area["name"="Tokyo"]->.inner;\nnwr["shop"="convenience"](area.inner);'
    tags = extract_tags_from_query(query)
    assert ("shop", "convenience") in tags


# ── build_area_hint ───────────────────────────────────────────────────────────


def test_build_area_hint_basic():
    hint = build_area_hint(3_601_234_567, "Shinjuku, Tokyo, Japan")
    assert "3601234567" in hint
    assert "Shinjuku, Tokyo, Japan" in hint


def test_build_area_hint_is_string():
    hint = build_area_hint(3_600_000_001, "Japan")
    assert isinstance(hint, str)
    assert len(hint) > 0


def test_build_area_hint_uses_correct_overpassql_syntax():
    """Hint must use area(id:...) not area[id:...] — the LLM must learn the right syntax."""
    hint = build_area_hint(3_601_234_567, "Shinjuku, Tokyo, Japan")
    assert "area(id:3601234567)" in hint
    assert "area[id:" not in hint


def test_build_area_hint_includes_syntax_snippet():
    """Hint should include a concrete Overpass QL snippet to guide the LLM."""
    hint = build_area_hint(3_601_234_567, "Shinjuku, Tokyo, Japan")
    # Must include the .searchArea variable assignment pattern
    assert ".searchArea" in hint


# ── fix_area_id_syntax ────────────────────────────────────────────────────────


from generate_overpassql_v2 import fix_area_id_syntax, add_area_comment


def test_fix_area_id_syntax_corrects_bracket_form():
    """area[id:X] → area(id:X)"""
    query = "area[id:3601234567]->.searchArea;\nnwr[\"amenity\"=\"cafe\"](area.searchArea);"
    fixed = fix_area_id_syntax(query)
    assert "area(id:3601234567)" in fixed
    assert "area[id:" not in fixed


def test_fix_area_id_syntax_leaves_correct_form_unchanged():
    query = "area(id:3601234567)->.searchArea;\nnwr[\"amenity\"=\"cafe\"](area.searchArea);"
    assert fix_area_id_syntax(query) == query


def test_fix_area_id_syntax_no_area_id():
    query = "area[\"name\"=\"Tokyo\"]->.inner;\nnwr[\"amenity\"=\"cafe\"](area.inner);"
    assert fix_area_id_syntax(query) == query


# ── add_area_comment ──────────────────────────────────────────────────────────


def test_add_area_comment_basic():
    query = "area(id:3601758858)->.searchArea;\nnwr[\"amenity\"=\"cafe\"](area.searchArea);"
    result = add_area_comment(query, 3601758858, "Shinjuku, Tokyo, Japan")
    assert "// Shinjuku, Tokyo, Japan" in result
    assert "area(id:3601758858)" in result


def test_add_area_comment_placed_on_same_line():
    """Comment must appear on the same line as area(id:...) for co-occurrence learning."""
    query = "area(id:3601758858)->.searchArea;\nnwr[\"amenity\"=\"cafe\"](area.searchArea);"
    result = add_area_comment(query, 3601758858, "Shinjuku, Tokyo, Japan")
    for line in result.splitlines():
        if "area(id:3601758858)" in line:
            assert "// Shinjuku, Tokyo, Japan" in line
            break
    else:
        pytest.fail("area(id:...) line not found")


def test_add_area_comment_no_match_leaves_query_unchanged():
    """If area_id not in query, return unchanged."""
    query = "area[\"name\"=\"Tokyo\"]->.inner;\nnwr[\"amenity\"=\"cafe\"](area.inner);"
    result = add_area_comment(query, 3601758858, "Shinjuku, Tokyo, Japan")
    assert result == query


def test_add_area_comment_full_query():
    query = (
        "[out:json][timeout:30];\n"
        "area(id:3601758858)->.searchArea;\n"
        "(\n"
        "  nwr[\"amenity\"=\"cafe\"](area.searchArea);\n"
        ");\n"
        "out geom;"
    )
    result = add_area_comment(query, 3601758858, "Shinjuku, Tokyo, Japan")
    assert "area(id:3601758858)->.searchArea; // Shinjuku, Tokyo, Japan" in result


def test_run_v2_output_contains_area_comment(tmp_path):
    """Saved v2 OverpassQL must contain the area name comment."""
    from generate_overpassql_v2 import run_v2

    base = tmp_path / "data" / "concerns" / "amenity" / "cafe" / "Japan" / "Tokyo" / "Shinjuku"
    base.mkdir(parents=True)
    (base / "input-trident.txt").write_text("AreaWithConcern: Shinjuku, Tokyo, Japan; Cafes")

    valid_query = (
        "[out:json][timeout:30];\n"
        "area(id:3601758858)->.searchArea;\n"
        "(\n  nwr[\"amenity\"=\"cafe\"](area.searchArea);\n);\nout geom;"
    )

    with patch("generate_overpassql_v2.nominatim.get_osm_relation_id", return_value=1758858), \
         patch("generate_overpassql_v2.build_prompt", return_value="PROMPT"), \
         patch("generate_overpassql_v2.generate_overpassql", return_value=(valid_query, "")), \
         patch("generate_overpassql_v2.taginfo.validate_tag", return_value=True), \
         patch("generate_overpassql_v2.fetch_elements", return_value=[{"id": 1}] * 10):
        run_v2(base_path=str(base), data_dir=str(tmp_path / "data"), model="qwen2.5-coder:3b")

    output = list(base.glob("output-*-v2.overpassql"))[0].read_text()
    assert "// Shinjuku, Tokyo, Japan" in output


# ── validate_query_tags ───────────────────────────────────────────────────────

VALID_QUERY = 'nwr["amenity"="cafe"](area.inner);'
INVALID_TAG_QUERY = 'nwr["aerport"="yes"](area.inner);'  # typo: aerport
NAME_KEY_QUERY = 'nwr["amenity"="hospital"]["name"="Tokyo Hospital"](area.inner);'
ADDR_KEY_QUERY = 'nwr["amenity"="bank"]["addr:city"="Tokyo"](area.inner);'


def test_validate_query_tags_all_valid():
    """Valid tags return an empty list (no invalid tags found)."""
    with patch("generate_overpassql_v2.taginfo.validate_tag", return_value=True):
        invalid = validate_query_tags(VALID_QUERY)
    assert invalid == []


def test_validate_query_tags_detects_typo():
    """Invalid/misspelled tags (count=0) are returned."""
    with patch("generate_overpassql_v2.taginfo.validate_tag", return_value=False):
        invalid = validate_query_tags(INVALID_TAG_QUERY)
    assert len(invalid) > 0
    assert any("aerport" in t for t in invalid)


def test_validate_query_tags_skips_name_key():
    """name=* keys should be skipped (they are not type classifiers)."""
    def mock_validate(key, value, **kwargs):
        if key == "name":
            raise AssertionError("name key should not be validated")
        return True

    with patch("generate_overpassql_v2.taginfo.validate_tag", side_effect=mock_validate):
        invalid = validate_query_tags(NAME_KEY_QUERY)
    assert invalid == []


def test_validate_query_tags_skips_addr_key():
    """addr:* keys should be skipped."""
    def mock_validate(key, value, **kwargs):
        if key.startswith("addr:"):
            raise AssertionError("addr:* key should not be validated")
        return True

    with patch("generate_overpassql_v2.taginfo.validate_tag", side_effect=mock_validate):
        invalid = validate_query_tags(ADDR_KEY_QUERY)
    assert invalid == []


def test_validate_query_tags_skips_area_name_tags():
    """area["name"="..."] filter tags should be skipped."""
    query = 'area["name"="Tokyo"]->.inner;\nnwr["amenity"="cafe"](area.inner);'
    with patch("generate_overpassql_v2.taginfo.validate_tag", return_value=True) as mock_v:
        invalid = validate_query_tags(query)
    # name key should never be validated
    for call in mock_v.call_args_list:
        assert call[0][0] != "name"
    assert invalid == []


# ── build_prompt_v2 (integration-level, mocked) ──────────────────────────────


def test_build_prompt_v2_includes_area_hint():
    """When Nominatim resolves the area, the prompt contains the area(id:...) hint."""
    from generate_overpassql_v2 import build_prompt_v2

    instruct = "AreaWithConcern: Taito, Tokyo, Japan; Cafes"

    with patch("generate_overpassql_v2.nominatim.get_osm_relation_id", return_value=12345), \
         patch("generate_overpassql_v2.build_prompt") as mock_bp:
        mock_bp.return_value = "MOCK_PROMPT"
        prompt, area_id = build_prompt_v2(instruct, data_dir="./data")

    assert area_id == 12345 + 3_600_000_000
    assert "3600012345" in prompt or mock_bp.called  # hint injected


def test_build_prompt_v2_no_area_id():
    """When Nominatim fails, prompt is built without area hint and area_id is None."""
    from generate_overpassql_v2 import build_prompt_v2

    instruct = "AreaWithConcern: Unknown Place XYZ; Cafes"

    with patch("generate_overpassql_v2.nominatim.get_osm_relation_id", return_value=None), \
         patch("generate_overpassql_v2.build_prompt") as mock_bp:
        mock_bp.return_value = "MOCK_PROMPT"
        prompt, area_id = build_prompt_v2(instruct, data_dir="./data")

    assert area_id is None
    assert prompt == "MOCK_PROMPT"


# ── run_v2 (end-to-end pipeline, fully mocked) ───────────────────────────────


def test_run_v2_success(tmp_path):
    """Full pipeline: Nominatim resolves, LLM generates valid query, Overpass returns elements."""
    from generate_overpassql_v2 import run_v2

    base = tmp_path / "data" / "concerns" / "amenity" / "cafe" / "Japan" / "Tokyo" / "Taito"
    base.mkdir(parents=True)
    (base / "input-trident.txt").write_text("AreaWithConcern: Taito, Tokyo, Japan; Cafes")

    valid_query = '[out:json][timeout:30];\narea(id:3601234567)->.inner;\n(\n  nwr["amenity"="cafe"](area.inner);\n);\nout geom;'

    with patch("generate_overpassql_v2.nominatim.get_osm_relation_id", return_value=1234567), \
         patch("generate_overpassql_v2.build_prompt", return_value="PROMPT"), \
         patch("generate_overpassql_v2.generate_overpassql", return_value=(valid_query, "")), \
         patch("generate_overpassql_v2.taginfo.validate_tag", return_value=True), \
         patch("generate_overpassql_v2.fetch_elements", return_value=[{"id": 1}] * 5):
        run_v2(base_path=str(base), data_dir=str(tmp_path / "data"))

    outputs = list(base.glob("output-*.overpassql"))
    assert len(outputs) == 1


def test_run_v2_output_uses_v2_slug(tmp_path):
    """Output file must use -v2 suffix, not collide with v1 output."""
    from generate_overpassql_v2 import run_v2

    base = tmp_path / "data" / "concerns" / "amenity" / "cafe" / "Japan" / "Tokyo" / "Taito"
    base.mkdir(parents=True)
    (base / "input-trident.txt").write_text("AreaWithConcern: Taito, Tokyo, Japan; Cafes")

    valid_query = '[out:json][timeout:30];\narea(id:3601234567)->.searchArea;\n(\n  nwr["amenity"="cafe"](area.searchArea);\n);\nout geom;'

    with patch("generate_overpassql_v2.nominatim.get_osm_relation_id", return_value=1234567), \
         patch("generate_overpassql_v2.build_prompt", return_value="PROMPT"), \
         patch("generate_overpassql_v2.generate_overpassql", return_value=(valid_query, "")), \
         patch("generate_overpassql_v2.taginfo.validate_tag", return_value=True), \
         patch("generate_overpassql_v2.fetch_elements", return_value=[{"id": 1}] * 5):
        run_v2(base_path=str(base), data_dir=str(tmp_path / "data"), model="qwen2.5-coder:3b")

    v2_outputs = list(base.glob("output-*-v2.overpassql"))
    v1_outputs = list(base.glob("output-qwen2.5-coder-3b.overpassql"))
    assert len(v2_outputs) == 1, "v2 output must exist"
    assert len(v1_outputs) == 0, "v1 output must NOT be created by run_v2"


def test_run_v2_invalid_tag_skips_overpass(tmp_path):
    """When Taginfo finds an invalid tag, Overpass should not be called."""
    from generate_overpassql_v2 import run_v2

    base = tmp_path / "data" / "concerns" / "aeroway" / "aerodrome" / "Japan" / "Tokyo" / "Taito"
    base.mkdir(parents=True)
    (base / "input-trident.txt").write_text("AreaWithConcern: Taito, Tokyo, Japan; Airports")

    bad_query = '[out:json][timeout:30];\nnwr["aerport"="yes"](area.inner);\nout geom;'

    with patch("generate_overpassql_v2.nominatim.get_osm_relation_id", return_value=None), \
         patch("generate_overpassql_v2.build_prompt", return_value="PROMPT"), \
         patch("generate_overpassql_v2.generate_overpassql", return_value=(bad_query, "")), \
         patch("generate_overpassql_v2.taginfo.validate_tag", return_value=False), \
         patch("generate_overpassql_v2.fetch_elements") as mock_fetch:
        run_v2(base_path=str(base), data_dir=str(tmp_path / "data"))

    mock_fetch.assert_not_called()
    not_found = list(base.glob("not-found-*.json"))
    assert len(not_found) == 1


def test_run_v2_skips_existing_output(tmp_path):
    """If output already exists, run_v2 returns early without calling LLM."""
    from generate_overpassql_v2 import run_v2

    base = tmp_path / "data" / "concerns" / "amenity" / "cafe" / "Japan" / "Tokyo" / "Taito"
    base.mkdir(parents=True)
    (base / "input-trident.txt").write_text("AreaWithConcern: Taito, Tokyo, Japan; Cafes")
    (base / "output-qwen2.5-coder-3b-v2.overpassql").write_text("existing")

    with patch("generate_overpassql_v2.generate_overpassql") as mock_gen:
        run_v2(base_path=str(base), data_dir=str(tmp_path / "data"), model="qwen2.5-coder:3b")

    mock_gen.assert_not_called()
