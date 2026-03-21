"""Tests for populate_administrative.py — create country-level admin stubs."""

import os
import sys
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from populate_administrative import (
    build_countries_query,
    build_subnodes_query,
    create_country_node,
    create_subnode,
    fetch_countries,
    fetch_subnodes,
    node_exists,
)


# ── build_countries_query ─────────────────────────────────────────────────────


def test_build_countries_query_targets_admin_level_2():
    q = build_countries_query()
    assert "admin_level" in q and "2" in q


def test_build_countries_query_requires_name_en():
    q = build_countries_query()
    assert "name:en" in q


def test_build_countries_query_filters_by_iso3166():
    q = build_countries_query()
    assert "ISO3166-1" in q


def test_build_countries_query_uses_out_tags():
    q = build_countries_query()
    assert "out tags" in q


# ── create_country_node ───────────────────────────────────────────────────────


def test_create_country_node_creates_files(tmp_path):
    create_country_node(str(tmp_path), "Japan")
    node = tmp_path / "Japan"
    assert (node / "input-trident.txt").exists()
    assert (node / "output-001.overpassql").exists()


def test_create_country_node_input_trident_format(tmp_path):
    create_country_node(str(tmp_path), "South Korea")
    txt = (tmp_path / "South Korea" / "input-trident.txt").read_text().strip()
    assert txt == "Area: South Korea"


def test_create_country_node_overpassql_format(tmp_path):
    create_country_node(str(tmp_path), "France")
    ql = (tmp_path / "France" / "output-001.overpassql").read_text()
    assert '"admin_level"="2"' in ql
    assert '"boundary"="administrative"' in ql
    assert '"France"' in ql
    assert "out geom;" in ql


def test_create_country_node_is_idempotent(tmp_path):
    create_country_node(str(tmp_path), "Japan")
    (tmp_path / "Japan" / "input-trident.txt").write_text("modified")
    create_country_node(str(tmp_path), "Japan")  # second call
    assert (tmp_path / "Japan" / "input-trident.txt").read_text() == "modified"


# ── node_exists ───────────────────────────────────────────────────────────────


def test_node_exists_true_when_trident_present(tmp_path):
    (tmp_path / "Japan").mkdir()
    (tmp_path / "Japan" / "input-trident.txt").write_text("Area: Japan")
    assert node_exists(str(tmp_path), "Japan")


def test_node_exists_false_when_missing(tmp_path):
    assert not node_exists(str(tmp_path), "Germany")


# ── fetch_countries ───────────────────────────────────────────────────────────


def test_fetch_countries_returns_name_en_list():
    mock_elements = [
        {"tags": {"name:en": "Japan", "name": "日本"}},
        {"tags": {"name:en": "France", "name": "France"}},
        {"tags": {"name": "Deutschland"}},  # no name:en — skip
    ]
    with patch("populate_administrative.fetch_elements", return_value=mock_elements):
        result = fetch_countries()
    assert "Japan" in result
    assert "France" in result
    assert len(result) == 2


def test_fetch_countries_deduplicates():
    mock_elements = [
        {"tags": {"name:en": "Japan"}},
        {"tags": {"name:en": "Japan"}},
    ]
    with patch("populate_administrative.fetch_elements", return_value=mock_elements):
        result = fetch_countries()
    assert result.count("Japan") == 1


# ── build_subnodes_query ──────────────────────────────────────────────────────


def test_build_subnodes_query_contains_area_name():
    q = build_subnodes_query("Hiroshima Prefecture, Japan", admin_level=7)
    assert "Hiroshima Prefecture" in q


def test_build_subnodes_query_contains_admin_level():
    q = build_subnodes_query("Hiroshima Prefecture, Japan", admin_level=7)
    assert '"7"' in q


def test_build_subnodes_query_uses_area_filter():
    q = build_subnodes_query("Hiroshima Prefecture, Japan", admin_level=7)
    assert "area" in q.lower()
    assert "out tags" in q


# ── fetch_subnodes ────────────────────────────────────────────────────────────


def test_fetch_subnodes_returns_name_en_list():
    mock_elements = [
        {"tags": {"name:en": "Hiroshima", "admin_level": "7"}},
        {"tags": {"name:en": "Fukuyama", "admin_level": "7"}},
        {"tags": {"name": "呉市"}},  # no name:en — skip
    ]
    with patch("populate_administrative.fetch_elements", return_value=mock_elements):
        result = fetch_subnodes("Hiroshima Prefecture, Japan", admin_level=7)
    assert "Hiroshima" in result
    assert "Fukuyama" in result
    assert len(result) == 2


def test_fetch_subnodes_deduplicates():
    mock_elements = [
        {"tags": {"name:en": "Hiroshima"}},
        {"tags": {"name:en": "Hiroshima"}},
    ]
    with patch("populate_administrative.fetch_elements", return_value=mock_elements):
        result = fetch_subnodes("Hiroshima Prefecture, Japan", admin_level=7)
    assert result.count("Hiroshima") == 1


# ── create_subnode ────────────────────────────────────────────────────────────


def test_create_subnode_creates_files(tmp_path):
    parent = tmp_path / "Japan" / "Hiroshima Prefecture"
    parent.mkdir(parents=True)
    create_subnode(str(tmp_path), ["Japan", "Hiroshima Prefecture", "Hiroshima"], admin_level=7)
    node = parent / "Hiroshima"
    assert (node / "input-trident.txt").exists()
    assert (node / "output-001.overpassql").exists()


def test_create_subnode_trident_format(tmp_path):
    parent = tmp_path / "Japan" / "Hiroshima Prefecture"
    parent.mkdir(parents=True)
    create_subnode(str(tmp_path), ["Japan", "Hiroshima Prefecture", "Hiroshima"], admin_level=7)
    txt = (tmp_path / "Japan" / "Hiroshima Prefecture" / "Hiroshima" / "input-trident.txt").read_text().strip()
    assert txt == "Area: Hiroshima, Hiroshima Prefecture, Japan"


def test_create_subnode_overpassql_contains_admin_level(tmp_path):
    parent = tmp_path / "Japan" / "Hiroshima Prefecture"
    parent.mkdir(parents=True)
    create_subnode(str(tmp_path), ["Japan", "Hiroshima Prefecture", "Naka Ward"], admin_level=8)
    ql = (tmp_path / "Japan" / "Hiroshima Prefecture" / "Naka Ward" / "output-001.overpassql").read_text()
    assert '"8"' in ql
    assert "Naka Ward" in ql


def test_create_subnode_is_idempotent(tmp_path):
    parent = tmp_path / "Japan" / "Hiroshima Prefecture"
    parent.mkdir(parents=True)
    create_subnode(str(tmp_path), ["Japan", "Hiroshima Prefecture", "Hiroshima"], admin_level=7)
    trident = tmp_path / "Japan" / "Hiroshima Prefecture" / "Hiroshima" / "input-trident.txt"
    trident.write_text("modified")
    create_subnode(str(tmp_path), ["Japan", "Hiroshima Prefecture", "Hiroshima"], admin_level=7)
    assert trident.read_text() == "modified"
