"""Nominatim geocoding API client with injectable endpoint for testability."""

import httpx

DEFAULT_ENDPOINT = "https://nominatim.yuiseki.net"


def search(
    query: str,
    *,
    limit: int = 1,
    endpoint: str = DEFAULT_ENDPOINT,
) -> list[dict]:
    """Search Nominatim by free-text query. Returns raw result list."""
    try:
        response = httpx.get(
            f"{endpoint}/search.php",
            params={"q": query, "format": "json", "limit": limit},
            timeout=30,
        )
        result: list[dict] = response.json()
        return result
    except Exception as e:
        print("Nominatim search error:", e)
        return []


def get_osm_relation_id(
    area_name: str,
    *,
    endpoint: str = DEFAULT_ENDPOINT,
) -> int | None:
    """Return the OSM relation ID for a place name, or None if not found.

    Only returns results where osm_type == "relation".
    """
    results = search(area_name, limit=3, endpoint=endpoint)
    for r in results:
        if r.get("osm_type") == "relation":
            return int(r["osm_id"])
    return None


def relation_to_area_id(osm_relation_id: int) -> int:
    """Convert an OSM relation ID to the Overpass area ID.

    Overpass area IDs for relations = osm_relation_id + 3_600_000_000.
    """
    return osm_relation_id + 3_600_000_000


def get_display_name(
    area_name: str,
    *,
    endpoint: str = DEFAULT_ENDPOINT,
) -> str | None:
    """Return the OSM display_name for a place name, or None if not found."""
    results = search(area_name, limit=1, endpoint=endpoint)
    if results:
        return results[0].get("display_name")
    return None
