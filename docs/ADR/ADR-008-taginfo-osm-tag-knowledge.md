# ADR-008: Taginfo API による OSM タグ知識のグラウンディング

## ステータス
Proposed

## コンテキスト

このシステムの根本的な価値命題は「**LLM から OSM タグ知識を抽出し、現実のデータにグラウンディングさせながらデータセットを合成すること**」である。しかし現在は OSM タグ知識の取得・検証が完全に LLM の学習データに依存している：

### 現在の問題

1. **タグの正確性が未保証**: LLM は `amenity=cafe` を知っているが、`cuisine=ramen` や `religion=shinto` などのサブタグを正確に知っているとは限らない。`amenity=coffee_shop`（非標準）のような誤ったタグを生成してもシステムが検知できない

2. **関心事カバレッジの設計が手動**: `good_concerns.yaml` の 28 件の関心事は人手で設定されている。「OSM に実際に使われているタグ」を体系的に把握して設計する仕組みがない

3. **タグの使用頻度が考慮されない**: `amenity=cafe`（数百万件）と `amenity=ice_cream`（数十万件）では実用性が大きく異なるが、データセットの関心事設計にこの情報が活用されていない

4. **タグの組み合わせが不明**: ある施設を検索する際に「どのタグの組み合わせが最も網羅的か」が不明。例えば `leisure=park` だけでなく `landuse=recreation_ground` も公園的な空間を表すが、これらの組み合わせが良いかどうかを LLM が知っているとは限らない

### Taginfo API（セルフホスト）

`https://taginfo.yuiseki.net/` は OSM データを分析し、タグの使用状況・組み合わせ・Wiki 情報を提供するツール。セルフホストインスタンスが既に稼働している。

主要エンドポイント：

```bash
# 特定キーの最頻出値（例: amenity の上位値）
GET /api/4/key/values?key=amenity&sortname=count&sortorder=desc

# 特定タグの統計（使用件数）
GET /api/4/tag/stats?key=amenity&value=cafe

# 特定キーとよく一緒に使われるキー
GET /api/4/key/combinations?key=amenity&value=cafe

# フリーテキスト検索
GET /api/4/search/by_key_and_value?query=cafe

# 人気キー一覧
GET /api/4/keys/popular?sortname=count&sortorder=desc
```

レスポンス形式：
```json
{
  "total": 1234,
  "data": [
    {"value": "cafe", "count": 2345678, "fraction": 0.023, ...},
    ...
  ]
}
```

データスナップショット: 2026-01-29 00:59 UTC（OSM 全データのカウント）

## 決定

Taginfo API を以下の 3 用途で活用する。

---

### 用途 A: `good_concerns.yaml` の自動生成・拡張

現在の手動管理 28 件から、Taginfo による使用頻度ベースの体系的な関心事カタログに移行する。

```python
# src/taginfo.py
DEFAULT_ENDPOINT = "https://taginfo.yuiseki.net"

def get_key_values(
    key: str,
    min_count: int = 10_000,
    endpoint: str = DEFAULT_ENDPOINT,
) -> list[dict]:
    """指定キーの値を使用頻度順に返す（min_count 以上のもの）"""

def get_tag_combinations(
    key: str,
    value: str,
    endpoint: str = DEFAULT_ENDPOINT,
) -> list[dict]:
    """指定タグとよく使われる組み合わせキーを返す"""

def get_tag_stats(
    key: str,
    value: str,
    endpoint: str = DEFAULT_ENDPOINT,
) -> dict:
    """指定タグの総使用件数・ノード/ウェイ/リレーション別内訳を返す"""
```

**活用フロー：**

```
Taginfo /api/4/key/values?key=amenity
→ [cafe: 2.3M, restaurant: 4.1M, hospital: 1.2M, ...]
→ min_count フィルタ（例: 10万件以上）
→ 新しい good_concerns.yaml エントリを自動生成
→ generate_trident.py が新関心事のデータセットを拡張
```

---

### 用途 B: LLM 生成クエリのタグ検証

LLM が生成した OverpassQL に含まれるタグ（`amenity=cafe` 等）を Taginfo で事前検証し、明らかに誤ったタグを弾く。

**現在のフロー：**
```
LLM 生成 → Overpass API 実行 → zero_results（失敗）
```

**Taginfo 検証追加後のフロー：**
```
LLM 生成 → Taginfo タグ検証 → タグ件数 0 なら early failure
                             → タグ件数 > 0 なら Overpass API 実行
```

```python
def validate_tag(
    key: str,
    value: str,
    min_count: int = 1000,
    endpoint: str = DEFAULT_ENDPOINT,
) -> bool:
    """タグが OSM 上に min_count 件以上存在する場合 True"""
    stats = get_tag_stats(key, value, endpoint)
    return stats.get("count", 0) >= min_count
```

