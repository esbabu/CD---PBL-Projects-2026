from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

import httpx


class APIError(RuntimeError):
    """A readable error raised for Groq API failures."""


def _load_dotenv() -> None:
    """Load KEY=VALUE entries from the project .env without overriding the environment."""
    candidates = (
        Path.cwd() / ".env",
        Path(__file__).resolve().parents[1] / ".env",
    )
    for path in candidates:
        if not path.is_file():
            continue
        try:
            for raw_line in path.read_text(encoding="utf-8").splitlines():
                line = raw_line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key and value and key not in os.environ:
                    os.environ[key] = value
        except OSError:
            # Environment variables can still provide configuration.
            continue


def _extract_json(content: str) -> dict[str, Any]:
    content = (content or "").strip()
    content = re.sub(r"^```(?:json)?\s*", "", content, flags=re.IGNORECASE)
    content = re.sub(r"\s*```$", "", content)

    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        start = content.find("{")
        end = content.rfind("}")
        if start < 0 or end <= start:
            raise APIError("Groq returned no JSON object.")
        try:
            data = json.loads(content[start:end + 1])
        except json.JSONDecodeError as exc:
            raise APIError(f"Groq returned malformed JSON: {exc}") from exc

    if not isinstance(data, dict):
        raise APIError("Groq response must be a JSON object.")
    return data


class GroqClient:
    """Small Groq Chat Completions client. Reads GROQ_API_KEY from .env or environment."""

    BASE_URL = "https://api.groq.com/openai/v1/chat/completions"

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        timeout_s: float = 120.0,
    ) -> None:
        _load_dotenv()
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.model = model or os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
        self.timeout_s = timeout_s

    def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> dict[str, Any]:
        if not self.api_key:
            raise APIError(
                "Groq API key is missing. Add GROQ_API_KEY to your .env file "
                "or environment. Do not put the key in source code."
            )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.1,
            "response_format": {"type": "json_object"},
        }

        try:
            with httpx.Client(timeout=self.timeout_s) as client:
                response = client.post(
                    self.BASE_URL,
                    headers=headers,
                    json=payload,
                )
        except httpx.TimeoutException as exc:
            raise APIError(
                f"Groq request timed out after {self.timeout_s:g} seconds."
            ) from exc
        except httpx.HTTPError as exc:
            raise APIError(f"Could not connect to Groq: {exc}") from exc

        if response.status_code != 200:
            try:
                body = response.json()
                error = body.get("error", {})
                detail = error.get("message", response.text) if isinstance(error, dict) else response.text
            except (ValueError, AttributeError):
                detail = response.text
            # Do not include headers or secrets in the error.
            raise APIError(
                f"Groq API returned HTTP {response.status_code}: {str(detail)[:600]}"
            )

        try:
            body = response.json()
            content = body["choices"][0]["message"]["content"]
        except (ValueError, KeyError, IndexError, TypeError) as exc:
            raise APIError("Groq returned an unexpected response structure.") from exc

        if not isinstance(content, str) or not content.strip():
            raise APIError("Groq returned an empty response.")

        return _extract_json(content)
