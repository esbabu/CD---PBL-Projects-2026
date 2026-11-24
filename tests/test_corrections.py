"""
Repeatable Correction Validation Test Suite
Tests candidate code generation and verification:
- Misspelled built-in / variable name
- Missing colon in function / statement
- Type error (string + int concatenation)
- Indexing error (out of bounds)
- Undefined variable whose intended value is ambiguous (honest refusal)
- Code that is already correct (preservation)
- Candidate that alters program behavior (oracle rejection)
"""

import pytest
from src.pipeline import AIErrorTutor
from src.correction_validator import CorrectionValidator, CorrectionStatus


@pytest.fixture
def tutor():
    return AIErrorTutor(use_ai=False)


@pytest.fixture
def validator():
    return CorrectionValidator()


# ───────────────────────────────────────────────────────────────────
# 1. Misspelled built-in or variable name (Expected to be repaired)
# ───────────────────────────────────────────────────────────────────

def test_correction_misspelled_builtin_print(tutor, validator):
    """Misspelled 'prnt' should be corrected to 'print' and verified against oracle."""
    code = "prnt('Hello from tutor')"
    res = tutor.analyze_code(code)

    assert not res.success
    assert res.error_type == "NameError"
    assert res.candidate_code is not None
    assert "print(" in res.candidate_code

    report = validator.validate_candidate(
        original_code=code,
        candidate_code=res.candidate_code,
        expected_error="NameError",
        expected_output="Hello from tutor\n",
        is_repair_expected=True
    )
    assert report.is_valid
    assert report.status == CorrectionStatus.VALIDATED_CORRECT
    assert report.syntax_valid
    assert report.behavior_verified is True


def test_correction_misspelled_variable_name(tutor, validator):
    """Misspelled variable 'totl' should be corrected to defined variable 'total'."""
    code = """total = 100
tax = 5
print(totl + tax)"""
    res = tutor.analyze_code(code)

    assert not res.success
    assert res.error_type == "NameError"
    assert res.candidate_code is not None

    report = validator.validate_candidate(
        original_code=code,
        candidate_code=res.candidate_code,
        expected_error="NameError",
        expected_output="105\n",
        is_repair_expected=True
    )
    assert report.is_valid
    assert report.status == CorrectionStatus.VALIDATED_CORRECT
    assert report.behavior_verified is True


# ───────────────────────────────────────────────────────────────────
# 2. Missing colon in Python syntax (Expected to be repaired)
# ───────────────────────────────────────────────────────────────────

def test_correction_missing_colon_def(tutor, validator):
    """Missing colon after def should be repaired and validated."""
    code = """def multiply(a, b)
    return a * b

print(multiply(3, 4))"""
    res = tutor.analyze_code(code)

    assert not res.success
    assert res.error_type == "SyntaxError"
    assert res.candidate_code is not None
    assert "def multiply(a, b):" in res.candidate_code

    report = validator.validate_candidate(
        original_code=code,
        candidate_code=res.candidate_code,
        expected_error="SyntaxError",
        expected_output="12\n",
        is_repair_expected=True
    )
    assert report.is_valid
    assert report.status == CorrectionStatus.VALIDATED_CORRECT
    assert report.behavior_verified is True


# ───────────────────────────────────────────────────────────────────
# 3. Type error: string + non-string concatenation (Expected to be repaired)
# ───────────────────────────────────────────────────────────────────

def test_correction_type_error_str_int(tutor, validator):
    """Concatenation of str and int should be repaired using str() conversion."""
    code = """age = 21
msg = "Age: " + age
print(msg)"""
    res = tutor.analyze_code(code)

    assert not res.success
    assert res.error_type == "TypeError"
    assert res.candidate_code is not None

    report = validator.validate_candidate(
        original_code=code,
        candidate_code=res.candidate_code,
        expected_error="TypeError",
        expected_output="Age: 21\n",
        is_repair_expected=True
    )
    assert report.is_valid
    assert report.status == CorrectionStatus.VALIDATED_CORRECT
    assert report.behavior_verified is True


# ───────────────────────────────────────────────────────────────────
# 4. Index error (Unrepairable without arbitrary assumption)
# ───────────────────────────────────────────────────────────────────

def test_correction_index_error_unrepaired(tutor, validator):
    """IndexError should not be silently patched with arbitrary values."""
    code = """items = [10, 20, 30]
print(items[99])"""
    res = tutor.analyze_code(code)

    assert not res.success
    assert res.error_type == "IndexError"
    # Should not claim a verified fix since changing index alters program semantics
    assert not res.validated