これにより `api_error` や `zero_results` の一部をより早い段階で検出でき、Overpass API への無駄なリクエストを削減できる。

---

### 用途 C: Few-Shot プロンプトへのタグ知識注入

現在の Few-Shot プロンプト（ADR-003）は成功した過去クエリの例のみを提示する。Taginfo から取得した「正確なタグ情報」をプロンプトに補足することで、LLM の生成精度を上げられる。

**プロンプト拡張案：**

```
[System Rules]
...
===
Tag Knowledge:
- amenity=cafe: 2,345,678 uses (nodes: 80%, ways: 20%)
  Common combinations: name, opening_hours, cuisine, outdoor_seating
- tourism=hotel: 1,123,456 uses
  Common combinations: name, stars, rooms
===
Examples:
...
```

生成時に TRIDENT の `filter_concern` から対応するタグを Taginfo で引き、プロンプトに動的に挿入する。

---

## 根拠

| 観点 | Taginfo 活用 | 現状 |
|------|-------------|------|
| タグ正確性 | OSM 実データで検証 | LLM 知識に依存 |
| 関心事カバレッジ | 使用頻度ベースで体系化 | 28 件の手動管理 |
| クエリ品質 | 早期エラー検出が可能 | Overpass 実行まで分からない |
| プロンプト品質 | タグ知識を動的に補完 | 例のみ（タグ説明なし） |

Taginfo はセルフホスト済みであり（ADR-002/007 と同様の運用コスト）、追加のインフラ費用は発生しない。API が明確に定義されており、`endpoint` 注入パターン（ADR-002/007 と同様）で実装できる。

## 結果

**期待されるポジティブな効果：**
- `zero_results` 失敗の一部（誤タグによるもの）を Overpass 呼び出し前に検出できる
- 関心事の体系化により、`good_concerns.yaml` の手動メンテナンスが不要になる
- 使用頻度 1 万件以上のタグを自動収録することで、データセットが OSM の実態を反映した網羅的なものになる
- タグの組み合わせ情報（`key/combinations`）から「`amenity=cafe` には `opening_hours` や `cuisine` も一緒に使われる」という知識が得られ、より豊かなクエリ生成につながる

**ネガティブ・課題：**
- Taginfo のデータはスナップショット（月次程度の更新）であり、最新の OSM データとわずかにずれる可能性がある
- タグ件数が多い（`amenity=cafe` が 2M件）からといって、特定地域に存在するかどうかは別問題（Overpass グラウンディングは引き続き必要）
- 用途 C のプロンプト拡張はコンテキスト長を増やすため、小型モデル（3b/8b）のパフォーマンスに影響する可能性がある。Few-Shot 例数を減らすなどのトレードオフが生じうる

## 実装計画

```
Phase 1: src/taginfo.py + tests/test_taginfo.py
  - get_key_values() / get_tag_stats() / get_tag_combinations()
  - エンドポイント注入・モックテスト（ADR-002 の overpass.py と同様の構造）

Phase 2: good_concerns_generator.py または generate_trident.py への統合
  - /api/4/keys/popular と /api/4/key/values を使って
    使用頻度上位の amenity/tourism/shop/leisure タグを収集
  - good_concerns.yaml を自動生成・更新するスクリプト

Phase 3: generate_overpassql.py への検証フック
  - 生成されたクエリから key=value を抽出
  - Taginfo で validate_tag() してカウント 0 なら early failure
  - failure_reason に "invalid_tag" を追加（FailureReason の拡張）

Phase 4: プロンプト拡張（試験的）
  - build_prompt() で filter_concern に対応するタグ情報を Taginfo から取得
  - PROMPT_PREFIX にタグ統計を動的挿入
  - ベンチマークで効果を測定（ADR-006 のフレームワークを活用）
```

## 補足

Taginfo API エンドポイント（セルフホスト）: `https://taginfo.yuiseki.net/`
API ドキュメント: `https://taginfo.yuiseki.net/taginfo/apidoc`
データスナップショット: 2026-01-29 00:59 UTC

関連 ADR：
- ADR-002: Overpass API グラウンディング（Taginfo は補完的に機能する）
- ADR-003: Few-Shot プロンプティング（用途 C で拡張）
- ADR-007: Nominatim 地名グラウンディング（Taginfo はタグ軸、Nominatim は地名軸の担当）

**3 API の役割分担：**

| API | 担当する知識 | 検証対象 |
|-----|------------|---------|
| Overpass API | 現実の OSM 要素データ | クエリが実際に結果を返すか |
| Nominatim | 地名 → OSM リレーション ID | 地名表記の正確性 |
| Taginfo | タグの定義・使用頻度・組み合わせ | タグの正確性・網羅性 |
