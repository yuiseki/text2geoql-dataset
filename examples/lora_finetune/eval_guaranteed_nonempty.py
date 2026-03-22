"""Guaranteed-nonempty evaluation: strict zero_results = fail.

Tests whether fine-tuned models correctly resolve geographic scope — not just
syntax validity but semantic correctness of the area query.

Methodology:
  1. A curated list of (input, verification_query) pairs is defined.
  2. At evaluation time, each verification_query is pre-run against Overpass
     to confirm the area+POI combination actually returns data. If a pair
     cannot be verified (returns 0 elements), it is skipped with a warning.
  3. Models are evaluated on the confirmed pairs. zero_results = FAIL,
     because we know data exists — a zero return means area resolution failed.

This directly measures: does the model generate a query that correctly scopes
the geographic area, not merely one that is syntactically valid?

Usage:
    uv run python src/eval_guaranteed_nonempty.py \\
        --model google/gemma-3-270m-it \\
        --adapter models/gemma3-270m-lora-v3 \\
        --output-json results/v3-gemma3-guaranteed.json
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

from dataset import SYSTEM_PROMPT

OVERPASS_ENDPOINT = "https://overpass.yuiseki.net/api/interpreter"
MAX_NEW_TOKENS = 256

# ---------------------------------------------------------------------------
# Curated test pairs with pre-verification queries.
#
# verification_query: a known-correct Overpass QL that we expect to return
#   > 0 elements, confirming the POI category exists in that area.
#   Written with well-known OSM name tags to maximise reliability.
#
# input: the TRIDENT intermediate language input fed to the model.
# ---------------------------------------------------------------------------
GUARANTEED_PAIRS = [
    # --- Europe: major cities, common POI types ---
    {
        "input": "AreaWithConcern: Paris, Île-de-France, France; Cafes",
        "verification_query": (
            '[out:json][timeout:30];\n'
            'area["name"="Paris"]["admin_level"="8"]->.a;\n'
            '(nwr["amenity"="cafe"](area.a););\n'
            'out count;'
        ),
    },
    {
        "input": "AreaWithConcern: Paris, Île-de-France, France; Museums",
        "verification_query": (
            '[out:json][timeout:30];\n'
            'area["name"="Paris"]["admin_level"="8"]->.a;\n'
            '(nwr["tourism"="museum"](area.a););\n'
            'out count;'
        ),
    },
    {
        "input": "AreaWithConcern: Paris, Île-de-France, France; Hotels",
        "verification_query": (
            '[out:json][timeout:30];\n'
            'area["name"="Paris"]["admin_level"="8"]->.a;\n'
            '(nwr["tourism"="hotel"](area.a););\n'
            'out count;'
        ),
    },
    {
        "input": "AreaWithConcern: London, United Kingdom; Cafes",
        "verification_query": (
            '[out:json][timeout:30];\n'
            'area["name"="London"]["admin_level"="6"]->.a;\n'
            '(nwr["amenity"="cafe"](area.a););\n'
            'out count;'
        ),
    },
    {
        "input": "AreaWithConcern: London, United Kingdom; Museums",
        "verification_query": (
            '[out:json][timeout:30];\n'
            'area["name"="London"]["admin_level"="6"]->.a;\n'
            '(nwr["tourism"="museum"](area.a););\n'
            'out count;'
        ),
    },
    {
        "input": "AreaWithConcern: Berlin, Germany; Cafes",
        "verification_query": (
            '[out:json][timeout:30];\n'
            'area["name"="Berlin"]["admin_level"="4"]->.a;\n'
            '(nwr["amenity"="cafe"](area.a););\n'
            'out count;'
        ),
    },
    {
        "input": "AreaWithConcern: Berlin, Germany; Museums",
        "verification_query": (
            '[out:json][timeout:30];\n'
            'area["name"="Berlin"]["admin_level"="4"]->.a;\n'
            '(nwr["tourism"="museum"](area.a););\n'
            'out count;'
        ),
    },
    {
        "input": "AreaWithConcern: Rome, Italy; Restaurants",
        "verification_query": (
            '[out:json][timeout:30];\n'
            'area["name"="Roma"]["admin_level"="8"]->.a;\n'
            '(nwr["amenity"="restaurant"](area.a););\n'
            'out count;'
        ),
    },
    {
        "input": "AreaWithConcern: Amsterdam, Netherlands; Cafes",
        "verification_query": (
            '[out:json][timeout:30];\n'
            'area["name"="Amsterdam"]["admin_level"="8"]->.a;\n'
            '(nwr["amenity"="cafe"](area.a););\n'
            'out count;'
        ),
    },
    # --- Seen regions (control) ---
    {
        "input": "AreaWithConcern: Shinjuku, Tokyo, Japan; Convenience stores",
        "verification_query": (
            '[out:json][timeout:30];\n'
            'area["name:en"="Tokyo"]->.outer;\n'
            'area["name:en"="Shinjuku"]->.inner;\n'
            '(nwr["shop"="convenience"](area.inner)(area.outer););\n'
            'out count;'
        ),
    },
    {
        "input": "AreaWithConcern: Shibuya, Tokyo, Japan; Cafes",
        "verification_query": (
            '[out:json][timeout:30];\n'
            'area["name:en"="Tokyo"]->.outer;\n'
            'area["name:en"="Shibuya"]->.inner;\n'
            '(nwr["amenity"="cafe"](area.inner)(area.outer););\n'
            'out count;'
        ),
    },
    {
        "input": "AreaWithConcern: Chiyoda, Tokyo, Japan; Hotels",
        "verification_query": (
            '[out:json][timeout:30];\n'
            'area["name:en"="Tokyo"]->.outer;\n'
            'area["name:en"="Chiyoda"]->.inner;\n'
            '(nwr["tourism"="hotel"](area.inner)(area.outer););\n'
            'out count;'
        ),
    },
    # --- Other unseen regions ---
    {
        "input": "AreaWithConcern: Sydney, New South Wales, Australia; Cafes",
        "verification_query": (
            '[out:json][timeout:30];\n'
            'area["name"="Sydney"]["admin_level"="6"]->.a;\n'
            '(nwr["amenity"="cafe"](area.a););\n'
            'out count;'
        ),
    },
    {
        "input": "AreaWithConcern: Mumbai, Maharashtra, India; Hotels",
        "verification_query": (
            '[out:json][timeout:30];\n'
            'area["name"="Mumbai"]["admin_level"="6"]->.a;\n'
            '(nwr["tourism"="hotel"](area.a););\n'
            'out count;'
        ),
    },
    {
        "input": "AreaWithConcern: São Paulo, Brazil; Restaurants",
        "verification_query": (
            '[out:json][timeout:30];\n'
            'area["name"="São Paulo"]["admin_level"="8"]->.a;\n'
            '(nwr["amenity"="restaurant"](area.a););\n'
            'out count;'
        ),
    },
    {
        "input": "AreaWithConcern: Cairo, Egypt; Mosques",
        "verification_query": (
            '[out:json][timeout:30];\n'
            'area["name:en"="Cairo"]["admin_level"="4"]->.a;\n'
            '(nwr["amenity"="place_of_worship"]["religion"="islam"](area.a););\n'
            'out count;'
        ),
    },
    {
        "input": "AreaWithConcern: Seoul, South Korea; Cafes",
        "verification_query": (
            '[out:json][timeout:30];\n'
            'area["name:en"="Seoul"]->.a;\n'
            '(nwr["amenity"="cafe"](area.a););\n'
            'out count;'
        ),
    },
    {
        "input": "AreaWithConcern: Gangnam-gu, Seoul, South Korea; Restaurants",
        "verification_query": (
            '[out:json][timeout:30];\n'
            'area["name:en"="Seoul"]->.outer;\n'
            'area["name:en"="Gangnam-gu"]->.inner;\n'
            '(nwr["amenity"="restaurant"](area.inner)(area.outer););\n'
            'out count;'
        ),
    },
]


def fetch_elements(query: str) -> list[dict]:
    import httpx
    try:
        response = httpx.get(OVERPASS_ENDPOINT, params={"data": query}, timeout=60)
        data = response.json()
        # Handle both full element list and count response
        if "elements" in data:
            return data["elements"]
        return []
    except Exception as e:
        print(f"    [overpass error] {e}")
        return []


def fetch_count(query: str) -> int:
    """Run a verification query (out count) and return the element count."""
    import httpx
    try:
        response = httpx.get(OVERPASS_ENDPOINT, params={"data": query}, timeout=60)
        data = response.json()
        elements = data.get("elements", [])
        if elements and elements[0].get("type") == "count":
            return int(elements[0].get("tags", {}).get("total", 0))
        return len(elements)
    except Exception as e:
        print(f"    [verify error] {e}")
        return -1


def extract_overpassql(text: str) -> str | None:
    m = re.search(r"```(?:overpassql)?\s*\n?(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if m:
        return m.group(1).strip()
    m = re.search(r"(\[out:json\].*)", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    return None


def rewrite_name_en_to_name(ql: str) -> str:
    """Replace ["name:en"=...] with ["name"=...] in area filters."""
    return re.sub(r'\["name:en"=', '["name"=', ql)


def score_strict(generated: str) -> tuple[str, str | None]:
    """Strict scoring with two-call name:en → name fallback.

    Returns (status, extracted_query_used).
    Status values:
      pass             : elements returned on first call
      pass_via_name_fb : zero on first call; name fallback succeeded
      zero_results     : zero on both calls — genuine area resolution failure
      no_code_block    : no valid QL block generated
      error            : Overpass API error
    """
    ql = extract_overpassql(generated)
    if ql is None or "[out:json]" not in ql or len(ql.strip()) < 20:
        return "no_code_block", None
    try:
        elements = fetch_elements(ql)
    except Exception:
        return "error", ql
    if len(elements) > 0:
        return "pass", ql

    # Two-call: rewrite name:en → name and retry
    ql_fallback = rewrite_name_en_to_name(ql)
    if ql_fallback == ql:
        return "zero_results", ql
    try:
        elements_fb = fetch_elements(ql_fallback)
    except Exception:
        return "zero_results", ql
    if len(elements_fb) > 0:
        return "pass_via_name_fb", ql_fallback
    return "zero_results", ql


def run_guaranteed_eval(
    *,
    model_id: str,
    adapter_dir: str | None = None,
    output_json: str | None = None,
    skip_verify: bool = False,
    confirmed_pairs_json: str | None = None,
) -> dict:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

    print(f"Model: {model_id}")
    if adapter_dir:
        print(f"Adapter: {adapter_dir}")

    # ── Step 1: load or pre-verify pairs ─────────────────────────────────────
    if confirmed_pairs_json is not None:
        # Load pre-confirmed pairs from external JSON (skips live pre-verification)
        with open(confirmed_pairs_json) as f:
            confirmed_pairs = json.load(f)
        print(f"\nLoaded {len(confirmed_pairs)} confirmed pairs from {confirmed_pairs_json}\n")
    elif skip_verify:
        confirmed_pairs = list(GUARANTEED_PAIRS)
        print(f"\nSkipping verification — using all {len(confirmed_pairs)} pairs.\n")
    else:
        print("\nPre-verifying pairs against Overpass API...")
        confirmed_pairs = []
        for pair in GUARANTEED_PAIRS:
            count = fetch_count(pair["verification_query"])
            if count > 0:
                confirmed_pairs.append(pair)
                print(f"  ✓ ({count:>5} elements) {pair['input']}")
            elif count == 0:
                print(f"  ✗ (0 elements — SKIPPED) {pair['input']}")
            else:
                print(f"  ? (verify error — SKIPPED) {pair['input']}")
        print(f"\nConfirmed {len(confirmed_pairs)}/{len(GUARANTEED_PAIRS)} pairs for evaluation.\n")

    # ── Step 2: load model ────────────────────────────────────────────────────
    tokenizer = AutoTokenizer.from_pretrained(
        adapter_dir if adapter_dir else model_id,
        trust_remote_code=True,
    )
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    device_map = "auto" if torch.cuda.is_available() else "cpu"
    dtype = torch.bfloat16 if "gemma" in model_id.lower() else (
        torch.float16 if torch.cuda.is_available() else torch.float32
    )
    base_model = AutoModelForCausalLM.from_pretrained(
        model_id, dtype=dtype, device_map=device_map, trust_remote_code=True,
    )
    if adapter_dir:
        from peft import PeftModel
        model = PeftModel.from_pretrained(base_model, adapter_dir)
        model = model.merge_and_unload()
    else:
        model = base_model

    pipe = pipeline(
        "text-generation", model=model, tokenizer=tokenizer,
        max_new_tokens=MAX_NEW_TOKENS, do_sample=False,
        temperature=None, top_p=None,
    )

    # ── Step 3: evaluate ──────────────────────────────────────────────────────
    results = []
    passed = 0
    n = len(confirmed_pairs)
    t0 = time.time()

    for i, pair in enumerate(confirmed_pairs):
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": pair["input"]},
        ]
        prompt = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        out = pipe(prompt)[0]["generated_text"]
        generated = out[len(prompt):]
        status, query = score_strict(generated)
        if status in ("pass", "pass_via_name_fb"):
            passed += 1

        results.append({
            "input": pair["input"],
            "status": status,
            "query": query,
            "generated": generated[:500],
        })

        marker = "✓" if status in ("pass", "pass_via_name_fb") else "✗"
        label = f"{status:20s}"
        elapsed = time.time() - t0
        print(f"  {marker} [{i+1}/{n}] {label}  {pair['input']}  ({elapsed:.0f}s)")

    elapsed = time.time() - t0
    score = passed / n * 100 if n > 0 else 0.0

    # Breakdown: seen (Tokyo control) vs unseen
    seen = [r for r in results if "Tokyo, Japan" in r["input"] or "Seoul, South Korea" in r["input"]]
    unseen = [r for r in results if r not in seen]
    seen_pass = sum(1 for r in seen if r["status"] in ("pass", "pass_via_name_fb"))
    unseen_pass = sum(1 for r in unseen if r["status"] in ("pass", "pass_via_name_fb"))

    summary = {
        "model": model_id,
        "adapter": adapter_dir,
        "scoring": "strict (zero_results=fail)",
        "n_total": n,
        "n_seen": len(seen),
        "n_unseen": len(unseen),
        "passed_total": passed,
        "passed_seen": seen_pass,
        "passed_unseen": unseen_pass,
        "score_total_pct": round(score, 1),
        "score_seen_pct": round(seen_pass / len(seen) * 100, 1) if seen else 0,
        "score_unseen_pct": round(unseen_pass / len(unseen) * 100, 1) if unseen else 0,
        "elapsed_s": round(elapsed, 1),
        "results": results,
    }

    print(f"\nTotal:  {score:.1f}% ({passed}/{n})  [strict: zero_results=fail]")
    print(f"Seen:   {seen_pass}/{len(seen)}")
    print(f"Unseen: {unseen_pass}/{len(unseen)}")

    if output_json:
        Path(output_json).parent.mkdir(parents=True, exist_ok=True)
        with open(output_json, "w") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        print(f"Results saved to {output_json}")

    return summary


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Guaranteed-nonempty strict evaluation"
    )
    parser.add_argument("--model", default="google/gemma-3-270m-it")
    parser.add_argument("--adapter", default=None)
    parser.add_argument("--output-json", default=None)
    parser.add_argument(
        "--skip-verify", action="store_true",
        help="Skip Overpass pre-verification step (use all pairs as-is)"
    )
    parser.add_argument(
        "--confirmed-pairs-json", default=None,
        help="Path to pre-confirmed pairs JSON (from precheck_candidates.py). "
             "Skips live pre-verification and uses this fixed list instead."
    )
    args = parser.parse_args()

    run_guaranteed_eval(
        model_id=args.model,
        adapter_dir=args.adapter,
        output_json=args.output_json,
        skip_verify=args.skip_verify,
        confirmed_pairs_json=args.confirmed_pairs_json,
    )


if __name__ == "__main__":
    main()
