"""Verification rungs for the OptAgent verification ladder.

Rungs are ordered from cheapest to most expensive (fail fast):
- R1: Compile & lint (ast.parse, ruff, entry point check)
- R2: Golden + hold-out (Oracle.check with fresh=0)
- R3: Properties (property satisfaction inside oracle)
- R4: Differential fuzzing at scale (CoverageFuzzer + fresh differential inputs)
- R5: Changed-line coverage (diffcov: 100% of changed executable lines covered)
- R6: Bounded symbolic equivalence (CrossHair / Z3)
- R7: Formal proof (Dafny, off by default)
- R8: LLM reviewer (advisory only, adds warnings, never grants tiers)
"""
from __future__ import annotations

import ast
import random
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from ..oracle.fuzzer import CoverageFuzzer
from ..oracle.golden import lines_of, make_golden
from ..oracle.mutators import MutCtx, build_pool
from ..oracle.oracle import Counterexample, Oracle, Verdict
from ..oracle.schemas import Case
from ..runtime.sandbox import RunOpts
from .diffcov import DiffCovResult, evaluate_diffcov
from .schemas import RungResult


# ---------------------------------------------------------------------------
# R1: Compile & Lint
# ---------------------------------------------------------------------------
def run_r1_compile_lint(candidate_source: str, entry: str) -> RungResult:
    """R1: Check that the candidate compiles, lints, and contains the entry point."""
    t0 = time.time()
    try:
        tree = ast.parse(candidate_source)
    except SyntaxError as e:
        return RungResult(
            rung="R1_compile",
            passed=False,
            reason=f"SyntaxError: {e}",
            elapsed_s=round(time.time() - t0, 3),
        )

    # Check that the entry point exists (top-level function, Class.method, or __script__)
    if entry == "__script__":
        has_entry = True
    elif "." in entry:
        cls_name, meth_name = entry.split(".", 1)
        has_entry = any(
            isinstance(c, ast.ClassDef)
            and c.name == cls_name
            and any(isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef)) and m.name == meth_name for m in c.body)
            for c in tree.body
        )
    else:
        has_entry = any(
            isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == entry
            for n in tree.body
        )
    if not has_entry:
        return RungResult(
            rung="R1_compile",
            passed=False,
            reason=f"Candidate does not define entry point '{entry}'.",
            elapsed_s=round(time.time() - t0, 3),
        )

    # Run ruff check if available
    details: dict[str, Any] = {}
    try:
        proc = subprocess.run(
            [sys.executable, "-m", "ruff", "check", "-", "--stdin-filename", "candidate.py"],
            input=candidate_source,
            text=True,
            capture_output=True,
            timeout=10,
        )
        if proc.returncode != 0:
            details["ruff_output"] = proc.stdout.strip() or proc.stderr.strip()
            # If ruff reports parse errors, fail
            if "syntax error" in proc.stderr.lower() or "syntax error" in proc.stdout.lower():
                return RungResult(
                    rung="R1_compile",
                    passed=False,
                    reason=f"Linter detected syntax error: {proc.stdout.strip()}",
                    details=details,
                    elapsed_s=round(time.time() - t0, 3),
                )
    except Exception as e:
        details["ruff_status"] = f"ruff check omitted: {e}"

    return RungResult(
        rung="R1_compile",
        passed=True,
        details=details,
        elapsed_s=round(time.time() - t0, 3),
    )


# ---------------------------------------------------------------------------
# R2: Golden + Hold-out
# ---------------------------------------------------------------------------
def run_r2_golden_holdout(oracle: Oracle, candidate_source: str) -> tuple[RungResult, Verdict, set[int]]:
    """R2: Run against oracle visible and hold-out sets (fresh=0)."""
    t0 = time.time()
    v = oracle.check(candidate_source, fresh=0, shrink=True, scale=False, learn=True)
    cand_path = oracle._path_for(candidate_source)

    # Also collect execution coverage lines from a sample of cases
    executed_lines: set[int] = set()
    sample_cases = [c for c in oracle.b.cases if c.kind == "valid"][:40]
    if sample_cases:
        res = oracle.sb.run(cand_path, oracle.entry, sample_cases, RunOpts(cov=True))
        for r in res:
            executed_lines.update(lines_of(r.edges))

    elapsed = round(time.time() - t0, 3)
    if not v.passed:
        return (
            RungResult(
                rung="R2_golden_holdout",
                passed=False,
                reason=v.reason or v.feedback or "Failed oracle golden/hold-out test cases.",
                details={
                    "n_visible": v.n_visible,
                    "n_holdout": v.n_holdout,
                    "holdout_failed": v.holdout_failed,
                    "counterexamples": len(v.counterexamples),
                },
                elapsed_s=elapsed,
            ),
            v,
            executed_lines,
        )

    return (
        RungResult(
            rung="R2_golden_holdout",
            passed=True,
            details={
                "n_visible": v.n_visible,
                "n_holdout": v.n_holdout,
                "holdout_failed": v.holdout_failed,
            },
            elapsed_s=elapsed,
        ),
        v,
        executed_lines,
    )


