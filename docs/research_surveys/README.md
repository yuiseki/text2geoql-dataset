# Research Surveys

このディレクトリは、text2geoql-dataset の先行研究・関連プロジェクトに関するサーベイをまとめたものである。

LLM 研究コミュニティに広く共有できる知見は `docs/research_findings/` を参照。
プロジェクト固有のバグ修正・実験記録は `docs/project-notes/` を参照。

---

## インデックス

| ファイル | 概要 |
|---------|------|
| [RS-001](RS-001-text-to-overpassql.md) | Text-to-OverpassQL (OverpassNL) — 最直接の先行研究。T5 fine-tuning + クラウドソーシングデータ |
| [RS-002](RS-002-nl-geodata-retrieval.md) | NL ドリブン地理データ取得 — ChatGeoPT, LLM-Geo, LLM-Find, Geode 等の関連プロジェクト群 |
| [RS-003](RS-003-geospatial-code-llms.md) | 地理空間コード生成 LLM — GeoCode-GPT, geospatial-code-llms-dataset 等 |
| [RS-004](RS-004-geospatial-qa-datasets.md) | 地理空間 QA データセット — GeoQuestions1089, MapEval, GeoLLM 等 |
| [RS-005](RS-005-trident-origin.md) | TRIDENT — 本プロジェクトの中間言語の起源プロジェクト |
| [RS-006](RS-006-osm-specific-nlp-llm.md) | OSM 特化 NLP/LLM 研究 — OsmT, SPOT v2, CHATMAP, WorldKG 等（検索調査済み） |

---

## text2geoql-dataset の新規性まとめ

先行研究との比較を通じて、本プロジェクトの独自貢献を整理する。

### 1. TRIDENT 中間言語（最大の新規性）

`AreaWithConcern: <地名>; <コンサーン>` という意味的な中間表現は、先行研究のいずれにも存在しない。
これにより：
- 自然言語の曖昧さを排除
- 地名解決を Nominatim に委譲（モデルが地名知識を保有する必要なし）
- 意味的グルーピング（「病院」= 複数 OSM タグの union）を中間層で解決

### 2. LLM + Overpass API による自動検証付き合成データ生成

既存の Overpass QL データセット（OverpassNL など）はクラウドソーシングに依存。
本プロジェクトは **LLM が生成したクエリを Overpass API に投げて結果が空でないことを検証** する自動パイプラインで、スケーラブルな合成データを生成する。

### 3. エッジデバイス向け Fine-tuning ターゲット

先行研究はサーバー上の大型 LLM（GPT-4 等）の Few-Shot 利用が主流。
本プロジェクトは **Raspberry Pi 4B 上の ≤1.1B モデル** を Fine-tuning ターゲットとし、オフライン・エッジ環境での動作を目指す。

### 4. 多言語・多文化対応の地名解決

Nominatim を用いた `area(id)` グラウンディングにより、日本語・英語・アラビア語等の多言語地名を精確に OSM エリアに解決する。
