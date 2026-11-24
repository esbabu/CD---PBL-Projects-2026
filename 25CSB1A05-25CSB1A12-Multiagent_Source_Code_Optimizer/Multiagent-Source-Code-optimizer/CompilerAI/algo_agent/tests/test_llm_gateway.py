"""Tests for the Ollama core gateway using a local stdlib fake Ollama HTTP server."""
from __future__ import annotations

import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

import pytest
from pydantic import BaseModel

from optagent.config import Settings
from optagent.llm.client import (
    LLMClient,
    LLMContextOverflow,
    LLMInvalidOutput,
    LLMUnavailable,
)
from optagent.llm.gateway import OllamaGateway
from optagent.llm.health import clear_health_cache


class _SimpleOut(BaseModel):
    answer: int
    note: str = ""


class _FakeOllamaState:
    def __init__(self) -> None:
        self.models: list[dict[str, Any]] = [
            {"name": "qwen2.5-coder:7b", "size": 4_500_000_000},
            {"name": "llama3.1:8b", "size": 4_800_000_000},
        ]
        self.context_length: int = 8192
        self.reject_schema_format: bool = False
        self.responses: list[dict[str, Any]] = []
        self.delay_s: float = 0.0
        self.requests: list[dict[str, Any]] = []
        self.active_in_flight: int = 0
        self.max_in_flight: int = 0
        self.lock = threading.Lock()


def _start_fake_ollama(state: _FakeOllamaState) -> tuple[ThreadingHTTPServer, str]:
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):
            pass

        def _send(self, code: int, obj: dict[str, Any]):
            body = json.dumps(obj).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            state.requests.append({"method": "GET", "path": self.path})
            if self.path == "/api/version":
                self._send(200, {"version": "0.5.1-fake"})
            elif self.path == "/api/tags":
                self._send(200, {"models": state.models})
            else:
                self._send(404, {"error": "not found"})

        def do_POST(self):
            n = int(self.headers.get("Content-Length", "0"))
            body = json.loads(self.rfile.read(n).decode("utf-8")) if n else {}
            state.requests.append({"method": "POST", "path": self.path, "body": body})

            if self.path == "/api/show":
                self._send(200, {"model_info": {"llama.context_length": state.context_length}})
                return

            if self.path == "/api/chat":
                with state.lock:
                    state.active_in_flight += 1
                    state.max_in_flight = max(state.max_in_flight, state.active_in_flight)
                try:
                    if state.delay_s > 0:
                        time.sleep(state.delay_s)
                    if state.reject_schema_format and isinstance(body.get("format"), dict):
                        self._send(400, {"error": "schema format not supported"})
                        return
                    if state.responses:
                        reply = state.responses.pop(0)
                    else:
                        reply = {
                            "message": {"role": "assistant", "content": json.dumps({"answer": 42, "note": "ok"})},
                            "done_reason": "stop",
                            "prompt_eval_count": 100,
                            "eval_count": 20,
                        }
                    self._send(200, reply)
                finally:
                    with state.lock:
                        state.active_in_flight -= 1
                return

            self._send(404, {"error": "unknown endpoint"})

    srv = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    port = srv.server_address[1]
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    return srv, f"http://127.0.0.1:{port}"


def _settings(tmp_path, base_url: str, **kw) -> Settings:
    defaults = dict(
        ollama_base=base_url,
        runs_dir=str(tmp_path / "runs"),
        llm_mode="assist",
        llm_cache=True,
        llm_connect_timeout_s=2.0,
        llm_read_timeout_s=10.0,
        llm_concurrency=1,
        llm_max_repairs=2,
    )
    defaults.update(kw)
    return Settings(**defaults)


def test_ollama_unreachable(tmp_path):
    clear_health_cache()
    s = _settings(tmp_path, "http://127.0.0.1:19999", llm_connect_timeout_s=0.5)
    gw = OllamaGateway(s)
    with pytest.raises(LLMUnavailable) as exc:
        gw.complete_json("spec", "sys", "user", _SimpleOut)
    assert "not reachable" in str(exc.value).lower() or "19999" in str(exc.value)


def test_ollama_no_models_installed(tmp_path):
    clear_health_cache()
    state = _FakeOllamaState()
    state.models = []
    srv, url = _start_fake_ollama(state)
    try:
        gw = OllamaGateway(_settings(tmp_path, url))
        with pytest.raises(LLMUnavailable) as exc:
            gw.complete_json("spec", "sys", "user", _SimpleOut)
        assert "ollama pull" in str(exc.value).lower()
        # Never calls /api/pull
        assert all("/api/pull" not in r["path"] for r in state.requests)
    finally:
        srv.shutdown()


def test_requested_model_missing_resolves_to_installed(tmp_path):
    clear_health_cache()
    state = _FakeOllamaState()
    srv, url = _start_fake_ollama(state)
    try:
        s = _settings(tmp_path, url, spec_model="ollama_chat/nonexistent:99b", predictor_model="missing-pred:1b")
        gw = OllamaGateway(s)
        out = gw.complete_json("spec", "sys", "hello", _SimpleOut)
        assert out.answer == 42
        assert gw.resolved_roles["spec"] == "qwen2.5-coder:7b"
        assert gw.resolved_roles["predictor"] == "llama3.1:8b"  # different family from spec
        assert all("/api/pull" not in r["path"] for r in state.requests)
    finally:
        srv.shutdown()


