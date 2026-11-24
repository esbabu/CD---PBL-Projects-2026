from __future__ import annotations
import ast
import random
import time
from pathlib import Path

from ..config import Settings
from ..llm.client import LLMClient
from ..runtime.sandbox import RunOpts, Sandbox
from ..schemas import IntentBundle, ModuleFacts
from .agents import AdversaryAgent, PropertyAgent
from .compare import Comparator
from .fuzzer import CoverageFuzzer
from .golden import make_golden
from .hyp import hypothesis_inputs
from .mutation import MutationTester, SurvivorHunter
from .mutators import MutCtx, build_pool, mutate_args
from .scaling import build_scaling
from .schema_infer import Gen, infer_params
from .schemas import (Case, CoverageInfo, GoldenRecord, MutationReport, OracleBundle,
                      PropertySpec, StrengthReport, split_of)


class OracleError(RuntimeError):
    pass


def executable_lines(source: str, mod: ModuleFacts, entry: str) -> tuple[set[int], set[str]]:
    """Statement lines of the entry function/method/script and everything it calls locally."""
    lines: set[int] = set()
    tree = ast.parse(source)
    if entry == "__script__":
        for sub in ast.walk(tree):
            if sub is tree or not isinstance(sub, ast.stmt):
                continue
            if isinstance(sub, (ast.Global, ast.Nonlocal, ast.Try)):
                continue
            if isinstance(sub, ast.Expr) and isinstance(sub.value, ast.Constant):
                continue
            lines.add(sub.lineno)
        return lines, {"__script__"}

    reach, stack = {entry}, [entry]
    while stack:
        cur = stack.pop()
        fn_obj = mod.functions.get(cur)
        if not fn_obj:
            continue
        for c in fn_obj.callees_local:
            if c not in reach:
                reach.add(c)
                stack.append(c)

    def _collect(fn_node: ast.AST) -> None:
        for sub in ast.walk(fn_node):
            if sub is fn_node or not isinstance(sub, ast.stmt):
                continue
            if isinstance(sub, (ast.Global, ast.Nonlocal, ast.Try)):
                continue  # no reliable line event
            if isinstance(sub, ast.Expr) and isinstance(sub.value, ast.Constant):
                continue  # docstrings
            lines.add(sub.lineno)

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in reach:
            _collect(node)
        elif isinstance(node, ast.ClassDef):
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and f"{node.name}.{item.name}" in reach:
                    _collect(item)
    return lines, reach


def grade(cov: float, mscore: float | None, n_holdout: int) -> str:
    if mscore is None:
        return "C" if cov >= 0.85 else "D"
    if cov >= 0.95 and mscore >= 0.90 and n_holdout > 0:
        return "A"
    if cov >= 0.85 and mscore >= 0.80:
        return "B"
    if cov >= 0.70 and mscore >= 0.60:
        return "C"
    return "D"


