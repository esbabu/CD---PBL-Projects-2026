"""Unified Ollama LLM Gateway: modes, model resolution, context control, cache, retries, tracing."""
from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any, Type, TypeVar

from pydantic import BaseModel

from ..config import Settings
from ..core.provenance import ComponentKind, Provenance, current_tracker
from .cache import LLMCache
from .health import OllamaHealth, check_ollama_health, resolve_role_models, strip_legacy_prefix
from .ollama import (
    LLMContextOverflow,
    LLMError,
    LLMInvalidOutput,
    LLMTimeout,
    LLMUnavailable,
    OllamaBackend,
    inline_json_schema_defs,
)

T = TypeVar("T", bound=BaseModel)

ROLE_NUM_PREDICT = {
    "spec": 2048,
    "predictor": 1024,
    "oracle": 1536,
    "proposer": 3072,
    "judge": 1024,
}


def estimate_tokens(text: str) -> int:
    return max(1, int(len(text) / 3.2))


def slice_budgeted_sections(sections: list[tuple[str, str]], max_chars: int) -> str:
    """Assemble prioritized prompt sections `(name, text)` within `max_chars`."""
    out: list[str] = []
    used = 0
    for name, body in sections:
        if not body:
            continue
        remaining = max_chars - used
        if remaining <= 0:
            break
        if len(body) <= remaining:
            out.append(body)
            used += len(body)
        else:
            if remaining > 120:
                out.append(body[: remaining - 40] + f"\n... [{name} truncated to fit context]")
            break
    return "\n\n".join(out)


def _extract_json_object(text: str) -> dict[str, Any]:
    txt = (text or "").strip()
    if txt.startswith("```"):
        lines = txt.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        txt = "\n".join(lines).strip()
    start = txt.find("{")
    end = txt.rfind("}") + 1
    if start == -1 or end <= start:
        raise ValueError(f"No JSON object found in model output: {txt[:200]}")
    return json.loads(txt[start:end])