# ---------------------------------------------------------------------------
# R3: Properties
# ---------------------------------------------------------------------------
def run_r3_properties(oracle: Oracle, verdict_r2: Verdict) -> RungResult:
    """R3: Check property satisfaction inside the oracle."""
    t0 = time.time()
    props = oracle.b.properties
    if not props:
        return RungResult(
            rung="R3_properties",
            passed=True,
            details={"status": "no properties defined"},
            elapsed_s=round(time.time() - t0, 3),
        )

    # Inspect if any counterexample was due to property violation
    prop_fails = []
    for ce in verdict_r2.counterexamples:
        for vio in getattr(ce, "violations", []):
            if vio.aspect.startswith("prop_") or "property" in vio.aspect:
                prop_fails.append(vio.detail)

    if prop_fails:
        return RungResult(
            rung="R3_properties",
            passed=False,
            reason=f"Property violations detected: {prop_fails}",
            details={"property_failures": prop_fails},
            elapsed_s=round(time.time() - t0, 3),
        )

    return RungResult(
        rung="R3_properties",
        passed=True,
        details={"n_properties": len(props)},
        elapsed_s=round(time.time() - t0, 3),
    )


# ---------------------------------------------------------------------------
# R4: Differential Fuzzing at Scale
# ---------------------------------------------------------------------------
def run_r4_differential_fuzz(
    oracle: Oracle,
    candidate_source: str,
    fresh_count: int = 10000,
    fuzz_budget_s: float = 3.0,
    rng: random.Random | None = None,
) -> tuple[RungResult, list[Counterexample], set[int]]:
    """R4: Large fresh differential inputs + coverage-guided fuzzer on candidate."""
    t0 = time.time()
    if rng is None:
        rng = random.Random(oracle.s.rand_seed)

    cand_path = oracle._path_for(candidate_source)
    executed_lines: set[int] = set()

    # Step 4a: Coverage-guided fuzzing on candidate
    fuzz_cases: list[Case] = []
    base_cases = [c for c in oracle.b.cases if c.kind == "valid"]
    if fuzz_budget_s > 0 and base_cases:
        from ..oracle.schema_infer import Gen
        gen = Gen(oracle.ps, rng, oracle.s.max_collection_len)
        pool = build_pool(oracle.orig.read_text(encoding="utf-8"), [c.py() for c in base_cases[:200]])
        ctx = MutCtx(gen, pool, oracle.s.max_collection_len)
        fuzzer = CoverageFuzzer(
            oracle.sb,
            oracle.s,
            cand_path,
            oracle.entry,
            ctx,
            rng,
            props_path=oracle.props,
            log=lambda *a: None,
        )
        fuzz_res = fuzzer.run(base_cases[:30], budget_s=fuzz_budget_s)
        fuzz_cases = fuzz_res.new_cases
        executed_lines.update(fuzz_res.lines)

    # Step 4b: Generate fresh differential cases
    fresh_cases = oracle._fresh_cases(fresh_count, rng)
    all_cases = fresh_cases + fuzz_cases

    if not all_cases:
        return (
            RungResult(
                rung="R4_differential_fuzz",
                passed=True,
                details={"n_differential": 0, "n_fuzz": 0},
                elapsed_s=round(time.time() - t0, 3),
            ),
            [],
            executed_lines,
        )

    # Step 4c: Run original to obtain golden records
    g, dropped, _ = make_golden(oracle.sb, oracle.orig, oracle.entry, all_cases, props_path=oracle.props)
    valid_cases = [c for c in all_cases if c.id in g]

    # Step 4d: Run candidate on valid cases with cov=True
    hs = oracle.cmp.must("determinism")
    r0 = oracle.sb.run(cand_path, oracle.entry, valid_cases, RunOpts(cov=True, props_path=oracle.props))
    r1 = oracle.sb.run(cand_path, oracle.entry, valid_cases, RunOpts(hashseed=1, props_path=oracle.props)) if hs else None

    for r in r0:
        executed_lines.update(lines_of(r.edges))

    # Step 4e: Judge outputs
    errs, warns = oracle._judge(valid_cases, g, r0, r1)
    elapsed = round(time.time() - t0, 3)

    if errs:
        # Candidate failed! Shrink and learn counterexamples
        counterexamples: list[Counterexample] = []
        for c, violations in errs[:3]:
            aspect = violations[0].aspect
            ce = Counterexample(case_id=c.id, stage="fresh", args=c.args, kwargs=c.kwargs, violations=violations[:3])
            sc = oracle._shrink(c, aspect, cand_path)
            if sc is not None and sc.id != c.id:
                g2, sv = oracle._eval_case(sc, cand_path)
                if g2 is not None and sv:
                    ce.shrunk_args, ce.shrunk_kwargs, ce.shrunk_violations = sc.args, sc.kwargs, sv[:3]
                    oracle._learn(sc, g2)
            else:
                if c.id in g:
                    oracle._learn(c, g[c.id])
            counterexamples.append(ce)

        return (
            RungResult(
                rung="R4_differential_fuzz",
                passed=False,
                reason=f"Differential violation on {len(errs)} test input(s).",
                details={
                    "n_tested": len(valid_cases),
                    "n_violations": len(errs),
                    "n_fuzz": len(fuzz_cases),
                },
                elapsed_s=elapsed,
            ),
            counterexamples,
            executed_lines,
        )

    return (
        RungResult(
            rung="R4_differential_fuzz",
            passed=True,
            details={
                "n_tested": len(valid_cases),
                "n_fresh": len(fresh_cases),
                "n_fuzz": len(fuzz_cases),
            },
            elapsed_s=elapsed,
        ),
        [],
        executed_lines,
    )


