# ADR-003: LLM + Few-Shot プロンプティングによる OverpassQL 生成

## ステータス
Accepted

## コンテキスト

OverpassQL クエリの生成方法として以下を検討した：

1. **ルールベース生成**: 地名と関心事から固定テンプレートでクエリを組み立てる
2. **専用ファインチューニング済みモデル**: text2geoql 専用に訓練された小型モデル
3. **汎用 LLM + Zero-Shot**: GPT-4 等に「OverpassQL を書け」と指示するだけ
4. **汎用 LLM + Few-Shot プロンプティング**: 既存の成功例をプロンプトに埋め込む

OverpassQL は OSM のタグ体系（`amenity=cafe`、`tourism=hotel` など）に精通している必要があり、かつ Overpass API の文法（`area` 指定子、`nwr` 検索、`out geom` 等）を正確に使う必要がある。ルールベースでは OSM タグの多様性（cuisine サブタグ、religion サブタグ、複合条件など）に対応しきれない。

さらに、このリポジトリ自体がデータセット「生成」のシステムであるため、生成されたデータは別モデルの訓練に使われる。**生成品質の下限を保証する仕組み**が重要だった。

## 決定

**ローカル LLM（Ollama）+ LangChain Chroma による意味的類似 Few-Shot プロンプティング**を採用する。

### プロンプト構造

```
[System Rules]
You are an expert of OpenStreetMap and Overpass API.
- Output valid Overpass API query.
- The query timeout MUST be 30.
- ... (詳細ルール)

===
Examples:

Input:
AreaWithConcern: Taito, Tokyo, Japan; Cafes

Output:
```
[out:json][timeout:30];
area["name:en"="Tokyo"]->.outer;
area["name:en"="Taito"]->.inner;
(nwr["amenity"="cafe"](area.inner)(area.outer););
out geom;
```

... (類似例 × 最大 4 件)

Input:
{question}   ← 生成対象の TRIDENT 命令

Output:
```

### Few-Shot 例の選択戦略

`SemanticSimilarityExampleSelector`（LangChain）+ `Chroma` ベクトルストアを使用：

1. `filter_type`（AreaWithConcern / Area / SubArea）が一致するもののみ候補とする
2. `filter_concern`（Cafes / Hotels 等）が一致するもの優先
3. 同じ地名のサンプルは最大 2 件に制限（過学習防止）
4. 残りを意味的近傍ベクトルで上位 4 件に絞る

埋め込みモデル: `nomic-embed-text:v1.5`（Ollama 経由）

### 生成後の検証

```python
parts = response["response"].split("```")
# コードブロックが抽出できなければ failure_reason = "no_code_block"
# 20行超なら failure_reason = "too_many_lines"
# Overpass API で 0 件なら failure_reason = "zero_results"
```

## 根拠

- **Few-Shot が Zero-Shot より確実**: OSM タグ体系は LLM の学習データに含まれるが、Overpass QL の細かい文法（`area` 変数の `.inner`/`.outer` パターン等）は Few-Shot 例があると格段に安定する
- **意味的類似例の選択**: ランダム例ではなく、同じ関心事・地域の例を選ぶことで「cafes なら `amenity=cafe`」という正確なタグを出力させられる
- **ローカル推論**: Ollama を使うことで API コスト・レートリミット・プライバシーの問題がない。自前の GPU でバッチ処理が可能
- **温度 0.01**: 決定論的に近い出力でデータセットの一貫性を保つ
- **Overpass API グラウンディング（ADR-002）との組み合わせ**: Few-Shot でクエリの品質を上げ、API でそれを検証する二段階品質保証

## 結果

**ポジティブ：**
- 小型モデル（3b）でも 80% の成功率（有効クエリ生成 + Overpass 結果あり）を達成
- Few-Shot 例が増えるほど生成品質が向上する正のフィードバックループが生まれる
- 新しい関心事（POI タイプ）を追加するだけで対応範囲を拡大できる
- `think=off`（`qwen3:8b`）で ~4.3 秒/クエリという実用的な速度

**ネガティブ：**
- Few-Shot 例のロードに Chroma + Ollama 埋め込みモデルが必要（オーバーヘッド）
- 例が少ない新しい関心事では品質が低下する（コールドスタート問題）
- プロンプトが長くなる（最大 4 例 × 10 行 = 40 行）ため、小型モデルのコンテキスト枠を圧迫する

## 補足

実装: `src/generate_overpassql.py`
テスト: `tests/test_generate_overpassql.py`

### モデル選定の経緯（2026-03-20 ベンチマーク結果より）

| モデル | Think | 成功率 | 平均速度 |
|--------|-------|--------|---------|
| qwen2.5-coder:3b | — | 80% | 3.8s |
| qwen3:8b | off | 80% | 4.3s |
| qwen2.5-coder:14b | — | 80% | 8.1s |

現在のデフォルト: `qwen2.5-coder:14b`（歴史的経緯）。推奨: `qwen3:8b --no-think`（同品質・より汎用）。

詳細: `tmp/benchmark-report-20260320.md`
