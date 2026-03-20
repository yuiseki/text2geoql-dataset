# RS-006: OpenStreetMap 特化 NLP / LLM 研究

text2geoql-dataset が扱う「OSM データに対する NLP・LLM の適用」に特化した研究群。
汎用地理空間 AI は除外し、OpenStreetMap に固有の研究のみを対象とする。

---

## 1. Text-to-OverpassQL の後継研究（最重要）

### OsmT: Tag-Aware Language Models for Text-to-OverpassQL (2024-12)

- **arXiv:** https://arxiv.org/abs/2512.04738
- **概要:** OverpassNL データセットに対するオープンソースモデルの Fine-tuning + **Tag Retrieval Augmentation (TRA)** の提案
- **TRA の仕組み:** 推論時に関連する OSM タグ知識（Taginfo / OSM Wiki）を動的に検索してプロンプトに注入
- **成果:** OQS 75.5（GPT-4 + sBERT 検索の 73.2 を上回る）
- **text2geoql との関係:**
  - TRA は text2geoql-dataset の Few-Shot プロンプトに Taginfo 知識を注入するアイデア（ADR-008）と本質的に同じ問題意識
  - ただし OsmT は OverpassNL の複雑なクエリが対象；text2geoql は AreaWithConcern の POI 検索に特化

### SPOT v1: Natural Language Interface for Geospatial Searches in OSM (2023-11)

- **arXiv:** https://arxiv.org/abs/2311.08093
- **概要:** 自然言語でOSMフィーチャーを検索する最初の SPOT システム

### SPOT v2: Bridging NL and Geospatial Search for Investigative Journalists (2025)

- **arXiv:** https://arxiv.org/abs/2506.13188
- **ACL Demo 2025:** https://aclanthology.org/2025.acl-demo.8.pdf
- **概要:** 調査報道記者向けの OSM 自然言語検索フルスタックオープンソースシステム
- **アプローチ:** LLaMA-3 を **合成生成した OSM 特化学習データ**で Fine-tuning
  - OSM タグの不整合・LLM ハルシネーション・ノイズ入力に対処
- **text2geoql との関係:**
  - **合成データで LLM を OSM 検索用に Fine-tuning する**という本プロジェクトの根幹的アプローチと完全に一致する
  - ただし SPOT v2 は investigative journalism（特定の構造物・施設の特定）が対象；text2geoql は AreaWithConcern の POI 一覧取得が対象
  - SPOT v2 は 2025 年の研究であり、text2geoql-dataset の着想（2023-05 TRIDENT）より後発

### NL-to-Overpass Multi-Step Task Decomposition (IEEE, 2025)

- **IEEE Xplore:** https://ieeexplore.ieee.org/document/11058453/
- **概要:** NL と Overpass QL の構造的ミスマッチを「タスク分解 + Key-Value Correction Module」で解決
- **アプローチ:** クエリ生成を複数ステップに分解し、OSM のタグキー・バリューペアの照合を専用モジュールで補正
- **text2geoql との関係:**
  - batch-generation-report で観察したタグ誤り問題（`amenity=mosque` ではなく `amenity=place_of_worship` + `religion=muslim`）への対処として、同様のアプローチが有効な可能性

---

## 2. OSM データに特化した LLM Fine-tuning

### CHATMAP: LLM Interaction with Cartographic Data (2023-10)

- **arXiv:** https://arxiv.org/abs/2310.01429
- **概要:** OSM データから合成データセットを構築し、**1B パラメータの LLM を LoRA + 8-bit 量子化で Fine-tuning**する最初の PoC
- **アプローチ:** 教師モデル（大型 LLM）が OSM の都市データから Q&A ペアを生成 → 1B モデルを Fine-tuning → 都市の観光・ビジネス Q&A に活用
- **text2geoql との関係:**
  - **「合成データ生成 → 小型モデル Fine-tuning」というパイプラインが完全に一致する**
  - CHATMAP は都市単位の Q&A；text2geoql は AreaWithConcern クエリ生成という違い
  - CHATMAP は 1B モデル実証済み — text2geoql の ≤1.1B Fine-tuning 目標の実現可能性を支持する重要な先行事例

### osmAG + LLM for Robot Navigation (2024-03)

- **arXiv:** https://arxiv.org/abs/2403.08228
- **GitHub:** https://github.com/xiefujing/llm-osmag-comprehension
- **概要:** OSM フォーマットの Area Graph（室内外ロボットナビ用）から学習データを構築し、LLaMA2-7B を Fine-tuning
- **成果:** Fine-tuning 後の LLaMA2-7B が ChatGPT-3.5 を地図トポロジー理解で上回る（成功率 >90%）
- **text2geoql との関係:** OSM XML 形式を LLM 入力表現として利用するアプローチ。Overpass QL ではなく OSM 構造理解が対象

### GeoLLM: Extracting Geospatial Knowledge from LLMs (ICLR 2024)

