# ベンチマーク結果 — 全モデル一覧

**評価セット:** 5命令 × 3試行 = 15クエリ
**評価命令:**
- `AreaWithConcern: Taito, Tokyo, Japan; Cafes`
- `AreaWithConcern: Taito, Tokyo, Japan; Convenience Stores`
- `AreaWithConcern: Shinjuku, Tokyo, Japan; Hotels`
- `AreaWithConcern: Gangnam-gu, Seoul, South Korea; Restaurants`
- `AreaWithConcern: Shibuya, Tokyo, Japan; Parks`

**成功条件:** Overpass API が 1件以上の要素を返す
**実行環境:** RTX 3060 12GB / Ryzen 9 5900X / 96GB RAM
**最終更新:** 2026-03-21

---

## 総合ランキング（デフォルト設定）

| モデル | Think | 成功率 | OK/Total | 平均秒 | 備考 |
|-------|-------|-------|---------|-------|------|
| **gemma3:12b** | off | **100%** | 15/15 | 6.5s | `--num-ctx 32768` 必須 (RF-001) |
| qwen3:8b | off | 87% | 13/15 | 5.5s | |
| gemma3:12b | default | 80% | 12/15 | 5.6s | |
| gemma3:27b | default | 80% | 12/15 | 8.0s | |
| qwen2.5-coder:3b | off | 80% | 12/15 | 4.9s | **コスパ最優秀** |
| qwen2.5-coder:3b | default | 80% | 4/5 | 3.8s | |
| qwen2.5-coder:14b | default | 80% | 4/5 | 8.1s | |
| qwen3:8b | on | 80% | 12/15 | 22.6s | think=on は遅い |
| qwen3-coder:30b | default | 80% | 4/5 | 9.0s | |
| gpt-oss-128k:20b | default | 73% | 11/15 | 6.9s | |
| granite4:tiny-h | default | 67% | 10/15 | 6.1s | granite 系最高 |
| gemma3:4b | default | 60% | 9/15 | 4.4s | |
| granite3.2:8b | default | 60% | 9/15 | 6.9s | |
| qwen2.5-coder:1.5b | default | 60% | 3/5 | 3.5s | |
| qwen2.5-coder:7b | default | 60% | 3/5 | 4.0s | |
| qwen3:14b | off | 60% | 9/15 | 5.6s | |
| qwen3.5:9b | off | 60% | 9/15 | 5.0s | |
| deepseek-r1:14b | off | 53% | 8/15 | 6.6s | |
| qwen3:1.7b | on | 53% | 8/15 | 7.6s | |
| granite4:micro-h | default | 47% | 7/15 | 5.9s | |
| ministral-3:8b | default | 47% | 7/15 | 6.7s | |
| gemma3:1b | default | 40% | 6/15 | 3.9s | |
| granite3.3:2b | default | 40% | 6/15 | 5.3s | |
| granite4:1b | default | 40% | 6/15 | 5.6s | |
| granite4:3b | default | 40% | 6/15 | 5.4s | |
| magistral:24b | off | 40% | 6/15 | 35.4s | 遅い |
| phi4:14b | default | 40% | 6/15 | 6.7s | |
| qwen3:1.7b | off | 40% | 6/15 | 3.4s | |
| qwen3:32b | off | 40% | 6/15 | 31.6s | 遅い |
| qwen3.5:0.8b | off | 40% | 6/15 | 3.7s | |
| qwen3.5:2b | off | 40% | 6/15 | 4.0s | |
| qwen3.5:4b | off | 40% | 6/15 | 4.5s | |
| gemma3:270m | default | 33% | 5/15 | 4.4s | |
| gpt-oss:20b | default | 33% | 5/15 | 7.2s | num_ctx=128000 で 73% (RF-001) |
| gpt-oss-safeguard:20b | default | 33% | 5/15 | 7.5s | |
| granite3.2:2b | default | 33% | 5/15 | 5.2s | |
| granite4:350m | default | 33% | 5/15 | 4.8s | |
| qwen3:0.6b | on | 33% | 5/15 | 5.9s | |
| ministral-3:14b | default | 27% | 4/15 | 7.2s | |
| qwen3:14b | on | 27% | 4/15 | 25.4s | |
| deepseek-r1:1.5b | off | 20% | 3/15 | 4.8s | |
| deepseek-r1:32b | off | 20% | 3/15 | 26.5s | |
| granite3.3:8b | default | 20% | 3/15 | 9.1s | 3.2:8b より大幅退化 |
| olmo2:7b | default | 20% | 3/15 | 7.0s | |
| qwen2.5-coder:0.5b | default | 20% | 1/5 | 3.3s | |
| qwen2.5-coder:32b | default | 20% | 1/5 | 32.0s | 遅い上に低い |
| gpt-oss:20b | off | 13% | 2/15 | 8.2s | |
| ministral-3:3b | default | 13% | 2/15 | 10.8s | |
| phi4-mini:3.8b | default | 7% | 1/15 | 6.2s | |
| qwen3:0.6b | off | 7% | 1/15 | 3.2s | |
| deepseek-r1:7b | off | 0% | 0/15 | 5.5s | |
| deepseek-r1:8b | off | 0% | 0/15 | 6.6s | |
| olmo2:13b | default | 0% | 0/15 | 9.2s | |
| phi4-mini-reasoning:3.8b | default | 0% | 0/15 | 7.6s | |
| qwen3:30b | off | 0% | 0/15 | 8.3s | no_code_block 全滅 |
| qwen3.5:27b | off | 0% | 0/15 | — | Ollama OOM crash |
| qwen3.5:35b | off | 0% | 0/15 | — | Ollama OOM crash |

