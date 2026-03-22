# RF-007: Guaranteed-Nonempty Strict Evaluation — Area Resolution Accuracy

**Date:** 2026-03-22
**Status:** Confirmed
**Related RF:** RF-005 (generalization), RF-006 (scoring policy)
**Models:** v3 LoRA adapters (pruned dataset, 4,217 pairs)

## Motivation

RF-006 established that all models achieve 100% syntactic correctness (zero_results
treated as pass). The next deeper question is: **does the model correctly resolve the
geographic scope of its Overpass QL?**

A model can generate syntactically valid Overpass QL with incorrect area filters
(wrong hierarchy, wrong name:en value, inner/outer inverted) — and still get zero_results
for an area that definitely contains the requested POI type.

This evaluation tests area resolution accuracy by using **guaranteed-nonempty pairs**:
test cases where we pre-verify (via a known-correct Overpass query) that the POI
category exists in the target area. Under strict scoring, zero_results = FAIL.

## Method

1. Curated 18 test inputs with pre-verification queries
2. Pre-ran each verification query against Overpass API to confirm element count > 0
3. 15/18 pairs confirmed (Sydney, Mumbai, Cairo dropped — OSM admin_level mismatch in
   verification queries, not a model issue)
4. Evaluated 3 v3 models on confirmed 15 pairs under strict scoring

Confirmed pairs (15): Paris×3, London×2, Berlin×2, Amsterdam, Rome, São Paulo,
Seoul, Gangnam-gu (Seoul), Shinjuku/Shibuya/Chiyoda (Tokyo control)

## Results

| Model | Total (15) | Seen (5) | Unseen (10) |
|-------|-----------|----------|-------------|
| Qwen2.5-Coder-0.5B | **80.0% (12/15)** | 5/5 | **7/10** |
| gemma-3-270m | 66.7% (10/15) | 5/5 | 5/10 |
| functiongemma-270m | 66.7% (10/15) | 5/5 | 5/10 |

All models scored 5/5 on seen regions (Tokyo, Seoul) — fine-tuning is fully intact.

### All-pass inputs (9/15)
Berlin (Cafes, Museums), London (Cafes, Museums), Seoul (Cafes),
Gangnam-gu Seoul (Restaurants), Shinjuku Tokyo (Convenience stores),
Shibuya Tokyo (Cafes), Chiyoda Tokyo (Hotels)

## Failure Analysis

### Failure class 1: Inner/outer hierarchy inversion on 3-level input

Training data format: `"Ward, City, Prefecture, Country"` (4 levels)
Paris input: `"Paris, Île-de-France, France"` (3 levels — city is terminal)

Expected mapping: outer = Île-de-France (region), inner = Paris (city)

| Model | Generated hierarchy | Error |
|-------|-------------------|-------|
| Qwen | `outer=Paris, inner=Île-de-France` | **Inverted** |
| gemma3 | `outer=Paris, inner=Île-de-France` | **Inverted** |
| functiongemma | `outer=Île-de-France, inner=Paris` | Correct! (but fails — see class 2) |

Qwen and gemma3 apply the training pattern incorrectly: in training data,
the second token from the right tends to be the outer area. For Paris, the
second token is "Île-de-France", but the model places Paris as outer instead.

functiongemma correctly identifies that the region (Île-de-France) should be
outer and the city (Paris) inner — but still fails due to failure class 2.

**Count: Paris 3 inputs × 2 models (Qwen, gemma3) = 6 failures**

### Failure class 2: `name:en` not registered in OSM

Even with correct hierarchy, `area["name:en"="Île-de-France"]` returns no match
because the Île-de-France region does not have `name:en` in OSM (only `name:fr`).

Affected:
- Paris (all 3 inputs): `name:en="Île-de-France"` not in OSM (functiongemma)
- Amsterdam: gemma3 generates `name:en="Amsterdam, Netherlands"` (concatenated) — no match

**Count: Paris 3 × functiongemma + Amsterdam × gemma3 = 4 failures**

### Failure class 3: Location+country concatenation bug

gemma3 and occasionally Qwen produce `name:en="Rome, Italy"` or
`name:en="Amsterdam, Netherlands"` — the model appends the country name to the
city name as if they form a single name:en value. No such compound string exists
in OSM.

Observed in:
- Rome: gemma3 → `inner="Rome, Italy"` → zero_results
- Amsterdam: gemma3 → `inner="Amsterdam, Netherlands"` → zero_results

**Count: 2 failures (Rome×gemma3, Amsterdam×gemma3)**

### Failure class 4: functiongemma hallucination — `cuisine~"food_for_people"`

functiongemma appends `["cuisine"~"food_for_people"]` as an extra filter on
restaurant queries for unseen regions (Rome, São Paulo). This tag does not exist
in OSM. The filter drastically reduces results to zero.

The hallucination appears specifically on "Restaurants" concern type for unseen
countries — functiongemma may have a training artifact that associates
`cuisine~"food_for_people"` with restaurant queries outside familiar regions.

**Count: 2 failures (Rome×functiongemma, São Paulo×functiongemma)**

## Summary of Failure Classes

| Class | Root cause | Affected models | Count |
|-------|-----------|----------------|-------|
| 1. Hierarchy inversion (3-level) | Training data only has 4-level inputs | Qwen, gemma3 | 6 |
| 2. `name:en` not in OSM | OSM coverage gap + no fallback | All | 4 |
| 3. City+country concatenation | Training artifact / hallucination | gemma3 | 2 |
| 4. `cuisine~"food_for_people"` hallucination | functiongemma training artifact | functiongemma | 2 |

## Key Findings

### 1. Qwen outperforms Gemma models on area resolution

Qwen correctly handles more 2-level and 3-level unseen inputs. Its larger parameter
count (494M vs 270M) contributes to better generalization of the area hierarchy pattern.

### 2. Seen regions are fully solved (5/5 all models)

The fine-tuning is complete and stable for the 4-level training format with seen countries.
The area resolution pattern for "Ward → City → Prefecture → Country" is perfectly learned.

### 3. Three distinct failure modes require three distinct fixes

| Fix | Targets |
|-----|---------|
| Add 3-level inputs (`City, Region, Country`) to training data | Class 1, 3 |
| Implement `name:en` → `name` fallback at query execution | Class 2 |
| Review functiongemma training data for restaurant tag patterns | Class 4 |

### 4. The guaranteed-nonempty evaluation is the correct next-level benchmark

It reveals failure modes invisible under syntactic-only scoring and provides
actionable signal for dataset and model improvements.

## Recommendations

1. **Add 2-level and 3-level geographic inputs** to training data:
   - `"City, Country"` (e.g., "Paris, France") → single-area or outer=Country, inner=City
   - `"City, Region, Country"` → outer=Region, inner=City

2. **Implement `name:en` → `name` fallback** in TRIDENT's Overpass query executor:
   retry with `["name"=...]` when `["name:en"=...]` returns zero results.

3. **Investigate functiongemma's `cuisine~"food_for_people"` hallucination**:
   search training data for this tag pattern and remove or correct it.

4. **Use `eval_guaranteed_nonempty.py`** as the standard deep evaluation for future
   model versions — it is a more meaningful benchmark than the standard holdout
   for measuring geographic scope accuracy.
