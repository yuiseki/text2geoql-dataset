# RD-007: Domain-specific CPT is Not Efficient for Small Models on Narrow Tasks

**Date**: 2026-03-22
**Related experiments**: EXP-001, EXP-002a/b/c/d in text2geoql-d-cpt-poc
**Conclusion**: CPT does not improve ROI for sub-500M models on highly structured, narrow tasks

## Summary

We conducted a systematic empirical study of Domain-specific Continual Pre-Training (D-CPT)
using OSM Wiki knowledge as a CPT corpus, followed by task-specific LoRA fine-tuning.
The conclusion is that **CPT consumes disproportionate time and compute relative to the
gains obtained**, and is not recommended for this task/model combination.

## Experimental Results

| Experiment | CPT corpus | CPT method | FT epochs/lr | Score | Time cost |
|---|---|---|---|---|---|
| Baseline A | — | — | 3ep / 2e-4 | **94.2%** (213/226) | ~11min |
| EXP-001 | Wikibase 81k tok | full-weight, 57 steps | 3ep / 2e-4 | 93.4% (211/226) | 1min + 11min |
| EXP-002a | dump 2.3M tok | full-weight, 816 steps | 3ep / 2e-4 | **0.4%** (1/226) | 33min + 11min |
| EXP-002b | dump 2.3M tok | LoRA, 816 steps | 3ep / 2e-4 | 41.2% (93/226) | 31min + 11min |
| EXP-002c | dump 2.3M tok | LoRA, 816 steps | 6ep / 3e-4 | 61.5% (139/226) | 31min + 21min |
| EXP-002d | dump 2.3M tok | LoRA, 816 steps | **9ep / 5e-4** | 87.2% (197/226) | 31min + 31min |

All experiments on gemma-3-270m-it, RTX 3060 (12GB).

## Key Findings

### 1. Full-weight CPT at scale destroys IT capabilities

EXP-002a: 816 steps of full-weight CLM training on 2.3M tokens overwrote the instruction-tuned
model's formatting behavior. Despite task FT showing normal eval_loss (0.098), the model
produced 221/226 `no_code_block` failures — correct query content, wrong output format.

EXP-001 (57 steps) was safe; EXP-002a (816 steps) was not. The threshold is somewhere between
57 and 816 full-weight steps for gemma-3-270m-it.

**Implication**: Full-weight CPT on IT models requires careful step-count management.
LoRA CPT is safer.

### 2. LoRA CPT preserves code formatting but introduces query pattern contamination

EXP-002b: LoRA CPT recovered code block generation (4/226 failures vs 221/226 in EXP-002a),
but the dump corpus contains diverse Overpass query examples in non-standard formats.
The model learned these patterns (`->.searchArea` single-area queries) which contaminated
the task FT, causing 93/129 failures from incorrect area hierarchy.

**Root cause**: The OSM Wiki dump Tag:/Key: pages frequently include Overpass QL examples
as documentation. CPT on raw wikitext ingests these patterns.

### 3. Stronger task FT progressively overrides CPT contamination — but at high cost

| FT strength | Score | Δ from baseline |
|---|---|---|
| 3ep / 2e-4 | 41.2% | -53% |
| 6ep / 3e-4 | 61.5% | -33% |
| 9ep / 5e-4 | 87.2% | -7% |

The CPT-introduced patterns can be overridden by increasing FT epochs and learning rate,
but each step multiplies training time linearly. To recover within 7% of baseline requires
3× the FT epochs and 2.5× the learning rate — all without exceeding baseline performance.

### 4. EXP-001 (Wikibase-only CPT) fixed model-originated errors — but barely

EXP-001's full-weight CPT at 57 steps (81k token corpus) fixed both baseline model errors:
- `craft=blacksmith` hallucination → eliminated
- Inner/outer area hierarchy inversion → eliminated

But the overall score (93.4% vs 94.2% baseline) showed no net improvement, partly because
the holdout set changed (pruning removed 4 pairs) and a new model error appeared (Factories:
`leisure~"factory"`). The signal is too weak to draw conclusions from EXP-001 alone.

## Why CPT Is Not Efficient Here

### The task is highly structural, not factual

The primary failure modes in the baseline are:
- **OSM data absence** (genuine zero_results) — CPT cannot fix this
- **Sparse training data coverage** — CPT cannot fix this
- **Tag name hallucination** (rare) — CPT might help, but rare enough to not matter

CPT excels at injecting *factual knowledge* (e.g., "craft=blacksmith is a valid tag").
But for this task, ~94% accuracy is already achieved by LoRA FT alone. The remaining 6%
failures are almost entirely external (OSM DB state, data coverage) — not model knowledge gaps.

### The model is too small to benefit from CPT at scale

At 270M parameters with a 2.3M token CPT corpus:
- CPT loss (3.4 train / 3.3 eval) is much higher than EXP-001 (2.8/2.1) — the model
  cannot absorb the full corpus effectively
- The ratio of CPT data to model capacity is large → pattern contamination dominates
- Larger models (≥1B) would have more capacity to separate CPT knowledge from task patterns

### Total time investment vs. gain

| Approach | Time | Final score |
|---|---|---|
| Baseline LoRA FT only | ~11 min | 94.2% |
| EXP-001 (CPT + FT) | ~12 min | 93.4% |
| EXP-002d (CPT + strong FT) | ~62 min | 87.2% |

Even the best CPT experiment (EXP-001) did not exceed baseline.
The dump-based CPT required 6× the time to reach 87.2% — still below baseline.

## Recommendations

1. **Do not use CPT for gemma-3-270m-it on this task.** The dataset quality and coverage
   improvements (RD-006) yield better ROI.

2. **If CPT is attempted in future work** (e.g., with ≥1B parameter models or a larger
   task-FT dataset), use LoRA CPT with filtered corpus (remove pages containing Overpass
   QL examples) and verify that task FT can still converge normally at 3 epochs.

3. **The Wikibase tool-call grounding approach** (RD-005) is a more promising direction
   for injecting OSM tag knowledge at inference time without training cost.

4. **Dataset improvements** remain the highest-ROI path: name:en two-call fallback,
   concern pruning, geographic expansion (RD-006).
