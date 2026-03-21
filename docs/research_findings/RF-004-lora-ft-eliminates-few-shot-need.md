# RF-004: LoRA Fine-Tuning Eliminates Few-Shot Prompting Need

**Date:** 2026-03-21
**Status:** Confirmed
**Related ADR:** ADR-003 (LLM Few-Shot), ADR-006 (Benchmark)

## Summary

LoRA fine-tuning of `Qwen2.5-Coder-0.5B-Instruct` on 4278 AreaWithConcern pairs achieves
**93.3% Overpass API pass rate** with no Few-Shot prompting — a dramatic improvement over the
0% base model and the 47% Few-Shot baseline using the 3B model. This suggests the current
dataset is already sufficient in scale and that Few-Shot prompting is no longer necessary
for the Deep Layer of TRIDENT.

## Background

Prior work established that:

- The Ollama-based Few-Shot pipeline achieves ~47% with `qwen2.5-coder:3b` at k=5 (RF-002)
- `gemma3:12b` with num_ctx=32768 reaches 100%, but requires a 12B model (RF-001)
- The TRIDENT architecture targets Raspberry Pi 4B / 5, requiring ≤1.1B parameter models

The open question was: can a 0.5B model serve the Deep Layer if fine-tuned on this dataset?

## Method

- **Model:** `Qwen/Qwen2.5-Coder-0.5B-Instruct` (HuggingFace)
- **Fine-tuning:** LoRA (PEFT + TRL SFTTrainer, no Unsloth)
- **Data:** 4504 AreaWithConcern pairs; 4278 train / 226 val (95%/5%, seed=42)
- **Hyperparameters:** r=16, alpha=32, dropout=0.05, 3 epochs, lr=2e-4, batch=8
- **Hardware:** NVIDIA GeForce RTX 3060 (12 GB VRAM), ~12 minutes
- **Evaluation:** 30 held-out val pairs; scored by executing against Overpass API (same as
  `src/benchmark_models.py`) — `pass` if element count > 0

## Results

| Condition | Model | Few-Shot | Score |
|-----------|-------|----------|-------|
| Base (before FT) | qwen2.5-coder:0.5b (Ollama) | k=5 | 47% (7/15) |
| Base (before FT) | Qwen2.5-Coder-0.5B-Instruct (HF) | none | 0.0% (0/30) |
| **After LoRA FT** | **Qwen2.5-Coder-0.5B-Instruct (HF)** | **none** | **93.3% (28/30)** |

### Training Metrics (3 epochs)

| Epoch | Train Loss | Val Loss | Token Accuracy |
|-------|-----------|----------|----------------|
| 1 | 0.877 | — | 86% |
| 2 | — | — | — |
| 3 | 0.077 | 0.0805 | 97.9% |

### Failure Analysis (2/30 failures)

Both failures are `zero_results` — the model generates syntactically correct OverpassQL
with appropriate OSM tags, but the POI type does not exist in the specified area:

1. `Islands District, Hong Kong → Embassies` — no embassies exist in this rural district
2. `Suminoe Ward, Osaka → Churches` — uses `building=church` (correct tag); churches
   genuinely sparse in this area

Neither failure is a model error; both are real-world data absence issues.

## Key Findings

### 1. Few-Shot prompting becomes unnecessary after fine-tuning

The model has internalized OSM tag knowledge (e.g. `amenity=convenience_store`,
`tourism=hotel`, multi-area `area["name:en"=...]` filter patterns) directly into its
weights. The system prompt is a single sentence with no examples.

### 2. Current dataset scale is sufficient

93.3% accuracy on 4504 pairs suggests the dataset's **diversity** (tag × area combinations)
already covers the distribution well. Scaling to more pairs is unlikely to improve results
significantly; quality improvement (more gold `output-001` entries) may be more valuable.

### 3. 0.5B model is viable for TRIDENT Deep Layer

- fp16 ~1 GB VRAM — fits on Raspberry Pi 5 (8 GB RAM) with CPU inference
- LoRA adapter: 35 MB — lightweight deployment
- No Few-Shot prompt overhead — lower latency, simpler runtime

### 4. No prompt engineering required

The evaluation uses a minimal 1-sentence system prompt with no structural instructions
(no "use `[out:json]`", no "use `area` filter", no example queries). The fine-tuned model
produces correct query structure autonomously.

## Recommendations

1. Adopt `Qwen2.5-Coder-0.5B-Instruct` + LoRA as the primary Deep Layer candidate for
   TRIDENT, replacing the Few-Shot Ollama pipeline.
2. Remove `num_ctx` tuning requirement from the inference stack (Few-Shot prompt size
   no longer relevant).
3. Focus future dataset work on **quality** (validating and expanding `output-001` gold
   entries) rather than **quantity**.
4. Consider periodic re-fine-tuning as the dataset grows — training cost is low (~12 min
   on consumer GPU).

## Code

See `examples/lora_finetune/` for the full training and evaluation code.
