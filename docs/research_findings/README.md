# Research Findings

This directory contains focused research finding documents from benchmark experiments and investigations.

Each RF document captures a specific discovery with enough detail to inform future design decisions and fine-tuning strategies.

## Index

| ID | Title | Status | Date |
|----|-------|--------|------|
| [RF-001](RF-001-num-ctx-context-window-effect.md) | num_ctx (Context Window Size) Effect on Few-Shot Quality | Confirmed | 2026-03-20 |
| [RF-002](RF-002-few-shot-k-model-size-dependency.md) | Few-Shot k (Number of Examples) Depends on Model Size | Confirmed | 2026-03-20 |
| [RF-003](RF-003-case-insensitive-concern-matching.md) | Case-Insensitive Concern Matching Bug Fix | Fixed | 2026-03-20 |
| [RF-004](RF-004-convenience-stores-hotels-failure-analysis.md) | Convenience Stores and Hotels Failure Analysis | Root cause identified | 2026-03-20 |

## Key Takeaways

1. **gemma3:12b + `--num-ctx 32768`** → 100% success rate (new best)
2. **k=6** only helps models ≥ 8B; degrades ≤ 3B models
3. **Case-insensitive matching** is required for concern names with variant capitalization
4. **Tag namespace mismatch** (`shop=*`, `tourism=*` vs intuitive `amenity=*`) is a persistent failure mode when Few-Shot context is truncated
