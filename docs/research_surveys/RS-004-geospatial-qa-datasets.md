# RS-004: 地理空間 QA データセット — 関連研究

地理的な質問応答（Geospatial Question Answering）のデータセットおよびベンチマーク研究。
text2geoql-dataset は「QA データセット」というより「クエリ生成データセット」だが、地名・POI 検索という観点で密接に関連する。

---

## 1. GeoQuestions1089 (2023-05/11)

- **論文:** [Benchmarking Geospatial Question Answering Engines Using the Dataset GeoQuestions1089](http://cgi.di.uoa.gr/~koubarak/publications/2023/ISWC_2023_GeoQuestions_paper-3.pdf)
- **リポジトリ / データ:** https://github.com/AI-team-UoA/GeoQuestions1089 / https://huggingface.co/datasets/AI-team-UoA/GeoQuestions1089
- **概要:** クラウドソーシングで収集した地理的 QA データセット。質問・クエリ・回答の三つ組 1,089 件を含む
- **クエリ言語:** GeoSPARQL（RDF/SPARQL ベース）
- **text2geoql との差異:** GeoSPARQL vs Overpass QL。知識グラフベース vs OSM ベース。クラウドソーシング vs 合成データ

## 2. MapEval (2024-10)

- **リポジトリ:** https://github.com/MapEval/MapEval-Textual / https://github.com/MapEval/MapEval-API / https://github.com/MapEval/MapEval-Visual
- **概要:** マルチモーダルな地図理解の評価ベンチマーク。テキスト・API・ビジュアルの 3 種の評価形式
- **MapEval-API との関連:** API 呼び出しを用いた地理的 QA を評価する点で、本プロジェクトの Overpass API 利用と構造的に近い

## 3. GeoLLM (2024-10)

- **論文:** [GeoLLM: Extracting Geospatial Knowledge from Large Language Models](https://arxiv.org/abs/2310.06213) — Manvi et al.
  - 関連: [Large Language Models are Geographically Biased](https://arxiv.org/abs/2402.02680)
- **リポジトリ:** https://github.com/rohinmanvi/GeoLLM
- **概要:** LLM が持つ地理空間知識（人口密度、貧困率等の社会経済指標）を抽出・活用する研究
- **text2geoql との関連:** LLM が OSM タグの知識（`amenity=restaurant` 等）を保有しているという前提は共通。ただし目的は異なる（QA vs クエリ生成）

## 4. GeoGLUE (2023-05)

- **論文:** [GeoGLUE: A GeoGraphic Language Understanding Evaluation Benchmark](https://arxiv.org/abs/2305.06545)
- **概要:** 地理言語理解の総合ベンチマーク。地名認識・地名解決・空間関係理解等のタスクを含む
- **text2geoql との関連:** 地名解決（Nominatim によるグラウンディング）は GeoGLUE のサブタスクと重なる

## 5. WorldKG / SE-KGE (地理的知識グラフ)

- **WorldKG (2021):** [WorldKG: A World-Scale Geographic Knowledge Graph](https://arxiv.org/abs/2109.10036) — OSM からの大規模地理知識グラフ
- **SE-KGE (2020):** [SE-KGE: A Location-Aware Knowledge Graph Embedding Model for Geographic Question Answering](https://arxiv.org/abs/2004.14171)
- **text2geoql との関連:** OSM を知識グラフとして利用するアプローチは本プロジェクトとは異なるが、OSM を QA の基盤にするという問題意識は共通

---

## 総括

| データセット | 言語 | 規模 | 生成方法 | 対象 |
|------------|-----|------|---------|------|
| GeoQuestions1089 | GeoSPARQL | 1,089 | クラウドソーシング | 地理 QA |
| OverpassNL | Overpass QL | ~3,000 | クラウドソーシング | OSM クエリ |
| **text2geoql-dataset** | **Overpass QL** | **6,415+** | **LLM 合成 + 自動検証** | **POI 検索** |

地理 QA 分野において、**Overpass QL に特化した合成データセット** は本プロジェクトが唯一であり、規模・生成方法・自動検証の点でいずれの先行データセットとも異なる。
