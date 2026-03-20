"""Benchmark multiple Ollama model sizes for Overpass QL generation quality.

Usage:
    # One model at a time (recommended — avoids long-running timeouts):
    uv run python src/benchmark_models.py --models qwen2.5-coder:0.5b
    uv run python src/benchmark_models.py --models qwen3:4b
    uv run python src/benchmark_models.py --models qwen3:4b --no-think

    # Named model groups:
    uv run python src/benchmark_models.py --group qwen2.5-coder
    uv run python src/benchmark_models.py --group qwen3
    uv run python src/benchmark_models.py --group qwen3.5
    uv run python src/benchmark_models.py --group gemma3
    uv run python src/benchmark_models.py --group granite4
    uv run python src/benchmark_models.py --group mistral
    uv run python src/benchmark_models.py --group gpt-oss

    # Custom options:
    uv run python src/benchmark_models.py --trials 3 --query-timeout 120

    # Compare think vs no-think for a qwen3 model:
    uv run python src/benchmark_models.py --models qwen3:4b --trials 3
    uv run python src/benchmark_models.py --models qwen3:4b --trials 3 --no-think

Output:
    Per-model JSON written immediately to tmp/benchmark-{slug}-{timestamp}.json
    Summary table printed after each model completes.
"""

import argparse
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from datetime import datetime, timezone
from pathlib import Path

import ollama

from generate_overpassql import build_prompt, generate_overpassql, default_num_predict
from meta import model_to_slug
from overpass import fetch_elements

# Named model groups (ascending parameter count within each family)
MODEL_GROUPS: dict[str, list[str]] = {
    "qwen2.5-coder": [
        "qwen2.5-coder:0.5b",
        "qwen2.5-coder:1.5b",
        "qwen2.5-coder:3b",
        "qwen2.5-coder:7b",
        "qwen2.5-coder:14b",
        "qwen2.5-coder:32b",
    ],
    "qwen3-coder": [
        "qwen3-coder:30b",
    ],
    "qwen3": [
        "qwen3:0.6b",
        "qwen3:1.7b",
        "qwen3:4b",
        "qwen3:8b",
        "qwen3:14b",
        "qwen3:30b",
        "qwen3:32b",
    ],
    "qwen3.5": [
        "qwen3.5:0.8b",
        "qwen3.5:2b",
        "qwen3.5:4b",
        "qwen3.5:9b",
        "qwen3.5:27b",
        "qwen3.5:35b",
    ],
    "gemma3": [
        "gemma3:270m",
        "gemma3:1b",
        "gemma3:4b",
        "gemma3:12b",
        "gemma3:27b",
    ],
    "granite4": [
        "granite4:350m",
        "granite4:1b",
        "granite4:3b",
        "granite4:micro-h",
        "granite4:tiny-h",
    ],
    "mistral": [
        "mistral:7b",
        "mistral-small3.2:24b",
        "devstral-small-2:24b",
    ],
    "gpt-oss": [
        "gpt-oss:20b",
        "gpt-oss-128k:20b",
        "gpt-oss:120b",
    ],
}

DEFAULT_GROUP = "qwen2.5-coder"
DEFAULT_MODELS = MODEL_GROUPS[DEFAULT_GROUP]

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
DEFAULT_QUERY_TIMEOUT = 90  # seconds per query (LLM + Overpass)


def _is_model_available(model: str) -> bool:
    """Return True if the model is pulled in local Ollama."""
    try:
        local = ollama.list()
        names = [m.model for m in local.models]
        return model in names
    except Exception:
        return False


