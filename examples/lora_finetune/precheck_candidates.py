"""Pre-verify candidate guaranteed-nonempty pairs against Overpass API.

Runs ~150 candidate (input, POI) pairs through Overpass API pre-verification.
Saves only confirmed pairs (element count > 0) to a JSON file for use with
eval_guaranteed_nonempty.py --confirmed-pairs-json.

Pre-verification queries use ["name:en"=...] to maximise consistency with
what the model will generate. Candidates that fail (no name:en in OSM, or
no POI data) are automatically dropped.

Usage:
    uv run python src/precheck_candidates.py \\
        --output results/confirmed_pairs_v2.json
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

OVERPASS_ENDPOINT = "https://overpass.yuiseki.net/api/interpreter"

# ---------------------------------------------------------------------------
# Candidate specs: (input_text, verify_city_name_en, osm_tag, osm_value)
#
# verify_city_name_en: the name:en value used in the pre-verification query.
# This is the innermost city/district in the location hierarchy.
# ---------------------------------------------------------------------------
# fmt: off
CANDIDATE_SPECS: list[tuple[str, str, str, str]] = [
    # ── Europe: Central ─────────────────────────────────────────────────────
    ("AreaWithConcern: Vienna, Austria; Cafes",              "Vienna",     "amenity", "cafe"),
    ("AreaWithConcern: Vienna, Austria; Restaurants",        "Vienna",     "amenity", "restaurant"),
    ("AreaWithConcern: Vienna, Austria; Museums",            "Vienna",     "tourism", "museum"),
    ("AreaWithConcern: Vienna, Austria; Pharmacies",         "Vienna",     "amenity", "pharmacy"),
    ("AreaWithConcern: Prague, Czech Republic; Cafes",       "Prague",     "amenity", "cafe"),
    ("AreaWithConcern: Prague, Czech Republic; Restaurants", "Prague",     "amenity", "restaurant"),
    ("AreaWithConcern: Prague, Czech Republic; Hotels",      "Prague",     "tourism", "hotel"),
    ("AreaWithConcern: Budapest, Hungary; Cafes",            "Budapest",   "amenity", "cafe"),
    ("AreaWithConcern: Budapest, Hungary; Restaurants",      "Budapest",   "amenity", "restaurant"),
    ("AreaWithConcern: Budapest, Hungary; Hotels",           "Budapest",   "tourism", "hotel"),
    ("AreaWithConcern: Warsaw, Poland; Restaurants",         "Warsaw",     "amenity", "restaurant"),
    ("AreaWithConcern: Warsaw, Poland; Hotels",              "Warsaw",     "tourism", "hotel"),
    ("AreaWithConcern: Bratislava, Slovakia; Cafes",         "Bratislava", "amenity", "cafe"),
    ("AreaWithConcern: Bratislava, Slovakia; Restaurants",   "Bratislava", "amenity", "restaurant"),
    ("AreaWithConcern: Ljubljana, Slovenia; Cafes",          "Ljubljana",  "amenity", "cafe"),
    ("AreaWithConcern: Zagreb, Croatia; Cafes",              "Zagreb",     "amenity", "cafe"),
    ("AreaWithConcern: Zagreb, Croatia; Restaurants",        "Zagreb",     "amenity", "restaurant"),
    ("AreaWithConcern: Bucharest, Romania; Restaurants",     "Bucharest",  "amenity", "restaurant"),
    ("AreaWithConcern: Bucharest, Romania; Hotels",          "Bucharest",  "tourism", "hotel"),
    ("AreaWithConcern: Sofia, Bulgaria; Cafes",              "Sofia",      "amenity", "cafe"),
    ("AreaWithConcern: Athens, Greece; Restaurants",         "Athens",     "amenity", "restaurant"),
    ("AreaWithConcern: Athens, Greece; Hotels",              "Athens",     "tourism", "hotel"),

    # ── Europe: West/North ──────────────────────────────────────────────────
    ("AreaWithConcern: Dublin, Ireland; Cafes",              "Dublin",     "amenity", "cafe"),
    ("AreaWithConcern: Dublin, Ireland; Restaurants",        "Dublin",     "amenity", "restaurant"),
    ("AreaWithConcern: Brussels, Belgium; Cafes",            "Brussels",   "amenity", "cafe"),
    ("AreaWithConcern: Brussels, Belgium; Restaurants",      "Brussels",   "amenity", "restaurant"),
    ("AreaWithConcern: Copenhagen, Denmark; Cafes",          "Copenhagen", "amenity", "cafe"),
    ("AreaWithConcern: Copenhagen, Denmark; Restaurants",    "Copenhagen", "amenity", "restaurant"),
    ("AreaWithConcern: Stockholm, Sweden; Cafes",            "Stockholm",  "amenity", "cafe"),
    ("AreaWithConcern: Stockholm, Sweden; Museums",          "Stockholm",  "tourism", "museum"),
    ("AreaWithConcern: Helsinki, Finland; Cafes",            "Helsinki",   "amenity", "cafe"),
    ("AreaWithConcern: Helsinki, Finland; Restaurants",      "Helsinki",   "amenity", "restaurant"),
    ("AreaWithConcern: Oslo, Norway; Cafes",                 "Oslo",       "amenity", "cafe"),
    ("AreaWithConcern: Oslo, Norway; Restaurants",           "Oslo",       "amenity", "restaurant"),
    ("AreaWithConcern: Zurich, Switzerland; Cafes",          "Zurich",     "amenity", "cafe"),
    ("AreaWithConcern: Zurich, Switzerland; Hotels",         "Zurich",     "tourism", "hotel"),
    ("AreaWithConcern: Geneva, Switzerland; Cafes",          "Geneva",     "amenity", "cafe"),
    ("AreaWithConcern: Madrid, Spain; Restaurants",          "Madrid",     "amenity", "restaurant"),
    ("AreaWithConcern: Madrid, Spain; Museums",              "Madrid",     "tourism", "museum"),
    ("AreaWithConcern: Lisbon, Portugal; Cafes",             "Lisbon",     "amenity", "cafe"),
    ("AreaWithConcern: Lisbon, Portugal; Restaurants",       "Lisbon",     "amenity", "restaurant"),
    ("AreaWithConcern: Kyiv, Ukraine; Cafes",                "Kyiv",       "amenity", "cafe"),
    ("AreaWithConcern: Kyiv, Ukraine; Restaurants",          "Kyiv",       "amenity", "restaurant"),

    # ── Europe: 3-level (City, Region, Country) ─────────────────────────────
    ("AreaWithConcern: Munich, Bavaria, Germany; Cafes",          "Munich",     "amenity", "cafe"),
    ("AreaWithConcern: Munich, Bavaria, Germany; Restaurants",    "Munich",     "amenity", "restaurant"),
    ("AreaWithConcern: Munich, Bavaria, Germany; Museums",        "Munich",     "tourism", "museum"),
    ("AreaWithConcern: Hamburg, Hamburg, Germany; Cafes",         "Hamburg",    "amenity", "cafe"),
    ("AreaWithConcern: Hamburg, Hamburg, Germany; Restaurants",   "Hamburg",    "amenity", "restaurant"),
    ("AreaWithConcern: Cologne, North Rhine-Westphalia, Germany; Restaurants", "Cologne", "amenity", "restaurant"),
    ("AreaWithConcern: Lyon, Auvergne-Rhône-Alpes, France; Restaurants",      "Lyon",    "amenity", "restaurant"),
    ("AreaWithConcern: Lyon, Auvergne-Rhône-Alpes, France; Cafes",            "Lyon",    "amenity", "cafe"),
    ("AreaWithConcern: Marseille, Provence-Alpes-Côte d'Azur, France; Restaurants", "Marseille", "amenity", "restaurant"),
    ("AreaWithConcern: Porto, Norte, Portugal; Cafes",            "Porto",      "amenity", "cafe"),
    ("AreaWithConcern: Porto, Norte, Portugal; Restaurants",      "Porto",      "amenity", "restaurant"),
    ("AreaWithConcern: Seville, Andalusia, Spain; Restaurants",   "Seville",    "amenity", "restaurant"),
    ("AreaWithConcern: Valencia, Community of Valencia, Spain; Restaurants", "Valencia", "amenity", "restaurant"),
    ("AreaWithConcern: Kraków, Lesser Poland, Poland; Cafes",     "Kraków",     "amenity", "cafe"),
    ("AreaWithConcern: Kraków, Lesser Poland, Poland; Restaurants","Kraków",    "amenity", "restaurant"),
    ("AreaWithConcern: Gdańsk, Pomerania, Poland; Cafes",         "Gdańsk",     "amenity", "cafe"),
    ("AreaWithConcern: Turin, Piedmont, Italy; Cafes",            "Turin",      "amenity", "cafe"),
    ("AreaWithConcern: Turin, Piedmont, Italy; Restaurants",      "Turin",      "amenity", "restaurant"),
    ("AreaWithConcern: Florence, Tuscany, Italy; Restaurants",    "Florence",   "amenity", "restaurant"),
    ("AreaWithConcern: Florence, Tuscany, Italy; Hotels",         "Florence",   "tourism", "hotel"),
    ("AreaWithConcern: Naples, Campania, Italy; Restaurants",     "Naples",     "amenity", "restaurant"),

    # ── Europe: 3-level (District, City, Country) ───────────────────────────
    ("AreaWithConcern: Mitte, Berlin, Germany; Restaurants",      "Mitte",      "amenity", "restaurant"),
    ("AreaWithConcern: Mitte, Berlin, Germany; Hotels",           "Mitte",      "tourism", "hotel"),
    ("AreaWithConcern: Pankow, Berlin, Germany; Cafes",           "Pankow",     "amenity", "cafe"),
    ("AreaWithConcern: Westminster, London, United Kingdom; Hotels",   "Westminster", "tourism", "hotel"),
    ("AreaWithConcern: Camden, London, United Kingdom; Cafes",    "Camden",     "amenity", "cafe"),
    ("AreaWithConcern: Tower Hamlets, London, United Kingdom; Restaurants", "Tower Hamlets", "amenity", "restaurant"),

    # ── East Asia (non-training) ─────────────────────────────────────────────
    ("AreaWithConcern: Taipei, Taiwan; Cafes",                    "Taipei",     "amenity", "cafe"),
    ("AreaWithConcern: Taipei, Taiwan; Restaurants",              "Taipei",     "amenity", "restaurant"),
    ("AreaWithConcern: Taipei, Taiwan; Hotels",                   "Taipei",     "tourism", "hotel"),
    ("AreaWithConcern: Bangkok, Thailand; Restaurants",           "Bangkok",    "amenity", "restaurant"),
    ("AreaWithConcern: Bangkok, Thailand; Hotels",                "Bangkok",    "tourism", "hotel"),
    ("AreaWithConcern: Kuala Lumpur, Malaysia; Restaurants",      "Kuala Lumpur", "amenity", "restaurant"),
    ("AreaWithConcern: Kuala Lumpur, Malaysia; Hotels",           "Kuala Lumpur", "tourism", "hotel"),
    ("AreaWithConcern: Ho Chi Minh City, Vietnam; Restaurants",   "Ho Chi Minh City", "amenity", "restaurant"),
    ("AreaWithConcern: Ho Chi Minh City, Vietnam; Hotels",        "Ho Chi Minh City", "tourism", "hotel"),
    ("AreaWithConcern: Jakarta, Indonesia; Restaurants",          "Jakarta",    "amenity", "restaurant"),
    ("AreaWithConcern: Jakarta, Indonesia; Hotels",               "Jakarta",    "tourism", "hotel"),
    ("AreaWithConcern: Manila, Philippines; Restaurants",         "Manila",     "amenity", "restaurant"),
    ("AreaWithConcern: Manila, Philippines; Hotels",              "Manila",     "tourism", "hotel"),

    # ── South Asia (non-training) ────────────────────────────────────────────
    ("AreaWithConcern: Mumbai, Maharashtra, India; Restaurants",  "Mumbai",     "amenity", "restaurant"),
    ("AreaWithConcern: Mumbai, Maharashtra, India; Hotels",       "Mumbai",     "tourism", "hotel"),
    ("AreaWithConcern: Delhi, India; Restaurants",                "Delhi",      "amenity", "restaurant"),
    ("AreaWithConcern: Delhi, India; Hotels",                     "Delhi",      "tourism", "hotel"),
    ("AreaWithConcern: Bangalore, Karnataka, India; Cafes",       "Bangalore",  "amenity", "cafe"),
    ("AreaWithConcern: Kathmandu, Nepal; Hotels",                 "Kathmandu",  "tourism", "hotel"),
    ("AreaWithConcern: Kathmandu, Nepal; Restaurants",            "Kathmandu",  "amenity", "restaurant"),

    # ── Middle East / Turkey ─────────────────────────────────────────────────
    ("AreaWithConcern: Istanbul, Turkey; Cafes",                  "Istanbul",   "amenity", "cafe"),
    ("AreaWithConcern: Istanbul, Turkey; Restaurants",            "Istanbul",   "amenity", "restaurant"),
    ("AreaWithConcern: Istanbul, Turkey; Hotels",                 "Istanbul",   "tourism", "hotel"),
    ("AreaWithConcern: Ankara, Turkey; Restaurants",              "Ankara",     "amenity", "restaurant"),
    ("AreaWithConcern: Ankara, Turkey; Hotels",                   "Ankara",     "tourism", "hotel"),
    ("AreaWithConcern: Amman, Jordan; Restaurants",               "Amman",      "amenity", "restaurant"),
    ("AreaWithConcern: Amman, Jordan; Hotels",                    "Amman",      "tourism", "hotel"),
    ("AreaWithConcern: Beirut, Lebanon; Restaurants",             "Beirut",     "amenity", "restaurant"),
    ("AreaWithConcern: Muscat, Oman; Hotels",                     "Muscat",     "tourism", "hotel"),

    # ── Africa ───────────────────────────────────────────────────────────────
    ("AreaWithConcern: Nairobi, Kenya; Restaurants",              "Nairobi",    "amenity", "restaurant"),
    ("AreaWithConcern: Nairobi, Kenya; Hotels",                   "Nairobi",    "tourism", "hotel"),
    ("AreaWithConcern: Cape Town, South Africa; Cafes",           "Cape Town",  "amenity", "cafe"),
    ("AreaWithConcern: Cape Town, South Africa; Restaurants",     "Cape Town",  "amenity", "restaurant"),
    ("AreaWithConcern: Accra, Ghana; Restaurants",                "Accra",      "amenity", "restaurant"),
    ("AreaWithConcern: Accra, Ghana; Hotels",                     "Accra",      "tourism", "hotel"),
    ("AreaWithConcern: Casablanca, Morocco; Cafes",               "Casablanca", "amenity", "cafe"),
    ("AreaWithConcern: Tunis, Tunisia; Cafes",                    "Tunis",      "amenity", "cafe"),
    ("AreaWithConcern: Addis Ababa, Ethiopia; Hotels",            "Addis Ababa","tourism", "hotel"),
    ("AreaWithConcern: Dakar, Senegal; Restaurants",              "Dakar",      "amenity", "restaurant"),

    # ── Americas ─────────────────────────────────────────────────────────────
    ("AreaWithConcern: Toronto, Ontario, Canada; Cafes",          "Toronto",    "amenity", "cafe"),
    ("AreaWithConcern: Toronto, Ontario, Canada; Restaurants",    "Toronto",    "amenity", "restaurant"),
    ("AreaWithConcern: Toronto, Ontario, Canada; Museums",        "Toronto",    "tourism", "museum"),
    ("AreaWithConcern: Vancouver, British Columbia, Canada; Cafes",    "Vancouver", "amenity", "cafe"),
    ("AreaWithConcern: Vancouver, British Columbia, Canada; Restaurants","Vancouver","amenity","restaurant"),
    ("AreaWithConcern: Montreal, Quebec, Canada; Cafes",          "Montreal",   "amenity", "cafe"),
    ("AreaWithConcern: Montreal, Quebec, Canada; Restaurants",    "Montreal",   "amenity", "restaurant"),
    ("AreaWithConcern: Buenos Aires, Argentina; Cafes",           "Buenos Aires","amenity","cafe"),
    ("AreaWithConcern: Buenos Aires, Argentina; Restaurants",     "Buenos Aires","amenity","restaurant"),
    ("AreaWithConcern: Santiago, Chile; Cafes",                   "Santiago",   "amenity", "cafe"),
    ("AreaWithConcern: Santiago, Chile; Restaurants",             "Santiago",   "amenity", "restaurant"),
    ("AreaWithConcern: Lima, Peru; Restaurants",                  "Lima",       "amenity", "restaurant"),
    ("AreaWithConcern: Lima, Peru; Hotels",                       "Lima",       "tourism", "hotel"),
    ("AreaWithConcern: Bogotá, Colombia; Cafes",                  "Bogotá",     "amenity", "cafe"),
    ("AreaWithConcern: Bogotá, Colombia; Restaurants",            "Bogotá",     "amenity", "restaurant"),
    ("AreaWithConcern: Montevideo, Uruguay; Cafes",               "Montevideo", "amenity", "cafe"),
    ("AreaWithConcern: Medellín, Colombia; Cafes",                "Medellín",   "amenity", "cafe"),

    # ── Oceania ──────────────────────────────────────────────────────────────
    ("AreaWithConcern: Melbourne, Victoria, Australia; Cafes",    "Melbourne",  "amenity", "cafe"),
    ("AreaWithConcern: Melbourne, Victoria, Australia; Restaurants","Melbourne","amenity", "restaurant"),
    ("AreaWithConcern: Brisbane, Queensland, Australia; Cafes",   "Brisbane",   "amenity", "cafe"),
    ("AreaWithConcern: Perth, Western Australia, Australia; Cafes","Perth",     "amenity", "cafe"),
    ("AreaWithConcern: Wellington, New Zealand; Cafes",           "Wellington", "amenity", "cafe"),
    ("AreaWithConcern: Auckland, New Zealand; Cafes",             "Auckland",   "amenity", "cafe"),
    ("AreaWithConcern: Auckland, New Zealand; Restaurants",       "Auckland",   "amenity", "restaurant"),

    # ── Japan (seen country, new cities/wards) ───────────────────────────────
    ("AreaWithConcern: Sapporo, Hokkaido, Japan; Cafes",          "Sapporo",    "amenity", "cafe"),
    ("AreaWithConcern: Sendai, Miyagi, Japan; Restaurants",       "Sendai",     "amenity", "restaurant"),
    ("AreaWithConcern: Nagoya, Aichi, Japan; Restaurants",        "Nagoya",     "amenity", "restaurant"),
    ("AreaWithConcern: Fukuoka, Fukuoka, Japan; Cafes",           "Fukuoka",    "amenity", "cafe"),
    ("AreaWithConcern: Naha, Okinawa, Japan; Restaurants",        "Naha",       "amenity", "restaurant"),
    ("AreaWithConcern: Chuo, Sapporo, Hokkaido, Japan; Convenience stores", "Chuo", "shop", "convenience"),
    ("AreaWithConcern: Hakata, Fukuoka, Fukuoka, Japan; Restaurants",        "Hakata","amenity","restaurant"),

    # ── Korea (seen country, new cities/districts) ───────────────────────────
    ("AreaWithConcern: Busan, South Korea; Cafes",                "Busan",      "amenity", "cafe"),
    ("AreaWithConcern: Busan, South Korea; Restaurants",          "Busan",      "amenity", "restaurant"),
    ("AreaWithConcern: Incheon, South Korea; Hotels",             "Incheon",    "tourism", "hotel"),
    ("AreaWithConcern: Daegu, South Korea; Cafes",                "Daegu",      "amenity", "cafe"),
    ("AreaWithConcern: Haeundae-gu, Busan, South Korea; Restaurants","Haeundae-gu","amenity","restaurant"),
    ("AreaWithConcern: Jung-gu, Busan, South Korea; Cafes",       "Jung-gu",    "amenity", "cafe"),
]
# fmt: on


def build_verify_query(city_name_en: str, osm_tag: str, osm_value: str) -> str:
    """Build a fast Overpass count query using name:en."""
    return (
        f'[out:json][timeout:60];\n'
        f'area["name:en"="{city_name_en}"]->.a;\n'
        f'(nwr["{osm_tag}"="{osm_value}"](area.a););\n'
        f'out count;'
    )


def fetch_count(query: str) -> int:
    """Run a verification query (out count) and return the element count."""
    import httpx
    try:
        response = httpx.get(OVERPASS_ENDPOINT, params={"data": query}, timeout=75)
        data = response.json()
        elements = data.get("elements", [])
        if elements and elements[0].get("type") == "count":
            return int(elements[0].get("tags", {}).get("total", 0))
        return len(elements)
    except Exception as e:
        print(f"    [verify error] {e}")
        return -1


def run_precheck(output_path: str) -> None:
    confirmed = []
    skipped = []
    n = len(CANDIDATE_SPECS)
    t0 = time.time()

    print(f"Pre-verifying {n} candidate pairs against Overpass API...")
    print(f"Endpoint: {OVERPASS_ENDPOINT}\n")

    for i, (input_text, city_name_en, osm_tag, osm_value) in enumerate(CANDIDATE_SPECS):
        query = build_verify_query(city_name_en, osm_tag, osm_value)
        count = fetch_count(query)

        if count > 0:
            confirmed.append({
                "input": input_text,
                "verification_query": query,
                "verified_count": count,
            })
            status = f"✓ count={count}"
        elif count == 0:
            skipped.append(input_text)
            status = "✗ zero (dropped)"
        else:
            skipped.append(input_text)
            status = "✗ error (dropped)"

        elapsed = time.time() - t0
        label = f"{city_name_en}:{osm_value}"
        print(f"  [{i+1:3d}/{n}] {status:<20} {label:<35} ({elapsed:.0f}s)")

    print(f"\nConfirmed: {len(confirmed)}/{n}  Dropped: {len(skipped)}")
    if skipped:
        print("Dropped inputs:")
        for s in skipped:
            print(f"  - {s}")

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(confirmed, f, indent=2, ensure_ascii=False)
    print(f"\nSaved {len(confirmed)} confirmed pairs to {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Pre-verify candidate guaranteed-nonempty pairs"
    )
    parser.add_argument(
        "--output",
        default="results/confirmed_pairs_v2.json",
        help="Output JSON path for confirmed pairs",
    )
    args = parser.parse_args()
    run_precheck(args.output)


if __name__ == "__main__":
    main()
