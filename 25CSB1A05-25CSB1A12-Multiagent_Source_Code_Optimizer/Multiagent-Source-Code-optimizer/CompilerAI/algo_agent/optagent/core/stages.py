"""Stage runner with exception isolation and structured diagnostics persistence."""
from __future__ import annotations

import json
import time
import traceback
from pathlib import Path
from typing import Any, Callable, TypeVar

from .outcome import Reason, ReasonCode, StageResult

T = TypeVar("T")


class StageRunner:
    """Executes pipeline stages safely, capturing tracebacks into diagnostics.json."""

    def __init__(self, run_dir: Path | None = None) -> None:
        self.run_dir = run_dir
        self.stages: list[StageResult] = []
        self.reasons: list[Reason] = []
        self.diagnostics: list[dict[str, Any]] = []
        self.critical_failure: bool = False

    def set_run_dir(self, run_dir: Path) -> None:
        self.run_dir = run_dir

    def run_stage(
        self,
        name: str,
        fn: Callable[[], T],
        *,
        fallback: Callable[[Exception], T] | None = None,
        critical: bool = False,
        produced_by: list[str] | None = None,
        reason_code: ReasonCode = ReasonCode.STAGE_ERROR,
    ) -> tuple[T | None, StageResult]:
        t0 = time.time()
        try:
            value = fn()
            sr = StageResult(
                name=name,
                status="ok",
                seconds=round(time.time() - t0, 3),
                produced_by=produced_by or ["heuristic"],
            )
            self.stages.append(sr)
            return value, sr
        except Exception as exc:
            tb = traceback.format_exc()
            self.diagnostics.append({
                "stage": name,
                "error_type": type(exc).__name__,
                "error": str(exc),
                "traceback": tb,
            })
            self.persist_diagnostics()

            reason = Reason(
                code=reason_code,
                message=f"Stage '{name}' failed ({type(exc).__name__}): {exc}",
                stage=name,
                detail={"error_type": type(exc).__name__},
            )
            self.reasons.append(reason)

            if fallback is not None:
                try:
                    fb_val = fallback(exc)
                    sr = StageResult(
                        name=name,
                        status="degraded",
                        seconds=round(time.time() - t0, 3),
                        produced_by=["heuristic"],
                        reasons=[reason],
                    )
                    self.stages.append(sr)
                    return fb_val, sr
                except Exception as fb_exc:
                    self.diagnostics.append({
                        "stage": f"{name}:fallback",
                        "error_type": type(fb_exc).__name__,
                        "error": str(fb_exc),
                        "traceback": traceback.format_exc(),
                    })
                    self.persist_diagnostics()

            if critical:
                self.critical_failure = True
            sr = StageResult(
                name=name,
                status="failed",
                seconds=round(time.time() - t0, 3),
                produced_by=produced_by or [],
                reasons=[reason],
            )
            self.stages.append(sr)
            return None, sr

    def record_skipped(self, name: str, reason: Reason | None = None) -> StageResult:
        sr = StageResult(
            name=name,
            status="skipped",
            seconds=0.0,
            produced_by=[],
            reasons=[reason] if reason else [],
        )
        if reason:
            self.reasons.append(reason)
        self.stages.append(sr)
        return sr

    def persist_diagnostics(self) -> None:
        if self.run_dir is None or not self.diagnostics:
            return
        try:
            self.run_dir.mkdir(parents=True, exist_ok=True)
            (self.run_dir / "diagnostics.json").write_text(
                json.dumps(self.diagnostics, indent=2),
                encoding="utf-8",
            )
        except Exception:
            pass
