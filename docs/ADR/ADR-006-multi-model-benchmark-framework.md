# ADR-006: マルチモデルベンチマーク基盤

## ステータス
Accepted

## コンテキスト

「どのモデルが OverpassQL 生成に最も適しているか」を定量的に評価する仕組みが必要だった。課題：

1. **モデルの多様性**: Qwen2.5-coder（0.5b〜32b）、Qwen3（0.6b〜32b）、Qwen3.5（0.8b〜35b）など多数のサイズ・ファミリが存在する
2. **Think モードの影響**: Qwen3/Qwen3.5 には chain-of-thought (think) モードがあり、有効・無効で品質と速度が大きく変わる
3. **タイムアウトリスク**: 一括実行すると大型モデルや think=on で長時間ブロックされる
4. **再現性**: 評価結果を JSON に保存して後から比較できる必要がある

## 決定

`src/benchmark_models.py` として独立したベンチマーク CLI を実装する。

### 評価セット（固定）

```python
EVAL_INSTRUCTIONS = [
    "AreaWithConcern: Taito, Tokyo, Japan; Cafes",
    "AreaWithConcern: Taito, Tokyo, Japan; Convenience Stores",
    "AreaWithConcern: Shinjuku, Tokyo, Japan; Hotels",
    "AreaWithConcern: Gangnam-gu, Seoul, South Korea; Restaurants",
    "AreaWithConcern: Shibuya, Tokyo, Japan; Parks",
]
```

地域（Tokyo/Seoul）、関心事（Cafes/Hotels/Parks/Restaurants）、コンビニなど多様性を確保した 5 命令。

### 主要設計

```python
# per-query タイムアウト（ThreadPoolExecutor + future.result(timeout=...)）
with ThreadPoolExecutor(max_workers=1) as executor:
    future = executor.submit(_run_one_query, ...)
    result = future.result(timeout=query_timeout)  # デフォルト 90s

# 即時保存（進捗保全）
model_path = f"tmp/benchmark-{slug}{think_suffix}-{timestamp}.json"
json.dump(model_report, f, indent=2)

# num_predict の自動スケール
def default_num_predict(model: str, think: bool | None = None) -> int:
    is_reasoning = any(model.startswith(f) for f in ("qwen3", "qwen3.5"))
    thinking_active = think is True or (think is None and is_reasoning)
    return 2048 if thinking_active else 256
```

### CLI インターフェース

```bash
# 単体モデル
uv run python src/benchmark_models.py --models qwen3:8b --no-think

# モデルグループ
uv run python src/benchmark_models.py --group qwen3 --trials 3

# think=on vs think=off 比較
uv run python src/benchmark_models.py --models qwen3:8b --trials 3
uv run python src/benchmark_models.py --models qwen3:8b --trials 3 --no-think
```

### 出力

- `tmp/benchmark-{slug}{think_suffix}-{timestamp}.json`: モデルごとの即時保存結果
- `tmp/benchmark-all-{timestamp}.json`: 集計レポート
- 実行中のサマリーテーブル（モデル完了ごとに表示）

## 根拠

- **モデルごとに個別実行**: 一括実行は 10 分タイムアウトで途中で切れる。`--models` で 1 モデルずつ指定することで長時間タスクを制御できる
- **即時保存**: `_probe_model()` 完了のたびに JSON を書くことで、途中でクラッシュしても進捗が失われない
- **per-query タイムアウト**: `ThreadPoolExecutor` を使った 90 秒タイムアウトで、stuck した LLM 推論を確実に打ち切れる
- **`num_predict` 自動スケール**: Think モードでは thinking トークンが `num_predict` バジェットを消費するため、`think=True` または reasoning family では 2048 に自動拡張する。これを怠ると 100% `no_code_block` になる

## 結果

**2026-03-20 ベンチマーク主要結果：**

| モデル | Think | 成功率 | 平均速度 | 推奨 |
|--------|-------|--------|---------|------|
| qwen3:8b | off | 80% | 4.3s | ★ 総合最強 |
| qwen2.5-coder:3b | — | 80% | 3.8s | ★ コーダー特化最速 |
| qwen2.5-coder:14b | — | 80% | 8.1s | — |
| qwen3-coder:30b | — | 80% | 9.0s | — |
| qwen3.5:9b | off | 60% | 5.0s | — |
| qwen3:4b | off/on | 0% | — | ✗ 重み壊れ疑い |
| qwen3.5:*/on | on | 0% | 15-35s | ✗ budget 枯渇 |

**ポジティブ：**
- モデル選定の意思決定を定量化できた
- Think=off が think=on より同品質で 5 倍速という知見を得た
- VRAM 制約（24GB）で 32b 以上はCPU fallback になることを発見

**ネガティブ：**
- 評価セットが 5 命令（固定）のため、特殊ケース（cuisine サブタグ、SubArea 等）の評価ができていない
- trials=1 で評価したモデルは信頼区間が広い（trials=3 以上が望ましい）

## 補足

実装: `src/benchmark_models.py`
レポート: `tmp/benchmark-report-20260320.md`

**known issue**: `qwen3:4b` は re-pull 後も全 `no_code_block`。weights 破損の疑いが強く、ベンチマーク結果から除外して考える。
