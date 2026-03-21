# Research Findings

This directory contains findings from benchmark experiments that are broadly applicable to Few-Shot LLM prompting and Overpass QL generation — insights worth sharing with the wider LLM/NLP research community.

Project-specific bug fixes and dataset-specific investigations are tracked separately in [`docs/project-notes/`](../project-notes/).

## Index

| ID | Title | Status | Date |
|----|-------|--------|------|
| [RF-001](RF-001-num-ctx-context-window-effect.md) | num_ctx (Context Window Size) Effect on Few-Shot Quality | Confirmed | 2026-03-20 |
| [RF-002](RF-002-few-shot-k-model-size-dependency.md) | Few-Shot k (Number of Examples) Depends on Model Size | Confirmed | 2026-03-20 |
| [RF-003](RF-003-administrative-hierarchy-enables-nominatim-disambiguation.md) | Pre-encoded Administrative Hierarchy Enables Nominatim to Solve LLM-Hard Toponym Disambiguation | Confirmed | 2026-03-21 |

## Key Takeaways

1. **Context window size (`num_ctx`) is a critical inference-time hyperparameter for Few-Shot quality** — models with truncated prompts fail to learn correct output patterns even if the dataset is correct. Each model family has a sweet spot (e.g., gemma3:12b → 32768, gpt-oss:20b → 128000).
2. **Optimal k (number of Few-Shot examples) depends on model size** — larger examples budgets help large models but hurt small ones, with a clear breakpoint around 7–8B parameters.
3. **Structured administrative hierarchy in the dataset design solves toponym disambiguation that LLMs fail at** — encoding the full administrative hierarchy (ward, city, prefecture, country) in the TRIDENT intermediate language enables Nominatim to uniquely resolve same-name areas (e.g., Hiroshima Prefecture vs Hiroshima City) via OSM area IDs, without requiring the LLM to possess or infer this knowledge. This problem is reportedly unsolved even by GPT-5.1 on free-text input.