class OllamaGateway:
    """Single entry point for every LLM call across OptAgent."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.s = settings or Settings()
        self.backend = OllamaBackend(
            base_url=self.s.ollama_base,
            connect_timeout_s=getattr(self.s, "llm_connect_timeout_s", 5.0),
            read_timeout_s=getattr(self.s, "llm_read_timeout_s", 600.0),
            concurrency=getattr(self.s, "llm_concurrency", 1),
        )
        cache_path = Path(self.s.runs_dir) / ".llm_cache.db"
        self.cache = LLMCache(cache_path, enabled=getattr(self.s, "llm_cache", True))
        self.trace: list[dict[str, Any]] = []
        self.resolution_warnings: list[str] = []
        self.resolved_roles: dict[str, str | None] = {}

    @property
    def mode(self) -> str:
        return getattr(self.s, "llm_mode", "assist").lower()

    def check_health(self, force: bool = False) -> OllamaHealth:
        if self.mode == "off":
            return OllamaHealth(
                reachable=False,
                base_url=self.s.ollama_base,
                reason_kind="off",
                remediation="LLM mode is set to 'off'; zero network calls performed.",
            )
        health = check_ollama_health(
            self.s.ollama_base,
            connect_timeout=getattr(self.s, "llm_connect_timeout_s", 5.0),
            force=force,
        )
        if health.reachable and health.models:
            res = resolve_role_models(health.models, self.s)
            self.resolved_roles = res["resolved"]
            self.resolution_warnings = res["warnings"]
            tracker = current_tracker()
            if tracker is not None:
                for k, v in self.resolved_roles.items():
                    if v:
                        tracker.model_resolutions[k] = v
        return health

    def resolve_model(self, role: str, requested_model: str | None = None) -> str:
        health = self.check_health()
        if not health.reachable or not health.models:
            raise LLMUnavailable(health.remediation or health.error or f"Ollama unavailable at {self.s.ollama_base}")

        # Prefer resolved role model from installed models
        if requested_model:
            clean = strip_legacy_prefix(requested_model)
            for m in health.models:
                if m.name.lower() == clean.lower() or m.name.lower().split(":")[0] == clean.lower().split(":")[0]:
                    return m.name
        chosen = self.resolved_roles.get(role) or self.resolved_roles.get("spec")
        if not chosen:
            raise LLMUnavailable(f"No suitable installed Ollama model found for role '{role}'.")
        return chosen

    def complete_json(
        self,
        role: str,
        system: str,
        user: str,
        schema: Type[T],
        *,
        requested_model: str | None = None,
        budget_sections: list[tuple[str, str]] | None = None,
    ) -> T:
        """Execute a structured JSON completion through Ollama with context control, caching, and repair."""
        if self.mode == "off":
            raise LLMUnavailable("OPT_LLM_MODE=off: LLM calls are disabled.")

        model = self.resolve_model(role, requested_model)
        schema_dict = inline_json_schema_defs(schema.model_json_schema())
        schema_hash = hashlib.sha256(json.dumps(schema_dict, sort_keys=True).encode("utf-8")).hexdigest()[:16]
        prompt_sha = hashlib.sha256((system + "\n" + user).encode("utf-8")).hexdigest()[:16]

        model_limit = self.backend.get_model_context_length(model, default=max(8192, self.s.num_ctx))
        ctx_cap = min(model_limit, getattr(self.s, "num_ctx_max", 16384))
        num_predict = ROLE_NUM_PREDICT.get(role, 2048)

        est_tokens = estimate_tokens(system) + estimate_tokens(user)
        margin = 512
        if est_tokens + num_predict + margin > ctx_cap:
            if budget_sections:
                avail_chars = max(1000, int((ctx_cap - num_predict - margin - estimate_tokens(system)) * 3.0))
                user = slice_budgeted_sections(budget_sections, avail_chars)
                est_tokens = estimate_tokens(system) + estimate_tokens(user)
            if est_tokens + num_predict > ctx_cap:
                raise LLMContextOverflow(
                    f"Prompt (~{est_tokens} tokens) + output ({num_predict}) exceeds context limit ({ctx_cap}) for model '{model}'."
                )

        num_ctx = max(4096, min(ctx_cap, est_tokens + num_predict + margin))
        options: dict[str, Any] = {
            "temperature": self.s.temperature,
            "top_k": 1,
            "seed": self.s.rand_seed,
            "num_ctx": num_ctx,
            "num_predict": num_predict,
        }

        cache_key = self.cache.make_key(model, options, system, user, schema_hash)
        cached = self.cache.get(cache_key)
        if cached is not None:
            try:
                validated = schema.model_validate(cached["response"])
                self._record_trace(
                    role=role,
                    model=model,
                    prompt_sha=prompt_sha,
                    attempt=0,
                    elapsed_s=0.0,
                    tokens_in=cached["prompt_tokens"],
                    tokens_out=cached["completion_tokens"],
                    cache_hit=True,
                    outcome="ok",
                )
                return validated
            except Exception:
                pass

        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]

        last_err: Exception | None = None
        max_attempts = self.s.llm_max_repairs + 1
        for attempt in range(max_attempts):
            t0 = time.time()
            content = ""
            try:
                resp = self.backend.chat(
                    model=model,
                    messages=messages,
                    options=options,
                    format_spec=schema_dict,
                )
                elapsed = round(time.time() - t0, 3)
                msg = resp.get("message") or {}
                content = msg.get("content") or ""
                done_reason = resp.get("done_reason", "stop")
                prompt_eval = int(resp.get("prompt_eval_count") or 0)
                eval_count = int(resp.get("eval_count") or 0)

                # Detect silent prompt truncation via prompt_eval_count
                cur_est = sum(estimate_tokens(m["content"]) for m in messages)
                if prompt_eval > 0 and cur_est > 400 and prompt_eval < int(cur_est * 0.55):
                    if options["num_ctx"] < ctx_cap:
                        options["num_ctx"] = ctx_cap
                        self._record_trace(
                            role=role, model=model, prompt_sha=prompt_sha, attempt=attempt,
                            elapsed_s=elapsed, tokens_in=prompt_eval, tokens_out=eval_count,
                            cache_hit=False, outcome="retry_truncation",
                        )
                        continue
                    raise LLMContextOverflow(
                        f"Prompt appears silently truncated by Ollama (prompt_eval_count={prompt_eval} vs estimated {cur_est})."
                    )

                # Detect output cutoff via done_reason == "length"
                if done_reason == "length":
                    options["num_predict"] = min(ctx_cap // 2, int(options["num_predict"] * 1.5))
                    last_err = LLMInvalidOutput("Model output was truncated (done_reason='length').")
                    self._record_trace(
                        role=role, model=model, prompt_sha=prompt_sha, attempt=attempt,
                        elapsed_s=elapsed, tokens_in=prompt_eval, tokens_out=eval_count,
                        cache_hit=False, outcome="retry_length",
                    )
                    if attempt < max_attempts - 1:
                        continue
                    raise last_err

                raw = _extract_json_object(content)
                validated = schema.model_validate(raw)

                self.cache.put(cache_key, model, raw, prompt_tokens=prompt_eval, completion_tokens=eval_count)
                self._record_trace(
                    role=role, model=model, prompt_sha=prompt_sha, attempt=attempt,
                    elapsed_s=elapsed, tokens_in=prompt_eval, tokens_out=eval_count,
                    cache_hit=False, outcome="ok",
                )
                return validated

            except (LLMUnavailable, LLMTimeout, LLMContextOverflow):
                raise
            except Exception as exc:
                elapsed = round(time.time() - t0, 3)
                last_err = exc
                self._record_trace(
                    role=role, model=model, prompt_sha=prompt_sha, attempt=attempt,
                    elapsed_s=elapsed, tokens_in=0, tokens_out=0,
                    cache_hit=False, outcome=f"error:{type(exc).__name__}", error=str(exc)[:250],
                )
                if attempt < max_attempts - 1:
                    messages.append({"role": "assistant", "content": content})
                    messages.append({
                        "role": "user",
                        "content": f"Your response was invalid JSON or failed schema validation: {exc}. Reply with ONLY a valid JSON object matching the schema.",
                    })

        raise LLMInvalidOutput(f"Ollama call for role '{role}' failed after {max_attempts} attempts: {last_err}") from last_err

    def _record_trace(
        self,
        *,
        role: str,
        model: str,
        prompt_sha: str,
        attempt: int,
        elapsed_s: float,
        tokens_in: int,
        tokens_out: int,
        cache_hit: bool,
        outcome: str,
        error: str | None = None,
    ) -> None:
        entry: dict[str, Any] = {
            "role": role,
            "model": model,
            "prompt_sha": prompt_sha,
            "attempt": attempt,
            "elapsed_s": elapsed_s,
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "cache_hit": cache_hit,
            "outcome": outcome,
        }
        if error:
            entry["error"] = error
        self.trace.append(entry)

        tracker = current_tracker()
        if tracker is not None:
            tracker.record_llm_call(tokens_in=tokens_in, tokens_out=tokens_out, cache_hit=cache_hit)
            tracker.record(
                Provenance(
                    kind=ComponentKind.LLM,
                    component=f"llm.gateway.{role}",
                    model=model,
                    prompt_sha=prompt_sha,
                    cache_hit=cache_hit,
                )
            )
