"""Tests for find_orphan_trident.py."""

from pathlib import Path

from find_orphan_trident import find_orphan_trident


class TestFindOrphanTrident:
    def test_finds_orphan(self, tmp_path: Path) -> None:
        d = tmp_path / "entry"
        d.mkdir()
        (d / "input-trident.txt").write_text("AreaWithConcern: Taito, Tokyo, Japan; Cafes\n")
        result = find_orphan_trident(str(tmp_path))
        assert str(d) in result

    def test_ignores_when_output_exists(self, tmp_path: Path) -> None:
        d = tmp_path / "entry"
        d.mkdir()
        (d / "input-trident.txt").write_text("AreaWithConcern: Taito, Tokyo, Japan; Cafes\n")
        (d / "output-001.overpassql").write_text("[out:json];nwr;out geom;\n")
        result = find_orphan_trident(str(tmp_path))
        assert str(d) not in result

    def test_ignores_when_not_found_exists(self, tmp_path: Path) -> None:
        d = tmp_path / "entry"
        d.mkdir()
        (d / "input-trident.txt").write_text("AreaWithConcern: Seoul, South Korea; Parks\n")
        (d / "not-found.txt").write_text("")
        result = find_orphan_trident(str(tmp_path))
        assert str(d) not in result

    def test_ignores_dir_without_input_trident(self, tmp_path: Path) -> None:
        d = tmp_path / "entry"
        d.mkdir()
        (d / "some_other_file.txt").write_text("hello")
        result = find_orphan_trident(str(tmp_path))
        assert result == []

    def test_finds_multiple_orphans(self, tmp_path: Path) -> None:
        for name in ("a", "b", "c"):
            d = tmp_path / name
            d.mkdir()
            (d / "input-trident.txt").write_text(f"AreaWithConcern: {name}; Cafes\n")
        result = find_orphan_trident(str(tmp_path))
        assert len(result) == 3

    def test_returns_list_not_none(self, tmp_path: Path) -> None:
        result = find_orphan_trident(str(tmp_path))
        assert isinstance(result, list)
