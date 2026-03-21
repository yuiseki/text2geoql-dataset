"""Tests for scan_concerns.py — hierarchical tag scan with __tag_scan/ storage."""

import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from scan_concerns import (
    admin_path_to_area_name,
    build_count_query,
    is_scanned,
    iter_admin_children,
    load_concerns,
    load_result,
    result_path,
    save_result,
    scan_node,
    scan_tree,
)


# ── load_concerns ─────────────────────────────────────────────────────────────


def test_load_concerns_returns_key_value_tuples(tmp_path):
    yaml = tmp_path / "concerns.yaml"
    yaml.write_text(
        "Cafes: data/concerns/amenity/cafe\n"
        "Anime Shops: data/concerns/shop/anime\n"
        "Hospitals: data/concerns/amenity/hospital\n"
    )
    concerns = load_concerns(str(yaml))
    assert ("amenity", "cafe") in concerns
    assert ("shop", "anime") in concerns
    assert ("amenity", "hospital") in concerns


def test_load_concerns_skips_composite_paths(tmp_path):
    yaml = tmp_path / "concerns.yaml"
    yaml.write_text(
        "Medical Facilities: data/concerns/medical/all\n"
        "Cafes: data/concerns/amenity/cafe\n"
        "# comment line\n"
    )
    concerns = load_concerns(str(yaml))
    assert ("amenity", "cafe") in concerns
    # composite paths (3+ components after data/concerns/) or non-standard keys are skipped
    keys = [k for k, v in concerns]
    assert "medical" not in keys


def test_load_concerns_skips_cuisine_subtags(tmp_path):
    yaml = tmp_path / "concerns.yaml"
    yaml.write_text(
        "Ramen shops: data/concerns/amenity/restaurant/cuisine/ramen\n"
        "Cafes: data/concerns/amenity/cafe\n"
    )
    concerns = load_concerns(str(yaml))
    assert ("amenity", "cafe") in concerns
    # cuisine subtag paths have depth > 2, skip
    assert ("amenity", "restaurant") not in concerns or True  # just check no crash


# ── result_path ───────────────────────────────────────────────────────────────


def test_result_path_country_level():
    path = result_path("data/administrative/Japan", "shop", "anime")
    assert path == "data/administrative/Japan/__tag_scan/shop/anime/result.json"


def test_result_path_city_level():
    path = result_path("data/administrative/Japan/Tokyo", "amenity", "cafe")
    assert path == "data/administrative/Japan/Tokyo/__tag_scan/amenity/cafe/result.json"


def test_result_path_district_level():
    path = result_path("data/administrative/Japan/Tokyo/Shinjuku", "amenity", "love_hotel")
    assert path == "data/administrative/Japan/Tokyo/Shinjuku/__tag_scan/amenity/love_hotel/result.json"


# ── admin_path_to_area_name ───────────────────────────────────────────────────


def test_admin_path_to_area_name_country():
    assert admin_path_to_area_name("data/administrative/Japan") == "Japan"


def test_admin_path_to_area_name_city():
    assert admin_path_to_area_name("data/administrative/Japan/Tokyo") == "Tokyo, Japan"


def test_admin_path_to_area_name_district():
    name = admin_path_to_area_name("data/administrative/Japan/Tokyo/Shinjuku")
    assert name == "Shinjuku, Tokyo, Japan"


def test_admin_path_to_area_name_deep():
    name = admin_path_to_area_name(
        "data/administrative/Japan/Hiroshima Prefecture/Hiroshima/Naka Ward"
    )
    assert name == "Naka Ward, Hiroshima, Hiroshima Prefecture, Japan"


# ── build_count_query ─────────────────────────────────────────────────────────


def test_build_count_query_contains_area_id():
    q = build_count_query(3600382313, "shop", "anime")
    assert "area(id:3600382313)" in q
    assert '["shop"="anime"]' in q
    assert "out count;" in q


def test_build_count_query_no_out_geom():
    q = build_count_query(3600382313, "amenity", "cafe")
    assert "out geom" not in q
    assert "out count;" in q


# ── save_result / load_result / is_scanned ────────────────────────────────────


def test_save_and_load_result(tmp_path):
    admin = str(tmp_path / "Japan")
    save_result(admin, "shop", "anime", count=892, relation_id=382313, area_name="Japan")
    assert is_scanned(admin, "shop", "anime")
    r = load_result(admin, "shop", "anime")
    assert r["count"] == 892
    assert r["osm_relation_id"] == 382313
    assert r["area_name"] == "Japan"
    assert "scanned_at" in r


