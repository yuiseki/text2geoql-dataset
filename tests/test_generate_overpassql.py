"""Tests for generate_overpassql.py — mocking LLM and Overpass calls."""

import hashlib
from pathlib import Path
from unittest.mock import MagicMock, patch

from generate_overpassql import (
    example_matches,
    generate_overpassql,
    generate_overpassql_llama_server,
    save_overpassql,
)
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


class TestGenerateOverpassqlLlamaServer:
    def test_extracts_code_block(self) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "content": "Here is the query:\n```\n[out:json];nwr[amenity=cafe];out geom;\n```"
        }
        mock_response.raise_for_status.return_value = None
        with patch("generate_overpassql.httpx.post", return_value=mock_response) as mock_post:
            query, reason = generate_overpassql_llama_server("some prompt", base_url="http://127.0.0.1:1234")
        assert query == "[out:json];nwr[amenity=cafe];out geom;"
        assert reason == ""
        args, kwargs = mock_post.call_args
        assert args[0] == "http://127.0.0.1:1234/completion"
        assert kwargs["json"]["prompt"] == "some prompt"

    def test_returns_none_when_no_code_block(self) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {"content": "I cannot generate a query for this."}
        mock_response.raise_for_status.return_value = None
        with patch("generate_overpassql.httpx.post", return_value=mock_response):
            query, reason = generate_overpassql_llama_server("some prompt", base_url="http://x")
        assert query is None
        assert reason == "no_code_block"

    def test_returns_none_when_too_many_lines(self) -> None:
        long_query = "\n".join([f"line{i}" for i in range(25)])
        mock_response = MagicMock()
        mock_response.json.return_value = {"content": f"```\n{long_query}\n```"}
        mock_response.raise_for_status.return_value = None
        with patch("generate_overpassql.httpx.post", return_value=mock_response):
            query, reason = generate_overpassql_llama_server("some prompt", base_url="http://x")
        assert query is None
        assert reason == "too_many_lines"

    def test_returns_server_error_on_connection_failure(self) -> None:
        with patch("generate_overpassql.httpx.post", side_effect=Exception("connection refused")):
            query, reason = generate_overpassql_llama_server("some prompt", base_url="http://x")
        assert query is None
        assert reason.startswith("server_error")


class TestExampleMatches:
    """Tests for the example_matches pure function."""

    def test_exact_match(self) -> None:
        assert example_matches(
            "AreaWithConcern: Taito, Tokyo, Japan; Cafes",
            "AreaWithConcern", "Cafes"
        )

    def test_case_insensitive_concern_uppercase_query(self) -> None:
        """'Convenience Stores' (uppercase S) matches dataset entry 'Convenience stores'."""
        assert example_matches(
            "AreaWithConcern: Taito, Tokyo, Japan; Convenience stores",
            "AreaWithConcern", "Convenience Stores"
        )

    def test_case_insensitive_concern_lowercase_query(self) -> None:
        """'convenience stores' (all lower) matches dataset entry 'Convenience Stores'."""
        assert example_matches(
            "AreaWithConcern: Taito, Tokyo, Japan; Convenience Stores",
            "AreaWithConcern", "convenience stores"
        )

    def test_unrelated_concern_not_matched(self) -> None:
        assert not example_matches(
            "AreaWithConcern: Taito, Tokyo, Japan; Cafes",
            "AreaWithConcern", "Hotels"
        )

    def test_wrong_filter_type_not_matched(self) -> None:
        assert not example_matches(
            "Area: Taito, Tokyo, Japan",
            "AreaWithConcern", "Cafes"
        )


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
