# RS-002: NL ドリブン地理データ取得 — 関連プロジェクト群

自然言語から OSM / Overpass API を操作しようとした一連のプロジェクト。
いずれも **Few-Shot または API 呼び出し** ベースのアプローチで、Fine-tuning や合成データセット構築には至っていない。

---

## 1. ChatGeoPT (2023-03)

- **概要:** 自然言語テキストを Overpass API 呼び出しに変換する最初期のデモ実装
- **リポジトリ:** https://github.com/earth-genome/ChatGeoPT
- **アプローチ:** GPT-3.5 への Few-Shot プロンプトで Overpass QL を生成。地名解決は未対応
- **限界:** PoC レベル。汎化性・精度の系統的評価なし

## 2. osm-ai-map (2023-03)

- **概要:** 自然言語リクエストを Overpass API クエリに変換するウェブデモ
- **リポジトリ:** https://github.com/steveattewell/osm-ai-map
- **アプローチ:** ChatGeoPT と同様の GPT Few-Shot、UI 実装重視
- **限界:** 地名解決・クエリ検証なし

## 3. OSM-GPT (2023-07)

- **概要:** 自然言語クエリと OSM データベースのギャップを埋めることを目的とした実験プロジェクト
- **リポジトリ:** https://github.com/rowheat02/osm-gpt
- **アプローチ:** GPT を用いた Overpass QL 生成。ユーザーが自然言語で地図を探索できる UI

## 4. LLM-Geo / Autonomous GIS (2023-05)

- **論文:** [Autonomous GIS: the next-generation AI-powered GIS](https://arxiv.org/abs/2305.06453) — Tang et al.
  - 拡張版: https://www.tandfonline.com/doi/full/10.1080/17538947.2023.2278895 (2023-11)
- **リポジトリ:** https://github.com/gladcolor/LLM-Geo
- **概要:** LLM が GIS 操作を自律的に計画・実行する「Autonomous GIS」コンセプトを提唱。コード生成 → 実行 → 自己修正のループ
- **アプローチ:** GPT-4 による Python GIS コード生成。Overpass QL は副産物的に使用
- **重要性:** 「LLM が GIS エージェントになれる」という方向性を示した先駆的論文

## 5. LLM-Find / AutonomousGIS_GeodataRetrieverAgent (2024-05/07)

- **論文:** [An Autonomous GIS Agent Framework for Geospatial Data Retrieval](https://arxiv.org/abs/2407.21024) — Ning et al.
- **リポジトリ:** https://github.com/gladcolor/LLM-Find / https://github.com/Teakinboyewa/AutonomousGIS_GeodataRetrieverAgent
- **概要:** 地理データ取得に特化した自律 GIS エージェント。OSM, Census, OpenTopography 等の複数 API を横断的に利用
- **アプローチ:** LLM が適切な API とパラメータを選択し、Overpass QL を含むクエリを生成
- **OSM 取得との関連:** Overpass QL 生成を「ツールの一つ」として扱う点で本プロジェクトと重なる

## 6. Geode (2024-06)

- **論文:** [Geode: A Zero-shot Geospatial Question-Answering Agent](https://arxiv.org/abs/2407.11014) — Gupta et al.
- **リポジトリ:** https://github.com/devashish-gupta/Geode
- **概要:** 明示的推論と精確な時空間取得を持つゼロショット地理空間 QA エージェント
- **アプローチ:** LLM による推論連鎖 + Overpass API / その他地理データソースとの統合
- **特徴:** 回答生成まで含めたエンドツーエンドの QA。本プロジェクトはクエリ生成に特化

## 7. GeoQAMap (2023-09)

- **論文:** [GeoQAMap - Geographic Question Answering with Maps Leveraging LLM and Open Knowledge Base](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.GIScience.2023.28)
- **概要:** LLM と OpenStreetMap を組み合わせた地理的 QA システム。地図上での回答可視化を含む
- **アプローチ:** LLM が質問を解釈し、OSM クエリを生成して地図上で回答を表示

## 8. ChatGeoAI (2024-10)

- **論文:** [ChatGeoAI: Enabling Geospatial Analysis for Public through Natural Language, with Large Language Models](https://www.mdpi.com/2220-9964/13/10/348)
- **概要:** 一般ユーザー向けに自然言語で地理空間分析を可能にするシステム
- **アプローチ:** LLM を用いた Overpass QL + 空間分析コード生成

---

## text2geoql-dataset との差異まとめ

| プロジェクト | Few-Shot | Fine-tuning | 合成データ | TRIDENT 中間言語 | Nominatim 地名解決 | 評価データセット |
|------------|---------|------------|----------|---------------|-------------------|---------------|
| ChatGeoPT | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| osm-ai-map | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| LLM-Geo | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| LLM-Find | ✓ | ✗ | ✗ | ✗ | ✗ | 限定的 |
| Geode | ✓ | ✗ | ✗ | ✗ | ✗ | 限定的 |
| **text2geoql** | ✓ | **目標** | **✓** | **✓** | **✓** | **✓ (6415+件)** |

**本プロジェクトの独自性:** 上記のいずれも Fine-tuning 用の合成データセット構築には取り組んでいない。TRIDENT 中間言語と自動検証付き合成データ生成は本プロジェクト固有の貢献。
