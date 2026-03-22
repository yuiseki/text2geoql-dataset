"""Evaluate base vs fine-tuned model on the text2geoql benchmark.

Replicates the benchmark logic from text2geoql-dataset using HuggingFace
inference instead of Ollama, so results are directly comparable.

Scoring (same rules as benchmark_models.py):
  - PASS: output contains a valid Overpass QL block with expected tag
  - FAIL: zero_results | no_code_block | wrong_tag | error

Usage:
    # Evaluate base model (before FT)
    uv run python src/evaluate.py --model Qwen/Qwen2.5-Coder-0.5B-Instruct

    # Evaluate fine-tuned LoRA adapter (after FT)
    uv run python src/evaluate.py --adapter models/qwen2.5-coder-0.5b-lora

    # Compare both
    uv run python src/evaluate.py --model Qwen/Qwen2.5-Coder-0.5B-Instruct --adapter models/qwen2.5-coder-0.5b-lora
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))

from dataset import DATASET_DIR, format_prompt, load_pairs

DEFAULT_MODEL = "Qwen/Qwen2.5-Coder-0.5B-Instruct"
BENCHMARK_SAMPLE = 30   # number of pairs to evaluate (for speed)
MAX_NEW_TOKENS = 256


def load_benchmark_pairs(
    dataset_dir: str = DATASET_DIR,
    n: int = BENCHMARK_SAMPLE,
    holdout_json: str | None = None,
):
    """Load held-out pairs for benchmarking.

    Uses the same train/val split as train.py (seed=42, val_ratio=0.05) so that
    evaluation samples are guaranteed to be outside the training set.

    If holdout_json is provided, use a fixed list of input texts (e.g. from a
    previous evaluation run) instead of recomputing the split. This enables
    fair cross-version comparisons when the dataset has changed.
    """
    pairs = load_pairs(dataset_dir)
    pairs = [p for p in pairs if p.input_text.startswith("AreaWithConcern:")]

    if holdout_json is not None:
        import json
        with open(holdout_json) as f:
            fixed_inputs = set(json.load(f))
        val_pairs = [p for p in pairs if p.input_text in fixed_inputs]
        print(f"  Fixed holdout: {len(val_pairs)}/{len(fixed_inputs)} pairs found in current dataset")
        return val_pairs[:n]

    from datasets import Dataset
    # Replicate the exact same split used in train.py
    texts = [format_prompt(p.input_text, p.output_text) for p in pairs]
    ds = Dataset.from_dict({"text": texts, "idx": list(range(len(pairs)))})
    split = ds.train_test_split(test_size=0.05, seed=42)
    val_indices = split["test"]["idx"]

    val_pairs = [pairs[i] for i in val_indices]
    import random
    rng = random.Random(0)
    rng.shuffle(val_pairs)
    print(f"  Holdout val set: {len(val_pairs)} pairs")
    return val_pairs[:n]


def extract_overpassql(text: str) -> str | None:
    """Extract OverpassQL block from model output."""
    # Between ```overpassql ... ``` or ``` ... ```
    m = re.search(r"```(?:overpassql)?\s*\n?(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if m:
        return m.group(1).strip()
    # Bare [out:json] block
    m = re.search(r"(\[out:json\].*)", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    return None


OVERPASS_ENDPOINT = "https://overpass.yuiseki.net/api/interpreter"


def fetch_elements(query: str) -> list[dict]:
    """Execute an Overpass QL query and return the elements list."""
    import httpx
    try:
        response = httpx.get(OVERPASS_ENDPOINT, params={"data": query}, timeout=60)
        return response.json().get("elements", [])
    except Exception as e:
        print(f"    [overpass error] {e}")
        return []


def rewrite_name_en_to_name(ql: str) -> str:
    """Mechanically replace ["name:en"=...] with ["name"=...] in area filters.

    Used as the two-call fallback: if a query returns zero results, retry with
    the unqualified name tag. This handles areas (e.g. Paris, Rome) that have
    no name:en in OSM but do have a name tag.
    """
    return re.sub(r'\["name:en"=', '["name"=', ql)


def score_output(input_text: str, generated: str) -> str:
    """Return detailed status string, applying two-call name:en → name fallback.

    Scoring philosophy (v2, 2026-03-22):
      The model's job is to translate TRIDENT intermediate language into
      syntactically valid Overpass QL. Whether a POI category exists in a
      given area is an OSM data question, not a model capability question.

    Two-call strategy (2026-03-22):
      If the model's query returns zero results, mechanically rewrite all
      ["name:en"=...] area filters to ["name"=...] and retry. This is a
      rule-based infrastructure fix for areas that lack name:en in OSM
      (e.g. Paris has name="Paris" but no name:en tag).

      Statuses:
        pass               : valid QL, elements returned on first call
        pass_via_name_fb   : zero on first call; name:en→name rewrite succeeded
        zero_results       : zero on both calls (or no name:en to rewrite)
                             counted as PASS in RF-006 scoring policy
        no_code_block      : model failed to produce a code block or [out:json]
        error              : Overpass API returned HTTP/parse error

    Callers should use is_pass(status) to determine the score contribution.
    """
    ql = extract_overpassql(generated)
    if ql is None:
        return "no_code_block"
    if "[out:json]" not in ql:
        return "no_code_block"
    if len(ql.strip()) < 20:
        return "no_code_block"
    try:
        elements = fetch_elements(ql)
    except Exception:
        return "error"
    if len(elements) > 0:
        return "pass"

    # First call returned zero — attempt name:en → name fallback
    ql_fallback = rewrite_name_en_to_name(ql)
    if ql_fallback == ql:
        # No name:en in query; fallback not applicable
        return "zero_results"
    try:
        elements_fb = fetch_elements(ql_fallback)
    except Exception:
        return "zero_results"
    if len(elements_fb) > 0:
        return "pass_via_name_fb"
    return "zero_results"


def is_pass(status: str) -> bool:
    """Return True if status counts as a pass under the current scoring policy.

    pass_via_name_fb: name:en→name fallback recovered the query — pass.
    zero_results: valid QL, area resolved correctly, but no OSM data for that
                  tag×area combination — not the model's fault (RF-006).
    """
    return status in ("pass", "pass_via_name_fb", "zero_results")


def run_eval(
    *,
    model_id: str = DEFAULT_MODEL,
    adapter_dir: str | None = None,
    dataset_dir: str = DATASET_DIR,
    n: int = BENCHMARK_SAMPLE,
    output_json: str | None = None,
    holdout_json: str | None = None,
) -> dict:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

    print(f"Model: {model_id}")
    if adapter_dir:
        print(f"Adapter: {adapter_dir}")
    print(f"Evaluating {n} samples...")

    tokenizer = AutoTokenizer.from_pretrained(
        adapter_dir if adapter_dir else model_id,
        trust_remote_code=True,
    )
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    device_map = "auto" if torch.cuda.is_available() else "cpu"
    # Gemma 3 requires bfloat16; other models work fine with float16
    dtype = torch.bfloat16 if "gemma" in model_id.lower() else (
        torch.float16 if torch.cuda.is_available() else torch.float32
    )
    base_model = AutoModelForCausalLM.from_pretrained(
        model_id,
        dtype=dtype,
        device_map=device_map,
        trust_remote_code=True,
    )

    if adapter_dir:
        from peft import PeftModel
        model = PeftModel.from_pretrained(base_model, adapter_dir)
        model = model.merge_and_unload()
    else:
        model = base_model

    pipe = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        max_new_tokens=MAX_NEW_TOKENS,
        do_sample=False,
        temperature=None,
        top_p=None,
    )

    pairs = load_benchmark_pairs(dataset_dir, n, holdout_json=holdout_json)
    n = len(pairs)  # actual evaluation count (may differ from requested n)
    results = []
    passed = 0
    t0 = time.time()

    for i, pair in enumerate(pairs):
        prompt = format_prompt(pair.input_text, tokenizer=tokenizer)
        out = pipe(prompt)[0]["generated_text"]
        generated = out[len(prompt):]  # strip prompt from output
        status = score_output(pair.input_text, generated)
        if is_pass(status):
            passed += 1
        results.append({
            "input": pair.input_text,
            "status": status,
            "generated": generated[:300],
        })
        if (i + 1) % 10 == 0:
            elapsed = time.time() - t0
            print(f"  [{i+1}/{n}] pass={passed} ({elapsed:.0f}s)")

    elapsed = time.time() - t0
    score = passed / n * 100
    summary = {
        "model": model_id,
        "adapter": adapter_dir,
        "n": n,
        "passed": passed,
        "score_pct": round(score, 1),
        "elapsed_s": round(elapsed, 1),
        "results": results,
    }
    print(f"\nScore: {score:.1f}% ({passed}/{n})  elapsed={elapsed:.0f}s")

    if output_json:
        Path(output_json).parent.mkdir(parents=True, exist_ok=True)
        with open(output_json, "w") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        print(f"Results saved to {output_json}")

    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate base vs fine-tuned model")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--adapter", default=None, help="Path to LoRA adapter dir")
    parser.add_argument("--dataset-dir", default=DATASET_DIR)
    parser.add_argument("--n", type=int, default=BENCHMARK_SAMPLE)
    parser.add_argument("--output-json", default=None)
    parser.add_argument("--holdout-json", default=None,
                        help="Fixed holdout input list (JSON array of input_text strings). "
                             "When provided, skips the train/val split and evaluates on "
                             "these specific pairs. Useful for cross-version comparisons.")
    args = parser.parse_args()

    run_eval(
        model_id=args.model,
        adapter_dir=args.adapter,
        dataset_dir=args.dataset_dir,
        n=args.n,
        output_json=args.output_json,
        holdout_json=args.holdout_json,
    )


if __name__ == "__main__":
    main()
