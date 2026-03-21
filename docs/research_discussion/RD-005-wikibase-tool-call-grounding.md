# RD-005: Wikibase Tool-Call Grounding as Alternative to CPT

**Date:** 2026-03-21
**Type:** Architectural proposal
**Related:** RD-003, RD-004, RF-004

## Summary

Instead of injecting OSM tag knowledge into model weights via Continued Pre-Training (CPT),
a fundamentally different approach is possible: use the OSM Wikibase instance as an
**external tool call** at inference time to deterministically ground natural language POI
concepts to correct OSM tags. This preserves tag knowledge outside the model, keeps it
always up-to-date, and avoids the complexity of CPT entirely.

---

## Background: The Knowledge Injection Problem

The remaining failure modes in the current LoRA-FT pipeline all trace back to the same root
cause: the model learns OSM tag mappings from training data, but training data contains
errors (e.g., `building=church` instead of `amenity=place_of_worship`) and cannot cover
every possible POI type exhaustively.

Two approaches exist to solve this:

**A. Bake knowledge into weights (CPT)** — Train the model on OSM Wiki text before task FT,
so it "knows" tag semantics from pre-training. Described in RD-003.

**B. Keep knowledge external (tool call)** — At inference time, look up the correct OSM
tags dynamically from an authoritative source. Described in this document.

---

## The Wikibase Tool-Call Architecture

### What Wikibase Provides

The OSM Wikibase instance (`wikibase-rdf.ttl.gz`, or the live API at
`https://wiki.openstreetmap.org/wiki/Special:ApiSandbox`) is a complete semantic graph of
OSM tag knowledge:

- Every tag has a structured entry with: key, value, status, description
- Deprecation chains: `amenity=church → use_instead → amenity=place_of_worship + religion=christian`
- Implication chains: `amenity=cafe → implies → amenity=yes`
- See-also / combination tags
- Status values: `approved`, `de facto`, `in use`, `deprecated`, `obsolete`

This is a **deterministic, authoritative, always-current** knowledge base. Unlike a
fine-tuned model's weights, it can be updated without retraining.

### Proposed Inference Pipeline

```
User NL Query
      │
      ▼
[Concern Extraction]          ← fast (regex or small model)
"place of worship" / "church"
      │
      ▼
[Wikibase Tag Lookup]         ← tool call: search by description/label
  Input: "place of worship"
  Output: amenity=place_of_worship (status: approved)
          religion=christian (for Christian churches)
          amenity=church (status: deprecated → use amenity=place_of_worship)
      │
      ▼
[OverpassQL Generator]        ← fine-tuned small model
  Input: AreaWithConcern + resolved OSM tags
  Output: valid OverpassQL
```

The fine-tuned model no longer needs to know which tags are correct — it receives the
resolved tags as part of its input. Its job is reduced to: **given these tags and this area,
produce valid OverpassQL syntax**.

---

## Comparison: CPT vs Tool-Call Grounding

| Dimension | CPT (RD-003) | Tool-Call Grounding |
|-----------|-------------|---------------------|
| Tag knowledge source | Model weights (baked in) | External Wikibase (live) |
| Up-to-date when OSM tagging evolves | Requires retraining | Automatic |
| Handles edge cases not in training data | Partial (limited by CPT corpus) | Complete (full Wikibase graph) |
| Inference latency | Same as current | +1 API call (~50–200ms) |
| Model complexity | Unchanged (small model fine-tuned) | Model task simplified further |
| Infrastructure complexity | CPT pipeline (GPU time, new checkpoint) | Wikibase client (lightweight) |
| Failure mode | Model hallucination of wrong tag | API timeout / Wikibase outage |
| Offline operation | Full | Requires either local mirror or self-hosted Wikibase |

---

## Why This Is Architecturally Sound

### 1. Clean Separation of Concerns

The model's task becomes even narrower: map `AreaWithConcern + resolved_tags → OverpassQL`.
This is a purer syntactic mapping problem. Tag semantics are fully delegated to Wikibase.

The docility vs intelligence principle (RD-002) suggests that narrower tasks fine-tune
better. Removing tag knowledge from the model's responsibility may actually improve accuracy.

### 2. Deterministic Grounding Eliminates a Class of Errors

When the model generates `building=church` today, it is making a semantic error —
conflating the physical structure tag with the institution tag. With tool-call grounding,
the Wikibase lookup would return:

```
building=church: status=in use, description="a building used as a church"
amenity=church: status=deprecated, use_instead=amenity=place_of_worship
```

The model receives pre-grounded tags. The semantic error becomes impossible.

### 3. Self-Hosting Is Feasible

