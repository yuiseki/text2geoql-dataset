# RF-001: num_ctx (Context Window Size) Effect on Few-Shot Quality

**Date:** 2026-03-20
**Status:** Confirmed
**Related ADR:** ADR-003 (LLM Few-Shot), ADR-006 (Benchmark)

## Summary

Context window size (`num_ctx`) passed at inference time has a large effect on Few-Shot quality. Each model has a sweet spot; using too small truncates the prompt, while too large may degrade KV-cache quality.

## Background

While benchmarking `gpt-oss:20b` vs `gpt-oss-128k:20b`, we discovered both models have identical weights. The only difference is `num_ctx=128000` in the Modelfile of the 128k variant. This directly caused the 33% vs 73% performance gap, motivating investigation across other models.

## Method

Used `ollama show <model>` to inspect Modelfile and architecture parameters. Then ran `benchmark_models.py` with `--num-ctx <value>` at varying context sizes (default, 32768, 40960, 128000, 131072).

## Key Finding: `ollama generate()` options override vs Modelfile

`options["num_ctx"]` passed to `ollama.generate()` IS applied. But `PARAMETER num_ctx` in the Modelfile is NOT automatically picked up by `ollama.generate()`. Custom model variants created via `ollama create` with `PARAMETER num_ctx 32768` showed no improvement, confirming the Modelfile parameter is ignored in the generate API. **Must always pass `--num-ctx` explicitly.**

## Results

| Model | Default | num_ctx=32768 | num_ctx=40960 | num_ctx=128000 | num_ctx=131072 |
|-------|---------|---------------|---------------|----------------|----------------|
| gemma3:12b | 80% | **100%** ✨ | — | — | 73% |
| qwen3:8b | 80% | 40% ↓ | 80% (default) | — | — |
| qwen2.5-coder:3b | 80% | 80% (no change) | — | — | — |
| gpt-oss:20b | 33% | 13% ↓ | — | 73% | — |

## Analysis

### gemma3:12b
- Default Ollama context for gemma3 models appears to be ~2048 tokens, truncating the Few-Shot prompt.
- At num_ctx=32768, the full prompt fits and the model achieves 100%.
- At num_ctx=131072, performance degrades to 73%, possibly due to KV-cache memory pressure or attention dilution.
- **Sweet spot: 32768**

### qwen3:8b
- Default context is 40960 (Ollama uses the model's `context_length` parameter).
- Reducing to 32768 cuts out parts of the prompt → performance drops to 40%.
- **Sweet spot: default (40960)**

### gpt-oss:20b
- Default Ollama context is small (probably ~2048 like other models without explicit num_ctx).
- num_ctx=32768 makes things worse (13%), likely because the model was trained for long contexts and the KV budget is still insufficient.
- num_ctx=128000 gives 73% — aligns with the gpt-oss-128k:20b result.
- **Sweet spot: 128000**

## Recommendations

```bash
# gemma3:12b — MUST pass num_ctx=32768
uv run python src/benchmark_models.py --models gemma3:12b --no-think --num-ctx 32768

# qwen3:8b — default is optimal, no flag needed
uv run python src/benchmark_models.py --models qwen3:8b --no-think

# gpt-oss:20b — must pass num_ctx=128000
uv run python src/benchmark_models.py --models gpt-oss:20b --no-think --num-ctx 128000
```

## Implication for Fine-Tuning

Models with small default context windows may perform poorly at inference even with good weights if the Few-Shot prompt is truncated. When fine-tuning, ensure `num_ctx` is set appropriately during both training and inference.
