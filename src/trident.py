"""Pure functions for parsing TRIDENT intermediate format strings.

Examples of TRIDENT format:
  "AreaWithConcern: Taito, Tokyo, Japan; Cafes"
  "Area: Taito, Tokyo, Japan"
  "SubArea: Taito, Tokyo, Japan"
"""


def parse_filter_type(instruct: str) -> str:
    """Extract the filter type prefix from a TRIDENT string.

    >>> parse_filter_type("AreaWithConcern: Taito, Tokyo, Japan; Cafes")
    'AreaWithConcern'
    >>> parse_filter_type("Area: Seoul, South Korea")
    'Area'
    """
    return instruct.split(":")[0].strip()


def parse_filter_concern(instruct: str) -> str:
    """Extract the concern (POI type) from a TRIDENT string.

    >>> parse_filter_concern("AreaWithConcern: Taito, Tokyo, Japan; Cafes")
    'Cafes'
    >>> parse_filter_concern("AreaWithConcern: Seoul, South Korea; Train Stations")
    'Train Stations'
    """
    return instruct.split("; ")[-1].strip()


def parse_filter_area(instruct: str) -> str:
    """Extract the smallest administrative unit from a TRIDENT string.

    >>> parse_filter_area("AreaWithConcern: Taito, Tokyo, Japan; Cafes")
    'Taito'
    >>> parse_filter_area("AreaWithConcern: Seoul, South Korea; Museums")
    'Seoul'
    """
    return instruct.split("; ")[0].split(": ")[-1].split(", ")[0].strip()


def build_area_with_concern(area: str, concern: str) -> str:
    """Build an AreaWithConcern TRIDENT string from area and concern.

    >>> build_area_with_concern("Taito, Tokyo, Japan", "Cafes")
    'AreaWithConcern: Taito, Tokyo, Japan; Cafes'
    """
    return f"AreaWithConcern: {area}; {concern}"


def area_path_from_trident(area_with_concern: str) -> str:
    """Convert an AreaWithConcern string to a reversed-area path segment.

    >>> area_path_from_trident("AreaWithConcern: Taito, Tokyo, Japan; Cafes")
    'Japan/Tokyo/Taito'
    """
    area_part = area_with_concern.split(";")[0].replace("AreaWithConcern: ", "")
    area_names = area_part.split(", ")
    return "/".join(reversed(area_names))
