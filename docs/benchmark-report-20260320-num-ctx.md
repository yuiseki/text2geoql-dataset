# ベンチマークレポート: num_ctx・case-fix・k実験 (2026-03-20)

## 実験の動機

80%の壁を超えるために2つのアプローチを検討:
1. Few-Shot 改善: case-insensitive マッチング修正 + k=4→6
2. コンテキスト幅拡張: gpt-oss:20b vs gpt-oss-128k:20b の差が num_ctx のみであることを ollama show で確認

## ollama show による発見

```
gpt-oss:20b      context_length=131072  num_ctx=(未設定=Ollamaデフォルト)
gpt-oss-128k:20b context_length=131072  num_ctx=128000  ← Modelfileに明示設定
```
→ 同一重み・同一アーキテクチャ。33% vs 73% の差は num_ctx のみ。

```
gemma3:12b   context_length=131072  num_ctx=(未設定)
qwen3:8b     context_length=40960   num_ctx=(未設定)  ← Ollamaがcontext_lengthを参照?
qwen2.5-coder:3b  context_length=32768  num_ctx=(未設定)
```

## 実験結果一覧

| モデル | default | k=6+case-fix | num_ctx=32768 | num_ctx=131072 |
|--------|---------|--------------|---------------|----------------|
| qwen2.5-coder:3b | 80% | 40% ↓ | 80% (復活) | — |
| qwen3:8b | 80% | 87% ↑ | 40% ↓ | 80% |
| gemma3:12b | 80% | 73% ↓ | **100%** ✨ | 73% |
| gpt-oss:20b | 33% | — | 13% ↓ | — |

## 重要な発見

### 1. k=6 はモデルサイズに依存
- 大きなモデル(qwen3:8b 8B): k=6 で改善(80%→87%)
- 小さなモデル(qwen2.5-coder:3b 3B): k=6 で大幅劣化(80%→40%)
  - 失敗パターン: area.inner を使わなくなる、誤タグ、構文崩壊
  - 原因: プロンプト長増加で小型モデルが構造を維持できない

### 2. gemma3:12b の num_ctx=32768 で 100%
- デフォルト context (おそらく ~2048) では Few-Shot プロンプトが切り詰められていた
- num_ctx=32768 で全例が読めるようになり 80%→100% に改善
- ただし num_ctx=131072 では 73% に劣化 (KVキャッシュ増大による品質低下?)
- **sweet spot: 32768**

### 3. num_ctx は Modelfile PARAMETER では効かない
- `ollama create` で `PARAMETER num_ctx 32768` を焼いても `ollama.generate()` options に反映されない
- `options["num_ctx"]` として明示的に渡す必要がある (`--num-ctx` CLI フラグ)

### 4. gpt-oss:20b の num_ctx は 128000 が最適
- num_ctx=32768: 13% (デフォルト33%より悪化)
- gpt-oss-128k:20b (num_ctx=128000): 73%
- 最適値は 128000 付近と推定

## 推奨設定

| モデル | 推奨コマンド |
|--------|-------------|
| gemma3:12b | `--num-ctx 32768` |
| qwen3:8b | デフォルト(オプション不要) |
| qwen2.5-coder:3b | デフォルト(オプション不要) |
| gpt-oss:20b | `--num-ctx 128000` |

## 残課題: Convenience Stores の失敗

全モデルで一貫して失敗する "Taito, Tokyo, Japan; Convenience Stores":
- 生成されるクエリ: `amenity=convenience_store` (誤)
- 正解: `shop=convenience`
- 原因: case-fix により "Convenience stores" の例が読めるようになったが
  正例が k=4 の top-4 に選ばれていない可能性 (他の concern の例が似た地名で選ばれる?)
- 次のアプローチ: Nominatim grounding または eval set への正解例の追加

## まとめ: 現時点のベスト構成

```
gemma3:12b + --num-ctx 32768  → 100%/6.5s  ← 新チャンピオン
qwen3:8b (default)            →  80%/5.5s
qwen2.5-coder:3b (default)    →  80%/4.9s  ← 速度優秀
```
