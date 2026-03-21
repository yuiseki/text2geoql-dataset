# text2geoql-dataset

A synthetic dataset for training small language models to translate **TRIDENT intermediate language** into **Overpass QL** queries for OpenStreetMap.

Published dataset: **[yuiseki/text2geoql](https://huggingface.co/datasets/yuiseki/text2geoql)** on Hugging Face Hub

---

## Background: TRIDENT

**[TRIDENT](https://github.com/yuiseki/TRIDENT)** is an AI-powered interactive map assistant that turns natural language conversation into live OpenStreetMap visualizations. Its architecture is intentionally decomposed into three layers:

```
User (natural language)
  ↓
Surface layer  — manages dialogue, decides if a map request is feasible
  ↓
Inner layer    — analyzes the conversation and writes TRIDENT intermediate language
  ↓
Deep layer     — reads the intermediate language and writes Overpass QL
  ↓
Overpass API   — returns real OSM elements → rendered as an interactive map
```

This three-layer decomposition was driven by a hard constraint: **the system had to work with text-davinci-003**, a pre-GPT-3.5 model. By splitting the task into simpler sub-problems, each layer could be guided reliably with few-shot examples even on weak models. Today's frontier models could handle everything in one shot, but the design remains valuable in **resource-constrained environments** — air-gapped infrastructure, edge devices, or a Raspberry Pi 4B with 8 GB RAM.

### TRIDENT intermediate language

The inner layer outputs a structured text format that the deep layer consumes:

```
ConfirmHelpful: 地図を作成しました。他にご要望はありますか？
TitleOfMap: 東京のラーメン店
Area: Taito, Tokyo
Area: Bunkyo, Tokyo
AreaWithConcern: Taito, Tokyo; Ramen shops
AreaWithConcern: Bunkyo, Tokyo; Ramen shops
EmojiForConcern: Ramen shops, 🍜
ColorForConcern: Ramen shops, lightyellow
```

The key entries for this dataset are `AreaWithConcern` (and `Area`), which express a geographic region paired with a point-of-interest category.

---

## Purpose of this repository

The deep layer of TRIDENT — translating `AreaWithConcern: Shinjuku, Tokyo, Japan; Cafes` into valid, grounded Overpass QL — is the task this dataset targets.

**The ambition:** fine-tune a **≤ 1.1B parameter LLM** specialized for this narrow task, using frameworks like [Unsloth](https://github.com/unslothai/unsloth) on a 24 GB VRAM machine. A 1.1B model fast enough to run on a Raspberry Pi 4B would make the full TRIDENT pipeline viable entirely offline.

---

## What has been achieved

- **18,000+ TRIDENT input instructions** paired with **3,000+ validated Overpass QL queries** (growing)
- All queries verified against a self-hosted Overpass API — every saved query returns ≥ 1 real OSM element
- **148 POI categories** across transport, accommodation, food & drink, shopping, health & medical, education, finance, public facilities, parks & nature, sport, tourism, historic & heritage, places of worship, craft & artisan, and natural features
- Multi-model benchmark across 60+ model/config combinations; best: **gemma3:12b `--num-ctx 32768` → 100%**, `qwen3:8b --no-think` → 87%, `qwen2.5-coder:3b` → 80% at 4.9 s/query
- Geographic coverage: Japan, South Korea, United States, Nepal, Taiwan, Kosovo, Lebanon, Kenya, Mexico, Ethiopia
- **LoRA fine-tuning PoC**: `Qwen2.5-Coder-0.5B-Instruct` + LoRA on 4278 pairs → **95.1% accuracy** on full 226-pair holdout with **no Few-Shot prompting** (vs. 47% Few-Shot baseline with 3B) → see [RF-004](docs/research_findings/RF-004-lora-ft-eliminates-few-shot-need.md) and [`examples/lora_finetune/`](examples/lora_finetune/)

---

## Technical approach

### Generation pipeline

```
TRIDENT AreaWithConcern instruction
  → Few-Shot prompt  (semantic similarity via LangChain + Chroma + nomic-embed-text)
  → Local LLM        (Ollama — deterministic, temp=0.01)
  → OverpassQL extraction + line-count check
  → Self-hosted Overpass API validation  (must return ≥ 1 element)
  → Saved with provenance metadata  (model, temperature, element_count)
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
  input-trident.txt                  # TRIDENT AreaWithConcern instruction
  output-{model-slug}.overpassql     # validated Overpass QL
  output-{model-slug}.meta.json      # provenance (model, temp, element_count)
  not-found-{model-slug}.json        # failure record (reason, query)
```

---

## Known issues

- **Semantic tag grouping**: Natural language concepts do not map 1:1 to OSM tags. Japanese 「病院」covers `amenity=hospital`, `amenity=clinic`, and `amenity=doctors`, while English "hospital" typically means only the first. The correct scope is language- and culture-dependent. (→ [ADR-009](docs/ADR/ADR-009-semantic-tag-grouping.md))
- **Dual tag namespaces**: OSM has parallel `amenity=` (legacy) and `healthcare=` (newer) namespaces. A comprehensive query for "pharmacies" must union `amenity=pharmacy` and `healthcare=pharmacy`. (→ [ADR-009](docs/ADR/ADR-009-semantic-tag-grouping.md))
- **Place name fragility**: LLM-generated `area["name:en"="Shinjuku"]` is fragile. Nominatim-grounded `area(3601758858)` is more reliable but requires integrating Nominatim into the generation pipeline. (→ [ADR-007](docs/ADR/ADR-007-nominatim-area-grounding.md))
- **VRAM constraint on large models**: Models above ~14b parameters exceed 24 GB VRAM on this machine and fall back to CPU inference, degrading quality and speed.

---

## Roadmap

### Near-term
- [x] Integrate Nominatim into the generation pipeline (`generate_overpassql_v2.py`)
- [x] Integrate Taginfo tag validation as a pre-Overpass filter to catch invalid tags early
- [x] Expand POI categories from 80 to 148 via OSM approved tags survey
- [ ] Run batch generation with v2 pipeline (Nominatim + Taginfo) across all entries
- [ ] Add composite concern entries for semantic groups (e.g., `Medical Facilities` = hospital + clinic + doctors union)

### Medium-term
- [ ] Auto-expand geographic coverage using Nominatim admin-area enumeration
- [ ] Auto-refresh `good_concerns.yaml` from Taginfo usage-frequency data
- [x] LoRA fine-tuning PoC on 0.5B model — 95.1% accuracy, Few-Shot no longer needed (→ [`examples/lora_finetune/`](examples/lora_finetune/))

### Long-term
- [ ] Ship a fine-tuned model that runs on Raspberry Pi 4B (8 GB RAM), enabling TRIDENT deep layer fully offline
- [ ] Multi-language TRIDENT intermediate language (Japanese/Korean/Arabic input) with language-aware concept-to-tag mapping

---

## Architecture decisions

Design rationale is documented in [`docs/ADR/`](docs/ADR/README.md).

---

## Research findings

Experiment-driven insights broadly applicable to Few-Shot LLM prompting and geospatial query generation — [`docs/research_findings/`](docs/research_findings/README.md)

| ID | Title | Status |
|----|-------|--------|
| [RF-001](docs/research_findings/RF-001-num-ctx-context-window-effect.md) | `num_ctx` (context window size) is a critical inference-time hyperparameter for Few-Shot quality | Confirmed |
| [RF-002](docs/research_findings/RF-002-few-shot-k-model-size-dependency.md) | Optimal Few-Shot k depends on model size — larger k hurts small models | Confirmed |
| [RF-003](docs/research_findings/RF-003-administrative-hierarchy-enables-nominatim-disambiguation.md) | Pre-encoded administrative hierarchy enables Nominatim to solve toponym disambiguation that LLMs fail at | Confirmed |
| [RF-004](docs/research_findings/RF-004-lora-ft-eliminates-few-shot-need.md) | LoRA fine-tuning of 0.5B model eliminates Few-Shot need — 95.1% accuracy on holdout with no prompt engineering | Confirmed |

---

## Related work

Surveys of prior work in Text-to-OverpassQL, NL-driven geodata retrieval, and OSM-specific NLP/LLM research — [`docs/research_surveys/`](docs/research_surveys/README.md)

| ID | Summary |
|----|---------|
| [RS-001](docs/research_surveys/RS-001-text-to-overpassql.md) | Text-to-OverpassQL (Schifferle et al. TACL 2024) — closest prior work; T5 fine-tuned on crowdsourced NL–Overpass pairs |
| [RS-002](docs/research_surveys/RS-002-nl-geodata-retrieval.md) | NL-driven geodata retrieval — ChatGeoPT, LLM-Find, Autonomous GIS, Geode |
| [RS-003](docs/research_surveys/RS-003-geospatial-code-llms.md) | Geospatial code generation LLMs — GeoCode-GPT, Geo-FuB, Chain-of-Programming |
| [RS-004](docs/research_surveys/RS-004-geospatial-qa-datasets.md) | Geospatial QA datasets — GeoQuestions1089, MapEval, WorldKG |
| [RS-005](docs/research_surveys/RS-005-trident-origin.md) | TRIDENT — origin project and intermediate language design rationale |
| [RS-006](docs/research_surveys/RS-006-osm-specific-nlp-llm.md) | OSM-specific NLP/LLM — OsmT (Dec 2024), SPOT v2 (ACL 2025), CHATMAP, WorldKG |

**Novelty of this project** vs prior work: TRIDENT intermediate language · automated synthetic data generation with Overpass API validation · edge-device fine-tuning target (≤1.1B on Raspberry Pi 4B) · Nominatim-grounded area disambiguation.

## Development

```bash
uv sync                          # install dependencies
uv run pytest                    # run tests

# Generate OverpassQL for one TRIDENT instruction
uv run python src/generate_overpassql.py data/concerns/amenity/cafe/Japan/Tokyo/Shinjuku

# Benchmark model sizes
uv run python src/benchmark_models.py --models qwen3:8b --no-think --trials 3

# Feasibility study (Nominatim + Taginfo)
uv run python src/feasibility_nominatim_taginfo.py
```
