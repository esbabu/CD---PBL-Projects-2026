"""Regression tests for Phase 8B: Diagnostic quality improvements."""

import os
import tempfile
import unittest

from backend.app.services.cpp_analysis import analyze_cpp_source
from cpp_parser import build_ast
from lexer import tokenize_file_clean


def tokenize_code(source: str):
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".cpp", encoding="utf-8", delete=False
    ) as f:
        f.write(source)
        path = f.name
    try:
        return tokenize_file_clean(path)
    finally:
        os.unlink(path)


class DiagnosticQualityTests(unittest.TestCase):
    # =========================================================================
    # Priority 1: Unknown tokens
    # =========================================================================
    def test_unknown_token_inside_declaration_reports_extra_tokens_with_location(self):
        source = "int main() {\n    int x = 5 @ 10;\n    return 0;\n}\n"
        tokens = tokenize_code(source)
        _, errors = build_ast(tokens)

        # Check parser error text and location
        self.assertTrue(any("EXTRA_TOKENS" in e and "line 2" in e and "column 15" in e for e in errors))

        # Check end-to-end analyzer response
        result = analyze_cpp_source(source)
        extra_token_diags = [d for d in result["diagnostics"] if d["category"] == "EXTRA_TOKENS"]
        self.assertEqual(len(extra_token_diags), 1)
        self.assertEqual(extra_token_diags[0]["origin"], "parser")
        self.assertEqual(extra_token_diags[0]["line"], 2)
        self.assertEqual(extra_token_diags[0]["column"], 15)

    def test_unknown_token_at_statement_level(self):
        source = "int main() {\n    @\n    return 0;\n}\n"
        result = analyze_cpp_source(source)
        extra_token_diags = [d for d in result["diagnostics"] if d["category"] == "EXTRA_TOKENS"]
        self.assertEqual(len(extra_token_diags), 1)
        self.assertEqual(extra_token_diags[0]["line"], 2)
        self.assertEqual(extra_token_diags[0]["column"], 5)

    # =========================================================================
    # Priority 2: Missing operands
    # =========================================================================
    def test_missing_operand_in_var_declaration(self):
        source = "int main() {\n    int total = 10 + ;\n    return 0;\n}\n"
        tokens = tokenize_code(source)
        _, errors = build_ast(tokens)

        self.assertTrue(any("INVALID_EXPRESSION" in e and "line 2" in e for e in errors))

        result = analyze_cpp_source(source)
        expr_diags = [d for d in result["diagnostics"] if d["category"] == "INVALID_EXPRESSION"]
        self.assertEqual(len(expr_diags), 1)
        self.assertEqual(expr_diags[0]["origin"], "parser")
        self.assertEqual(expr_diags[0]["line"], 2)
        self.assertEqual(expr_diags[0]["column"], 20)

    def test_missing_operand_in_expr_statement(self):
        source = "int main() {\n    int x = 10;\n    x = x * ;\n    return 0;\n}\n"
        result = analyze_cpp_source(source)
        expr_diags = [d for d in result["diagnostics"] if d["category"] == "INVALID_EXPRESSION"]
        self.assertEqual(len(expr_diags), 1)
        self.assertEqual(expr_diags[0]["origin"], "parser")
        self.assertEqual(expr_diags[0]["line"], 3)
        self.assertEqual(expr_diags[0]["column"], 11)

    def test_missing_operand_in_return_statement(self):
        source = "int main() {\n    return 10 - ;\n}\n"
        result = analyze_cpp_source(source)
        expr_diags = [d for d in result["diagnostics"] if d["category"] == "INVALID_EXPRESSION"]
        self.assertEqual(len(expr_diags), 1)
        self.assertEqual(expr_diags[0]["origin"], "parser")
        self.assertEqual(expr_diags[0]["line"], 2)
        self.assertEqual(expr_diags[0]["column"], 15)

    def test_valid_unary_and_postfix_operators_do_not_report_missing_operand(self):
        source = (
            "int main() {\n"
            "    int a = -5;\n"
            "    int b = +10;\n"
            "    int* p = &a;\n"
            "    int c = *p;\n"
            "    bool flag = !false;\n"
            "    int mask = ~0;\n"
            "    a++;\n"
            "    b--;\n"
            "    int result = ((a + b) * (c - 1));\n"
            "    return 0;\n"
            "}\n"
        )
        tokens = tokenize_code(source)
        _, errors = build_ast(tokens)
        self.assertEqual(errors, [])

        result = analyze_cpp_source(source)
        self.assertEqual(result["summary"]["parserDiagnosticCount"], 0)

    # =========================================================================
    # Priority 3: Delimiter locations
    # =========================================================================
    def test_unmatched_opening_brace_reports_meaningful_line(self):
        source = (
            "int main() {\n"
            "    if (true) {\n"
            "        int x = 1;\n"
            "    return 0;\n"
            "}\n"
        )
        result = analyze_cpp_source(source)
        parser_brace_diags = [
            d for d in result["diagnostics"]
            if d["category"] == "UNMATCHED_BRACE" and d["origin"] == "parser"
        ]
        self.assertEqual(len(parser_brace_diags), 1)
        # Should point to the unclosed block starting at line 1
        self.assertEqual(parser_brace_diags[0]["line"], 1)
        self.assertEqual(parser_brace_diags[0]["column"], 12)

    def test_unmatched_closing_brace_reports_exact_line_and_column(self):
        source = (
            "int main() {\n"
            "    int a = 1;\n"
            "    return 0;\n"
            "}}\n"
        )
        result = analyze_cpp_source(source)
        parser_brace_diags = [
            d for d in result["diagnostics"]
            if d["category"] == "UNMATCHED_BRACE" and d["origin"] == "parser"
        ]
        self.assertEqual(len(parser_brace_diags), 1)
        self.assertEqual(parser_brace_diags[0]["line"], 4)
        self.assertEqual(parser_brace_diags[0]["column"], 2)

    def test_unmatched_opening_parenthesis_reports_exact_line_and_column(self):
        source = (
            "int main() {\n"
            "    if (a > 0 {\n"
            "        return 1;\n"
            "    }\n"
            "    return 0;\n"
            "}\n"
        )
        result = analyze_cpp_source(source)
        paren_diags = [
            d for d in result["diagnostics"]
            if d["category"] == "UNMATCHED_PARANTHESES" and d["origin"] == "parser"
        ]
        self.assertEqual(len(paren_diags), 1)
        self.assertEqual(paren_diags[0]["line"], 2)
        self.assertEqual(paren_diags[0]["column"], 8)

    def test_valid_nested_blocks_parse_cleanly(self):
        source = (
            "int main() {\n"
            "    if (true) {\n"
            "        while (false) {\n"
            "            for (int i = 0; i < 10; i++) {\n"
            "                int y = i * 2;\n"
            "            }\n"
            "        }\n"
            "    }\n"
            "    return 0;\n"
            "}\n"
        )
        result = analyze_cpp_source(source)
        self.assertEqual(result["summary"]["diagnosticCount"], 0)

    # =========================================================================
    # Multi-error and standard library operator scenarios
    # =========================================================================
    def test_multiple_independent_syntax_errors_in_single_snippet(self):
        source = (
            "#include <iostream>\n\n"
            "int main() {\n"
            "    int a = 10\n"
            "    100 = a;\n"
            "    if (a > 0 {\n"
            "        return 1;\n"
            "    }\n"
            "    return 0;\n"
            "}\n"
        )
        result = analyze_cpp_source(source)
        diags = result["diagnostics"]
        categories = {d["category"] for d in diags}

        # Expect both MISSING_SEMICOLON and UNMATCHED_PARANTHESES
        self.assertIn("MISSING_SEMICOLON", categories)
        self.assertIn("UNMATCHED_PARANTHESES", categories)

        # Confirm non-null line locations
        located = [d for d in diags if d["line"] is not None]
        self.assertGreaterEqual(len(located), 2)
        lines = {d["line"] for d in located}
        self.assertIn(4, lines)  # missing semicolon at line 4

    def test_standard_library_streaming_operators_produce_no_false_positives(self):
        source = (
            "#include <iostream>\n"
            "#include <string>\n\n"
            "int main() {\n"
            "    std::string name;\n"
            "    std::cout << \"Enter: \" << std::endl;\n"
            "    std::cin >> name;\n"
            "    std::cout << \"Welcome, \" << name << \"!\" << std::endl;\n"
            "    return 0;\n"
            "}\n"
        )
        result = analyze_cpp_source(source)
        self.assertEqual(result["summary"]["diagnosticCount"], 0)

    def test_empty_source_raises_value_error(self):
        with self.assertRaises(ValueError):
            analyze_cpp_source("   \n\t  ")


if __name__ == "__main__":
    unittest.main()
