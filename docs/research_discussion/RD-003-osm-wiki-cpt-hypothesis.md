# RD-003: Hypothesis — OSM Wiki Continued Pre-Training Before Task Fine-tuning

**Date:** 2026-03-21
**Type:** Hypothesis + Implementation plan
**Related:** RD-001, RD-002, RF-004

## Hypothesis

Sub-1B models lack OSM-specific vocabulary in their pre-training corpora (Common Crawl,
GitHub, etc. contain very few OSM Wiki articles). Continued pre-training (CPT) on OSM
Wiki text before task-specific fine-tuning should improve the model's internalized
knowledge of OSM tag semantics, deprecation rules, and key-value relationships.

Expected benefit: the model would "know" that:
- `amenity=church` is deprecated; `amenity=place_of_worship` + `religion=christian` is correct
- `building=church` refers to the physical structure, not the institution
- `healthcare=pharmacy` and `amenity=pharmacy` are parallel namespaces
- regional tagging conventions vary (e.g., Japanese 病院 maps to multiple tag combinations)

This knowledge is currently absent in base models and must be injected via the fine-tuning
dataset. With CPT, it would be pre-loaded into the weights before task fine-tuning begins.

---

## Data Source

**Location:** `repos/_maps/openstreetmap-wiki-dump/`

| File | Compressed | Uncompressed | Content |
|------|-----------|--------------|---------|
| `dump.xml.gz` | 6.3 GB | ~3 GB | Full MediaWiki XML export (multilingual) |
| `wikibase-rdf.ttl.gz` | 10 MB | ~? | Wikibase RDF — structured tag properties, deprecation status |

The XML dump includes:
- `Tag:*` pages — documentation for specific tag values (e.g., `Tag:amenity=cafe`)
- `Key:*` pages — documentation for tag keys (e.g., `Key:amenity`)
- `Relation:*` pages — OSM relation types
- Mapping guidelines, regional conventions, tagging proposals
- Multiple languages (EN, DE, FR, JA, RU, etc.)

---

## Proposed CPT Pipeline

### Step 1: Extract and Filter

```
dump.xml.gz → MediaWiki XML parser
           → filter: namespace=0 (main articles)
           → filter: title startswith Tag: | Key: | Relation: | Map Features | Overpass
           → estimated yield: ~10,000–30,000 high-signal pages
```

Priority pages (highest OSM tag signal):
- `Tag:amenity=*`, `Tag:tourism=*`, `Tag:leisure=*`, etc. — ~10,000+ tag pages
- `Key:amenity`, `Key:shop`, `Key:tourism`, etc. — ~500 key pages
- `Map Features` — the master tag reference
- `Overpass API` / `Overpass QL` pages

Lower priority (still useful):
- General mapping guides
- Country-specific tagging conventions (especially Japan, Korea, China)
- Language-specific namespaces (JA:, RU:, DE: — relevant for multi-lingual coverage)

### Step 2: MediaWiki → Plain Text

MediaWiki markup contains significant noise for LM training:
- Template syntax (`{{tag|amenity|cafe}}`) — needs expansion or stripping
- Wikilinks (`[[Key:amenity|amenity]]`) — strip to plain text
- Tables — convert to structured text or strip
- Categories — strip

Tool options:
- `mwparserfromhell` (Python) — parse and extract plain text
- Custom regex pipeline — faster, less accurate

### Step 3: Format for CPT

Two formatting strategies:

**A. Raw text (standard CLM)**
```
Tag:amenity=cafe

A café or coffee shop. Used for establishments primarily serving coffee and light
refreshments. See also: amenity=restaurant (for full meals), shop=coffee (for retail).

Status: approved
Implies: amenity=yes
```

**B. Structured pairs (more targeted)**
```
OSM Tag: amenity=cafe
Description: A café or coffee shop...
Status: approved
Related: amenity=restaurant, shop=coffee
```

Option A is simpler to implement and more natural for CLM. Option B may be more
efficient for injecting structured knowledge.

### Step 4: Continued Pre-training

```python
# Training setup
model = AutoModelForCausalLM.from_pretrained("google/gemma-3-270m-it")
# No LoRA for CPT — update all weights (or use larger LoRA r)
# Causal LM loss on OSM Wiki text
# ~1–3 epochs, learning rate ~1e-5 (lower than task FT)
```

Key decisions:
- **Full fine-tuning vs LoRA for CPT**: Full FT preserves knowledge better; LoRA is faster
  and avoids catastrophic forgetting. Given 270M parameter size, full FT may be feasible.
- **Learning rate**: Lower than task FT (1e-5 vs 2e-4) to avoid overwriting base knowledge
- **Data mixing**: Optionally mix a small fraction of general text to prevent catastrophic
  forgetting of language modeling ability

### Step 5: Task Fine-tuning on CPT Checkpoint

Same LoRA FT as current pipeline, but starting from the CPT checkpoint instead of the
base model.

---

## Expected Results

| Condition | Expected Score |
|-----------|---------------|
| Base → Task FT (current) | 93–97% |
| Base → OSM Wiki CPT → Task FT | 97–100%? |

The `building=church` failure should resolve without data fixes, because the model would
know from CPT that `amenity=place_of_worship` + `religion=christian` is the correct tag.

---

## Wikibase RDF as Alternative / Complement

`wikibase-rdf.ttl.gz` (10 MB compressed) contains structured tag knowledge:
- Tag key/value properties
- `approved` / `deprecated` / `in use` status
- Related tags, implied tags

This could be converted to structured text pairs and added to the CPT corpus:
```
Tag amenity=church: status=deprecated, use_instead=amenity=place_of_worship + religion=christian
Tag building=church: status=in use, description="building used as a church"
Tag amenity=place_of_worship: status=approved, religion values: christian, muslim, jewish, ...
```

This is a much smaller but higher-precision signal source than the full wiki dump.

---

## Risks and Mitigations

| Risk | Mitigation |
|------|-----------|
| Catastrophic forgetting of chat template | Evaluate base model chat behavior before/after CPT |
| CPT on multilingual wiki hurts English-only task | Filter to English namespace only first |
| Mediawiki markup noise degrades CPT quality | Use mwparserfromhell for clean extraction |
| CPT time too long for 270M | Tag: + Key: subset (~10k pages) is fast even on CPU |

---

## Implementation Priority

1. **High value, low effort**: Parse `wikibase-rdf.ttl.gz` → structured text → add to FT
   corpus as auxiliary data. No CPT needed; just augments training signal.

2. **High value, medium effort**: Extract `Tag:*` and `Key:*` pages from `dump.xml.gz`
   → plain text → CPT → Task FT.

3. **Full pipeline**: All namespace=0 pages → cleaned text → CPT → Task FT.
