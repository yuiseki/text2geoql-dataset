"""Collect input/output pairs from the data directory and push to Hugging Face Hub."""

import os

import datasets
from huggingface_hub import DatasetCard, DatasetCardData


DATASET_CARD = """\
---
license: cc0-1.0
language:
- en
task_categories:
- other
tags:
- openstreetmap
- overpass-ql
- geospatial
- text2sql
- synthetic
---

# text2geoql

A synthetic dataset for training small language models to translate **TRIDENT intermediate language** into **Overpass QL** queries for OpenStreetMap.

## Task

Given a `AreaWithConcern` instruction, generate a valid Overpass QL query:

**Input:**
```
AreaWithConcern: Shinjuku, Tokyo, Japan; Cafes
```

**Output:**
```overpassql
[out:json][timeout:30];
area["name:en"="Tokyo"]->.outer;
area["name:en"="Shinjuku"]->.inner;
(
  nwr["amenity"="cafe"](area.inner)(area.outer);
);
out geom;
```

Areas are listed **smallest to largest** — first token is the innermost area (inner filter), each subsequent token is a larger containing area (outer filter).

## Key result

`Qwen2.5-Coder-0.5B-Instruct` fine-tuned with LoRA (PEFT + TRL) achieves **100.0% (112/112)** on guaranteed-nonempty strict evaluation and runs at **25.8 tok/s on Raspberry Pi 5** (Q4_K_M, llama.cpp).

## Dataset

- ~4,900 validated training pairs
- All queries verified against the public Overpass API (≥ 1 element returned)
- 148 POI categories, global geographic coverage

## Source

GitHub: [yuiseki/text2geoql-dataset](https://github.com/yuiseki/text2geoql-dataset)
"""


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

    card = DatasetCard(DATASET_CARD)
    card.push_to_hub("yuiseki/text2geoql")
    print("Dataset card updated (license: cc0-1.0)")
