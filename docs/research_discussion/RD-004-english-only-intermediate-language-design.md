# RD-004: English-Only Intermediate Language as an Intentional Design Decision

**Date:** 2026-03-21
**Type:** Design rationale
**Related:** RD-001, RD-003, RF-003, ADR-007

## Summary

TRIDENT intermediate language is intentionally English-only. This is a deliberate
architectural constraint, not a limitation. It serves two purposes simultaneously:
a practical heuristic for OSM data quality and a precision-maximizing constraint for
small language models.

---

## The Design Decision

All TRIDENT intermediate language entries use English exclusively:

```
AreaWithConcern: Shinjuku, Tokyo, Japan; Ramen shops    ← English, always
AreaWithConcern: 新宿, 東京, 日本; ラーメン店            ← this form is NOT used
```

The corresponding OverpassQL uses `name:en` for area lookups:

```overpassql
area["name:en"="Tokyo"]->.outer;
area["name:en"="Shinjuku"]->.inner;
```

---

## Why `name:en` Fails Sometimes (and How It Is Handled)

Not all OSM areas have `name:en` tags. Rural districts, smaller cities, and some
countries have inconsistent English name tagging in OSM data. This causes `zero_results`
not because the POI is absent, but because the area was not found.

The TRIDENT frontend handles this with a **two-call heuristic**:

```
1st call: area["name:en"="Ome"]  →  zero_results (no name:en tag in OSM)
2nd call: area["name"="Ome"]     →  success (Japanese name tag exists)
```

This is explicitly not pushed down to the model. The model always generates `name:en`.
The fallback is handled at the infrastructure layer, keeping the model's task simple.

---

## Why English-Only Is Precision-Maximizing for Small Models

### 1. Eliminates Cross-Lingual Variance

A model asked to handle multilingual input must learn:
- `新宿, 東京` → same area as `Shinjuku, Tokyo`
- `서울` → `Seoul`
- `大阪府大阪市住之江区` → `Suminoe Ward, Osaka, Osaka Prefecture, Japan`

This is non-trivial for a 270M–500M parameter model. English-only input removes this
entire class of variance. The model never needs to resolve transliterations, character
sets, or multilingual synonyms.

### 2. Aligns Input and Output Language

OSM tags are English by convention (`amenity=cafe`, not `amenity=カフェ`). By keeping
both input (TRIDENT intermediate) and output (OverpassQL tag values) in English, the
model operates in a single linguistic space. There is no language-switching overhead.

### 3. Reduces Model Vocabulary Pressure

A 270M model has limited embedding capacity. Requiring it to represent Japanese, Korean,
Chinese, and Arabic place names alongside English would dilute the representation quality
of each. English-only maximizes the signal per token for the actual task.

### 4. Consistent Training Signal

All 4504 training pairs use English intermediate language. The training distribution is
tightly concentrated in one linguistic space. This is another instance of the "low input
entropy" principle from RD-001 — the model can allocate all capacity to learning the
mapping, not the language.

---

## Implications for OSM Wiki CPT (RD-003)

This design decision directly informs how OSM Wiki CPT data should be prepared:

- **Prioritize English namespace** (`Tag:amenity=cafe`, not `JA:Tag:amenity=cafe`)
- **Multilingual pages add noise, not signal** — a model fine-tuned on English-only
  intermediate language does not benefit from Japanese descriptions of OSM tags
- **Exception**: country-specific tagging guides in English (e.g., `Japan tagging`,
  `Korea tagging`) are valuable — they document regional conventions that affect which
  tags appear in training data

---

## Implications for Dataset Expansion

When expanding geographic coverage:
- Input must always be in English even for non-English-speaking regions
- Place names must have English equivalents (or use Nominatim to resolve to OSM relation IDs,
  which bypasses the `name:en` issue entirely — see ADR-007)
- The two-call fallback at the infrastructure layer compensates for OSM data gaps

---

## Connection to the `name:en` Failure Pattern

Several failures in the full holdout evaluation (RF-004) were `zero_results` caused
by areas lacking `name:en` in OSM (e.g., `Ome, Tokyo`, `Omiya Ward, Saitama`). These
are not model errors — the model correctly generates `name:en` lookups per its training.
The fix is at the infrastructure layer (two-call fallback) or via Nominatim-grounded
area IDs (ADR-007), not at the model layer.

This distinction matters: attributing these failures to the model would lead to wrong
remediation (e.g., training the model to sometimes use `name` instead of `name:en`),
degrading the precision of the learned mapping.
