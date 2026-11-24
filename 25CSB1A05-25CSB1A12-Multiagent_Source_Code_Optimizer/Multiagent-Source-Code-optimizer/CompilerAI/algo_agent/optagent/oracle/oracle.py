from __future__ import annotations
import ast
import hashlib
import random
import time
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from ..config import Settings
from ..runtime.sandbox import RunOpts, Sandbox
from ..schemas import IntentBundle
from .compare import Comparator
from .golden import make_golden
from .mutators import MutCtx, build_pool, mutate_args
from .scaling import scale_case
from .schema_infer import Gen, ParamSchema
from .schemas import Case, OracleBundle, Violation, split_of
from .shrink import shrink_args


def source_sha(source: str, language: str = "python") -> str:
    if language == "python":
        return hashlib.sha256(source.encode()).hexdigest()[:12]      # same rule as Step 1
    return hashlib.sha256(f"{language}\0{source}".encode()).hexdigest()[:12]


class Counterexample(BaseModel):
    case_id: str
    stage: str                                   # visible | fresh
    args: list[Any]
    kwargs: dict[str, Any] = {}
    violations: list[Violation]
    shrunk_args: list[Any] | None = None
    shrunk_kwargs: dict[str, Any] | None = None
    shrunk_violations: list[Violation] = []


class Verdict(BaseModel):
    passed: bool
    reason: str = ""
    counterexamples: list[Counterexample] = []
    warnings: list[Violation] = []               # non-blocking (type-confusion probes, aliasing notes)
    n_visible: int = 0
    n_holdout: int = 0
    n_fresh: int = 0
    holdout_failed: int = 0                      # count only: details are withheld on purpose
    scale: list[dict] = []
    oracle_tier: str = "D"
    feedback: str = ""                           # the ONLY text a proposer may see
    elapsed_s: float = 0.0


