"""Ollama health check and role-to-model resolution (read-only; never installs or pulls)."""
from __future__ import annotations

import re
import threading
import time
from dataclasses import dataclass, field
from typing import Any

import httpx

from ..config import Settings

CODE_ROLE_PREFS = [
    "qwen2.5-coder",
    "qwen3-coder",
    "deepseek-coder",
    "codellama",
    "starcoder2",
    "qwen3",
    "llama3",
    "gemma",
    "mistral",
]
GENERAL_ROLE_PREFS = [
    "llama3",
    "qwen3",
    "qwen2.5",
    "gemma",
    "mistral",
    "qwen2.5-coder",
    "deepseek-coder",
    "codellama",
]

_PARAM_SIZE_RE = re.compile(r"(\d+(?:\.\d+)?)\s*[bB]")


@dataclass
class ModelInfo:
    name: str
    size_bytes: int = 0
    family: str = ""
    param_b: float = 0.0

    @property
    def size_gb(self) -> float:
        return self.size_bytes / (1024 ** 3) if self.size_bytes else 0.0


@dataclass
class OllamaHealth:
    reachable: bool
    base_url: str
    version: str | None = None
    models: list[ModelInfo] = field(default_factory=list)
    error: str | None = None
    reason_kind: str = "ok"  # ok | unreachable | no_models | http_error
    remediation: str = ""
    checked_at: float = 0.0

    @property
    def model_names(self) -> list[str]:
        return [m.name for m in self.models]


def strip_legacy_prefix(model_name: str) -> str:
    """Strip legacy LiteLLM prefixes like `ollama_chat/` or `ollama/`."""
    m = (model_name or "").strip()
    for prefix in ("ollama_chat/", "ollama/"):
        if m.startswith(prefix):
            m = m[len(prefix):]
    return m


def _extract_family(model_name: str) -> str:
    base = strip_legacy_prefix(model_name).split(":")[0].lower()
    # Collapse e.g. qwen2.5-coder -> qwen, llama3.1 -> llama
    m = re.match(r"([a-z]+)", base)
    return m.group(1) if m else base


def _extract_param_b(model_name: str) -> float:
    m = _PARAM_SIZE_RE.search(model_name)
    return float(m.group(1)) if m else 0.0


class HealthCache:
    def __init__(self, ttl_s: float = 30.0) -> None:
        self.ttl_s = ttl_s
        self._lock = threading.Lock()
        self._cache: dict[str, OllamaHealth] = {}

    def clear(self) -> None:
        with self._lock:
            self._cache.clear()

    def check(self, base_url: str, connect_timeout: float = 5.0, force: bool = False) -> OllamaHealth:
        base = base_url.rstrip("/")
        now = time.time()
        with self._lock:
            cached = self._cache.get(base)
            if not force and cached and (now - cached.checked_at) < self.ttl_s:
                return cached

        health = _probe_ollama(base, connect_timeout=connect_timeout)
        with self._lock:
            self._cache[base] = health
        return health


_HEALTH_CACHE = HealthCache(ttl_s=30.0)


def check_ollama_health(base_url: str, connect_timeout: float = 5.0, force: bool = False) -> OllamaHealth:
    return _HEALTH_CACHE.check(base_url, connect_timeout=connect_timeout, force=force)


def clear_health_cache() -> None:
    _HEALTH_CACHE.clear()


def _probe_ollama(base: str, connect_timeout: float = 5.0) -> OllamaHealth:
    timeout = httpx.Timeout(connect=connect_timeout, read=connect_timeout, write=connect_timeout, pool=connect_timeout)
    now = time.time()
    try:
        with httpx.Client(timeout=timeout) as client:
            vr = client.get(f"{base}/api/version")
            if vr.status_code >= 400:
                return OllamaHealth(
                    reachable=False,
                    base_url=base,
                    error=f"HTTP {vr.status_code} from /api/version",
                    reason_kind="http_error",
                    remediation=f"Check the Ollama service at {base} (HTTP {vr.status_code}).",
                    checked_at=now,
                )
            version = vr.json().get("version")

            tr = client.get(f"{base}/api/tags")
            if tr.status_code >= 400:
                return OllamaHealth(
                    reachable=False,
                    base_url=base,
                    version=version,
                    error=f"HTTP {tr.status_code} from /api/tags",
                    reason_kind="http_error",
                    remediation=f"Check the Ollama service at {base} (HTTP {tr.status_code}).",
                    checked_at=now,
                )
            raw_models = tr.json().get("models", [])
            models = [
                ModelInfo(
                    name=m.get("name", ""),
                    size_bytes=int(m.get("size", 0) or 0),
                    family=_extract_family(m.get("name", "")),
                    param_b=_extract_param_b(m.get("name", "")),
                )
                for m in raw_models
                if m.get("name")
            ]
            if not models:
                return OllamaHealth(
                    reachable=True,
                    base_url=base,
                    version=version,
                    models=[],
                    error="No models installed in Ollama",
                    reason_kind="no_models",
                    remediation="No models installed in Ollama; run `ollama pull qwen2.5-coder:7b` manually.",
                    checked_at=now,
                )
            return OllamaHealth(
                reachable=True,
                base_url=base,
                version=version,
                models=models,
                reason_kind="ok",
                checked_at=now,
            )
    except Exception as exc:
        return OllamaHealth(
            reachable=False,
            base_url=base,
            error=str(exc),
            reason_kind="unreachable",
            remediation=f"Ollama not reachable at {base}; start it manually or run with OPT_LLM_MODE=off.",
            checked_at=now,
        )


