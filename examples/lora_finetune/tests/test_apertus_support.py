"""Pure-function tests for Apertus support in the LoRA fine-tuning example.

No GPU/model loading required. Run with:
    uv run pytest examples/lora_finetune/tests
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dataset import requires_bf16
from train import lora_target_modules


def test_requires_bf16_true_for_apertus() -> None:
    assert requires_bf16("swiss-ai/Apertus-v1.1-0.5B-Instruct") is True


def test_requires_bf16_true_for_gemma() -> None:
    assert requires_bf16("google/gemma-3-1b-it") is True


def test_requires_bf16_false_for_qwen() -> None:
    assert requires_bf16("Qwen/Qwen2.5-Coder-0.5B-Instruct") is False


def test_lora_target_modules_excludes_gate_proj_for_apertus() -> None:
    assert "gate_proj" not in lora_target_modules("swiss-ai/Apertus-v1.1-0.5B-Instruct")


def test_lora_target_modules_includes_gate_proj_for_others() -> None:
    assert "gate_proj" in lora_target_modules("Qwen/Qwen2.5-Coder-0.5B-Instruct")
