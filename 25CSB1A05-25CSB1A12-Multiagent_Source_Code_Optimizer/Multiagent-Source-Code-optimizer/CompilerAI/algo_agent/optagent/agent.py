"""OptimizerAgent facade: unified orchestrator for Triage + Steps 1 through 7."""
from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Callable

from pydantic import BaseModel, ConfigDict, Field

from .syntax import SyntaxGate
from .module import ModuleOptimizer
from .analysis.static_facts import AmbiguousEntry
from .bench.runner import BenchmarkRunner
from .complexity.analyzer import Analyzer
from .complexity.schemas import AnalysisBundle
from .complexity.static_cost import StaticCostAnalyzer
from .config import Settings
from .core.outcome import OptimizeOutcome, Reason, ReasonCode, StageResult, SupportLevel
from .core.provenance import ComponentKind, Provenance, ProvenanceTracker
from .core.stages import StageRunner
from .core.triage import ExecutionStrategy, run_triage
from .intent.pipeline import IntentExtractor
from .lang.registry import get_adapter
from .llm.gateway import OllamaGateway
from .memory.schemas import MemoryEntry
from .memory.store import MemoryStore
from .oracle.builder import OracleBuilder, OracleError
from .oracle.oracle import Oracle, source_sha
from .proposers.ensemble import ProposerEnsemble
from .report.builder import ReportBuilder
from .report.schemas import ComplexityDiff, Report
from .schemas import Constraints
from .search.controller import SearchController
from .search.schemas import SearchBudget, SearchResult
from .verify.ladder import Ladder


class OptimizeRequest(BaseModel):
    """Input request for optimizing an algorithm."""
    model_config = ConfigDict(extra="allow")

    source: str
    entry: str | None = None
    overrides: dict[str, Any] | None = None
    budget: SearchBudget | None = None
    constraints: Constraints | None = None
    use_llm: bool = False
    language: str | None = None
    source_name: str = "input.py"
    llm_mode: str | None = None            # off | assist | required
    accept_low_confidence: bool = False
    accept_unverified: bool = False
    module_mode: bool = False
    syntax_fix: bool = True


class OptimizeResult(BaseModel):
    """Result of the optimization pipeline."""
    model_config = ConfigDict(extra="allow")

    status: str = "ok"                     # ok | needs_input | error
    language: str = "python"
    report: Report | None = None
    bundle_paths: dict[str, str] = Field(default_factory=dict)
    candidates: list[str] = Field(default_factory=list)  # if needs_input (AmbiguousEntry)
    message: str = ""
    elapsed_s: float = 0.0
    outcome: OptimizeOutcome | None = None
    syntax_report: Any = None
    module_outcome: Any = None


