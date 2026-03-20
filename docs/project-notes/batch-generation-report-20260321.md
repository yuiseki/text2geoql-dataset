# バッチ生成レポート (2026-03-21)

**実行日時:** 2026-03-20 23:04 〜 2026-03-21 01:17 JST
**モデル:** qwen2.5-coder:3b (temperature=0.01, num_predict=256)
**対象:** 未生成の AreaWithConcern エントリ全件

---

## 実行結果サマリー

| 項目 | 値 |
|-----|---|
| 処理件数 | 2,803件 |
| 成功 (output あり) | 476件 (17%) |
| 失敗 (not-found) | 2,327件 (83%) |
| 失敗内訳 | zero_results: 2,098 / その他: 229 |
| 所要時間 | 133分 |
| 処理速度 | 21.1件/分 |
| データセット総数 | 2,294 → **2,770件** (+476件) |

---

## concern 別の成功率

| Concern | 成功 | 失敗 | 成功率 |
|---------|------|------|-------|
| Train Stations | 18 | 9 | 67% |
| Churches | 35 | 20 | 64% |
| Hospitals | 17 | 13 | 57% |
| University campuses | 76 | 60 | 56% |
| Cafes | 16 | 13 | 55% |
| Bars | 15 | 15 | 50% |
| Temples | 26 | 31 | 46% |
| Sushi shops | 54 | 69 | 44% |
| Pizza shops | 78 | 112 | 41% |
| Parks | 10 | 22 | 31% |
| Hotels | 7 | 16 | 30% |
| Ramen shops | 23 | 67 | 26% |
| Museums | 7 | 21 | 25% |
| Galleries | 6 | 25 | 19% |
| Shelters | 6 | 25 | 19% |
| Theme parks | 26 | 133 | 16% |
| Zoos | 19 | 147 | 11% |
| Burger shops | 19 | 189 | 9% |
| Aquariums | 2 | 32 | 6% |
| Castles | 9 | 194 | 4% |
| Convenience stores | 1 | 23 | 4% |
| Shrines | 2 | 54 | 4% |
| Embassies | 2 | 202 | 1% |
| Mosques | 1 | 202 | 0% |
| Soba noodle shops | 1 | 207 | 0% |
| Airports | 0 | 197 | 0% |

---

## 失敗の類型

### 1. タグ誤り（モデルの知識不足）

クエリは生成されたが OSM 上で 0件を返した。正しい OSM タグへの対応が学習されていない。

| Concern | モデルが生成したタグ | 正解タグ |
|---------|----------------|---------|
| Airports | `nwr["aerport"]` | `nwr["aeroway"="aerodrome"]` |
| Soba noodle shops | `nwr["shop"="soba"]` | `nwr["amenity"="restaurant"]["cuisine"="soba"]` |
| Embassies | `nwr["building"="embassy"]` | `nwr["amenity"="embassy"]` |
| Mosques | `nwr["amenity"="mosque"]` | `nwr["amenity"="place_of_worship"]["religion"="muslim"]` |

Airports のケースは `aerport` というタイポまで含まれており、正しい Few-Shot 例示がなければモデルが推測で誤タグを生成することを示す。

### 2. 地理的スケール不一致（legitimate な zero_results）

POI が対象エリア内に実在しない。主にレアな施設を小さい行政区単位で検索しているケース。

| Concern | 理由 |
|---------|------|
| Zoos / Theme parks / Aquariums | 都市に数個しか存在せず、区・郡レベルのエリアでは 0件が多い |
| Castles | 特定の地域（日本・欧州の城下町）に集中 |
| Shrines | 日本以外では存在しない |
| Airports | 都市圏に 1〜数個。区レベルのエリアでは大半が 0件 |
| Burger shops (一部) | OSM へのタギングが疎な地域（途上国など）では実在しても未登録 |

### 3. 成功例の分析

成功率が高い concern の共通点：
- **Train Stations (67%), Hospitals (57%), Cafes (55%)** — どの都市のどの区にも普遍的に存在する
- **University campuses (56%)** — 大学は面的に広く、OSM でのカバレッジが高い
- **Pizza shops (41%), Sushi shops (44%)** — 都市部では世界中に普及しているが、地方・小都市では 0件

---

## 考察と次のアクション

### タグ誤り問題への対処

4件のタグ誤りはいずれも Few-Shot 例がない（または少ない）concern に起きている。

**対処案:**
1. **good_concerns.yaml の見直し**: 成功率 10% 未満の concern（Airports, Soba, Embassies, Mosques）は生成対象から外すか、正しいタグを prompt に明示
2. **データ追加**: 少なくとも各 concern に都市レベル（区ではなく市）での検証済みペアを追加し、Few-Shot に乗るようにする
3. **Taginfo 検証**: 生成クエリのタグが Taginfo に存在するか確認してから Overpass に投げる（ADR-008 参照）

### 地理的スケール問題への対処

Zoos / Theme parks / Airports のような「都市スケール施設」に対して区・郡レベルのエリア指定は本質的に成功しにくい。

**対処案:**
1. **seed area の見直し**: こういった concern には区レベルではなく市・県レベルの seed area のみを使う
2. **concern と area スケールのマッチング**: `good_concerns.yaml` に推奨スケール（ward / city / prefecture）を付与する仕組みを検討

### 成功件数 476 の内訳

最も多く生成できた concern:
- Pizza shops: 78件、University campuses: 76件、Sushi shops: 54件

これらは world-wide に存在する POI であり、多様な地域での例が得られたことで Few-Shot の質が高まっている。Fine-tuning 時に特に有効な training signal になると期待される。

---

## 残タスク

- 1,048件の未処理エントリ（administrative = `Area:` 形式のため batch_generate がスキップ）は AreaWithConcern ではないので無視でよい
- タグ誤りの多い concern（Airports, Soba, Embassies）に対して手動で正解クエリを追加するか、good_concerns.yaml から除外するかを検討