---

## num_ctx 実験結果

`--num-ctx` オプションによるコンテキスト幅指定の効果。詳細は RF-001 参照。

| モデル | Think | num_ctx | 成功率 | 平均秒 |
|-------|-------|---------|-------|-------|
| gemma3:12b | off | **32768** | **100%** | 6.5s |
| gemma3:12b | off | default (~2048) | 80% | 5.6s |
| gemma3:12b | off | 131072 | 73% | 6.8s |
| qwen3:8b | off | default (40960) | 80% | 5.5s |
| qwen3:8b | off | 32768 | 40% | 5.2s |
| gpt-oss:20b | default | default (~2048) | 33% | 7.2s |
| gpt-oss:20b | default | 128000 | 73% | 7.0s |
| gpt-oss:20b | default | 32768 | 13% | 7.5s |

---

## ファミリー別まとめ

### qwen2.5-coder (推奨: 3b)
コーディング特化モデル。3b が速度・品質・コスパのバランス最良。32b は遅い上に 20% と最低。

| モデル | 成功率 | 平均秒 |
|-------|-------|-------|
| qwen2.5-coder:0.5b | 20% | 3.3s |
| qwen2.5-coder:1.5b | 60% | 3.5s |
| qwen2.5-coder:3b | 80% | 4.9s |
| qwen2.5-coder:7b | 60% | 4.0s |
| qwen2.5-coder:14b | 80% | 8.1s |
| qwen2.5-coder:32b | 20% | 32.0s |

### qwen3 (推奨: 8b think=off)
think=off が必須。8b が最高コスパ。30b は no_code_block 全滅、32b は40%/遅い。

| モデル | Think | 成功率 | 平均秒 |
|-------|-------|-------|-------|
| qwen3:0.6b | off | 7% | 3.2s |
| qwen3:1.7b | off | 40% | 3.4s |
| qwen3:4b | off | 0% | 6.0s |
| qwen3:8b | off | **87%** | 5.5s |
| qwen3:14b | off | 60% | 5.6s |
| qwen3:30b | off | 0% | 8.3s |
| qwen3:32b | off | 40% | 31.6s |

### qwen3.5 (think=off で試行)
全体的に低調。0.8b〜9b が 40〜60%。27b/35b は OOM クラッシュ。

