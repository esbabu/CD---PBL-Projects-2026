"""Unit tests for JavaAnalyzer in SyntaxSense."""

import unittest
from backend.app.services.java_analyzer import JavaAnalyzer


class JavaAnalyzerTests(unittest.TestCase):
    def setUp(self):
        self.analyzer = JavaAnalyzer()

    def test_analyzer_metadata(self):
        self.assertEqual(self.analyzer.language_id, "java")
        self.assertTrue(self.analyzer.is_supported)

    def test_valid_java_program_reports_clean_status(self):
        source = (
            "package com.example.app;\n\n"
            "public class Calculator {\n"
            "    private int total = 0;\n\n"
            "    public Calculator(int initial) {\n"
            "        this.total = initial;\n"
            "    }\n\n"
            "    public int add(int a, int b) {\n"
            "        return a + b;\n"
            "    }\n\n"
            "    public static void main(String[] args) {\n"
            "        Calculator calc = new Calculator(10);\n"
            "        int res = calc.add(5, 7);\n"
            "        System.out.println(\"Result: \" + res);\n"
            "    }\n"
            "}\n"
        )
        result = self.analyzer.analyze(source)

        self.assertEqual(result["language"], "java")
        self.assertEqual(result["analysisVersion"], "java-ast-v1")
        self.assertEqual(result["classification"]["label"], "CLEAN")
        self.assertEqual(result["classification"]["confidence"], 100.0)
        self.assertEqual(result["classification"]["source"], "java_parser")
        self.assertEqual(result["summary"]["diagnosticCount"], 0)
        self.assertEqual(len(result["diagnostics"]), 0)

    def test_valid_java_with_comments_and_escaped_strings_produces_zero_diagnostics(self):
        source = (
            "public class StringsAndComments {\n"
            "    // Single-line comment with braces {} and semicolons ;;\n"
            "    /* Multi-line comment\n"
            "       containing if (x > 0) { return; } */\n"
            "    private String text = \"String with \\\"escaped quotes\\\" and {braces} and ;;\";\n"
            "    private char quote = '\\'';\n"
            "    private char newline = '\\n';\n"
            "    \n"
            "    public void run() {\n"
            "        System.out.println(text);\n"
            "    }\n"
            "}\n"
        )
        result = self.analyzer.analyze(source)
        self.assertEqual(result["summary"]["diagnosticCount"], 0)
        self.assertEqual(result["classification"]["label"], "CLEAN")

    def test_missing_semicolon_in_variable_declaration(self):
        source = (
            "public class Main {\n"
            "    public static void main(String[] args) {\n"
            "        int x = 10\n"
            "        System.out.println(x);\n"
            "    }\n"
            "}\n"
        )
        result = self.analyzer.analyze(source)

        self.assertEqual(result["classification"]["label"], "MISSING_SEMICOLON")
        self.assertGreaterEqual(result["summary"]["diagnosticCount"], 1)

        diag = result["diagnostics"][0]
        self.assertEqual(diag["category"], "MISSING_SEMICOLON")
        self.assertEqual(diag["line"], 3)
        self.assertEqual(diag["origin"], "parser")
        self.assertIn("semicolon", diag["explanation"].lower())

    def test_missing_semicolon_in_return_statement(self):
        source = (
            "public class Main {\n"
            "    public int getValue() {\n"
            "        return 42\n"
            "    }\n"
            "}\n"
        )
        result = self.analyzer.analyze(source)

        self.assertEqual(result["classification"]["label"], "MISSING_SEMICOLON")
        diag = result["diagnostics"][0]
        self.assertEqual(diag["category"], "MISSING_SEMICOLON")
        self.assertEqual(diag["line"], 3)

    def test_unmatched_opening_brace(self):
        source = (
            "public class Main {\n"
            "    public static void main(String[] args) {\n"
            "        int x = 1;\n"
            "    return;\n"
            "}\n"
        )
        result = self.analyzer.analyze(source)

        self.assertEqual(result["classification"]["label"], "UNMATCHED_BRACE")
        diag = result["diagnostics"][0]
        self.assertEqual(diag["category"], "UNMATCHED_BRACE")
        self.assertEqual(diag["line"], 1)

    def test_extra_closing_brace(self):
        source = (
            "public class Main {\n"
            "    int a = 1;\n"
            "}}\n"
        )
        result = self.analyzer.analyze(source)

        self.assertEqual(result["classification"]["label"], "UNMATCHED_BRACE")
        diag = result["diagnostics"][0]
        self.assertEqual(diag["category"], "UNMATCHED_BRACE")
        self.assertEqual(diag["line"], 3)

    def test_unmatched_opening_parenthesis(self):
        source = (
            "public class Main {\n"
            "    public static void main(String[] args) {\n"
            "        if (x > 5 {\n"
            "            return;\n"
            "        }\n"
            "    }\n"
            "}\n"
        )
        result = self.analyzer.analyze(source)

        self.assertEqual(result["classification"]["label"], "UNMATCHED_PARANTHESES")
        diag = result["diagnostics"][0]
        self.assertEqual(diag["category"], "UNMATCHED_PARANTHESES")
        self.assertEqual(diag["line"], 3)

    def test_unmatched_bracket(self):
        source = (
            "public class Main {\n"
            "    public static void main(String[] args) {\n"
            "        int[] arr = new int[10;\n"
            "    }\n"
            "}\n"
        )
        result = self.analyzer.analyze(source)

        self.assertIn("UNMATCHED", result["classification"]["label"])
        diags = [d for d in result["diagnostics"] if d["category"] == "UNMATCHED_BRACKET"]
        self.assertGreaterEqual(len(diags), 1)
        self.assertEqual(diags[0]["line"], 3)

    def test_invalid_conditional_missing_parentheses(self):
        source = (
            "public class Main {\n"
            "    public static void main(String[] args) {\n"
            "        if x > 5 {\n"
            "            return;\n"
            "        }\n"
            "    }\n"
            "}\n"
        )
        result = self.analyzer.analyze(source)

        self.assertEqual(result["classification"]["label"], "INVALID_CONDITIONAL")
        diag = result["diagnostics"][0]
        self.assertEqual(diag["category"], "INVALID_CONDITIONAL")
        self.assertEqual(diag["line"], 3)
        self.assertIn("condition", diag["explanation"].lower())

    def test_invalid_loop_missing_parentheses(self):
        source = (
            "public class Main {\n"
            "    public static void main(String[] args) {\n"
            "        while count > 0 {\n"
            "            count--;\n"
            "        }\n"
            "    }\n"
            "}\n"
        )
        result = self.analyzer.analyze(source)

        self.assertEqual(result["classification"]["label"], "INVALID_LOOP")
        diag = result["diagnostics"][0]
        self.assertEqual(diag["category"], "INVALID_LOOP")
        self.assertEqual(diag["line"], 3)

    def test_malformed_class_declaration_missing_name(self):
        source = "public class {\n    int a = 1;\n}\n"
        result = self.analyzer.analyze(source)

        self.assertEqual(result["classification"]["label"], "INVALID_CLASS_DECL")
        diag = result["diagnostics"][0]
        self.assertEqual(diag["category"], "INVALID_CLASS_DECL")
        self.assertEqual(diag["line"], 1)

    def test_invalid_assignment_to_literal(self):
        source = (
            "public class Main {\n"
            "    public static void main(String[] args) {\n"
            "        100 = total;\n"
            "    }\n"
            "}\n"
        )
        result = self.analyzer.analyze(source)

        self.assertEqual(result["classification"]["label"], "INVALID_ASSIGNMENT")
        diag = result["diagnostics"][0]
        self.assertEqual(diag["category"], "INVALID_ASSIGNMENT")
        self.assertEqual(diag["line"], 3)

    def test_unexpected_token_stray_hash(self):
        source = (
            "#include <stdio.h>\n"
            "public class Main {}\n"
        )
        result = self.analyzer.analyze(source)

        self.assertEqual(result["classification"]["label"], "EXTRA_TOKENS")
        diag = result["diagnostics"][0]
        self.assertEqual(diag["category"], "EXTRA_TOKENS")
        self.assertEqual(diag["line"], 1)

    def test_unclosed_string_literal(self):
        source = (
            "public class Main {\n"
            "    String msg = \"hello;\n"
            "}\n"
        )
        result = self.analyzer.analyze(source)

        self.assertEqual(result["classification"]["label"], "UNTERMINATED_STRING")
        diag = result["diagnostics"][0]
        self.assertEqual(diag["category"], "UNTERMINATED_STRING")
        self.assertEqual(diag["line"], 2)

    def test_unclosed_block_comment(self):
        source = (
            "/* This comment is never closed\n"
            "public class Main {}\n"
        )
        result = self.analyzer.analyze(source)

        self.assertEqual(result["classification"]["label"], "UNTERMINATED_STRING")
        diag = result["diagnostics"][0]
        self.assertEqual(diag["category"], "UNTERMINATED_STRING")
        self.assertEqual(diag["line"], 1)

    def test_empty_input_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.analyzer.analyze("")

    def test_whitespace_input_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.analyzer.analyze("   \n\t  \n")


if __name__ == "__main__":
    unittest.main()