class OracleBuilder:
    def __init__(self, settings: Settings | None = None, use_llm: bool = True, log=print, adapter=None):
        self.s = settings or Settings()
        self.use_llm, self.log = use_llm, log
        self.adapter = adapter
        self.llm = LLMClient(self.s.spec_model, self.s, "oracle") if use_llm else None

    # ------------------------------------------------------------------
    def _validated_props(self, sb, src, entry, cands: list[PropertySpec], cases: list[Case],
                         odir: Path, warns: list[str]) -> list[PropertySpec]:
        """A property is kept only if it holds on EVERY valid case for the ORIGINAL function."""
        cand_path = odir / "props_candidates.py"
        cand_path.write_text("\n\n".join(p.code for p in cands), encoding="utf-8")
        res = sb.run(src, entry, cases[:300], RunOpts(props_path=str(cand_path)))
        bad, ran = set(), 0
        for r in res:
            if r.status == "ok":
                ran += 1
                bad |= {p.rstrip("!") for p in r.prop_failures}
        good = [p for p in cands if p.name not in bad] if ran else []
        dropped = [p.name for p in cands if p.name in bad]
        if dropped:
            warns.append(f"Discarded LLM properties that the ORIGINAL violates: {dropped}")
        if good:
            (odir / "props.py").write_text("\n\n".join(p.code for p in good), encoding="utf-8")
        return good

    # ------------------------------------------------------------------
    def build(self, intent: IntentBundle, run_mutation: bool = True) -> OracleBundle:
        s, log = self.s, self.log
        t0 = time.time()
        adapter = self.adapter
        if adapter is None and getattr(intent, "language", "python") != "python":
            from ..lang.registry import get_adapter
            adapter = get_adapter(intent.language)
        is_foreign = adapter is not None and adapter.id != "python"
        odir = Path(s.runs_dir) / intent.source_sha / "oracle"
        odir.mkdir(parents=True, exist_ok=True)
        (odir / "props.py").unlink(missing_ok=True)
        orig_ext = adapter.extensions[0] if is_foreign else ".py"
        src = odir / f"original{orig_ext}"
        src.write_text(intent.source, encoding="utf-8")
        entry = intent.entry_point
        is_script = entry == "__script__"
        fn = intent.module_facts.functions.get(entry)
        hints = dict(fn.extra.get("_hints") or {}) if (fn is not None and isinstance(getattr(fn, "extra", None), dict)) else {}
        # B8: Adaptive per-case timeout calibrated from Step 1 golden seed timings
        seed_times = sorted(r.elapsed_s for r in intent.golden_seed if r.status == "ok" and r.elapsed_s > 0)
        if seed_times:
            median_t = seed_times[min(len(seed_times) // 2, 2)]
            adaptive_t = max(s.case_timeout_s, min(60.0, max(2.0, 50.0 * median_t)))
            if adaptive_t > s.case_timeout_s:
                from dataclasses import replace
                s = replace(s, case_timeout_s=round(adaptive_t, 2))
        sb = Sandbox(s, profile=adapter.sandbox_profile(hints)) if is_foreign else Sandbox(s)
        rng = random.Random(s.rand_seed)
        warns: list[str] = []
        if not sb.is_isolated:
            warns.append("LOCAL sandbox in use: resource limits only, no network/filesystem isolation. "
                         "Run only trusted code, or install Docker.")
        log(f"[oracle] sandbox={sb.backend}  entry={entry}")
        comparator = Comparator(intent.contract, intent.constraints, s.strict_probes)
        if is_foreign:
            exec_lines, reach = adapter.executable_lines(intent.source, intent.module_facts, entry)
        else:
            exec_lines, reach = executable_lines(intent.source, intent.module_facts, entry)
        state = {"props": None}

        # ---------------- 1. seed corpus + schema ----------------
        corpus: dict[str, Case] = {}

        def add(c: Case) -> None:
            corpus.setdefault(c.id, c)

        for r in intent.golden_seed:
            add(Case.make(r.args, r.kwargs, origin=r.origin, category="seed"))
        if not corpus:
            raise OracleError("No seed inputs from Step 1. Provide 'inputs' in the overrides file.")
        if len(intent.golden_seed) >= 3 and all(r.status == "timeout" for r in intent.golden_seed):
            raise OracleError("All seed inputs timed out (possible infinite loop or excessive runtime).")
        ok_seed = [Case.make(r.args, r.kwargs).py() for r in intent.golden_seed if r.status == "ok"]
        ps = adapter.param_schema(fn, hints, ok_seed or [c.py() for c in corpus.values()]) if (is_foreign and fn is not None) else None
        if ps is None:
            ps = infer_params(ok_seed or [c.py() for c in corpus.values()])
        gen = Gen(ps, rng, s.max_collection_len)
        pool = build_pool(intent.source, [c.py() for c in corpus.values()])
        ctx = MutCtx(gen, pool, s.max_collection_len)
        log(f"[oracle] schema: {[v.kind for v in ps.args]}  derived-int slots: "
            f"{[i for i, v in enumerate(ps.args) if v.derived]}")

        # ---------------- 2. generated corpus ----------------
        if not is_script:
            fams = ["random", "sorted", "reversed", "all_equal", "few_unique"]
            for i in range(s.n_family):
                a, k = gen.case(fams[i % 5])
                add(Case.make(a, k, "family", fams[i % 5]))
            try:
                for a, k in hypothesis_inputs(ps, s.n_hypothesis, s.rand_seed, s.max_collection_len):
                    add(Case.make(a, k, "hypothesis", "hypothesis"))
            except Exception as e:
                warns.append(f"Hypothesis generation failed: {e}")
            base = list(corpus.values())
            for _ in range(s.n_probe):
                a, k = rng.choice(base).py()
                a2, k2 = mutate_args(a, k, rng, ctx, force_probe=True)
                add(Case.make(a2, k2, "probe", "type_confusion", "probe"))
        log(f"[oracle] generated corpus: {len(corpus)} candidate cases")

        # ---------------- 3. LLM properties (validated against the original) ----------------
        props: list[PropertySpec] = []
        if self.use_llm and self.llm is not None and fn is not None and not is_foreign:
            try:
                cands = PropertyAgent(self.llm).propose(intent, fn)
                if cands:
                    valid = [c for c in corpus.values() if c.kind == "valid"]
                    props = self._validated_props(sb, src, entry, cands, valid, odir, warns)
                    if props:
                        state["props"] = str(odir / "props.py")
                log(f"[oracle] properties: {len(props)} kept of {len(cands)} proposed")
            except Exception as e:
                warns.append(f"LLM property proposal skipped (fallback): {e}")

        # ---------------- 4. golden execution + coverage ----------------
        golden: dict[str, GoldenRecord] = {}
        case_lines: dict[str, set[int]] = {}

        def ingest() -> int:
            todo = [c for c in corpus.values() if c.id not in golden]
            if not todo:
                return 0
            if is_foreign and hasattr(adapter, "make_golden_extra"):
                g, dropped, lines, extra_warns = adapter.make_golden_extra(sb, src, entry, todo, hints, cov=True)
                warns.extend(extra_warns)
            else:
                g, dropped, lines = make_golden(sb, src, entry, todo, cov=True, props_path=state["props"])
            if is_foreign:
                for gr in g.values():
                    gr.result = adapter.normalize_result(gr.result)
                    if gr.alt is not None:
                        gr.alt = adapter.normalize_result(gr.alt)
            golden.update(g)
            case_lines.update(lines)
            for c, _status, _msg in dropped:
                corpus.pop(c.id, None)
            if dropped:
                reasons = sorted({d[1] for d in dropped})
                warns.append(f"{len(dropped)} generated inputs dropped (original {'/'.join(reasons)}).")
            return len(g)

        def covered() -> set[int]:
            out: set[int] = set()
            for cid, ls in case_lines.items():
                c = corpus.get(cid)
                if c is not None and c.kind == "valid":
                    out |= ls
            return out & exec_lines

        log(f"[oracle] golden runs (2 hash seeds, coverage on): {ingest()} cases")
        if not golden:
            raise OracleError("The original failed or timed out on every input. "
                              "Check the seeds, the sandbox, or case_timeout_s.")
        log(f"[oracle] line coverage so far: {len(covered())}/{len(exec_lines)}")

        # ---------------- 5. coverage-guided fuzzing ----------------
        fuzz_res = None
        seeds = sorted((c for c in corpus.values() if c.kind == "valid" and c.id in golden),
                       key=lambda c: c.size)[:150]
        if seeds and s.fuzz_budget_s > 0 and not is_script:
            fuzz_res = CoverageFuzzer(sb, s, src, entry, ctx, rng, state["props"], log).run(seeds, s.fuzz_budget_s)
            for c in fuzz_res.new_cases:
                add(c)
            log(f"[oracle] fuzzer: +{len(fuzz_res.new_cases)} cases ({fuzz_res.stop_reason}); "
                f"golden for {ingest()} new")

        # ---------------- 6. LLM red-team rounds (aim at uncovered lines) ----------------
        adv = AdversaryAgent(self.llm) if (self.use_llm and self.llm is not None and fn is not None and not is_script) else None
        if adv:
            try:
                for rnd in range(2):
                    unc = sorted(exec_lines - covered())
                    if rnd == 1 and not unc:
                        break
                    for a, k in adv.propose(intent, fn, s.n_adversarial, unc):
                        try:
                            add(Case.make(a, k, "llm", "adversarial"))
                        except Exception:
                            continue
                    ingest()
                    log(f"[oracle] red-team round {rnd + 1}: coverage {len(covered())}/{len(exec_lines)}")
            except Exception as e:
                warns.append(f"LLM red-team generation skipped (fallback): {e}")

        # ---------------- 7. scaling set ----------------
        multiset = not comparator.must("return_order")
        scaling = []
        if not is_script:
            try:
                scaling = build_scaling(sb, src, entry, ps, multiset, s, log)
            except Exception as e:
                warns.append(f"Scaling set could not be built: {e}")

        # ---------------- 8. mutation testing + survivor hunting ----------------
        mut_report: MutationReport | None = None
        if run_mutation and not is_script:
            mut_cases = [c for c in corpus.values() if c.id in golden]
            tester = MutationTester(sb, s, comparator, log)
            if is_foreign:
                mops = adapter.mutation_ops()
                if mops.generate is not None:
                    tester.generate = lambda source, reachable, r: mops.generate(source, reachable, s.max_mutants, r)  # type: ignore[assignment]
                tester._ext = mops.file_extension  # type: ignore[attr-defined]
            rep = tester.run(entry, intent.source, reach, mut_cases, golden, covered(), state["props"], rng)
            survivors = sorted((m for m in rep.mutants if m.status == "survived"), key=lambda m: m.line_covered)
            log(f"[oracle] mutation score {rep.score} ({rep.killed}/{rep.total}); hunting "
                f"{min(len(survivors), s.hunt_max_survivors)} of {len(survivors)} survivors")
            hunter = SurvivorHunter(sb, s, comparator, ctx, src, entry, state["props"], rng, log)
            valid_pool = [c for c in corpus.values() if c.kind == "valid" and c.id in golden]
            killers: list[Case] = []
            mut_ext = getattr(tester, "_ext", ".py")
            for info in survivors[:s.hunt_max_survivors]:
                m = tester.mutants[info.id]
                mpath = Path(tester._tmp.name) / f"mutant_{info.id}{mut_ext}"
                parents = [c for c in valid_pool if info.line in case_lines.get(c.id, ())] or valid_pool
                parents = rng.sample(parents, min(40, len(parents)))
                extra = list(killers)
                if adv:
                    try:
                        for a, k in adv.targeted(intent, fn, info.desc, info.line):
                            try:
                                extra.append(Case.make(a, k, "llm", "targeted"))
                            except Exception:
                                continue
                    except Exception:
                        pass
                hit = hunter.hunt(m, mpath, parents, extra)
                info.hunted = True
                if hit:
                    c, g, lines = hit
                    info.status, info.killed_by, info.by_visible = "killed", c.id, False
                    corpus[c.id], golden[c.id], case_lines[c.id] = c, g, lines
                    killers.append(c)
                else:
                    info.likely_equivalent = True
            mut_report = MutationTester.summarize(rep.mutants)
            eq = sum(1 for i in mut_report.mutants if i.status == "survived" and i.likely_equivalent)
            denom = mut_report.total - eq
            mut_report.score = round(mut_report.killed / denom, 3) if denom else 0.0
            log(f"[oracle] after hunting: score {mut_report.score} "
                f"(raw {round(mut_report.killed / max(mut_report.total, 1), 3)}, "
                f"{eq} survivors judged likely-equivalent, {len(killers)} new killer inputs)")

        # ---------------- 9. assemble, grade, save ----------------
        final = [c for c in corpus.values() if c.id in golden]
        cov_lines = covered()
        total = len(exec_lines)
        cov_frac = round(len(cov_lines) / total, 3) if total else 1.0
        coverage = CoverageInfo(lines_total=total, lines_covered=len(cov_lines),
                                uncovered=sorted(exec_lines - cov_lines),
                                arcs_observed=sum(">" in e for e in fuzz_res.edges) if fuzz_res else 0)
        n_hold = sum(split_of(c, s.holdout_pct) == "holdout" for c in final)
        n_vis = len(final) - n_hold
        mscore = mut_report.score if mut_report else None
        tier = grade(cov_frac, mscore, n_hold)
        notes: list[str] = []
        if coverage.uncovered:
            notes.append(f"Lines never executed by any valid input: {coverage.uncovered}")
        if mut_report:
            unhunted = [i for i in mut_report.mutants
                        if i.status == "survived" and not i.likely_equivalent]
            if unhunted:
                notes.append("Survivors not hunted or not killed: " +
                             "; ".join(f"L{i.line} {i.op} ({i.desc})" for i in unhunted[:8]))
            notes.append(f"visible-only mutation score {mut_report.score_visible_only}")
        else:
            notes.append("Mutation testing skipped: tier capped at C.")
        if n_hold == 0:
            notes.append("No hold-out cases: reward-hacking defense is inactive.")
        if not props:
            notes.append("No validated properties (LLM disabled or all rejected).")
        strength = StrengthReport(tier=tier, line_coverage=cov_frac, mutation_score=mscore,
                                  n_cases=len(final), n_visible=n_vis, n_holdout=n_hold,
                                  n_probes=sum(c.kind == "probe" for c in final), notes=notes)
        bundle = OracleBundle(
            language=getattr(intent, "language", "python"),
            source_sha=intent.source_sha, entry_point=entry, param_schema=ps.model_dump(),
            contract=intent.contract, constraints=intent.constraints, cases=final,
            golden={c.id: golden[c.id] for c in final}, properties=props, scaling=scaling,
            coverage=coverage, mutation=mut_report, strength=strength, multiset_returns=multiset,
            warnings=warns)
        (odir / "oracle.json").write_text(bundle.model_dump_json(indent=1), encoding="utf-8")
        if self.llm:
            import json
            (odir / "llm_trace.json").write_text(json.dumps(self.llm.trace, indent=2), encoding="utf-8")
        log(f"[oracle] DONE in {time.time() - t0:.1f}s  tier={tier}  cases={len(final)}  -> {odir / 'oracle.json'}")
        return bundle