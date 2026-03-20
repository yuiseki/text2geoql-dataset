# ADR-007: Nominatim による地名グラウンディングとデータセット拡張

## ステータス
Proposed

## コンテキスト

現在のシステムの最大の強みは「LLM から OSM タグ知識を抽出し、現実の OSM データにグラウンディングさせながらデータセットを合成できること」である。しかし地名の扱いには課題がある：

### 現在の課題

1. **地名の正確性が未保証**: `AreaWithConcern: Shinjuku, Tokyo, Japan; Cafes` という TRIDENT 命令の "Shinjuku" が実際に OSM 上でどう表現されているかを LLM に頼っている
   - LLM は `area["name:en"="Shinjuku"]` と書くかもしれないが、OSM に `name:en=Shinjuku` というタグがない場合 `zero_results` になる
   - `area["name"="新宿区"]` の方が正しいかもしれないが、LLM はそれを知らない

2. **スペリング表記ゆれ**: "Seocho-gu" と "Seocho" は同じ地区を指すが、OSM 上では `name=서초구` / `name:en=Seocho-gu` で管理されている

3. **OSM リレーション ID の未活用**: Overpass API では `area(3453345)` のように OSM リレーション ID で直接エリアを指定できる（最も確実）。しかし現在は name タグで曖昧検索している

4. **データセット拡張の地名カバレッジ**: `generate_trident.py` が生成する地名は既存データから抽出した seeds のみ。Nominatim を使えば任意の地域の行政区域を体系的に列挙できる

### Nominatim API（セルフホスト）

セルフホストの Nominatim インスタンス: `https://nominatim.yuiseki.net/`

```bash
# 例: 渋谷の検索
https://nominatim.yuiseki.net/search.php?q=渋谷&format=json

# 例: 行政区域の検索（structured query）
https://nominatim.yuiseki.net/search.php?city=Shibuya&state=Tokyo&country=Japan&format=json

# 例: リバースジオコーディング
https://nominatim.yuiseki.net/reverse.php?lat=35.6580&lon=139.7016&format=json

# 例: OSM リレーション ID の取得
https://nominatim.yuiseki.net/search.php?q=Shinjuku,Tokyo,Japan&format=json
# → [{"osm_type": "relation", "osm_id": 1234567, "display_name": "...", ...}]
```

## 決定

Nominatim を活用した以下の機能を順次実装する。

---

### Phase 1: `src/nominatim.py` — Nominatim API クライアント

```python
DEFAULT_ENDPOINT = "https://nominatim.yuiseki.net"

def search(query: str, endpoint: str = DEFAULT_ENDPOINT) -> list[dict]:
    """地名文字列から Nominatim 検索結果を返す"""

def get_osm_relation_id(area_name: str, endpoint: str = DEFAULT_ENDPOINT) -> int | None:
    """地名から OSM リレーション ID を返す。見つからなければ None"""

def get_display_name(area_name: str, endpoint: str = DEFAULT_ENDPOINT) -> str | None:
    """地名から OSM 上の正式な display_name を返す"""
```

設計原則（ADR-002 と同様）:
- `endpoint` を引数注入してテスト可能にする
- HTTP エラー・空結果は `None` / 空リストで graceful degradation

---

### Phase 2: Overpass クエリへの OSM 関係 ID 注入

Nominatim で取得した `osm_id`（リレーション）を使って、Overpass クエリを決定論的にする。

**現在の LLM 生成クエリ（不安定）：**
```
area["name:en"="Shinjuku"]->.inner;
```

**Nominatim グラウンディング後（安定）：**
```
area(3600358679)->.inner;  ← OSM リレーション ID からの area 変換
```

Overpass API における `area(id)` の計算:
```
osm_relation_id + 3600000000 = overpass_area_id
# 例: 358679 → 3600358679
```

Few-Shot プロンプトのサンプルにこの形式のクエリを含めることで、LLM も同パターンを学習する。

---

### Phase 3: `generate_trident.py` の地名拡張

Nominatim の `/search` や `/details` を使って、指定国・都市の行政区域を自動列挙する。

