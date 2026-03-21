# RD-002: Docility vs Intelligence — Why Older Specialized Models Fine-tune Better

**Date:** 2026-03-21
**Type:** Hypothesis / observation
**Related:** RF-001, RF-002, RF-004, RD-001

## Overview

A counter-intuitive finding from this project: `qwen2.5-coder:3b` (a 3B model from 2024)
achieved the best cost-performance ratio in few-shot inference, outperforming larger and
more recent models. This document explores the hypothesis that recent models are
over-optimized for benchmark diversity at the cost of task-specific fine-tunability.

---

## The Unexpected Result

In few-shot Ollama inference benchmarks:

| Model | Score | Notes |
|-------|-------|-------|
| gemma3:12b + num_ctx=32768 | 100% | Requires 12B, large context |
| qwen3:8b --no-think | 87% | Requires disabling chain-of-thought |
| **qwen2.5-coder:3b** | **80% / 4.9s** | **Best cost-performance** |
| qwen3:8b (default) | ~40% | Chain-of-thought derails output |
| gemma3:1b | 40% | — |
| qwen3.5:27b | OOM / 0% | Unstable on 24GB VRAM |

The 3B model from a previous generation outperforms newer 8B+ models in normal conditions.

---

## Hypothesis: Benchmark Over-optimization Degrades Task Specialization

Modern LLMs are evaluated on increasingly diverse benchmarks (MMLU, HumanEval, MATH,
coding, reasoning, multilingual, etc.). To score well across all of them, training
incorporates:

- **Chain-of-thought RLHF** — models learn to "think before answering"
- **Safety and refusal tuning** — models hedge, add caveats, ask for clarification
- **Instruction-following complexity** — models respond to nuanced multi-turn prompts

For a task like `AreaWithConcern → OverpassQL`, all of these are noise:

- Chain-of-thought produces explanation text instead of code
- Safety tuning may add warnings about map data accuracy
- Instruction complexity causes the model to over-interpret the simple input

`qwen2.5-coder:3b`, being a **code-specialized model from 2024**, has less of this RLHF
overhead. It was trained to produce code, not to reason or explain. Its "narrow" training
is an advantage on a narrow task.

---

## The "Docility vs Intelligence" Framing

We can characterize two distinct properties relevant to fine-tuning:

**Intelligence** — the model's capacity for general reasoning, few-shot adaptation,
and cross-domain transfer. Correlates with scale and diverse training.

**Docility** — the model's tendency to produce the exact output format it was trained on,
without deviation. Inversely correlates with RLHF diversity pressure.

For task-specific fine-tuning on a narrow, deterministic mapping:

- **Intelligence** is largely irrelevant — there is no reasoning required
- **Docility** is essential — the model must produce exactly the right format

This creates a paradox: **more capable general models may be harder to fully specialize.**
Their stronger priors resist overwriting. Smaller, more narrowly pre-trained models
yield completely to the fine-tuning signal.

Observed evidence:
- `gemma3:12b` is "intelligent" enough to solve the task via few-shot (100%)
- `gemma-3-270m-it` is "docile" enough to be fully specialized via fine-tuning (97%)
- `qwen3:8b` requires explicit suppression of intelligence (`--no-think`) to perform well

---

## Implications for Model Selection in Fine-tuning Projects

When selecting a base model for task-specific fine-tuning:

1. **Prefer code/domain-specialized models over general instruction models** — they have
   less RLHF overhead to overcome
2. **Prefer older generation models if the task is narrow** — recent models optimize for
   benchmark diversity, which may add noise for specialized tasks
3. **Small models can be fully overwritten; large models partially resist** — for complete
   task specialization, smaller is sometimes better
4. **"Thinking" models need chain-of-thought suppression for deterministic tasks** — or
   avoid them entirely if the task has no reasoning component

---

## Open Questions

1. **Is this generalizable beyond OverpassQL?** — Does the same pattern hold for other
   structured output tasks (SQL generation, API call generation, DSL compilation)?

2. **At what scale does "intelligence" start helping fine-tuning?** — There may be a
   threshold above which a model is large enough that its priors can be redirected rather
   than overwritten. 7B–13B may be that range.

3. **Does FunctionGemma's function-calling specialization help or hurt?** — Initial
   results (93.3% vs gemma-3-270m-it's 96.7%) suggest it may slightly hurt, possibly
   because function-calling priors impose structure that conflicts with OverpassQL format.
   Retraining on the corrected dataset will clarify this.

4. **Would a model trained from scratch on TRIDENT→OverpassQL alone perform better?** —
   The ultimate test of the "docility" hypothesis: a model with zero prior task knowledge,
   only task-specific training data. Probably impractical at useful scale, but worth noting.
