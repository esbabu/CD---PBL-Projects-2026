"""BaseAnalyzer interface for SyntaxSense language analyzers."""

from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseAnalyzer(ABC):
    """Abstract base analyzer interface."""

    @property
    @abstractmethod
    def language_id(self) -> str:
        """Unique language identifier (lowercase, e.g. 'cpp', 'python', 'java')."""
        pass

    @property
    @abstractmethod
    def is_supported(self) -> bool:
        """Whether this language analyzer is currently implemented and supported."""
        pass

    @abstractmethod
    def analyze(self, code: str) -> Dict[str, Any]:
        """Analyze source code and return a structured dictionary conforming to AnalyzeResponse.

        Parameters:
            code: Source code text to analyze.

        Returns:
            Dictionary matching AnalyzeResponse schema:
            {
                "language": str,
                "analysisVersion": str,
                "classification": {
                    "label": str,
                    "confidence": float,
                    "source": str
                },
                "diagnostics": list[dict],
                "tokens": list[dict],
                "summary": {
                    "diagnosticCount": int,
                    "parserDiagnosticCount": int,
                    "sourceHeuristicDiagnosticCount": int
                }
            }
        """
        pass
