"""Backward-compatible LLMClient facade backed exclusively by OllamaGateway."""
from __future__ import annotations

from typing import Type, TypeVar

from pydantic import BaseModel

from ..config import Settings
from .gateway import OllamaGateway
from .ollama import (
    LLMContextOverflow,
    LLMError,
    LLMInvalidOutput,
    LLMTimeout,
    LLMUnavailable,
)

T = TypeVar("T", bound=BaseModel)


class LLMClient:
    """Thin role-scoped client delegating all inference to OllamaGateway."""

    def __init__(self, model: str, settings: Settings, role: str, gateway: OllamaGateway | None = None):
        self.model = model
        self.s = settings
        self.role = role
        self.gateway = gateway or OllamaGateway(settings)

    @property
    def trace(self) -> list[dict]:
        return self.gateway.trace

    def complete_json(self, system: str, user: str, schema: Type[T]) -> T:
        """Call the Ollama gateway and return a validated Pydantic model instance."""
        return self.gateway.complete_json(
            role=self.role,
            system=system,
            user=user,
            schema=schema,
            requested_model=self.model,
        )


__all__ = [
    "LLMClient",
    "LLMError",
    "LLMUnavailable",
    "LLMTimeout",
    "LLMInvalidOutput",
    "LLMContextOverflow",
]
