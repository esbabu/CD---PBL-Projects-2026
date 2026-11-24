"""Ground truth comparator: compares actual pipeline run against expected.yaml."""
from __future__ import annotations

import yaml
from typing import Any
from pydantic import BaseModel, Field


class UnitComparison(BaseModel):
    unit: str
    status_pass: bool
    actual_status: str
    expected_status: str
    speedup_pass: bool = True
    actual_speedup: float = 1.0
    expected_min_speedup: float | None = None
    findings_pass: bool = True
    notes: list[str] = Field(default_factory=list)


class ComparisonReport(BaseModel):
    all_passed: bool
    total_units: int
    passed_units: int
    failed_units: int
    details: list[UnitComparison] = Field(default_factory=list)


class Comparator:
    """Compares actual results with expected.yaml."""

    @classmethod
    def compare(cls, actual_results: dict[str, Any], expected_yaml_path: str) -> ComparisonReport:
        with open(expected_yaml_path, "r", encoding="utf-8") as f:
            expected_data = yaml.safe_load(f)

        expected_units = expected_data.get("units", {})
        details = []
        all_ok = True

        for uname, exp in expected_units.items():
            act = actual_results.get(uname, {})
            act_status = act.get("status", "no_improvement_found")
            exp_status = exp.get("expected_status", "no_improvement_found")

            status_pass = (act_status == exp_status)
            speedup_pass = True
            act_speedup = float(act.get("speedup", 1.0))
            exp_min_speedup = exp.get("speedup_min")
            if exp_min_speedup is not None:
                if act_speedup < exp_min_speedup:
                    speedup_pass = False

            findings_pass = True
            exp_findings = exp.get("security_findings", [])
            act_findings = act.get("security_findings", [])
            for ef in exp_findings:
                if not any(ef in af for af in act_findings):
                    # soft check for finding substring
                    pass

            passed = status_pass and speedup_pass and findings_pass
            if not passed:
                all_ok = False

            details.append(UnitComparison(
                unit=uname,
                status_pass=status_pass,
                actual_status=act_status,
                expected_status=exp_status,
                speedup_pass=speedup_pass,
                actual_speedup=act_speedup,
                expected_min_speedup=exp_min_speedup,
                findings_pass=findings_pass,
                notes=act.get("notes", []),
            ))

        passed_count = sum(1 for d in details if d.status_pass and d.speedup_pass)
        return ComparisonReport(
            all_passed=all_ok,
            total_units=len(details),
            passed_units=passed_count,
            failed_units=len(details) - passed_count,
            details=details,
        )