def _run_one_query(
    instruct: str,
    model: str,
    data_dir: str,
    temperature: float,
    num_predict: int,
    think: bool | None,
) -> dict[str, object]:
    """Run a single instruction through LLM + Overpass. Returns a result dict."""
    t0 = time.monotonic()
    prompt = build_prompt(instruct, data_dir)
    effective_num_predict = max(num_predict, default_num_predict(model, think=think))
    query, failure_reason = generate_overpassql(
        prompt, model=model, temperature=temperature, num_predict=effective_num_predict, think=think
    )
    elapsed = time.monotonic() - t0

    if query is None:
        return {
            "instruct": instruct,
            "success": False,
            "failure_reason": failure_reason,
            "element_count": 0,
            "elapsed_s": round(elapsed, 2),
            "query": None,
        }

    try:
        elements = fetch_elements(query)
        n = len(elements)
    except Exception as e:
        return {
            "instruct": instruct,
            "success": False,
            "failure_reason": f"api_error: {e}",
            "element_count": 0,
            "elapsed_s": round(elapsed, 2),
            "query": query,
        }

    return {
        "instruct": instruct,
        "success": n > 0,
        "failure_reason": "" if n > 0 else "zero_results",
        "element_count": n,
        "elapsed_s": round(elapsed, 2),
        "query": query,
    }


def _probe_model(
    model: str,
    instructions: list[str],
    data_dir: str,
    trials: int,
    temperature: float,
    num_predict: int,
    query_timeout: int,
    think: bool | None,
) -> dict:
    """Run all eval instructions against one model with per-query timeout."""
    results: list[dict[str, object]] = []

    for instruct in instructions:
        for trial in range(trials):
            print(f"    [{trial+1}/{trials}] {instruct[:50]} ...", end=" ", flush=True)
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(
                    _run_one_query, instruct, model, data_dir, temperature, num_predict, think
                )
                try:
                    result = future.result(timeout=query_timeout)
                    result["trial"] = trial
                    results.append(result)
                    status = "OK" if result["success"] else result["failure_reason"]
                    print(f"{status} ({result['elapsed_s']}s)")
                except FuturesTimeoutError:
                    print(f"TIMEOUT (>{query_timeout}s)")
                    results.append({
                        "instruct": instruct,
                        "trial": trial,
                        "success": False,
                        "failure_reason": f"timeout_{query_timeout}s",
                        "element_count": 0,
                        "elapsed_s": query_timeout,
                        "query": None,
                    })
                except Exception as e:
                    print(f"ERROR: {e}")
                    results.append({
                        "instruct": instruct,
                        "trial": trial,
                        "success": False,
                        "failure_reason": f"exception: {e}",
                        "element_count": 0,
                        "elapsed_s": 0,
                        "query": None,
                    })

    total = len(results)
    success_count = sum(1 for r in results if r["success"] is True)
    no_code_block = sum(1 for r in results if r["failure_reason"] == "no_code_block")
    too_many_lines = sum(1 for r in results if r["failure_reason"] == "too_many_lines")
    zero_results = sum(1 for r in results if r["failure_reason"] == "zero_results")
    timeouts = sum(1 for r in results if str(r.get("failure_reason", "")).startswith("timeout_"))
    elapsed_values = [r["elapsed_s"] for r in results if isinstance(r["elapsed_s"], (int, float))]
    avg_elapsed = round(sum(elapsed_values) / total, 2) if total else 0

    return {
        "model": model,
        "model_slug": model_to_slug(model),
        "total": total,
        "success_count": success_count,
        "success_rate": round(success_count / total, 3) if total else 0,
        "no_code_block": no_code_block,
        "too_many_lines": too_many_lines,
        "zero_results": zero_results,
        "timeouts": timeouts,
        "avg_elapsed_s": avg_elapsed,
        "results": results,
    }


def _print_summary(model_reports: list[dict]) -> None:
    header = (
        f"{'Model':<32} {'Think':>6} {'Success':>8} {'Rate':>6} "
        f"{'NoBlock':>8} {'TooLong':>8} {'ZeroRes':>8} {'Timeout':>8} {'AvgSec':>7}"
    )
    sep = "=" * len(header)
    print("\n" + sep)
    print(header)
    print("-" * len(header))
    for r in model_reports:
        think_val = r.get("think")
        think_str = "default" if think_val is None else ("on" if think_val else "off")
        print(
            f"{r['model']:<32} "
            f"{think_str:>6} "
            f"{r['success_count']:>5}/{r['total']:<2} "
            f"{r['success_rate']:>5.0%} "
            f"{r['no_code_block']:>8} "
            f"{r['too_many_lines']:>8} "
            f"{r['zero_results']:>8} "
            f"{r.get('timeouts', 0):>8} "
            f"{r['avg_elapsed_s']:>7.1f}s"
        )
    print(sep)


