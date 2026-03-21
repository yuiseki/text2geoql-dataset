"""Populate data/administrative/ with country-level (admin_level=2) stubs.

Creates input-trident.txt and output-001.overpassql for each country
found in OSM that doesn't already have a directory.

Deeper levels (admin_level=4/6/8) are intentionally out of scope here —
admin systems vary significantly by country and require separate handling.

Usage:
    uv run python src/populate_administrative.py
    uv run python src/populate_administrative.py --dry-run
"""

from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from overpass import fetch_elements

DEFAULT_ADMIN_ROOT = "data/administrative"
DEFAULT_OVERPASS_ENDPOINT = "https://overpass.yuiseki.net/api/interpreter"


# ── query builders ────────────────────────────────────────────────────────────


def build_countries_query() -> str:
    """Build Overpass QL query to fetch all admin_level=2 relations with name:en.

    Filters by ISO3166-1 tag to exclude border/dispute relations that OSM
    models as admin_level=2 but are not sovereign countries (e.g. shared
    borders between two countries).

    >>> q = build_countries_query()
    >>> "admin_level" in q and "2" in q
    True
    >>> "ISO3166-1" in build_countries_query()
    True
    """
    return (
        '[out:json][timeout:120];\n'
        'relation["boundary"="administrative"]["admin_level"="2"]["ISO3166-1"]["name:en"];\n'
        'out tags;'
    )


# ── Overpass fetchers ─────────────────────────────────────────────────────────


def fetch_countries(
    *,
    endpoint: str = DEFAULT_OVERPASS_ENDPOINT,
) -> list[str]:
    """Return sorted list of unique country name:en values from OSM."""
    query = build_countries_query()
    elements = fetch_elements(query, endpoint=endpoint)
    seen: set[str] = set()
    result: list[str] = []
    for el in elements:
        name = el.get("tags", {}).get("name:en")
        if name and name not in seen:
            seen.add(name)
            result.append(name)
    return sorted(result)


# ── node helpers ──────────────────────────────────────────────────────────────


def node_exists(admin_root: str, country_name: str) -> bool:
    """Return True if the country directory already has an input-trident.txt."""
    return os.path.exists(
        os.path.join(admin_root, country_name, "input-trident.txt")
    )


def create_country_node(admin_root: str, country_name: str) -> None:
    """Create input-trident.txt and output-001.overpassql for a country.

    Idempotent: does nothing if the node already exists.
    """
    if node_exists(admin_root, country_name):
        return

    node_dir = os.path.join(admin_root, country_name)
    os.makedirs(node_dir, exist_ok=True)

    # input-trident.txt
    with open(os.path.join(node_dir, "input-trident.txt"), "w") as f:
        f.write(f"Area: {country_name}\n")

    # output-001.overpassql
    ql = (
        f'[out:json][timeout:30];\n'
        f'relation["boundary"="administrative"]["admin_level"="2"]["name:en"="{country_name}"];\n'
        f'out geom;'
    )
    with open(os.path.join(node_dir, "output-001.overpassql"), "w") as f:
        f.write(ql + "\n")


# ── CLI ───────────────────────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Populate data/administrative/ with country-level stubs"
    )
    parser.add_argument("--admin-root", default=DEFAULT_ADMIN_ROOT)
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be created without writing files")
    args = parser.parse_args()

    print("Fetching country list from Overpass...")
    countries = fetch_countries()
    print(f"Found {len(countries)} countries with name:en in OSM")
    print()

    created = 0
    skipped = 0
    for name in countries:
        if node_exists(args.admin_root, name):
            skipped += 1
            continue
        if args.dry_run:
            print(f"  [new] {name}")
        else:
            create_country_node(args.admin_root, name)
            print(f"  created: {name}")
        created += 1

    print()
    print(f"Done. {created} {'would be ' if args.dry_run else ''}created, {skipped} already exist.")


if __name__ == "__main__":
    main()
