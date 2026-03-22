"""
Generate 2-level and 3-level training pairs for text2geoql dataset.

This script adds:
- 2-level: City, Country → single searchArea query (fixes Busan-as-Seoul-ward bug)
- 3-level: City, Region, Country → outer=Region, inner=City (fixes hierarchy inversion)

Generated pairs are saved as input-trident.txt + output-001.overpassql
in the data/concerns/<tag>/<value>/<Country>/[<Region>/]<City>/ structure.
"""

import json
import os
import time

import requests

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

CONCERNS = [
    # (osm_category, osm_tag, osm_value, concern_label)
    ("amenity", "amenity", "cafe", "Cafes"),
    ("amenity", "amenity", "restaurant", "Restaurants"),
    ("tourism", "tourism", "museum", "Museums"),
    ("tourism", "tourism", "hotel", "Hotels"),
    ("shop", "shop", "convenience", "Convenience stores"),
]

# 3-level locations: (city, region, country)
LOCATIONS_3LEVEL = [
    # Japan: City, Prefecture, Japan (hierarchy inversion failures)
    ("Sendai", "Miyagi Prefecture", "Japan"),
    ("Nagoya", "Aichi Prefecture", "Japan"),
    ("Sapporo", "Hokkaido", "Japan"),
    ("Fukuoka", "Fukuoka Prefecture", "Japan"),
    ("Hiroshima", "Hiroshima Prefecture", "Japan"),
    ("Kyoto", "Kyoto Prefecture", "Japan"),
    ("Kobe", "Hyogo Prefecture", "Japan"),
    ("Kawasaki", "Kanagawa Prefecture", "Japan"),
    ("Niigata", "Niigata Prefecture", "Japan"),
    # Europe: City, Region, Country
    ("Munich", "Bavaria", "Germany"),
    ("Hamburg", "Hamburg", "Germany"),
    ("Rome", "Lazio", "Italy"),
    ("Milan", "Lombardy", "Italy"),
    ("Amsterdam", "North Holland", "Netherlands"),
    ("Warsaw", "Masovian Voivodeship", "Poland"),
    ("Brussels", "Brussels-Capital Region", "Belgium"),
    ("Lyon", "Auvergne-Rhône-Alpes", "France"),
    ("Barcelona", "Catalonia", "Spain"),
    ("Valencia", "Valencia", "Spain"),
    # Asia
    ("Osaka", "Osaka Prefecture", "Japan"),
    ("Bangkok", "Bangkok", "Thailand"),
    ("Ho Chi Minh City", "Ho Chi Minh City", "Vietnam"),
    ("Hanoi", "Hanoi", "Vietnam"),
]

# 2-level locations: (city, country)  — fixes Busan-as-Seoul-ward bug
LOCATIONS_2LEVEL = [
    ("Busan", "South Korea"),
    ("Daegu", "South Korea"),
    ("Incheon", "South Korea"),
    ("Gwangju", "South Korea"),
    ("Daejeon", "South Korea"),
    ("Ulsan", "South Korea"),
    ("Taipei", "Taiwan"),
    ("Kaohsiung", "Taiwan"),
    ("Jakarta", "Indonesia"),
    ("Surabaya", "Indonesia"),
    ("Kuala Lumpur", "Malaysia"),
    ("Singapore", "Singapore"),
    ("Nairobi", "Kenya"),
    ("Lagos", "Nigeria"),
    ("Cairo", "Egypt"),
    ("Casablanca", "Morocco"),
    ("Melbourne", "Australia"),
    ("Sydney", "Australia"),
    ("Auckland", "New Zealand"),
    ("Vancouver", "Canada"),
    ("Toronto", "Canada"),
    ("Montreal", "Canada"),
    ("Buenos Aires", "Argentina"),
    ("Lima", "Peru"),
    ("Bogotá", "Colombia"),
    ("Lisbon", "Portugal"),
    ("Athens", "Greece"),
    ("Helsinki", "Finland"),
    ("Oslo", "Norway"),
    ("Stockholm", "Sweden"),
    ("Copenhagen", "Denmark"),
    ("Dublin", "Ireland"),
    ("Zurich", "Switzerland"),
    ("Vienna", "Austria"),
    ("Prague", "Czech Republic"),
    ("Budapest", "Hungary"),
    ("Bucharest", "Romania"),
    ("Warsaw", "Poland"),
    ("Kyiv", "Ukraine"),
    ("Istanbul", "Turkey"),
    ("Tehran", "Iran"),
    ("Riyadh", "Saudi Arabia"),
    ("Dubai", "United Arab Emirates"),
    ("Mumbai", "India"),
    ("Delhi", "India"),
    ("Kolkata", "India"),
    ("Bangalore", "India"),
    ("Lahore", "Pakistan"),
    ("Dhaka", "Bangladesh"),
    ("Colombo", "Sri Lanka"),
    ("Kathmandu", "Nepal"),
]


def build_query_3level(city: str, region: str, tag: str, value: str) -> str:
    """Build 3-level QL: outer=Region, inner=City."""
    return (
        f'[out:json][timeout:30];\n'
        f'area["name:en"="{region}"]->.outer;\n'
        f'area["name:en"="{city}"]->.inner;\n'
        f'(\n'
        f'  nwr["{tag}"="{value}"](area.inner)(area.outer);\n'
        f');\n'
        f'out geom;'
    )


