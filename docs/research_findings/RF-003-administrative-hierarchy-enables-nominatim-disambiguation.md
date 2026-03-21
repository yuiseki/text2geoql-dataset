# RF-003: 行政階層構造の事前符号化による地名曖昧性解消

**発見日:** 2026-03-21
**カテゴリ:** 地名解決 / 中間言語設計 / 地理的曖昧性

---

## 概要

OpenStreetMap では同一の英語名を持つ行政区画が複数存在する（例: 広島県と広島市はどちらも `name:en=Hiroshima`）。
この曖昧性は **自然言語クエリのみでは大型 LLM でも解決が困難**だが、
text2geoql-dataset のアーキテクチャではデータセット設計の段階でこの問題が解消されている。

---

## 問題の具体例

| 行政区画 | OSM `name:en` | OSM relation ID |
|---------|--------------|----------------|
| 広島県 (Hiroshima Prefecture) | `Hiroshima` | 3218753 |
| 広島市 (Hiroshima City) | `Hiroshima` | 4097196 |

v1 の名前ベースクエリ `area["name:en"="Hiroshima"]` はどちらにもマッチしてしまい、
意図しないスコープで POI を検索するリスクがある。

同様のケース:

| 都道府県 | 政令指定都市 | 共通名 |
|---------|------------|-------|
| 京都府 (id=2137477) | 京都市 (id=357794) | Kyoto |
| 大阪府 (id=341906) | 大阪市 (id=358674) | Osaka |

---

## 解決策: ディレクトリ構造による行政階層の事前符号化

text2geoql-dataset のデータディレクトリ構造は行政階層を明示的に契約している:

```
data/concerns/amenity/cafe/
  Japan/
    Hiroshima Prefecture/          ← 広島県レベル
      Hiroshima/                   ← 広島市レベル
        Naka Ward/                 ← 中区レベル
          input-trident.txt
```

このディレクトリ構造から生成される TRIDENT 中間言語:

```
AreaWithConcern: Naka Ward, Hiroshima, Hiroshima Prefecture, Japan; Cafes
```

`parse_full_area()` が抽出する完全な階層表現:
`"Naka Ward, Hiroshima, Hiroshima Prefecture, Japan"`

---

## Nominatim による検証

この階層表現を Nominatim に渡すと、完全に正確に解決できる:

| クエリ | Nominatim の解決結果 |
|-------|-------------------|
| `"Hiroshima Prefecture, Japan"` | 広島県 (id=3218753) ✓ |
| `"Hiroshima, Hiroshima Prefecture, Japan"` | 広島市 (id=4097196) ✓ |
| `"Kyoto Prefecture, Japan"` | 京都府 (id=2137477) ✓ |
| `"Kyoto, Kyoto Prefecture, Japan"` | 京都市 (id=357794) ✓ |
| `"Osaka Prefecture, Japan"` | 大阪府 (id=341906) ✓ |
| `"Osaka, Osaka Prefecture, Japan"` | 大阪市 (id=358674) ✓ |

---

## この問題が難しい理由

**事前構造化された階層知識がない場合**、自然言語クエリ「広島のカフェを教えて」は曖昧である:
- "広島" は広島県を指すか、広島市を指すか
- 多くの場合ユーザー自身も意識していない

この曖昧性解消は、単なる語彙知識の問題ではなく:
1. 行政区画の包含関係の知識 (広島市 ⊂ 広島県)
2. ユーザーの意図の推定
3. コンテキストからの絞り込み

を同時に必要とする。**GPT-5.1 を含む大型 LLM であっても、自由テキスト入力に対してこの問題を安定的に解くことは報告されていない。**

---

## text2geoql-dataset のアーキテクチャ的優位性

```
自由テキスト入力の問題:
  "広島のカフェ" → LLM が Hiroshima Prefecture か Hiroshima City か判断できない

text2geoql-dataset の解決:
  ディレクトリ構造 → TRIDENT 中間言語 → Nominatim → area(id:XXXXXX)

  "Hiroshima, Hiroshima Prefecture, Japan; Cafes"
                    ↓ Nominatim
         area(id:4097196)  ← 広島市に一意に解決
```

**データセット設計の段階で行政階層を構造化することで、LLM の地名知識に依存せず Nominatim という外部グラウンディング源に委譲できる。** これは TRIDENT 中間言語の核心的な設計思想の一つである。

---

## 応用可能性

この知見は OSM に限らず、行政区画データを持つあらゆる地理情報システムに適用できる:
- GeoNames, Wikidata, GADM 等の階層的行政区画データと組み合わせることで同様の効果が期待できる
- 自然言語クエリからの地理的意図推定（Geoparsing）タスクに対するデータセット設計指針として参照できる
