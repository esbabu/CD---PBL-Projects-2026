"""Unit tests for AnalyzerRegistry in SyntaxSense."""

import unittest
from backend.app.services.base_analyzer import BaseAnalyzer
from backend.app.services.registry import (
    AnalyzerRegistry,
    UnsupportedLanguageError,
    get_default_registry,
)
from backend.app.services.cpp_analyzer import CppAnalyzer
from backend.app.services.python_analyzer import PythonAnalyzer
from backend.app.services.java_analyzer import JavaAnalyzer


class DummyPlannedAnalyzer(BaseAnalyzer):
    @property
    def language_id(self) -> str:
        return "kotlin"

    @property
    def is_supported(self) -> bool:
        return False

    def analyze(self, code: str):
        raise NotImplementedError("Planned")


class RegistryTests(unittest.TestCase):
    def setUp(self):
        self.registry = AnalyzerRegistry()

    def test_default_registry_has_expected_languages(self):
        reg = get_default_registry()
        self.assertIn("cpp", reg.supported_languages)
        self.assertIn("python", reg.supported_languages)
        self.assertIn("java", reg.supported_languages)

    def test_get_cpp_analyzer(self):
        analyzer = self.registry.get_analyzer("cpp")
        self.assertIsInstance(analyzer, CppAnalyzer)
        self.assertEqual(analyzer.language_id, "cpp")
        self.assertTrue(analyzer.is_supported)

    def test_get_python_analyzer(self):
        analyzer = self.registry.get_analyzer("python")
        self.assertIsInstance(analyzer, PythonAnalyzer)
        self.assertEqual(analyzer.language_id, "python")
        self.assertTrue(analyzer.is_supported)

    def test_get_java_analyzer(self):
        analyzer = self.registry.get_analyzer("java")
        self.assertIsInstance(analyzer, JavaAnalyzer)
        self.assertEqual(analyzer.language_id, "java")
        self.assertTrue(analyzer.is_supported)

    def test_case_insensitive_lookup(self):
        self.assertIsInstance(self.registry.get_analyzer("CPP"), CppAnalyzer)
        self.assertIsInstance(self.registry.get_analyzer("Python"), PythonAnalyzer)
        self.assertIsInstance(self.registry.get_analyzer("JAVA"), JavaAnalyzer)

    def test_planned_language_raises_unsupported_language_error(self):
        self.registry.register(DummyPlannedAnalyzer())
        with self.assertRaises(UnsupportedLanguageError) as ctx:
            self.registry.get_analyzer("kotlin")

        exc = ctx.exception
        self.assertEqual(exc.language, "kotlin")
        self.assertIn("kotlin", exc.planned)
        self.assertIn("cpp", exc.supported)
        self.assertIn("python", exc.supported)
        self.assertIn("java", exc.supported)

    def test_unknown_language_raises_unsupported_language_error(self):
        with self.assertRaises(UnsupportedLanguageError) as ctx:
            self.registry.get_analyzer("rust")

        exc = ctx.exception
        self.assertEqual(exc.language, "rust")
        self.assertNotIn("rust", exc.supported)
        self.assertNotIn("rust", exc.planned)


if __name__ == "__main__":
    unittest.main()