def run_benchmark(
    models: list[str] | None = None,
    data_dir: str = DEFAULT_DATA_DIR,
    tmp_dir: str = DEFAULT_TMP_DIR,
    trials: int = 3,
    temperature: float = 0.01,
    num_predict: int = 256,
    query_timeout: int = DEFAULT_QUERY_TIMEOUT,
    think: bool | None = None,
    skip_unavailable: bool = True,
) -> dict:
    if models is None:
        models = DEFAULT_MODELS

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    os.makedirs(tmp_dir, exist_ok=True)

    report: dict = {
        "benchmark_at": datetime.now(timezone.utc).isoformat(),
        "trials_per_instruction": trials,
        "temperature": temperature,
        "num_predict": num_predict,
        "query_timeout_s": query_timeout,
        "think": think,
        "instructions": EVAL_INSTRUCTIONS,
        "models": [],
    }

    for model in models:
        if skip_unavailable and not _is_model_available(model):
            print(f"[SKIP] {model} — not pulled locally")
            continue

        think_label = "think=default" if think is None else f"think={think}"
        n_queries = trials * len(EVAL_INSTRUCTIONS)
        print(f"\n[RUN]  {model}  ({n_queries} queries, {think_label}, timeout {query_timeout}s each)")
        model_report = _probe_model(
            model=model,
            instructions=EVAL_INSTRUCTIONS,
            data_dir=data_dir,
            trials=trials,
            temperature=temperature,
            num_predict=num_predict,
            query_timeout=query_timeout,
            think=think,
        )
        model_report["think"] = think
        report["models"].append(model_report)

        # Save per-model result immediately so progress is preserved
        slug = model_to_slug(model)
        think_suffix = "" if think is None else ("-think" if think else "-nothink")
        model_path = os.path.join(tmp_dir, f"benchmark-{slug}{think_suffix}-{timestamp}.json")
        with open(model_path, "w") as f:
            json.dump(model_report, f, indent=2, ensure_ascii=False)
        print(f"       -> saved: {model_path}")

        _print_summary(report["models"])

    # Also save the full aggregate report
    full_path = os.path.join(tmp_dir, f"benchmark-all-{timestamp}.json")
    with open(full_path, "w") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"\nFull report: {full_path}")

    return report


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--models", nargs="+", default=None,
        help="Model name(s) to benchmark"
    )
    parser.add_argument(
        "--group", choices=list(MODEL_GROUPS.keys()), default=None,
        help="Named model group to benchmark (used when --models is not set)"
    )
    parser.add_argument("--data-dir", default=DEFAULT_DATA_DIR)
    parser.add_argument("--tmp-dir", default=DEFAULT_TMP_DIR)
    parser.add_argument("--trials", type=int, default=3, help="Trials per instruction (default: 3)")
    parser.add_argument("--temperature", type=float, default=0.01)
    parser.add_argument("--num-predict", type=int, default=256)
    parser.add_argument(
        "--query-timeout", type=int, default=DEFAULT_QUERY_TIMEOUT,
        help=f"Seconds to wait per query before marking as timeout (default: {DEFAULT_QUERY_TIMEOUT})"
    )
    think_group = parser.add_mutually_exclusive_group()
    think_group.add_argument(
        "--no-think", action="store_true",
        help="Disable chain-of-thought thinking (for qwen3/qwen3.5 models)"
    )
    think_group.add_argument(
        "--think", action="store_true",
        help="Explicitly enable chain-of-thought thinking"
    )
    parser.add_argument(
        "--include-unavailable", action="store_true",
        help="Attempt models not yet pulled locally (will error)"
    )
    args = parser.parse_args()

    if args.no_think:
        think: bool | None = False
    elif args.think:
        think = True
    else:
        think = None

    models = args.models
    if models is None and args.group is not None:
        models = MODEL_GROUPS[args.group]

    run_benchmark(
        models=models,
        data_dir=args.data_dir,
        tmp_dir=args.tmp_dir,
        trials=args.trials,
        temperature=args.temperature,
        num_predict=args.num_predict,
        query_timeout=args.query_timeout,
        think=think,
        skip_unavailable=not args.include_unavailable,
    )


if __name__ == "__main__":
    main()
