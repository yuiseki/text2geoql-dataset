"""Taginfo API client with injectable endpoint for testability."""

import httpx

DEFAULT_ENDPOINT = "https://taginfo.yuiseki.net"


def _get(path: str, params: dict, endpoint: str) -> dict:
    """Internal GET helper. Returns empty dict on error."""
    try:
        response = httpx.get(f"{endpoint}/api/4/{path}", params=params, timeout=30)
        result: dict = response.json()
        return result
    except Exception as e:
        print("Taginfo error:", e)
        return {}


def get_key_values(
    key: str,
    *,
    min_count: int = 10_000,
    rp: int = 50,
    endpoint: str = DEFAULT_ENDPOINT,
) -> list[dict]:
    """Return values for a key sorted by count descending, filtered by min_count.

    Each item: {"value": str, "count": int, "fraction": float, "in_wiki": bool}
    """
    data = _get(
        "key/values",
        {"key": key, "sortname": "count", "sortorder": "desc", "page": 1, "rp": rp},
        endpoint,
    )
    items: list[dict] = data.get("data", [])
    return [item for item in items if item.get("count", 0) >= min_count]


def get_tag_stats(
    key: str,
    value: str,
    *,
    endpoint: str = DEFAULT_ENDPOINT,
) -> dict:
    """Return usage statistics for a key=value tag.

    Returns a dict with keys: "all", "nodes", "ways", "relations"
    mapping to count integers. Returns zeros on error.
    """
    data = _get("tag/stats", {"key": key, "value": value}, endpoint)
    result = {"all": 0, "nodes": 0, "ways": 0, "relations": 0}
    for item in data.get("data", []):
        t = item.get("type", "")
        if t in result:
            result[t] = item.get("count", 0)
    return result


def get_tag_combinations(
    key: str,
    value: str,
    *,
    rp: int = 10,
    endpoint: str = DEFAULT_ENDPOINT,
) -> list[dict]:
    """Return keys frequently used together with key=value, sorted by co-occurrence.

    Each item: {"other_key": str, "together_count": int, "to_fraction": float}
    """
    data = _get(
        "tag/combinations",
        {
            "key": key,
            "value": value,
            "sortname": "together_count",
            "sortorder": "desc",
            "page": 1,
            "rp": rp,
        },
        endpoint,
    )
    return data.get("data", [])


def validate_tag(
    key: str,
    value: str,
    *,
    min_count: int = 1_000,
    endpoint: str = DEFAULT_ENDPOINT,
) -> bool:
    """Return True if key=value exists in OSM with at least min_count uses."""
    stats = get_tag_stats(key, value, endpoint=endpoint)
    return stats["all"] >= min_count