# ───────────────────────────────────────────────────────────────────
# 5. Ambiguous undefined variable (Should be rejected / refused)
# ───────────────────────────────────────────────────────────────────

def test_correction_ambiguous_undefined_variable(tutor, validator):
    """When variable is undefined and ambiguous, tutor must refuse to invent a value."""
    code = """print(totally_unknown_variable_xyz)"""
    res = tutor.analyze_code(code)

    assert not res.success
    assert res.error_type == "NameError"
    # The agent must not guess an arbitrary value
    assert not res.validated

    report = validator.validate_candidate(
        original_code=code,
        candidate_code=res.candidate_code or code,
        expected_error="NameError",
        is_repair_expected=False,
        is_ambiguous=True
    )
    assert report.status == CorrectionStatus.AMBIGUOUS_REJECTED
    assert "refused to invent arbitrary values" in report.reason.lower() or report.is_valid


# ───────────────────────────────────────────────────────────────────
# 6. Already correct code (Should remain unchanged and pass)
# ───────────────────────────────────────────────────────────────────

def test_correction_already_correct_code(tutor, validator):
    """Code that is already correct should succeed without altering source code."""
    code = """x = 10
y = 20
print(f"Sum: {x + y}")"""
    res = tutor.analyze_code(code)

    assert res.success
    assert res.error_type is None

    report = validator.validate_candidate(
        original_code=code,
        candidate_code=code,
        expected_output="Sum: 30\n",
        is_repair_expected=False
    )
    assert report.is_valid
    assert report.status == CorrectionStatus.NO_REPAIR_EXPECTED
    assert report.behavior_verified is True


# ───────────────────────────────────────────────────────────────────
# 7. Candidate that alters program behavior (Rejected by oracle)
# ───────────────────────────────────────────────────────────────────

def test_rejection_of_behavior_altering_candidate(validator):
    """A candidate that runs but alters expected behavior must be rejected by validator."""
    original = "print('expected result')"
    bad_candidate = "print('completely different output')"

    report = validator.validate_candidate(
        original_code=original,
        candidate_code=bad_candidate,
        expected_output="expected result\n",
        is_repair_expected=True
    )
    assert not report.is_valid
    assert report.status == CorrectionStatus.BEHAVIOR_FAILED
    assert report.behavior_verified is False
    assert "output mismatch" in report.reason.lower()


# ───────────────────────────────────────────────────────────────────
# 8. Multilingual Candidate Validation (C++ and Java)
# ───────────────────────────────────────────────────────────────────

def test_multilingual_cpp_correction_validation(validator):
    """Validates that a corrected C++ candidate compiles cleanly and passes oracle check."""
    orig_code = (
        "#include <iostream>\n"
        "int main() {\n"
        "    int a = 5\n"
        "    std::cout << \"Val: \" << a << std::endl;\n"
        "    return 0;\n"
        "}\n"
    )
    corrected_code = (
        "#include <iostream>\n"
        "int main() {\n"
        "    int a = 5;\n"
        "    std::cout << \"Val: \" << a << std::endl;\n"
        "    return 0;\n"
        "}\n"
    )
    rep = validator.validate_multilingual_candidate(
        language="cpp",
        original_code=orig_code,
        candidate_code=corrected_code,
        expected_output="Val: 5\n"
    )
    assert rep.is_valid is True
    assert rep.syntax_valid is True
    assert rep.security_passed is True
    assert rep.status in (CorrectionStatus.VALIDATED_CORRECT, CorrectionStatus.UNVERIFIED_SYNTAX_ONLY)


def test_multilingual_java_correction_validation(validator):
    """Validates that a corrected Java candidate passes syntax and security check."""
    orig_code = (
        "public class Demo {\n"
        "    public static void main(String[] args) {\n"
        "        System.out.printl(\"Done\");\n"
        "    }\n"
        "}\n"
    )
    corrected_code = (
        "public class Demo {\n"
        "    public static void main(String[] args) {\n"
        "        System.out.println(\"Done\");\n"
        "    }\n"
        "}\n"
    )
    rep = validator.validate_multilingual_candidate(
        language="java",
        original_code=orig_code,
        candidate_code=corrected_code
    )
    assert rep.is_valid is True
    assert rep.syntax_valid is True
    assert rep.security_passed is True
    assert rep.status == CorrectionStatus.UNVERIFIED_SYNTAX_ONLY
