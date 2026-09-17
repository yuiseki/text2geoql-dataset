"""Tests for generate_overpassql.py — mocking LLM and Overpass calls."""

import hashlib
from pathlib import Path
from unittest.mock import MagicMock, patch

from generate_overpassql import (
    PROMPT_PREFIX,
    build_prompt,
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


class _FakeEmbeddings:
    """Deterministic embeddings: one axis per keyword, so similarity is checkable by hand.

    Chroma and InMemoryVectorStore both talk to an embedding model through
    embed_documents/embed_query only, so a fake here exercises the real
    selector path without Ollama.
    """

    KEYWORDS = ("cafe", "hotel", "museum", "shrine")

    def _vector(self, text: str) -> list[float]:
        lowered = text.lower()
        return [1.0 if word in lowered else 0.0 for word in self.KEYWORDS]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._vector(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._vector(text)


class TestBuildPrompt:
    """build_prompt picks the k nearest examples through the vector store."""

    CONCERNS = ("Cafes", "Hotels", "Museums", "Shrines")

    def _make_data_dir(self, tmp_path: Path) -> str:
        for index, concern in enumerate(self.CONCERNS):
            entry = tmp_path / f"entry{index}"
            entry.mkdir()
            instruct = f"AreaWithConcern: Taito, Tokyo, Japan; {concern}"
            (entry / "input-trident.txt").write_text(instruct)
            (entry / "output-test.overpassql").write_text(f"// query for {concern}")
        return str(tmp_path)

    def test_includes_the_matching_example(self, tmp_path: Path) -> None:
        data_dir = self._make_data_dir(tmp_path)
        with patch("generate_overpassql.OllamaEmbeddings", return_value=_FakeEmbeddings()):
            prompt = build_prompt("AreaWithConcern: Shibuya, Tokyo, Japan; Cafes", data_dir)

        assert "// query for Cafes" in prompt

    def test_excludes_examples_of_other_concerns(self, tmp_path: Path) -> None:
        data_dir = self._make_data_dir(tmp_path)
        with patch("generate_overpassql.OllamaEmbeddings", return_value=_FakeEmbeddings()):
            prompt = build_prompt("AreaWithConcern: Shibuya, Tokyo, Japan; Cafes", data_dir)

        for concern in ("Hotels", "Museums", "Shrines"):
            assert f"// query for {concern}" not in prompt

    def test_keeps_the_question_and_the_prefix(self, tmp_path: Path) -> None:
        data_dir = self._make_data_dir(tmp_path)
        instruct = "AreaWithConcern: Shibuya, Tokyo, Japan; Cafes"
        with patch("generate_overpassql.OllamaEmbeddings", return_value=_FakeEmbeddings()):
            prompt = build_prompt(instruct, data_dir)

        assert prompt.startswith(PROMPT_PREFIX)
        assert prompt.rstrip().endswith(f"Input:\n{instruct}\n\nOutput:")

    def test_no_matching_example_still_builds_a_prompt(self, tmp_path: Path) -> None:
        data_dir = self._make_data_dir(tmp_path)
        instruct = "AreaWithConcern: Shibuya, Tokyo, Japan; Aquariums"
        with patch("generate_overpassql.OllamaEmbeddings", return_value=_FakeEmbeddings()):
            prompt = build_prompt(instruct, data_dir)

        assert prompt.startswith(PROMPT_PREFIX)
        assert instruct in prompt


class _RankingEmbeddings:
    """One axis per word of the query, so nearness is decided by word overlap.

    The axes are chosen so cosine and L2 rank these examples identically —
    the assertions hold whichever metric the vector store defaults to.
    """

    AXES = ("shibuya", "tokyo", "japan", "asia", "cafes")

    def _vector(self, text: str) -> list[float]:
        lowered = text.lower()
        return [1.0 if word in lowered else 0.0 for word in self.AXES]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._vector(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._vector(text)


class TestBuildPromptRanking:
    """The k=4 nearest of five candidates, all of which pass the concern filter."""

    QUESTION = "AreaWithConcern: Shibuya, Tokyo, Japan; Cafes"
    EXAMPLES = (
        ("AreaWithConcern: Shibuya, Tokyo, Japan; Cafes", "// nearest"),
        ("AreaWithConcern: Taito, Tokyo, Japan; Cafes", "// second"),
        ("AreaWithConcern: Osaka, Japan; Cafes", "// third"),
        ("AreaWithConcern: Paris, France; Cafes", "// fourth"),
        ("AreaWithConcern: Seoul, South Korea; Cafes", "// farthest, somewhere in asia"),
    )

    def _make_data_dir(self, tmp_path: Path) -> str:
        for index, (instruct, query) in enumerate(self.EXAMPLES):
            entry = tmp_path / f"entry{index}"
            entry.mkdir()
            (entry / "input-trident.txt").write_text(instruct)
            (entry / "output-test.overpassql").write_text(query)
        return str(tmp_path)

    def test_keeps_the_four_nearest_and_drops_the_farthest(self, tmp_path: Path) -> None:
        data_dir = self._make_data_dir(tmp_path)
        with patch("generate_overpassql.OllamaEmbeddings", return_value=_RankingEmbeddings()):
            prompt = build_prompt(self.QUESTION, data_dir)

        for kept in ("// nearest", "// second", "// third", "// fourth"):
            assert kept in prompt
        assert "// farthest" not in prompt


class TestBuildPromptIsolation:
    """Two calls in one process must not share examples.

    batch_generate and benchmark_models both call build_prompt in a loop, so a
    store that survives the call would mix concerns across entries.
    """

    def _make_data_dir(self, tmp_path: Path) -> str:
        for index, (concern, query) in enumerate((("Cafes", "// cafe"), ("Hotels", "// hotel"))):
            entry = tmp_path / f"entry{index}"
            entry.mkdir()
            (entry / "input-trident.txt").write_text(
                f"AreaWithConcern: Taito, Tokyo, Japan; {concern}"
            )
            (entry / "output-test.overpassql").write_text(query)
        return str(tmp_path)

    def test_second_call_does_not_see_the_first_call_examples(self, tmp_path: Path) -> None:
        data_dir = self._make_data_dir(tmp_path)
        with patch("generate_overpassql.OllamaEmbeddings", return_value=_FakeEmbeddings()):
            first = build_prompt("AreaWithConcern: Shibuya, Tokyo, Japan; Cafes", data_dir)
            second = build_prompt("AreaWithConcern: Shibuya, Tokyo, Japan; Hotels", data_dir)

        assert "// cafe" in first and "// hotel" not in first
        assert "// hotel" in second
        assert "// cafe" not in second
