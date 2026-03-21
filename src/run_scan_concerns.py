"""CLI entry point for hierarchical tag scan.

Parallelism: concerns are scanned in parallel per country using
ThreadPoolExecutor. Max workers default to 8, safely below the
Overpass API rate limit of 10 concurrent requests per user
(OVERPASS_RATE_LIMIT=10, OVERPASS_FASTCGI_PROCESSES=12).

Usage:
    # Scan all concerns across all countries (full run)
    uv run python src/run_scan_concerns.py

    # Scan a specific country only
    uv run python src/run_scan_concerns.py --country Japan

    # Scan a specific tag only
    uv run python src/run_scan_concerns.py --key shop --value anime

    # Dry run: show what would be scanned without querying
    uv run python src/run_scan_concerns.py --dry-run

    # Adjust parallelism (default: 8)
    uv run python src/run_scan_concerns.py --workers 4
"""

import argparse
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, os.path.dirname(__file__))

from scan_concerns import (
    DEFAULT_ADMIN_ROOT,
    DEFAULT_CONCERNS_YAML,
    is_scanned,
    iter_admin_children,
    load_concerns,
    scan_tree,
)

# Overpass config: OVERPASS_RATE_LIMIT=10, OVERPASS_FASTCGI_PROCESSES=12
# Use 8 workers to stay safely under the per-user rate limit.
DEFAULT_WORKERS = 8


def main() -> None:
    parser = argparse.ArgumentParser(description="Hierarchical OSM tag count scanner")
    parser.add_argument("--admin-root", default=DEFAULT_ADMIN_ROOT)
    parser.add_argument("--concerns-yaml", default=DEFAULT_CONCERNS_YAML)
    parser.add_argument("--country", default=None,
                        help="Scan only this country (e.g. 'Japan')")
    parser.add_argument("--key", default=None)
    parser.add_argument("--value", default=None)
    parser.add_argument("--workers", type=int, default=DEFAULT_WORKERS,
                        help=f"Parallel workers (default: {DEFAULT_WORKERS}, max safe: 10)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    concerns = load_concerns(args.concerns_yaml)
    if args.key and args.value:
        concerns = [(k, v) for k, v in concerns if k == args.key and v == args.value]
    elif args.key:
        concerns = [(k, v) for k, v in concerns if k == args.key]

    country_paths = sorted(iter_admin_children(args.admin_root))
    if args.country:
        country_paths = [p for p in country_paths if os.path.basename(p) == args.country]

    # Build work items: (country_path, key, value) that are not yet scanned
    work = [
        (cp, k, v)
        for k, v in concerns
        for cp in country_paths
        if not is_scanned(cp, k, v)
    ]
    total = len(concerns) * len(country_paths)
    skipped = total - len(work)

    print(f"Scanning {len(concerns)} concerns × {len(country_paths)} countries")
    print(f"  {skipped} already scanned, {len(work)} remaining")
    print(f"  workers: {args.workers}")
    print()

    if args.dry_run:
        for cp, k, v in work[:20]:
            print(f"  [dry-run] {os.path.basename(cp)} — {k}={v}")
        if len(work) > 20:
            print(f"  ... and {len(work) - 20} more")
        return

    done = 0
    t0 = time.time()

    def _scan(item):
        cp, k, v = item
        scan_tree(cp, k, v)
        return item

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(_scan, item): item for item in work}
        for future in as_completed(futures):
            cp, k, v = futures[future]
            done += 1
            elapsed = time.time() - t0
            country = os.path.basename(cp)
            try:
                future.result()
                print(f"[{done}/{len(work)}] {country} — {k}={v}  ({elapsed:.0f}s)")
            except Exception as e:
                print(f"[{done}/{len(work)}] ERROR {country} — {k}={v}: {e}")

    elapsed = time.time() - t0
    print()
    print(f"Done. {len(work)} scanned, {skipped} skipped. elapsed={elapsed:.0f}s")


if __name__ == "__main__":
    main()
