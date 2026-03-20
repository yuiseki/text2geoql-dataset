"""Benchmark multiple Ollama model sizes for Overpass QL generation quality.

Usage:
    uv run python src/benchmark_models.py
    uv run python src/benchmark_models.py --models qwen2.5-coder:0.5b qwen2.5-coder:1.5b
    uv run python src/benchmark_models.py --trials 3 --data-dir ./data

Output: JSON report written to ./tmp/benchmark-{timestamp}.json
        and a summary table printed to stdout.
"""

import argparse
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import ollama

from generate_overpassql import build_prompt, generate_overpassql
from meta import model_to_slug
from overpass import fetch_elements

# Candidate model sizes to probe (in ascending order)
DEFAULT_MODELS = [
    "qwen2.5-coder:0.5b",
    "qwen2.5-coder:1.5b",
    "qwen2.5-coder:3b",
    "qwen2.5-coder:7b",
    "qwen2.5-coder:14b",
    "qwen2.5-coder:32b",
    "qwen3-coder:30b",
]

# Fixed evaluation set: diverse TRIDENT instructions
EVAL_INSTRUCTIONS = [
    "AreaWithConcern: Taito, Tokyo, Japan; Cafes",
    "AreaWithConcern: Taito, Tokyo, Japan; Convenience Stores",
    "AreaWithConcern: Shinjuku, Tokyo, Japan; Hotels",
    "AreaWithConcern: Gangnam-gu, Seoul, South Korea; Restaurants",
    "AreaWithConcern: Shibuya, Tokyo, Japan; Parks",
]

REPO_ROOT = Path(__file__).parent.parent
DEFAULT_DATA_DIR = str(REPO_ROOT / "data")
DEFAULT_TMP_DIR = str(REPO_ROOT / "tmp")


def _is_model_available(model: str) -> bool:
    """Return True if the model is pulled in local Ollama."""
    try:
        local = ollama.list()
        names = [m.model for m in local.models]
        return model in names
    except Exception:
        return False


def _probe_model(
    model: str,
    instructions: list[str],
    data_dir: str,
    trials: int,
    temperature: float,
    num_predict: int,
) -> dict:
    """Run all eval instructions against one model and collect metrics."""
    results: list[dict[str, object]] = []
    for instruct in instructions:
        for trial in range(trials):
            t0 = time.monotonic()
            try:
                prompt = build_prompt(instruct, data_dir)
                query, failure_reason = generate_overpassql(
                    prompt,
                    model=model,
                    temperature=temperature,
                    num_predict=num_predict,
                )
                elapsed = time.monotonic() - t0

                if query is None:
                    results.append({
                        "instruct": instruct,
                        "trial": trial,
                        "success": False,
                        "failure_reason": failure_reason,
                        "element_count": 0,
                        "elapsed_s": round(elapsed, 2),
                        "query": None,
                    })
                    continue

                try:
                    elements = fetch_elements(query)
                    n = len(elements)
                except Exception as e:
                    results.append({
                        "instruct": instruct,
                        "trial": trial,
                        "success": False,
                        "failure_reason": f"api_error: {e}",
                        "element_count": 0,
                        "elapsed_s": round(elapsed, 2),
                        "query": query,
                    })
                    continue

                results.append({
                    "instruct": instruct,
                    "trial": trial,
                    "success": n > 0,
                    "failure_reason": "" if n > 0 else "zero_results",
                    "element_count": n,
                    "elapsed_s": round(elapsed, 2),
                    "query": query,
                })

            except Exception as e:
                elapsed = time.monotonic() - t0
                results.append({
                    "instruct": instruct,
                    "trial": trial,
                    "success": False,
                    "failure_reason": f"exception: {e}",
                    "element_count": 0,
                    "elapsed_s": round(elapsed, 2),
                    "query": None,
                })

    total = len(results)
    success_count = sum(1 for r in results if r["success"] is True)
    code_block_failures = sum(1 for r in results if r["failure_reason"] == "no_code_block")
    too_many_lines = sum(1 for r in results if r["failure_reason"] == "too_many_lines")
    zero_results_count = sum(1 for r in results if r["failure_reason"] == "zero_results")
    avg_elapsed = round(sum(r["elapsed_s"] for r in results if isinstance(r["elapsed_s"], (int, float))) / total, 2) if total else 0

    return {
        "model": model,
        "model_slug": model_to_slug(model),
        "total": total,
        "success_count": success_count,
        "success_rate": round(success_count / total, 3) if total else 0,
        "no_code_block": code_block_failures,
        "too_many_lines": too_many_lines,
        "zero_results": zero_results_count,
        "avg_elapsed_s": avg_elapsed,
        "results": results,
    }


