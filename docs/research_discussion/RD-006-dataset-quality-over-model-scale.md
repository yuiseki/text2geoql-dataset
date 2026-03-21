# RD-006: Dataset Quality and Infrastructure Over Model Scale

**Date:** 2026-03-21
**Type:** Conclusion / Design principle
**Related:** RF-004, RD-001, RD-002, RD-003, RD-004, RD-005

## Summary

After evaluating three sub-500M models on a 226-sample full holdout, the performance
ceiling for this task is ~95% regardless of model size or architecture within this range.
All remaining failures are attributable to external factors — OSM data gaps, infrastructure
limitations, and training data quality — not model capacity. Scaling to 1B–2B models is
overkill for this task. The highest-leverage improvements are dataset quality and an
infrastructure-layer `name:en` fallback.

---

## The Saturation Finding

Full holdout results (226 samples, v2 church-fixed dataset):

| Model | Params | Score | Model errors |
|-------|--------|-------|-------------|
| Qwen2.5-Coder-0.5B-Instruct | 494M | 95.1% (215/226) | 1 |
| functiongemma-270m-it | 270M | 94.7% (214/226) | 0 |
| gemma-3-270m-it | 270M | 94.2% (213/226) | 2 |

The spread between best and worst is **2 samples out of 226**. All three models have
converged to effectively the same ceiling. The differences are within OSM database update
noise between evaluation sessions (Overpass API is deterministic; inter-session discrepancies
reflect live OSM data changes, not model behavior).

---

## Why Larger Models Will Not Help

Every failure in the full holdout can be attributed to one of four categories, none of
which are addressable by increasing model parameters:

### 1. Genuine POI absence (4 failures, all models)

The queried POI type does not exist in the area in reality:
- Islands District, Hong Kong → Embassies (rural island, no diplomatic offices)
- Higashi Ward, Nagoya → Alpine Huts
- Nishi Ward, Yokohama → Camp Sites

A 7B model would produce the same zero_results. The model's query is correct; the POI
simply does not exist.

### 2. `name:en` resolution gaps (3 failures, all models)

OSM areas for Ome (Tokyo), Omiya Ward (Saitama) lack `name:en` tags. The model correctly
generates `area["name:en"="Ome"]` per its training (RD-004), but OSM returns no match.
This is an infrastructure problem: a two-call fallback (`name:en` → `name`) at the
TRIDENT frontend layer would resolve these without any model changes.

### 3. Genuine POI scarcity (4 failures, all models)

The POI type exists in principle but is too sparse in the target area for OSM coverage:
- Ramen shops in Nishi Ward, Niigata
- Indian restaurants in Chuo Ward, Fukuoka
- Soba shops in Chuo, Kobe

These would return zero_results regardless of query quality, because mappers have not
tagged these establishments in OSM for these specific wards.

### 4. Training data sparsity on rare concern types (model-dependent)

A small number of failures reflect concern types with very few training pairs. These
produce model errors on the smallest models:

- gemma-3-270m: `Blacksmiths` → hallucinated tag `cuisine~"braised_black_pebbles"`
  (correct tag: `craft=blacksmith`); also reversed inner/outer area hierarchy
- gemma-3-270m: `Soba noodle shops, Kobe Chuo` → wrong area hierarchy (Hyogo Prefecture
  as outer instead of Kobe)
- Qwen2.5-Coder-0.5B: `Indian restaurants, Pingshan District, Shenzhen` → emitted
  `name:zh` (Chinese) instead of `name:en`

These are the only genuine model errors in the entire 226-sample evaluation. They appear
on rare or underrepresented concern types. **Removing or better covering these concern types
in the training dataset would eliminate them without increasing model size.**

---

## Model-Originated Errors Are a Dataset Signal, Not a Capacity Signal

The critical insight is the distinction between two types of failure:

**Capacity failure**: the model cannot learn the mapping because it is too small to
represent the pattern. Remedy: larger model.

**Coverage failure**: the model has not seen enough examples of a specific pattern.
Remedy: more or better training data for that pattern.

All observed model errors in this evaluation are coverage failures:
- `craft=blacksmith` is absent or near-absent from training data → model confabulates
- Chinese place names in training data are sparse → model slips to `name:zh`
- Soba noodle shops appear infrequently enough that area hierarchy generalizes poorly

A 1B or 2B model trained on the same dataset would likely produce the same errors on
the same rare inputs — because the signal is absent, not because the model is too small
to use it.

---

## gemma-3-270m as a Boundary Case

gemma-3-270m is notable as the only model with genuine structural reasoning errors
(hallucinated tags, inverted area hierarchy) on rare concern types. At 270M parameters
with a conservative base pre-training, it sits at the lower edge of reliable
generalization for this task.

functiongemma-270m, despite identical parameter count, shows zero model-originated
errors. Its function-calling specialization — training to produce structured, schema-bound
outputs — appears to confer robustness on structural generation even for sparse inputs.

This suggests that **architecture and specialization matter more than raw parameter count**
at this scale: a well-specialized 270M model (functiongemma) outperforms a general-purpose
270M model (gemma-3) on structural reliability, while a larger but similarly specialized
model (Qwen 494M) achieves marginally higher absolute accuracy.

---

## The Highest-Leverage Improvements

Ranked by expected impact per unit of effort:

### 1. Infrastructure: `name:en` two-call fallback (High impact, low effort)

3 failures across all models are caused by missing `name:en` tags in OSM. A frontend
fallback that retries with `name` when `name:en` returns zero_results would recover
these without any retraining. Expected improvement: +1.3 percentage points.

### 2. Dataset: remove unrealistic concern types (Medium impact, low effort)

Concern types like `Alpine Huts`, `Camp Sites`, `Blacksmiths`, `Embassies` are
legitimate OSM tags but are extremely rare or absent in dense urban wards. Including
them in training creates sparse coverage and degrades generalization on similar rare
inputs. Pruning `good_concerns.yaml` to remove urban-inappropriate concern types
improves training signal concentration.

### 3. Dataset: expand geographic coverage (Medium impact, medium effort)

Current failures include Chinese district names (Pingshan, Nanshan) where `name:en`
coverage is uneven. Expanding training pairs with verified Chinese/Korean/Southeast
Asian areas improves robustness on non-Japanese inputs.

### 4. Dataset: Wikibase tag grounding (High impact, medium effort)

As proposed in RD-005, grounding concern-to-tag mapping via the OSM Wikibase graph at
inference time or as a training data quality gate would eliminate tag errors (e.g.,
`name:zh` slip, `craft=blacksmith` hallucination) systematically. This addresses the
root cause of coverage failures without requiring more training pairs.

### 5. Model scale-up to 1B–2B (Low impact, high cost)

Not recommended at this stage. The task is saturated at sub-500M. The remaining failures
are not capacity-limited. Training a 1B model costs ~4–8× more compute and produces a
checkpoint that does not fit the Raspberry Pi 4B target (≤1.1B is the stated constraint,
but inference speed and VRAM usage scale unfavorably). The expected improvement is
negligible relative to the infrastructure and dataset improvements above.

---

## Conclusion

The performance ceiling for AreaWithConcern → OverpassQL translation is ~95% on the
current holdout set, achieved by all three sub-500M models. This ceiling is set by OSM
data quality and infrastructure gaps, not model capacity.

The engineering priorities going forward are:

1. **Implement `name:en` fallback** in the TRIDENT frontend
2. **Prune unrealistic concerns** from training data
3. **Expand geographic coverage** of training pairs
4. **Explore Wikibase grounding** (RD-005) as a systematic tag quality mechanism

Scaling to larger models is not a productive direction for this task at this time.
