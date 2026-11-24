from typing import Dict, Any, Optional
from app.contracts.optimization import OptimizationResult
from app.contracts.security import SecurityResult, SecurityFinding

class ResultNormalizer:
    """
    Validates and normalizes raw dictionary payloads from agents into strongly-typed models.
    """

    @staticmethod
    def normalize_optimization(raw: Dict[str, Any], run_id: str) -> OptimizationResult:
        return OptimizationResult(
            run_id=run_id,
            status=raw.get("status", "completed"),
            optimized_code=raw.get("optimized_code"),
            transformations=raw.get("transformations", []),
            metrics=raw.get("metrics", {}),
            raw_result=raw,
            diagnostics=raw.get("diagnostics", []),
            duration_ms=raw.get("duration_ms", 0),
            is_demo=raw.get("is_demo", True),
        )

    @staticmethod
    def normalize_security(raw: Dict[str, Any], run_id: str, source_kind: str) -> SecurityResult:
        findings = []
        for f in raw.get("findings", []):
            if isinstance(f, dict):
                findings.append(SecurityFinding(**f))
            elif isinstance(f, SecurityFinding):
                findings.append(f)

        return SecurityResult(
            run_id=run_id,
            status=raw.get("status", "completed"),
            source_kind=source_kind,
            findings=findings,
            raw_result=raw,
            diagnostics=raw.get("diagnostics", []),
            duration_ms=raw.get("duration_ms", 0),
            is_demo=raw.get("is_demo", True),
        )
