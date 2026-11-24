"""Component taxonomy, provenance tracking, and LLM fallback decorator."""
from __future__ import annotations

import contextvars
import functools
from enum import Enum
from typing import Any, Callable, TypeVar

from pydantic import BaseModel, Field

F = TypeVar("F", bound=Callable[..., Any])


class ComponentKind(str, Enum):
    HEURISTIC = "heuristic"
    TOOL = "tool"
    LLM = "llm"
    HYBRID = "hybrid"


class Provenance(BaseModel):
    kind: ComponentKind
    component: str
    model: str | None = None
    prompt_sha: str | None = None
    cache_hit: bool = False
    fallback_used: bool = False
    fallback_reason: str | None = None


class ProvenanceSummary(BaseModel):
    counts: dict[str, int] = Field(default_factory=lambda: {"heuristic": 0, "tool": 0, "llm": 0, "hybrid": 0})
    llm_calls: int = 0
    llm_tokens_in: int = 0
    llm_tokens_out: int = 0
    cache_hits: int = 0
    fallbacks: list[dict[str, str]] = Field(default_factory=list)
    model_resolutions: dict[str, str] = Field(default_factory=dict)
    items: list[Provenance] = Field(default_factory=list)


class ComponentEntry(BaseModel):
    name: str
    module: str
    kind: ComponentKind
    has_fallback: bool = False
    description: str = ""


_REGISTRY: dict[str, ComponentEntry] = {}
_CURRENT_TRACKER: contextvars.ContextVar["ProvenanceTracker | None"] = contextvars.ContextVar(
    "optagent_provenance_tracker", default=None
)


class ProvenanceTracker:
    """Collects provenance items and LLM usage metrics for a single run."""

    def __init__(self) -> None:
        self.items: list[Provenance] = []
        self.llm_calls: int = 0
        self.llm_tokens_in: int = 0
        self.llm_tokens_out: int = 0
        self.cache_hits: int = 0
        self.fallbacks: list[dict[str, str]] = []
        self.model_resolutions: dict[str, str] = {}
        self._token: contextvars.Token | None = None

    def __enter__(self) -> "ProvenanceTracker":
        self._token = _CURRENT_TRACKER.set(self)
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if self._token is not None:
            _CURRENT_TRACKER.reset(self._token)
            self._token = None

    def record(self, prov: Provenance) -> None:
        self.items.append(prov)
        if prov.cache_hit:
            self.cache_hits += 1
        if prov.fallback_used:
            self.fallbacks.append({
                "component": prov.component,
                "reason": prov.fallback_reason or "fallback_triggered",
            })

    def record_llm_call(self, tokens_in: int = 0, tokens_out: int = 0, cache_hit: bool = False) -> None:
        self.llm_calls += 1
        self.llm_tokens_in += tokens_in
        self.llm_tokens_out += tokens_out
        if cache_hit:
            self.cache_hits += 1

    def summary(self) -> ProvenanceSummary:
        counts = {"heuristic": 0, "tool": 0, "llm": 0, "hybrid": 0}
        for it in self.items:
            counts[it.kind.value] = counts.get(it.kind.value, 0) + 1
        return ProvenanceSummary(
            counts=counts,
            llm_calls=self.llm_calls,
            llm_tokens_in=self.llm_tokens_in,
            llm_tokens_out=self.llm_tokens_out,
            cache_hits=self.cache_hits,
            fallbacks=list(self.fallbacks),
            model_resolutions=dict(self.model_resolutions),
            items=list(self.items),
        )


def current_tracker() -> ProvenanceTracker | None:
    return _CURRENT_TRACKER.get()


def register_component(name: str, module: str, kind: ComponentKind, has_fallback: bool = False, description: str = "") -> None:
    _REGISTRY[name] = ComponentEntry(
        name=name,
        module=module,
        kind=kind,
        has_fallback=has_fallback,
        description=description,
    )


def get_component_registry() -> list[ComponentEntry]:
    return sorted(_REGISTRY.values(), key=lambda e: (e.kind.value, e.module, e.name))


def component(
    kind: ComponentKind,
    *,
    llm_fallback: Callable[..., Any] | None = None,
    name: str | None = None,
    description: str = "",
) -> Callable[[F], F]:
    """Classify a pipeline component and enforce deterministic fallback on LLM errors."""

    def decorator(fn: F) -> F:
        comp_name = name or f"{fn.__module__}.{fn.__qualname__}"
        doc = description or (fn.__doc__.strip().splitlines()[0] if fn.__doc__ else "")
        register_component(comp_name, fn.__module__, kind, has_fallback=llm_fallback is not None, description=doc)

        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            tracker = current_tracker()
            try:
                res = fn(*args, **kwargs)
                if tracker is not None:
                    tracker.record(Provenance(kind=kind, component=comp_name))
                return res
            except Exception as exc:
                # Only catch typed LLM errors when a fallback is registered
                err_name = type(exc).__name__
                is_llm_err = err_name in {
                    "LLMError",
                    "LLMUnavailable",
                    "LLMTimeout",
                    "LLMInvalidOutput",
                    "LLMContextOverflow",
                }
                if is_llm_err and llm_fallback is not None:
                    if tracker is not None:
                        tracker.record(
                            Provenance(
                                kind=ComponentKind.HEURISTIC,
                                component=comp_name,
                                fallback_used=True,
                                fallback_reason=f"{err_name}: {exc}",
                            )
                        )
                    return llm_fallback(*args, **kwargs)
                raise

        setattr(wrapper, "_optagent_component", {"name": comp_name, "kind": kind, "has_fallback": llm_fallback is not None})
        return wrapper  # type: ignore[return-value]

    return decorator


def render_component_map_markdown() -> str:
    entries = get_component_registry()
    lines = [
        "# OptAgent Component Taxonomy Map",
        "",
        "Generated directly from `@component` registrations (`optagent/core/provenance.py`).",
        "",
        "| Kind | Component | Module | Fallback Defined | Description |",
        "|---|---|---|---|---|",
    ]
    for e in entries:
        lines.append(
            f"| `{e.kind.value.upper()}` | `{e.name}` | `{e.module}` | {'Yes' if e.has_fallback else 'No'} | {e.description.replace('|', '/')} |"
        )
    lines.append("")
    return "\n".join(lines)
