"""Load text2geoql training pairs and format for instruction fine-tuning.

Data sources (from this repository):
  data/concerns/{key}/{value}/{area}/input-trident.txt
  data/concerns/{key}/{value}/{area}/output-001.overpassql          <- validated gold
  data/concerns/{key}/{value}/{area}/output-qwen2.5-coder-3b.overpassql

Usage:
    >>> pairs = load_pairs()                  # uses DATASET_DIR default
    >>> ds = build_hf_dataset(pairs)
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

# Default: two levels up from this file (i.e. the repo root)
DATASET_DIR = os.environ.get(
    "TEXT2GEOQL_DATASET_DIR",
    os.path.join(os.path.dirname(__file__), "..", ".."),
)

OUTPUT_FILENAMES = ["output-001.overpassql", "output-qwen2.5-coder-3b.overpassql"]

SYSTEM_PROMPT = (
    "You are an expert at generating Overpass QL queries for OpenStreetMap. "
    "Given a location and a point-of-interest type, output only a valid Overpass QL query "
    "with no explanation."
)


@dataclass
class TrainingPair:
    input_text: str   # content of input-trident.txt
    output_text: str  # content of output-*.overpassql
    source: str       # e.g. "output-001" or "output-qwen2.5-coder-3b"


def iter_pairs(dataset_dir: str = DATASET_DIR) -> Iterator[TrainingPair]:
    """Yield TrainingPair for every (input-trident.txt, output-*.overpassql) pair found."""
    concerns_dir = Path(dataset_dir) / "data" / "concerns"
    if not concerns_dir.exists():
        return

    for trident_path in sorted(concerns_dir.rglob("input-trident.txt")):
        input_text = trident_path.read_text().strip()
        node_dir = trident_path.parent
        for fname in OUTPUT_FILENAMES:
            output_path = node_dir / fname
            if output_path.exists():
                output_text = output_path.read_text().strip()
                source = fname.replace(".overpassql", "")
                yield TrainingPair(input_text=input_text, output_text=output_text, source=source)
                break  # prefer output-001 when both exist


def load_pairs(dataset_dir: str = DATASET_DIR) -> list[TrainingPair]:
    """Return all training pairs as a list."""
    return list(iter_pairs(dataset_dir))


def format_prompt(input_text: str, output_text: str | None = None) -> str:
    """Format a pair as a Qwen2.5 chat template string.

    With output_text=None  → inference prompt (ends at <|im_start|>assistant\\n)
    With output_text given → full training string (ends at <|im_end|>)
    """
    messages = (
        f"<|im_start|>system\n{SYSTEM_PROMPT}<|im_end|>\n"
        f"<|im_start|>user\n{input_text}<|im_end|>\n"
        f"<|im_start|>assistant\n"
    )
    if output_text is not None:
        messages += f"{output_text}<|im_end|>"
    return messages


def build_hf_dataset(
    pairs: list[TrainingPair],
    *,
    val_ratio: float = 0.05,
    seed: int = 42,
):
    """Build a HuggingFace DatasetDict with train/validation splits.

    Returns datasets.DatasetDict with 'train' and 'validation' keys.
    Each example has a 'text' field containing the full formatted prompt+response.
    """
    from datasets import Dataset, DatasetDict

    texts = [format_prompt(p.input_text, p.output_text) for p in pairs]
    ds = Dataset.from_dict({"text": texts})
    split = ds.train_test_split(test_size=val_ratio, seed=seed)
    return DatasetDict({"train": split["train"], "validation": split["test"]})
