"""Language analyzer registry for SyntaxSense multi-language dispatch."""

from typing import Dict, List, Optional
from backend.app.services.base_analyzer import BaseAnalyzer
from backend.app.services.cpp_analyzer import CppAnalyzer
from backend.app.services.python_analyzer import PythonAnalyzer
from backend.app.services.java_analyzer import JavaAnalyzer


class UnsupportedLanguageError(Exception):
    """Raised when a requested language is not supported or is planned."""

    def __init__(self, language: str, supported: List[str], planned: List[str]):
        super().__init__(f"Language '{language}' is not supported.")
        self.language = language
        self.supported = supported
        self.planned = planned


LANGUAGE_ALIASES: Dict[str, str] = {
    "c++": "cpp",
    "cplusplus": "cpp",
    "py": "python",
}


class AnalyzerRegistry:
    """Registry maintaining active and planned language analyzers."""

    def __init__(self) -> None:
        self._analyzers: Dict[str, BaseAnalyzer] = {}
        self.register(CppAnalyzer())
        self.register(PythonAnalyzer())
        self.register(JavaAnalyzer())

    def register(self, analyzer: BaseAnalyzer) -> None:
        """Register an analyzer instance under its normalized language_id."""
        self._analyzers[analyzer.language_id.lower()] = analyzer

    def get_analyzer(self, language: str) -> BaseAnalyzer:
        """Look up an active analyzer for the given language.

        Raises:
            UnsupportedLanguageError if language is unknown or unsupported.
        """
        raw_lang = language.strip().lower() if language else ""
        lang = LANGUAGE_ALIASES.get(raw_lang, raw_lang)
        analyzer = self._analyzers.get(lang)
        if analyzer is None or not analyzer.is_supported:
            raise UnsupportedLanguageError(
                language=language,
                supported=self.supported_languages,
                planned=self.planned_languages,
            )
        return analyzer

    @property
    def supported_languages(self) -> List[str]:
        """List of active, fully-implemented language IDs."""
        return [aid for aid, a in self._analyzers.items() if a.is_supported]

    @property
    def planned_languages(self) -> List[str]:
        """List of recognized but not-yet-implemented language IDs."""
        return [aid for aid, a in self._analyzers.items() if not a.is_supported]


_default_registry = AnalyzerRegistry()


def get_default_registry() -> AnalyzerRegistry:
    """Return the global default analyzer registry instance."""
    return _default_registry
