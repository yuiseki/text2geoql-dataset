"""Tests for generate_trident.py helper functions."""

from pathlib import Path

from generate_trident import (
    load_examples,
    extract_seed_areas,
    generate_missing_tridents,
    write_trident_files,
)


class TestLoadExamples:
    def test_loads_non_empty_entries(self, tmp_path: Path) -> None:
        d = tmp_path / "entry"
        d.mkdir()
        (d / "input-trident.txt").write_text("Area: Taito, Tokyo, Japan\n")

        result = load_examples(str(tmp_path))
        assert len(result) == 1
        assert result[0]["input"] == "Area: Taito, Tokyo, Japan"

    def test_skips_empty_entries(self, tmp_path: Path) -> None:
        d = tmp_path / "entry"
        d.mkdir()
        (d / "input-trident.txt").write_text("  \n")

        result = load_examples(str(tmp_path))
        assert result == []

    def test_returns_path_field(self, tmp_path: Path) -> None:
        d = tmp_path / "entry"
        d.mkdir()
        (d / "input-trident.txt").write_text("Area: Seoul, South Korea\n")

        result = load_examples(str(tmp_path))
        assert "path" in result[0]
        assert result[0]["path"].endswith("input-trident.txt")


class TestExtractSeedAreas:
    def test_extracts_area_with_three_or_more_commas(self) -> None:
        # Non-Seoul/HK areas require at least 3 commas in the full string
        examples = [{"input": "Area: Taito, Tokyo, Kanto, Japan", "path": ""}]
        result = extract_seed_areas(examples)
        assert "Taito, Tokyo, Kanto, Japan" in result

    def test_skips_area_with_only_two_commas(self) -> None:
        # "Area: Taito, Tokyo, Japan" has 2 commas → skipped for non-Seoul/HK
        examples = [{"input": "Area: Taito, Tokyo, Japan", "path": ""}]
        result = extract_seed_areas(examples)
        assert result == []

    def test_skips_area_with_semicolon(self) -> None:
        examples = [{"input": "Area: Taito, Tokyo, Japan; something", "path": ""}]
        result = extract_seed_areas(examples)
        assert result == []

    def test_skips_area_with_too_few_commas(self) -> None:
        examples = [{"input": "Area: Tokyo, Japan", "path": ""}]
        result = extract_seed_areas(examples)
        assert result == []

    def test_seoul_requires_two_or_more_commas(self) -> None:
        # Seoul areas require at least 2 commas
        examples = [{"input": "Area: Gangnam-gu, Seoul, South Korea", "path": ""}]
        result = extract_seed_areas(examples)
        assert "Gangnam-gu, Seoul, South Korea" in result

    def test_seoul_with_one_comma_is_skipped(self) -> None:
        examples = [{"input": "Area: Seoul, South Korea", "path": ""}]
        result = extract_seed_areas(examples)
        assert result == []

    def test_skips_area_with_concern(self) -> None:
        examples = [{"input": "AreaWithConcern: Taito, Tokyo, Japan; Cafes", "path": ""}]
        result = extract_seed_areas(examples)
        assert result == []

    def test_skips_subarea(self) -> None:
        examples = [{"input": "SubArea: Taito, Tokyo, Japan", "path": ""}]
        result = extract_seed_areas(examples)
        assert result == []

    def test_deduplicates(self) -> None:
        examples = [
            {"input": "Area: Taito, Tokyo, Kanto, Japan", "path": ""},
            {"input": "Area: Taito, Tokyo, Kanto, Japan", "path": ""},
        ]
        result = extract_seed_areas(examples)
        assert result.count("Taito, Tokyo, Kanto, Japan") == 1


class TestGenerateMissingTridents:
    def test_generates_new_entry(self) -> None:
        seed_areas = ["Taito, Tokyo, Japan"]
        seed_concerns = [{"concern": "Cafes", "base_path": "data/concerns/amenity/cafe"}]
        existing: set[str] = set()

        result = generate_missing_tridents(seed_areas, seed_concerns, existing)

        assert len(result) == 1
        assert result[0]["area_with_concern"] == "AreaWithConcern: Taito, Tokyo, Japan; Cafes"
        assert result[0]["base_path"] == "data/concerns/amenity/cafe"

    def test_skips_existing_entry(self) -> None:
        seed_areas = ["Taito, Tokyo, Japan"]
        seed_concerns = [{"concern": "Cafes", "base_path": "data/concerns/amenity/cafe"}]
        existing = {"AreaWithConcern: Taito, Tokyo, Japan; Cafes"}

        result = generate_missing_tridents(seed_areas, seed_concerns, existing)
        assert result == []

    def test_cross_product(self) -> None:
        seed_areas = ["Taito, Tokyo, Japan", "Seoul, South Korea"]
        seed_concerns = [
            {"concern": "Cafes", "base_path": "path/cafe"},
            {"concern": "Parks", "base_path": "path/park"},
        ]
        result = generate_missing_tridents(seed_areas, seed_concerns, set())
        assert len(result) == 4


class TestWriteTridentFiles:
    def test_writes_input_trident_txt(self, tmp_path: Path) -> None:
        items = [
            {
                "area_with_concern": "AreaWithConcern: Taito, Tokyo, Japan; Cafes",
                "base_path": str(tmp_path),
            }
        ]
        write_trident_files(items)

        expected = tmp_path / "Japan" / "Tokyo" / "Taito" / "input-trident.txt"
        assert expected.exists()
        assert expected.read_text().strip() == "AreaWithConcern: Taito, Tokyo, Japan; Cafes"

    def test_idempotent(self, tmp_path: Path) -> None:
        items = [
            {
                "area_with_concern": "AreaWithConcern: Seoul, South Korea; Museums",
                "base_path": str(tmp_path),
            }
        ]
        write_trident_files(items)
        write_trident_files(items)  # second call should not raise

        expected = tmp_path / "South Korea" / "Seoul" / "input-trident.txt"
        assert expected.exists()