def _match_installed(requested: str, installed: list[ModelInfo]) -> ModelInfo | None:
    clean = strip_legacy_prefix(requested).lower()
    if not clean:
        return None
    # Exact match
    for m in installed:
        if m.name.lower() == clean:
            return m
    # Prefix match ignoring tag
    req_base = clean.split(":")[0]
    matches = [m for m in installed if m.name.lower().split(":")[0] == req_base]
    if matches:
        return sorted(matches, key=lambda m: (m.param_b, m.size_bytes), reverse=True)[0]
    return None


def _pick_by_preferences(
    installed: list[ModelInfo],
    prefs: list[str],
    max_gb: float,
    exclude_family: str | None = None,
) -> ModelInfo | None:
    eligible = [m for m in installed if (m.size_gb == 0.0 or m.size_gb <= max_gb)]
    if not eligible:
        eligible = list(installed)
    if exclude_family:
        diff = [m for m in eligible if m.family != exclude_family]
        if diff:
            eligible = diff

    for pref in prefs:
        cands = [m for m in eligible if m.name.lower().split(":")[0].startswith(pref)]
        if cands:
            return sorted(cands, key=lambda m: (m.param_b, m.size_bytes), reverse=True)[0]
    return sorted(eligible, key=lambda m: (m.param_b, m.size_bytes), reverse=True)[0] if eligible else None


def resolve_role_models(
    installed_models: list[ModelInfo] | list[str],
    settings: Settings,
) -> dict[str, Any]:
    """Resolve spec, predictor, proposer, judge, oracle roles strictly against installed models."""
    models: list[ModelInfo] = [
        m if isinstance(m, ModelInfo) else ModelInfo(name=m, family=_extract_family(m), param_b=_extract_param_b(m))
        for m in installed_models
    ]
    warnings: list[str] = []
    resolved: dict[str, str | None] = {}

    if not models:
        return {"resolved": {"spec": None, "predictor": None, "proposer": None, "judge": None, "oracle": None}, "warnings": ["No Ollama models installed."]}

    role_requests = {
        "spec": (settings.spec_model, CODE_ROLE_PREFS),
        "proposer": (getattr(settings, "proposer_model", settings.spec_model), CODE_ROLE_PREFS),
        "oracle": (settings.spec_model, CODE_ROLE_PREFS),
        "judge": (getattr(settings, "judge_model", settings.predictor_model), GENERAL_ROLE_PREFS),
    }

    for role, (req, prefs) in role_requests.items():
        matched = _match_installed(req, models)
        if matched is None:
            matched = _pick_by_preferences(models, prefs, getattr(settings, "max_model_gb", 16.0))
            if matched and strip_legacy_prefix(req):
                warnings.append(f"Role '{role}': requested '{strip_legacy_prefix(req)}' not installed; resolved to '{matched.name}'.")
        resolved[role] = matched.name if matched else None

    # Predictor: prefer a different model family from spec when >1 family is installed
    spec_model = resolved.get("spec")
    spec_family = _extract_family(spec_model) if spec_model else None
    pred_req = settings.predictor_model
    pred_match = _match_installed(pred_req, models)
    distinct_families = {m.family for m in models}
    if pred_match is None or (spec_family and pred_match.family == spec_family and len(distinct_families) > 1):
        alt = _pick_by_preferences(models, GENERAL_ROLE_PREFS, getattr(settings, "max_model_gb", 16.0), exclude_family=spec_family)
        if alt:
            if pred_match is None and strip_legacy_prefix(pred_req):
                warnings.append(f"Role 'predictor': requested '{strip_legacy_prefix(pred_req)}' not installed; resolved to '{alt.name}'.")
            pred_match = alt
    resolved["predictor"] = pred_match.name if pred_match else spec_model

    if resolved["spec"] and resolved["predictor"] and _extract_family(resolved["spec"]) == _extract_family(resolved["predictor"]):
        warnings.append(
            f"Spec ('{resolved['spec']}') and predictor ('{resolved['predictor']}') share model family '{spec_family}'; independence is reduced."
        )

    return {"resolved": resolved, "warnings": warnings}
