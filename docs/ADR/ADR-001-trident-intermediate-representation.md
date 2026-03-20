# ADR-001: TRIDENT 中間表現の採用

## ステータス
Accepted

## コンテキスト

### TRIDENT システムとは

**TRIDENT** は、自然言語の対話から OpenStreetMap のインタラクティブ地図を生成する AI システムである（[リポジトリ](https://github.com/yuiseki/TRIDENT)）。ユーザーが「新宿のカフェを見せて」と言うと、TRIDENT は Overpass API でデータを取得し、地図上に可視化する。

TRIDENT のアーキテクチャは**三層構造**に分解されている：

```
Surface layer（表層）
  役割: ユーザーとの対話を管理し、地図生成が可能なリクエストかを判断する
  入力: 自然言語
  出力: ability（"overpass-api" / "ask-more" / "apology"）+ 応答メッセージ
  ↓
Inner layer（中層）
  役割: 対話履歴を分析し、TRIDENT 中間言語を記述する
  入力: 対話履歴
  出力: TRIDENT 中間言語表現
  ↓
Deep layer（深層）
  役割: TRIDENT 中間言語を読み取り、Overpass QL を記述する
  入力: TRIDENT 中間言語表現
  出力: Overpass QL クエリ
  ↓
Overpass API → GeoJSON → インタラクティブ地図
```

### なぜ三層に分解したか

この設計は **text-davinci-003 時代の制約**から生まれた。GPT-3.5-turbo 以前の弱いモデルでも動かす必要があり、「自然言語 → Overpass QL」を一度に解かせると精度が出なかった。タスクを三つの単純なサブ問題に分割し、それぞれを Few-Shot 例で誘導することで実現した。

現在のフロンティアモデルではこの分業は不要だが、以下の環境ではいまだに実用的である：
- エアギャップ環境（インターネット接続なし）
- Raspberry Pi 4B（8 GB RAM）などの極度にリソース制約された環境

### text2geoql-dataset の役割

このリポジトリは **Deep layer の特化型 Fine-tuning** を目的としている。≤ 1.1B パラメータの超小型 LLM を「TRIDENT 中間言語 → Overpass QL」タスクに特化して訓練することで、Raspberry Pi 4B 上でも TRIDENT Deep layer が動作するモデルを作ることが野心的な目標である。

---

## 決定

**TRIDENT 中間言語の `AreaWithConcern` 形式**をこのデータセットの入力表現として採用する。

### TRIDENT 中間言語の完全なフォーマット

Inner layer が出力する中間言語は以下の構造を持つ：

```
ConfirmHelpful: [ユーザーの言語での確認メッセージ]
TitleOfMap: [地図のタイトル]
Area: [地名（小→大の順）]
AreaWithConcern: [地名（小→大の順）]; [関心事]
EmojiForConcern: [関心事], [絵文字]
ColorForConcern: [関心事], [色名]
```

具体例：

```
ConfirmHelpful: 地図を作成しました。他にご要望はありますか？
TitleOfMap: 東京のラーメン店
Area: Taito, Tokyo
Area: Bunkyo, Tokyo
AreaWithConcern: Taito, Tokyo; Ramen shops
AreaWithConcern: Bunkyo, Tokyo; Ramen shops
EmojiForConcern: Ramen shops, 🍜
ColorForConcern: Ramen shops, lightyellow
```

### このデータセットが扱う行

このデータセットは中間言語全体ではなく、Deep layer への入力となる**2種類の行**を扱う：

| 行タイプ | 例 | 用途 |
|---------|----|----|
| `AreaWithConcern: <地名>; <関心事>` | `AreaWithConcern: Shinjuku, Tokyo, Japan; Cafes` | POI クエリの大半 |
| `Area: <地名>` | `Area: Taito, Tokyo, Japan` | 行政区域の境界クエリ |

### TRIDENT ファイルの命名

このリポジトリでは上記の行を `input-trident.txt` として保存する。"TRIDENT" はこのフォーマットの出所（TRIDENT システムの Inner layer）を明示するための命名である。

### パース関数（`src/trident.py`）

```python
parse_filter_type(instruct)    # "AreaWithConcern" / "Area" / "SubArea"
parse_filter_concern(instruct) # "Cafes", "Ramen shops", ...
parse_filter_area(instruct)    # "Shinjuku"（最小地名単位）
area_path_from_trident(inst)   # "Japan/Tokyo/Shinjuku"（ファイルパス用逆順）
```

## 根拠

- **既存システムとの一貫性**: TRIDENT Inner layer がすでにこの形式を出力している。新しいフォーマットを設計する必要がない
- **LLM への Few-Shot 例として使いやすい**: 1行で完結するため、プロンプトに多数の例を埋め込める
- **ファイルシステムとのマッピングが容易**: 地名部分を逆転してディレクトリパスに変換できる（ADR-004）
- **パースが単純**: `split(": ", 1)` と `split("; ", 1)` で分解できる。LLM 時代以前の単純なパーサーで扱える
- **Fine-tuning のターゲットが明確**: `input-trident.txt` → `output-*.overpassql` の 1:1 対応が Fine-tuning の訓練ペアになる

## 結果

**ポジティブ：**
- `src/trident.py` の純粋関数群は副作用なしで完全にユニットテスト可能
- Few-Shot プロンプトに自然に組み込める
- `generate_trident.py` による自動生成（地名 × 関心事のクロスプロダクト）が可能

**ネガティブ：**
- 地名の表記ゆれ（"Shinjuku" vs "新宿"）はこのフォーマットでは解決できない（→ ADR-007 で Nominatim により対応予定）
- 自然言語概念の曖昧さ（「病院」= hospital + clinic + doctors）はこの形式では表現できない（→ ADR-009）
- 現在は英語地名・英語関心事名のみを想定しており、他言語対応は未検討

## 補足

実装: `src/trident.py`
テスト: `tests/test_trident.py`
TRIDENT リポジトリ: https://github.com/yuiseki/TRIDENT

地名逆転ロジック（`area_path_from_trident`）：
```
"Shinjuku, Tokyo, Japan"
→ ["Shinjuku", "Tokyo", "Japan"]
→ reversed → ["Japan", "Tokyo", "Shinjuku"]
→ os.path.join → "Japan/Tokyo/Shinjuku"
```
