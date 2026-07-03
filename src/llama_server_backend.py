"""Lifecycle management for llama-server subprocesses.

Complements the Ollama-based generation path in generate_overpassql.py.
Used by benchmark_models.py to serve GGUF models (e.g. Apertus) via
llama.cpp's llama-server HTTP API, without touching the existing
Ollama-based flow.
"""

from __future__ import annotations

import shutil
import socket
import subprocess
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator

import httpx

LLAMA_SERVER_BIN_DEFAULT = "llama-server"
DEFAULT_STARTUP_TIMEOUT = 120.0
DEFAULT_HEALTH_POLL_INTERVAL = 0.5


@dataclass
class GgufModelSpec:
    """Describes a GGUF model to be served by llama-server via -hf autodownload."""

    hf_repo: str
    quant: str | None = None
    n_ctx: int = 4096
    n_gpu_layers: int = 99  # Metal/CUDA offload; harmless on CPU-only hosts
    extra_args: list[str] = field(default_factory=list)

    def hf_ref(self) -> str:
        return f"{self.hf_repo}:{self.quant}" if self.quant else self.hf_repo


def is_llama_server_available(bin_name: str = LLAMA_SERVER_BIN_DEFAULT) -> bool:
    """Return True if the llama-server binary is found on PATH."""
    return shutil.which(bin_name) is not None


def _find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def build_llama_server_command(
    spec: GgufModelSpec,
    port: int,
    bin_name: str = LLAMA_SERVER_BIN_DEFAULT,
) -> list[str]:
    """Build the llama-server argv for the given model spec. Pure function for testability."""
    return [
        bin_name,
        "-hf", spec.hf_ref(),
        "-c", str(spec.n_ctx),
        "-ngl", str(spec.n_gpu_layers),
        "--port", str(port),
        "--host", "127.0.0.1",
        "--no-webui",
        *spec.extra_args,
    ]


def start_llama_server(
    spec: GgufModelSpec,
    *,
    port: int | None = None,
    bin_name: str = LLAMA_SERVER_BIN_DEFAULT,
    startup_timeout: float = DEFAULT_STARTUP_TIMEOUT,
    log_path: str | Path | None = None,
) -> tuple[subprocess.Popen, str]:
    """Start llama-server for spec; block until /health is ready. Returns (proc, base_url)."""
    if not is_llama_server_available(bin_name):
        raise RuntimeError(f"{bin_name} not found on PATH — install llama.cpp first")

    port = port or _find_free_port()
    cmd = build_llama_server_command(spec, port, bin_name)
    log_file = open(log_path, "w") if log_path else subprocess.DEVNULL
    proc = subprocess.Popen(cmd, stdout=log_file, stderr=subprocess.STDOUT)
    base_url = f"http://127.0.0.1:{port}"

    deadline = time.monotonic() + startup_timeout
    while time.monotonic() < deadline:
        if proc.poll() is not None:
            raise RuntimeError(f"llama-server exited early (code {proc.returncode}); see {log_path}")
        try:
            if httpx.get(f"{base_url}/health", timeout=2.0).status_code == 200:
                return proc, base_url
        except Exception:
            pass
        time.sleep(DEFAULT_HEALTH_POLL_INTERVAL)

    stop_llama_server(proc)
    raise TimeoutError(f"llama-server did not become healthy within {startup_timeout}s")


def stop_llama_server(proc: subprocess.Popen, *, timeout: float = 10.0) -> None:
    """Terminate proc gracefully, escalating to kill if it doesn't exit in time."""
    if proc.poll() is not None:
        return
    proc.terminate()
    try:
        proc.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=timeout)


@contextmanager
def llama_server_session(
    spec: GgufModelSpec,
    *,
    port: int | None = None,
    bin_name: str = LLAMA_SERVER_BIN_DEFAULT,
    startup_timeout: float = DEFAULT_STARTUP_TIMEOUT,
    log_path: str | Path | None = None,
) -> Iterator[str]:
    """Start llama-server, yield base_url, guarantee shutdown even on exception."""
    proc, base_url = start_llama_server(
        spec, port=port, bin_name=bin_name, startup_timeout=startup_timeout, log_path=log_path,
    )
    try:
        yield base_url
    finally:
        stop_llama_server(proc)
