# RF-005: Generalization to Unseen Geographic Regions

**Date:** 2026-03-22
**Status:** Confirmed
**Related RF:** RF-004 (LoRA FT)
**Models:** v3 LoRA adapters (pruned dataset, 4,217 pairs)

## Summary

LoRA fine-tuned sub-1B models generalize **tag knowledge** correctly to completely unseen
geographic regions (Europe, Oceania, South Asia, Middle East, Latin America), achieving
**55–67% pass rate** on 24 unseen-region inputs. The remaining failures are almost entirely
attributable to **input hierarchy mismatch** (training data uses 4-level structure; test
inputs have 2–3 levels) and **OSM `name:en` registration gaps**, not to tag knowledge failure.

## Setup

### Training data coverage
All training pairs use locations from:
- Japan, China, South Korea, Kosovo, United States only

### Test set (26 inputs)
- 24 unseen-region inputs: Paris, London, Berlin, Rome, Amsterdam, Barcelona, Sydney,
  Melbourne, Mumbai, Delhi, Cairo, Dubai, São Paulo, Buenos Aires, Westminster (London),
  Mitte (Berlin), Île-de-France
- 2 control inputs: Shibuya/Shinjuku (Tokyo, Japan) — seen region

## Results

| Model | Total (26) | Unseen (24) | Control Tokyo (2) |
|-------|-----------|-------------|-------------------|
| Qwen2.5-Coder-0.5B | 69.2% (18/26) | **66.7% (16/24)** | 2/2 |
| gemma-3-270m | 65.4% (17/26) | **62.5% (15/24)** | 2/2 |
| functiongemma-270m | 57.7% (15/26) | **54.2% (13/24)** | 2/2 |

All models scored 2/2 on the Tokyo control — confirming fine-tuned behavior is intact.

### All-pass inputs (13/26 — all 3 models pass)

| Input | Region |
|-------|--------|
| London → Cafes, Museums, Parks | Europe |
| Berlin → Cafes, Museums | Europe |
| Rome → Museums | Europe |
| Sydney → Cafes, Parks | Oceania |
| Mumbai → Hotels | South Asia |
| Delhi → Hospitals | South Asia |
| Buenos Aires → Cafes | Latin America |
| Shibuya/Shinjuku → Cafes, Convenience stores | Control |

## Failure Analysis

### 1. Paris — all models fail on all Paris inputs (4 inputs × 3 models)

Paris inputs use 2-level structure: `"Paris, France"`. Training data is exclusively
4-level: `"Ward, City, Prefecture, Country"`. Models apply incorrect patterns:

| Model | Pattern | Problem |
|-------|---------|---------|
| Qwen | `area["name:en"="Paris"]->.searchArea` | Single-area pattern (not in training format) |
| gemma3 | `outer=Paris, inner=Paris` | Outer = Inner (redundant/broken) |
| functiongemma | `outer=Paris, inner=France` | Inner/outer inverted |

**Root cause**: The model has never seen 2-level `"City, Country"` inputs and cannot
correctly map them to a single-area or proper outer/inner pattern.

### 2. name:en resolution failures (OSM data issue, not model error)

Westminster and Mitte queries show **structurally correct** Overpass QL:
```overpassql
area["name:en"="London"]->.outer;
area["name:en"="Westminster"]->.inner;
```
The queries fail at runtime because OSM does not register `name:en="Westminster"` or
`name:en="Mitte"` on the relevant administrative boundary polygons. This is the same
`name:en` gap documented in RF-004 (Ome, Omiya Ward), not a model error.

### 3. Inner/outer hierarchy inversion for 2-level city inputs

Barcelona (`"Barcelona, Catalonia, Spain"`), Dubai (`"Dubai, UAE"`), Melbourne
(`"Melbourne, Victoria, Australia"`) — gemma3/functiongemma tend to place the
lower-level area as outer and the higher-level as inner, reversing the expected hierarchy.

Qwen handles these better (higher pass rate on 2-level inputs).

### 4. Tag knowledge generalizes correctly

Successful tag mappings on unseen regions:

| Concern | Tag used | Regions passed |
|---------|----------|----------------|
| Cafes | `amenity=cafe` | Berlin, London, Sydney, Buenos Aires, Amsterdam (Qwen/func) |
| Museums | `tourism=museum` | Berlin, London, Rome |
| Parks | `leisure=park` | London, Sydney |
| Hotels | `tourism=hotel` | Dubai (Qwen, gemma3), Mumbai |
| Hospitals | `amenity=hospital` | Delhi |
| Mosques | `amenity=place_of_worship` + `religion=islam` | Cairo (gemma3, functiongemma) |
| Restaurants | `amenity=restaurant` | Rome (Qwen), São Paulo (Qwen, gemma3), Melbourne (Qwen, gemma3) |

**Qwen note**: Cairo Mosques → `building~"mosque"` (hallucination). gemma3/functiongemma
correctly generate `amenity=place_of_worship` with `religion=islam`.

## Key Findings

### 1. Tag knowledge generalizes globally

OSM tag mappings (amenity=cafe, tourism=museum, etc.) transfer correctly to unseen
countries and continents. The model internalized OSM's language-neutral tag schema, not
just region-specific patterns.

### 2. Input hierarchy is the primary failure mode

Training data exclusively uses 4-level administrative hierarchy. Inputs with fewer
levels (2: `"City, Country"` or 3: `"District, City, Country"`) confuse the models.
This is a **dataset design limitation**, not a model capacity issue.

### 3. Qwen outperforms smaller Gemma models on unseen regions

| Model | Params | Unseen pass rate |
|-------|--------|-----------------|
| Qwen2.5-Coder-0.5B | 494M | **66.7%** |
| gemma-3-270m | 270M | 62.5% |
| functiongemma-270m | 270M | 54.2% |

Qwen's larger capacity (494M vs 270M) provides better generalization on out-of-distribution
inputs. The gap that was invisible on the in-distribution holdout (all ~95%) becomes
apparent on unseen regions.

### 4. name:en remains a systemic infrastructure gap

Westminster, Mitte, and other sub-city districts fail due to OSM `name:en` absence —
the same issue affecting Ome and Omiya Ward in RF-004. A `name:en` → `name` two-call
fallback at inference time would recover these cases.

## Recommendations

1. **Add 2-level and 3-level hierarchy inputs to training data** (e.g., `"City, Country"`,
   `"District, City, Country"`). This would address the Paris/Barcelona failure class.

2. **Implement `name:en` → `name` fallback** at inference time to recover sub-city
   districts where `name:en` is unregistered in OSM.

3. **Qwen2.5-Coder-0.5B is the preferred model** for production deployment where unseen
   geographic regions are expected — its larger capacity provides better generalization.

4. **Extend training geography** beyond 5 countries (Japan/China/Korea/Kosovo/US) to
   include European, South American, and Oceanian cities. This would improve both
   in-distribution accuracy and generalization.
