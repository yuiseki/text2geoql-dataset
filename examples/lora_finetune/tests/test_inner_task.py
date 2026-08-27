"""Training the inner layer with the same tooling that trained the deep layer.

The deep layer maps TRIDENT's intermediate language to Overpass QL and reads
its pairs out of data/concerns. The inner layer maps a human utterance to the
intermediate language and reads its pairs out of a JSONL the assembler wrote.
Same LoRA recipe, different source and different system prompt.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dataset import (  # noqa: E402
    INNER_SYSTEM_PROMPT,
    SYSTEM_PROMPT,
    format_prompt,
    load_inner_pairs,
)

PAIR = {
    "input": "新潟市中央区の空港を教えてください",
    "output": (
        "ConfirmHelpful: 地図の作成が完了しました。\n"
        "TitleOfMap: 新潟市中央区の空港\n"
        "Area: Chuo Ward, Niigata, Niigata Prefecture, Japan\n"
        "AreaWithConcern: Chuo Ward, Niigata, Niigata Prefecture, Japan, Airports\n"
        "EmojiForConcern: Airports, ✈️\n"
        "ColorForConcern: Airports, lightblue"
    ),
    "lang": "ja",
    "levels": 4,
    "verdict": "accepted",
}


def write_jsonl(tmp_path: Path, rows: list[dict]) -> Path:
    path = tmp_path / "train.jsonl"
    path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n")
    return path


class TestLoadInnerPairs:
    def test_reads_the_utterance_and_the_block(self, tmp_path: Path) -> None:
        pairs = load_inner_pairs(write_jsonl(tmp_path, [PAIR]))
        assert len(pairs) == 1
        assert pairs[0].input_text == "新潟市中央区の空港を教えてください"
        assert pairs[0].output_text.startswith("ConfirmHelpful:")

    def test_records_where_the_pair_came_from(self, tmp_path: Path) -> None:
        pairs = load_inner_pairs(write_jsonl(tmp_path, [PAIR]))
        assert pairs[0].source == "accepted"

    def test_skips_blank_lines(self, tmp_path: Path) -> None:
        path = tmp_path / "train.jsonl"
        path.write_text(json.dumps(PAIR, ensure_ascii=False) + "\n\n")
        assert len(load_inner_pairs(path)) == 1

    def test_a_pair_with_no_output_is_skipped(self, tmp_path: Path) -> None:
        pairs = load_inner_pairs(write_jsonl(tmp_path, [PAIR, {**PAIR, "output": ""}]))
        assert len(pairs) == 1

    def test_an_empty_file_yields_nothing(self, tmp_path: Path) -> None:
        path = tmp_path / "train.jsonl"
        path.write_text("")
        assert load_inner_pairs(path) == []


class TestTheInnerSystemPrompt:
    def test_it_is_not_the_deep_one(self) -> None:
        assert INNER_SYSTEM_PROMPT != SYSTEM_PROMPT

    def test_it_names_every_key_the_block_must_carry(self) -> None:
        for key in ("ConfirmHelpful", "TitleOfMap", "Area", "AreaWithConcern",
                    "EmojiForConcern", "ColorForConcern"):
            assert key in INNER_SYSTEM_PROMPT

    def test_it_asks_for_the_hierarchy_smallest_first(self) -> None:
        # The measured weakness: four levels come back as two.
        assert "smallest" in INNER_SYSTEM_PROMPT.lower()

    def test_it_asks_for_the_human_s_language(self) -> None:
        assert "language" in INNER_SYSTEM_PROMPT.lower()

    def test_it_can_be_used_to_format_a_pair(self) -> None:
        text = format_prompt(PAIR["input"], PAIR["output"], system_prompt=INNER_SYSTEM_PROMPT)
        assert INNER_SYSTEM_PROMPT in text
        assert PAIR["input"] in text
        assert "AreaWithConcern:" in text

    def test_the_deep_prompt_is_still_the_default(self) -> None:
        assert SYSTEM_PROMPT in format_prompt("AreaWithConcern: Japan; Cafes")
