"""Populate data/administrative/ with admin node stubs from OSM.

Country level (admin_level=2):
    uv run python src/populate_administrative.py
    uv run python src/populate_administrative.py --dry-run

Sub-country levels (e.g. Japanese cities within a prefecture):
    uv run python src/populate_administrative.py \\
        --parent "Japan/Hiroshima Prefecture" --admin-level 7
    uv run python src/populate_administrative.py \\
        --parent "Japan/Hiroshima Prefecture/Hiroshima" --admin-level 8

Note: admin level systems vary by country. Use --parent + --admin-level
for targeted expansion rather than bulk automation.
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


# ── subnode query / fetch ─────────────────────────────────────────────────────


def build_subnodes_query(area_name: str, admin_level: int) -> str:
    """Build Overpass QL query to fetch admin subdivisions within an area.

    Uses a name-based area filter to find all relations at the given
    admin_level within the named parent area.

    >>> q = build_subnodes_query("Hiroshima Prefecture, Japan", admin_level=7)
    >>> "Hiroshima Prefecture" in q and '"7"' in q
    True
    """
    # Use the most specific part of the area name to find the OSM area
    primary_name = area_name.split(",")[0].strip()
    return (
        f'[out:json][timeout:60];\n'
        f'area["name:en"="{primary_name}"]->.parent;\n'
        f'relation["boundary"="administrative"]["admin_level"="{admin_level}"](area.parent);\n'
        f'out tags;'
    )


def fetch_subnodes(
    area_name: str,
    admin_level: int,
    *,
    endpoint: str = DEFAULT_OVERPASS_ENDPOINT,
) -> list[str]:
    """Return sorted unique name:en list of admin subdivisions within an area."""
    query = build_subnodes_query(area_name, admin_level)
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


def node_exists(admin_root: str, *path_parts: str) -> bool:
    """Return True if the admin node directory already has an input-trident.txt."""
    return os.path.exists(
        os.path.join(admin_root, *path_parts, "input-trident.txt")
    )


def create_subnode(admin_root: str, path_parts: list[str], admin_level: int) -> None:
    """Create input-trident.txt and output-001.overpassql for a sub-country node.

    path_parts: e.g. ["Japan", "Hiroshima Prefecture", "Hiroshima"]
    The area name in TRIDENT format is built by reversing the parts:
      "Hiroshima, Hiroshima Prefecture, Japan"

    Idempotent: does nothing if the node already exists.
    """
    if node_exists(admin_root, *path_parts):
        return

    node_dir = os.path.join(admin_root, *path_parts)
    os.makedirs(node_dir, exist_ok=True)

    # TRIDENT area name: reverse path parts → "Hiroshima, Hiroshima Prefecture, Japan"
    area_name = ", ".join(reversed(path_parts))
    primary_name = path_parts[-1]  # most specific name for OSM query

    with open(os.path.join(node_dir, "input-trident.txt"), "w") as f:
        f.write(f"Area: {area_name}\n")

    ql = (
        f'[out:json][timeout:30];\n'
        f'relation["boundary"="administrative"]["admin_level"="{admin_level}"]["name:en"="{primary_name}"];\n'
        f'out geom;'
    )
    with open(os.path.join(node_dir, "output-001.overpassql"), "w") as f:
        f.write(ql + "\n")


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
        description="Populate data/administrative/ with admin node stubs"
    )
    parser.add_argument("--admin-root", default=DEFAULT_ADMIN_ROOT)
    parser.add_argument("--parent", default=None,
                        help="Parent path relative to admin-root, e.g. 'Japan/Hiroshima Prefecture'")
    parser.add_argument("--admin-level", type=int, default=None,
                        help="OSM admin_level for subnodes (required with --parent)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.parent:
        # Sub-country mode
        if args.admin_level is None:
            parser.error("--admin-level is required with --parent")
        parent_parts = args.parent.split("/")
        area_name = ", ".join(reversed(parent_parts))
        print(f"Fetching admin_level={args.admin_level} subnodes within '{area_name}'...")
        names = fetch_subnodes(area_name, args.admin_level)
        print(f"Found {len(names)} subnodes")
        print()
        created = skipped = 0
        for name in names:
            path_parts = parent_parts + [name]
            if node_exists(args.admin_root, *path_parts):
                skipped += 1
                continue
            if args.dry_run:
                print(f"  [new] {name}")
            else:
                create_subnode(args.admin_root, path_parts, args.admin_level)
                print(f"  created: {name}")
            created += 1
    else:
        # Country mode
        print("Fetching country list from Overpass...")
        names = fetch_countries()
        print(f"Found {len(names)} countries with name:en in OSM")
        print()
        created = skipped = 0
        for name in names:
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
