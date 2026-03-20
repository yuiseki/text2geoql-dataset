"""Tests for taginfo.py — mocking HTTP calls."""

from unittest.mock import patch, MagicMock

from taginfo import get_key_values, get_tag_stats, get_tag_combinations, validate_tag


def _mock_response(data: dict):
    m = MagicMock()
    m.json.return_value = data
    return m


_KEY_VALUES_RESPONSE = {
    "total": 100,
    "data": [
        {"value": "cafe", "count": 618_379, "fraction": 0.006, "in_wiki": True},
        {"value": "restaurant", "count": 1_534_553, "fraction": 0.015, "in_wiki": True},
        {"value": "rare_tag", "count": 500, "fraction": 0.0, "in_wiki": False},
    ],
}

_TAG_STATS_RESPONSE = {
    "data": [
        {"type": "all", "count": 618_379},
        {"type": "nodes", "count": 533_536},
        {"type": "ways", "count": 84_264},
        {"type": "relations", "count": 579},
    ]
}

_TAG_COMBINATIONS_RESPONSE = {
    "data": [
        {"other_key": "name", "other_value": "", "together_count": 542_553, "to_fraction": 0.877},
        {"other_key": "cuisine", "other_value": "", "together_count": 180_533, "to_fraction": 0.292},
    ]
}


class TestGetKeyValues:
    def test_returns_values_above_min_count(self) -> None:
        with patch("taginfo.httpx.get", return_value=_mock_response(_KEY_VALUES_RESPONSE)):
            values = get_key_values("amenity", min_count=10_000)
        assert len(values) == 2  # rare_tag (500) filtered out
        assert values[0]["value"] == "cafe"
        assert values[1]["value"] == "restaurant"

    def test_returns_empty_on_error(self) -> None:
        with patch("taginfo.httpx.get", side_effect=Exception("timeout")):
            values = get_key_values("amenity")
        assert values == []

    def test_passes_custom_endpoint(self) -> None:
        with patch("taginfo.httpx.get", return_value=_mock_response({"data": []})) as mock_get:
            get_key_values("amenity", endpoint="https://custom.example.com")
        assert "custom.example.com" in mock_get.call_args[0][0]

    def test_all_filtered_when_min_count_high(self) -> None:
        with patch("taginfo.httpx.get", return_value=_mock_response(_KEY_VALUES_RESPONSE)):
            values = get_key_values("amenity", min_count=2_000_000)
        assert values == []


class TestGetTagStats:
    def test_returns_counts_by_type(self) -> None:
        with patch("taginfo.httpx.get", return_value=_mock_response(_TAG_STATS_RESPONSE)):
            stats = get_tag_stats("amenity", "cafe")
        assert stats["all"] == 618_379
        assert stats["nodes"] == 533_536
        assert stats["ways"] == 84_264
        assert stats["relations"] == 579

    def test_returns_zeros_on_error(self) -> None:
        with patch("taginfo.httpx.get", side_effect=Exception("timeout")):
            stats = get_tag_stats("amenity", "cafe")
        assert stats == {"all": 0, "nodes": 0, "ways": 0, "relations": 0}

    def test_returns_zeros_on_empty_data(self) -> None:
        with patch("taginfo.httpx.get", return_value=_mock_response({"data": []})):
            stats = get_tag_stats("amenity", "nonexistent")
        assert stats["all"] == 0


class TestGetTagCombinations:
    def test_returns_combination_list(self) -> None:
        with patch("taginfo.httpx.get", return_value=_mock_response(_TAG_COMBINATIONS_RESPONSE)):
            combos = get_tag_combinations("amenity", "cafe")
        assert len(combos) == 2
        assert combos[0]["other_key"] == "name"
        assert combos[1]["other_key"] == "cuisine"

    def test_returns_empty_on_error(self) -> None:
        with patch("taginfo.httpx.get", side_effect=Exception("timeout")):
            combos = get_tag_combinations("amenity", "cafe")
        assert combos == []


class TestValidateTag:
    def test_valid_tag_above_threshold(self) -> None:
        with patch("taginfo.httpx.get", return_value=_mock_response(_TAG_STATS_RESPONSE)):
            assert validate_tag("amenity", "cafe") is True

    def test_invalid_tag_below_threshold(self) -> None:
        low_response = {"data": [{"type": "all", "count": 50}]}
        with patch("taginfo.httpx.get", return_value=_mock_response(low_response)):
            assert validate_tag("amenity", "nonexistent_tag") is False

    def test_error_returns_false(self) -> None:
        with patch("taginfo.httpx.get", side_effect=Exception("timeout")):
            assert validate_tag("amenity", "cafe") is False

    def test_custom_min_count(self) -> None:
        with patch("taginfo.httpx.get", return_value=_mock_response(_TAG_STATS_RESPONSE)):
            # 618_379 >= 500_000 → True
            assert validate_tag("amenity", "cafe", min_count=500_000) is True
            # 618_379 < 700_000 → False
            assert validate_tag("amenity", "cafe", min_count=700_000) is False
