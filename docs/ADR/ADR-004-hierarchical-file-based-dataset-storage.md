# ADR-004: OSM タグスキーマに準拠した階層ファイルベースのデータセット構造

## ステータス
Accepted

## コンテキスト

6,000 件以上の入力命令と 2,000 件以上のクエリを管理するストレージ方式を決める必要があった。候補：

1. **SQLite / RDB**: 全データをデータベースに格納
2. **JSON Lines / CSV**: フラットなテキストファイル
3. **階層ファイルシステム**: ディレクトリ構造でデータを整理

また、データの整理軸として何を使うかも決める必要があった：
- 地名（国 → 都市 → 区）
- 関心事の種類（cafes, hotels, parks...）
- OSM タグスキーマ（amenity, tourism, shop...）

このシステムは GitHub 上で公開されており、人間がブラウズしたり、`git diff` でデータの変化を確認できることも重要だった。

## 決定

**OSM タグスキーマ × 地名階層のファイルシステム構造**を採用する。

### ディレクトリ構造

```
data/
├── concerns/                       # 関心事（POI タイプ）軸
│   ├── amenity/                    # OSM タグ: amenity=*
│   │   ├── cafe/                   # amenity=cafe
│   │   │   ├── Japan/
│   │   │   │   └── Tokyo/
│   │   │   │       ├── Shinjuku/
│   │   │   │       │   ├── input-trident.txt
│   │   │   │       │   ├── output-qwen2.5-coder-14b.overpassql
│   │   │   │       │   └── output-qwen2.5-coder-14b.meta.json
│   │   │   │       └── Taito/
│   │   │   └── South Korea/
│   │   │       └── Seoul/
│   │   ├── restaurant/
│   │   │   └── cuisine/            # サブタグ対応
│   │   │       └── ramen/
│   │   ├── hospital/
│   │   └── ...
│   ├── tourism/
│   │   ├── hotel/
│   │   ├── museum/
│   │   └── ...
│   ├── shop/
│   ├── leisure/
│   ├── railway/
│   └── ...
└── administrative/                 # 行政区域軸（SubArea 展開用）
    ├── Japan/
    ├── South Korea/
    └── ...
```

### 各エントリのファイル

```
{concern}/{country}/{city}/{district}/
├── input-trident.txt               # 入力: TRIDENT 命令（必須）
├── output-{model-slug}.overpassql  # 成功出力: OverpassQL クエリ（0 件以上）
├── output-{model-slug}.meta.json   # 成功メタデータ: 生成プロベナンス
└── not-found-{model-slug}.json     # 失敗記録: 失敗理由（成功ファイルがない場合）
```

`{model-slug}` の例: `qwen2.5-coder-14b`、`qwen3-8b`

### ファイル命名規則

- **入力**: `input-trident.txt`（固定名）
- **成功出力**: `output-{slug}.overpassql`
- **成功メタ**: `output-{slug}.meta.json`
- **失敗記録**: `not-found-{slug}.json`
- **スラッグ変換**: `model_to_slug("qwen2.5-coder:14b")` → `"qwen2.5-coder-14b"`（`:` と `/` を `-` に変換）

## 根拠

- **OSM タグスキーマとの一致**: `amenity/cafe/`、`tourism/hotel/` というパスは OSM タグ `amenity=cafe`、`tourism=hotel` を直接反映する。関心事を追加するときに OSM タグ体系を参照するだけでよい
- **複数モデル出力の共存**: `output-{slug}.overpassql` というネーミングにより、同じ `input-trident.txt` に対して複数モデルの出力を同一ディレクトリに保持できる
- **イデンポテントな生成**: `output-{slug}.overpassql` が存在すれば再生成をスキップできる
- **Git フレンドリー**: 1 ファイル = 1 エントリなので `git diff` でデータの変化が追いやすい。大量の変更も `git add data/concerns/amenity/cafe/` のように範囲を絞れる
- **HuggingFace 公開時の変換**: `compile.py` がディレクトリツリーを歩いて `{input, output}` ペアに変換する

## 結果

**ポジティブ：**
- 6,000 件以上のエントリを見通しよく管理できる
- `find_orphan_trident.py` でまだ生成されていないエントリを効率よく発見できる
- 関心事を新規追加するとき（新しい `good_concerns.yaml` エントリ）、ディレクトリを追加するだけでよい
- Makefile で `make cafe` `make hotel` のように関心事単位でバッチ生成できる

**ネガティブ：**
- パスにスペースや特殊文字を含む地名（"Gangnam-gu", "Itaewon-dong" 等）でシェルスクリプトが扱いにくくなる（`xargs -I{}` の引数引渡しに工夫が必要）
- ディレクトリ数が多い（6,000 以上）ため、`os.walk` の速度が問題になりうる
- 同じ地名が異なるスペリングで登録されるリスク（→ ADR-007 で Nominatim による名寄せで対応）

## 補足

実装: `src/generate_trident.py`（ファイル作成）、`src/find_orphan_trident.py`（未生成発見）、`src/compile.py`（HuggingFace 変換）
設定: `good_concerns.yaml`（関心事 → パスのマッピング）
