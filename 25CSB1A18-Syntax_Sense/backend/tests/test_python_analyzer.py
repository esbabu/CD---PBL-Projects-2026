"""Unit tests for PythonAnalyzer in SyntaxSense."""

import unittest
from backend.app.services.python_analyzer import PythonAnalyzer


class PythonAnalyzerTests(unittest.TestCase):
    def setUp(self):
        self.analyzer = PythonAnalyzer()

    def test_analyzer_metadata(self):
        self.assertEqual(self.analyzer.language_id, "python")
        self.assertTrue(self.analyzer.is_supported)

    def test_valid_python_program_reports_clean_status(self):
        source = (
            "def calculate_total(items: list[int]) -> int:\n"
            "    total = 0\n"
            "    for item in items:\n"
            "        total += item\n"
            "    return total\n\n"
            "values = [10, 20, 30]\n"
            "print(f'Total: {calculate_total(values)}')\n"
        )
        result = self.analyzer.analyze(source)

        self.assertEqual(result["language"], "python")
        self.assertEqual(result["analysisVersion"], "python-ast-v1")
        self.assertEqual(result["classification"]["label"], "CLEAN")
        self.assertEqual(result["classification"]["confidence"], 100.0)
        self.assertEqual(result["classification"]["source"], "ast_parser")
        self.assertEqual(result["summary"]["diagnosticCount"], 0)
        self.assertEqual(len(result["diagnostics"]), 0)

    def test_missing_colon_in_if_statement(self):
        source = "x = 10\nif x > 5\n    print('Greater')\n"
        result = self.analyzer.analyze(source)

        self.assertEqual(result["language"], "python")
        self.assertEqual(result["classification"]["label"], "MISSING_COLON")
        self.assertGreaterEqual(result["summary"]["diagnosticCount"], 1)

        diag = result["diagnostics"][0]
        self.assertEqual(diag["category"], "MISSING_COLON")
        self.assertEqual(diag["origin"], "parser")
        self.assertEqual(diag["line"], 2)
        self.assertIn("colon", diag["explanation"].lower())
        self.assertIn("add ':'", diag["suggestion"].lower())

    def test_missing_colon_in_def_function(self):
        source = "def add(a, b)\n    return a + b\n"
        result = self.analyzer.analyze(source)

        self.assertEqual(result["classification"]["label"], "MISSING_COLON")
        diag = result["diagnostics"][0]
        self.assertEqual(diag["category"], "MISSING_COLON")
        self.assertEqual(diag["line"], 1)

    def test_unexpected_indentation_error(self):
        source = "x = 1\n  y = 2\n"
        result = self.analyzer.analyze(source)

        self.assertIn(result["classification"]["label"], ("UNEXPECTED_INDENT", "INDENTATION_ERROR"))
        diag = result["diagnostics"][0]
        self.assertEqual(diag["category"], "UNEXPECTED_INDENT")
        self.assertEqual(diag["line"], 2)
        self.assertEqual(diag["origin"], "parser")

    def test_unindent_mismatch_error(self):
        source = "def process():\n    val = 10\n   val += 5\n    return val\n"
        result = self.analyzer.analyze(source)

        self.assertIn(result["classification"]["label"], ("UNINDENT_MISMATCH", "INDENTATION_ERROR"))
        diag = result["diagnostics"][0]
        self.assertEqual(diag["category"], "UNINDENT_MISMATCH")
        self.assertEqual(diag["line"], 3)

    def test_unclosed_parenthesis_reports_unmatched_delimiter(self):
        source = "total = (10 + 20\nprint(total)\n"
        result = self.analyzer.analyze(source)

        self.assertEqual(result["classification"]["label"], "UNMATCHED_DELIMITER")
        diag = result["diagnostics"][0]
        self.assertEqual(diag["category"], "UNMATCHED_DELIMITER")
        self.assertEqual(diag["line"], 1)

    def test_unclosed_square_bracket_reports_unmatched_delimiter(self):
        source = "numbers = [1, 2, 3\nprint(numbers)\n"
        result = self.analyzer.analyze(source)

        self.assertEqual(result["classification"]["label"], "UNMATCHED_DELIMITER")
        diag = result["diagnostics"][0]
        self.assertEqual(diag["category"], "UNMATCHED_DELIMITER")
        self.assertEqual(diag["line"], 1)

    def test_unclosed_string_literal(self):
        source = "message = 'hello world\nprint(message)\n"
        result = self.analyzer.analyze(source)

        self.assertEqual(result["classification"]["label"], "UNTERMINATED_STRING")
        diag = result["diagnostics"][0]
        self.assertEqual(diag["category"], "UNTERMINATED_STRING")
        self.assertEqual(diag["line"], 1)

    def test_invalid_assignment_to_literal(self):
        source = "100 = counter\n"
        result = self.analyzer.analyze(source)

        self.assertEqual(result["classification"]["label"], "INVALID_ASSIGNMENT")
        diag = result["diagnostics"][0]
        self.assertEqual(diag["category"], "INVALID_ASSIGNMENT")
        self.assertEqual(diag["line"], 1)

    def test_empty_input_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.analyzer.analyze("")

    def test_whitespace_only_input_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.analyzer.analyze("   \n\t  \n")

    def test_oversized_input_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.analyzer.analyze("x = 1\n" * 50000)

    def test_code_is_never_executed(self):
        # Code that raises ZeroDivisionError if executed, or modifies global state
        source = "x = 1 / 0\n"
        # Must parse cleanly as valid syntax without executing!
        result = self.analyzer.analyze(source)
        self.assertEqual(result["summary"]["diagnosticCount"], 0)
        self.assertEqual(result["classification"]["label"], "CLEAN")


if __name__ == "__main__":
    unittest.main()
