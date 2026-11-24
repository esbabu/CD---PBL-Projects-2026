"""Layer-by-layer diagnostic ladder for OptAgent (`python -m optagent.repair.ladder`).

Runs L0..L8 in strict order, stopping at the first FAIL, recording exact evidence
to `runs/repair/<lang>-<fixture>.json`, and optionally generating a Markdown matrix.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import tempfile
import time
import traceback
from pathlib import Path
from typing import Any

from ..agent import OptimizerAgent, OptimizeRequest
from ..config import Settings
from ..intent.pipeline import IntentExtractor
from ..lang.registry import detect_language, get_adapter
from ..oracle.builder import OracleBuilder
from ..oracle.oracle import Oracle
from ..oracle.schemas import Case
from ..runtime.sandbox import RunOpts, Sandbox
from ..search.schemas import SearchBudget

ROOT = Path(__file__).resolve().parents[2]
REPAIR_FIXTURES_DIR = ROOT / "examples" / "repair"

LANG_ALIAS = {"py": "python", "python": "python", "js": "javascript", "javascript": "javascript", "c": "c", "cpp": "cpp", "c++": "cpp"}
DIR_TO_LANG = {"python": "python", "js": "javascript", "c": "c", "cpp": "cpp"}


def _fast_settings(td: Path) -> Settings:
    return Settings(
        sandbox_backend="local",
        runs_dir=str(td / "runs"),
        memory_db_path=str(td / "memory.db"),
        n_family=8,
        n_hypothesis=8,
        n_probe=3,
        n_adversarial=3,
        fuzz_budget_s=0.4,
        fuzz_max_rounds=1,
        max_mutants=3,
        scale_sizes=(10, 25),
        ladder_fresh_inputs=20,
        ladder_fuzz_budget_s=0.4,
        bench_warmups=1,
        bench_reps=2,
        search_max_depth=1,
        search_max_candidates=2,
    )


def _smoke_cases_for(lang: str, fn: Any, fixture_name: str) -> list[Case]:
    """Return 3 small hand-written smoke cases for L3 when possible."""
    params = getattr(fn, "params", [])
    if fixture_name in ("simple_fn", "leetcode_class", "two_sum") and lang in ("python", "javascript"):
        return [
            Case.make([[2, 7, 11, 15], 9], {}, origin="smoke"),
            Case.make([[3, 2, 4], 6], {}, origin="smoke"),
            Case.make([[1, 2, 3], 10], {}, origin="smoke"),
        ]
    if fixture_name == "static_and_classmethods":
        return [
            Case.make([[1, 2, 3]], {}, origin="smoke"),
            Case.make([[1, 2, 1]], {}, origin="smoke"),
            Case.make([[]], {}, origin="smoke"),
        ]
    if fixture_name == "two_sum" and lang == "c":
        return [
            Case.make([[1, 2, 3, 4], 4, 5], {}, origin="smoke"),
            Case.make([[1, 1, 1], 3, 2], {}, origin="smoke"),
            Case.make([[], 0, 0], {}, origin="smoke"),
        ]
    if fixture_name == "dedupe_rank" and lang == "cpp":
        return [
            Case.make([["a", "b", "a"], 2], {}, origin="smoke"),
            Case.make([["x"], 1], {}, origin="smoke"),
            Case.make([[], 0], {}, origin="smoke"),
        ]
    if len(params) == 1:
        p0 = params[0]
        ann = (p0.annotation or "").lower()
        if "int" in ann and "list" not in ann and "[]" not in ann and "vector" not in ann:
            return [Case.make([0], {}, origin="smoke"), Case.make([3], {}, origin="smoke"), Case.make([5], {}, origin="smoke")]
        return [Case.make([[1, 2, 3]], {}, origin="smoke"), Case.make([[1, 1, 2]], {}, origin="smoke"), Case.make([[]], {}, origin="smoke")]
    return []


def run_ladder(lang: str, fixture_path: Path, use_llm: bool = False) -> dict[str, Any]:
    lang_id = LANG_ALIAS.get(lang.lower(), lang.lower())
    source = fixture_path.read_text(encoding="utf-8")
    stem = fixture_path.stem
    layers: dict[str, dict[str, Any]] = {}
    td = Path(tempfile.mkdtemp(prefix=f"ladder_{lang_id}_{stem}_"))
    s = _fast_settings(td)

    def record(layer: str, status: str, t0: float, detail: str = "", extra: dict[str, Any] | None = None):
        layers[layer] = {
            "status": status,
            "seconds": round(time.time() - t0, 3),
            "detail": detail[:400],
            **(extra or {}),
        }

    adapter = None
    mod = None
    entry = None
    intent = None
    oracle = None

    try:
        # L0: detect_language + adapter registry
        t0 = time.time()
        try:
            detected = detect_language(fixture_path.name, source, lang_id)
            adapter = get_adapter(detected)
            if adapter.id != lang_id:
                record("L0", "FAIL", t0, f"Adapter mismatch: requested {lang_id}, got {adapter.id}")
                return _finalize(lang_id, fixture_path, layers, td)
            record("L0", "PASS", t0, f"adapter={adapter.id}")
        except Exception as e:
            record("L0", "FAIL", t0, f"{type(e).__name__}: {e}")
            return _finalize(lang_id, fixture_path, layers, td)

        # L1: Fact extraction
        t0 = time.time()
        fn = None
        try:
            mod = adapter.analyze(source, {})
            entry = adapter.select_entry(mod, None)
            fn = mod.functions.get(entry)
            pnames = [p.name for p in fn.params] if fn else []
            record("L1", "PASS", t0, f"entry={entry}, params={pnames}")
        except Exception as e:
            record("L1", "FAIL", t0, f"{type(e).__name__}: {e}")
            return _finalize(lang_id, fixture_path, layers, td)

        # L2: Build / syntax check
        t0 = time.time()
        try:
            bdir = td / "build"
            bdir.mkdir(parents=True, exist_ok=True)
            bres = adapter.build(source, entry, {}, bdir)
            if not bres.ok:
                record("L2", "FAIL", t0, f"Build failed: {bres.log[:300]}")
                return _finalize(lang_id, fixture_path, layers, td)
            record("L2", "PASS", t0, "build ok")
        except Exception as e:
            record("L2", "FAIL", t0, f"{type(e).__name__}: {e}")
            return _finalize(lang_id, fixture_path, layers, td)

        # L3: Harness smoke with hand-written cases
        t0 = time.time()
        seed_hints = {"_source": source, "_strategy": "script" if entry == "__script__" else "function"}
        try:
            smoke = _smoke_cases_for(lang_id, fn, stem) if fn is not None else []
            if not smoke:
                smoke = [Case.make(c["args"], c.get("kwargs", {}), origin="seed") for c in adapter.seed_inputs(fn, seed_hints)[:3]]
            if not smoke:
                record("L3", "FAIL", t0, "No smoke cases could be constructed")
                return _finalize(lang_id, fixture_path, layers, td)
            src_file = td / f"smoke_src{adapter.extensions[0]}"
            src_file.write_text(source, encoding="utf-8")
            sb = Sandbox(s, profile=adapter.sandbox_profile({}))
            results = [adapter.normalize_result(r) for r in sb.run(src_file, entry, smoke, RunOpts(hashseed=0))]
            bad = [r for r in results if r.status == "load_error"]
            if bad:
                record("L3", "FAIL", t0, f"load_error: {bad[0].exc_type}: {bad[0].exc_msg}")
                return _finalize(lang_id, fixture_path, layers, td)
            ok_count = sum(1 for r in results if r.status in ("ok", "exception"))
            if ok_count == 0:
                record("L3", "FAIL", t0, f"All {len(results)} smoke cases failed: {[r.status for r in results]}")
                return _finalize(lang_id, fixture_path, layers, td)
            record("L3", "PASS", t0, f"{ok_count}/{len(results)} executed")
        except Exception as e:
            record("L3", "FAIL", t0, f"{type(e).__name__}: {e}")
            return _finalize(lang_id, fixture_path, layers, td)

        # L4: Seed inputs without LLM (or with LLM if enabled)
        t0 = time.time()
        try:
            seeds = adapter.seed_inputs(fn, seed_hints)
            if len(seeds) < 1:
                record("L4", "FAIL", t0, f"seed_inputs returned {len(seeds)} seeds (expected >= 1)")
                return _finalize(lang_id, fixture_path, layers, td)
            record("L4", "PASS", t0, f"{len(seeds)} seeds generated")
        except Exception as e:
            record("L4", "FAIL", t0, f"{type(e).__name__}: {e}")
            return _finalize(lang_id, fixture_path, layers, td)

        # L5: Intent + Golden seeds
        t0 = time.time()
        try:
            extractor = IntentExtractor(s, use_llm=use_llm, adapter=adapter)
            intent = extractor.run(source, entry=None if entry == "__script__" else entry, source_name=fixture_path.name, language=lang_id, auto_select=True)
            exec_ok = [r for r in intent.golden_seed if r.status in ("ok", "exception")]
            if not exec_ok:
                record("L5", "FAIL", t0, f"0 executable golden seeds (warnings={intent.warnings[:2]})")
                return _finalize(lang_id, fixture_path, layers, td)
            record("L5", "PASS", t0, f"{len(exec_ok)} golden seeds")
        except Exception as e:
            record("L5", "FAIL", t0, f"{type(e).__name__}: {e}")
            return _finalize(lang_id, fixture_path, layers, td)

        # L6: Oracle build
        t0 = time.time()
        try:
            bundle = OracleBuilder(s, use_llm=use_llm, log=lambda *a: None, adapter=adapter).build(intent, run_mutation=False)
            oracle = Oracle(bundle, s, adapter=adapter)
            tier = bundle.strength.tier if bundle.strength else "D"
            record("L6", "PASS", t0, f"tier={tier}, cases={len(bundle.cases)}")
        except Exception as e:
            record("L6", "FAIL", t0, f"{type(e).__name__}: {e}")
            return _finalize(lang_id, fixture_path, layers, td)

        # L7: Oracle.check on known-right and known-wrong rewrites
        t0 = time.time()
        try:
            right_p = fixture_path.with_name(f"{stem}_right{fixture_path.suffix}")
            wrong_p = fixture_path.with_name(f"{stem}_wrong{fixture_path.suffix}")
            if right_p.exists() and wrong_p.exists():
                vr = oracle.check(right_p.read_text(encoding="utf-8"), shrink=False)
                vw = oracle.check(wrong_p.read_text(encoding="utf-8"), shrink=True)
                if not vr.passed:
                    record("L7", "FAIL", t0, f"Known-right rejected: {vr.summary}")
                    return _finalize(lang_id, fixture_path, layers, td)
                if vw.passed:
                    record("L7", "FAIL", t0, "Known-wrong was incorrectly accepted!")
                    return _finalize(lang_id, fixture_path, layers, td)
                has_ce = bool(getattr(vw, "failures", None) or getattr(vw, "shrunk", None))
                record("L7", "PASS", t0, f"right=PASS, wrong=FAIL (counterexample={has_ce})")
            else:
                vself = oracle.check(source, shrink=False)
                if not vself.passed:
                    record("L7", "FAIL", t0, f"Original failed self-check: {vself.summary}")
                    return _finalize(lang_id, fixture_path, layers, td)
                record("L7", "PASS", t0, "self-check PASS")
        except Exception as e:
            record("L7", "FAIL", t0, f"{type(e).__name__}: {e}")
            return _finalize(lang_id, fixture_path, layers, td)

        # L8: Full OptimizerAgent run
        t0 = time.time()
        try:
            td8 = td / "full"
            td8.mkdir(parents=True, exist_ok=True)
            s8 = _fast_settings(td8)
            agent = OptimizerAgent(s8, log=lambda *a: None)
            req = OptimizeRequest(
                source=source,
                language=lang_id,
                source_name=fixture_path.name,
                budget=SearchBudget(max_candidates=2, max_time_s=12.0),
                use_llm=use_llm,
            )
            res = agent.run(req)
            if res.status == "error":
                record("L8", "FAIL", t0, f"status=error: {res.message}")
                return _finalize(lang_id, fixture_path, layers, td)
            outcome = getattr(res, "outcome", None)
            lvl = outcome.support_level.value if outcome else res.status
            record("L8", "PASS", t0, f"status={res.status}, support={lvl}")
        except Exception as e:
            record("L8", "FAIL", t0, f"{type(e).__name__}: {e}")
            return _finalize(lang_id, fixture_path, layers, td)

    finally:
        shutil.rmtree(td, ignore_errors=True)

    return _finalize(lang_id, fixture_path, layers, None)


def _finalize(lang_id: str, fixture_path: Path, layers: dict[str, dict[str, Any]], td: Path | None) -> dict[str, Any]:
    if td and td.exists():
        shutil.rmtree(td, ignore_errors=True)
    out_dir = ROOT / "runs" / "repair"
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "language": lang_id,
        "fixture": fixture_path.name,
        "layers": layers,
        "highest_pass": max((k for k, v in layers.items() if v["status"] == "PASS"), default="NONE"),
        "first_fail": next((k for k, v in layers.items() if v["status"] == "FAIL"), None),
    }
    (out_dir / f"{lang_id}-{fixture_path.stem}.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def discover_fixtures() -> list[tuple[str, Path]]:
    items: list[tuple[str, Path]] = []
    for dname, lang in (("python", "python"), ("js", "javascript"), ("c", "c"), ("cpp", "cpp")):
        d = REPAIR_FIXTURES_DIR / dname
        if not d.exists():
            continue
        for p in sorted(d.iterdir()):
            if not p.is_file():
                continue
            if p.stem.endswith("_right") or p.stem.endswith("_wrong"):
                continue
            items.append((lang, p))
    return items


def render_matrix_markdown(results: list[dict[str, Any]], title: str = "OptAgent Repair Matrix") -> str:
    cols = ["L0", "L1", "L2", "L3", "L4", "L5", "L6", "L7", "L8"]
    lines = [
        f"# {title}",
        "",
        "| Language | Fixture | " + " | ".join(cols) + " | First Failure Detail |",
        "|---|---|" + "|".join(["---"] * len(cols)) + "|---|",
    ]
    for r in results:
        cells = []
        fail_detail = ""
        for c in cols:
            info = r["layers"].get(c)
            if not info:
                cells.append("-")
            else:
                cells.append(info["status"])
                if info["status"] == "FAIL" and not fail_detail:
                    fail_detail = f"`{c}`: {info['detail'].replace('|', '/').replace(chr(10), ' ')[:140]}"
        lines.append(f"| {r['language']} | `{r['fixture']}` | " + " | ".join(cells) + f" | {fail_detail} |")
    lines.append("")
    passed_l8 = sum(1 for r in results if r["layers"].get("L8", {}).get("status") == "PASS")
    lines.append(f"**Summary**: {passed_l8}/{len(results)} fixtures reached L8 PASS.")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="OptAgent diagnostic layer ladder")
    ap.add_argument("--lang", help="Language (py, js, c, cpp)")
    ap.add_argument("--file", help="Path to fixture file")
    ap.add_argument("--all", action="store_true", help="Run all fixtures under examples/repair/")
    ap.add_argument("--no-llm", action="store_true", default=True, help="Disable LLM calls")
    ap.add_argument("--llm", action="store_true", help="Enable LLM calls")
    ap.add_argument("--out", help="Write Markdown matrix to this path")
    args = ap.parse_args(argv)
    use_llm = bool(args.llm)

    if args.all:
        all_res = []
        for lang, fp in discover_fixtures():
            print(f"Running {lang:10s} {fp.name} ...", flush=True)
            res = run_ladder(lang, fp, use_llm=use_llm)
            all_res.append(res)
            print(f"  -> highest={res['highest_pass']} first_fail={res['first_fail']}", flush=True)
        md = render_matrix_markdown(all_res)
        if args.out:
            outp = Path(args.out)
            outp.parent.mkdir(parents=True, exist_ok=True)
            outp.write_text(md, encoding="utf-8")
            print(f"Matrix written to {outp}")
        else:
            print(md)
        return 0

    if not args.lang or not args.file:
        ap.error("Provide --all or both --lang and --file")
    res = run_ladder(args.lang, Path(args.file), use_llm=use_llm)
    print(json.dumps(res, indent=2))
    return 0 if res["first_fail"] is None else 1


if __name__ == "__main__":
    raise SystemExit(main())
