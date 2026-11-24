"""
Test Suite: Programming Language Detection (Phase 3)
Tests automatic language detection across Python, C++, and Java with confidence scoring,
ambiguity handling, and user overrides.
"""

import pytest
from src.language_detector import LanguageDetector, LanguageDetectionResult


@pytest.fixture
def detector():
    return LanguageDetector()


# ==============================================================================
# Python Detection Tests
# ==============================================================================

def test_detect_python_function(detector):
    code = (
        "def fibonacci(n):\n"
        "    if n <= 1:\n"
        "        return n\n"
        "    return fibonacci(n - 1) + fibonacci(n - 2)\n"
    )
    res = detector.detect_language(code)
    assert res.language == "python"
    assert res.confidence >= 0.70
    assert res.confidence_level in ("high", "medium")
    assert res.ambiguous is False
    assert any("def" in s for s in res.signals)


def test_detect_python_class_with_dunder(detector):
    code = (
        "class DataProcessor:\n"
        "    def __init__(self, data):\n"
        "        self.data = [x for x in data if x is not None]\n"
        "    def get_summary(self):\n"
        "        return len(self.data)\n"
    )
    res = detector.detect_language(code)
    assert res.language == "python"
    assert res.confidence_level == "high"


def test_detect_python_error_snippet(detector):
    # Python code with syntax error (missing colon)
    code = (
        "def calculate_tax(income)\n"
        "    total = income * 0.2\n"
        "    print(f'Tax: {total}')\n"
    )
    res = detector.detect_language(code)
    assert res.language == "python"
    assert res.ambiguous is False


# ==============================================================================
# C++ Detection Tests
# ==============================================================================

def test_detect_cpp_standard_program(detector):
    code = (
        "#include <iostream>\n"
        "#include <vector>\n"
        "using namespace std;\n"
        "\n"
        "int main() {\n"
        "    cout << \"Hello World!\" << endl;\n"
        "    return 0;\n"
        "}\n"
    )
    res = detector.detect_language(code)
    assert res.language == "cpp"
    assert res.confidence_level == "high"
    assert res.confidence >= 0.85
    assert res.ambiguous is False


def test_detect_cpp_template_and_pointers(detector):
    code = (
        "template<typename T>\n"
        "class Node {\n"
        "public:\n"
        "    T val;\n"
        "    Node* next;\n"
        "    Node(T v) : val(v), next(nullptr) {}\n"
        "};\n"
    )
    res = detector.detect_language(code)
    assert res.language == "cpp"
    assert res.ambiguous is False
    assert any("template" in s or "nullptr" in s for s in res.signals)


def test_detect_cpp_syntax_error_snippet(detector):
    # C++ code with syntax error (missing semicolon)
    code = (
        "#include <iostream>\n"
        "int main() {\n"
        "    std::cout << \"Missing semicolon\"\n"
        "    return 0;\n"
        "}\n"
    )
    res = detector.detect_language(code)
    assert res.language == "cpp"
    assert res.confidence >= 0.70


# ==============================================================================
# Java Detection Tests
# ==============================================================================

def test_detect_java_standard_class(detector):
    code = (
        "package com.example.tutor;\n"
        "import java.util.Scanner;\n"
        "\n"
        "public class Calculator {\n"
        "    public static void main(String[] args) {\n"
        "        System.out.println(\"Ready\");\n"
        "    }\n"
        "}\n"
    )
    res = detector.detect_language(code)
    assert res.language == "java"
    assert res.confidence_level == "high"
    assert res.confidence >= 0.85
    assert res.ambiguous is False


def test_detect_java_interface_and_methods(detector):
    code = (
        "public class Worker implements Runnable {\n"
        "    private String name;\n"
        "    public Worker(String name) {\n"
        "        this.name = name;\n"
        "    }\n"
        "    @Override\n"
        "    public void run() {\n"
        "        System.out.println(this.name + \" working\");\n"
        "    }\n"
        "}\n"
    )
    res = detector.detect_language(code)
    assert res.language == "java"
    assert res.confidence_level == "high"
    assert any("implements" in s or "@Override" in s for s in res.signals)


# ==============================================================================
# Ambiguous & Short Snippet Tests
# ==============================================================================

def test_detect_short_ambiguous_snippet(detector):
    code = "x = 42"
    res = detector.detect_language(code)
    assert res.ambiguous is True
    assert res.confidence_level == "ambiguous"
    assert res.confidence <= 0.50


def test_detect_empty_code(detector):
    res = detector.detect_language("   \n\t  ")
    assert res.ambiguous is True
    assert res.confidence == 0.0


# ==============================================================================
# User Override Tests
# ==============================================================================

def test_user_override_applied(detector):
    # Python code, but user explicitly wants it treated as cpp
    code = "def foo(): return 1"
    res = detector.detect_language(code, user_override="cpp")
    assert res.language == "cpp"
    assert res.user_override == "cpp"
    assert res.confidence == 1.0
    assert "User override applied" in res.reason


def test_user_override_case_insensitive(detector):
    code = "public class App {}"
    res = detector.detect_language(code, user_override="JAVA")
    assert res.language == "java"
    assert res.user_override == "java"