def _print_summary(model_reports: list[dict]) -> None:
    header = f"{'Model':<28} {'Success':>8} {'Rate':>6} {'NoBlock':>8} {'TooLong':>8} {'ZeroRes':>8} {'AvgSec':>7}"
    print("\n" + "=" * len(header))
    print(header)
    print("-" * len(header))
    for r in model_reports:
        print(
            f"{r['model']:<28} "
            f"{r['success_count']:>5}/{r['total']:<2} "
            f"{r['success_rate']:>5.0%} "
            f"{r['no_code_block']:>8} "
            f"{r['too_many_lines']:>8} "
            f"{r['zero_results']:>8} "
            f"{r['avg_elapsed_s']:>7.1f}s"
        )
    print("=" * len(header))


def run_benchmark(
    models: list[str] | None = None,
    data_dir: str = DEFAULT_DATA_DIR,
    tmp_dir: str = DEFAULT_TMP_DIR,
    trials: int = 1,
    temperature: float = 0.01,
    num_predict: int = 256,
    skip_unavailable: bool = True,
) -> dict:
    if models is None:
        models = DEFAULT_MODELS

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    report: dict = {
        "benchmark_at": datetime.now(timezone.utc).isoformat(),
        "trials_per_instruction": trials,
        "temperature": temperature,
        "num_predict": num_predict,
        "instructions": EVAL_INSTRUCTIONS,
        "models": [],
    }

    for model in models:
        if skip_unavailable and not _is_model_available(model):
            print(f"[SKIP] {model} — not pulled locally")
            continue

        print(f"\n[RUN]  {model} ({trials} trial(s) × {len(EVAL_INSTRUCTIONS)} instructions) ...")
        model_report = _probe_model(
            model=model,
            instructions=EVAL_INSTRUCTIONS,
            data_dir=data_dir,
            trials=trials,
            temperature=temperature,
            num_predict=num_predict,
        )
        report["models"].append(model_report)
        print(f"       success {model_report['success_count']}/{model_report['total']}  "
              f"avg {model_report['avg_elapsed_s']}s/query")

    _print_summary(report["models"])

    os.makedirs(tmp_dir, exist_ok=True)
    out_path = os.path.join(tmp_dir, f"benchmark-{timestamp}.json")
    with open(out_path, "w") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"\nReport saved to: {out_path}")

    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--models", nargs="+", default=None, help="Model names to benchmark (default: all qwen2.5-coder sizes)")
    parser.add_argument("--data-dir", default=DEFAULT_DATA_DIR, help="Path to data dir with few-shot examples")
    parser.add_argument("--tmp-dir", default=DEFAULT_TMP_DIR, help="Directory to write the JSON report")
    parser.add_argument("--trials", type=int, default=1, help="Trials per instruction per model (default: 1)")
    parser.add_argument("--temperature", type=float, default=0.01)
    parser.add_argument("--num-predict", type=int, default=256)
    parser.add_argument("--include-unavailable", action="store_true", help="Attempt models not yet pulled (will error)")
    args = parser.parse_args()

    run_benchmark(
        models=args.models,
        data_dir=args.data_dir,
        tmp_dir=args.tmp_dir,
        trials=args.trials,
        temperature=args.temperature,
        num_predict=args.num_predict,
        skip_unavailable=not args.include_unavailable,
    )


if __name__ == "__main__":
    main()
