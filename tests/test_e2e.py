"""End-to-end tests: real Ollama inference + real self-hosted Overpass API.

Run with:
    uv run pytest -m e2e -v

These tests are excluded from the default test run (addopts = "-m 'not e2e'").
They require:
  - Ollama running locally with qwen2.5-coder:0.5b pulled
  - Self-hosted Overpass API reachable at https://overpass.yuiseki.net/api/interpreter
  - The ./data directory present (for few-shot examples)
"""

import os
from pathlib import Path

import pytest

from generate_overpassql import run
from overpass import count_elements

# Smallest available coder model — fast enough for CI-style e2e
E2E_MODEL = os.environ.get("TEXT2GEOQL_E2E_MODEL", "qwen2.5-coder:0.5b")

# Use the real data dir relative to repo root so few-shot examples are available
REPO_ROOT = Path(__file__).parent.parent
DATA_DIR = str(REPO_ROOT / "data")


@pytest.mark.e2e
class TestRunPipeline:
    def test_generates_or_marks_not_found(self, tmp_path: Path) -> None:
        """Full pipeline: TRIDENT → LLM → Overpass validation → file saved."""
        # Simple, well-known query: cafes in Taito, Tokyo
        instruct = "AreaWithConcern: Taito, Tokyo, Japan; Cafes"
        (tmp_path / "input-trident.txt").write_text(instruct + "\n")

        run(
            base_path=str(tmp_path),
            data_dir=DATA_DIR,
            tmp_root=str(tmp_path / "tmp"),
            model=E2E_MODEL,
        )

        output = tmp_path / "output-001.overpassql"
        not_found = tmp_path / "not-found.txt"
        # Either a valid query was saved or the model produced unusable output
        assert output.exists() or not_found.exists(), (
            "run() must produce either output-001.overpassql or not-found.txt"
        )

    def test_saved_query_returns_elements(self, tmp_path: Path) -> None:
        """If a query is saved, it must return at least one element from Overpass."""
        instruct = "AreaWithConcern: Taito, Tokyo, Japan; Cafes"
        (tmp_path / "input-trident.txt").write_text(instruct + "\n")

        run(
            base_path=str(tmp_path),
            data_dir=DATA_DIR,
            tmp_root=str(tmp_path / "tmp"),
            model=E2E_MODEL,
        )

        output = tmp_path / "output-001.overpassql"
        if not output.exists():
            pytest.skip("LLM did not produce a valid query (not-found.txt created)")

        query = output.read_text().strip()
        n = count_elements(query)
        assert n > 0, f"Saved query returned 0 elements from Overpass:\n{query}"

    def test_idempotent_run(self, tmp_path: Path) -> None:
        """Running twice on the same directory must not raise and must not overwrite."""
        instruct = "AreaWithConcern: Taito, Tokyo, Japan; Cafes"
        (tmp_path / "input-trident.txt").write_text(instruct + "\n")

        run(base_path=str(tmp_path), data_dir=DATA_DIR, tmp_root=str(tmp_path / "tmp"), model=E2E_MODEL)

        output = tmp_path / "output-001.overpassql"
        mtime_after_first = output.stat().st_mtime if output.exists() else None

        run(base_path=str(tmp_path), data_dir=DATA_DIR, tmp_root=str(tmp_path / "tmp"), model=E2E_MODEL)

        if mtime_after_first is not None:
            assert output.stat().st_mtime == mtime_after_first, "Second run must not overwrite output"


@pytest.mark.e2e
class TestOverpassConnectivity:
    def test_self_hosted_overpass_reachable(self) -> None:
        """Sanity check: self-hosted Overpass returns elements for a known relation."""
        # relation 1543125 = Japan
        query = "[out:json][timeout:30];relation(1543125);out geom;"
        n = count_elements(query)
        assert n > 0, "Self-hosted Overpass API did not return elements for Japan relation"
