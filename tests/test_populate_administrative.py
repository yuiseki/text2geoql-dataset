"""Tests for populate_administrative.py — create country-level admin stubs."""

import os
import sys
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from populate_administrative import (
    build_countries_query,
    create_country_node,
    fetch_countries,
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