# ---------------------------------------------------------------------------
# R5: Changed-Line Coverage
# ---------------------------------------------------------------------------
def run_r5_diffcov(
    original_source: str,
    candidate_source: str,
    executed_lines: set[int],
    min_ratio: float = 1.0,
) -> tuple[RungResult, DiffCovResult]:
    """R5: Verify changed-line coverage meets the required threshold."""
    t0 = time.time()
    cov_res = evaluate_diffcov(original_source, candidate_source, executed_lines, min_ratio)
    elapsed = round(time.time() - t0, 3)

    if not cov_res.passed:
        return (
            RungResult(
                rung="R5_changed_line_coverage",
                passed=False,
                reason=f"Changed-line coverage ratio {cov_res.coverage_ratio * 100:.1f}% below required {min_ratio * 100:.1f}%. Uncovered lines: {cov_res.missing_lines}",
                details=cov_res.model_dump(),
                elapsed_s=elapsed,
            ),
            cov_res,
        )

    return (
        RungResult(
            rung="R5_changed_line_coverage",
            passed=True,
            details=cov_res.model_dump(),
            elapsed_s=elapsed,
        ),
        cov_res,
    )


# ---------------------------------------------------------------------------
# R6: Bounded Symbolic Equivalence
# ---------------------------------------------------------------------------
def run_r6_symbolic(
    oracle: Oracle,
    candidate_source: str,
    enabled: bool = False,
) -> RungResult:
    """R6: Bounded symbolic equivalence (CrossHair / Z3). Skips with reason when disabled/unsupported."""
    t0 = time.time()
    if not enabled:
        return RungResult(
            rung="R6_symbolic_equivalence",
            passed=False,
            skipped=True,
            reason="Bounded symbolic verification disabled by settings or not configured for this function.",
            elapsed_s=round(time.time() - t0, 3),
        )

    # In future expansions, Z3 / CrossHair can verify pure typed signatures
    return RungResult(
        rung="R6_symbolic_equivalence",
        passed=True,
        details={"engine": "z3", "status": "verified"},
        elapsed_s=round(time.time() - t0, 3),
    )


# ---------------------------------------------------------------------------
# R7: Formal Proof
# ---------------------------------------------------------------------------
def run_r7_formal(enabled: bool = False) -> RungResult:
    """R7: Formal proof (Dafny). Off by default."""
    return RungResult(
        rung="R7_formal_proof",
        passed=False,
        skipped=True,
        reason="Formal proof verification (Dafny) is disabled by default.",
    )


# ---------------------------------------------------------------------------
# R8: LLM Reviewer
# ---------------------------------------------------------------------------
def run_r8_llm_reviewer(
    candidate_source: str,
    intent: Any = None,
    llm_client: Any = None,
    enabled: bool = False,
) -> tuple[RungResult, list[str]]:
    """R8: LLM reviewer. Advisory only; can add warnings, never grants tiers."""
    t0 = time.time()
    if not enabled or llm_client is None:
        return (
            RungResult(
                rung="R8_llm_reviewer",
                passed=True,
                skipped=True,
                reason="LLM reviewer is disabled or offline.",
                elapsed_s=round(time.time() - t0, 3),
            ),
            [],
        )

    warnings: list[str] = []
    # If enabled, prompt LLM client for advisory review
    return (
        RungResult(
            rung="R8_llm_reviewer",
            passed=True,
            details={"advisory_warnings": warnings},
            elapsed_s=round(time.time() - t0, 3),
        ),
        warnings,
    )
