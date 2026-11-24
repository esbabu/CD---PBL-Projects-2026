from __future__ import annotations

import hashlib
import json
from pathlib import Path

from ..analysis.inputs import heuristic_seed_inputs
from ..analysis.static_facts import analyze_source, select_entry
from ..config import Settings
from ..core.provenance import ComponentKind, Provenance, current_tracker
from ..llm import prompts as P
from ..llm.client import LLMClient, LLMError
from ..runtime.executor import Executor
from ..schemas import (
    Aspect,
    Constraints,
    ExecRecord,
    FunctionFacts,
    IntentBundle,
    Level,
    PreservationItem,
    Source,
    Spec,
    ValidationReport,
)
from .contract import build_contract, reconcile_spec
from .input_agent import InputAgent, dedupe
from .spec_agent import SpecAgent
from .validator import SpecValidator


class IntentError(RuntimeError):
    pass


def _template_spec_from_facts(fn: FunctionFacts | None, entry: str, lang_id: str) -> Spec:
    """Deterministic fallback spec constructed strictly from static facts (zero LLM)."""
    if fn is None or entry == "__script__":
        return Spec(
            summary=f"Executable {lang_id} script reading stdin and writing stdout (heuristic template spec).",
            entry_point=entry,
            notes=["Generated deterministically from static facts (LLM off or unavailable)."],
        )
    params_sig = ", ".join(
        f"{p.name}: {p.annotation}" if p.annotation else p.name for p in fn.params
    )
    ret_sig = f" -> {fn.returns_annotation}" if fn.returns_annotation else ""
    notes = ["Generated deterministically from static facts (LLM off or unavailable)."]
    if fn.mutated_params:
        notes.append(f"Mutates parameters: {', '.join(fn.mutated_params)}")
    if fn.raises:
        notes.append(f"Explicitly raises: {', '.join(fn.raises)}")
    if fn.is_async:
        notes.append("Async coroutine entry point")
    if fn.is_generator:
        notes.append("Generator entry point (capped at 10,000 yielded items)")
    return Spec(
        summary=f"{entry}({params_sig}){ret_sig} ({lang_id})",
        entry_point=entry,
        notes=notes,
    )