- **arXiv:** https://arxiv.org/abs/2310.06213
- **概要:** OSM の近傍フィーチャーをコンテキストとして LLM に注入し、社会経済指標予測を Fine-tuning
- **text2geoql との関係:** LLM が OSM タグ知識（`amenity=hospital` 等）を保有しているという前提が共通。目的は異なる（クエリ生成 vs 社会経済予測）

### CityFM: City Foundation Models (CIKM 2024)

- **arXiv:** https://arxiv.org/abs/2310.00583
- **概要:** OSM データのみを使い、外部ラベル不要の自己教師あり Foundation Model を訓練。空間・視覚・テキスト（OSM タグ）のマルチモーダル表現
- **text2geoql との関係:** OSM タグのテキストを LLM で処理する先行事例

---

## 3. OSM タグのセマンティクスと知識構造

### Enriching Building Function Classification Using LLM Embeddings of OSM Tags (Springer 2024)

- **DOI:** https://link.springer.com/article/10.1007/s12145-024-01463-8
- **概要:** OSM タグ（キー・バリューペアのテキスト）を LLM 埋め込みで表現し、建物用途分類の精度を向上
- **成果:** LLM 埋め込みが one-hot 表現より +6.2%、物理/空間指標のみより +12.5% F1 向上
- **text2geoql との関係:** **LLM は OSM タグのセマンティクスを理解している**という本プロジェクトの根本前提を実証的に支持する

### MapQA: Open-Domain Geospatial QA on OSM Data (2025-03)

- **arXiv:** https://arxiv.org/abs/2503.07871
- **概要:** OSM から 3,154 件の Q&A ペアを構築（175 地理エンティティタイプ、空間推論必要）。LLM の SQL 生成 vs 検索ベース手法を比較評価
- **text2geoql との関係:** OSM ベースの評価データセット構築という観点で参考になる

---

## 4. OSM オントロジーと知識グラフ化

### WorldKG (CIKM 2021)

- **arXiv:** https://arxiv.org/abs/2109.10036
- **概要:** OSM を形式的知識グラフに変換（1億+ エンティティ、8億+ トリプル）。Wikidata/DBpedia クラス階層と整合させた Neural Schema Alignment を用いる
- **神経スキーマ整合:** https://arxiv.org/abs/2107.13257
- **text2geoql との関係:** good_concerns.yaml が扱う「OSM タグ → 概念のマッピング」問題は WorldKG が扱う「OSM タグ → 知識グラフクラスのマッピング」問題と本質的に同型

### OSMonto: An Ontology of OSM Tags (2011, 基礎的)

- **概要:** OSM タグを OWL オントロジーとして形式化した先駆的論文
- **text2geoql との関係:** good_concerns.yaml は OSMonto に相当する軽量な「用途特化オントロジー」と捉えられる

---

## 5. Nominatim・地名解決の改善

### Toponym Resolution Leveraging Lightweight Open-Source LLMs and Geo-Knowledge (IJGIS 2024)

- **DOI:** https://www.tandfonline.com/doi/full/10.1080/13658816.2024.2405182
- **GitHub:** https://github.com/uhuohuy/LLM-geocoding
- **概要:** Mistral 7B を地名曖昧性解消で Fine-tuning。Nominatim を解決パイプラインの中核コンポーネントとして使用
- **成果:** Accuracy@161km = 0.91（GENRE 比 +17%）
- **text2geoql との関係:** text2geoql の Nominatim 利用（地名 → OSM relation ID 解決）と問題意識が近い

---

## text2geoql-dataset との位置づけ整理

| 研究 | 合成データ | 小型 Fine-tuning | OSM タグ特化 | TRIDENT 中間言語 | 自動検証 |
|-----|----------|----------------|-----------|---------------|---------|
| OverpassNL | ✗ | ✗ (T5) | ✓ | ✗ | ✗ |
| OsmT | ✗ | ✓ (small) | ✓ (TRA) | ✗ | ✗ |
| SPOT v2 | ✓ | ✓ (LLaMA-3) | ✓ | ✗ | ✗ |
| CHATMAP | ✓ | ✓ (1B) | ✓ | ✗ | ✗ |
| **text2geoql** | **✓** | **✓ (≤1.1B 目標)** | **✓** | **✓ (固有)** | **✓ (Overpass API)** |

### 最重要な競合・関連研究

1. **SPOT v2 (ACL 2025)** — 合成データで LLM を Fine-tuning する点で最も近い。ただし目的・中間言語設計・自動検証パイプラインは異なる
2. **OsmT (arXiv 2024-12)** — Tag Retrieval Augmentation が ADR-008 と同じ問題を解く
3. **CHATMAP (2023)** — 1B モデルを OSM 合成データで Fine-tuning する PoC として本プロジェクトの実現可能性を支持

### text2geoql-dataset の独自貢献（再確認）

- **TRIDENT 中間言語** は上記いずれの研究にも存在しない
- **Overpass API による実行結果検証付き合成データ**（空クエリ排除）は SPOT v2 を含め明示的に報告した先行研究がない
- **6,415+ ペアの公開データセット**として最大規模（OverpassNL の約 2 倍）
