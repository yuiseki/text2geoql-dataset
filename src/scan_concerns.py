"""Hierarchical tag scan — stores count results in __tag_scan/ per admin node.

Storage layout:
  data/administrative/{Country}/__tag_scan/{key}/{value}/result.json
  data/administrative/{Country}/{Region}/__tag_scan/{key}/{value}/result.json
  ...

Pruning rule: if count == 0 at a node, children are not scanned.
Idempotency: if result.json already exists, the node is skipped (safe to rerun).
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))

import nominatim
from meta import now_iso
from overpass import fetch_count

DEFAULT_ADMIN_ROOT = "data/administrative"
DEFAULT_CONCERNS_YAML = "good_concerns.yaml"
DEFAULT_OVERPASS_ENDPOINT = "https://overpass.yuiseki.net/api/interpreter"
DEFAULT_NOMINATIM_ENDPOINT = nominatim.DEFAULT_ENDPOINT


# ── concern loading ───────────────────────────────────────────────────────────


def load_concerns(yaml_path: str = DEFAULT_CONCERNS_YAML) -> list[tuple[str, str]]:
    """Parse good_concerns.yaml and return (key, value) pairs.

    Only returns simple two-component paths like data/concerns/shop/anime.
    Skips composite paths (medical/all), cuisine subtags, and comments.

    >>> load_concerns  # doctest: +SKIP
    """
    concerns: list[tuple[str, str]] = []
    known_osm_keys = {
        "amenity", "shop", "tourism", "leisure", "historic", "craft",
        "healthcare", "emergency", "office", "man_made", "natural",
        "aeroway", "railway", "building", "social_facility",
    }
    with open(yaml_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            # Format: "Label: data/concerns/{key}/{value}"
            m = re.match(r"^[^:]+:\s*data/concerns/([^/\s]+)/([^/\s]+)\s*$", line)
            if not m:
                continue
            key, value = m.group(1), m.group(2)
            if key not in known_osm_keys:
                continue
            concerns.append((key, value))
    return concerns


# ── path helpers ──────────────────────────────────────────────────────────────


def result_path(admin_path: str, key: str, value: str) -> str:
    """Return the path to result.json for a given admin node and tag."""
    return os.path.join(admin_path, "__tag_scan", key, value, "result.json")


def admin_path_to_area_name(admin_path: str) -> str:
    """Convert an admin directory path to a comma-separated area name.

    data/administrative/Japan                          → "Japan"
    data/administrative/Japan/Tokyo                    → "Tokyo, Japan"
    data/administrative/Japan/Tokyo/Shinjuku           → "Shinjuku, Tokyo, Japan"
    data/administrative/Japan/Hiroshima Prefecture/Hiroshima/Naka Ward
        → "Naka Ward, Hiroshima, Hiroshima Prefecture, Japan"

    >>> admin_path_to_area_name("data/administrative/Japan")
    'Japan'
    >>> admin_path_to_area_name("data/administrative/Japan/Tokyo")
    'Tokyo, Japan'
    >>> admin_path_to_area_name("data/administrative/Japan/Tokyo/Shinjuku")
    'Shinjuku, Tokyo, Japan'
    """
    # Strip leading admin root prefix (handles relative and absolute paths)
    parts = Path(admin_path).parts
    # Find "administrative" and take everything after it
    try:
        idx = parts.index("administrative")
    except ValueError:
        # fallback: use all parts
        idx = 0
    area_parts = list(parts[idx + 1:])
    # Reverse for "most specific first" order
    return ", ".join(reversed(area_parts))


def iter_admin_children(admin_path: str):
    """Yield immediate subdirectory paths that are admin nodes (not __* dirs)."""
    try:
        for entry in sorted(os.scandir(admin_path), key=lambda e: e.name):
            if entry.is_dir() and not entry.name.startswith("__"):
                yield entry.path
    except FileNotFoundError:
        pass


# ── result persistence ────────────────────────────────────────────────────────


def is_scanned(admin_path: str, key: str, value: str) -> bool:
    """Return True if result.json already exists for this node + tag."""
    return os.path.exists(result_path(admin_path, key, value))


def load_result(admin_path: str, key: str, value: str) -> dict | None:
    """Load and return result.json, or None if not found."""
    path = result_path(admin_path, key, value)
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)


def save_result(
    admin_path: str,
    key: str,
    value: str,
    *,
    count: int,
    relation_id: int | None,
    area_name: str,
) -> None:
    """Write result.json for this node + tag."""
    path = result_path(admin_path, key, value)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    data = {
        "count": count,
        "osm_relation_id": relation_id,
        "area_name": area_name,
        "scanned_at": now_iso(),
    }
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


# ── Overpass count query ──────────────────────────────────────────────────────


def build_count_query(area_id: int, key: str, value: str) -> str:
    """Build an Overpass QL query that returns only the element count.

    >>> q = build_count_query(3600382313, "shop", "anime")
    >>> "area(id:3600382313)" in q and 'out count;' in q
    True
    """
    return (
        f'[out:json][timeout:60];\n'
        f'area(id:{area_id})->.searchArea;\n'
        f'nwr["{key}"="{value}"](area.searchArea);\n'
        f'out count;'
    )


# ── Nominatim resolution ──────────────────────────────────────────────────────


def get_relation_id(
    area_name: str,
    *,
    nominatim_endpoint: str = DEFAULT_NOMINATIM_ENDPOINT,
) -> int | None:
    """Resolve an area name to an OSM relation ID via Nominatim."""
    return nominatim.get_osm_relation_id(area_name, endpoint=nominatim_endpoint)


# ── scan node ─────────────────────────────────────────────────────────────────


def scan_node(
    admin_path: str,
    key: str,
    value: str,
    *,
    relation_id: int | None = None,
    overpass_endpoint: str = DEFAULT_OVERPASS_ENDPOINT,
) -> int:
    """Scan a single admin node for a tag. Returns the element count.

    If result.json already exists, returns cached count without querying.
    Otherwise, queries Overpass and saves the result.
    """
    if is_scanned(admin_path, key, value):
        result = load_result(admin_path, key, value)
        return result["count"] if result else 0

    area_name = admin_path_to_area_name(admin_path)

    count = 0
    if relation_id is not None:
        area_id = nominatim.relation_to_area_id(relation_id)
        query = build_count_query(area_id, key, value)
        count = fetch_count(query, endpoint=overpass_endpoint)

    save_result(
        admin_path, key, value,
        count=count,
        relation_id=relation_id,
        area_name=area_name,
    )
    return count


# ── scan tree ─────────────────────────────────────────────────────────────────


def scan_tree(
    admin_path: str,
    key: str,
    value: str,
    *,
    nominatim_endpoint: str = DEFAULT_NOMINATIM_ENDPOINT,
    overpass_endpoint: str = DEFAULT_OVERPASS_ENDPOINT,
) -> None:
    """Recursively scan an admin node and its children for a tag.

    Pruning: if count == 0 at this node, children are not scanned.
    Idempotency: already-scanned nodes are skipped entirely.
    """
    area_name = admin_path_to_area_name(admin_path)

    # Resolve relation ID (or reuse from cached result)
    relation_id: int | None = None
    if is_scanned(admin_path, key, value):
        cached = load_result(admin_path, key, value)
        count = cached["count"] if cached else 0
        relation_id = cached.get("osm_relation_id") if cached else None
    else:
        relation_id = get_relation_id(area_name, nominatim_endpoint=nominatim_endpoint)
        count = scan_node(
            admin_path, key, value,
            relation_id=relation_id,
            overpass_endpoint=overpass_endpoint,
        )

    if count == 0:
        return  # prune children

    for child_path in iter_admin_children(admin_path):
        scan_tree(
            child_path, key, value,
            nominatim_endpoint=nominatim_endpoint,
            overpass_endpoint=overpass_endpoint,
        )
