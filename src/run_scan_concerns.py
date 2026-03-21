"""CLI entry point for hierarchical tag scan.

Usage:
    # Scan all concerns across all countries (full run)
    uv run python src/run_scan_concerns.py

    # Scan a specific country only
    uv run python src/run_scan_concerns.py --country Japan

    # Scan a specific tag only
    uv run python src/run_scan_concerns.py --key shop --value anime

    # Dry run: show what would be scanned without querying
    uv run python src/run_scan_concerns.py --dry-run
"""

import argparse
import os
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))

from scan_concerns import (
    DEFAULT_ADMIN_ROOT,
    DEFAULT_CONCERNS_YAML,
    is_scanned,
    iter_admin_children,
    load_concerns,
    scan_tree,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Hierarchical OSM tag count scanner")
    parser.add_argument("--admin-root", default=DEFAULT_ADMIN_ROOT,
                        help="Root of administrative tree (default: data/administrative)")
    parser.add_argument("--concerns-yaml", default=DEFAULT_CONCERNS_YAML,
                        help="Path to good_concerns.yaml")
    parser.add_argument("--country", default=None,
                        help="Scan only this country directory name (e.g. 'Japan')")
    parser.add_argument("--key", default=None,
                        help="Scan only this OSM key (e.g. 'shop')")
    parser.add_argument("--value", default=None,
                        help="Scan only this OSM value (e.g. 'anime')")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print what would be scanned without querying Overpass")
    args = parser.parse_args()

    concerns = load_concerns(args.concerns_yaml)

    # Filter by key/value if specified
    if args.key and args.value:
        concerns = [(k, v) for k, v in concerns if k == args.key and v == args.value]
    elif args.key:
        concerns = [(k, v) for k, v in concerns if k == args.key]

    # Country nodes
    country_paths = sorted(iter_admin_children(args.admin_root))
    if args.country:
        country_paths = [p for p in country_paths if os.path.basename(p) == args.country]

    print(f"Scanning {len(concerns)} concerns × {len(country_paths)} countries")
    print(f"Admin root: {args.admin_root}")
    print()

    total = len(concerns) * len(country_paths)
    done = 0
    skipped = 0
    t0 = time.time()

    for key, value in concerns:
        for country_path in country_paths:
            done += 1
            country = os.path.basename(country_path)

            if is_scanned(country_path, key, value):
                skipped += 1
                continue

            elapsed = time.time() - t0
            print(f"[{done}/{total}] {country} — {key}={value}  (elapsed={elapsed:.0f}s)")

            if args.dry_run:
                print(f"  (dry-run, skipping)")
                continue

            scan_tree(country_path, key, value)

    elapsed = time.time() - t0
    print()
    print(f"Done. {done} checked, {skipped} already scanned. elapsed={elapsed:.0f}s")


if __name__ == "__main__":
    main()
