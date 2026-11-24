"""Multi-language adapter framework for OptAgent."""
from .base import (
    BenchProfile,
    BuildResult,
    Capabilities,
    ContractRule,
    LanguageAdapter,
    MutationOps,
    PromptPack,
    RulePack,
    Rung,
)
from .detect import detect_language, normalize_language
from .python_adapter import PythonAdapter
from .registry import get_adapter, list_adapters, register_adapter

__all__ = [
    "BenchProfile",
    "BuildResult",
    "Capabilities",
    "ContractRule",
    "LanguageAdapter",
    "MutationOps",
    "PromptPack",
    "PythonAdapter",
    "RulePack",
    "Rung",
    "detect_language",
    "get_adapter",
    "list_adapters",
    "normalize_language",
    "register_adapter",
]
