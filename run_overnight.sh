#!/usr/bin/env bash
# Overnight batch job: benchmark new families, then batch-generate missing entries.
# Run inside tmux: tmux new-session -d -s overnight 'bash run_overnight.sh 2>&1 | tee tmp/overnight.log'

set -euo pipefail
cd "$(dirname "$0")"
LOG_PREFIX="[overnight]"

echo "$LOG_PREFIX ====== START $(date) ======"
echo "$LOG_PREFIX Phase 1: Benchmark new model families"

run_bench() {
    local group="$1"; shift
    echo ""
    echo "$LOG_PREFIX --- benchmark group: $group $* ---"
    uv run python src/benchmark_models.py --group "$group" "$@" || true
}

# Small reasoning models (may need think tokens)
run_bench phi4
run_bench ministral-3
run_bench magistral --no-think
run_bench deepseek-r1 --no-think
run_bench olmo2

# Remaining large qwen3 / qwen3.5
run_bench qwen3-large --no-think
run_bench qwen3.5-large --no-think

echo ""
echo "$LOG_PREFIX Phase 1 complete: $(date)"
echo "$LOG_PREFIX Phase 2: Batch data generation"
echo ""

uv run python src/batch_generate.py \
    --model qwen2.5-coder:3b \
    --num-predict 256 \
    --data-dir ./data \
    --tmp-dir ./tmp \
    --disk-min-gb 20 \
    || true

echo ""
echo "$LOG_PREFIX ====== DONE $(date) ======"
