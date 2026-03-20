# RS-005: TRIDENT — 中間言語の起源プロジェクト

## 概要

text2geoql-dataset が採用している **TRIDENT 中間言語** は、yuiseki によって 2023-05 に開始された OSS プロジェクト TRIDENT に由来する。

- **リポジトリ:** https://github.com/yuiseki/TRIDENT
- **開始:** 2023-05-13

---

## TRIDENT とは

TRIDENT は、人道支援・災害対応文脈での地理情報可視化を目的とした自然言語インターフェースシステムである。
ユーザーの自然言語入力を解釈し、OpenStreetMap の Overpass API を介して地理データを取得・表示する。

### 三層アーキテクチャ

| レイヤー | 役割 |
|---------|------|
| **Surface layer** | 自然言語入力（例: "Show me hospitals in Tokyo"） |
| **Inner layer** | **TRIDENT 中間言語**（例: `AreaWithConcern: Tokyo, Japan; Hospitals`） |
| **Deep layer** | Overpass QL（例: `nwr["amenity"="hospital"](area.inner)`） |

### TRIDENT 中間言語の設計思想

- 自然言語の曖昧さを排除しつつ、Overpass QL の複雑さを隠蔽する意味的中間層
- **`AreaWithConcern: <地名>; <コンサーン>`** という構文で地名とコンサーンを明示的に分離
- 地名は Nominatim で OSM の relation ID に解決（`area(id)` クエリで精確なエリア指定が可能）
- コンサーンは good_concerns.yaml で管理された OSM タグへのマッピング

---

## text2geoql-dataset における TRIDENT の位置づけ

text2geoql-dataset は TRIDENT の Inner layer → Deep layer 変換（TRIDENT 中間言語 → Overpass QL）を学習データとして体系的に収集・構築するプロジェクトである。

- TRIDENT プロジェクト自体は Few-Shot + 大型 LLM（text-davinci-003 時代）で Surface → Inner → Deep の三段変換を実装
- text2geoql-dataset の目標は **Inner → Deep 変換を Raspberry Pi 4B 上の ≤1.1B モデルで実行できるように Fine-tuning する**こと
- これにより、TRIDENT をオフライン・エッジ環境でも動作させることが可能になる

---

## 独自性の核心

TRIDENT 中間言語という概念は：

1. **NL-to-OSM 先行研究（OverpassNL, ChatGeoPT 等）には存在しない**
2. 意味的グルーピング問題（「病院」= `amenity=hospital` + `healthcare=clinic` + `healthcare=doctor`）を中間層で解決できる（ADR-009 参照）
3. 地名解決を Nominatim に委譲することで、クエリ生成モデルが地名知識を保有する必要をなくす
4. Fine-tuning データとして利用しやすい構造化された入力表現を提供する

これらの設計は text2geoql-dataset および TRIDENT が独自に考案したものである。
