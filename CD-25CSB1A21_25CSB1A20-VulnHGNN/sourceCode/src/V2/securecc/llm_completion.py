"""Route chat completions to Groq (cloud) or Ollama (local) when offline."""

from __future__ import annotations

import json
import os
import socket
import urllib.error
import urllib.request
from typing import Any

from .groq_config import groq_api_key, groq_model


def ollama_base_url() -> str:
    raw = (os.environ.get("OLLAMA_BASE_URL") or "http://127.0.0.1:11434").strip().rstrip("/")
    if raw.endswith("/v1"):
        return raw[:-3].rstrip("/")
    return raw


def ollama_model() -> str:
    return (os.environ.get("OLLAMA_MODEL") or "llama3.2:3b").strip()


def ollama_available() -> bool:
    url = f"{ollama_base_url()}/api/tags"
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=2.5) as resp:
            return resp.status == 200
    except (urllib.error.URLError, OSError, TimeoutError, ValueError):
        return False


def has_internet(timeout: float = 2.0) -> bool:
    for host in ("8.8.8.8", "1.1.1.1"):
        try:
            socket.create_connection((host, 53), timeout=timeout)
            return True
        except OSError:
            continue
    return False


def should_use_local_llm() -> bool:
    return not has_internet()


def llm_backend_hint() -> str:
    if should_use_local_llm():
        return "local"
    if groq_api_key() and has_internet():
        return "groq"
    if ollama_available():
        return "local"
    return "none"


def _groq_complete(
    *,
    messages: list[dict[str, str]],
    json_mode: bool,
    temperature: float,
    max_tokens: int | None,
    model: str | None,
) -> tuple[str, str]:
    api_key = groq_api_key()
    if not api_key:
        raise RuntimeError("GROQ_API_KEY not configured")
    try:
        from groq import Groq
    except ImportError as exc:
        raise RuntimeError("groq package not installed") from exc

    kwargs: dict[str, Any] = {
        "model": model or groq_model(),
        "messages": messages,
        "temperature": temperature,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
    if max_tokens is not None:
        kwargs["max_tokens"] = max_tokens

    client = Groq(api_key=api_key)
    response = client.chat.completions.create(**kwargs)
    raw = (response.choices[0].message.content or "").strip()
    if not raw:
        raise RuntimeError("Empty response from Groq")
    return raw, "groq"


def _ollama_complete(
    *,
    messages: list[dict[str, str]],
    json_mode: bool,
    temperature: float,
) -> tuple[str, str]:
    url = f"{ollama_base_url()}/api/chat"
    body: dict[str, Any] = {
        "model": ollama_model(),
        "messages": messages,
        "stream": False,
        "options": {"temperature": temperature},
    }
    if json_mode:
        body["format"] = "json"

    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=600) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        raise RuntimeError(f"Ollama HTTP {exc.code}: {detail}") from exc
    except (urllib.error.URLError, OSError, TimeoutError) as exc:
        raise RuntimeError(
            f"Ollama unreachable at {ollama_base_url()}. "
            "Start Ollama and run: ollama pull " + ollama_model()
        ) from exc

    msg = payload.get("message") or {}
    raw = (msg.get("content") or "").strip()
    if not raw:
        raise RuntimeError("Empty response from Ollama")
    return raw, "ollama"


def complete_chat(
    *,
    messages: list[dict[str, str]],
    json_mode: bool = False,
    temperature: float = 0.2,
    max_tokens: int | None = None,
    model: str | None = None,
) -> tuple[str, str]:
    """Return (assistant_text, backend) where backend is 'groq' or 'ollama'."""
    offline = should_use_local_llm()

    if offline or not groq_api_key():
        if ollama_available():
            return _ollama_complete(messages=messages, json_mode=json_mode, temperature=temperature)
        if offline:
            raise RuntimeError(
                "No internet and Ollama is not reachable. "
                f"Start Ollama at {ollama_base_url()} and pull {ollama_model()}."
            )
        raise RuntimeError(
            "No LLM available: set GROQ_API_KEY or start Ollama "
            f"({ollama_base_url()}, model {ollama_model()})."
        )

    try:
        from groq import Groq  # noqa: F401
    except ImportError:
        if ollama_available():
            return _ollama_complete(messages=messages, json_mode=json_mode, temperature=temperature)
        raise RuntimeError("groq package not installed and Ollama unavailable") from None

    if has_internet():
        try:
            return _groq_complete(
                messages=messages,
                json_mode=json_mode,
                temperature=temperature,
                max_tokens=max_tokens,
                model=model,
            )
        except Exception:
            if ollama_available():
                return _ollama_complete(messages=messages, json_mode=json_mode, temperature=temperature)
            raise

    if ollama_available():
        return _ollama_complete(messages=messages, json_mode=json_mode, temperature=temperature)

    raise RuntimeError("No LLM available (offline and Ollama unreachable).")