class Oracle:
    def __init__(self, bundle: OracleBundle, settings: Settings | None = None,
                 sandbox: Sandbox | None = None, adapter: Any = None):
        self.b = bundle
        self.s = settings or Settings()
        if adapter is None and getattr(bundle, "language", "python") != "python":
            from ..lang.registry import get_adapter
            adapter = get_adapter(bundle.language)
        self.adapter = adapter
        is_foreign = self.adapter is not None and self.adapter.id != "python"
        self.run_dir = Path(self.s.runs_dir) / bundle.source_sha / "oracle"
        self._hints: dict[str, Any] = {}
        if is_foreign:
            intent_p = Path(self.s.runs_dir) / bundle.source_sha / "intent.json"
            if intent_p.exists():
                try:
                    ib = IntentBundle.model_validate_json(intent_p.read_text(encoding="utf-8"))
                    fn_f = ib.module_facts.functions.get(bundle.entry_point)
                    if fn_f and isinstance(fn_f.extra, dict):
                        self._hints = dict(fn_f.extra.get("_hints") or {})
                except Exception:
                    pass
            ext = self.adapter.extensions[0]
            self.orig = self.run_dir / f"original{ext}"
            self.sb = sandbox or Sandbox(self.s, profile=self.adapter.sandbox_profile(self._hints))
        else:
            self.orig = self.run_dir / "original.py"
            self.sb = sandbox or Sandbox(self.s)
        props = self.run_dir / "props.py"
        self.props = str(props) if props.exists() and bundle.properties else None
        self.cmp = Comparator(bundle.contract, bundle.constraints, self.s.strict_probes)
        self.ps = ParamSchema(**bundle.param_schema)
        self.cases = {c.id: c for c in bundle.cases}

    # ---------- construction ----------
    @classmethod
    def load(cls, sha: str, settings: Settings | None = None) -> "Oracle":
        s = settings or Settings()
        p = Path(s.runs_dir) / sha / "oracle" / "oracle.json"
        if not p.exists():
            raise FileNotFoundError(f"{p} not found. Run: python -m optagent.cli_oracle build <file>")
        return cls(OracleBundle.model_validate_json(p.read_text(encoding="utf-8")), s)

    @property
    def entry(self) -> str:
        return self.b.entry_point

    def intent(self) -> IntentBundle:
        p = Path(self.s.runs_dir) / self.b.source_sha / "intent.json"
        return IntentBundle.model_validate_json(p.read_text(encoding="utf-8"))

    def save(self) -> None:
        (self.run_dir / "oracle.json").write_text(self.b.model_dump_json(indent=1), encoding="utf-8")

    # ---------- helpers ----------
    def _static(self, src: str) -> str | None:
        if self.adapter is not None and self.adapter.id != "python":
            try:
                mod = self.adapter.analyze(src, self._hints)
                if self.entry not in mod.functions:
                    return f"Candidate must define function '{self.entry}'."
            except Exception as e:
                return f"Candidate does not parse: {e}"
            return None
        try:
            tree = ast.parse(src)
        except SyntaxError as e:
            return f"Candidate does not parse: {e}"
        if self.entry == "__script__":
            return None
        if "." in self.entry:
            cls_name, meth_name = self.entry.split(".", 1)
            found = any(
                isinstance(c, ast.ClassDef)
                and c.name == cls_name
                and any(isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef)) and m.name == meth_name for m in c.body)
                for c in tree.body
            )
            if not found:
                return f"Candidate must define method '{self.entry}'."
            return None
        if not any(isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == self.entry for n in tree.body):
            return f"Candidate must define a top-level function named '{self.entry}'."
        return None

    def _path_for(self, src: str) -> Path:
        d = self.run_dir / "candidates"
        d.mkdir(parents=True, exist_ok=True)
        ext = self.adapter.extensions[0] if (self.adapter is not None and self.adapter.id != "python") else ".py"
        p = d / (hashlib.sha1(src.encode()).hexdigest()[:12] + ext)
        p.write_text(src, encoding="utf-8")
        return p

    def _run(self, cases: list[Case], path: Path, hs: bool):
        r0 = self.sb.run(path, self.entry, cases, RunOpts(hashseed=0, props_path=self.props))
        r1 = self.sb.run(path, self.entry, cases, RunOpts(hashseed=1, props_path=self.props)) if hs else None
        if self.adapter is not None and self.adapter.id != "python":
            r0 = [self.adapter.normalize_result(r) for r in r0]
            if r1 is not None:
                r1 = [self.adapter.normalize_result(r) for r in r1]
        return r0, r1

    def _judge(self, cases, gold, r0, r1):
        errs, warns = [], []
        for i, c in enumerate(cases):
            vs = self.cmp.compare(c, gold[c.id], r0[i], r1[i] if r1 else None)
            e = [v for v in vs if v.severity == "error"]
            warns += [v for v in vs if v.severity == "warn"]
            if e:
                errs.append((c, e))
        return errs, warns

    def _fresh_cases(self, n: int, rng: random.Random) -> list[Case]:
        base = [c for c in self.b.cases if c.kind == "valid"]
        gen = Gen(self.ps, rng, self.s.max_collection_len)
        pool = build_pool(self.orig.read_text(encoding="utf-8"), [c.py() for c in base[:200]])
        ctx = MutCtx(gen, pool, self.s.max_collection_len)
        others = [c.py() for c in rng.sample(base, min(20, len(base)))]
        fams = ["random", "sorted", "reversed", "all_equal", "few_unique"]
        out: dict[str, Case] = {}
        for _ in range(n * 3):
            if len(out) >= n:
                break
            if base and rng.random() < 0.65:
                a, k = rng.choice(base).py()
                a, k = mutate_args(a, k, rng, ctx, others=others)
            else:
                a, k = gen.case(rng.choice(fams))
            c = Case.make(a, k, "fresh", "fresh")
            if c.id in self.cases or c.id in out or c.size > 30000:
                continue
            out[c.id] = c
        return list(out.values())

    def _eval_case(self, case: Case, path: Path):
        g, _, _ = make_golden(self.sb, self.orig, self.entry, [case], props_path=self.props)
        if case.id not in g:
            return None, []
        r = self.sb.run_batch(path, self.entry, [case], RunOpts(props_path=self.props))[0]
        return g[case.id], [v for v in self.cmp.compare(case, g[case.id], r) if v.severity == "error"]

    def _shrink(self, case: Case, aspect: str, path: Path) -> Case | None:
        a, k = case.py()

        def fails(batch):
            cs = [Case.make(x, y, "shrink") for x, y in batch]
            g, _, _ = make_golden(self.sb, self.orig, self.entry, cs, props_path=self.props)
            res = self.sb.run(path, self.entry, cs, RunOpts(props_path=self.props))
            out = []
            for c, r in zip(cs, res):
                gr = g.get(c.id)
                out.append(bool(gr) and any(v.severity == "error" and v.aspect == aspect
                                            for v in self.cmp.compare(c, gr, r)))
            return out

        try:
            a2, k2 = shrink_args(a, k, fails)
        except Exception:
            return None
        return Case.make(a2, k2, "counterexample", "shrunk", case.kind)

    def _learn(self, case: Case, g) -> None:
        if case.id in self.cases:
            return
        c = case.model_copy(update={"origin": "counterexample"})
        self.cases[c.id] = c
        self.b.cases.append(c)
        self.b.golden[c.id] = g

    # ---------- scaling ----------
    def _scale(self, path: Path) -> list[dict]:
        mode = "multiset" if self.b.multiset_returns else "exact"
        pts = [p for p in self.b.scaling if p.status in ("ok", "exception")]
        alive = {(p.family, p.mode) for p in pts}
        rows: list[dict] = []
        for n in sorted({p.n for p in pts}):
            cur = [p for p in pts if p.n == n and (p.family, p.mode) in alive]
            if not cur:
                continue
            cases = [scale_case(self.ps, p) for p in cur]
            # single process on purpose: parallel workers would distort the timings
            res = self.sb.run_batch(path, self.entry, cases,
                                    RunOpts(timeout=self.s.scale_timeout_s, digest=mode))
            for p, r in zip(cur, res):
                match = self.cmp.compare_scale(p, r)
                sp = (p.orig_time_s / r.elapsed_s) if p.orig_time_s and r.elapsed_s else None
                rows.append({"family": p.family, "mode": p.mode, "n": n, "match": match,
                             "status": r.status, "orig_time_s": p.orig_time_s,
                             "cand_time_s": r.elapsed_s, "speedup": round(sp, 2) if sp else None})
                if not match or r.status in ("timeout", "crash"):
                    alive.discard((p.family, p.mode))
        return rows

    def check_scale(self, candidate_source: str) -> list[dict]:
        return self._scale(self._path_for(candidate_source))

    # ---------- the main gate ----------
    def check(self, candidate_source: str, *, fresh: int | None = None, shrink: bool = True,
              scale: bool = False, seed: int | None = None, learn: bool = True,
              hashseed_check: bool = True) -> Verdict:
        t0 = time.time()
        s = self.s
        fresh = s.fresh_default if fresh is None else fresh
        v = Verdict(passed=False, oracle_tier=self.b.strength.tier)
        bad = self._static(candidate_source)
        if bad:
            v.reason = v.feedback = bad
            v.elapsed_s = round(time.time() - t0, 2)
            return v
        path = self._path_for(candidate_source)
        hs = hashseed_check and self.cmp.must("determinism")
        gold = dict(self.b.golden)
        errs_all: list[tuple[Case, list[Violation], str]] = []
        warns: list[Violation] = []

        vis = [c for c in self.b.cases if split_of(c, s.holdout_pct) == "visible"]
        hold = [c for c in self.b.cases if split_of(c, s.holdout_pct) == "holdout"]
        vis.sort(key=lambda c: (0 if c.origin in ("counterexample", "mutant_killer", "llm") else 1, c.size))

        # stage 1: visible cases, small batches first (fail fast)
        i, step = 0, 48
        while i < len(vis):
            chunk = vis[i:i + step]
            r0, r1 = self._run(chunk, path, hs)
            errs, w = self._judge(chunk, gold, r0, r1)
            v.n_visible += len(chunk)
            warns += w
            if errs:
                errs_all += [(c, e, "visible") for c, e in errs]
                break
            i, step = i + step, step * 4

        # stage 2: hold-out (count only)
        if not errs_all and hold:
            r0, r1 = self._run(hold, path, hs)
            errs, w = self._judge(hold, gold, r0, r1)
            v.n_holdout, v.holdout_failed = len(hold), len(errs)
            warns += w

        # stage 3: fresh inputs the oracle has never seen
        fresh_gold: dict = {}
        if not errs_all and not v.holdout_failed and fresh > 0:
            rng = random.Random(seed if seed is not None else time.time_ns())
            fc = self._fresh_cases(fresh, rng)
            if fc:
                g, _, _ = make_golden(self.sb, self.orig, self.entry, fc, props_path=self.props)
                fc = [c for c in fc if c.id in g]
                r0, r1 = self._run(fc, path, hs)
                errs, w = self._judge(fc, g, r0, r1)
                v.n_fresh = len(fc)
                warns += w
                errs_all += [(c, e, "fresh") for c, e in errs]
                fresh_gold = g

        # counterexamples: one per distinct aspect (max 3), shrunk, and learned
        learned = False
        seen: set[str] = set()
        for c, e, stage in sorted(errs_all, key=lambda t: t[0].size):
            aspect = e[0].aspect
            if aspect in seen:
                continue
            seen.add(aspect)
            ce = Counterexample(case_id=c.id, stage=stage, args=c.args, kwargs=c.kwargs, violations=e[:3])
            if learn and stage == "fresh" and c.id in fresh_gold:
                self._learn(c, fresh_gold[c.id])
                learned = True
            if shrink and not aspect.startswith("determinism"):
                sc = self._shrink(c, aspect, path)
                if sc is not None and sc.id != c.id:
                    g2, sv = self._eval_case(sc, path)
                    if g2 is not None and sv:
                        ce.shrunk_args, ce.shrunk_kwargs, ce.shrunk_violations = sc.args, sc.kwargs, sv[:3]
                        if learn:
                            self._learn(sc, g2)
                            learned = True
            v.counterexamples.append(ce)
            if len(v.counterexamples) >= 3:
                break

        seen_w, uniq = set(), []
        for w in warns:
            if w.aspect not in seen_w:
                seen_w.add(w.aspect)
                uniq.append(w)
        v.warnings = uniq[:5]
        v.passed = not v.counterexamples and not v.holdout_failed

        if v.passed and scale:
            v.scale = self._scale(path)
            badrows = [r for r in v.scale if not r["match"]]
            if badrows:
                v.passed = False
                r = badrows[0]
                v.reason = (f"Output differs from the original on a scaling input "
                            f"({r['family']}/{r['mode']}, n={r['n']}, candidate status {r['status']}).")
        if not v.reason:
            if v.counterexamples:
                v.reason = f"{len(v.counterexamples)} behavioural difference(s) found"
            elif v.holdout_failed:
                v.reason = f"{v.holdout_failed} hidden check(s) failed"
            else:
                v.reason = "no difference found"
        v.feedback = self._feedback(v)
        v.elapsed_s = round(time.time() - t0, 2)
        if learned:
            self.save()
        return v

    # ---------- feedback text (safe to show to a proposer) ----------
    def _feedback(self, v: Verdict) -> str:
        if v.passed:
            return "PASS"
        from ..runtime import canon
        out = []
        for i, ce in enumerate(v.counterexamples, 1):
            args = ce.shrunk_args if ce.shrunk_args is not None else ce.args
            kw = ce.shrunk_kwargs if ce.shrunk_kwargs is not None else ce.kwargs
            vio = (ce.shrunk_violations or ce.violations)[0]
            out.append(f"Counterexample {i} [{vio.aspect}] {vio.detail}\n"
                       f"  call: {self.entry}(*{canon.decode(args)!r}, **{canon.decode(kw)!r})\n"
                       f"  expected (original): {vio.expected}\n  got (candidate):     {vio.actual}")
        if v.holdout_failed:
            out.append(f"{v.holdout_failed} of {v.n_holdout} hidden checks also failed (details withheld). "
                       "The candidate is wrong in ways not shown above; do not special-case the examples.")
        if not out:
            out.append(v.reason)
        return "\n".join(out)


def build_oracle(source: str, entry: str | None = None, overrides: dict | None = None, *,
                 use_llm: bool = True, settings: Settings | None = None,
                 run_mutation: bool = True, log=print, language: str | None = None,
                 adapter: Any = None, source_name: str = "input.py") -> Oracle:
    """Step 1 + Step 2 in one call (what the orchestrator uses)."""
    from ..intent.pipeline import IntentExtractor
    from .builder import OracleBuilder
    s = settings or Settings()
    if adapter is None:
        lang = language or (overrides or {}).get("language")
        if lang and lang != "python":
            from ..lang.registry import get_adapter
            adapter = get_adapter(lang)
    intent = IntentExtractor(s, use_llm=use_llm, adapter=adapter).run(
        source, entry=entry, overrides=overrides, source_name=source_name
    )
    bundle = OracleBuilder(s, use_llm=use_llm, log=log, adapter=adapter).build(intent, run_mutation=run_mutation)
    return Oracle(bundle, s, adapter=adapter)