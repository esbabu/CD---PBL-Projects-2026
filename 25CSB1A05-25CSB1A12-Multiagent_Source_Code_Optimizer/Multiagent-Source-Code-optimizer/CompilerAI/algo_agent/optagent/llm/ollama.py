"""Native Ollama HTTP backend (`POST /api/chat`, `POST /api/show`).

Never installs, pulls, or starts Ollama or models. All failures surface as typed exceptions.
"""
from __future__ import annotations

import copy
import threading
import time
from typing import Any

import httpx


class LLMError(RuntimeError):
    """Base error for all LLM gateway failures."""


class LLMUnavailable(LLMError):
    """Ollama service is unreachable, has no models, or returned 5xx/connection error."""


class LLMTimeout(LLMError):
    """Ollama request timed out."""


class LLMInvalidOutput(LLMError):
    """Model output was truncated (`done_reason=length`), non-JSON, or schema-invalid."""


class LLMContextOverflow(LLMError):
    """Prompt exceeds model context window even after slicing/num_ctx adjustment."""


def inline_json_schema_defs(schema: dict[str, Any]) -> dict[str, Any]:
    """Inline `$defs` / `definitions` `$ref` nodes so Ollama structured outputs accept the schema."""
    root = copy.deepcopy(schema)
    defs = root.pop("$defs", None) or root.pop("definitions", None) or {}

    def _resolve(node: Any, seen: frozenset[str] = frozenset()) -> Any:
        if isinstance(node, dict):
            if "$ref" in node and isinstance(node["$ref"], str):
                ref = node["$ref"]
                name = ref.rsplit("/", 1)[-1]
                if name in defs and name not in seen:
                    merged = _resolve(copy.deepcopy(defs[name]), seen | {name})
                    # Preserve sibling metadata (like description)
                    for k, v in node.items():
                        if k != "$ref" and k not in merged:
                            merged[k] = _resolve(v, seen)
                    return merged
            return {k: _resolve(v, seen) for k, v in node.items()}
        if isinstance(node, list):
            return [_resolve(item, seen) for item in node]
        return node

    return _resolve(root)


class OllamaBackend:
    """Thread-safe HTTP client for a pre-existing local Ollama server."""

    _semaphores_lock = threading.Lock()
    _semaphores: dict[int, threading.Semaphore] = {}
    _context_cache: dict[tuple[str, str], int] = {}
    _warmed_models: set[tuple[str, str]] = set()

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        connect_timeout_s: float = 5.0,
        read_timeout_s: float = 600.0,
        concurrency: int = 1,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.connect_timeout_s = connect_timeout_s
        self.read_timeout_s = read_timeout_s
        self.concurrency = max(1, concurrency)

    def _semaphore(self) -> threading.Semaphore:
        with self._semaphores_lock:
            sem = self._semaphores.get(self.concurrency)
            if sem is None:
                sem = threading.Semaphore(self.concurrency)
                self._semaphores[self.concurrency] = sem
            return sem

    def get_model_context_length(self, model: str, default: int = 8192) -> int:
        key = (self.base_url, model)
        if key in self._context_cache:
            return self._context_cache[key]
        timeout = httpx.Timeout(connect=self.connect_timeout_s, read=15.0, write=10.0, pool=10.0)
        ctx_len = default
        try:
            with httpx.Client(timeout=timeout) as client:
                resp = client.post(f"{self.base_url}/api/show", json={"name": model})
                if resp.status_code == 200:
                    data = resp.json()
                    model_info = data.get("model_info") or {}
                    for k, v in model_info.items():
                        if k.endswith(".context_length") and isinstance(v, int) and v > 0:
                            ctx_len = v
                            break
        except Exception:
            pass
        self._context_cache[key] = ctx_len
        return ctx_len

    def warmup_once(self, model: str) -> None:
        key = (self.base_url, model)
        if key in self._warmed_models:
            return
        self._warmed_models.add(key)

    def chat(
        self,
        model: str,
        messages: list[dict[str, str]],
        *,
        options: dict[str, Any],
        format_spec: dict[str, Any] | str | None = None,
        keep_alive: str = "30m",
    ) -> dict[str, Any]:
        """Send a single POST /api/chat request under the process concurrency semaphore."""
        payload: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "stream": False,
            "keep_alive": keep_alive,
            "options": options,
        }
        if format_spec is not None:
            payload["format"] = format_spec

        timeout = httpx.Timeout(
            connect=self.connect_timeout_s,
            read=self.read_timeout_s,
            write=30.0,
            pool=self.connect_timeout_s,
        )

        with self._semaphore():
            self.warmup_once(model)
            t0 = time.time()
            try:
                with httpx.Client(timeout=timeout) as client:
                    resp = client.post(f"{self.base_url}/api/chat", json=payload)
            except httpx.TimeoutException as exc:
                raise LLMTimeout(f"Ollama /api/chat timed out after {round(time.time() - t0, 2)}s: {exc}") from exc
            except httpx.ConnectError as exc:
                raise LLMUnavailable(f"Cannot connect to Ollama at {self.base_url}: {exc}") from exc
            except httpx.HTTPError as exc:
                raise LLMUnavailable(f"Ollama HTTP transport error at {self.base_url}: {exc}") from exc

        if resp.status_code == 400 and isinstance(format_spec, dict):
            # Retry once with format="json" when server rejects JSON Schema format
            return self.chat(model, messages, options=options, format_spec="json", keep_alive=keep_alive)

        if resp.status_code == 404:
            raise LLMUnavailable(f"Ollama model '{model}' not found at {self.base_url} (HTTP 404). Pull it manually with `ollama pull {model}`.")
        if resp.status_code >= 500:
            raise LLMUnavailable(f"Ollama server error HTTP {resp.status_code}: {resp.text[:300]}")
        if resp.status_code >= 400:
            raise LLMInvalidOutput(f"Ollama rejected request HTTP {resp.status_code}: {resp.text[:300]}")

        try:
            data = resp.json()
        except Exception as exc:
            raise LLMInvalidOutput(f"Non-JSON HTTP body from Ollama: {resp.text[:200]}") from exc
        return data
