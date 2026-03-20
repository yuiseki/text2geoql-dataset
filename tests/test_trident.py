"""Tests for trident.py pure parsing functions."""

from trident import (
    parse_filter_type,
    parse_filter_concern,
    parse_filter_area,
    build_area_with_concern,
    area_path_from_trident,
)


class TestParseFilterType:
    def test_area_with_concern(self) -> None:
        assert parse_filter_type("AreaWithConcern: Taito, Tokyo, Japan; Cafes") == "AreaWithConcern"

    def test_area(self) -> None:
        assert parse_filter_type("Area: Seoul, South Korea") == "Area"

    def test_subarea(self) -> None:
        assert parse_filter_type("SubArea: Shinjuku, Tokyo, Japan") == "SubArea"


class TestParseFilterConcern:
    def test_single_word(self) -> None:
        assert parse_filter_concern("AreaWithConcern: Taito, Tokyo, Japan; Cafes") == "Cafes"

    def test_multi_word(self) -> None:
        assert parse_filter_concern("AreaWithConcern: Seoul, South Korea; Train Stations") == "Train Stations"

    def test_no_semicolon(self) -> None:
        # Without "; ", returns the whole string (area-only TRIDENT)
        assert parse_filter_concern("Area: Taito, Tokyo, Japan") == "Area: Taito, Tokyo, Japan"


class TestParseFilterArea:
    def test_district_level(self) -> None:
        assert parse_filter_area("AreaWithConcern: Taito, Tokyo, Japan; Cafes") == "Taito"

    def test_city_level(self) -> None:
        assert parse_filter_area("AreaWithConcern: Seoul, South Korea; Museums") == "Seoul"

    def test_strips_whitespace(self) -> None:
        assert parse_filter_area("AreaWithConcern:  Shibuya, Tokyo, Japan; Parks") == "Shibuya"


class TestBuildAreaWithConcern:
    def test_basic(self) -> None:
        result = build_area_with_concern("Taito, Tokyo, Japan", "Cafes")
        assert result == "AreaWithConcern: Taito, Tokyo, Japan; Cafes"

    def test_roundtrip_concern(self) -> None:
        original = "AreaWithConcern: Seoul, South Korea; Train Stations"
        # area is just the first segment; build full area string separately
        assert build_area_with_concern("Seoul, South Korea", "Train Stations") == original


class TestAreaPathFromTrident:
    def test_three_level(self) -> None:
        result = area_path_from_trident("AreaWithConcern: Taito, Tokyo, Japan; Cafes")
        assert result == "Japan/Tokyo/Taito"

    def test_two_level(self) -> None:
        result = area_path_from_trident("AreaWithConcern: Seoul, South Korea; Museums")
        assert result == "South Korea/Seoul"

    def test_preserves_spaces(self) -> None:
        result = area_path_from_trident("AreaWithConcern: New York, United States; Parks")
        assert result == "United States/New York"
