# ADR-010: Apertus 評価のための llama-server バックエンド段階的導入

## ステータス
Accepted

## コンテキスト

Swiss AI の Apertus-v1.1 系列（0.5B/1.5B、Base/Instruct）をモデル比較対象に追加したい。一方で `src/benchmark_models.py` は Ollama（`ollama.generate()`）に強く依存しており、60 モデル超が登録済み。プロジェクトオーナーは Ollama から llama.cpp（`llama-cli`/`llama-server`）への個人的な移行を進めており、Apertus 追加を機に llama.cpp 系での構築を志向したが、既存 60 モデルの全面移行は過大なため段階的移行とした。

検証で判明した制約：

1. `llama-cli` は Instruct モデルで対話モード（`-cnv`）が既定有効になり、`-no-cnv` を付けても標準入力が空だと `> ` を出し続けてハングする（単発 CLI 実行に不向き）。
2. `llama-server` の `/completion` エンドポイントは生 prompt（chat template 適用なし）を受け付け、HTTP リクエスト完結型のため上記のハング問題を回避できる。既存の Few-Shot プロンプト（`build_prompt()` が組み立てる1本の文字列）とインターフェースが一致する。
3. `llama-server` は embedding 用途と生成用途を同一プロセスで併用できない（`--embedding` フラグ付きサーバーは生成 API を拒否する）。また `num_ctx` 相当はリクエスト単位で指定できず起動時 `-c` で固定される。
4. Apertus の GGUF はコミュニティ変換版が 4 種（0.5B/1.5B × Base/Instruct）すべて HF に存在する。
5. Apertus の MLP は xIELU 活性化を使い `gate_proj` が存在しない（`up_proj`→活性化→`down_proj` のみ）ため、既存の LoRA `target_modules` 固定リストのままだと LoRA アタッチに失敗する。

## 決定

- 既存の Ollama 経路（`generate_overpassql()`, `MODEL_GROUPS` の60モデル超, Few-Shot 例選択の `OllamaEmbeddings`）は一切変更しない。
- 新規 `src/llama_server_backend.py` を追加し、`llama-server` サブプロセスのライフサイクル（起動・`/health` ポーリング・停止）を管理する。GGUF は `llama-server -hf <repo>[:quant]` の自動ダウンロード機能を使い、追加の依存パッケージなしで完結させる。
- `src/generate_overpassql.py` に `generate_overpassql_llama_server()` を追加し、`/completion` を叩く。既存 `generate_overpassql()` 内のコードブロック抽出ロジックは `_extract_overpassql_block()` として共通化。
- `src/benchmark_models.py` に `APERTUS_MODELS: dict[str, GgufModelSpec]` レジストリと `MODEL_GROUPS["apertus"]` を追加し、`_model_backend(model)` でモデルごとに Ollama / llama_server を振り分ける。llama_server 系はモデルごとに **1回だけ** サーバーを起動し、`EVAL_INSTRUCTIONS × trials` の全クエリをそのセッション内で処理してから停止する（クエリ毎起動はしない）。
- `examples/lora_finetune/dataset.py` に `requires_bf16(model_id)` を追加し、Gemma3・Apertus を bf16 対象として一本化。`train.py` に `lora_target_modules(model_id)` を追加し、Apertus では `gate_proj` を除外した target_modules を返す。

### モデルレジストリ

```python
APERTUS_MODELS: dict[str, GgufModelSpec] = {
    "apertus-0.5b-base":     GgufModelSpec(hf_repo="NonMiFrega/Apertus-v1.1-0.5B-Q4_K_M-GGUF"),
    "apertus-0.5b-instruct": GgufModelSpec(hf_repo="MrMeOrYou/Apertus-v1.1-0.5B-Instruct-Q4_K_M-GGUF"),
    "apertus-1.5b-base":     GgufModelSpec(hf_repo="NonMiFrega/Apertus-v1.1-1.5B-Q4_K_M-GGUF"),
    "apertus-1.5b-instruct": GgufModelSpec(hf_repo="MrMeOrYou/Apertus-v1.1-1.5B-Instruct-GGUF", quant="Q4_K_M"),
}
```

### CLI インターフェース

```bash
uv run python src/benchmark_models.py --group apertus --trials 3
```

## 根拠

- **なぜ `/completion` であって `/v1/chat/completions` でないか**: 現行の Few-Shot プロンプトは chat message 形式ではなく1本の completion 文字列。`/completion` を使えば chat template 変換のロジックを新設せず、Ollama の `ollama.generate(prompt=...)` と同じ使い方のまま置き換えられる。
- **なぜ都度起動方式であって router mode でないか**: `llama-server` は `--models-dir` + `/models/load`/`/models/unload` によるモデル動的切替（router mode）を実装済みだが、Apertus は 4 モデルのみであり、モデルごとにサブプロセスを起動・停止するシンプルな方式で十分。60 モデル超の Ollama 群を将来 llama-server へ全面移行する場合に router mode へ発展させやすいよう、`GgufModelSpec` レジストリと `_model_backend()` によるディスパッチという形にしてある。
- **なぜ既存 Ollama 経路に一切手を入れないか**: 60 モデル超のベンチマーク実績・比較データの再現性を壊さないため。新機能は追加のみで既存関数のシグネチャ・挙動を変えない。
- **なぜ `target_modules` をモデル名文字列で分岐するか**: PEFT の `LoraConfig` はモデルの実際のモジュール構造を検査せず `target_modules` に列挙された名前をそのまま探すため、存在しない `gate_proj` を含めると即座にエラーになる。Apertus の xIELU MLP 構造は `transformers/models/apertus/modeling_apertus.py` で確認済み（`up_proj`→活性化→`down_proj` のみ）。

## 対象外（将来検討）

- 既存 Ollama 60 モデル超の router mode への全面移行。
- Few-Shot 例選択の embedding（`OllamaEmbeddings`）の置き換え。

## 補足

実装: `src/llama_server_backend.py`, `src/generate_overpassql.py`, `src/benchmark_models.py`, `examples/lora_finetune/{dataset,train,evaluate}.py`
