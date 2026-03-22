"""Fine-tune Qwen2.5-Coder-0.5B-Instruct with LoRA + SFTTrainer (no Unsloth).

Usage:
    uv run python src/train.py
    uv run python src/train.py --model Qwen/Qwen2.5-Coder-0.5B-Instruct
    uv run python src/train.py --output-dir models/qwen2.5-coder-0.5b-lora
    uv run python src/train.py --epochs 3 --batch-size 4
"""

from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from dataset import DATASET_DIR, build_hf_dataset, load_pairs

DEFAULT_MODEL = "Qwen/Qwen2.5-Coder-0.5B-Instruct"
DEFAULT_OUTPUT_DIR = "models/qwen2.5-coder-0.5b-lora"
DEFAULT_EPOCHS = 3
DEFAULT_BATCH_SIZE = 8
DEFAULT_LR = 2e-4
DEFAULT_MAX_SEQ_LEN = 512

# LoRA hyperparameters
LORA_R = 16
LORA_ALPHA = 32
LORA_DROPOUT = 0.05
LORA_TARGET_MODULES = ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]


def train(
    *,
    model_id: str = DEFAULT_MODEL,
    output_dir: str = DEFAULT_OUTPUT_DIR,
    dataset_dir: str = DATASET_DIR,
    epochs: int = DEFAULT_EPOCHS,
    batch_size: int = DEFAULT_BATCH_SIZE,
    learning_rate: float = DEFAULT_LR,
    max_seq_len: int = DEFAULT_MAX_SEQ_LEN,
) -> None:
    import torch
    from peft import LoraConfig, TaskType, get_peft_model
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from trl import SFTConfig, SFTTrainer

    print(f"Model: {model_id}")
    print(f"Output: {output_dir}")
    print(f"CUDA: {torch.cuda.is_available()}, devices: {torch.cuda.device_count()}")

    # ── tokenizer ─────────────────────────────────────────────────────────────
    tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # ── load dataset ──────────────────────────────────────────────────────────
    print("\nLoading training pairs...")
    pairs = load_pairs(dataset_dir)
    # Filter to AreaWithConcern: only (exclude bare Area: admin stubs)
    pairs = [p for p in pairs if p.input_text.startswith("AreaWithConcern:")]
    print(f"  {len(pairs)} AreaWithConcern pairs")

    hf_ds = build_hf_dataset(pairs, val_ratio=0.05, seed=42, tokenizer=tokenizer)
    print(f"  train={len(hf_ds['train'])}, val={len(hf_ds['validation'])}")

    # ── model ─────────────────────────────────────────────────────────────────
    # Gemma 3 requires bfloat16; other models work fine with float16
    device_map = "auto" if torch.cuda.is_available() else "cpu"
    dtype = torch.bfloat16 if "gemma" in model_id.lower() else (
        torch.float16 if torch.cuda.is_available() else torch.float32
    )
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        dtype=dtype,
        device_map=device_map,
        trust_remote_code=True,
    )
    model.config.use_cache = False

    # ── LoRA via PEFT (not Unsloth) ───────────────────────────────────────────
    lora_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=LORA_R,
        lora_alpha=LORA_ALPHA,
        lora_dropout=LORA_DROPOUT,
        target_modules=LORA_TARGET_MODULES,
        bias="none",
    )
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    # ── SFT config (TrainingArguments + SFT-specific params) ──────────────────
    os.makedirs(output_dir, exist_ok=True)
    sft_config = SFTConfig(
        output_dir=output_dir,
        num_train_epochs=epochs,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        gradient_accumulation_steps=2,
        learning_rate=learning_rate,
        lr_scheduler_type="cosine",
        warmup_steps=int(0.05 * len(hf_ds["train"]) // (batch_size * 2)),
        fp16=torch.cuda.is_available() and "gemma" not in model_id.lower(),
        bf16=torch.cuda.is_available() and "gemma" in model_id.lower(),
        logging_steps=50,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        report_to="none",
        dataloader_drop_last=False,
        # SFT-specific
        max_length=max_seq_len,
        dataset_text_field="text",
    )

    # ── SFTTrainer ────────────────────────────────────────────────────────────
    trainer = SFTTrainer(
        model=model,
        args=sft_config,
        train_dataset=hf_ds["train"],
        eval_dataset=hf_ds["validation"],
        processing_class=tokenizer,
    )

    print("\nStarting training...")
    trainer.train()

    # ── save LoRA adapter (standard PEFT save, no Unsloth) ────────────────────
    print(f"\nSaving LoRA adapter to {output_dir} ...")
    trainer.model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)
    print("Done.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Fine-tune with LoRA + SFTTrainer")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--dataset-dir", default=DATASET_DIR)
    parser.add_argument("--epochs", type=int, default=DEFAULT_EPOCHS)
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE)
    parser.add_argument("--lr", type=float, default=DEFAULT_LR)
    parser.add_argument("--max-seq-len", type=int, default=DEFAULT_MAX_SEQ_LEN)
    args = parser.parse_args()

    train(
        model_id=args.model,
        output_dir=args.output_dir,
        dataset_dir=args.dataset_dir,
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.lr,
        max_seq_len=args.max_seq_len,
    )


if __name__ == "__main__":
    main()
