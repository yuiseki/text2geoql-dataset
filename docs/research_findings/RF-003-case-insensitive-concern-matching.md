# RF-003: Case-Insensitive Concern Matching Bug Fix

**Date:** 2026-03-20
**Status:** Fixed and deployed
**Related ADR:** ADR-003 (LLM Few-Shot)
**Fix commit:** (see git log)

## Summary

A case-sensitivity bug in Few-Shot example selection was causing "Convenience Stores" to find zero matching examples, resulting in systematically wrong queries for that concern. Fixed by extracting `example_matches()` as a pure function with case-insensitive concern comparison.

## Root Cause

In `load_examples_for_instruct()`, the concern filter was a substring match:

```python
# BEFORE (broken)
if filter_concern not in input_txt:
    continue
```

The eval instruction used `"Convenience Stores"` (uppercase S), while the dataset files used `"Convenience stores"` (lowercase s). The exact-case check missed all relevant examples.

## Impact

- `"Taito, Tokyo, Japan; Convenience Stores"` found **0 examples** → model had no guidance
- Model fell back to generic knowledge → generated `amenity=convenience_store` (wrong tag)
- Correct tag is `shop=convenience`

## Fix

Extracted a pure function `example_matches()` with case-insensitive concern matching:

```python
def example_matches(input_txt: str, filter_type: str, filter_concern: str) -> bool:
    if not input_txt.startswith(filter_type):
        return False
    if filter_concern.lower() not in input_txt.lower():  # case-insensitive
        return False
    return True
```

## Tests Added

`TestExampleMatches` class in `tests/test_generate_overpassql.py`:
- `test_exact_match`
- `test_case_insensitive_concern_uppercase_query`
- `test_case_insensitive_concern_lowercase_query`
- `test_unrelated_concern_not_matched`
- `test_wrong_filter_type_not_matched`

## Remaining Issue

Despite the fix, "Convenience Stores" still fails in benchmarks. Investigation shows:
1. The case fix now finds dataset examples with `shop=convenience`
2. But the area lookup `area["name"="Taito"]` returns 0 elements in some models' outputs
3. Correct lookup requires `area["name:en"="Taito"]` (English name tag)

See RF-004 for the area name tag investigation.