```python
def fetch_admin_areas(
    country: str,
    admin_level: int = 8,  # OSM の admin_level（市区町村レベル）
    endpoint: str = DEFAULT_ENDPOINT,
) -> list[str]:
    """Nominatim から指定国の行政区域名を返す"""
```

これにより `generate_trident.py` のシードが「既存データに含まれる地名」だけでなく「OSM 上に存在するすべての行政区域」に拡張できる。

---

### Phase 4: TRIDENT 地名の正規化パイプライン

既存の TRIDENT ファイルに含まれる地名を Nominatim で検証・正規化する。

```
input-trident.txt:  "AreaWithConcern: Seocho, Seoul, South Korea; Cafes"
                                          ↓ Nominatim 検索
nominatim result: osm_id=123456, display_name="서초구, 서울특별시, ..."
                                          ↓ 正規化
normalized:        "AreaWithConcern: Seocho-gu, Seoul, South Korea; Cafes"
                   + nominatim_osm_id: 123456  (メタデータとして保存)
```

---

## 根拠

### なぜ Nominatim か

| 方法 | 精度 | 維持コスト | OSM との一貫性 |
|------|------|-----------|--------------|
| LLM に name タグを推測させる | △ | — | △（知識が古い可能性） |
| Google Maps / 外部ジオコーダー | ○ | 高（課金） | ✗（OSM タグと無関係） |
| **Nominatim（OSM ベース）** | ○ | 低（セルフホスト済み） | **◎（OSM と直結）** |

Nominatim は OSM データから構築されるため、**「OSM 上でこの地名をどう検索するか」の答えをそのまま返す**。Overpass API の `area[name="..."]` パターンよりも、`area(osm_id)` パターンの方が確実であり、Nominatim はその OSM ID を提供できる。

### なぜセルフホストか

- Overpass と同様に大量リクエストが発生するため（ADR-002 と同じ理由）
- `https://nominatim.yuiseki.net/` はすでに運用中
- データの一貫性：Overpass インスタンスと Nominatim インスタンスが同じ OSM データダンプを使えば、地名→ ID→要素の一貫性が保たれる

## 結果

**期待されるポジティブな効果：**
- `zero_results` の失敗率が大幅に低下（地名の name タグ誤りが原因のケースが解消される）
- 新規地域への拡張がセルフサービス化（Nominatim で対象国の行政区域を列挙してシードに追加するだけ）
- Few-Shot プロンプトに `area(osm_id)` パターンが増えることで LLM の出力品質が安定する
- 多言語対応への道が開ける（Nominatim は日本語・韓国語・アラビア語等の地名も返せる）

**ネガティブ・課題：**
- Nominatim のレスポンスは OSM データ更新に依存するため、インデックス更新のタイミングで osm_id が変わることがある
- `area(osm_id)` 形式のクエリは LLM が学習しにくい（Few-Shot 例を充実させる必要がある）
- Phase 1〜4 の段階的実装が必要であり、既存の `generate_overpassql.py` との統合設計が複雑になりうる
- Nominatim の Fuzzy 検索結果が複数候補を返すケース（同名の地名が世界に複数ある）への対処が必要

## 実装計画

```
Phase 1: src/nominatim.py + tests/test_nominatim.py
  - search() / get_osm_relation_id() 関数
  - エンドポイント注入・モックテスト

Phase 2: generate_overpassql.py への統合
  - build_prompt() で TRIDENT の地名を Nominatim で解決し、area(id) 形式に変換
  - Few-Shot サンプルも area(id) 形式で再生成

Phase 3: generate_trident.py への統合
  - fetch_admin_areas() で指定国の行政区域を列挙
  - 既存 seed 抽出を補完

Phase 4: データ正規化スクリプト
  - 既存 TRIDENT ファイルに nominatim_osm_id.json を追加
  - 表記ゆれの統合
```

## 補足

Nominatim API エンドポイント（セルフホスト）: `https://nominatim.yuiseki.net/`

Overpass API における area ID 計算:
```python
def relation_to_area_id(osm_relation_id: int) -> int:
    return osm_relation_id + 3_600_000_000
```

参考: Overpass QL での利用例
```
// 渋谷区 (OSM relation 1234567) のカフェを検索
area(3601234567)->.target;
nwr["amenity"="cafe"](area.target);
out geom;
```
