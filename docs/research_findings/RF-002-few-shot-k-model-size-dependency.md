# RF-002: Few-Shot k (Number of Examples) Depends on Model Size

**Date:** 2026-03-20
**Status:** Confirmed
**Related ADR:** ADR-003 (LLM Few-Shot)

## Summary

Increasing the number of Few-Shot examples (`k`) from 4 to 6 improves large models but catastrophically degrades small models. There is a clear model-size dependency.

## Background

All models were plateauing at 80%. One hypothesis was that more examples would help the model generalize. We experimented with k=6 combined with the case-insensitive concern matching fix.

## Results

| Model | k=4 (default) | k=6 | Δ |
|-------|---------------|-----|---|
| qwen2.5-coder:3b | 80% | 40% ↓ | -40pp |
| qwen3:8b | 80% | 87% ↑ | +7pp |

## Failure Analysis for Small Models (k=6)

When qwen2.5-coder:3b received k=6 examples:
1. **Lost `area.inner` construct**: Stopped using the required inner area reference pattern
2. **Wrong tags**: Used `amenity=convenience_store` instead of `shop=convenience`
3. **Structural collapse**: Query syntax became malformed in some cases

The increased prompt length (k=6 vs k=4 adds ~2 more input/output example pairs) appears to push the 3B model beyond its effective attention span for instruction following, even though the raw prompt fits in the context window.

## Interpretation

- Large models (8B+): Can leverage additional examples, improving generalization
- Small models (≤3B): More examples confuse rather than guide; the model "copies" one of the examples poorly or loses track of the required output format

## Decision

Reverted to `k=4` (default) to keep small model performance intact.

## Future Work

- Consider **adaptive k**: use k=6 only for models ≥ 8B
- Consider **calibrated k**: benchmark k=3,4,5,6 for each target model size during fine-tuning dataset preparation
- When using `num_ctx=32768` for gemma3:12b (which reaches 100% at k=4), testing k=6 may be worthwhile since the model has proven it can handle the full prompt