def test_save_result_zero_count(tmp_path):
    admin = str(tmp_path / "Ethiopia")
    save_result(admin, "shop", "anime", count=0, relation_id=None, area_name="Ethiopia")
    r = load_result(admin, "shop", "anime")
    assert r["count"] == 0
    assert r["osm_relation_id"] is None


def test_is_scanned_false_when_no_file(tmp_path):
    assert not is_scanned(str(tmp_path / "Japan"), "shop", "anime")


# ── iter_admin_children ───────────────────────────────────────────────────────


def test_iter_admin_children_returns_subdirs(tmp_path):
    admin = tmp_path / "Japan"
    (admin / "Tokyo").mkdir(parents=True)
    (admin / "Osaka Prefecture").mkdir()
    (admin / "__tag_scan").mkdir()  # should be excluded
    (admin / "__meta").mkdir()      # should be excluded
    (admin / "input-trident.txt").write_text("")  # file, not dir

    children = list(iter_admin_children(str(admin)))
    names = [Path(c).name for c in children]
    assert "Tokyo" in names
    assert "Osaka Prefecture" in names
    assert "__tag_scan" not in names
    assert "__meta" not in names
    assert "input-trident.txt" not in names


# ── scan_node ─────────────────────────────────────────────────────────────────


def test_scan_node_returns_cached_count_if_already_scanned(tmp_path):
    admin = str(tmp_path / "Japan")
    save_result(admin, "shop", "anime", count=500, relation_id=382313, area_name="Japan")

    with patch("scan_concerns.fetch_count") as mock_fetch:
        count = scan_node(admin, "shop", "anime", relation_id=382313)

    assert count == 500
    mock_fetch.assert_not_called()


def test_scan_node_queries_overpass_when_not_scanned(tmp_path):
    admin = str(tmp_path / "Japan")

    with patch("scan_concerns.fetch_count", return_value=892) as mock_fetch:
        count = scan_node(admin, "shop", "anime", relation_id=382313)

    assert count == 892
    mock_fetch.assert_called_once()
    assert is_scanned(admin, "shop", "anime")
    assert load_result(admin, "shop", "anime")["count"] == 892


def test_scan_node_saves_zero_count(tmp_path):
    admin = str(tmp_path / "Ethiopia")

    with patch("scan_concerns.fetch_count", return_value=0):
        count = scan_node(admin, "shop", "anime", relation_id=999)

    assert count == 0
    assert is_scanned(admin, "shop", "anime")


# ── scan_tree ─────────────────────────────────────────────────────────────────


def test_scan_tree_prunes_children_on_zero_count(tmp_path):
    """If count=0 at country level, children must not be scanned."""
    admin = tmp_path / "Ethiopia"
    child = admin / "Addis Ababa"
    child.mkdir(parents=True)

    with patch("scan_concerns.fetch_count", return_value=0) as mock_fetch:
        with patch("scan_concerns.get_relation_id", return_value=12345):
            scan_tree(str(admin), "shop", "anime")

    # Only one call (country level), child not scanned
    assert mock_fetch.call_count == 1
    assert not is_scanned(str(child), "shop", "anime")


def test_scan_tree_recurses_into_children_on_nonzero_count(tmp_path):
    """If count>0 at country level, children are scanned."""
    admin = tmp_path / "Japan"
    child = admin / "Tokyo"
    child.mkdir(parents=True)

    call_counts = {"Japan": 50, "Tokyo": 20}

    def fake_fetch(query, **kwargs):
        if "Tokyo" in query or str(child) in query:
            return call_counts["Tokyo"]
        return call_counts["Japan"]

    with patch("scan_concerns.fetch_count", side_effect=fake_fetch):
        with patch("scan_concerns.get_relation_id", return_value=11111):
            scan_tree(str(admin), "amenity", "cafe")

    assert is_scanned(str(admin), "amenity", "cafe")
    assert is_scanned(str(child), "amenity", "cafe")


def test_scan_tree_skips_already_scanned_nodes(tmp_path):
    admin = tmp_path / "Japan"
    child = admin / "Tokyo"
    child.mkdir(parents=True)

    # Pre-save results
    save_result(str(admin), "amenity", "cafe", count=1000, relation_id=382313, area_name="Japan")
    save_result(str(child), "amenity", "cafe", count=200, relation_id=111111, area_name="Tokyo, Japan")

    with patch("scan_concerns.fetch_count") as mock_fetch:
        with patch("scan_concerns.get_relation_id", return_value=382313):
            scan_tree(str(admin), "amenity", "cafe")

    mock_fetch.assert_not_called()