| モデル | Think | 成功率 | 平均秒 |
|-------|-------|-------|-------|
| qwen3.5:0.8b | off | 40% | 3.7s |
| qwen3.5:2b | off | 40% | 4.0s |
| qwen3.5:4b | off | 40% | 4.5s |
| qwen3.5:9b | off | 60% | 5.0s |
| qwen3.5:27b | off | 0% | — (OOM) |
| qwen3.5:35b | off | 0% | — (OOM) |

### gemma3 (推奨: 12b + --num-ctx 32768)
num_ctx=32768 で 100% 達成。4b 以上は安定して高成績。

| モデル | 成功率 | 平均秒 |
|-------|-------|-------|
| gemma3:270m | 33% | 4.4s |
| gemma3:1b | 40% | 3.9s |
| gemma3:4b | 60% | 4.4s |
| gemma3:12b (default) | 80% | 5.6s |
| **gemma3:12b (num_ctx=32768)** | **100%** | 6.5s |
| gemma3:27b | 80% | 8.0s |

### granite4 (推奨: tiny-h)
-h (Hypothetical) variant が基本 variant より優秀。最高 67%。

| モデル | 成功率 | 平均秒 |
|-------|-------|-------|
| granite4:350m | 33% | 4.8s |
| granite4:1b | 40% | 5.6s |
| granite4:3b | 40% | 5.4s |
| granite4:micro-h | 47% | 5.9s |
| granite4:tiny-h | **67%** | 6.1s |

### granite3.2 / granite3.3
3.2:8b が granite 系最高 60%。3.3 世代は 3.2 より退化（3.3:8b → 20%）。

| モデル | 成功率 | 平均秒 |
|-------|-------|-------|
| granite3.2:2b | 33% | 5.2s |
| granite3.2:8b | **60%** | 6.9s |
| granite3.3:2b | 40% | 5.3s |
| granite3.3:8b | 20% | 9.1s |

### gpt-oss (推奨: gpt-oss-128k:20b)
num_ctx が鍵。128k variant (num_ctx=128000) が 73%。

| モデル | 成功率 | 平均秒 |
|-------|-------|-------|
| gpt-oss:20b (default) | 33% | 7.2s |
| gpt-oss:20b (num_ctx=128000) | 73% | 7.0s |
| gpt-oss-128k:20b | 73% | 6.9s |
| gpt-oss-safeguard:20b | 33% | 7.5s |

### mistral 系

| モデル | 成功率 | 平均秒 |
|-------|-------|-------|
| ministral-3:3b | 13% | 10.8s |
| ministral-3:8b | 47% | 6.7s |
| ministral-3:14b | 27% | 7.2s |
| magistral:24b (think=off) | 40% | 35.4s |

### deepseek-r1 (think=off で試行)
14b が最高 53%。7b/8b は 0%。

| モデル | 成功率 | 平均秒 |
|-------|-------|-------|
| deepseek-r1:1.5b | 20% | 4.8s |
| deepseek-r1:7b | 0% | 5.5s |
| deepseek-r1:8b | 0% | 6.6s |
| deepseek-r1:14b | **53%** | 6.6s |
| deepseek-r1:32b | 20% | 26.5s |

### その他

| モデル | 成功率 | 平均秒 |
|-------|-------|-------|
| phi4-mini:3.8b | 7% | 6.2s |
| phi4-mini-reasoning:3.8b | 0% | 7.6s |
| phi4:14b | 40% | 6.7s |
| olmo2:7b | 20% | 7.0s |
| olmo2:13b | 0% | 9.2s |
| qwen3-coder:30b | 80% | 9.0s |

---

## ベストモデル選定

| 用途 | 推奨モデル | 設定 | 成功率 | 平均秒 |
|-----|----------|------|-------|-------|
| **最高品質** | gemma3:12b | `--no-think --num-ctx 32768` | 100% | 6.5s |
| **速度優先** | qwen2.5-coder:3b | `--no-think` | 80% | 4.9s |
| **汎用バランス** | qwen3:8b | `--no-think` | 87% | 5.5s |
| **Fine-tuning 目標** | ≤1.1B モデル | 未達成 | — | — |
