"""Collect input/output pairs from the data directory and push to Hugging Face Hub."""

import os

import datasets


def collect_text2geoql_files(directory: str) -> list[dict[str, str]]:
    """Walk directory and collect paired input-trident / output-*.overpassql entries."""
    results: list[dict[str, str]] = []
    for root, dirs, files in os.walk(directory):
        if "input-trident.txt" not in files:
            continue
        input_txt = open(os.path.join(root, "input-trident.txt")).read().strip()
        output_files = [
            f for f in files if f.startswith("output-") and f.endswith(".overpassql")
        ]
        for output_file in output_files:
            output_txt = open(os.path.join(root, output_file)).read().strip()
            results.append(
                {
                    "input": input_txt,
                    "input_type": "trident",
                    "output": output_txt,
                    "output_type": "overpassql",
                }
            )
    return results


if __name__ == "__main__":
    dir_path = "./data"
    records = collect_text2geoql_files(dir_path)
    my_dataset = datasets.Dataset.from_list(records)
    print(my_dataset)
    my_dataset.push_to_hub("yuiseki/text2geoql")
