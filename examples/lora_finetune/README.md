# LoRA Fine-Tuning Example

Fine-tune `Qwen2.5-Coder-0.5B-Instruct` on the text2geoql dataset using PEFT + TRL.

This example demonstrates that a 0.5B model with **no Few-Shot prompting** can reach
**93.3% accuracy** on the Overpass API benchmark after LoRA fine-tuning — compared to
**0% (base)** and the **47% Few-Shot baseline** (see RF-004).

## Hardware

| Item | Spec |
|------|------|
| GPU | NVIDIA GeForce RTX 3060 (12 GB VRAM) |
| Training time | ~12 minutes (3 epochs, 4278 pairs) |
| Adapter size | ~35 MB |

CPU-only is also supported (much slower).

## Setup

```bash
pip install -r examples/lora_finetune/requirements.txt
```

> **Note:** Unsloth is intentionally not used due to known LoRA save/load bugs
> ([#1670](https://github.com/unslothai/unsloth/issues/1670),
> [#1805](https://github.com/unslothai/unsloth/issues/1805)).
> PEFT + TRL work reliably.

## Training

```bash
# Default: Qwen2.5-Coder-0.5B-Instruct, 3 epochs, batch_size=8
uv run python examples/lora_finetune/train.py

# Custom options
uv run python examples/lora_finetune/train.py \
  --model Qwen/Qwen2.5-Coder-0.5B-Instruct \
  --output-dir models/qwen2.5-coder-0.5b-lora \
  --epochs 3 \
  --batch-size 4
```

The adapter is saved to `--output-dir` (default: `models/qwen2.5-coder-0.5b-lora/`).

## Evaluation

Evaluation executes each generated query against the real Overpass API, matching
the methodology of `src/benchmark_models.py`.

```bash
# Base model (before FT)
uv run python examples/lora_finetune/evaluate.py \
  --output-json results/before.json

# Fine-tuned adapter (after FT)
uv run python examples/lora_finetune/evaluate.py \
  --adapter models/qwen2.5-coder-0.5b-lora \
  --output-json results/after.json
```

## Results

| Condition | Score | Primary failure |
|-----------|-------|-----------------|
| Base 0.5B (no FT, no Few-Shot) | 0.0% (0/30) | `no_code_block` — repeats input verbatim |
| Base 3B (no FT, Few-Shot k=5) | 47% (7/15) | `zero_results` |
| **FT 0.5B LoRA (no Few-Shot)** | **93.3% (28/30)** | `zero_results` × 2 (POI doesn't exist in area) |

The 2 remaining failures are data-level issues (e.g. no embassies in Hong Kong's Islands
District), not model errors.

## LoRA Hyperparameters

| Parameter | Value |
|-----------|-------|
| r | 16 |
| lora_alpha | 32 |
| lora_dropout | 0.05 |
| target_modules | q/k/v/o/gate/up/down_proj |
| epochs | 3 |
| batch_size | 8 |
| grad_accumulation | 2 |
| learning_rate | 2e-4 |
| lr_scheduler | cosine |
| max_seq_len | 512 |

## Files

| File | Description |
|------|-------------|
| `dataset.py` | Loads training pairs, formats Qwen chat template prompts |
| `train.py` | LoRA fine-tuning with PEFT + TRL SFTTrainer |
| `evaluate.py` | Benchmark evaluation with real Overpass API scoring |
| `requirements.txt` | Python dependencies |
