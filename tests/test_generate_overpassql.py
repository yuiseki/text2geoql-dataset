"""Tests for generate_overpassql.py — mocking LLM and Overpass calls."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from generate_overpassql import generate_overpassql, save_overpassql


class TestGenerateOverpassql:
    def _mock_response(self, text: str) -> MagicMock:
        m = MagicMock()
        m.__getitem__ = lambda self, key: text if key == "response" else None
        return m

    def test_extracts_code_block(self) -> None:
        llm_output = "Here is the query:\n```\n[out:json];nwr[amenity=cafe];out geom;\n```"
        with patch("generate_overpassql.ollama.generate", return_value={"response": llm_output}):
            result = generate_overpassql("some prompt")
        assert result == "[out:json];nwr[amenity=cafe];out geom;"

    def test_returns_none_when_no_code_block(self) -> None:
        llm_output = "I cannot generate a query for this."
        with patch("generate_overpassql.ollama.generate", return_value={"response": llm_output}):
            result = generate_overpassql("some prompt")
        assert result is None

    def test_returns_none_when_too_many_lines(self) -> None:
        long_query = "\n".join([f"line{i}" for i in range(25)])
        llm_output = f"```\n{long_query}\n```"
        with patch("generate_overpassql.ollama.generate", return_value={"response": llm_output}):
            result = generate_overpassql("some prompt")
        assert result is None

    def test_uses_configured_model(self) -> None:
        llm_output = "```\n[out:json];out;\n```"
        with patch("generate_overpassql.ollama.generate", return_value={"response": llm_output}) as mock_gen:
            generate_overpassql("prompt", model="custom-model:7b")
        assert "custom-model:7b" in str(mock_gen.call_args)


class TestSaveOverpassql:
    QUERY = "[out:json][timeout:30000];\nnwr[amenity=cafe];\nout geom;\n"

    def test_writes_to_base_path(self, tmp_path: Path) -> None:
        base = tmp_path / "entry"
        base.mkdir()
        save_overpassql(self.QUERY, str(base), tmp_root=str(tmp_path / "tmp"))

        output = base / "output-001.overpassql"
        assert output.exists()
        assert output.read_text() == self.QUERY + "\n"

    def test_writes_to_tmp_dedup_store(self, tmp_path: Path) -> None:
        base = tmp_path / "entry"
        base.mkdir()
        tmp_root = tmp_path / "tmp"
        save_overpassql(self.QUERY, str(base), tmp_root=str(tmp_root))

        # tmp dir is named by md5 hash of the query
        import hashlib
        query_hash = hashlib.md5(self.QUERY.encode("utf-8")).hexdigest()
        tmp_output = tmp_root / query_hash / "output-001.overpassql"
        assert tmp_output.exists()

    def test_idempotent(self, tmp_path: Path) -> None:
        base = tmp_path / "entry"
        base.mkdir()
        tmp_root = str(tmp_path / "tmp")
        save_overpassql(self.QUERY, str(base), tmp_root=tmp_root)
        save_overpassql(self.QUERY, str(base), tmp_root=tmp_root)  # should not raise
