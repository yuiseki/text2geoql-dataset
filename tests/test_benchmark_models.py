"""Tests for benchmark_models.py — backend dispatch and model group registration."""

from benchmark_models import APERTUS_MODELS, MODEL_GROUPS, _model_backend


class TestModelBackendDispatch:
    def test_apertus_models_use_llama_server_backend(self) -> None:
        for name in APERTUS_MODELS:
            assert _model_backend(name) == "llama_server"

    def test_ollama_models_default_to_ollama_backend(self) -> None:
        assert _model_backend("qwen2.5-coder:0.5b") == "ollama"


class TestModelGroupsIntegrity:
    def test_apertus_group_matches_registry_keys(self) -> None:
        assert set(MODEL_GROUPS["apertus"]) == set(APERTUS_MODELS.keys())

    def test_apertus_group_has_four_variants(self) -> None:
        assert set(MODEL_GROUPS["apertus"]) == {
            "apertus-0.5b-base",
            "apertus-0.5b-instruct",
            "apertus-1.5b-base",
            "apertus-1.5b-instruct",
        }
