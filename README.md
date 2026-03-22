# text2geoql-dataset

A synthetic dataset for training small language models to translate **TRIDENT intermediate language** into **Overpass QL** queries for OpenStreetMap.

**Key result:** `Qwen2.5-Coder-0.5B-Instruct` fine-tuned with LoRA (PEFT + TRL) achieves **100.0% (112/112)** on a held-out evaluation set of pairs that are (1) excluded from training data and (2) guaranteed to return non-empty results from the Overpass API. Runs at **25.8 tok/s on Raspberry Pi 5** — making the full TRIDENT pipeline viable entirely offline on a $80 device.

Published dataset: **[yuiseki/text2geoql](https://huggingface.co/datasets/yuiseki/text2geoql)** on Hugging Face Hub

Published model (GGUF): **[yuiseki/qwen2.5-coder-0.5b-trident-deep-v4.2-gguf](https://huggingface.co/yuiseki/qwen2.5-coder-0.5b-trident-deep-v4.2-gguf)** on Hugging Face Hub

---

## What it does

Given a TRIDENT `AreaWithConcern` instruction, the model generates a valid Overpass QL query:

**Input:**
```
AreaWithConcern: Shinjuku, Tokyo, Japan; Cafes
```

**Output:**
```overpassql
[out:json][timeout:30];
area["name:en"="Tokyo"]->.outer;
area["name:en"="Shinjuku"]->.inner;
(
  nwr["amenity"="cafe"](area.inner)(area.outer);
);
out geom;
```

Areas in `AreaWithConcern` are always listed **smallest to largest** — the first token is the innermost area (inner filter), each subsequent token is a larger containing area (outer filter).

---

## Background: TRIDENT

**[TRIDENT](https://github.com/yuiseki/TRIDENT)** is an AI-powered interactive map assistant that turns natural language conversation into live OpenStreetMap visualizations. Its architecture decomposes the task into three layers:

```
User (natural language)
  ↓
Surface layer  — manages dialogue, decides if a map request is feasible
  ↓
Inner layer    — analyzes the conversation and writes TRIDENT intermediate language
  ↓
Deep layer     — reads the intermediate language and writes Overpass QL   ← this dataset
  ↓
Overpass API   — returns real OSM elements → rendered as an interactive map
```

This dataset targets the **deep layer**: translating structured `AreaWithConcern` instructions into executable Overpass QL. The decomposed design is valuable in **resource-constrained environments** — air-gapped infrastructure, edge devices, or a Raspberry Pi 5 — where a single frontier model is not available. See [RS-005](docs/research_surveys/RS-005-trident-origin.md) for origin and design rationale.

---

## What has been achieved

- **4,897 validated training pairs** (as of 2026-03-22, growing)
- All queries verified against the public Overpass API — every saved query returns ≥ 1 real OSM element
- **148 POI categories** across transport, accommodation, food & drink, shopping, health & medical, education, finance, public facilities, parks & nature, sport, tourism, historic & heritage, places of worship, craft & artisan, and natural features
- **Geographic coverage:** Japan (Tokyo, Osaka, Sapporo, Sendai, Nagoya, Fukuoka, Kyoto, Kobe, Naha…), South Korea (Seoul, Busan, Daegu, Incheon…), Europe (London, Paris, Munich, Rome, Amsterdam, Warsaw, Florence, Valencia…), Asia-Pacific (Singapore, Taipei, Melbourne, Sydney, Bangkok…), Africa, Americas, and more
- **LoRA fine-tuning** — `Qwen2.5-Coder-0.5B-Instruct` with PEFT+TRL (no Unsloth) achieves **100.0% (112/112)** on a held-out eval set of pairs excluded from training and guaranteed to return non-empty Overpass API results (v4.2 adapter); see [RF-004](docs/research_findings/RF-004-lora-ft-eliminates-few-shot-need.md) and [RF-009](docs/research_findings/RF-009-v4-multilevel-augmentation.md)
- **Raspberry Pi 5 deployment confirmed** — GGUF-quantized model runs on Raspberry Pi 5 (8 GB RAM) via llama.cpp:

| Quantization | Size | Generation speed | ~100-token query |
|---|---|---|---|
| Q4_K_M | 380 MB | **25.8 tok/s** | ~4 sec |
| Q8_0 | 507 MB | 19.3 tok/s | ~5 sec |
| F16 | 949 MB | 11.6 tok/s | ~9 sec |

---

## Fine-tuning

LoRA fine-tuning code (PEFT + TRL, no Unsloth) is included in [`examples/lora_finetune/`](examples/lora_finetune/README.md). It trains `Qwen2.5-Coder-0.5B-Instruct` in ~12 minutes on an NVIDIA RTX 3060 × 2 (12 GB VRAM each) and produces a ~35 MB adapter.

```bash
pip install -r examples/lora_finetune/requirements.txt
python examples/lora_finetune/train.py
python examples/lora_finetune/eval_guaranteed_nonempty.py --adapter models/qwen2.5-coder-0.5b-lora
```

---

## Technical approach

### Generation pipeline

```
TRIDENT AreaWithConcern instruction
  → Few-Shot prompt  (semantic similarity via LangChain + Chroma + nomic-embed-text)
  → Local LLM        (Ollama — deterministic, temp=0.01)
  → OverpassQL extraction + line-count check
  → Public Overpass API validation  (must return ≥ 1 element)
  → Saved with provenance metadata  (model, temperature, element_count)
```

For multi-level training pairs (3-level `City, Region, Country` and 2-level `City, Country`), `src/generate_multilevel_pairs.py` generates correct Overpass QL from templates and verifies via the public Overpass API.

### Dataset file structure

```
data/concerns/{osm-key}/{osm-value}/{Country}/[{Region}/]{City}/[{District}/]
  input-trident.txt                  # TRIDENT AreaWithConcern instruction
  output-001.overpassql              # validated Overpass QL (gold standard)
  output-{model-slug}.overpassql    # model-generated outputs (where available)
```

### Overpass QL patterns

**4-level** (`District, City, Region, Country`):
```overpassql
[out:json][timeout:30];
area["name:en"="City"]->.outer;
area["name:en"="District"]->.inner;
(
  nwr["amenity"="cafe"](area.inner)(area.outer);
);
out geom;
```

**3-level** (`City, Region, Country`):
```overpassql
[out:json][timeout:30];
area["name:en"="Region"]->.outer;
area["name:en"="City"]->.inner;
(
  nwr["amenity"="cafe"](area.inner)(area.outer);
);
out geom;
```

**2-level** (`City, Country`):
```overpassql
[out:json][timeout:30];
area["name:en"="City"]->.searchArea;
(
  nwr["amenity"="cafe"](area.searchArea);
);
out geom;
```

---

## OSM `name:en` tagging conventions

Three patterns affect whether `area["name:en"=...]` resolves correctly:

| Pattern | Description | Example | Two-call fallback |
|---------|-------------|---------|-------------------|
| **A** — tag absent (name = name:en) | OSM omits `name:en` when identical to `name` | Düsseldorf, Bilbao, Bordeaux | ✅ Recoverable |
| **B** — accent mismatch or absent | English differs from native due to diacritics | Kraków→Krakow, Île-de-France | ✅ Recoverable |
| **C** — admin hierarchy gap | Area not linked into region's OSM relation hierarchy | Marseille/Provence | ❌ Not recoverable |

The **two-call fallback** retries with `["name"=...]` when `["name:en"=...]` returns zero results, recovering Pattern A and B at zero model cost (+20% coverage). See [RF-008](docs/research_findings/RF-008-two-call-name-fallback.md) for full analysis and implementation.

**Japanese ward naming** differs by city type:
- Tokyo's 23 special wards (特別区): `name:en` **without** "Ward" suffix — e.g., `"Shinjuku"`, `"Shibuya"`
- Other cities' wards (行政区): `name:en` **with** "Ward" suffix — e.g., `"Chuo Ward"`, `"Atsuta Ward"`
- Korean wards (구): `name:en` with "-gu" suffix — e.g., `"Gangnam-gu"`

---

## Known issues

- **Semantic tag grouping**: Natural language concepts do not map 1:1 to OSM tags. Japanese 「病院」covers `amenity=hospital`, `amenity=clinic`, and `amenity=doctors`, while English "hospital" typically means only the first. (→ [ADR-009](docs/ADR/ADR-009-semantic-tag-grouping.md))
- **Dual tag namespaces**: OSM has parallel `amenity=` (legacy) and `healthcare=` (newer) namespaces. A comprehensive query for "pharmacies" must union both. (→ [ADR-009](docs/ADR/ADR-009-semantic-tag-grouping.md))
- **`name:en` fragility**: Model-generated `area["name:en"="Shinjuku"]` can fail for areas where OSM omits `name:en`. The two-call fallback (RF-008) mitigates this at inference time.
- **Administrative hierarchy gaps (Pattern C)**: Some city areas exist in OSM but are not linked into their containing region's relation hierarchy, causing `(area.inner)(area.outer)` to return zero. Not recoverable by name fallback.

---

## Roadmap

### Near-term
- [x] Expand POI categories to 148 via OSM approved tags survey
- [x] LoRA fine-tuning — Qwen 0.5B: 100.0% (112/112) on guaranteed-nonempty eval (v4.2)
- [x] Multi-level training data (3-level JP cities, 2-level Korean/world cities)
- [x] Two-call `name:en` → `name` fallback infrastructure
- [x] GGUF quantization (Q8_0, Q4_K_M, F16) for Raspberry Pi 5 deployment
- [x] Raspberry Pi 5 llama.cpp inference benchmark — Q4_K_M: **25.8 tok/s**, fully practical
- [ ] Add more cities' administrative wards (Osaka, Nagoya, Fukuoka, Kyoto…)

### Medium-term
- [ ] Nominatim-grounded area filter — `area(relation_id)` instead of `area["name:en"=...]`
- [ ] Composite concern entries (e.g., `Medical Facilities` = hospital ∪ clinic ∪ doctors)
- [ ] Multi-language TRIDENT input (Japanese/Korean input → English OSM tags)

### Long-term
- [x] ~~Ship a fine-tuned model that runs fully offline on Raspberry Pi 5 (8 GB RAM)~~ **Done** — Q4_K_M at 25.8 tok/s on Pi 5
- [ ] Integrate with TRIDENT deep layer in production

---

## Architecture decisions

Design rationale is documented in [`docs/ADR/`](docs/ADR/README.md).

---

## Research findings

Experiment-driven insights on Few-Shot LLM prompting, LoRA fine-tuning, and geospatial query generation — [`docs/research_findings/`](docs/research_findings/README.md)

| ID | Title | Status |
|----|-------|--------|
| [RF-001](docs/research_findings/RF-001-num-ctx-context-window-effect.md) | `num_ctx` is a critical inference-time hyperparameter for Few-Shot quality | Confirmed |
| [RF-002](docs/research_findings/RF-002-few-shot-k-model-size-dependency.md) | Optimal Few-Shot k depends on model size — larger k hurts small models | Confirmed |
| [RF-003](docs/research_findings/RF-003-administrative-hierarchy-enables-nominatim-disambiguation.md) | Administrative hierarchy enables Nominatim toponym disambiguation | Confirmed |
| [RF-004](docs/research_findings/RF-004-lora-ft-eliminates-few-shot-need.md) | LoRA fine-tuning of sub-1B models eliminates Few-Shot need | Confirmed |
| [RF-005](docs/research_findings/RF-005-generalization-unseen-cities.md) | Unseen city generalization: tag knowledge transfers, area hierarchy does not | Confirmed |
| [RF-006](docs/research_findings/RF-006-zero-results-scoring-policy.md) | Scoring policy: `zero_results=pass` reveals all failures are OSM coverage, not syntax | Confirmed |
| [RF-007](docs/research_findings/RF-007-guaranteed-nonempty-eval.md) | Guaranteed-nonempty strict eval identifies 4 failure classes | Confirmed |
| [RF-008](docs/research_findings/RF-008-two-call-name-fallback.md) | Two-call `name:en` → `name` fallback: +20% at zero model cost; OSM tagging conventions | Confirmed |
| [RF-009](docs/research_findings/RF-009-v4-multilevel-augmentation.md) | v4 dataset augmentation: 92.0% → 100.0% via multi-level training pairs + system prompt | Confirmed |

---

## Related work

Surveys of prior work in Text-to-OverpassQL, NL-driven geodata retrieval, and OSM-specific NLP/LLM research — [`docs/research_surveys/`](docs/research_surveys/README.md)

| ID | Summary |
|----|---------|
| [RS-001](docs/research_surveys/RS-001-text-to-overpassql.md) | Text-to-OverpassQL (Schifferle et al. TACL 2024) — closest prior work |
| [RS-002](docs/research_surveys/RS-002-nl-geodata-retrieval.md) | NL-driven geodata retrieval — ChatGeoPT, LLM-Find, Autonomous GIS, Geode |
| [RS-003](docs/research_surveys/RS-003-geospatial-code-llms.md) | Geospatial code generation LLMs — GeoCode-GPT, Geo-FuB, Chain-of-Programming |
| [RS-004](docs/research_surveys/RS-004-geospatial-qa-datasets.md) | Geospatial QA datasets — GeoQuestions1089, MapEval, WorldKG |
| [RS-005](docs/research_surveys/RS-005-trident-origin.md) | TRIDENT — origin project and intermediate language design rationale |
| [RS-006](docs/research_surveys/RS-006-osm-specific-nlp-llm.md) | OSM-specific NLP/LLM — OsmT (Dec 2024), SPOT v2 (ACL 2025), CHATMAP, WorldKG |

**Novelty of this project** vs prior work: TRIDENT intermediate language · automated synthetic data generation with Overpass API validation · edge-device deployment confirmed (0.5B at 25.8 tok/s on Raspberry Pi 5) · two-call `name:en` → `name` fallback · OSM tagging convention documentation.

---

## Development

```bash
uv sync                          # install dependencies
uv run pytest                    # run tests

# Generate OverpassQL for one TRIDENT instruction
uv run python src/generate_overpassql.py data/concerns/amenity/cafe/Japan/Tokyo/Shinjuku

# Generate multi-level training pairs (3-level / 2-level) with Overpass verification
uv run python src/generate_multilevel_pairs.py

# Compile all pairs and push to Hugging Face Hub
uv run python src/compile.py

# Benchmark model sizes (Few-Shot baseline)
uv run python src/benchmark_models.py --models qwen3:8b --no-think --trials 3
```

LoRA fine-tuning code (PEFT + TRL, no Unsloth) lives in [`examples/lora_finetune/`](examples/lora_finetune/README.md). Adapters are evaluated against guaranteed-nonempty pairs verified via the public Overpass API.