class IntentExtractor:
    def __init__(self, settings: Settings | None = None, use_llm: bool = True, adapter=None):
        self.s = settings or Settings()
        self.use_llm = use_llm and (getattr(self.s, "llm_mode", "assist").lower() != "off")
        self.adapter = adapter
        self.executor = Executor(self.s)
        self.spec_llm = LLMClient(self.s.spec_model, self.s, "spec")
        self.pred_llm = LLMClient(self.s.predictor_model, self.s, "predictor")
        self.warnings: list[str] = []
        if self.use_llm and self.s.spec_model == self.s.predictor_model:
            self.warnings.append("spec and predictor use the SAME model: the cross-check is less independent.")

    def _run_seeds_sandbox(self, adapter, src_path: Path, entry: str, cases: list[dict], hints: dict) -> list[ExecRecord]:
        """Execute Step 1 golden seeds through Sandbox for non-Python languages."""
        from ..oracle.schemas import Case
        from ..runtime.sandbox import RunOpts, Sandbox

        sb = Sandbox(self.s, profile=adapter.sandbox_profile(hints))
        case_objs = [Case.make(c["args"], c.get("kwargs", {}), origin=c["origin"]) for c in cases]
        r0 = [adapter.normalize_result(r) for r in sb.run(src_path, entry, case_objs, RunOpts(hashseed=0))]
        r1 = [adapter.normalize_result(r) for r in sb.run(src_path, entry, case_objs, RunOpts(hashseed=1))]
        records: list[ExecRecord] = []
        for c, a, b in zip(cases, r0, r1):
            if a.status == "load_error":
                raise IntentError(f"Original code failed to load/compile: {a.exc_type}: {a.exc_msg}")
            nondet: list[str] = []
            if a.status == b.status and a.status in ("ok", "exception"):
                if json.dumps(a.ret, sort_keys=True) != json.dumps(b.ret, sort_keys=True):
                    nondet.append("return")
                if a.stdout != b.stdout:
                    nondet.append("stdout")
                if a.exc_type != b.exc_type:
                    nondet.append("exc_type")
                if json.dumps(a.mut, sort_keys=True) != json.dumps(b.mut, sort_keys=True):
                    nondet.append("mut")
            elif a.status != b.status:
                nondet.append("status")
            records.append(
                ExecRecord(
                    origin=c["origin"],
                    args=c["args"],
                    kwargs=c.get("kwargs", {}),
                    status=a.status,
                    ret=a.ret,
                    return_type=a.return_type,
                    exc_type=a.exc_type,
                    exc_msg=a.exc_msg,
                    stdout=a.stdout,
                    mutated_args=sorted(a.mut.keys()),
                    globals_changed=sorted(a.glob.keys()),
                    returns_input_alias=list(a.alias),
                    elapsed_s=a.elapsed_s,
                    generator=a.generator,
                    nondeterministic_fields=nondet,
                )
            )
        return records

    def run(
        self,
        source: str,
        entry: str | None = None,
        overrides: dict | None = None,
        source_name: str = "input.py",
        language: str | None = None,
        *,
        auto_select: bool = False,
        execute_seeds: bool = True,
    ) -> IntentBundle:
        overrides = overrides or {}
        warnings = list(self.warnings)
        adapter = self.adapter
        req_lang = language or overrides.get("language")
        if adapter is None and (req_lang or (source_name and not source_name.endswith(".py"))):
            from ..lang.registry import detect_language, get_adapter

            detected = detect_language(source_name if source_name != "input.py" else None, source, req_lang)
            if detected != "python":
                adapter = get_adapter(detected)
        is_foreign = adapter is not None and adapter.id != "python"
        lang_id = adapter.id if is_foreign else "python"
        hints = dict(overrides.get("hints") or {})

        # Injection 1: analyze & select_entry
        is_script = False
        if is_foreign:
            try:
                mod = adapter.analyze(source, hints)
            except Exception as e:
                raise IntentError(f"Source does not parse ({lang_id}): {e}")
            entry = adapter.select_entry(mod, entry or overrides.get("entry_point"))
            fn = mod.functions[entry]
            if hints:
                fn.extra["_hints"] = hints
        else:
            try:
                mod = analyze_source(source)
            except SyntaxError as e:
                raise IntentError(f"Source does not parse: {e}")
            req_e = entry or overrides.get("entry_point")
            if (not mod.functions and not req_e) or req_e == "__script__":
                entry = "__script__"
                is_script = True
                fn = FunctionFacts(name="__script__", lineno=1, end_lineno=len(source.splitlines()), params=[])
                mod.functions["__script__"] = fn
            else:
                entry = select_entry(mod, req_e, auto_select=auto_select)
                fn = mod.functions[entry]

        if is_foreign:
            sha = hashlib.sha256(f"{lang_id}\0{source}".encode()).hexdigest()[:12]
        else:
            sha = hashlib.sha256(source.encode()).hexdigest()[:12]
        run_dir = Path(self.s.runs_dir) / sha
        run_dir.mkdir(parents=True, exist_ok=True)
        orig_ext = adapter.extensions[0] if is_foreign else ".py"
        src_path = (run_dir / f"original{orig_ext}").resolve()
        src_path.write_text(source, encoding="utf-8")
        facts_text = P.render_facts(fn, mod)

        # Injection 4: Spec drafting (heuristic fallback guaranteed if LLM off or unavailable)
        spec = _template_spec_from_facts(fn, entry, lang_id)
        tracker = current_tracker()
        if self.use_llm:
            try:
                spec = SpecAgent(self.spec_llm).draft(source, entry, facts_text)
            except (LLMError, Exception) as e:
                warnings.append(f"LLM spec drafting failed (heuristic template used): {e}")
                if tracker is not None:
                    tracker.record(
                        Provenance(
                            kind=ComponentKind.HEURISTIC,
                            component="intent.spec_draft",
                            fallback_used=True,
                            fallback_reason=str(e),
                        )
                    )
        elif tracker is not None:
            tracker.record(Provenance(kind=ComponentKind.HEURISTIC, component="intent.spec_draft"))

        # Injection 2: seed inputs (user > heuristic ladder > LLM additive)
        cases = [dict(c, origin="user") for c in overrides.get("inputs", [])]
        if is_foreign:
            cases += [dict(c, origin="annotation") for c in adapter.seed_inputs(fn, hints)]
        else:
            strategy = "script" if is_script else "function"
            cases += [
                dict(c, origin=c.get("origin", "heuristic"))
                for c in heuristic_seed_inputs(None if is_script else fn, source=source, strategy=strategy)
            ]
        if self.use_llm and not is_script:
            try:
                cases += [
                    dict(c, origin="llm")
                    for c in InputAgent(self.spec_llm).generate(fn, spec, self.s.max_sample_inputs)
                ]
            except (LLMError, Exception) as e:
                warnings.append(f"LLM input generation failed (heuristic seeds kept): {e}")
                if tracker is not None:
                    tracker.record(
                        Provenance(
                            kind=ComponentKind.HEURISTIC,
                            component="intent.input_agent",
                            fallback_used=True,
                            fallback_reason=str(e),
                        )
                    )
        cases = dedupe(cases)
        if not cases:
            warnings.append(
                "No inputs available (no annotations, heuristic inference produced none, LLM disabled/failed). "
                "Provide 'inputs' in the overrides file."
            )

        # Injection 3: execute ORIGINAL on every input (Executor for Python, Sandbox for foreign)
        records: list[ExecRecord] = []
        if execute_seeds and cases:
            if is_foreign:
                records = self._run_seeds_sandbox(adapter, src_path, entry, cases, hints)
            else:
                consec_timeouts = 0
                for c in cases:
                    rec = self.executor.run_case(src_path, entry, c["args"], c.get("kwargs", {}), c["origin"])
                    if rec.status == "load_error":
                        raise IntentError(f"Original code failed to import/load: {rec.exc_type}: {rec.exc_msg}")
                    records.append(rec)
                    if rec.status == "timeout":
                        consec_timeouts += 1
                        if consec_timeouts >= 3 and not any(r.status in ("ok", "exception") for r in records):
                            warnings.append("Stopped seed execution early after 3 consecutive timeouts (possible infinite loop).")
                            break
                    else:
                        consec_timeouts = 0

        for r in records:
            if r.status in ("timeout", "crash"):
                warnings.append(f"input {json.dumps(r.args)[:80]} -> {r.status} {r.exc_msg or ''}".strip())
        executable = [r for r in records if r.status in ("ok", "exception")]

        # 4) validate the spec with an independent model, refine while it disagrees (graceful fallback)
        report = ValidationReport(status="skipped")
        if self.use_llm and executable and not is_script:
            try:
                validator, agent = SpecValidator(self.pred_llm, self.s), SpecAgent(self.spec_llm)
                for rnd in range(self.s.max_refine_rounds + 1):
                    rr = validator.validate(spec, fn, records)
                    report.rounds.append(rr)
                    if rr.score >= self.s.agreement_threshold or rnd == self.s.max_refine_rounds:
                        break
                    try:
                        spec = agent.refine(spec, source, entry, facts_text, [c for c in rr.cases if not c.agree])
                    except (LLMError, Exception) as e:
                        warnings.append(f"spec refinement failed: {e}")
                        break
                if report.rounds:
                    final = report.rounds[-1].score
                    report.status = (
                        "validated"
                        if final >= self.s.agreement_threshold
                        else "partially_validated"
                        if final >= 0.5
                        else "unvalidated"
                    )
                    if report.status != "validated":
                        warnings.append(
                            "Spec could not be validated: downstream steps must rely on golden executions, "
                            "not on the spec text."
                        )
            except (LLMError, Exception) as e:
                report = ValidationReport(status="skipped")
                warnings.append(f"Spec validation skipped due to LLM error: {e}")
                if tracker is not None:
                    tracker.record(
                        Provenance(
                            kind=ComponentKind.HEURISTIC,
                            component="intent.spec_validator",
                            fallback_used=True,
                            fallback_reason=str(e),
                        )
                    )

        # Injection 5: reconcile + contract + language contract rules
        spec = reconcile_spec(spec, fn, records)
        constraints = Constraints(**(overrides.get("constraints") or {}))
        contract = build_contract(fn, records, constraints, overrides if not is_foreign else None)

        # B1: Add self_state aspect for instance methods; B10: async aspect for async entries
        if not is_foreign and "." in entry and fn.extra.get("method_kind") == "instance":
            contract.append(
                PreservationItem(
                    aspect=Aspect.SELF_STATE,
                    applicable=True,
                    level=Level.MUST,
                    source=Source.STATIC,
                    rationale="Instance method may read/mutate `self` attributes; instance state must be preserved.",
                )
            )
        if not is_foreign and fn.is_async:
            contract.append(
                PreservationItem(
                    aspect=Aspect.ASYNC_SEMANTICS,
                    applicable=True,
                    level=Level.MUST,
                    source=Source.STATIC,
                    rationale="Entry point is an async coroutine; candidate must preserve async invocation semantics.",
                )
            )

        if is_foreign:
            existing_aspects = {it.aspect: i for i, it in enumerate(contract)}
            for rule in adapter.contract_rules():
                item = rule.evaluate(fn, records, hints)
                if item.aspect in existing_aspects:
                    contract[existing_aspects[item.aspect]] = item
                else:
                    existing_aspects[item.aspect] = len(contract)
                    contract.append(item)
            from ..schemas import Aspect as A, Level as L, Source as S

            for name, lvl in (overrides.get("preservation") or {}).items():
                aspect, level = A(name), L(lvl)
                for it in contract:
                    if it.aspect == aspect:
                        it.level, it.source = level, S.USER
                        it.rationale += " [user override]"

        bundle = IntentBundle(
            language=lang_id,
            source_sha=sha,
            source_path=source_name,
            entry_point=entry,
            source=source,
            module_facts=mod,
            spec=spec,
            contract=contract,
            constraints=constraints,
            golden_seed=records,
            validation=report,
            warnings=warnings,
        )
        (run_dir / "intent.json").write_text(bundle.model_dump_json(indent=2), encoding="utf-8")
        trace = self.spec_llm.trace + self.pred_llm.trace
        (run_dir / "llm_trace.json").write_text(json.dumps(trace, indent=2), encoding="utf-8")
        return bundle
