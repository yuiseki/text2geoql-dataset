"""Tests for batch_generate.py."""

from pathlib import Path

from batch_generate import find_missing_entries


class TestFindMissingEntries:
    def test_finds_area_with_concern_without_output(self, tmp_path: Path) -> None:
        d = tmp_path / "concerns" / "amenity" / "cafe" / "Japan" / "Tokyo" / "Shinjuku"
        d.mkdir(parents=True)
        (d / "input-trident.txt").write_text("AreaWithConcern: Shinjuku, Tokyo, Japan; Cafes\n")
        result = find_missing_entries(str(tmp_path))
        assert str(d) in result

    def test_skips_entry_with_existing_output(self, tmp_path: Path) -> None:
        d = tmp_path / "concerns" / "amenity" / "cafe" / "Japan" / "Tokyo" / "Shinjuku"
        d.mkdir(parents=True)
        (d / "input-trident.txt").write_text("AreaWithConcern: Shinjuku, Tokyo, Japan; Cafes\n")
        (d / "output-qwen2.5-coder-3b.overpassql").write_text("[out:json];nwr;out geom;\n")
        result = find_missing_entries(str(tmp_path))
        assert str(d) not in result

    def test_skips_entry_with_not_found_record(self, tmp_path: Path) -> None:
        d = tmp_path / "concerns" / "amenity" / "cafe" / "Japan" / "Tokyo" / "Shibuya"
        d.mkdir(parents=True)
        (d / "input-trident.txt").write_text("AreaWithConcern: Shibuya, Tokyo, Japan; Cafes\n")
        (d / "not-found-qwen2.5-coder-3b.json").write_text('{"reason": "zero_results"}\n')
        result = find_missing_entries(str(tmp_path))
        assert str(d) not in result

    def test_skips_non_area_with_concern_entries(self, tmp_path: Path) -> None:
        d = tmp_path / "administrative" / "Japan" / "Tokyo"
        d.mkdir(parents=True)
        (d / "input-trident.txt").write_text("Area: Tokyo, Japan\n")
        result = find_missing_entries(str(tmp_path))
        assert str(d) not in result

    def test_skips_dirs_without_input_trident(self, tmp_path: Path) -> None:
        d = tmp_path / "some" / "random" / "dir"
        d.mkdir(parents=True)
        (d / "output-model.overpassql").write_text("[out:json];nwr;out geom;\n")
        result = find_missing_entries(str(tmp_path))
        assert str(d) not in result

    def test_returns_multiple_missing(self, tmp_path: Path) -> None:
        for ward in ["Shinjuku", "Shibuya", "Taito"]:
            d = tmp_path / "concerns" / "amenity" / "cafe" / "Japan" / "Tokyo" / ward
            d.mkdir(parents=True)
            (d / "input-trident.txt").write_text(f"AreaWithConcern: {ward}, Tokyo, Japan; Cafes\n")
        result = find_missing_entries(str(tmp_path))
        assert len(result) == 3
