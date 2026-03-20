"""Overpass API client with injectable endpoint for testability."""

import httpx

DEFAULT_ENDPOINT = "https://overpass.yuiseki.net/api/interpreter"


def fetch_elements(
    query: str,
    *,
    endpoint: str = DEFAULT_ENDPOINT,
) -> list[dict]:
    """Execute an Overpass QL query and return the elements list.

    Returns an empty list on any error.
    """
    params = {"data": query}
    try:
        response = httpx.get(endpoint, params=params, timeout=None)
        response_json = response.json()
        elements: list[dict] = response_json.get("elements", [])
        return elements
    except Exception as e:
        print("Error:", e)
        return []


def count_elements(
    query: str,
    *,
    endpoint: str = DEFAULT_ENDPOINT,
) -> int:
    """Return the number of elements returned by an Overpass QL query."""
    return len(fetch_elements(query, endpoint=endpoint))
