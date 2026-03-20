# ADR-005: 生成プロベナンスと失敗メタデータの記録

## ステータス
Accepted

## コンテキスト

LLM によるデータ生成では「何が生成されたか」だけでなく「どのモデルがどの設定で生成したか」「なぜ失敗したか」を記録しておく必要があった。理由：

1. **再現性**: 同じクエリを別モデルで再生成するかどうかの判断に使う
2. **品質管理**: モデルバージョン更新時に古いクエリを再評価できる
3. **失敗分析**: `no_code_block`、`zero_results` などの失敗パターンを集計してプロンプト改善に活かす
4. **イデンポテント処理**: 「このモデルでは既に試みた」という記録がないと、`run()` が毎回同じ試みを繰り返す

当初は `not-found.txt`（レガシー）という空ファイルで「生成失敗」を記録していたが、失敗理由が分からなかった。

## 決定

成功・失敗それぞれに専用の JSON メタデータファイルを用意する。

### 成功: `output-{slug}.meta.json`

```json
{
  "model": "qwen2.5-coder:14b",
  "model_slug": "qwen2.5-coder-14b",
  "temperature": 0.01,
  "num_predict": 256,
  "generated_at": "2026-03-20T07:00:00+00:00",
  "element_count": 42
}
```

### 失敗: `not-found-{slug}.json`

```json
{
  "model": "qwen2.5-coder:14b",
  "model_slug": "qwen2.5-coder-14b",
  "reason": "zero_results",
  "query": "[out:json][timeout:30];...",
  "generated_at": "2026-03-20T07:00:00+00:00"
}
```

### 失敗理由の分類（`FailureReason` Literal 型）

| reason | 意味 | 対処方針 |
|--------|------|---------|
| `no_code_block` | LLM がコードブロックを出力しなかった | プロンプト改善 or 別モデル試行 |
| `too_many_lines` | クエリが 20 行を超えた | プロンプトに行数制限を追加 |
| `zero_results` | Overpass API が 0 件を返した | OSM タグ誤り or 該当地域にデータなし |
| `api_error` | Overpass API への接続エラー | ネットワーク問題、タイムアウト |

### `model_to_slug()` 変換

```python
def model_to_slug(model: str) -> str:
    return model.replace(":", "-").replace("/", "-")
# "qwen2.5-coder:14b" → "qwen2.5-coder-14b"
# "qwen3/14b" → "qwen3-14b"
```

## 根拠

- **失敗理由の型安全性**: `Literal["no_code_block", "too_many_lines", "zero_results", "api_error"]` で列挙することで、mypy が未定義の reason を検出できる
- **成功メタデータの活用**: `element_count` を記録することでクエリの「豊かさ」を後から比較できる（1 件しか返さないクエリより 100 件返すクエリの方が汎用性が高い）
- **モデルごとの独立ファイル**: `not-found-{slug}.json` として保存することで、あるモデルで失敗した後に別モデルで成功した場合も両方の記録を保持できる
- **レガシー `not-found.txt` との後方互換**: `run()` で `not-found.txt` のチェックも残し、古いエントリを処理できる

## 結果

**ポジティブ：**
- `reason` 別の集計が容易（benchmark_models.py の summary テーブルで活用）
- `element_count` による事後的なデータセット品質フィルタリングが可能
- 失敗率のモデル間比較が定量的にできる
- `run()` のイデンポテント性が型安全な形で保証される

**ネガティブ：**
- メタファイルが増えることで `find_orphan_trident.py` の検索ロジックがやや複雑になる
- `not-found.txt`（レガシー）と `not-found-{slug}.json` の 2 種類を判定する必要がある

## 補足

実装: `src/meta.py`
テスト: `tests/test_meta.py`

```python
# src/meta.py のコアクラス
@dataclass
class GenerationMeta:
    model: str
    model_slug: str
    temperature: float
    num_predict: int
    generated_at: str
    element_count: int

@dataclass
class FailureMeta:
    model: str
    model_slug: str
    reason: FailureReason
    query: str | None
    generated_at: str
```
