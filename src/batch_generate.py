"""Batch-generate Overpass QL for all unprocessed AreaWithConcern TRIDENT entries.

Designed for long overnight runs. Skips entries that already have output or
not-found records. Stops automatically if free disk drops below a safety
threshold (default 20 GB).

Usage:
    # Default: qwen2.5-coder:3b, all missing entries
    uv run python src/batch_generate.py

    # Best-quality model with optimal context window
    uv run python src/batch_generate.py --model gemma3:12b --num-ctx 32768

    # Limit number of entries (e.g. for a quick test)
    uv run python src/batch_generate.py --limit 10

Output:
    - Writes output-<slug>.overpassql and .meta.json into each data directory.
    - Writes not-found-<slug>.json for failures.
    - Prints running totals and elapsed time.
"""

import argparse
import os
import shutil
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(Path(__file__).parent))

from generate_overpassql import run as run_one, OLLAMA_MODEL, default_num_predict

DEFAULT_DATA_DIR = str(REPO_ROOT / "data")
DEFAULT_TMP_DIR = str(REPO_ROOT / "tmp")
DISK_MIN_FREE_GB = 20.0


def find_missing_entries(data_dir: str) -> list[str]:
    """Return paths of AreaWithConcern dirs that have no output and no not-found record."""
    missing: list[str] = []
    for root, dirs, files in os.walk(data_dir):
        if "input-trident.txt" not in files:
            continue
        txt = open(os.path.join(root, "input-trident.txt")).read().strip()
        if not txt.startswith("AreaWithConcern:"):
            continue
        has_output = any(f.startswith("output-") and f.endswith(".overpassql") for f in files)
        has_nf = any(f.startswith("not-found") for f in files)
        if not has_output and not has_nf:
            missing.append(root)
    return missing


def free_gb(path: str) -> float:
    return shutil.disk_usage(path).free / (1024 ** 3)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--model", default=OLLAMA_MODEL, help="Ollama model name")
    parser.add_argument(
        "--num-ctx", type=int, default=None,
        help="Override context window size (e.g. 32768 for gemma3:12b)"
    )
    parser.add_argument("--num-predict", type=int, default=256)
    parser.add_argument("--temperature", type=float, default=0.01)
    parser.add_argument("--data-dir", default=DEFAULT_DATA_DIR)
    parser.add_argument("--tmp-dir", default=DEFAULT_TMP_DIR)
    parser.add_argument(
        "--limit", type=int, default=None,
        help="Maximum number of entries to process (default: all)"
    )
    parser.add_argument(
        "--disk-min-gb", type=float, default=DISK_MIN_FREE_GB,
        help=f"Stop if free disk drops below this GB (default: {DISK_MIN_FREE_GB})"
    )
    args = parser.parse_args()

    entries = find_missing_entries(args.data_dir)
    total_found = len(entries)
    limit = args.limit if args.limit is not None else total_found
    entries = entries[:limit]

    effective_num_predict = max(args.num_predict, default_num_predict(args.model, think=None))

    print(f"Model:          {args.model}")
    print(f"num_ctx:        {args.num_ctx or 'model default'}")
    print(f"num_predict:    {effective_num_predict}")
    print(f"Missing entries found: {total_found}  (processing: {len(entries)})")
    print(f"Disk guard:     stop if free < {args.disk_min_gb:.0f} GB")
    print()

    t_start = time.monotonic()
    ok = 0
    failed = 0

    for i, entry_path in enumerate(entries, 1):
        gb = free_gb(args.data_dir)
        if gb < args.disk_min_gb:
            print(f"\n[STOP] Disk free {gb:.1f} GB < {args.disk_min_gb:.0f} GB threshold. Exiting.")
            break

        elapsed_total = time.monotonic() - t_start
        rate = i / elapsed_total if elapsed_total > 0 else 0
        eta_s = (len(entries) - i) / rate if rate > 0 else 0
        eta_min = eta_s / 60

        print(
            f"[{i}/{len(entries)}] disk={gb:.0f}GB  "
            f"elapsed={elapsed_total/60:.1f}m  ETA={eta_min:.0f}m"
        )

        before_output = any(
            f.startswith("output-") and f.endswith(".overpassql")
            for f in os.listdir(entry_path)
        )

        try:
            run_one(
                base_path=entry_path,
                data_dir=args.data_dir,
                tmp_root=args.tmp_dir,
                model=args.model,
                temperature=args.temperature,
                num_predict=effective_num_predict,
                num_ctx=args.num_ctx,
            )
        except Exception as e:
            print(f"  [ERROR] {e}")
            failed += 1
            continue

        after_output = any(
            f.startswith("output-") and f.endswith(".overpassql")
            for f in os.listdir(entry_path)
        )
        if after_output and not before_output:
            ok += 1
        else:
            failed += 1

    elapsed_total = time.monotonic() - t_start
    processed = ok + failed
    print(f"\n{'='*60}")
    print(f"Done. Processed: {processed}  OK: {ok}  Failed: {failed}")
    print(f"Elapsed: {elapsed_total/60:.1f} min  ({elapsed_total/3600:.2f} h)")
    if processed > 0:
        print(f"Rate: {processed / (elapsed_total/60):.1f} entries/min")


if __name__ == "__main__":
    main()