def build_query_2level(city: str, tag: str, value: str) -> str:
    """Build 2-level QL: single searchArea=City."""
    return (
        f'[out:json][timeout:30];\n'
        f'area["name:en"="{city}"]->.searchArea;\n'
        f'(\n'
        f'  nwr["{tag}"="{value}"](area.searchArea);\n'
        f');\n'
        f'out geom;'
    )


def count_query(query: str) -> int:
    """Run Overpass count query with retry/backoff. Returns count or -1 on error."""
    count_ql = query.replace("out geom;", "out count;")
    for attempt in range(4):
        try:
            resp = requests.post(OVERPASS_URL, data={"data": count_ql}, timeout=30)
            if resp.status_code == 429:
                wait = 30 * (attempt + 1)
                print(f"  [429] Rate limited, waiting {wait}s...")
                time.sleep(wait)
                continue
            resp.raise_for_status()
            data = resp.json()
            elements = data.get("elements", [])
            if elements and "tags" in elements[0]:
                return int(elements[0]["tags"].get("total", 0))
            return 0
        except requests.exceptions.HTTPError as e:
            if e.response is not None and e.response.status_code == 429:
                wait = 30 * (attempt + 1)
                print(f"  [429] Rate limited, waiting {wait}s...")
                time.sleep(wait)
                continue
            print(f"  [ERROR] {e}")
            return -1
        except Exception as e:
            print(f"  [ERROR] {e}")
            return -1
    print(f"  [ERROR] Max retries exceeded")
    return -1


def save_pair(dir_path: str, input_text: str, query: str) -> None:
    """Save input-trident.txt and output-001.overpassql to dir_path."""
    os.makedirs(dir_path, exist_ok=True)
    input_file = os.path.join(dir_path, "input-trident.txt")
    output_file = os.path.join(dir_path, "output-001.overpassql")
    if os.path.exists(input_file):
        return  # Skip if already exists
    with open(input_file, "w") as f:
        f.write(input_text)
    with open(output_file, "w") as f:
        f.write(query)


def get_concern_dir(base_dir: str, osm_category: str, osm_value: str) -> str:
    return os.path.join(base_dir, "concerns", osm_category, osm_value)


def main():
    base_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    base_dir = os.path.abspath(base_dir)
    print(f"Dataset base: {base_dir}")

    results = {"created": [], "skipped_zero": [], "skipped_exists": [], "errors": []}

    # --- 3-level ---
    print(f"\n=== Processing {len(LOCATIONS_3LEVEL)} 3-level locations ===")
    for city, region, country in LOCATIONS_3LEVEL:
        for osm_category, osm_tag, osm_value, concern_label in CONCERNS:
            concern_dir = get_concern_dir(base_dir, osm_category, osm_value)
            dir_path = os.path.join(concern_dir, country, region, city)
            input_file = os.path.join(dir_path, "input-trident.txt")

            if os.path.exists(input_file):
                results["skipped_exists"].append(f"{city},{region},{country}:{osm_value}")
                continue

            input_text = f"AreaWithConcern: {city}, {region}, {country}; {concern_label}"
            query = build_query_3level(city, region, osm_tag, osm_value)

            print(f"  Checking: {input_text}")
            count = count_query(query)
            time.sleep(3)  # Rate limiting

            if count < 0:
                print(f"    -> ERROR")
                results["errors"].append(input_text)
            elif count == 0:
                print(f"    -> ZERO (skip)")
                results["skipped_zero"].append(input_text)
            else:
                print(f"    -> {count} elements, SAVING")
                save_pair(dir_path, input_text, query)
                results["created"].append(input_text)

    # --- 2-level ---
    print(f"\n=== Processing {len(LOCATIONS_2LEVEL)} 2-level locations ===")
    for city, country in LOCATIONS_2LEVEL:
        for osm_category, osm_tag, osm_value, concern_label in CONCERNS:
            concern_dir = get_concern_dir(base_dir, osm_category, osm_value)
            dir_path = os.path.join(concern_dir, country, city)
            input_file = os.path.join(dir_path, "input-trident.txt")

            if os.path.exists(input_file):
                results["skipped_exists"].append(f"{city},{country}:{osm_value}")
                continue

            input_text = f"AreaWithConcern: {city}, {country}; {concern_label}"
            query = build_query_2level(city, osm_tag, osm_value)

            print(f"  Checking: {input_text}")
            count = count_query(query)
            time.sleep(3)  # Rate limiting

            if count < 0:
                print(f"    -> ERROR")
                results["errors"].append(input_text)
            elif count == 0:
                print(f"    -> ZERO (skip)")
                results["skipped_zero"].append(input_text)
            else:
                print(f"    -> {count} elements, SAVING")
                save_pair(dir_path, input_text, query)
                results["created"].append(input_text)

    # Summary
    print(f"\n=== Summary ===")
    print(f"Created:        {len(results['created'])}")
    print(f"Skipped (zero): {len(results['skipped_zero'])}")
    print(f"Skipped (exist): {len(results['skipped_exists'])}")
    print(f"Errors:         {len(results['errors'])}")

    results_file = os.path.join(os.path.dirname(__file__), "..", "results", "multilevel_pairs_generation.json")
    os.makedirs(os.path.dirname(results_file), exist_ok=True)
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nResults saved to: {results_file}")


if __name__ == "__main__":
    main()
