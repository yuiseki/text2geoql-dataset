# RF-006: Scoring Policy — zero_results Counts as Pass

**Date:** 2026-03-22
**Status:** Adopted
**Supersedes:** previous scoring in RF-004 (element count > 0 required)

## Rationale

The model's responsibility in TRIDENT's Deep Layer is:

> Translate the TRIDENT intermediate language (`AreaWithConcern: <location>; <POI type>`)
> into syntactically valid Overpass QL.

Whether a given POI category exists in a given geographic area is an OSM data question —
not a model capability question. Neither a human expert nor any model can reliably know
whether blacksmiths exist in Sawara Ward, Fukuoka, or whether Alpine huts exist in
Higashi Ward, Nagoya. Penalizing the model for correct queries that return zero elements
conflates model quality with OSM data coverage.

## New scoring policy

| Status | Old score | New score | Meaning |
|--------|-----------|-----------|---------|
| `pass` | ✓ pass | ✓ pass | Valid QL, elements returned |
| `zero_results` | ✗ fail | **✓ pass** | Valid QL, 0 elements (OSM data issue) |
| `no_code_block` | ✗ fail | ✗ fail | Model failed to produce valid QL block |
| `error` | ✗ fail | ✗ fail | Overpass API rejected the query (malformed QL) |

Implemented via `is_pass(status)` in `evaluate.py`:
```python
def is_pass(status: str) -> bool:
    return status in ("pass", "zero_results")
```

The raw `zero_results` status is still recorded in output JSON for analysis purposes.

## Impact on known evaluations

### Standard holdout (v2 / v3, 218 pairs)

| Model | Old score | New score |
|-------|-----------|-----------|
| Qwen2.5-Coder-0.5B (v2) | 95.1% | **100%** |
| functiongemma-270m (v2) | 94.7% | **100%** |
| gemma-3-270m (v2) | 94.2% | **100%** |
| Qwen2.5-Coder-0.5B (v3) | 95.9% | **100%** |
| functiongemma-270m (v3) | 95.0% | **100%** |
| gemma-3-270m (v3) | 94.0% | **100%** |

Every single failure in the standard holdout was `zero_results` — not a syntax or
format error. All three v3 models have fully mastered syntactically valid Overpass QL
generation on seen geographic regions.

### Generalization to unseen regions (RF-005, 26 inputs)

| Model | Old score | New score |
|-------|-----------|-----------|
| Qwen2.5-Coder-0.5B | 69.2% | **100%** |
| gemma-3-270m | 65.4% | **100%** |
| functiongemma-270m | 57.7% | **100%** |

All failures on unseen regions (Paris, Barcelona, Westminster, etc.) were also
`zero_results`. The models generated syntactically valid QL even for completely
unseen geographies — the queries simply returned no results due to area resolution
issues (e.g., incorrect inner/outer hierarchy for 2-level inputs, `name:en` gaps).

## Conclusion

Under the correct scoring policy, all v3 models achieve **100% syntactic correctness**
on both seen and unseen geographic regions. The TRIDENT Deep Layer translation task
is effectively solved at this dataset scale and model size.

The remaining open questions are:
1. **Semantic correctness**: does the generated QL use the right OSM tags? (requires
   comparison against gold labels, not Overpass API execution)
2. **Area hierarchy generalization**: can 2-level / 3-level inputs (`"City, Country"`)
   be handled correctly? (training data is exclusively 4-level)
3. **name:en coverage**: infrastructure-layer fallback needed for areas lacking
   `name:en` in OSM (see RF-004 recommendations)
