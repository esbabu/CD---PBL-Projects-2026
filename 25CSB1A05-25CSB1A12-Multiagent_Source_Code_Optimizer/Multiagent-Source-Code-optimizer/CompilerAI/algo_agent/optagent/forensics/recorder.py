"""Forensic recorder, drop funnel, and instrumentation probes."""
from __future__ import annotations

import functools
import inspect
import threading
import time
import traceback
from typing import Any, Callable
from pydantic import BaseModel, Field


class DropEvent(BaseModel):
    stage: str
    reason: str
    item_repr: str
    timestamp: float = Field(default_factory=time.time)


class StageProbeRecord(BaseModel):
    stage: str
    duration_s: float
    produced_by: list[str] = Field(default_factory=list)
    reasons: list[str] = Field(default_factory=list)
    input_summary: str = ""
    output_summary: str = ""
    exception: str | None = None
    innermost_locals: dict[str, str] = Field(default_factory=dict)


class UnitFunnel(BaseModel):
    unit: str
    bottlenecks: int = 0
    proposals: int = 0
    extracted: int = 0
    changed: int = 0
    built: int = 0
    oracle: int = 0
    sanitizer: int = 0
    benchmarked: int = 0
    faster: int = 0
    selected: int = 0
    drops: list[DropEvent] = Field(default_factory=list)

    def drop(self, stage: str, reason: str, item: Any = None) -> None:
        rep = repr(item) if item is not None else ""
        if len(rep) > 200:
            rep = rep[:197] + "..."
        self.drops.append(DropEvent(stage=stage, reason=reason, item_repr=rep))

    def step(self, name: str, count: int = 1) -> None:
        if hasattr(self, name):
            setattr(self, name, getattr(self, name) + count)


class ForensicRecorder:
    """Thread-local & session-wide recorder for funnel drops and stage instrumentation."""
    _local = threading.local()

    def __init__(self):
        self.funnels: dict[str, UnitFunnel] = {}
        self.stage_records: list[StageProbeRecord] = []
        self.probe_calls: list[dict[str, Any]] = []

    @classmethod
    def current(cls) -> ForensicRecorder:
        if not hasattr(cls._local, "active_recorder") or cls._local.active_recorder is None:
            cls._local.active_recorder = ForensicRecorder()
        return cls._local.active_recorder

    @classmethod
    def set_current(cls, rec: ForensicRecorder | None) -> None:
        cls._local.active_recorder = rec

    def get_funnel(self, unit: str = "default") -> UnitFunnel:
        if unit not in self.funnels:
            self.funnels[unit] = UnitFunnel(unit=unit)
        return self.funnels[unit]

    def record_drop(self, stage: str, reason: str, item: Any = None, unit: str = "default") -> None:
        self.get_funnel(unit).drop(stage, reason, item)

    def record_stage(
        self,
        stage: str,
        duration_s: float,
        produced_by: list[str] | None = None,
        reasons: list[str] | None = None,
        input_summary: str = "",
        output_summary: str = "",
        exc: Exception | None = None,
        tb: Any | None = None,
    ) -> StageProbeRecord:
        innermost_locals = {}
        exc_str = None
        if exc is not None:
            exc_str = f"{type(exc).__name__}: {exc}"
        if tb is not None:
            innermost_locals = extract_innermost_locals(tb)
        elif exc is not None and exc.__traceback__ is not None:
            innermost_locals = extract_innermost_locals(exc.__traceback__)

        rec = StageProbeRecord(
            stage=stage,
            duration_s=round(duration_s, 4),
            produced_by=produced_by or [],
            reasons=reasons or [],
            input_summary=input_summary[:300],
            output_summary=output_summary[:300],
            exception=exc_str,
            innermost_locals=innermost_locals,
        )
        self.stage_records.append(rec)
        return rec


def extract_innermost_locals(tb: Any) -> dict[str, str]:
    """Find the innermost optagent/user frame and extract repr(locals) truncated to 200 chars."""
    frames = []
    curr = tb
    while curr is not None:
        frames.append(curr.tb_frame)
        curr = curr.tb_next
    if not frames:
        return {}

    # Prefer innermost frame inside optagent or target module
    target_frame = frames[-1]
    res: dict[str, str] = {}
    for k, v in target_frame.f_locals.items():
        if k.startswith("__"):
            continue
        # redact secrets
        if any(sec in k.lower() for sec in ["secret", "password", "token", "key"]):
            res[k] = "<REDACTED>"
        else:
            try:
                r = repr(v)
            except Exception:
                r = "<unprintable>"
            if len(r) > 200:
                r = r[:197] + "..."
            res[k] = r
    return res


# Global drop helper
def drop(stage: str, reason: str, item: Any = None, unit: str = "default") -> None:
    ForensicRecorder.current().record_drop(stage, reason, item, unit)


# Probe registry
FORENSIC_PROBES: dict[str, Callable] = {}


def register_probe(name: str):
    """Decorator to wrap public functions in the pipeline to capture telemetry."""
    def decorator(fn: Callable):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            rec = ForensicRecorder.current()
            t0 = time.time()
            exc_obj = None
            ret = None
            try:
                ret = fn(*args, **kwargs)
                return ret
            except Exception as e:
                exc_obj = e
                raise
            finally:
                dur = time.time() - t0
                arg_sum = f"args={len(args)}, kwargs={list(kwargs.keys())}"
                ret_sum = type(ret).__name__ if ret is not None else "None"
                rec.probe_calls.append({
                    "probe": name,
                    "duration_s": round(dur, 4),
                    "args_summary": arg_sum,
                    "ret_summary": ret_sum,
                    "error": str(exc_obj) if exc_obj else None,
                })
        FORENSIC_PROBES[name] = wrapper
        return wrapper
    return decorator