class OptimizerAgent:
    """End-to-end agent orchestrating triage, intent, oracle, complexity, proposers, verification, benchmarking, and reporting."""

    def __init__(self, settings: Settings | None = None, log: Callable = print):
        self.s = settings or Settings()
        self.log = log
        self.memory = MemoryStore(self.s.memory_db_path)

    def _build_analysis_only_report(
        self,
        source: str,
        sha: str,
        lang_id: str,
        entry: str,
        reasons: list[Reason],
        intent=None,
    ) -> Report:
        """Produce an honest T0 UNVERIFIED static analysis report when execution is unavailable."""
        before_time, before_space, derivation = "", "", ""
        if intent is not None and entry in intent.module_facts.functions:
            try:
                t, sp, notes = StaticCostAnalyzer(intent).analyze_function(entry)
                before_time, before_space = t, sp
                derivation = "; ".join(notes)
            except Exception:
                pass
        warnings = [f"[{r.code.value}] {r.message} Remediation: {r.remediation}" for r in reasons]
        return Report(
            source_sha=sha,
            entry_point=entry or "<none>",
            original_source=source,
            optimized_source=source,
            complexity=ComplexityDiff(
                before_time=before_time,
                after_time=before_time,
                before_space=before_space,
                after_space=before_space,
                derivation=derivation or "Static analysis only (code not executed).",
            ),
            evidence_tier="T0",
            overall_speedup=1.0,
            overall_mem_ratio=1.0,
            warnings=warnings,
        )

    def run(
        self,
        req: OptimizeRequest,
        progress_callback: Callable[[str, str, float], None] | None = None,
    ) -> OptimizeResult:
        """Run the full optimization pipeline with typed outcomes and stage isolation."""
        t0 = time.time()

        def report_progress(stage: str, msg: str, pct: float):
            self.log(f"[{stage.upper()}] {msg} ({pct * 100:.0f}%)")
            if progress_callback:
                progress_callback(stage, msg, pct)

        with ProvenanceTracker() as tracker:
            runner = StageRunner()

            # ------------------------------------------------------------------
            # Stage S0: Syntax Gate (parse check, deterministic fixers, LLM patch)
            # ------------------------------------------------------------------
            syntax_report = None
            syntax_mode = getattr(self.s, "syntax_fix_mode", "auto")
            if getattr(req, "syntax_fix", True) and syntax_mode != "off":
                report_progress("syntax_gate", "Running syntax gate parse check and repair...", 0.02)
                llm_gw = OllamaGateway(self.s) if syntax_mode == "auto" else None
                gate = SyntaxGate(mode=syntax_mode, llm_gateway=llm_gw)
                repaired_source, syntax_report = gate.process(
                    req.source, language=req.language or "python"
                )
                if not syntax_report.ok:
                    last_round = syntax_report.rounds[-1] if syntax_report.rounds else None
                    err_dict = last_round.error if last_round else {}
                    err_msg = err_dict.get("message", "Syntax error")
                    err_line = err_dict.get("line", 1)
                    err_col = err_dict.get("column", 1)
                    syntax_reason = Reason(
                        code=ReasonCode.SYNTAX_ERROR,
                        message=f"SyntaxError at line {err_line}, col {err_col}: {err_msg}",
                        stage="syntax_gate",
                        remediation="Fix syntax errors in the source code before running optimization.",
                        detail={"line": err_line, "column": err_col, "error": err_msg},
                    )
                    outcome = OptimizeOutcome(
                        support_level=SupportLevel.REFUSED,
                        reasons=[syntax_reason],
                        stages=[StageResult(name="syntax_gate", status="failed", produced_by=["heuristic"])],
                        provenance=tracker.summary(),
                        language=req.language or "python",
                        syntax_report=syntax_report,
                    )
                    return OptimizeResult(
                        status="error",
                        language=outcome.language,
                        message=f"Syntax error at line {err_line}, col {err_col}: {err_msg}",
                        elapsed_s=round(time.time() - t0, 3),
                        outcome=outcome,
                        syntax_report=syntax_report,
                    )
                if syntax_report.repaired_sha and syntax_report.repaired_sha != syntax_report.original_sha:
                    req.source = repaired_source

            # ------------------------------------------------------------------
            # Module Mode: Multi-Unit Decomposition and Optimization
            # ------------------------------------------------------------------
            if req.module_mode or (req.entry is None and getattr(self.s, "module_mode", False)):
                report_progress("module_opt", "Running module-level multi-unit optimization...", 0.1)
                mod_opt = ModuleOptimizer(use_llm=req.use_llm)
                mod_outcome = mod_opt.optimize_module(req.source)
                outcome = OptimizeOutcome(
                    support_level=SupportLevel.FULL if mod_outcome.differential_verified else SupportLevel.VERIFIED_WEAK,
                    stages=[
                        StageResult(name="syntax_gate", status="ok", produced_by=["heuristic"]),
                        StageResult(name="module_optimization", status="ok", produced_by=["heuristic"]),
                    ],
                    provenance=tracker.summary(),
                    strategy="module",
                    language=req.language or "python",
                    syntax_report=syntax_report,
                    module_outcome=mod_outcome,
                )
                return OptimizeResult(
                    status="ok",
                    language=outcome.language,
                    message=f"Module optimization completed: {mod_outcome.verified_units_count} units optimized and verified.",
                    elapsed_s=round(time.time() - t0, 3),
                    outcome=outcome,
                    syntax_report=syntax_report,
                    module_outcome=mod_outcome,
                )

            # ------------------------------------------------------------------
            # Stage 0: Triage (syntax, language, deps, entry, toolchain)
            # ------------------------------------------------------------------
            report_progress("triage", "Running language, syntax, entry, and toolchain triage...", 0.05)
            triage, _ = runner.run_stage(
                "triage",
                lambda: run_triage(
                    req.source,
                    language=req.language,
                    source_name=req.source_name,
                    entry=req.entry,
                    overrides=req.overrides,
                    settings=self.s,
                ),
                critical=True,
                produced_by=["heuristic"],
            )
            if triage is None:
                outcome = OptimizeOutcome(
                    support_level=SupportLevel.REFUSED,
                    reasons=runner.reasons,
                    stages=runner.stages,
                    provenance=tracker.summary(),
                    language=req.language or "python",
                )
                return OptimizeResult(
                    status="error",
                    language=outcome.language,
                    message="Triage stage failed.",
                    elapsed_s=round(time.time() - t0, 3),
                    outcome=outcome,
                )

            lang_id = triage.language
            reasons: list[Reason] = list(triage.reasons)
            run_dir = Path(self.s.runs_dir) / (triage.source_sha or "refused")
            runner.set_run_dir(run_dir)

            # REFUSED (empty, syntax error, unsupported language, too large)
            if triage.strategy == ExecutionStrategy.REFUSED:
                outcome = OptimizeOutcome(
                    support_level=SupportLevel.REFUSED,
                    reasons=reasons,
                    stages=runner.stages,
                    provenance=tracker.summary(),
                    strategy=triage.strategy.value,
                    language=lang_id,
                    entry_point=triage.entry_point,
                )
                return OptimizeResult(
                    status="error",
                    language=lang_id,
                    message="; ".join(r.message for r in reasons) or "Input refused.",
                    elapsed_s=round(time.time() - t0, 3),
                    outcome=outcome,
                )

            # Preserve backward-compatible `needs_input` when Python has an exact tie between equal roots
            if (
                lang_id == "python"
                and not req.entry
                and not (req.overrides or {}).get("entry_point")
                and len(triage.entry_ranking) >= 2
                and triage.entry_ranking[0]["score"] == triage.entry_ranking[1]["score"]
                and not any("called_in_main" in r.get("signals", []) for r in triage.entry_ranking[:2])
                and not any("single_class_method" in r.get("signals", []) for r in triage.entry_ranking[:2])
            ):
                cands = [r["name"] for r in triage.entry_ranking]
                outcome = OptimizeOutcome(
                    support_level=SupportLevel.ANALYSIS_ONLY,
                    reasons=[
                        Reason(
                            code=ReasonCode.NO_ENTRY_FOUND,
                            message=f"Ambiguous entry point: tied candidates {cands}.",
                            remediation="Specify `entry` in the request or `--entry <name>`.",
                            stage="triage",
                            detail={"candidates": cands},
                        )
                    ],
                    stages=runner.stages,
                    provenance=tracker.summary(),
                    strategy=triage.strategy.value,
                    language=lang_id,
                )
                return OptimizeResult(
                    status="needs_input",
                    language=lang_id,
                    candidates=cands,
                    message=f"Ambiguous entry point: multiple top-level functions found {cands}. Please specify 'entry'.",
                    elapsed_s=round(time.time() - t0, 3),
                    outcome=outcome,
                )

            # ------------------------------------------------------------------
            # LLM Mode & Ollama Health Gate
            # ------------------------------------------------------------------
            eff_llm_mode = (req.llm_mode or (self.s.llm_mode if req.use_llm else "off")).lower()
            effective_use_llm = req.use_llm and eff_llm_mode != "off"
            if eff_llm_mode == "required":
                effective_use_llm = True

            if eff_llm_mode != "off" and effective_use_llm:
                gw = OllamaGateway(self.s)
                health = gw.check_health()
                if not health.reachable or not health.models:
                    llm_reason = Reason(
                        code=ReasonCode.LLM_UNAVAILABLE,
                        message=health.error or f"Ollama unavailable at {self.s.ollama_base}",
                        remediation=health.remediation,
                        stage="llm_health",
                        detail={"base_url": self.s.ollama_base, "reason_kind": health.reason_kind},
                    )
                    reasons.append(llm_reason)
                    if eff_llm_mode == "required":
                        outcome = OptimizeOutcome(
                            support_level=SupportLevel.REFUSED,
                            reasons=reasons,
                            stages=runner.stages,
                            provenance=tracker.summary(),
                            strategy=triage.strategy.value,
                            language=lang_id,
                            entry_point=triage.entry_point,
                        )
                        return OptimizeResult(
                            status="error",
                            language=lang_id,
                            message=f"LLM required but unavailable: {llm_reason.message}. {llm_reason.remediation}",
                            elapsed_s=round(time.time() - t0, 3),
                            outcome=outcome,
                        )
                    # assist mode: degrade cleanly to heuristics without aborting
                    effective_use_llm = False
                    tracker.record(
                        Provenance(
                            kind=ComponentKind.HEURISTIC,
                            component="llm.health",
                            fallback_used=True,
                            fallback_reason=llm_reason.message,
                        )
                    )

            adapter = get_adapter(lang_id)

            # ------------------------------------------------------------------
            # ANALYSIS_ONLY fast-degrade path (e.g. missing toolchain/dep/main-only)
            # ------------------------------------------------------------------
            if triage.strategy == ExecutionStrategy.ANALYSIS_ONLY:
                intent_static = None
                if triage.entry_point:
                    try:
                        extractor = IntentExtractor(self.s, use_llm=effective_use_llm, adapter=adapter)
                        intent_static = extractor.run(
                            req.source,
                            entry=triage.entry_point,
                            overrides=req.overrides,
                            source_name=req.source_name,
                            language=lang_id,
                            auto_select=True,
                            execute_seeds=False,
                        )
                    except Exception:
                        intent_static = None

                report = self._build_analysis_only_report(
                    req.source,
                    triage.source_sha,
                    lang_id,
                    triage.entry_point or "<none>",
                    reasons,
                    intent=intent_static,
                )
                runner.record_skipped("oracle")
                runner.record_skipped("search")
                outcome = OptimizeOutcome(
                    support_level=SupportLevel.ANALYSIS_ONLY,
                    reasons=reasons + runner.reasons,
                    stages=runner.stages,
                    provenance=tracker.summary(),
                    strategy=triage.strategy.value,
                    language=lang_id,
                    entry_point=triage.entry_point,
                    unverified=True,
                )
                return OptimizeResult(
                    status="ok",
                    language=lang_id,
                    report=report,
                    message=f"Analysis-only mode ({lang_id}): " + "; ".join(r.message for r in reasons),
                    elapsed_s=round(time.time() - t0, 3),
                    outcome=outcome,
                )

            # ------------------------------------------------------------------
            # Stage 1: Intent Extraction
            # ------------------------------------------------------------------
            report_progress("intent", "Extracting static facts and contract...", 0.10)
            extractor = IntentExtractor(self.s, use_llm=effective_use_llm, adapter=adapter)

            def _do_intent():
                return extractor.run(
                    req.source,
                    entry=req.entry or triage.entry_point,
                    overrides=req.overrides,
                    source_name=req.source_name,
                    language=lang_id,
                    auto_select=True,
                )

            intent, _ = runner.run_stage(
                "intent",
                _do_intent,
                critical=True,
                produced_by=["hybrid"] if effective_use_llm else ["heuristic"],
            )
            if intent is None:
                # Degrade to ANALYSIS_ONLY instead of bare crash
                all_reasons = reasons + runner.reasons
                report = self._build_analysis_only_report(
                    req.source, triage.source_sha, lang_id, triage.entry_point or "<none>", all_reasons
                )
                outcome = OptimizeOutcome(
                    support_level=SupportLevel.ANALYSIS_ONLY,
                    reasons=all_reasons,
                    stages=runner.stages,
                    provenance=tracker.summary(),
                    strategy=ExecutionStrategy.ANALYSIS_ONLY.value,
                    language=lang_id,
                    entry_point=triage.entry_point,
                    unverified=True,
                )
                return OptimizeResult(
                    status="ok",
                    language=lang_id,
                    report=report,
                    message=f"Degraded to analysis-only: {runner.reasons[-1].message if runner.reasons else 'intent failed'}",
                    elapsed_s=round(time.time() - t0, 3),
                    outcome=outcome,
                )

            sha = source_sha(intent.source, getattr(intent, "language", "python"))
            run_dir = Path(self.s.runs_dir) / sha
            run_dir.mkdir(parents=True, exist_ok=True)
            runner.set_run_dir(run_dir)
            bundle_paths = {"intent": str(run_dir / "intent.json")}

            # ------------------------------------------------------------------
            # Stage 2: Oracle Construction
            # ------------------------------------------------------------------
            report_progress("oracle", "Building test corpus and scaling set...", 0.25)
            oracle_json = run_dir / "oracle" / "oracle.json"

            def _do_oracle():
                if oracle_json.exists():
                    return Oracle.load(sha, self.s, adapter=adapter)
                bundle = OracleBuilder(
                    self.s,
                    use_llm=effective_use_llm,
                    log=lambda *a: None,
                    adapter=adapter,
                ).build(intent, run_mutation=True)
                return Oracle(bundle, self.s, adapter=adapter)

            oracle, _ = runner.run_stage(
                "oracle",
                _do_oracle,
                critical=True,
                produced_by=["tool", "heuristic"],
                reason_code=ReasonCode.NO_SEED_INPUTS if not intent.golden_seed else ReasonCode.STAGE_ERROR,
            )
            if oracle is None:
                all_reasons = reasons + runner.reasons
                report = self._build_analysis_only_report(
                    req.source, sha, lang_id, intent.entry_point, all_reasons, intent=intent
                )
                outcome = OptimizeOutcome(
                    support_level=SupportLevel.ANALYSIS_ONLY,
                    reasons=all_reasons,
                    stages=runner.stages,
                    provenance=tracker.summary(),
                    strategy=ExecutionStrategy.ANALYSIS_ONLY.value,
                    language=lang_id,
                    entry_point=intent.entry_point,
                    unverified=True,
                )
                return OptimizeResult(
                    status="ok",
                    language=lang_id,
                    report=report,
                    bundle_paths=bundle_paths,
                    message=f"Degraded to analysis-only: {runner.reasons[-1].message if runner.reasons else 'oracle failed'}",
                    elapsed_s=round(time.time() - t0, 3),
                    outcome=outcome,
                )

            bundle_paths["oracle"] = str(oracle_json)
            oracle_tier = oracle.b.strength.tier if oracle.b.strength else "D"

            # ------------------------------------------------------------------
            # Stage 3: Complexity Analysis & Profiler
            # ------------------------------------------------------------------
            report_progress("complexity", "Analyzing static and empirical complexity...", 0.40)

            def _do_analysis():
                return Analyzer(self.s, log=lambda *a: None).analyze(intent, oracle)

            def _fallback_analysis(_exc: Exception) -> AnalysisBundle:
                t_c, s_c, notes = StaticCostAnalyzer(intent).analyze_function(intent.entry_point)
                return AnalysisBundle(
                    source_sha=sha,
                    entry_point=intent.entry_point,
                    static_time=t_c,
                    static_space=s_c,
                    reconciled_time=t_c,
                    reconciled_space=s_c,
                    findings=notes,
                )

            analysis, _ = runner.run_stage(
                "complexity",
                _do_analysis,
                fallback=_fallback_analysis,
                produced_by=["heuristic", "tool"],
            )
            bundle_paths["analysis"] = str(run_dir / "analysis" / "analysis.json")

            # ------------------------------------------------------------------
            # Stage 4: Proposers Ensemble
            # ------------------------------------------------------------------
            report_progress("proposers", "Assembling proposers and rule catalog...", 0.50)
            proposers = ProposerEnsemble(self.s, use_llm=effective_use_llm)

            # ------------------------------------------------------------------
            # Stage 5 & 6: Verification Ladder, Benchmarking & Search
            # ------------------------------------------------------------------
            report_progress("search", "Exploring transformation candidates...", 0.65)

            def _do_search():
                ladder = Ladder(oracle, self.s, log=lambda *a: None)
                bench = BenchmarkRunner(oracle, self.s, log=lambda *a: None)
                controller = SearchController(
                    oracle,
                    analysis,
                    proposers,
                    ladder,
                    bench,
                    self.s,
                    log=lambda *a: None,
                )
                return controller.run(req.budget)

            search_res, _ = runner.run_stage(
                "search",
                _do_search,
                fallback=lambda _exc: SearchResult(
                    source_sha=sha,
                    entry_point=intent.entry_point,
                    best_candidate=None,
                    all_evaluated=[],
                    stop_reason="search_degraded",
                ),
                produced_by=["hybrid"] if effective_use_llm else ["heuristic", "tool"],
            )

            # ------------------------------------------------------------------
            # Stage 7: Reporting & Memory
            # ------------------------------------------------------------------
            report_progress("report", "Generating report and updating memory...", 0.90)
            builder = ReportBuilder(self.s)
            report, _ = runner.run_stage(
                "report",
                lambda: builder.build(intent, oracle, analysis, search_res),
                fallback=lambda _exc: self._build_analysis_only_report(
                    req.source, sha, lang_id, intent.entry_point, reasons + runner.reasons, intent=intent
                ),
                produced_by=["heuristic"],
            )
            bundle_paths["report_json"] = str(run_dir / "report.json")
            bundle_paths["report_md"] = str(run_dir / "report.md")

            # Persist memory entries safely
            try:
                if search_res and search_res.best_candidate and report:
                    self.memory.store_positive(
                        MemoryEntry(
                            id=f"{sha}_{search_res.best_candidate.id}",
                            pattern_key="algorithm_optimization",
                            conditions=["pure" if intent.contract else "general"],
                            original_snippet=intent.source,
                            rewrite_snippet=search_res.best_candidate.source,
                            transform_ids=search_res.best_candidate.transform_ids,
                            speedup=report.overall_speedup,
                            mem_ratio=report.overall_mem_ratio,
                            evidence_tier=report.evidence_tier,
                            is_positive=True,
                        )
                    )
                if search_res:
                    for n in search_res.all_evaluated:
                        if n.status == "rejected" and n.evidence:
                            self.memory.store_negative(
                                MemoryEntry(
                                    id=f"{sha}_{n.candidate.id}",
                                    pattern_key="rejected_candidate",
                                    conditions=[],
                                    original_snippet=intent.source,
                                    rewrite_snippet=n.candidate.source,
                                    transform_ids=n.candidate.transform_ids,
                                    speedup=0.0,
                                    mem_ratio=1.0,
                                    evidence_tier="REJECTED",
                                    is_positive=False,
                                    failure_reason=n.evidence.feedback,
                                )
                            )
            except Exception:
                pass

            # Determine honest support_level from oracle tier
            all_reasons = reasons + runner.reasons
            if oracle_tier in ("C", "D"):
                support_level = SupportLevel.VERIFIED_WEAK
                low_conf = True
                all_reasons.append(
                    Reason(
                        code=ReasonCode.ORACLE_WEAK,
                        message=f"Oracle strength is Tier {oracle_tier}; verification confidence is low.",
                        stage="oracle",
                        detail={"oracle_tier": oracle_tier},
                    )
                )
            else:
                support_level = SupportLevel.FULL
                low_conf = False

            outcome = OptimizeOutcome(
                support_level=support_level,
                reasons=all_reasons,
                stages=runner.stages,
                provenance=tracker.summary(),
                strategy=triage.strategy.value,
                language=lang_id,
                entry_point=intent.entry_point,
                low_confidence=low_conf,
                unverified=False,
            )

            report_progress("complete", "Optimization complete.", 1.0)
            return OptimizeResult(
                status="ok",
                language=lang_id,
                report=report,
                bundle_paths=bundle_paths,
                message=f"Optimization complete ({support_level.value}, {lang_id}) with speedup {report.overall_speedup:.2f}x at evidence tier {report.evidence_tier}.",
                elapsed_s=round(time.time() - t0, 3),
                outcome=outcome,
            )