def test_schema_rejected_retries_with_json_format(tmp_path):
    clear_health_cache()
    state = _FakeOllamaState()
    state.reject_schema_format = True
    srv, url = _start_fake_ollama(state)
    try:
        gw = OllamaGateway(_settings(tmp_path, url))
        out = gw.complete_json("spec", "sys", "hello", _SimpleOut)
        assert out.answer == 42
        chat_reqs = [r["body"] for r in state.requests if r["path"] == "/api/chat"]
        assert len(chat_reqs) == 2
        assert isinstance(chat_reqs[0]["format"], dict)
        assert chat_reqs[1]["format"] == "json"
    finally:
        srv.shutdown()


def test_invalid_json_then_repair_succeeds(tmp_path):
    clear_health_cache()
    state = _FakeOllamaState()
    state.responses = [
        {"message": {"content": "not valid json at all"}, "done_reason": "stop", "prompt_eval_count": 50, "eval_count": 10},
        {"message": {"content": '{"answer": 99, "note": "repaired"}'}, "done_reason": "stop", "prompt_eval_count": 80, "eval_count": 12},
    ]
    srv, url = _start_fake_ollama(state)
    try:
        client = LLMClient("qwen2.5-coder:7b", _settings(tmp_path, url), "spec")
        out = client.complete_json("sys", "user", _SimpleOut)
        assert out.answer == 99 and out.note == "repaired"
    finally:
        srv.shutdown()


def test_truncated_prompt_detected_and_handled(tmp_path):
    clear_health_cache()
    state = _FakeOllamaState()
    state.context_length = 8192
    # Return tiny prompt_eval_count compared to large prompt -> triggers retry then LLMContextOverflow
    state.responses = [
        {"message": {"content": '{"answer": 1}'}, "done_reason": "stop", "prompt_eval_count": 50, "eval_count": 5},
        {"message": {"content": '{"answer": 1}'}, "done_reason": "stop", "prompt_eval_count": 50, "eval_count": 5},
    ]
    srv, url = _start_fake_ollama(state)
    try:
        gw = OllamaGateway(_settings(tmp_path, url, llm_cache=False, num_ctx_max=8192))
        big_user = "x" * 3000
        with pytest.raises(LLMContextOverflow):
            gw.complete_json("spec", "sys", big_user, _SimpleOut)
    finally:
        srv.shutdown()


def test_done_reason_length_retries_with_higher_num_predict(tmp_path):
    clear_health_cache()
    state = _FakeOllamaState()
    state.responses = [
        {"message": {"content": '{"answer": 1'}, "done_reason": "length", "prompt_eval_count": 40, "eval_count": 100},
        {"message": {"content": '{"answer": 7, "note": "full"}'}, "done_reason": "stop", "prompt_eval_count": 40, "eval_count": 120},
    ]
    srv, url = _start_fake_ollama(state)
    try:
        gw = OllamaGateway(_settings(tmp_path, url, llm_cache=False))
        out = gw.complete_json("spec", "sys", "u", _SimpleOut)
        assert out.answer == 7
        chat_reqs = [r["body"] for r in state.requests if r["path"] == "/api/chat"]
        assert chat_reqs[1]["options"]["num_predict"] > chat_reqs[0]["options"]["num_predict"]
    finally:
        srv.shutdown()


def test_slow_response_within_read_timeout_and_cache_hit(tmp_path):
    clear_health_cache()
    state = _FakeOllamaState()
    state.delay_s = 0.25
    srv, url = _start_fake_ollama(state)
    try:
        gw = OllamaGateway(_settings(tmp_path, url, llm_read_timeout_s=5.0, llm_cache=True))
        out1 = gw.complete_json("spec", "sys", "same prompt", _SimpleOut)
        out2 = gw.complete_json("spec", "sys", "same prompt", _SimpleOut)
        assert out1.answer == 42 and out2.answer == 42
        chat_reqs = [r for r in state.requests if r["path"] == "/api/chat"]
        assert len(chat_reqs) == 1  # second call served from sqlite cache!
        assert gw.trace[-1]["cache_hit"] is True
    finally:
        srv.shutdown()


def test_concurrency_semaphore_limits_parallel_calls(tmp_path):
    clear_health_cache()
    state = _FakeOllamaState()
    state.delay_s = 0.15
    srv, url = _start_fake_ollama(state)
    try:
        s = _settings(tmp_path, url, llm_concurrency=1, llm_cache=False)
        gw = OllamaGateway(s)
        results = []

        def worker(i: int):
            results.append(gw.complete_json("spec", "sys", f"prompt {i}", _SimpleOut).answer)

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert results == [42, 42, 42]
        assert state.max_in_flight == 1
    finally:
        srv.shutdown()


def test_off_mode_makes_zero_http_requests(tmp_path):
    clear_health_cache()
    state = _FakeOllamaState()
    srv, url = _start_fake_ollama(state)
    try:
        gw = OllamaGateway(_settings(tmp_path, url, llm_mode="off"))
        health = gw.check_health()
        assert health.reason_kind == "off"
        with pytest.raises(LLMUnavailable):
            gw.complete_json("spec", "sys", "hello", _SimpleOut)
        assert len(state.requests) == 0
    finally:
        srv.shutdown()


@pytest.mark.ollama
def test_live_ollama_optional(tmp_path):
    """Runs only if a real Ollama daemon is reachable locally."""
    clear_health_cache()
    gw = OllamaGateway(Settings(runs_dir=str(tmp_path / "runs"), llm_connect_timeout_s=1.0))
    health = gw.check_health(force=True)
    if not health.reachable or not health.models:
        pytest.skip("Real Ollama not reachable or no models installed")
    out = gw.complete_json("spec", "Return JSON with integer field answer=1.", "Provide answer=1.", _SimpleOut)
    assert isinstance(out.answer, int)
