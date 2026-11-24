"""Constructs the final optimization Report from pipeline stage artifacts."""
from __future__ import annotations

import difflib
import time
from pathlib import Path
from typing import Any

from ..complexity.schemas import AnalysisBundle
from ..config import Settings
from ..oracle.oracle import Oracle
from ..schemas import IntentBundle, Level
from ..search.schemas import SearchNode, SearchResult
from .render import render_json, render_markdown
from .schemas import (
    BenchmarkCurve,
    BenchmarkCurvePoint,
    ComplexityDiff,
    RejectedCandidate,
    Report,
)


class ReportBuilder:
    """Builds a complete, audit-grade optimization report."""

    def __init__(self, settings: Settings | None = None):
        self.s = settings or Settings()

    def build(
        self,
        intent: IntentBundle,
        oracle: Oracle,
        analysis: AnalysisBundle,
        search_result: SearchResult,
    ) -> Report:
        best_cand = search_result.best_candidate
        orig_src = intent.source
        opt_src = best_cand.source if best_cand else orig_src

        # Compute unified diff
        diff_lines = list(
            difflib.unified_diff(
                orig_src.splitlines(keepends=True),
                opt_src.splitlines(keepends=True),
                fromfile="original.py",
                tofile="optimized.py",
            )
        )
        diff_text = "".join(diff_lines)

        # Locate evaluated node for best candidate
        best_node: SearchNode | None = None
        if best_cand:
            best_node = next(
                (n for n in search_result.all_evaluated if n.candidate.id == best_cand.id and n.status == "benchmarked"),
                None,
            )

        # Complexity diff
        resolved = []
        if analysis.bottlenecks:
            resolved = [f"Line {b.line}: {b.pattern} ({b.detail})" for b in analysis.bottlenecks]

        comp_diff = ComplexityDiff(
            before_time=analysis.overall_time or "Unknown",
            after_time=best_cand.claimed_time if best_cand and best_cand.claimed_time else (analysis.overall_time or "Unknown"),
            before_space=analysis.overall_space or "Unknown",
            after_space=best_cand.claimed_space if best_cand and best_cand.claimed_space else (analysis.overall_space or "Unknown"),
            derivation=best_cand.rationale if best_cand else "No rewrite applied.",
            bottlenecks_resolved=resolved,
        )

        # Evidence & Rungs summary
        evidence_tier = "T0"
        rungs_summary: list[dict[str, Any]] = []
        warnings: list[str] = list(oracle.b.warnings)

        if best_node and best_node.evidence:
            evidence_tier = best_node.evidence.tier
            rungs_summary = [r.model_dump() for r in best_node.evidence.rungs]
            warnings.extend(best_node.evidence.warnings)

        # Benchmarks
        bench_curves: list[BenchmarkCurve] = []
        speedup = 1.0
        mem_ratio = 1.0

        if best_node and best_node.bench:
            speedup = best_node.bench.overall_speedup
            mem_ratio = best_node.bench.overall_mem_ratio
            for fam_name, fam_bench in best_node.bench.families.items():
                pts = [
                    BenchmarkCurvePoint(
                        n=p.n,
                        orig_time_s=p.orig_time_s,
                        cand_time_s=p.cand_stats.median,
                        speedup=p.speedup,
                    )
                    for p in fam_bench.points
                ]
                bench_curves.append(
                    BenchmarkCurve(
                        family=fam_name,
                        points=pts,
                        crossover_n=fam_bench.crossover_n,
                        max_speedup=fam_bench.max_n_speedup,
                    )
                )

        # Remaining behavioral differences (contract may_change items)
        remaining = [
            f"Aspect '{item.aspect.value if hasattr(item.aspect, 'value') else item.aspect}' may change (permitted by contract)."
            for item in intent.contract
            if item.level == Level.MAY
        ]

        # Rejected candidates
        rejected = [
            RejectedCandidate(
                candidate_id=n.candidate.id,
                proposer=n.candidate.proposer,
                transform_ids=n.candidate.transform_ids,
                reason=n.evidence.feedback if n.evidence else "Rejected during search",
                feedback=n.evidence.feedback if n.evidence else "",
            )
            for n in search_result.all_evaluated
            if n.status == "rejected"
        ]

        report = Report(
            source_sha=oracle.b.source_sha,
            entry_point=intent.entry_point,
            original_source=orig_src,
            optimized_source=opt_src,
            diff=diff_text,
            complexity=comp_diff,
            evidence_tier=evidence_tier,
            rungs_summary=rungs_summary,
            benchmarks=bench_curves,
            overall_speedup=speedup,
            overall_mem_ratio=mem_ratio,
            remaining_differences=remaining,
            rejected_candidates=rejected,
            warnings=warnings,
            created_at=time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        )

        # Persist report artifacts
        run_dir = Path(self.s.runs_dir) / oracle.b.source_sha
        run_dir.mkdir(parents=True, exist_ok=True)
        (run_dir / "report.json").write_text(render_json(report), encoding="utf-8")
        (run_dir / "report.md").write_text(render_markdown(report), encoding="utf-8")

        return report
