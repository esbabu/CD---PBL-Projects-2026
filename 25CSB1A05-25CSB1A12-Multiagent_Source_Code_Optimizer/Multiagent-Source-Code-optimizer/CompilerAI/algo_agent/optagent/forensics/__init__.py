"""OptAgent Forensics: Reverse-Engineering & Root-Cause Failure Analysis Tool."""
from .recorder import ForensicRecorder, UnitFunnel, DropEvent, StageProbeRecord, drop, register_probe
from .locator import ExceptionLocator, LocatedException
from .decompose import UnitDecomposer, UnitSpec, ModuleDecomposition
from .probe import DynamicBehaviorProbe, DynamicFacts, DynamicEffect
from .crosscheck import StaticVsDynamicCrossCheck, AnalyzerBlindSpot
from .explain import Explainer, Explanation
from .minimize import Minimizer, MinimizeResult
from .compare import Comparator, ComparisonReport, UnitComparison
from .report import ForensicReporter, ForensicReportData

__all__ = [
    "ForensicRecorder",
    "UnitFunnel",
    "DropEvent",
    "StageProbeRecord",
    "drop",
    "register_probe",
    "ExceptionLocator",
    "LocatedException",
    "UnitDecomposer",
    "UnitSpec",
    "ModuleDecomposition",
    "DynamicBehaviorProbe",
    "DynamicFacts",
    "DynamicEffect",
    "StaticVsDynamicCrossCheck",
    "AnalyzerBlindSpot",
    "Explainer",
    "Explanation",
    "Minimizer",
    "MinimizeResult",
    "Comparator",
    "ComparisonReport",
    "UnitComparison",
    "ForensicReporter",
    "ForensicReportData",
]
