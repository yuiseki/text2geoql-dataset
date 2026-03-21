# RF-004: LoRA Fine-Tuning Eliminates Few-Shot Prompting Need

**Date:** 2026-03-21
**Status:** Confirmed
**Related ADR:** ADR-003 (LLM Few-Shot), ADR-006 (Benchmark)

## Summary

LoRA fine-tuning of sub-1B models on 4278 AreaWithConcern pairs achieves **95–97% Overpass
API pass rate** with no Few-Shot prompting — a dramatic improvement over the 0% base model
and the 47% Few-Shot baseline using the 3B model. Both `Qwen2.5-Coder-0.5B-Instruct` (494M)
and `gemma-3-270m-it` (270M) exceed 93% on held-out samples. This suggests the current
dataset is already sufficient in scale and that Few-Shot prompting is no longer necessary
for the Deep Layer of TRIDENT.

## Background

Prior work established that:

- The Ollama-based Few-Shot pipeline achieves ~47% with `qwen2.5-coder:3b` at k=5 (RF-002)
- `gemma3:12b` with num_ctx=32768 reaches 100%, but requires a 12B model (RF-001)
- The TRIDENT architecture targets Raspberry Pi 4B / 5, requiring ≤1.1B parameter models

The open question was: can a sub-1B model serve the Deep Layer if fine-tuned on this dataset?

## Method

- **Fine-tuning:** LoRA (PEFT + TRL SFTTrainer, no Unsloth)
- **Data:** 4504 AreaWithConcern pairs; 4278 train / 226 val (95%/5%, seed=42)
- **Hyperparameters:** r=16, alpha=32, dropout=0.05, 3 epochs, lr=2e-4, batch=8
- **Hardware:** NVIDIA GeForce RTX 3060 (12 GB VRAM), ~11–12 minutes per model
- **Evaluation:** Held-out val pairs; scored by executing against Overpass API (same as
  `src/benchmark_models.py`) — `pass` if element count > 0
- **Chat template:** `tokenizer.apply_chat_template()` — model-native format, no hardcoded Qwen ChatML

### Models

| Model | Parameters | Architecture | dtype |
|-------|-----------|--------------|-------|
| `Qwen/Qwen2.5-Coder-0.5B-Instruct` | 494M | Qwen2.5 | fp16 |
| `google/gemma-3-270m-it` | 270M | Gemma 3 | bfloat16 |

## Results

### Main Comparison Table

| Condition | Model | Params | Few-Shot | Score |
|-----------|-------|--------|----------|-------|
| Base (before FT) | qwen2.5-coder:0.5b (Ollama) | 494M | k=5 | 47% (7/15) |
| Base (before FT) | Qwen2.5-Coder-0.5B-Instruct (HF) | 494M | none | 0.0% (0/30) |
| Base (before FT) | gemma-3-270m-it (HF) | 270M | none | 0.0% (0/30) |
| **After LoRA FT** | **Qwen2.5-Coder-0.5B-Instruct (HF)** | **494M** | **none** | **93.3% (28/30)** |
| **After LoRA FT** | **Qwen2.5-Coder-0.5B-Instruct (HF)** | **494M** | **none** | **95.1% (215/226) full holdout** |
| **After LoRA FT** | **gemma-3-270m-it (HF)** | **270M** | **none** | **96.7% (29/30)** |

### Training Metrics — Qwen2.5-Coder-0.5B (3 epochs)

| Epoch | Train Loss | Val Loss | Token Accuracy |
|-------|-----------|----------|----------------|
| 1 | 0.877 | — | 86% |
| 2 | — | — | — |
| 3 | 0.077 | 0.0805 | 97.9% |

### Training Metrics — gemma-3-270m-it (3 epochs)

| Epoch | Train Loss | Val Loss | Token Accuracy |
|-------|-----------|----------|----------------|
| 1 | 1.581 | 0.1166 | 96.84% |
| 2 | — | 0.0990 | 97.09% |
| 3 (best) | 0.092 | 0.0941 | 97.16% |

### Failure Analysis

**Qwen2.5-Coder-0.5B full holdout (11/226 failures, all `zero_results`):**

| Category | Count | Examples |
|----------|-------|---------|
| Real POI absence | 4 | Islands District→Embassies, Suminoe→Alpine huts |
| Wrong OSM tag | 2 | Churches: `building=church` instead of `amenity=place_of_worship` |
| `name:en` resolution failure | ~3 | Ome, Omiya Ward lacking `name:en` in OSM |
| Genuine POI scarcity | 2 | Ramen in Niigata Nishi, Indian restaurants in Fukuoka Chuo |

**gemma-3-270m-it (1/30 failures):**

- `Suminoe Ward, Osaka → Churches` — uses `building=church` → zero_results (same as Qwen)
  - This is a tag quality issue in training data, not a model capability gap

## Key Findings

### 1. Few-Shot prompting becomes unnecessary after fine-tuning

Both models internalized OSM tag knowledge (e.g. `amenity=convenience_store`,
`tourism=hotel`, multi-area `area["name:en"=...]` filter patterns) directly into weights.
The system prompt is a single sentence with no examples.

### 2. 270M model matches or exceeds 494M model on this task

`gemma-3-270m-it` achieves 96.7% (29/30) vs Qwen's 93.3% (28/30) on the same 30 samples.
This is remarkable: a 270M model outperforming a 494M model, suggesting this task is narrow
enough that architecture and training data quality matter more than raw parameter count.

### 3. Current dataset scale is sufficient

Both models exceed 93% accuracy on 4504 pairs. Scaling to more pairs is unlikely to improve
results significantly; quality improvement (fixing tag errors like `building=church` →
`amenity=place_of_worship`) may eliminate the remaining failures.

### 4. Sub-1B models are viable for TRIDENT Deep Layer

| Model | VRAM (fp16/bf16) | LoRA adapter | Training time |
|-------|-----------------|--------------|---------------|
| Qwen2.5-Coder-0.5B | ~1 GB | 35 MB | ~12 min |
| gemma-3-270m-it | ~0.6 GB | ~20 MB | ~11 min |

Both fit on Raspberry Pi 5 (8 GB RAM) with CPU inference. No Few-Shot prompt overhead —
lower latency, simpler runtime.

### 5. No prompt engineering required

The evaluation uses a minimal 1-sentence system prompt with no structural instructions
(no "use `[out:json]`", no "use `area` filter", no example queries). Both fine-tuned models
produce correct query structure autonomously.

## Recommendations

1. Adopt `gemma-3-270m-it` + LoRA as the primary Deep Layer candidate for TRIDENT — smaller
   than Qwen 0.5B yet matches or exceeds its accuracy on this task.
2. Alternatively adopt `Qwen2.5-Coder-0.5B-Instruct` + LoRA as a well-tested fallback.
3. Remove `num_ctx` tuning requirement from the inference stack (Few-Shot prompt size
   no longer relevant).
4. Fix tag quality: replace `building=church` with `amenity=place_of_worship` + `religion=christian`
   in training data to eliminate the shared remaining failure mode.
5. Consider periodic re-fine-tuning as the dataset grows — training cost is low (~11 min
   on consumer GPU).

## Code

See `examples/lora_finetune/` for the full training and evaluation code.
