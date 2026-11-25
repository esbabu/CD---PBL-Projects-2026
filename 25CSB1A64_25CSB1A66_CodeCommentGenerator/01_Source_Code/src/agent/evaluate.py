"""
Agent evaluation
=================
Runs the fix-and-verify agent over

* the labelled vulnerable fixtures — every ``tests/security_fixtures/*.py``
  file that contains an ``# expect:`` label, and
* the OWASP BenchmarkPython test cases used by ``src.security.benchmarks``
  (all 1230 cases; the case's real/false label is kept so results can be split),

and reports, per rule and overall:

  findings          active findings the analyzer reported before fixing
  attempted         findings for which at least one strategy was tried
  fixed_verified    findings fixed by a patch that passed all four checks
  needs_manual_fix  findings left for a human (no strategy, or none passed)
  rejected_patches  patches that a strategy produced but verification refused

Every count is measured on this run; nothing is estimated. "Verified" means
verified by the analyzer and ``ast.parse`` — the patched programs are not
executed.

    python -m src.agent.evaluate [--out outputs/benchmarks/final] [--skip-owasp]
"""
from __future__ import annotations

import argparse
import ast
import glob
import json
import os
import time
from collections import defaultdict
from typing import Dict, Iterable, List, Tuple

from ..config import configure_stdio
from ..security.benchmarks import OWASP_DIR, OWASP_NEW_RULES, OWASP_RULES, ROOT, owasp_cases, run_meta
from .fixer import FIXED, fix_file

FIXTURE_DIR = os.path.join(ROOT, "tests", "security_fixtures")
KEYS = ("findings", "attempted", "fixed_verified", "needs_manual_fix", "rejected_patches")


def labelled_fixtures() -> List[str]:
    out = []
    for path in sorted(glob.glob(os.path.join(FIXTURE_DIR, "*.py"))):
        with open(path, encoding="utf-8") as fh:
            if "# expect:" in fh.read():
                out.append(path)
    return out


def _empty() -> Dict[str, int]:
    return {k: 0 for k in KEYS}


def _add(table: Dict[str, Dict[str, int]], result) -> None:
    for o in result.outcomes:
        row = table.setdefault(o.rule_id, _empty())
        row["findings"] += 1
        row["attempted"] += bool(o.attempts)
        row["fixed_verified"] += o.status == FIXED
        row["needs_manual_fix"] += o.status != FIXED
        row["rejected_patches"] += o.rejected


def _summarise(table: Dict[str, Dict[str, int]]) -> dict:
    overall = _empty()
    for row in table.values():
        for k in KEYS:
            overall[k] += row[k]
    for row in list(table.values()) + [overall]:
        row["fix_rate_of_attempted"] = round(row["fixed_verified"] / row["attempted"], 3) if row["attempted"] else None
        row["fix_rate_of_all"] = round(row["fixed_verified"] / row["findings"], 3) if row["findings"] else None
    return {"per_rule": dict(sorted(table.items())), "overall": overall}


def _run(paths: Iterable[Tuple[str, dict]]) -> Tuple[List[dict], dict]:
    """Fix every file; returns (per-file rows, run statistics)."""
    rows, parse_failures, t0 = [], 0, time.perf_counter()
    for path, meta in paths:
        result = fix_file(path)
        if result.changed:
            ast.parse(result.patched)          # independent of the agent's own check (a)
        parse_failures += bool(result.parse_error)
        rows.append({**meta, "file": os.path.relpath(path, ROOT), "result": result})
    return rows, {"files": len(rows), "files_not_parsable": parse_failures,
                  "files_changed": sum(r["result"].changed for r in rows),
                  "seconds": round(time.perf_counter() - t0, 1)}


def evaluate_fixtures() -> dict:
    rows, stats = _run((p, {}) for p in labelled_fixtures())
    table: Dict[str, Dict[str, int]] = {}
    for r in rows:
        _add(table, r["result"])
    return {"dataset": "tests/security_fixtures (files with # expect: labels)", "run": stats,
            **_summarise(table),
            "files": [{"file": r["file"], **r["result"].counts(),
                       "findings_before": r["result"].findings_before,
                       "findings_after": r["result"].findings_after} for r in rows]}


def evaluate_owasp() -> dict:
    cases = owasp_cases()
    paths = ((os.path.join(OWASP_DIR, "testcode", f"{c['test']}.py"), c) for c in cases)
    rows, stats = _run(paths)
    tables = {"all": {}, "real_vulnerability": {}, "false_positive_case": {}}
    cleared = defaultdict(lambda: {"flagged_before": 0, "cleared_after": 0})
    for r in rows:
        res = r["result"]
        _add(tables["all"], res)
        _add(tables["real_vulnerability" if r["real"] else "false_positive_case"], res)
        rules = OWASP_RULES.get(r["category"]) or OWASP_NEW_RULES.get(r["category"])
        if rules and r["real"]:
            before = [o for o in res.outcomes if o.rule_id in rules]
            if before:
                c = cleared[r["category"]]
                c["flagged_before"] += 1
                c["cleared_after"] += all(o.status == FIXED for o in before)
    return {"dataset": "OWASP BenchmarkPython (all test cases)", "run": stats,
            **_summarise(tables["all"]),
            "by_case_label": {k: _summarise(v) for k, v in tables.items() if k != "all"},
            "real_cases_with_category_finding_fully_fixed": dict(sorted(cleared.items()))}


def _print(name: str, block: dict) -> None:
    print(f"\n{name}: {block['run']['files']} files, {block['run']['seconds']} s")
    print(f"  {'rule':<8}{'findings':>9}{'attempted':>11}{'fixed':>7}{'manual':>8}{'rejected':>10}")
    for rule, row in list(block["per_rule"].items()) + [("overall", block["overall"])]:
        print(f"  {rule:<8}{row['findings']:>9}{row['attempted']:>11}{row['fixed_verified']:>7}"
              f"{row['needs_manual_fix']:>8}{row['rejected_patches']:>10}")


def main(argv=None) -> int:
    configure_stdio()
    ap = argparse.ArgumentParser(prog="python -m src.agent.evaluate")
    ap.add_argument("--out", default=os.path.join(ROOT, "outputs", "benchmarks", "final"))
    ap.add_argument("--skip-owasp", action="store_true")
    args = ap.parse_args(argv)

    report = {"meta": run_meta("agent-fix-eval", "fixtures + OWASP BenchmarkPython",
                               {"max_attempts": 3, "llm": False}),
              "fixtures": evaluate_fixtures()}
    _print("Fixtures", report["fixtures"])
    if not args.skip_owasp:
        if os.path.isdir(OWASP_DIR):
            report["owasp"] = evaluate_owasp()
            _print("OWASP BenchmarkPython", report["owasp"])
        else:
            print(f"\nOWASP data missing at {OWASP_DIR}; run python benchmarks/fetch.py")
    os.makedirs(args.out, exist_ok=True)
    path = os.path.join(args.out, "agent_fix_eval.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)
    print(f"\nSaved {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
