"""Provider Adapter for centralized model provider access, telemetry, and error sanitization."""

from __future__ import annotations

import logging
import re
from types import SimpleNamespace
from typing import Any, Dict, List, Optional

from backend.config import AppConfig
from backend.model_provider import (
    MODEL_NAME,
    create_model_client,
    provider_display_name,
    provider_ready,
)
from backend.provider_errors import classify_provider_error

logger = logging.getLogger(__name__)

# Pattern to detect potential API keys / bearer tokens in error text
_SECRET_PATTERN = re.compile(
    r"(?:bearer\s+[a-zA-Z0-9_\-\.]{6,}|(?:api[_-]?key|token|password|secret)[\s:=]+['\"]?[a-zA-Z0-9_\-\.]{8,}['\"]?)",
    re.IGNORECASE,
)


def redact_secrets(text: str) -> str:
    """Sanitize strings so secret tokens or bearer headers are never logged or exposed."""
    if not text:
        return ""
    return _SECRET_PATTERN.sub("[REDACTED_SECRET]", str(text))


class ProviderAdapterError(RuntimeError):
    """Safe, sanitized exception raised when a provider call fails."""

    def __init__(self, message: str, status_code: int = 502, details: Optional[Dict[str, Any]] = None) -> None:
        safe_msg = redact_secrets(message)
        super().__init__(safe_msg)
        self.status_code = status_code
        self.details = details or {}


class ProviderAdapter:
    """Centralized adapter for AI model providers, telemetry, and resilience."""

    def __init__(self, provider_id: Optional[str] = None, model_name: Optional[str] = None) -> None:
        self._provider_id = provider_id
        self._model_name = model_name

    @property
    def provider_id(self) -> str:
        return (self._provider_id or AppConfig.AI_PROVIDER).strip().lower()

    @property
    def provider_name(self) -> str:
        return provider_display_name(self.provider_id)

    @property
    def active_model(self) -> str:
        return self._model_name or MODEL_NAME

    def is_provider_ready(self, client: Any = None) -> bool:
        """Report whether the configured provider is reachable and credentials are set."""
        if self.provider_id == "ast":
            return True
        if client is None:
            client = self.create_client()
        return bool(provider_ready(client))

    def is_model_execution_ready(self, client: Any = None) -> bool:
        """Report whether a non-AST model client is available and ready for agent runs."""
        if self.provider_id == "ast":
            return False
        if client is None:
            client = self.create_client()
        return bool(client is not None and getattr(client, "chat", None) and provider_ready(client))

    def create_client(
        self,
        provider_override: Optional[str] = None,
        api_key_override: Optional[str] = None,
        model_override: Optional[str] = None,
        base_url_override: Optional[str] = None,
    ) -> Any:
        """Instantiate the low-level provider client."""
        return create_model_client(
            provider_override=provider_override or self._provider_id,
            api_key_override=api_key_override,
            model_override=model_override or self._model_name,
            base_url_override=base_url_override,
        )

    def get_provider_info(self, client: Any = None) -> Dict[str, Any]:
        """Return standardized provider status summary for the UI and telemetry."""
        configured_ready = self.is_provider_ready(client)
        execution_ready = self.is_model_execution_ready(client)
        return {
            "id": self.provider_id,
            "name": self.provider_name,
            "ready": configured_ready,
            "model_execution_ready": execution_ready,
            "model": self.active_model,
        }

    def execute_completion(
        self,
        client: Any,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 1500,
        session: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Execute a chat completion request with error classification and secret redaction."""
        if client is None:
            raise ProviderAdapterError("No AI model client is configured or available.", status_code=503)

        if session is not None and hasattr(session, "record_model_call"):
            session.record_model_call()

        target_model = model or self.active_model
        try:
            return client.chat.completions.create(
                model=target_model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs,
            )
        except Exception as exc:
            classified = classify_provider_error(exc, self.provider_name)
            if classified:
                payload, http_status = classified
                error_msg = payload.get("error", "Provider request failed.")
            else:
                error_msg = f"{self.provider_name} request failed: {redact_secrets(str(exc))}"
                http_status = 502

            logger.warning("Provider call failed [%s: %d]: %s", self.provider_id, http_status, error_msg)
            raise ProviderAdapterError(error_msg, status_code=http_status) from exc

    def as_chat_client(self, client: Any, session: Any = None) -> Any:
        """Return an OpenAI-compatible adapter object wrapping client and telemetry."""
        adapter = self

        class _ChatCompletionsProxy:
            def create(self, **kwargs: Any) -> Any:
                messages = kwargs.pop("messages", [])
                model = kwargs.pop("model", None)
                temperature = kwargs.pop("temperature", 0.1)
                max_tokens = kwargs.pop("max_tokens", 1500)
                return adapter.execute_completion(
                    client=client,
                    messages=messages,
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    session=session,
                    **kwargs,
                )

        proxy = SimpleNamespace(chat=SimpleNamespace(completions=_ChatCompletionsProxy()))
        proxy._provider_adapter_wrapped = True
        return proxy


# Default module-level instance
default_provider_adapter = ProviderAdapter()
