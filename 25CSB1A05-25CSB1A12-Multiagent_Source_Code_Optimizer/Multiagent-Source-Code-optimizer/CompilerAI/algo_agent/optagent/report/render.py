"""Markdown and JSON renderers for OptAgent reports."""
from __future__ import annotations

from .schemas import Report


def render_markdown(report: Report) -> str:
    """Render a comprehensive GitHub-flavored Markdown report."""
    lines: list[str] = [
        f"# OptAgent Optimization Report: `{report.entry_point}`",
        f"**Source SHA:** `{report.source_sha}` | **Timestamp:** {report.created_at}",
        "",
        "## 1. Executive Summary",
        f"- **Measured Speedup:** **{report.overall_speedup:.2f}x**",
        f"- **Memory Ratio:** **{report.overall_mem_ratio:.2f}x** ({'Memory reduced' if report.overall_mem_ratio < 1.0 else 'Memory preserved/increased'})",
        f"- **Evidence Tier:** **{report.evidence_tier}**",
        f"- **Time Complexity:** `{report.complexity.before_time}` -> `{report.complexity.after_time}`",
        f"- **Space Complexity:** `{report.complexity.before_space}` -> `{report.complexity.after_space}`",
        "",
        "## 2. Code Transformation",
        "```diff",
        report.diff.strip() if report.diff else "# No diff (identical)",
        "```",
        "",
        "### Optimized Implementation",
        "```python",
        report.optimized_source.strip(),
        "```",
        "",
        "## 3. Complexity Analysis & Derivation",
        f"- **Derivation:** {report.complexity.derivation}",
    ]

    if report.complexity.bottlenecks_resolved:
        lines.append("- **Resolved Bottlenecks:**")
        for b in report.complexity.bottlenecks_resolved:
            lines.append(f"  - {b}")

    lines.extend([
        "",
        "## 4. Verification Ladder",
        "| Rung | Status | Details |",
        "|---|---|---|",
    ])
    for r in report.rungs_summary:
        status_icon = "PASS" if r.get("passed") else ("SKIP" if r.get("skipped") else "FAIL")
        lines.append(f"| `{r.get('rung')}` | **{status_icon}** | {r.get('reason') or str(r.get('details', ''))[:60]} |")

    lines.extend([
        "",
        "## 5. Benchmark Scaling Curves",
    ])

    if report.benchmarks:
        for bench in report.benchmarks:
            lines.append(f"### Family: `{bench.family}`" + (f" (Crossover N: {bench.crossover_n})" if bench.crossover_n else ""))
            lines.append("| Input Size (N) | Original Time (s) | Candidate Time (s) | Speedup |")
            lines.append("|---|---|---|---|")
            for pt in bench.points:
                lines.append(f"| {pt.n:,} | {pt.orig_time_s:.6f} | {pt.cand_time_s:.6f} | **{pt.speedup:.2f}x** |")
            lines.append("")
    else:
        lines.append("_No empirical scaling points recorded._")

    if report.remaining_differences:
        lines.extend([
            "",
            "## 6. Remaining Behavioral Differences (Contract May-Change)",
        ])
        for diff in report.remaining_differences:
            lines.append(f"- {diff}")

    if report.rejected_candidates:
        lines.extend([
            "",
            "## 7. Rejected Candidates",
            "| Candidate ID | Proposer | Reason |",
            "|---|---|---|",
        ])
        for rej in report.rejected_candidates:
            lines.append(f"| `{rej.candidate_id}` | `{rej.proposer}` | {rej.reason[:70]} |")

    if report.warnings:
        lines.extend([
            "",
            "## 8. Warnings",
        ])
        for w in report.warnings:
            lines.append(f"- {w}")

    return "\n".join(lines) + "\n"


def render_json(report: Report) -> str:
    """Render report to formatted JSON."""
    return report.model_dump_json(indent=2)
