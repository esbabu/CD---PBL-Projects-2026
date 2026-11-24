"""
Test Suite: Complex Program Evaluation Dataset (Phase 6)
Evaluates AI Error Tutor across Level 1 (Basic), Level 2 (Intermediate), and Level 3 (Complex)
programs in Python, C++, and Java.
"""

import pytest
from src.pipeline import AIErrorTutor
from src.language_detector import LanguageDetector
from tests.fixtures.dataset import (
    COMPLEX_EVALUATION_DATASET,
    get_benchmarks_by_language,
    get_benchmarks_by_complexity
)


@pytest.fixture
def tutor():
    return AIErrorTutor(use_ai=False)


@pytest.fixture
def detector():
    return LanguageDetector()


# ==============================================================================
# Automatic Language Detection on Complex Programs
# ==============================================================================

@pytest.mark.parametrize("benchmark", COMPLEX_EVALUATION_DATASET)
def test_language_detection_on_complex_dataset(detector, benchmark):
    """Verifies that all benchmarks across all 3 levels are correctly identified."""
    res = detector.detect_language(benchmark.code)
    assert res.language == benchmark.language, (
        f"Expected {benchmark.language} for benchmark {benchmark.id} ({benchmark.title}), "
        f"but got {res.language} with scores {res.scores}"
    )


# ==============================================================================
# Python Complex Program Tests (Levels 1, 2, 3)
# ==============================================================================

def test_python_level1_name_error(tutor):
    bench = next(b for b in COMPLEX_EVALUATION_DATASET if b.id == "PY_L1_01")
    res = tutor.analyze_code(bench.code, language="python")
    assert res.success is False
    assert res.error_type == "NameError"
    assert res.line_number == 3
    assert res.language == "python"


def test_python_level2_recursive_tree(tutor):
    bench = next(b for b in COMPLEX_EVALUATION_DATASET if b.id == "PY_L2_01")
    res = tutor.analyze_code(bench.code, language="python")
    assert res.success is False
    assert res.error_type == "NameError"
    assert res.language == "python"


def test_python_level3_dijkstra_attribute_error(tutor):
    bench = next(b for b in COMPLEX_EVALUATION_DATASET if b.id == "PY_L3_01")
    res = tutor.analyze_code(bench.code, language="python")
    assert res.success is False
    assert res.error_type == "AttributeError"
    assert "distane" in res.raw_error
    assert res.language == "python"


def test_python_level3_lru_cache_attribute_error(tutor):
    bench = next(b for b in COMPLEX_EVALUATION_DATASET if b.id == "PY_L3_02")
    res = tutor.analyze_code(bench.code, language="python")
    assert res.success is False
    assert res.error_type == "AttributeError"
    assert "nxt" in res.raw_error


# ==============================================================================
# C++ Complex Program Tests (Levels 1, 2, 3)
# ==============================================================================

def test_cpp_level1_missing_semicolon(tutor):
    bench = next(b for b in COMPLEX_EVALUATION_DATASET if b.id == "CPP_L1_01")
    res = tutor.analyze_code(bench.code, language="cpp")
    assert res.success is False
    assert res.error_type == "MissingSemicolon"
    assert res.language == "cpp"


def test_cpp_level2_inverted_stream(tutor):
    bench = next(b for b in COMPLEX_EVALUATION_DATASET if b.id == "CPP_L2_01")
    res = tutor.analyze_code(bench.code, language="cpp")
    assert res.success is False
    assert res.error_type in ("StreamOperatorError", "CompilationError", "SyntaxError")
    assert res.language == "cpp"


def test_cpp_level3_templated_bst(tutor):
    bench = next(b for b in COMPLEX_EVALUATION_DATASET if b.id == "CPP_L3_01")
    res = tutor.analyze_code(bench.code, language="cpp")
    assert res.success is False
    assert res.error_type in ("MissingSemicolon", "SyntaxError", "CompilationError")
    assert res.language == "cpp"


def test_cpp_level3_matrix_unmatched_brace(tutor):
    bench = next(b for b in COMPLEX_EVALUATION_DATASET if b.id == "CPP_L3_02")
    res = tutor.analyze_code(bench.code, language="cpp")
    assert res.success is False
    assert res.error_type in ("UnmatchedBrace", "SyntaxError", "CompilationError")
    assert res.language == "cpp"


# ==============================================================================
# Java Complex Program Tests (Levels 1, 2, 3)
# ==============================================================================

def test_java_level1_typo(tutor):
    bench = next(b for b in COMPLEX_EVALUATION_DATASET if b.id == "JAVA_L1_01")
    res = tutor.analyze_code(bench.code, language="java")
    assert res.success is False
    assert res.error_type in ("TypoError", "CannotFindSymbol", "SyntaxError")
    assert res.language == "java"


def test_java_level2_missing_import(tutor):
    bench = next(b for b in COMPLEX_EVALUATION_DATASET if b.id == "JAVA_L2_01")
    res = tutor.analyze_code(bench.code, language="java")
    assert res.success is False
    assert res.error_type in ("MissingImport", "CannotFindSymbol", "SyntaxError")
    assert res.language == "java"


def test_java_level2_missing_class(tutor):
    bench = next(b for b in COMPLEX_EVALUATION_DATASET if b.id == "JAVA_L2_02")
    res = tutor.analyze_code(bench.code, language="java")
    assert res.success is False
    assert res.error_type == "MissingClassDeclaration"
    assert res.language == "java"


def test_java_level3_hierarchy_missing_return(tutor):
    bench = next(b for b in COMPLEX_EVALUATION_DATASET if b.id == "JAVA_L3_01")
    res = tutor.analyze_code(bench.code, language="java")
    assert res.success is False
    assert res.error_type in ("MissingReturnStatement", "SyntaxError")
    assert res.language == "java"


def test_java_level3_generic_task_scheduler_unclosed_brace(tutor):
    bench = next(b for b in COMPLEX_EVALUATION_DATASET if b.id == "JAVA_L3_02")
    res = tutor.analyze_code(bench.code, language="java")
    assert res.success is False
    assert res.error_type in ("UnclosedBlock", "SyntaxError")
    assert res.language == "java"
