"""Tests for compile.py — collect_text2geoql_files."""

from pathlib import Path

from compile import collect_text2geoql_files


class TestCollectText2GeoqlFiles:
    def test_collects_paired_entry(self, tmp_path: Path) -> None:
        d = tmp_path / "entry"
        d.mkdir()
        (d / "input-trident.txt").write_text("AreaWithConcern: Taito, Tokyo, Japan; Cafes\n")
        (d / "output-001.overpassql").write_text("[out:json];nwr[amenity=cafe];out geom;\n")

        result = collect_text2geoql_files(str(tmp_path))

        assert len(result) == 1
        assert result[0]["input"] == "AreaWithConcern: Taito, Tokyo, Japan; Cafes"
        assert result[0]["input_type"] == "trident"
        assert result[0]["output_type"] == "overpassql"
        assert "[out:json]" in result[0]["output"]

    def test_skips_entry_without_output(self, tmp_path: Path) -> None:
        d = tmp_path / "entry"
        d.mkdir()
        (d / "input-trident.txt").write_text("AreaWithConcern: Seoul, South Korea; Museums\n")

        result = collect_text2geoql_files(str(tmp_path))
        assert result == []

    def test_collects_multiple_outputs_for_one_input(self, tmp_path: Path) -> None:
        d = tmp_path / "entry"
        d.mkdir()
        (d / "input-trident.txt").write_text("AreaWithConcern: Taito, Tokyo, Japan; Parks\n")
        (d / "output-001.overpassql").write_text("query1")
        (d / "output-002.overpassql").write_text("query2")

        result = collect_text2geoql_files(str(tmp_path))
        assert len(result) == 2

    def test_returns_empty_for_empty_dir(self, tmp_path: Path) -> None:
        result = collect_text2geoql_files(str(tmp_path))
        assert result == []

    def test_collects_multiple_entries(self, tmp_path: Path) -> None:
        for name in ("a", "b"):
            d = tmp_path / name
            d.mkdir()
            (d / "input-trident.txt").write_text(f"AreaWithConcern: {name}; Cafes\n")
            (d / "output-001.overpassql").write_text(f"query_{name}")

        result = collect_text2geoql_files(str(tmp_path))
        assert len(result) == 2
