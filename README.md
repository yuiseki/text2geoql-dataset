# text2geoql-dataset

A synthetic dataset for **text-to-GeoQL** — translating natural language into geospatial query languages, starting with [Overpass QL](https://wiki.openstreetmap.org/wiki/Overpass_API/Overpass_QL) for OpenStreetMap.

Published dataset: **[yuiseki/text2geoql](https://huggingface.co/datasets/yuiseki/text2geoql)** on Hugging Face Hub

---

## What has been achieved

- **6,415 TRIDENT input instructions** paired with **2,300+ validated OverpassQL queries**
- All queries verified against a self-hosted Overpass API — every saved query returns ≥ 1 real OSM element
- **80 POI categories** (concerns) spanning transport, accommodation, food, shopping, healthcare, education, public facilities, parks, sport, tourism, historic sites, and places of worship
- Multi-model generation pipeline benchmarked across Qwen2.5-coder (0.5b–32b), Qwen3 (0.6b–14b), Qwen3.5 (0.8b–9b); best result: **80% success rate** at ~4 s/query (`qwen3:8b --no-think`, `qwen2.5-coder:3b`)
- Geographic coverage: Japan, South Korea, United States, Nepal, Taiwan, Kosovo, Lebanon, Kenya, Mexico, Ethiopia

---

## Technical approach

### TRIDENT intermediate language

Natural language intent is first expressed as a structured **TRIDENT** instruction:

```
AreaWithConcern: Shinjuku, Tokyo, Japan; Cafes
```

TRIDENT decouples the place name and the POI type, making it easy to cross-product areas × concerns to generate input instructions at scale.

### Generation pipeline

```
TRIDENT instruction
  → Few-Shot prompt (semantic similarity via LangChain + Chroma + nomic-embed-text)
  → Local LLM inference (Ollama)
  → OverpassQL extraction
  → Validation against self-hosted Overpass API (must return ≥ 1 element)
  → Saved with provenance metadata (model, temperature, element_count)
```

### Self-hosted OSM infrastructure

All grounding uses self-hosted instances — no external rate limits:

| API | Endpoint | Role |
|-----|----------|------|
| **Overpass API** | `https://overpass.yuiseki.net/` | Query validation against real OSM data |
| **Nominatim** | `https://nominatim.yuiseki.net/` | Place name → OSM relation ID resolution |
| **Taginfo** | `https://taginfo.yuiseki.net/` | Tag usage statistics and validation |

### Dataset file structure

```
data/concerns/{osm-key}/{osm-value}/{Country}/{City}/{District}/
  input-trident.txt          # TRIDENT instruction
  output-{model-slug}.overpassql   # validated OverpassQL
  output-{model-slug}.meta.json    # provenance (model, temp, element_count)
  not-found-{model-slug}.json      # failure record (reason, query)
```

---

## Known issues

- **Semantic tag grouping**: Natural language concepts do not map 1:1 to OSM tags. Japanese 「病院」covers `amenity=hospital`, `amenity=clinic`, and `amenity=doctors`, while English "hospital" typically means only the former. The correct OSM tag scope is language- and culture-dependent. (→ [ADR-009](docs/ADR/ADR-009-semantic-tag-grouping.md))
- **Dual tag namespaces**: OSM has parallel `amenity=` (legacy) and `healthcare=` (newer) namespaces for medical facilities, and `amenity=pharmacy` coexists with `healthcare=pharmacy`. Comprehensive queries must union both. Same pattern applies to other domains. (→ [ADR-009](docs/ADR/ADR-009-semantic-tag-grouping.md))
- **Place name ambiguity**: LLM-generated `area["name:en"="Shinjuku"]` queries are fragile. Nominatim-grounded `area(3601758858)` queries are more reliable but require Nominatim integration in the generation pipeline. (→ [ADR-007](docs/ADR/ADR-007-nominatim-area-grounding.md))
- **Large model VRAM constraint**: Models above ~14b parameters exceed 2× RTX 3060 (24 GB) VRAM and fall back to CPU inference, degrading quality and speed.
- **qwen3:4b corrupted weights**: All outputs are `no_code_block` even after re-pull. Results for this size are not representative.

---

## Roadmap

### Near-term
- [ ] Integrate Nominatim into the generation pipeline: resolve TRIDENT area names to OSM relation IDs before prompting, replacing fragile `name:en` queries with `area(id)` queries
- [ ] Add composite concern entries for semantic groups (e.g., `Medical Facilities` = hospital + clinic + doctors union) and include union-query Few-Shot examples
- [ ] Integrate Taginfo tag validation as a pre-Overpass filter to catch invalid tags early and reduce wasted API calls
- [ ] Run `generate_trident.py` to expand the 80 concern × existing seed areas and grow the dataset

### Medium-term
- [ ] Auto-expand geographic coverage using Nominatim admin-area enumeration (fetch all districts for a given country/city)
- [ ] Auto-refresh `good_concerns.yaml` from Taginfo usage-frequency data
- [ ] Publish updated dataset to Hugging Face Hub

### Long-term
- [ ] Multi-language TRIDENT (Japanese, Korean, Arabic input) with language-aware concept-to-tag mapping
- [ ] Fine-tune a small model on this dataset and benchmark against few-shot prompting baseline

---

## Architecture decisions

Design rationale is documented in [`docs/ADR/`](docs/ADR/README.md).

## Development

```bash
# Install dependencies
uv sync

# Run tests
uv run pytest

# Generate OverpassQL for a single TRIDENT directory
uv run python src/generate_overpassql.py data/concerns/amenity/cafe/Japan/Tokyo/Shinjuku

# Benchmark model sizes
uv run python src/benchmark_models.py --models qwen3:8b --no-think --trials 3

# Run feasibility study (Nominatim + Taginfo)
uv run python src/feasibility_nominatim_taginfo.py
```
