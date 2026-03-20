"""Tests for generate_overpassql.py — mocking LLM and Overpass calls."""

import hashlib
from pathlib import Path
from unittest.mock import patch

from generate_overpassql import generate_overpassql, save_overpassql
from meta import GenerationMeta


def _make_meta(model: str = "test-model:7b") -> GenerationMeta:
    return GenerationMeta.create(model=model, temperature=0.01, num_predict=256, element_count=1)


class TestGenerateOverpassql:
    def test_extracts_code_block(self) -> None:
        llm_output = "Here is the query:\n```\n[out:json];nwr[amenity=cafe];out geom;\n```"
        with patch("generate_overpassql.ollama.generate", return_value={"response": llm_output}):
            query, reason = generate_overpassql("some prompt")
        assert query == "[out:json];nwr[amenity=cafe];out geom;"
        assert reason == ""

    def test_returns_none_when_no_code_block(self) -> None:
        llm_output = "I cannot generate a query for this."
        with patch("generate_overpassql.ollama.generate", return_value={"response": llm_output}):
            query, reason = generate_overpassql("some prompt")
        assert query is None
        assert reason == "no_code_block"

    def test_returns_none_when_too_many_lines(self) -> None:
        long_query = "\n".join([f"line{i}" for i in range(25)])
        llm_output = f"```\n{long_query}\n```"
        with patch("generate_overpassql.ollama.generate", return_value={"response": llm_output}):
            query, reason = generate_overpassql("some prompt")
        assert query is None
        assert reason == "too_many_lines"

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
        meta = _make_meta()
        save_overpassql(self.QUERY, str(base), meta, tmp_root=str(tmp_path / "tmp"))

        slug = meta.model_slug
        output = base / f"output-{slug}.overpassql"
        assert output.exists()
        assert output.read_text() == self.QUERY + "\n"

    def test_writes_meta_json(self, tmp_path: Path) -> None:
        base = tmp_path / "entry"
        base.mkdir()
        meta = _make_meta()
        save_overpassql(self.QUERY, str(base), meta, tmp_root=str(tmp_path / "tmp"))

        slug = meta.model_slug
        meta_file = base / f"output-{slug}.meta.json"
        assert meta_file.exists()

    def test_writes_to_tmp_dedup_store(self, tmp_path: Path) -> None:
        base = tmp_path / "entry"
        base.mkdir()
        tmp_root = tmp_path / "tmp"
        meta = _make_meta()
        save_overpassql(self.QUERY, str(base), meta, tmp_root=str(tmp_root))

        query_hash = hashlib.md5(self.QUERY.encode("utf-8")).hexdigest()
        slug = meta.model_slug
        tmp_output = tmp_root / query_hash / f"output-{slug}.overpassql"
        assert tmp_output.exists()

    def test_idempotent(self, tmp_path: Path) -> None:
        base = tmp_path / "entry"
        base.mkdir()
        tmp_root = str(tmp_path / "tmp")
        meta = _make_meta()
        save_overpassql(self.QUERY, str(base), meta, tmp_root=tmp_root)
        save_overpassql(self.QUERY, str(base), meta, tmp_root=tmp_root)  # should not raise

    def test_returns_save_path(self, tmp_path: Path) -> None:
        base = tmp_path / "entry"
        base.mkdir()
        meta = _make_meta()
        saved = save_overpassql(self.QUERY, str(base), meta, tmp_root=str(tmp_path / "tmp"))
        assert saved.endswith(f"output-{meta.model_slug}.overpassql")
