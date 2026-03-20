# RS-001: Text-to-OverpassQL — 最直接の先行研究

## 概要

**OverpassNL / Text-to-OverpassQL** (Schifferle et al., 2023) は、自然言語から Overpass QL を生成するタスクを初めて体系的に定式化した論文であり、text2geoql-dataset の最も直接的な先行研究である。

- **論文:** [Text-to-OverpassQL: A Natural Language Interface for Complex Geodata Querying of OpenStreetMap](https://arxiv.org/abs/2308.16060)
  - TACL 掲載版: https://direct.mit.edu/tacl/article/doi/10.1162/tacl_a_00654
- **コード・データ:** https://github.com/raphael-sch/OverpassNL
- **発表:** 2023-08-30 (arXiv), 2024-04-30 (TACL)

---

## アプローチ

| 項目 | OverpassNL |
|------|-----------|
| モデル | T5 (fine-tuned) |
| データ収集 | クラウドソーシング（Mechanical Turk）による NL-Overpass QL ペア |
| データ量 | ~3,000 ペア |
| 中間表現 | なし（NL → Overpass QL 直接） |
| 合成データ | なし |
| 推論方式 | Fine-tuning |
| 対象クエリ | 複雑な空間クエリ（周辺検索・面積フィルタ等含む） |

---

## text2geoql-dataset との差異

| 観点 | OverpassNL | text2geoql-dataset |
|------|-----------|-------------------|
| 中間言語 | なし | **TRIDENT** による意味的な中間表現 |
| データ生成 | 人手クラウドソーシング | **LLM + Overpass API による合成データ** |
| 推論方式 | Fine-tuning (T5) | **Few-Shot + Fine-tuning (≤1.1B 目標)** |
| スケール | ~3,000 ペア | 6,415+ ペア（継続拡張中） |
| 地名解決 | クエリ内の文字列マッチ | **Nominatim による area(id) グラウンディング** |
| 対象クエリ | 複雑な空間クエリ中心 | **AreaWithConcern (POI 検索)** に特化 |
| ターゲットデバイス | サーバー | **Raspberry Pi 4B 向け ≤1.1B** |

---

## 主な知見（論文から）

- T5-base の fine-tuning で、Few-Shot GPT-3 より高い精度を達成
- Overpass QL は SQL と異なり area フィルタリング等の独自構文が多く、モデルの学習難易度が高い
- クラウドソーシングデータの品質ばらつきが課題

---

## text2geoql-dataset へのインプリケーション

- OverpassNL は「複雑なクエリ」を扱うが、我々の AreaWithConcern は「シンプルだが多様な地名×コンサーン組み合わせ」に特化しており、直接競合ではなく補完的な位置づけ
- OverpassNL がクラウドソーシングに頼るのに対し、**LLM + Overpass API による自動検証付き合成データ生成**は本プロジェクトの独自貢献
- TRIDENT 中間言語は OverpassNL にはない概念であり、本プロジェクトの核心的な新規性
