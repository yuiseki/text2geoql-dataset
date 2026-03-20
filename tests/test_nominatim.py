"""Tests for nominatim.py — mocking HTTP calls."""

from unittest.mock import patch, MagicMock

from nominatim import search, get_osm_relation_id, get_display_name, relation_to_area_id


_SHINJUKU_RESULT = [
    {
        "place_id": 258984930,
        "osm_type": "relation",
        "osm_id": 1758858,
        "name": "新宿区",
        "display_name": "新宿区, 東京都, 160-8484, 日本",
        "lat": "35.6937632",
        "lon": "139.7036319",
    }
]

_NODE_RESULT = [
    {
        "osm_type": "node",
        "osm_id": 9999,
        "display_name": "Shinjuku Station",
    }
]


def _mock_response(data):
    m = MagicMock()
    m.json.return_value = data
    return m


class TestRelationToAreaId:
    def test_converts_correctly(self) -> None:
        assert relation_to_area_id(1758858) == 3_601_758_858

    def test_large_id(self) -> None:
        assert relation_to_area_id(12_394_677) == 3_612_394_677


class TestSearch:
    def test_returns_results(self) -> None:
        with patch("nominatim.httpx.get", return_value=_mock_response(_SHINJUKU_RESULT)):
            results = search("Shinjuku, Tokyo, Japan")
        assert len(results) == 1
        assert results[0]["osm_id"] == 1758858

    def test_returns_empty_on_error(self) -> None:
        with patch("nominatim.httpx.get", side_effect=Exception("timeout")):
            results = search("anywhere")
        assert results == []

    def test_passes_custom_endpoint(self) -> None:
        with patch("nominatim.httpx.get", return_value=_mock_response([])) as mock_get:
            search("test", endpoint="https://custom.example.com")
        assert "custom.example.com" in mock_get.call_args[0][0]


class TestGetOsmRelationId:
    def test_returns_relation_id(self) -> None:
        with patch("nominatim.httpx.get", return_value=_mock_response(_SHINJUKU_RESULT)):
            osm_id = get_osm_relation_id("Shinjuku, Tokyo, Japan")
        assert osm_id == 1758858

    def test_returns_none_when_no_relation(self) -> None:
        with patch("nominatim.httpx.get", return_value=_mock_response(_NODE_RESULT)):
            osm_id = get_osm_relation_id("Shinjuku Station")
        assert osm_id is None

    def test_returns_none_on_empty_results(self) -> None:
        with patch("nominatim.httpx.get", return_value=_mock_response([])):
            osm_id = get_osm_relation_id("Nowhere")
        assert osm_id is None

    def test_returns_none_on_error(self) -> None:
        with patch("nominatim.httpx.get", side_effect=Exception("timeout")):
            osm_id = get_osm_relation_id("anywhere")
        assert osm_id is None


class TestGetDisplayName:
    def test_returns_display_name(self) -> None:
        with patch("nominatim.httpx.get", return_value=_mock_response(_SHINJUKU_RESULT)):
            name = get_display_name("Shinjuku, Tokyo, Japan")
        assert name == "新宿区, 東京都, 160-8484, 日本"

    def test_returns_none_on_empty(self) -> None:
        with patch("nominatim.httpx.get", return_value=_mock_response([])):
            name = get_display_name("Nowhere")
        assert name is None
