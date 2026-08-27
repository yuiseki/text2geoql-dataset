"""Serve a LoRA adapter behind the OpenAI chat-completions endpoint.

The inner layer is measured through TRIDENT, not by calling a model directly:
TRIDENT owns the prompt and the parsing, and measuring anything else measures
something that will drift from it within a week. TRIDENT speaks to an
OpenAI-compatible server, so a fine-tuned adapter needs one to be measurable
at all.

llama-server is the production path and this is not a substitute for it. It
exists so a first read on an adapter costs a minute rather than a conversion
to GGUF, which is worth doing only once the adapter is worth deploying.

    python examples/lora_finetune/serve_adapter.py \\
        --adapter models/inner-coder-0.5b-lora --port 18095

    # .env.local
    LLAMA_CPP_INNER_BASE_URL=http://127.0.0.1:18095/v1
    TRIDENT_INNER_PROMPT_STYLE=finetuned
"""

from __future__ import annotations

import argparse
import json
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

MODEL_NAME = "trident-inner-ft"


def build_generator(base: str, adapter: str | None, device: str):
    import torch
    from peft import PeftModel
    from transformers import AutoModelForCausalLM, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(base, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        base,
        dtype=torch.float16 if device.startswith("cuda") else torch.float32,
        trust_remote_code=True,
    )
    if adapter:
        model = PeftModel.from_pretrained(model, adapter)
        model = model.merge_and_unload()
    model.to(device)
    model.eval()

    def generate(messages: list[dict], max_new_tokens: int) -> str:
        text = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        inputs = tokenizer(text, return_tensors="pt").to(device)
        with torch.no_grad():
            out = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=False,
                pad_token_id=tokenizer.pad_token_id,
            )
        # Only what was added; echoing the prompt back is a failure mode the
        # deep layer already showed once.
        return tokenizer.decode(
            out[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True
        ).strip()

    return generate


def make_handler(generate):
    class Handler(BaseHTTPRequestHandler):
        def _send(self, code: int, payload: dict) -> None:
            body = json.dumps(payload).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args) -> None:  # quiet
            pass

        def do_GET(self) -> None:
            if self.path.rstrip("/").endswith("/models"):
                self._send(200, {"object": "list", "data": [
                    {"id": MODEL_NAME, "object": "model", "owned_by": "local"}
                ]})
            else:
                self._send(404, {"error": {"message": "not found"}})

        def do_POST(self) -> None:
            if not self.path.rstrip("/").endswith("/chat/completions"):
                self._send(404, {"error": {"message": "not found"}})
                return
            length = int(self.headers.get("Content-Length") or 0)
            try:
                request = json.loads(self.rfile.read(length) or b"{}")
            except json.JSONDecodeError:
                self._send(400, {"error": {"message": "bad json"}})
                return
            messages = request.get("messages") or []
            max_new = int(request.get("max_tokens") or 512)
            try:
                text = generate(messages, max_new)
            except Exception as exc:  # a failure here is a result, not a crash
                self._send(500, {"error": {"message": f"{type(exc).__name__}: {exc}"}})
                return
            self._send(200, {
                "id": "chatcmpl-local",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": request.get("model") or MODEL_NAME,
                "choices": [{
                    "index": 0,
                    "message": {"role": "assistant", "content": text},
                    "finish_reason": "stop",
                }],
                "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
            })

    return Handler


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--base", default="Qwen/Qwen2.5-Coder-0.5B-Instruct")
    parser.add_argument("--adapter", help="omit to serve the base model")
    parser.add_argument("--port", type=int, default=18095)
    parser.add_argument("--device", default="cuda:1")
    args = parser.parse_args()

    print(f"loading {args.base}" + (f" + {args.adapter}" if args.adapter else " (base only)"))
    generate = build_generator(args.base, args.adapter, args.device)
    server = ThreadingHTTPServer(("127.0.0.1", args.port), make_handler(generate))
    print(f"listening on http://127.0.0.1:{args.port}/v1")
    server.serve_forever()


if __name__ == "__main__":
    main()
