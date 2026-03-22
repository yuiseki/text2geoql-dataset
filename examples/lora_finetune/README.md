# LoRA Fine-Tuning Example

Fine-tune `Qwen2.5-Coder-0.5B-Instruct` on the text2geoql dataset using PEFT + TRL.

This example demonstrates that a 0.5B model with **no Few-Shot prompting** can reach
**100.0% accuracy** (112/112) on the guaranteed-nonempty strict evaluation (v4.2 adapter)
— compared to **0% (base)** and the **47% Few-Shot baseline** (see RF-004, RF-009).

## Hardware

| Item | Spec |
|------|------|
| GPU | NVIDIA GeForce RTX 3060 (12 GB VRAM) |
| Training time | ~12 minutes (3 epochs, ~4,900 pairs) |
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

### Overpass API benchmark (30 held-out pairs)

| Condition | Score | Primary failure |
|-----------|-------|-----------------|
| Base 0.5B (no FT, no Few-Shot) | 0.0% (0/30) | `no_code_block` — repeats input verbatim |
| Base 3B (no FT, Few-Shot k=5) | 47% (7/15) | `zero_results` |
| **FT 0.5B LoRA v1 (no Few-Shot)** | **93.3% (28/30)** | `zero_results` × 2 (POI doesn't exist in area) |

### Guaranteed-nonempty strict evaluation (112 pairs — see `eval_guaranteed_nonempty.py`)

All 112 pairs are verified to return ≥1 OSM element; the two-call `name:en→name` fallback is included.

| Adapter | Score | Notes |
|---------|-------|-------|
| v3 | 92.0% (103/112) | Hierarchy inversion + Busan bug |
| v4 | 94.6% (106/112) | Multi-level training data added |
| v4.1 | 99.1% (111/112) | Test data fixed + system prompt + Europe pairs |
| **v4.2** | **100.0% (112/112)** | Ward suffix convention added |

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
| `dataset.py` | Loads training pairs, formats chat template prompts (any tokenizer) |
| `train.py` | LoRA fine-tuning with PEFT + TRL SFTTrainer |
| `evaluate.py` | Benchmark evaluation with real Overpass API scoring |
| `eval_guaranteed_nonempty.py` | Strict eval on 112 guaranteed-nonempty pairs with two-call fallback |
| `precheck_candidates.py` | Pre-screen candidate pairs via Overpass API before adding to dataset |
| `requirements.txt` | Python dependencies |
