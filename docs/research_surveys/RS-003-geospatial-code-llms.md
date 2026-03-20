# RS-003: 地理空間コード生成 LLM — 関連研究

自然言語から地理空間コード（Python GIS コード, Overpass QL, Earth Engine スクリプト等）を生成する LLM 研究群。
text2geoql-dataset の「Overpass QL 生成」は、この研究領域の一部として位置づけられる。

---

## 1. geospatial-code-llms-dataset (2024-08/10)

- **論文:** [Evaluation of Code LLMs on Geospatial Code Generation](https://arxiv.org/abs/2410.04617) — Kraina AI
- **リポジトリ:** https://github.com/kraina-ai/geospatial-code-llms-dataset
- **概要:** 地理空間コード生成タスクにおける Code LLM の評価データセット。Python ベースの GIS コード（GeoPandas, Shapely, OSMnx 等）生成を対象
- **アプローチ:** 複数 LLM（GPT-4, CodeLlama 等）のゼロショット・Few-Shot 評価
- **text2geoql との差異:** Python コードが対象。Overpass QL のような DSL 生成は含まない

## 2. GeoCode-GPT / GeoCode-Bench (2024-10)

- **論文:** [GeoCode-GPT: A Large Language Model for Geospatial Code Generation Tasks](https://arxiv.org/abs/2410.17031)
  - 関連: [Can Large Language Models Generate Geospatial Code?](https://arxiv.org/abs/2410.09738)
- **概要:** 地理空間コード生成に特化した LLM の提案と、ベンチマーク（GeoCode-Bench）の構築
- **対象コード:** Python GIS コード, Google Earth Engine スクリプト
- **重要性:** 地理空間ドメイン特化の LLM Fine-tuning が有効であることを示す

## 3. Geo-FuB (2024-08/10)

- **論文:** [Geo-FuB: A Method for Constructing an Operator-Function Knowledge Base for Geospatial Code Generation Tasks Using Large Language Models](https://arxiv.org/abs/2410.20975)
- **リポジトリ:** https://github.com/whuhsy/Geo-FuB
- **概要:** LLM を用いて地理空間コード生成タスク向けのオペレータ・関数知識ベースを自動構築する手法
- **text2geoql との類似:** **LLM を使ってデータを自動生成する** アプローチは共通。ただし対象は OSM タグ知識ベースではなく Python API 関数

## 4. Chain-of-Programming (CoP) (2024-11)

- **論文:** [Chain-of-Programming (CoP): Empowering Large Language Models for Geospatial Code Generation](https://arxiv.org/abs/2411.10753)
- **概要:** 地理空間コード生成における Chain-of-Thought の変種「Chain-of-Programming」を提案。コードの分解・段階的生成で精度向上
- **text2geoql との関連:** Overpass QL 生成に同様の段階的生成アプローチを適用する余地あり

## 5. GIS Copilot / SpatialAnalysisAgent (2024-09/11)

- **論文:** [GIS Copilot: Towards an Autonomous GIS Agent for Spatial Analysis](https://arxiv.org/abs/2411.03205)
- **リポジトリ:** https://github.com/Teakinboyewa/SpatialAnalysisAgent
- **概要:** QGIS プラグインとして実装された自律 GIS エージェント。自然言語指示から QGIS 操作コードを生成・実行
- **対象コード:** PyQGIS スクリプト（Python）

## 6. GeoAgent (2024-10)

- **論文:** [An LLM Agent for Automatic Geospatial Data Analysis](https://arxiv.org/abs/2410.18792)
- **概要:** 地理空間データ解析を自動化する LLM エージェント。データ取得・分析・可視化を一貫して実行

---

## 総括: text2geoql の位置づけ

地理空間コード生成の研究群の中で、**Overpass QL（DSL）に特化した Fine-tuning 用合成データセット**を構築しているのは text2geoql-dataset が唯一である。

既存研究の大半は：
- Python GIS ライブラリコードを対象としている
- Fine-tuning ではなく Few-Shot / Zero-shot 評価に留まっている
- データセット規模が小さい（数百件程度）

本プロジェクトは Raspberry Pi 4B のような **エッジデバイス上の ≤1.1B モデル** を Fine-tuning ターゲットとしており、実用的な小型化という観点でも独自性がある。
