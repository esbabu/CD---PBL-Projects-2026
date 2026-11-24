"""Forensic report generator: produces FORENSIC_REPORT.md and forensics.json."""
from __future__ import annotations

import json
from typing import Any
from pydantic import BaseModel, Field
from .decompose import ModuleDecomposition
from .crosscheck import AnalyzerBlindSpot
from .explain import Explanation
from .compare import ComparisonReport


class ForensicReportData(BaseModel):
    title: str = "OptAgent Forensic Analysis Report"
    target_file: str
    first_failing_point: str
    failure_chain: list[str] = Field(default_factory=list)
    per_unit_explanations: list[Explanation] = Field(default_factory=list)
    analyzer_blind_spots: list[AnalyzerBlindSpot] = Field(default_factory=list)
    predictions_evaluation: dict[str, str] = Field(default_factory=dict)
    actual_results: dict[str, Any] = Field(default_factory=dict)
    comparison: ComparisonReport | None = None
    timings: dict[str, float] = Field(default_factory=dict)
    provenance: dict[str, Any] = Field(default_factory=dict)


class ForensicReporter:
    """Generates FORENSIC_REPORT.md and forensics.json."""

    @classmethod
    def render_markdown(cls, data: ForensicReportData) -> str:
        lines = []
        lines.append(f"# {data.title}")
        lines.append("")
        lines.append(f"**Target File:** `{data.target_file}`  ")
        lines.append(f"**First Failing Point:** `{data.first_failing_point}`  ")
        lines.append("")

        lines.append("## 1. Executive Summary & Failure Chain")
        lines.append("")
        if data.failure_chain:
            for i, step in enumerate(data.failure_chain, 1):
                lines.append(f"{i}. {step}")
        else:
            lines.append("No critical pipeline failure recorded.")
        lines.append("")

        lines.append("## 2. Per-Unit Forensic Evaluation")
        lines.append("")
        lines.append("| Unit | Decision Step | Blocking Cause | Primary Reason | What Would Unlock |")
        lines.append("|---|---|---|---|---|")
        for exp in data.per_unit_explanations:
            lines.append(f"| `{exp.unit}` | {exp.decision_step} | `{exp.blocking_cause}` | {exp.primary_reason} | {exp.what_would_unlock} |")
        lines.append("")

        lines.append("## 3. Hypotheses Evaluation (Predictions P1 - P10)")
        lines.append("")
        lines.append("| Hypothesis | Status | Evidence / Observation |")
        lines.append("|---|---|---|")
        for pred, status_ev in data.predictions_evaluation.items():
            lines.append(f"| **{pred}** | {status_ev} |")
        lines.append("")

        lines.append("## 4. Analyzer Blind Spots (Static vs. Dynamic Disagreements)")
        lines.append("")
        if data.analyzer_blind_spots:
            lines.append("| Severity | Unit | Kind | Static Said | Dynamic Saw |")
            lines.append("|---|---|---|---|---|")
            for spot in data.analyzer_blind_spots:
                lines.append(f"| `{spot.severity}` | `{spot.unit}` | `{spot.kind}` | {spot.static_said} | {spot.dynamic_saw} |")
        else:
            lines.append("No analyzer blind spots detected.")
        lines.append("")

        if data.comparison:
            lines.append("## 5. Expected vs Actual Matrix")
            lines.append("")
            lines.append(f"**Summary:** {data.comparison.passed_units}/{data.comparison.total_units} units matched expected outcome.")
            lines.append("")
            lines.append("| Unit | Expected Status | Actual Status | Match | Speedup (Act / Exp) |")
            lines.append("|---|---|---|---|---|")
            for item in data.comparison.details:
                match_icon = "PASS" if item.status_pass and item.speedup_pass else "FAIL"
                exp_sp = f">={item.expected_min_speedup}x" if item.expected_min_speedup else "N/A"
                act_sp = f"{item.actual_speedup:.2f}x"
                lines.append(f"| `{item.unit}` | `{item.expected_status}` | `{item.actual_status}` | **{match_icon}** | {act_sp} / {exp_sp} |")
            lines.append("")

        lines.append("## 6. Provenance & Execution Timings")
        lines.append("")
        for k, v in data.timings.items():
            lines.append(f"- **{k}**: {v:.3f}s")
        lines.append("")

        return "\n".join(lines)

    @classmethod
    def save(cls, data: ForensicReportData, md_path: str, json_path: str) -> None:
        md_content = cls.render_markdown(data)
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(md_content)
        with open(json_path, "w", encoding="utf-8") as f:
            f.write(data.model_dump_json(indent=2))
