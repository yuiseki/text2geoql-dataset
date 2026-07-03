"""Tests for llama_server_backend.py — subprocess lifecycle management, mocked."""

import subprocess
from unittest.mock import MagicMock, patch

import pytest

from llama_server_backend import (
    GgufModelSpec,
    build_llama_server_command,
    is_llama_server_available,
    start_llama_server,
    stop_llama_server,
)


class TestGgufModelSpec:
    def test_hf_ref_with_quant(self) -> None:
        spec = GgufModelSpec(hf_repo="org/repo-GGUF", quant="Q4_K_M")
        assert spec.hf_ref() == "org/repo-GGUF:Q4_K_M"

    def test_hf_ref_without_quant(self) -> None:
        spec = GgufModelSpec(hf_repo="org/repo-GGUF")
        assert spec.hf_ref() == "org/repo-GGUF"


class TestBuildLlamaServerCommand:
    def test_includes_hf_ref_and_quant(self) -> None:
        spec = GgufModelSpec(hf_repo="org/repo-GGUF", quant="Q4_K_M", n_ctx=8192)
        cmd = build_llama_server_command(spec, port=12345)
        assert "-hf" in cmd
        assert "org/repo-GGUF:Q4_K_M" in cmd
        assert "8192" in cmd
        assert "12345" in cmd

    def test_omits_quant_suffix_when_none(self) -> None:
        spec = GgufModelSpec(hf_repo="org/repo-GGUF")
        cmd = build_llama_server_command(spec, port=1)
        assert "org/repo-GGUF" in cmd
        assert not any(":" in arg and "org/repo-GGUF:" in arg for arg in cmd)

    def test_includes_extra_args(self) -> None:
        spec = GgufModelSpec(hf_repo="org/repo-GGUF", extra_args=["--verbose"])
        cmd = build_llama_server_command(spec, port=1)
        assert "--verbose" in cmd


class TestIsLlamaServerAvailable:
    def test_true_when_found_on_path(self) -> None:
        with patch("llama_server_backend.shutil.which", return_value="/usr/local/bin/llama-server"):
            assert is_llama_server_available() is True

    def test_false_when_not_found(self) -> None:
        with patch("llama_server_backend.shutil.which", return_value=None):
            assert is_llama_server_available() is False


class TestStopLlamaServer:
    def test_terminates_running_process(self) -> None:
        proc = MagicMock()
        proc.poll.return_value = None
        stop_llama_server(proc)
        proc.terminate.assert_called_once()

    def test_kills_on_terminate_timeout(self) -> None:
        proc = MagicMock()
        proc.poll.return_value = None
        proc.wait.side_effect = [subprocess.TimeoutExpired(cmd="x", timeout=10), None]
        stop_llama_server(proc)
        proc.kill.assert_called_once()

    def test_noop_if_already_exited(self) -> None:
        proc = MagicMock()
        proc.poll.return_value = 0
        stop_llama_server(proc)
        proc.terminate.assert_not_called()


class TestStartLlamaServer:
    def test_raises_when_binary_missing(self) -> None:
        with patch("llama_server_backend.shutil.which", return_value=None):
            with pytest.raises(RuntimeError):
                start_llama_server(GgufModelSpec(hf_repo="org/repo"))

    def test_becomes_healthy_after_polling(self) -> None:
        mock_proc = MagicMock()
        mock_proc.poll.return_value = None

        healthy_response = MagicMock(status_code=200)
        with patch("llama_server_backend.shutil.which", return_value="/usr/local/bin/llama-server"), \
             patch("llama_server_backend.subprocess.Popen", return_value=mock_proc), \
             patch("llama_server_backend.httpx.get", return_value=healthy_response), \
             patch("llama_server_backend.time.sleep"):
            proc, base_url = start_llama_server(GgufModelSpec(hf_repo="org/repo"), port=9999)

        assert proc is mock_proc
        assert base_url == "http://127.0.0.1:9999"

    def test_raises_when_process_exits_early(self) -> None:
        mock_proc = MagicMock()
        mock_proc.poll.return_value = 1
        mock_proc.returncode = 1

        with patch("llama_server_backend.shutil.which", return_value="/usr/local/bin/llama-server"), \
             patch("llama_server_backend.subprocess.Popen", return_value=mock_proc):
            with pytest.raises(RuntimeError):
                start_llama_server(GgufModelSpec(hf_repo="org/repo"), port=9999)

    def test_timeout_raises_and_stops_process(self) -> None:
        mock_proc = MagicMock()
        mock_proc.poll.return_value = None

        with patch("llama_server_backend.shutil.which", return_value="/usr/local/bin/llama-server"), \
             patch("llama_server_backend.subprocess.Popen", return_value=mock_proc), \
             patch("llama_server_backend.httpx.get", side_effect=Exception("connection refused")), \
             patch("llama_server_backend.time.sleep"), \
             patch("llama_server_backend.time.monotonic", side_effect=[0, 1, 200]):
            with pytest.raises(TimeoutError):
                start_llama_server(GgufModelSpec(hf_repo="org/repo"), port=9999, startup_timeout=100.0)

        mock_proc.terminate.assert_called_once()
