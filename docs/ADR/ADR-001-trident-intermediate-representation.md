# ADR-001: TRIDENT 中間表現の採用

## ステータス
Accepted

## コンテキスト

text2geoql-dataset はテキストから Overpass QL クエリへの変換のための学習データを生成するシステムである。入力となる「地理空間クエリの意図」を表現するにあたって、以下の選択肢があった：

1. **自然言語をそのまま入力とする**: "Show me cafes in Shinjuku, Tokyo" のような文
2. **構造化 JSON/YAML**: `{"type": "amenity", "value": "cafe", "area": "Shinjuku, Tokyo, Japan"}`
3. **TRIDENT 形式**: `AreaWithConcern: Shinjuku, Tokyo, Japan; Cafes`

自然言語は表現のブレが大きく（「カフェ」「喫茶店」「coffee shop」など）、LLM による生成やデータセットの管理が困難になる。一方で完全な構造化 JSON はファイルパスや管理が重くなる。

また、データセットのファイルシステム上の整理（どのディレクトリにどのファイルを置くか）と、LLM への入力フォーマットを統一する必要があった。

## 決定

**TRIDENT（Text Representation for Instructed Dataset ENTries）形式** を中間表現として採用する。

TRIDENT は以下の 3 種類の命令タイプを持つ：

```
# 地名 × 関心事の組み合わせ（最も頻出）
AreaWithConcern: <地名（小→大の順）>; <関心事>
例: AreaWithConcern: Shinjuku, Tokyo, Japan; Cafes

# 地名のみ（行政区域の探索用）
Area: <地名（小→大の順）>
例: Area: Taito, Tokyo, Japan

# サブエリア展開（行政区域の下位探索用）
SubArea: <地名>
例: SubArea: Tokyo, Japan
```

**構文規則：**
- 地名は「最小単位, ..., 国名」の順（人間の読みやすさ優先）
- ファイルパスは逆順（`Japan/Tokyo/Shinjuku/`）で階層を表す
- セミコロンで地名と関心事を区切る
- パース関数は `src/trident.py` に集約（純粋関数）

## 根拠

- **機械可読性と人間可読性の両立**: TRIDENT は構造化されているが、プレーンテキストとして自然に読める
- **LLM への Few-Shot 例として使いやすい**: 1行で完結するため、プロンプトに多数の例を埋め込める
- **ファイルシステムとのマッピングが容易**: `area_path_from_trident()` で地名部分を逆転してディレクトリパスに変換できる
- **パースが単純**: Python の `split(": ", 1)` と `split("; ", 1)` だけで分解できる
- **拡張性**: 新しい命令タイプを追加しても既存のパーサーに影響しない

## 結果

**ポジティブ：**
- データセットの各エントリが `input-trident.txt` 1ファイルで完結し、管理が容易
- `src/trident.py` の純粋関数群は副作用なしで完全にユニットテスト可能
- Few-Shot プロンプトに自然に組み込める（`Input:\n{trident}\n\nOutput:\n```\n{overpassql}\n```)`
- `generate_trident.py` による自動生成（地名 × 関心事のクロスプロダクト）が可能

**ネガティブ：**
- 独自フォーマットのため、外部システムとの連携には変換レイヤーが必要
- 地名の表記ゆれ（"Shinjuku" vs "新宿"）はこのフォーマットでは解決できない（→ ADR-007 で Nominatim を使った名寄せで対応予定）
- 現在は英語地名のみを想定しており、他言語対応は未検討

## 補足

実装: `src/trident.py`
テスト: `tests/test_trident.py`

`area_path_from_trident()` の地名逆転ロジック：
```
"Shinjuku, Tokyo, Japan"
→ split by ", "
→ ["Shinjuku", "Tokyo", "Japan"]
→ reversed → ["Japan", "Tokyo", "Shinjuku"]
→ os.path.join → "Japan/Tokyo/Shinjuku"
```