`wikibase-rdf.ttl.gz` (10 MB compressed) can be loaded into a local RDF store (e.g., Apache
Jena, Oxigraph) or indexed into a simple SQLite/JSON lookup table for offline use.
The `build_osm_wiki_corpus.py` script already demonstrates that the full graph is parseable.

A lightweight local Wikibase proxy could serve the TRIDENT stack without internet dependency.

### 4. Aligns with TRIDENT's Raspberry Pi Target

On a Raspberry Pi 5, an additional 50–200ms Wikibase API call is acceptable if it eliminates
retraining overhead and keeps the model smaller. The alternative (CPT) requires GPU time
upfront and produces a larger checkpoint.

---

## Implementation Path

### Option A: Pre-inference Tag Lookup (minimal change to model)

```
1. Extract concern from AreaWithConcern input
2. Query local Wikibase index for matching tags
3. Append resolved tags to model input:
   "AreaWithConcern: Shinjuku, Tokyo, Japan; Churches
    [OSM context: amenity=place_of_worship, religion=christian]"
4. Fine-tuned model generates OverpassQL using the provided tags
```

The model needs to be retrained on augmented input format to learn to use the injected tags.

### Option B: Post-generation Tag Validation (no change to model)

```
1. Model generates OverpassQL as currently
2. Extract tag key-value pairs from generated OverpassQL
3. Validate each tag against Wikibase:
   - If status=deprecated: replace with use_instead value
   - If status=approved or de facto: keep
4. Re-inject corrected tags into the query
```

This is a pure post-processing step requiring no model retraining. Lower precision
(depends on regex extraction from OverpassQL), but zero retraining cost.

### Option C: Concern-to-Tags Model + OverpassQL Assembler (most modular)

```
Stage 1: NL concern → OSM tags (Wikibase lookup or small classifier)
Stage 2: AreaWithConcern + OSM tags → OverpassQL (current fine-tuned model)
```

Stage 2 is the current model, but retrained with explicit tag annotations in input.
Stage 1 is a deterministic lookup, not a model. The most architecturally clean option.

---

## Relationship to Existing Work

### `build_osm_wiki_corpus.py` and `data/osm_wiki_corpus.txt`

The existing CPT corpus builder already extracts exactly the data needed for a tool-call
grounding index. The same `parse_rdf()` function can back a lookup API — the output
format just changes from a training corpus to a query-response service.

### The Two-Call Fallback Pattern (RD-004)

The frontend's two-call `name:en` fallback is an existing example of TRIDENT's
willingness to do multi-step inference for correctness. Tool-call grounding is the
same pattern applied at the tag layer.

### v2 Training Dataset (church-fixed)

The church fix (`amenity=place_of_worship + religion=christian` union) in the training
data is a manual workaround for the same problem that Wikibase tool-call grounding would
solve automatically and systematically across all deprecation cases.

---

## Open Questions

1. **What is the optimal point to inject tag knowledge?** — Pre-inference (augmented input)
   vs post-generation (validation/correction) vs hybrid?

2. **How well does Wikibase text-search resolve natural language concerns?** — "churches"
   → `amenity=place_of_worship` requires semantic matching, not just exact tag lookup.
   A small embedding-based retrieval step may be needed for ambiguous concerns.

3. **How does regional tagging variance interact with global Wikibase?** — Wikibase
   encodes the global consensus. Regional conventions (e.g., Japanese hospitals using
   `amenity=hospital` + specific subtags) may require region-aware lookup.

4. **Would a Wikibase-grounded model need retraining from v2?** — Option A requires
   retraining on augmented input format. Could reuse the v2 checkpoints with a
   prompt-engineering approach first to estimate the benefit before retraining.

5. **Can the local `wikibase-rdf.ttl.gz` mirror serve as the production index?** — The
   10 MB file covers the full tag graph. A lightweight Python service over this file
   could serve the TRIDENT stack with sub-millisecond local lookups.

---

## Conclusion

The existence of a complete, structured, queryable OSM Wikibase graph creates an
opportunity to eliminate the model's tag knowledge responsibility entirely — moving it
from probabilistic weights into a deterministic, always-current lookup system.

This is architecturally cleaner than CPT (no retraining required for tag updates),
more reliable (no hallucination of wrong tags), and feasible on the Raspberry Pi target
(lightweight local index).

CPT (RD-003) and tool-call grounding are not mutually exclusive — CPT improves the model's
baseline understanding; tool-call grounding catches residual errors at inference time.
But if only one is implemented, tool-call grounding addresses the concrete failure cases
(wrong tags) more directly than CPT.
