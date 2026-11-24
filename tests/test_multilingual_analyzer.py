"""
Test Suite: Multilingual Analyzers (C++ and Java) (Phase 4 & 5)
Tests compile-based and heuristic error diagnostics, security enforcement,
and fallback execution.
"""

import pytest
from src.cpp_analyzer import CppAnalyzer
from src.java_analyzer import JavaAnalyzer


# ==============================================================================
# C++ Analyzer Tests
# ==============================================================================

def test_cpp_compiler_clean_code():
    analyzer = CppAnalyzer()
    code = (
        "#include <iostream>\n"
        "int main() {\n"
        "    std::cout << \"Hello!\" << std::endl;\n"
        "    return 0;\n"
        "}\n"
    )
    res = analyzer.analyze(code)
    assert res["language"] == "cpp"
    assert res["status"] == "SUCCESS"
    assert res["error_type"] is None


def test_cpp_compiler_missing_semicolon():
    analyzer = CppAnalyzer()
    code = (
        "#include <iostream>\n"
        "int main() {\n"
        "    int x = 10\n"
        "    std::cout << x << std::endl;\n"
        "    return 0;\n"
        "}\n"
    )
    res = analyzer.analyze(code)
    assert res["language"] == "cpp"
    assert res["status"] == "ERROR"
    assert res["error_type"] == "MissingSemicolon"
    assert res["line_number"] in (3, 4)
    assert "semicolon" in res["explanation"].lower()


def test_cpp_compiler_undeclared_identifier():
    analyzer = CppAnalyzer()
    code = (
        "#include <iostream>\n"
        "int main() {\n"
        "    std::cout << secret_variable << std::endl;\n"
        "    return 0;\n"
        "}\n"
    )
    res = analyzer.analyze(code)
    assert res["language"] == "cpp"
    assert res["status"] == "ERROR"
    assert res["error_type"] == "UndeclaredIdentifier"
    assert "secret_variable" in res["error_message"]


def test_cpp_security_block_system_call():
    analyzer = CppAnalyzer()
    code = (
        "#include <cstdlib>\n"
        "int main() {\n"
        "    system(\"rm -rf /\");\n"
        "    return 0;\n"
        "}\n"
    )
    res = analyzer.analyze(code)
    assert res["status"] == "BLOCKED"
    assert res["error_type"] == "SecurityViolation"
    assert "system()" in res["error_message"]


def test_cpp_heuristic_fallback_inverted_stream():
    # Force heuristic mode by passing compiler_path=None
    analyzer = CppAnalyzer(compiler_path=None)
    code = (
        "#include <iostream>\n"
        "using namespace std;\n"
        "int main() {\n"
        "    cout >> \"Wrong operator\";\n"
        "    return 0;\n"
        "}\n"
    )
    res = analyzer.analyze(code)
    assert res["status"] == "ERROR"
    assert res["error_type"] == "StreamOperatorError"
    assert "cout" in res["explanation"] and "<<" in res["explanation"]


def test_cpp_heuristic_fallback_unmatched_brace():
    analyzer = CppAnalyzer(compiler_path=None)
    code = (
        "#include <iostream>\n"
        "int main() {\n"
        "    int a = 1;\n"
    )
    res = analyzer.analyze(code)
    assert res["status"] == "ERROR"
    assert res["error_type"] == "UnmatchedBrace"


# ==============================================================================
# Java Analyzer Tests
# ==============================================================================

def test_java_clean_code():
    analyzer = JavaAnalyzer()
    code = (
        "public class HelloWorld {\n"
        "    public static void main(String[] args) {\n"
        "        System.out.println(\"Hello World\");\n"
        "    }\n"
        "}\n"
    )
    res = analyzer.analyze(code)
    assert res["language"] == "java"
    assert res["status"] == "SUCCESS"
    assert res["error_type"] is None


def test_java_missing_class_declaration():
    analyzer = JavaAnalyzer()
    code = (
        "public static void main(String[] args) {\n"
        "    System.out.println(\"No class\");\n"
        "}\n"
    )
    res = analyzer.analyze(code)
    assert res["status"] == "ERROR"
    assert res["error_type"] == "MissingClassDeclaration"
    assert "class" in res["explanation"].lower()


def test_java_system_out_typo():
    analyzer = JavaAnalyzer()
    code = (
        "public class Demo {\n"
        "    public static void main(String[] args) {\n"
        "        System.out.printl(\"Typo here\");\n"
        "    }\n"
        "}\n"
    )
    res = analyzer.analyze(code)
    assert res["status"] == "ERROR"
    assert res["error_type"] == "TypoError"
    assert "println" in res["explanation"]


def test_java_missing_semicolon():
    analyzer = JavaAnalyzer()
    code = (
        "public class Calc {\n"
        "    public static void main(String[] args) {\n"
        "        int total = 100\n"
        "        System.out.println(total);\n"
        "    }\n"
        "}\n"
    )
    res = analyzer.analyze(code)
    assert res["status"] == "ERROR"
    assert res["error_type"] == "MissingSemicolon"
    assert res["line_number"] == 3


def test_java_missing_scanner_import():
    analyzer = JavaAnalyzer()
    code = (
        "public class InputApp {\n"
        "    public static void main(String[] args) {\n"
        "        Scanner sc = new Scanner(System.in);\n"
        "    }\n"
        "}\n"
    )
    res = analyzer.analyze(code)
    assert res["status"] == "ERROR"
    assert res["error_type"] == "MissingImport"
    assert "java.util.Scanner" in res["explanation"]


def test_java_security_block_runtime_exec():
    analyzer = JavaAnalyzer()
    code = (
        "public class Exploit {\n"
        "    public static void main(String[] args) {\n"
        "        Runtime.getRuntime().exec(\"calc.exe\");\n"
        "    }\n"
        "}\n"
    )
    res = analyzer.analyze(code)
    assert res["status"] == "BLOCKED"
    assert res["error_type"] == "SecurityViolation"
    assert "Runtime" in res["error_message"] or "Runtime.exec" in res["error_message"] or "prohibited" in res["error_message"].lower()
