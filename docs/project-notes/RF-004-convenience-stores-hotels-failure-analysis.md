# RF-004: Convenience Stores and Hotels Failure Analysis

**Date:** 2026-03-20
**Status:** Root cause identified; partially resolved
**Related ADR:** ADR-003 (Few-Shot), ADR-008 (Taginfo), ADR-009 (Semantic Grouping)

## Summary

"Convenience Stores" and "Hotels" persistently fail across models because:
1. OSM tag namespaces are counter-intuitive (`shop=convenience`, `tourism=hotel`) versus model intuition (`amenity=convenience`, `amenity=hotel`)
2. Without sufficient context window, Few-Shot examples showing correct tags are truncated
3. With case-insensitive matching fix (RF-003) + `--num-ctx 32768`, gemma3:12b achieves 100% including these concerns

## Failure Timeline for gemma3:12b

### Before case-insensitive fix (run T121556):

```
Convenience Stores:
  area["name"="Taito"]->.searchArea;    ← area not found (no :en)
  nwr["shop"="convenience"]             ← tag is CORRECT
  → zero_results

Hotels:
  area["name"="Shinjuku"]->.searchArea; ← area not found (no :en)
  nwr["tourism"="hotel"]                ← tag is CORRECT
  → zero_results
```

Root cause here was **area name tag** (`name` vs `name:en`).

### After case-insensitive fix, without --num-ctx 32768 (run T123707):

```
Convenience Stores:
  area["name:en"="Taito"]->.inner;      ← area lookup CORRECT
  nwr["amenity"="convenience"]          ← tag is WRONG (should be shop=convenience)
  → zero_results

Hotels:
  area["name:en"="Shinjuku"]->.inner;   ← area lookup CORRECT
  nwr["amenity"="hotel"]                ← tag is WRONG (should be tourism=hotel)
  → zero_results
```

Root cause shifted to **wrong tag namespace**. The model fell back to `amenity=*` because:
- Few-Shot examples with correct tags were truncated (default ~2048 ctx)
- Model relied on intuitive OSM knowledge: "hotels and stores are amenities"

### After case-insensitive fix + --num-ctx 32768 (run T122929):

```
All 15 trials: OK  → 100% success rate
```

With full context, the correct Few-Shot examples show `shop=convenience` and `tourism=hotel`.

## Tag Namespace Mismatch (OSM Design Reality)

These concepts reveal a fundamental OSM tagging pattern that confounds LLMs:

| Human Concept | Intuitive Tag | Correct OSM Tag |
|---------------|---------------|-----------------|
| Convenience Store | `amenity=convenience_store` | `shop=convenience` |
| Hotel | `amenity=hotel` | `tourism=hotel` |
| Museum | `amenity=museum` | `tourism=museum` |
| Hospital | `amenity=hospital` ✓ | `amenity=hospital` (this one is correct) |

This is the "Semantic Grouping Problem" (ADR-009): the `amenity` key is overloaded in common perception but OSM has a strict taxonomy.

## Models Affected

| Model | Without fix | After case-fix | After case-fix + num_ctx |
|-------|-------------|----------------|--------------------------|
| gemma3:12b | 73% (area name wrong) | 73% (tag namespace wrong) | **100%** |
| qwen3:8b | 80% (passes on 4/5) | ~80% | not tested |
| qwen2.5-coder:3b | 80% (passes on 4/5) | ~80% | not tested |

Both qwen3:8b and qwen2.5-coder:3b pass 4/5 eval instructions (missing one of the two failing concerns) — the exact failure varies by trial.

## Proposed Solutions

### Short-term (already implemented)
1. ✅ Case-insensitive concern matching (RF-003)
2. ✅ `--num-ctx` parameter for larger context window (RF-001)

### Medium-term
3. **Tag hint injection**: Add a note to the PROMPT_PREFIX explaining that `shop=*` is for shops, `tourism=*` for tourism, `amenity=*` for amenities
4. **Taginfo validation at query time**: Verify generated tag exists in OSM before accepting
5. **Additional Few-Shot examples for confusing concerns**: Ensure "Hotels" and "Convenience Stores" appear in the top-k selected examples

### Long-term
6. **Nominatim grounding**: Resolve area names to OSM relation IDs to avoid `name` vs `name:en` ambiguity entirely

## Impact on Dataset Quality

The dataset itself contains correct queries (verified via Overpass API). The issue is purely at inference time when models lack sufficient Few-Shot guidance. Once fine-tuned on this dataset, the model should internalize the correct tag namespaces.
