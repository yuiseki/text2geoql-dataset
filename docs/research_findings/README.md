# Research Findings

This directory contains findings from benchmark experiments that are broadly applicable to Few-Shot LLM prompting, LoRA fine-tuning, and Overpass QL generation — insights worth sharing with the wider LLM/NLP research community.

Project-specific bug fixes and dataset-specific investigations are tracked separately in [`docs/project-notes/`](../project-notes/).

## Index

| ID | Title | Status | Date |
|----|-------|--------|------|
| [RF-001](RF-001-num-ctx-context-window-effect.md) | `num_ctx` is a critical inference-time hyperparameter for Few-Shot quality | Confirmed | 2026-03-20 |
| [RF-002](RF-002-few-shot-k-model-size-dependency.md) | Optimal Few-Shot k depends on model size — larger k hurts small models | Confirmed | 2026-03-20 |
| [RF-003](RF-003-administrative-hierarchy-enables-nominatim-disambiguation.md) | Administrative hierarchy enables Nominatim toponym disambiguation | Confirmed | 2026-03-21 |
| [RF-004](RF-004-lora-ft-eliminates-few-shot-need.md) | LoRA fine-tuning of sub-1B models eliminates Few-Shot need | Confirmed | 2026-03-21 |
| [RF-005](RF-005-generalization-unseen-cities.md) | Unseen city generalization: tag knowledge transfers, area hierarchy does not | Confirmed | 2026-03-22 |
| [RF-006](RF-006-zero-results-scoring-policy.md) | Scoring policy: `zero_results=pass` reveals all failures are OSM coverage, not syntax | Confirmed | 2026-03-22 |
| [RF-007](RF-007-guaranteed-nonempty-eval.md) | Guaranteed-nonempty strict eval identifies 4 failure classes | Confirmed | 2026-03-22 |
| [RF-008](RF-008-two-call-name-fallback.md) | Two-call `name:en` → `name` fallback: +20% at zero model cost; OSM tagging conventions | Confirmed | 2026-03-22 |
| [RF-009](RF-009-v4-multilevel-augmentation.md) | v4 dataset augmentation: 92.0% → 100.0% via multi-level training pairs + system prompt | Confirmed | 2026-03-22 |

## Key Takeaways

1. **Context window size (`num_ctx`) is a critical inference-time hyperparameter for Few-Shot quality** — models with truncated prompts fail to learn correct output patterns even if the dataset is correct. Each model family has a sweet spot (e.g., gemma3:12b → 32768, gpt-oss:20b → 128000). (→ RF-001)

2. **Optimal k (number of Few-Shot examples) depends on model size** — larger example budgets help large models but hurt small ones, with a clear breakpoint around 7–8B parameters. (→ RF-002)

3. **Structured administrative hierarchy in the dataset design solves toponym disambiguation that LLMs fail at** — encoding the full administrative hierarchy (ward, city, prefecture, country) in the TRIDENT intermediate language enables Nominatim to uniquely resolve same-name areas (e.g., Hiroshima Prefecture vs Hiroshima City) via OSM area IDs, without requiring the LLM to possess or infer this knowledge. (→ RF-003)

4. **LoRA fine-tuning of a 0.5B model eliminates the need for Few-Shot prompting entirely** — base model scores 0%, fine-tuned adapter scores 100% on the eval set. The narrow task is fully learnable at sub-1B scale. (→ RF-004)

5. **Tag knowledge generalizes to unseen cities; area hierarchy does not** — a fine-tuned model correctly maps "Cafes" → `amenity=cafe` for any city, but generates wrong area filter structure for cities absent from training data. Multi-level training data (RF-009) fixes this. (→ RF-005)

6. **`zero_results=pass` scoring policy is appropriate for this task** — all failures under strict scoring are OSM data coverage gaps, not model errors. The model never produces syntactically invalid queries. (→ RF-006)

7. **A held-out guaranteed-nonempty eval set is essential for measuring real model quality** — standard holdout sets include impossible queries (POI doesn't exist in area), masking true failure modes. (→ RF-007)

8. **Two-call `name:en` → `name` fallback recovers +20% coverage at zero model cost** — OSM omits `name:en` when identical to `name` (Pattern A) or when accent differs (Pattern B). A mechanical retry with `["name"=...]` resolves both. (→ RF-008)

9. **Multi-level training data (2-level City/Country, 3-level City/Region/Country) fixes hierarchy inversion and city confusion bugs** — dataset augmentation from 4,217 → ~4,900 pairs pushed accuracy from 92.0% to 100.0% on the guaranteed-nonempty eval set. System prompt clarification of the TRIDENT area ordering rule also contributed. (→ RF-009)
