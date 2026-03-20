"""Tests for meta.py — GenerationMeta, FailureMeta, model_to_slug."""

import json
from pathlib import Path

from meta import FailureMeta, GenerationMeta, model_to_slug


class TestModelToSlug:
    def test_colon_replaced_by_dash(self) -> None:
        assert model_to_slug("qwen2.5-coder:14b") == "qwen2.5-coder-14b"

    def test_slash_replaced_by_dash(self) -> None:
        assert model_to_slug("hf.co/org/model:latest") == "hf.co-org-model-latest"

    def test_no_special_chars(self) -> None:
        assert model_to_slug("gemma3-12b") == "gemma3-12b"

    def test_gemma3(self) -> None:
        assert model_to_slug("gemma3:12b") == "gemma3-12b"


class TestGenerationMeta:
    def test_create_sets_fields(self) -> None:
        meta = GenerationMeta.create(model="qwen2.5-coder:14b", temperature=0.01, num_predict=256, element_count=5)
        assert meta.model == "qwen2.5-coder:14b"
        assert meta.model_slug == "qwen2.5-coder-14b"
        assert meta.temperature == 0.01
        assert meta.num_predict == 256
        assert meta.element_count == 5
        assert meta.generated_at != ""

    def test_save_and_load_roundtrip(self, tmp_path: Path) -> None:
        meta = GenerationMeta.create(model="gemma3:12b", temperature=0.5, num_predict=128, element_count=10)
        path = str(tmp_path / "meta.json")
        meta.save(path)

        loaded = GenerationMeta.load(path)
        assert loaded.model == meta.model
        assert loaded.model_slug == meta.model_slug
        assert loaded.temperature == meta.temperature
        assert loaded.num_predict == meta.num_predict
        assert loaded.element_count == meta.element_count
        assert loaded.generated_at == meta.generated_at

    def test_save_writes_valid_json(self, tmp_path: Path) -> None:
        meta = GenerationMeta.create(model="test:1b", temperature=0.0, num_predict=64, element_count=1)
        path = str(tmp_path / "meta.json")
        meta.save(path)

        with open(path) as f:
            data = json.load(f)
        assert data["model"] == "test:1b"
        assert data["model_slug"] == "test-1b"


class TestFailureMeta:
    def test_create_sets_fields(self) -> None:
        meta = FailureMeta.create(model="qwen2.5-coder:14b", reason="no_code_block")
        assert meta.model == "qwen2.5-coder:14b"
        assert meta.model_slug == "qwen2.5-coder-14b"
        assert meta.reason == "no_code_block"
        assert meta.query is None
        assert meta.generated_at != ""

    def test_create_with_query(self) -> None:
        meta = FailureMeta.create(model="test:7b", reason="api_error", query="[out:json];out;")
        assert meta.query == "[out:json];out;"

    def test_save_and_load_roundtrip(self, tmp_path: Path) -> None:
        meta = FailureMeta.create(model="gemma3:12b", reason="zero_results", query="some query")
        path = str(tmp_path / "not-found.json")
        meta.save(path)

        loaded = FailureMeta.load(path)
        assert loaded.model == meta.model
        assert loaded.model_slug == meta.model_slug
        assert loaded.reason == meta.reason
        assert loaded.query == meta.query
        assert loaded.generated_at == meta.generated_at

    def test_save_writes_valid_json(self, tmp_path: Path) -> None:
        meta = FailureMeta.create(model="test:1b", reason="too_many_lines")
        path = str(tmp_path / "not-found.json")
        meta.save(path)

        with open(path) as f:
            data = json.load(f)
        assert data["reason"] == "too_many_lines"
        assert data["query"] is None

    def test_all_failure_reasons(self) -> None:
        for reason in ("no_code_block", "too_many_lines", "zero_results", "api_error"):
            meta = FailureMeta.create(model="m:1b", reason=reason)  # type: ignore[arg-type]
            assert meta.reason == reason
