"""Analyzer orchestrator for Step 3: static + empirical + profiling -> AnalysisBundle."""
from __future__ import annotations

import time
from pathlib import Path

from ..config import Settings
from ..oracle.schemas import OracleBundle
from ..schemas import IntentBundle
from .empirical import fit_scaling_data
from .profiler import Profiler
from .reconcile import reconcile_complexity
from .schemas import AnalysisBundle, FunctionComplexity
from .static_cost import StaticCostAnalyzer


class Analyzer:
    def __init__(self, settings: Settings | None = None, log=print):
        self.s = settings or Settings()
        self.log = log

    def analyze(self, intent: IntentBundle, oracle: OracleBundle | None = None) -> AnalysisBundle:
        t0 = time.time()
        entry = intent.entry_point
        sha = intent.source_sha
        self.log(f"[analyzer] analyzing {entry} (sha {sha})...")

        # 1. Static Cost Walk
        static_analyzer = StaticCostAnalyzer(intent)
        static_time, static_space, static_findings = static_analyzer.analyze_function(entry)
        self.log(f"[analyzer] static prediction: time={static_time}, space={static_space}")

        # 2. Empirical Scaling Fit
        time_fit = None
        scaling_pts = getattr(oracle, "scaling", None) or (oracle.b.scaling if hasattr(oracle, "b") else None)
        if scaling_pts:
            time_fit, _ = fit_scaling_data(scaling_pts)
            self.log(f"[analyzer] empirical time fit: {time_fit.model} (R^2 = {time_fit.r2:.3f})")

        # 3. Profiler & Bottleneck Ranking
        profiler = Profiler(self.s, self.log)
        bottlenecks, space_fit = profiler.profile(intent, oracle)
        if space_fit:
            self.log(f"[analyzer] empirical space fit: {space_fit.model}")
        if bottlenecks:
            top_bn = bottlenecks[0]
            self.log(f"[analyzer] top bottleneck: L{top_bn.line} '{top_bn.pattern}' ({top_bn.share_of_time:.1%} time)")

        # 4. Reconciliation
        reconciled_time, reconciled_space, rec_findings = reconcile_complexity(
            static_time, static_space, time_fit, space_fit
        )
        self.log(f"[analyzer] reconciled: time={reconciled_time}, space={reconciled_space}")

        # 5. Assemble Bundle
        fn_comp = FunctionComplexity(
            name=entry,
            static_time=static_time,
            static_space=static_space,
            empirical_time=time_fit.model if time_fit else None,
            empirical_space=space_fit.model if space_fit else None,
            time_fit=time_fit,
            space_fit=space_fit,
            reconciled_time=reconciled_time,
            reconciled_space=reconciled_space,
            bottlenecks=bottlenecks,
            findings=static_findings + rec_findings,
        )

        bundle = AnalysisBundle(
            source_sha=sha,
            entry_point=entry,
            functions={entry: fn_comp},
            overall_time=reconciled_time,
            overall_space=reconciled_space,
            bottlenecks=bottlenecks,
            findings=static_findings + rec_findings,
            warnings=[],
        )

        # 6. Save Bundle to runs/<sha>/analysis/analysis.json
        out_dir = Path(self.s.runs_dir) / sha / "analysis"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = out_dir / "analysis.json"
        out_file.write_text(bundle.model_dump_json(indent=2), encoding="utf-8")
        self.log(f"[analyzer] DONE in {time.time() - t0:.2f}s -> {out_file}")

        return bundle

