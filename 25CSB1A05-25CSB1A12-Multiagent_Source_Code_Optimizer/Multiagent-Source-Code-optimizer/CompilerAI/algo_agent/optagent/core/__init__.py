"""Core outcome, stage runner, and provenance abstractions for OptAgent."""
from .outcome import OptimizeOutcome, Reason, ReasonCode, REASON_REMEDIATION, StageResult, SupportLevel
from .provenance import ComponentKind, Provenance, ProvenanceSummary, ProvenanceTracker, component, get_component_registry
from .stages import StageRunner

__all__ = [
    "ComponentKind",
    "OptimizeOutcome",
    "Provenance",
    "ProvenanceSummary",
    "ProvenanceTracker",
    "Reason",
    "ReasonCode",
    "REASON_REMEDIATION",
    "StageResult",
    "StageRunner",
    "SupportLevel",
    "component",
    "get_component_registry",
]
