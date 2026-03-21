"""Evaluate base vs fine-tuned model on the text2geoql benchmark.

Scores by executing generated OverpassQL against the real Overpass API,
matching the methodology of src/benchmark_models.py for fair comparison.

Scoring:
  pass         : query returns at least 1 element
  zero_results : query runs but returns 0 elements
  no_code_block: no valid OverpassQL block found in output
  error        : Overpass API request failed

Usage:
    # Base model (before FT)
    uv run python examples/lora_finetune/evaluate.py

    # Fine-tuned LoRA adapter (after FT)
    uv run python examples/lora_finetune/evaluate.py --adapter models/qwen2.5-coder-0.5b-lora

    # Save results to JSON
    uv run python examples/lora_finetune/evaluate.py --output-json results/after.json
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
OVERPASS_ENDPOINT = "https://overpass.yuiseki.net/api/interpreter"
BENCHMARK_SAMPLE = 30
MAX_NEW_TOKENS = 256


def load_benchmark_pairs(dataset_dir: str = DATASET_DIR, n: int = BENCHMARK_SAMPLE):
    """Load held-out pairs guaranteed to be outside the training set.

    Uses the same train/val split as train.py (seed=42, val_ratio=0.05).
    """
    from datasets import Dataset

    pairs = load_pairs(dataset_dir)
    pairs = [p for p in pairs if p.input_text.startswith("AreaWithConcern:")]

    texts = [format_prompt(p.input_text, p.output_text) for p in pairs]
    ds = Dataset.from_dict({"text": texts, "idx": list(range(len(pairs)))})
    split = ds.train_test_split(test_size=0.05, seed=42)
    val_indices = split["test"]["idx"]

    import random
    val_pairs = [pairs[i] for i in val_indices]
    random.Random(0).shuffle(val_pairs)
    print(f"  Holdout val set: {len(val_pairs)} pairs")
    return val_pairs[:n]


def extract_overpassql(text: str) -> str | None:
    """Extract OverpassQL block from model output."""
    m = re.search(r"```(?:overpassql)?\s*\n?(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if m:
        return m.group(1).strip()
    m = re.search(r"(\[out:json\].*)", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    return None


def fetch_elements(query: str) -> list[dict]:
    """Execute an Overpass QL query and return the elements list."""
    import httpx
    try:
        response = httpx.get(OVERPASS_ENDPOINT, params={"data": query}, timeout=60)
        return response.json().get("elements", [])
    except Exception as e:
        print(f"    [overpass error] {e}")
        return []


def score_output(generated: str) -> str:
    """Return 'pass' or a failure reason string."""
    ql = extract_overpassql(generated)
    if ql is None or "[out:json]" not in ql or len(ql.strip()) < 20:
        return "no_code_block"
    try:
        elements = fetch_elements(ql)
    except Exception:
        return "error"
    return "pass" if elements else "zero_results"


def run_eval(
    *,
    model_id: str = DEFAULT_MODEL,
    adapter_dir: str | None = None,
    dataset_dir: str = DATASET_DIR,
    n: int = BENCHMARK_SAMPLE,
    output_json: str | None = None,
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
    base_model = AutoModelForCausalLM.from_pretrained(
        model_id,
        dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
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

    pairs = load_benchmark_pairs(dataset_dir, n)
    results = []
    passed = 0
    t0 = time.time()

    for i, pair in enumerate(pairs):
        prompt = format_prompt(pair.input_text)
        out = pipe(prompt)[0]["generated_text"]
        generated = out[len(prompt):]
        status = score_output(generated)
        if status == "pass":
            passed += 1
        results.append({
            "input": pair.input_text,
            "status": status,
            "generated": generated[:300],
        })
        if (i + 1) % 10 == 0:
            print(f"  [{i+1}/{n}] pass={passed} ({time.time()-t0:.0f}s)")

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
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--adapter", default=None)
    parser.add_argument("--dataset-dir", default=DATASET_DIR)
    parser.add_argument("--n", type=int, default=BENCHMARK_SAMPLE)
    parser.add_argument("--output-json", default=None)
    args = parser.parse_args()

    run_eval(
        model_id=args.model,
        adapter_dir=args.adapter,
        dataset_dir=args.dataset_dir,
        n=args.n,
        output_json=args.output_json,
    )


if __name__ == "__main__":
    main()
