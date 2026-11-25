"""CppAnalyzer adapter for SyntaxSense C++ analysis pipeline."""

from typing import Any, Dict
from backend.app.services.base_analyzer import BaseAnalyzer
from backend.app.services.cpp_analysis import analyze_cpp_source


class CppAnalyzer(BaseAnalyzer):
    """Adapter wrapping existing C++ AST, source heuristics, and Random Forest classifier."""

    @property
    def language_id(self) -> str:
        return "cpp"

    @property
    def is_supported(self) -> bool:
        return True

    def analyze(self, code: str) -> Dict[str, Any]:
        return analyze_cpp_source(code)
