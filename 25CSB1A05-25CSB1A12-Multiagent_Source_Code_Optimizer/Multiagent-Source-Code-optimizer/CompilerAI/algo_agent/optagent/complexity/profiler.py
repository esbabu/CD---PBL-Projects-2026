"""Line-level profiler and bottleneck ranking using ProfileSandbox and static fact correlation."""
from __future__ import annotations

import collections
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

from ..config import Settings
from ..oracle.schemas import Case, OracleBundle
from ..runtime.sandbox import PKG_ROOT, Sandbox, _limiter
from ..schemas import FunctionFacts, IntentBundle
from .empirical import fit_curve
from .schemas import Bottleneck, FitResult

PROFILE_HARNESS = Path(__file__).resolve().parents[1] / "runtime" / "profile_harness.py"


class ProfileSandbox(Sandbox):
    """Sandbox subclass that executes profile_harness.py to gather cProfile and line timings."""

    def run_profile_batch(self, src_path, entry: str, cases: list[Case], timeout: float = 10.0) -> list[dict]:
        n = len(cases)
        if n == 0:
            return []

        results: list[dict] = []
        with tempfile.TemporaryDirectory(prefix="optagent_prof_") as td:
            root = Path(td)
            work, out = root / "work", root / "out"
            work.mkdir()
            out.mkdir()
            shutil.copy(src_path, work / "target.py")

            with open(work / "cases.jsonl", "w", encoding="utf-8") as f:
                for c in cases:
                    f.write(json.dumps({"args": c.args, "kwargs": c.kwargs}) + "\n")

            cfg = {"entry": entry, "timeout": timeout, "rand_seed": self.s.rand_seed, "start": 0}
            (work / "cfg.json").write_text(json.dumps(cfg), encoding="utf-8")
            out_file = out / "out.jsonl"
            out_file.write_text("", encoding="utf-8")

            # Local or Docker spawn
            env = {"PATH": os.environ.get("PATH", ""), "PYTHONHASHSEED": "0", "PYTHONDONTWRITEBYTECODE": "1"}
            for k in ("SYSTEMROOT", "TEMP", "TMP", "HOME", "VIRTUAL_ENV", "LD_LIBRARY_PATH"):
                if k in os.environ:
                    env[k] = os.environ[k]

            cmd = [sys.executable, str(PROFILE_HARNESS), str(PKG_ROOT), str(work / "target.py"),
                   str(work / "cases.jsonl"), str(out / "out.jsonl"), str(work / "cfg.json")]

            kw = {}
            if os.name == "posix":
                kw = dict(start_new_session=True,
                          preexec_fn=_limiter(self.s.exec_mem_mb, int(timeout * n + 60)))

            proc = subprocess.Popen(cmd, cwd=out, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, **kw)
            try:
                proc.communicate(timeout=timeout * n + 10)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.communicate()

            if out_file.exists():
                with open(out_file, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            d = json.loads(line)
                            if "idx" in d:
                                results.append(d)
                        except Exception:
                            continue

        return results


class Profiler:
    def __init__(self, settings: Settings, log=print):
        self.s = settings
        self.log = log
        self.sb = ProfileSandbox(settings)

    def profile(self, intent: IntentBundle, oracle: OracleBundle | None = None) -> tuple[list[Bottleneck], FitResult | None]:
        """Profile the original function and produce ranked bottlenecks and space fit."""
        entry = intent.entry_point
        if getattr(intent, "language", "python") != "python" or entry == "__script__":
            return [], None
        fn_facts: FunctionFacts = intent.module_facts.functions.get(entry)
        source_lines = intent.source.splitlines()

        # Gather representative test cases for profiling (preferably scaling cases of medium/large size)
        cases: list[Case] = []
        scaling_pts = getattr(oracle, "scaling", None) or (oracle.b.scaling if hasattr(oracle, "b") else None)
        if scaling_pts:
            # Use top points from scaling set
            sorted_scale = sorted(scaling_pts, key=lambda p: p.n)
            # Pick mid to large points that succeeded
            valid_scale = [p for p in sorted_scale if p.status == "ok"]
            for p in valid_scale[-self.s.profile_case_count:]:
                c = Case.make(p.args, p.kwargs, origin="scale", category="profile", kind="valid")
                c.size = p.n
                cases.append(c)

        if not cases and oracle and getattr(oracle, "cases", None):
            # Fallback to visible oracle cases with larger sizes (oracle.cases may be dict or list)
            raw_cases = oracle.cases.values() if isinstance(oracle.cases, dict) else oracle.cases
            sorted_cases = sorted((c for c in raw_cases if getattr(c, "kind", "valid") == "valid"), key=lambda c: c.size)
            cases = sorted_cases[-self.s.profile_case_count:]

        if not cases and intent.golden_seed:
            for r in intent.golden_seed:
                if r.status == "ok":
                    cases.append(Case.make(r.args, r.kwargs, origin="seed"))

        if not cases:
            return [], None

        # Write original source to temp file
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as tf:
            tf.write(intent.source)
            src_path = tf.name

        try:
            profile_records = self.sb.run_profile_batch(src_path, entry, cases)
        finally:
            try:
                os.unlink(src_path)
            except Exception:
                pass

        if not profile_records:
            return [], None

        # Aggregate line hits and line times
        total_time_all = 0.0
        line_times: dict[int, float] = collections.defaultdict(float)
        line_hits: dict[int, int] = collections.defaultdict(int)
        mem_points: list[tuple[int, float]] = []

        for rec in profile_records:
            if rec.get("status") != "ok":
                continue
            elapsed = rec.get("elapsed_s", 0.0)
            total_time_all += elapsed
            lt = rec.get("line_times", {})
            lh = rec.get("line_hits", {})
            for ln_s, t in lt.items():
                line_times[int(ln_s)] += float(t)
            for ln_s, h in lh.items():
                line_hits[int(ln_s)] += int(h)

            peak_mem = rec.get("peak_mem_bytes")
            idx = rec.get("idx", 0)
            if peak_mem is not None and idx < len(cases):
                sz = cases[idx].size or 10
                mem_points.append((sz, float(peak_mem)))

        # Fit memory curve if data available
        space_fit: FitResult | None = None
        if len(mem_points) >= 2:
            mem_points.sort(key=lambda x: x[0])
            space_fit = fit_curve([x[0] for x in mem_points], [x[1] for x in mem_points])

        # Rank bottlenecks
        bottlenecks: list[Bottleneck] = []
        cost_pattern_map = {p.line: p for p in (fn_facts.cost_patterns if fn_facts else [])}
        sort_pattern_map = {s.line: s for s in (fn_facts.sort_uses if fn_facts else [])}

        total_line_time = sum(line_times.values())
        norm_base = max(total_line_time, total_time_all, 1e-9)

        # Collect candidate lines
        candidate_lines = set(line_times.keys()) | set(line_hits.keys())
        if fn_facts:
            candidate_lines |= set(cost_pattern_map.keys()) | set(sort_pattern_map.keys())

        for ln in sorted(candidate_lines):
            if ln < 1 or ln > len(source_lines):
                continue
            code_str = source_lines[ln - 1].strip()
            hits = line_hits.get(ln, 0)
            t_spent = line_times.get(ln, 0.0)
            share = min(1.0, t_spent / norm_base)

            pattern = "hotspot"
            detail = ""
            claimed_c = ""

            if ln in cost_pattern_map:
                cp = cost_pattern_map[ln]
                pattern = cp.kind
                detail = cp.detail
                claimed_c = "O(n^2)" if cp.in_loop else "O(n)"
            elif ln in sort_pattern_map:
                sp = sort_pattern_map[ln]
                pattern = "sort"
                detail = f"{sp.kind} ({sp.detail})"
                claimed_c = "O(n log n)"
            elif fn_facts and fn_facts.max_loop_depth >= 2 and ("for " in code_str or "while " in code_str):
                pattern = "nested_loop"
                claimed_c = f"O(n^{fn_facts.max_loop_depth})"
                detail = f"loop header at depth {fn_facts.max_loop_depth}"

            # Only include lines with measurable impact or cost pattern
            if share > 0.05 or hits > 50 or pattern in ("nested_loop", "linear_membership", "sort"):
                bottlenecks.append(Bottleneck(
                    line=ln,
                    code=code_str,
                    pattern=pattern,
                    share_of_time=round(share, 3),
                    hits=hits,
                    claimed_complexity=claimed_c,
                    detail=detail or f"{hits} executions"
                ))

        # Sort bottlenecks: highest share of time, then hits
        bottlenecks.sort(key=lambda b: (b.share_of_time, b.hits), reverse=True)

        return bottlenecks, space_fit
