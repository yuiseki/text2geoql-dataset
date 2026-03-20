"""Generate TRIDENT input-trident.txt files from seed areas and good_concerns.yaml."""

import os

import yaml

from trident import build_area_with_concern, area_path_from_trident


def load_examples(directory: str) -> list[dict[str, str]]:
    """Walk directory and return all non-empty input-trident.txt entries."""
    examples: list[dict[str, str]] = []
    for root, dirs, files in os.walk(directory):
        if "input-trident.txt" not in files:
            continue
        input_txt = open(os.path.join(root, "input-trident.txt")).read().strip()
        if input_txt:
            examples.append({"input": input_txt, "path": os.path.join(root, "input-trident.txt")})
    return examples


def load_seed_concerns(good_concerns_path: str) -> list[dict[str, str]]:
    """Load concern name → base_path mapping from good_concerns.yaml."""
    with open(good_concerns_path) as f:
        good_concerns: dict[str, str] = yaml.safe_load(f)
    return [{"concern": concern, "base_path": path} for concern, path in good_concerns.items()]


def extract_seed_areas(examples: list[dict[str, str]]) -> list[str]:
    """Extract valid area strings from Area: entries in examples."""
    seed_areas: list[str] = []
    for example in examples:
        input_txt = example["input"]
        if not input_txt.startswith("Area:"):
            continue
        if ";" in input_txt:
            continue
        # Special regions require fewer comma-separated parts
        if "Hong Kong" in input_txt or "Seoul" in input_txt:
            if input_txt.count(",") < 2:
                continue
        else:
            if input_txt.count(",") < 3:
                continue
        new_area = input_txt.replace("Area: ", "").strip()
        if new_area not in seed_areas:
            seed_areas.append(new_area)
    return seed_areas


def generate_missing_tridents(
    seed_areas: list[str],
    seed_concerns: list[dict[str, str]],
    existing_inputs: set[str],
) -> list[dict[str, str]]:
    """Return AreaWithConcern entries not yet present in existing_inputs."""
    results: list[dict[str, str]] = []
    for area in seed_areas:
        for concern_item in seed_concerns:
            area_with_concern = build_area_with_concern(area, concern_item["concern"])
            if area_with_concern in existing_inputs:
                continue
            results.append({"area_with_concern": area_with_concern, "base_path": concern_item["base_path"]})
    return results


def write_trident_files(items: list[dict[str, str]]) -> None:
    """Write input-trident.txt files for each item."""
    for item in items:
        print(item["area_with_concern"])
        area_name_reversed = area_path_from_trident(item["area_with_concern"])
        item_path = os.path.join(item["base_path"], area_name_reversed)
        print(item_path)
        os.makedirs(item_path, exist_ok=True)
        with open(os.path.join(item_path, "input-trident.txt"), "w") as f:
            f.write(f"{item['area_with_concern']}\n")


if __name__ == "__main__":
    examples = load_examples("./data")
    seed_concerns = load_seed_concerns("good_concerns.yaml")
    seed_areas = extract_seed_areas(examples)
    existing_inputs = {e["input"] for e in examples}
    items = generate_missing_tridents(seed_areas, seed_concerns, existing_inputs)
    write_trident_files(items)
