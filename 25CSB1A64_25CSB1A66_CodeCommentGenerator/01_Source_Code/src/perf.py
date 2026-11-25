"""
Block-wise performance instrumentation
=======================================
    from src import perf
    with perf.profile(memory=False) as prof:      # timing pass
        run_pipeline(...)
    prof.summary()

    with perf.block("security.taint", lines=n):   # inside the code being measured
        ...

When no profile is active, ``block()`` costs one context-variable lookup, so the
instrumentation stays in place in normal runs.

Per block it records wall time (``time.perf_counter``) and, when ``memory=True``,
the peak of Python allocations inside the block (``tracemalloc``; nested blocks
handled so each parent sees its children's peaks) and the change in process
resident memory (``psutil``). tracemalloc slows Python code down several times,
so the benchmark measures time and memory in two separate passes.
"""
from __future__ import annotations

import contextvars
import statistics
import time
import tracemalloc
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from typing import Dict, List, Optional

try:
    import psutil
    _PROC = psutil.Process()
except Exception:                     # psutil is optional
    _PROC = None

_ACTIVE: contextvars.ContextVar = contextvars.ContextVar("ccg_profiler", default=None)


@dataclass
class BlockRecord:
    name: str
    ms: float
    lines: int = 0
    items: int = 0
    peak_kb: Optional[float] = None       # tracemalloc peak above the block's starting allocation
    rss_delta_kb: Optional[float] = None
    depth: int = 0


@dataclass
class _Frame:
    name: str
    t0: float
    lines: int
    items: int
    start_cur: int = 0
    running_peak: int = 0
    rss0: int = 0


class Profiler:
    def __init__(self, memory: bool = False):
        self.memory = memory
        self.records: List[BlockRecord] = []
        self._stack: List[_Frame] = []
        self._started_tracemalloc = False
        self.t0 = time.perf_counter()
        self.total_ms = 0.0

    # ── frames ──────────────────────────────────────────────────────────
    def enter(self, name: str, lines: int = 0, items: int = 0) -> None:
        f = _Frame(name, time.perf_counter(), lines, items)
        if self.memory:
            cur, peak = tracemalloc.get_traced_memory()
            if self._stack:                                   # keep the parent's peak before resetting
                self._stack[-1].running_peak = max(self._stack[-1].running_peak, peak)
            tracemalloc.reset_peak()
            f.start_cur = cur
            f.running_peak = cur
            if _PROC is not None:
                f.rss0 = _PROC.memory_info().rss
        self._stack.append(f)

    def exit(self) -> None:
        if not self._stack:
            return
        f = self._stack.pop()
        ms = (time.perf_counter() - f.t0) * 1000
        rec = BlockRecord(f.name, round(ms, 3), f.lines, f.items, depth=len(self._stack))
        if self.memory:
            cur, peak = tracemalloc.get_traced_memory()
            top = max(peak, f.running_peak)
            rec.peak_kb = round(max(0, top - f.start_cur) / 1024, 1)
            if _PROC is not None:
                rec.rss_delta_kb = round((_PROC.memory_info().rss - f.rss0) / 1024, 1)
            if self._stack:
                self._stack[-1].running_peak = max(self._stack[-1].running_peak, top)
        self.records.append(rec)

    def start(self) -> None:
        if self.memory and not tracemalloc.is_tracing():
            tracemalloc.start()
            self._started_tracemalloc = True

    def stop(self) -> None:
        while self._stack:
            self.exit()
        self.total_ms = round((time.perf_counter() - self.t0) * 1000, 3)
        if self._started_tracemalloc:
            tracemalloc.stop()

    # ── results ─────────────────────────────────────────────────────────
    def by_block(self) -> Dict[str, dict]:
        groups: Dict[str, List[BlockRecord]] = {}
        for r in self.records:
            groups.setdefault(r.name, []).append(r)
        out = {}
        for name, rs in groups.items():
            ms = [r.ms for r in rs]
            lines = sum(r.lines for r in rs)
            peaks = [r.peak_kb for r in rs if r.peak_kb is not None]
            out[name] = {"calls": len(rs), "total_ms": round(sum(ms), 3), "mean_ms": round(statistics.fmean(ms), 3),
                         "median_ms": round(statistics.median(ms), 3),
                         "p95_ms": round(sorted(ms)[max(0, int(round(0.95 * len(ms))) - 1)], 3),
                         "max_ms": round(max(ms), 3), "lines": lines,
                         "lines_per_s": round(lines / (sum(ms) / 1000), 1) if lines and sum(ms) > 0 else None,
                         "peak_kb": round(max(peaks), 1) if peaks else None,
                         "mean_peak_kb": round(statistics.fmean(peaks), 1) if peaks else None}
        return out

    def summary(self) -> dict:
        return {"total_ms": self.total_ms, "memory_measured": self.memory, "blocks": self.by_block(),
                "records": [asdict(r) for r in self.records]}


@contextmanager
def profile(memory: bool = False):
    prof = Profiler(memory)
    token = _ACTIVE.set(prof)
    prof.start()
    try:
        yield prof
    finally:
        prof.stop()
        _ACTIVE.reset(token)


@contextmanager
def block(name: str, lines: int = 0, items: int = 0):
    prof = _ACTIVE.get()
    if prof is None:
        yield
        return
    prof.enter(name, lines, items)
    try:
        yield
    finally:
        prof.exit()


def active() -> Optional[Profiler]:
    return _ACTIVE.get()
