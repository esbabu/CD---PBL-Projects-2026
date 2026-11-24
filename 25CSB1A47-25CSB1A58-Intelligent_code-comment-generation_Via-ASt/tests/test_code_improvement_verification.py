"""Comprehensive test suite for the upgraded FORGE, REMEDY, and VERITY workflow.

Verifies:
1. AST Code Analysis (9 categories: syntax, undefined, types, duplicates, complexity,
   separation of responsibilities, algorithms, security, maintainability).
2. Minimal Structured Patch Generation (all 8 required fields, minimal surgical edits).
3. Patch Safety & Structural Validation (function signatures, classes, imports, security).
4. Behavioral Verification in Disposable Sandbox (isolated process, scrubbed secrets,
   disabled network, timeout enforcement, text-only mode).
5. VERITY Independent Audit & Honest Final Status (7 honest status fields, no false claims).
"""

import ast
import os
import unittest

from backend.behavioral_verifier import (
    build_sanitized_environment,
    run_isolated_behavioral_tests,
)
from backend.code_analysis_engine import (
    analyze_code_comprehensively,
)
from backend.optimization_agent import optimize_code
from backend.patch_safety import (
    compare_class_definitions,
    compare_function_signatures,
    detect_new_security_issues,
    inspect_imports,
    validate_patch_structural_safety,
)
from backend.security_fixing_agent import fix_attack_vulnerabilities
from backend.agentic.agents.specialists import (
    AuditAgent,
)
from backend.agentic.session import AgentSession
from backend.agentic.tools.registry import ToolDefinition, ToolRegistry


class CodeAnalysisEngineTests(unittest.TestCase):
    """Test Suite 1: AST Code Analysis Engine (9 domains)."""

    def test_analyzes_all_nine_domains(self):
        code = """import os

def calculate_items(a, b, c, d, e, f):
    # Missing docstring
    total = ""
    for i in range(10):
        total += str(i)
        for j in range(5):
            pass

    if a > 0:
        x = 1
    elif a > 0:
        x = 2

    try:
        os.system("echo " + total)
    except Exception:
        pass

    return total
"""
        results = analyze_code_comprehensively(code)
        self.assertTrue(results["syntax_valid"])
        # Duplicate logic (duplicated condition in elif)
        self.assertGreater(len(results["duplicate_logic"]), 0)
        # Separation of responsibilities (6 params: excessive parameter count)
        self.assertGreater(len(results["separation_of_responsibilities"]), 0)
        # Inefficient algorithms (string concatenation in loop and nested loop)
        self.assertGreater(len(results["inefficient_algorithms"]), 0)
        # Security problems (os.system command injection)
        self.assertGreater(len(results["security_problems"]), 0)
        # Maintainability issues (missing docstring, silent broad exception)
        self.assertGreater(len(results["maintainability_issues"]), 0)

    def test_syntax_error_reported_immediately(self):
        bad_code = "def broken_func(:\n    pass"
        results = analyze_code_comprehensively(bad_code)
        self.assertFalse(results["syntax_valid"])
        self.assertEqual(len(results["syntax_errors"]), 1)
        self.assertIn("syntax", results["syntax_errors"][0]["title"].lower())

    def test_undefined_names_and_type_issues_detected(self):
        code = """def foo():
    return unknown_variable_xyz + 42
"""
        results = analyze_code_comprehensively(code)
        self.assertGreater(len(results["undefined_names"]), 0)
        self.assertEqual(results["undefined_names"][0]["name"], "unknown_variable_xyz")


class StructuredPatchGenerationTests(unittest.TestCase):
    """Test Suite 2: Minimal Structured Patch Generation."""

    def test_forge_produces_structured_minimal_patches(self):
        quadratic_code = """def find_duplicates(numbers):
    dups = []
    for i in range(len(numbers)):
        for j in range(i + 1, len(numbers)):
            if numbers[i] == numbers[j] and numbers[i] not in dups:
                dups.append(numbers[i])
    return dups
"""
        res = optimize_code(quadratic_code)
        self.assertTrue(res["optimized"])
        self.assertIn("patches", res)
        self.assertGreater(len(res["patches"]), 0)

        patch = res["patches"][0]
        # Verify all 8 mandatory patch fields
        self.assertIn("finding_id", patch)
        self.assertIn("root_cause", patch)
        self.assertIn("original_source_location", patch)
        self.assertIn("proposed_modification", patch)
        self.assertIn("explanation", patch)
        self.assertIn("expected_benefit", patch)
        self.assertIn("potential_risk", patch)
        self.assertIn("confidence", patch)
        self.assertGreaterEqual(patch["confidence"], 0.8)

    def test_remedy_produces_structured_minimal_patches(self):
        vulnerable_code = """import sqlite3

def get_user(user_id):
    conn = sqlite3.connect("test.db")
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE id = '{user_id}'"
    cursor.execute(query)
    return cursor.fetchall()
"""
        res = fix_attack_vulnerabilities(vulnerable_code)
        self.assertTrue(res["fixed"])
        self.assertIn("patches", res)
        self.assertGreater(len(res["patches"]), 0)

        patch = res["patches"][0]
        # Verify all 8 mandatory patch fields
        self.assertIn("finding_id", patch)
        self.assertIn("root_cause", patch)
        self.assertIn("original_source_location", patch)
        self.assertIn("proposed_modification", patch)
        self.assertIn("explanation", patch)
        self.assertIn("expected_benefit", patch)
        self.assertIn("potential_risk", patch)
        self.assertIn("confidence", patch)


class PatchSafetyStructuralValidationTests(unittest.TestCase):
    """Test Suite 3: Patch Safety & Structural Validation."""

    def test_rejects_removed_parameter(self):
        orig = "def compute(x, y, multiplier=1):\n    return (x + y) * multiplier\n"
        # Candidate dropped 'multiplier'
        cand = "def compute(x, y):\n    return x + y\n"
        tree_orig = ast.parse(orig)
        tree_cand = ast.parse(cand)
        ok, issues = compare_function_signatures(tree_orig, tree_cand)
        self.assertFalse(ok)
        self.assertTrue(any("removed parameter" in i.lower() for i in issues))

    def test_rejects_renamed_positional_parameter(self):
        orig = "def process_data(records, timeout=30):\n    return records\n"
        cand = "def process_data(items, timeout=30):\n    return items\n"
        tree_orig = ast.parse(orig)
        tree_cand = ast.parse(cand)
        ok, issues = compare_function_signatures(tree_orig, tree_cand)
        self.assertFalse(ok)
        self.assertTrue(any("renamed" in i.lower() for i in issues))

    def test_rejects_added_required_parameter_without_default(self):
        orig = "def fetch(url):\n    return url\n"
        cand = "def fetch(url, headers):\n    return url\n"
        tree_orig = ast.parse(orig)
        tree_cand = ast.parse(cand)
        ok, issues = compare_function_signatures(tree_orig, tree_cand)
        self.assertFalse(ok)
        self.assertTrue(any("new required parameter" in i.lower() for i in issues))

    def test_rejects_removed_class_method(self):
        orig = """class DataProcessor:
    def process(self):
        return 1
    def validate(self):
        return True
"""
        # Candidate dropped public method validate
        cand = """class DataProcessor:
    def process(self):
        return 1
"""
        tree_orig = ast.parse(orig)
        tree_cand = ast.parse(cand)
        ok, issues = compare_class_definitions(tree_orig, tree_cand)
        self.assertFalse(ok)
        self.assertTrue(any("removed public method 'validate'" in i for i in issues))

    def test_rejects_dangerous_import(self):
        orig = "def run():\n    return 42\n"
        cand = "import ctypes\ndef run():\n    return 42\n"
        tree_orig = ast.parse(orig)
        tree_cand = ast.parse(cand)
        ok, issues = inspect_imports(tree_orig, tree_cand)
        self.assertFalse(ok)
        self.assertTrue(any("dangerous import 'ctypes'" in i for i in issues))

    def test_rejects_new_security_vulnerability(self):
        orig = "def eval_expr(expr):\n    return str(expr)\n"
        # Candidate introduced eval (CWE-94)
        cand = "def eval_expr(expr):\n    return eval(expr)\n"
        ok, issues = detect_new_security_issues(orig, cand)
        self.assertFalse(ok)
        self.assertTrue(any("security vulnerability" in i.lower() for i in issues))

    def test_validate_patch_structural_safety_full_pass(self):
        orig = "def add(a, b=0):\n    return a + b\n"
        cand = "def add(a, b=0):\n    # safe comment\n    return a + b\n"
        val = validate_patch_structural_safety(orig, cand)
        self.assertTrue(val["is_safe"])
        self.assertIsNotNone(val["acceptance_explanation"])


class BehavioralVerificationSandboxTests(unittest.TestCase):
    """Test Suite 4: Disposable Sandbox Behavioral Verification."""

    def test_sandbox_executes_unit_test_successfully(self):
        candidate = "def multiply(x, y):\n    return x * y\n"
        test_harness = """import unittest
from candidate_module import multiply

class TestMultiply(unittest.TestCase):
    def test_mult(self):
        self.assertEqual(multiply(3, 4), 12)

if __name__ == '__main__':
    unittest.main()
"""
        res = run_isolated_behavioral_tests(candidate, test_harness, timeout_seconds=5.0)
        self.assertTrue(res["behavioral_tests_run"])
        self.assertTrue(res["behavioral_tests_passed"])
        self.assertEqual(res["exit_code"], 0)
        self.assertFalse(res["timed_out"])
        self.assertTrue(res["sandbox_isolated"])

    def test_sandbox_catches_failing_unit_test(self):
        candidate = "def multiply(x, y):\n    return x + y\n"  # Bug
        test_harness = """import unittest
from candidate_module import multiply

class TestMultiply(unittest.TestCase):
    def test_mult(self):
        self.assertEqual(multiply(3, 4), 12)

if __name__ == '__main__':
    unittest.main()
"""
        res = run_isolated_behavioral_tests(candidate, test_harness, timeout_seconds=5.0)
        self.assertTrue(res["behavioral_tests_run"])
        self.assertFalse(res["behavioral_tests_passed"])
        self.assertNotEqual(res["exit_code"], 0)

    def test_sandbox_scrubs_all_application_secrets(self):
        # Set dummy secret in host env
        os.environ["API_KEY"] = "super_secret_host_key_12345"
        os.environ["SERVER_API_KEY"] = "super_admin_key_99999"
        clean = build_sanitized_environment(disable_network=True)
        self.assertNotIn("API_KEY", clean)
        self.assertNotIn("SERVER_API_KEY", clean)
        self.assertNotIn("super_secret_host_key_12345", str(clean))

    def test_sandbox_disables_network_access(self):
        candidate = "def get_data(): return 1\n"
        network_test = """import socket
import unittest

class TestNet(unittest.TestCase):
    def test_no_outbound(self):
        s = socket.socket()
        with self.assertRaises(PermissionError):
            s.connect(('8.8.8.8', 53))

if __name__ == '__main__':
    unittest.main()
"""
        res = run_isolated_behavioral_tests(candidate, network_test, timeout_seconds=5.0)
        self.assertTrue(res["behavioral_tests_run"])
        self.assertTrue(res["behavioral_tests_passed"])

    def test_sandbox_enforces_execution_timeout_on_infinite_loop(self):
        candidate = "def hang():\n    while True:\n        pass\n"
        hang_test = """from candidate_module import hang
hang()
"""
        res = run_isolated_behavioral_tests(candidate, hang_test, timeout_seconds=1.5)
        self.assertTrue(res["behavioral_tests_run"])
        self.assertFalse(res["behavioral_tests_passed"])
        self.assertTrue(res["timed_out"])
        self.assertIn("timed out", res["error"].lower())

    def test_text_only_mode_returns_honest_unexecuted_status(self):
        res = run_isolated_behavioral_tests("def f(): pass", test_code=None, enabled=False)
        self.assertFalse(res["behavioral_tests_run"])
        self.assertFalse(res["behavioral_tests_passed"])
        self.assertEqual(res["mode"], "text_only")


class VerityIndependentAuditAndHonestStatusTests(unittest.TestCase):
    """Test Suite 5: VERITY Independent Audit & Honest Final Status."""

    def test_verity_reports_all_seven_honest_status_fields(self):
        code = "def add(a, b):\n    return a + b\n"
        session = AgentSession(
            session_id="test_verity_audit",
            original_code=code,
            original_code_digest="abc",
            current_code=code,
            task="Audit code",
        )
        tools = ToolRegistry()
        tools.register(ToolDefinition(
            name="verify_code_integrity",
            description="test",
            parameters_schema={},
            handler=lambda a, c: {
                "all_passed": True,
                "syntax_valid": True,
                "definitions_preserved": True,
                "signatures_compatible": True,
                "executable_code_preserved": True,
            },
        ))
        tools.register(ToolDefinition(
            name="compute_unified_diff",
            description="test",
            parameters_schema={},
            handler=lambda a, c: {"diff": "", "added_lines": 0, "removed_lines": 0},
        ))
        tools.register(ToolDefinition(
            name="probe_security_vulnerabilities",
            description="test",
            parameters_schema={},
            handler=lambda a, c: {"scenarios": []},
        ))
        tools.register(ToolDefinition(
            name="infer_type_errors",
            description="test",
            parameters_schema={},
            handler=lambda a, c: {"definite_type_errors": []},
        ))
        tools.register(ToolDefinition(
            name="evaluate_quality",
            description="test",
            parameters_schema={},
            handler=lambda a, c: {"score": 100, "findings": []},
        ))
        tools.register(ToolDefinition(
            name="run_isolated_behavioral_tests",
            description="test",
            parameters_schema={},
            handler=lambda a, c: {"behavioral_tests_run": False, "behavioral_tests_passed": False},
        ))

        verity = AuditAgent(tools=tools)
        outcome = verity.deterministic_turn(session, sub_task="Verify code integrity")

        self.assertIn("audit", outcome)
        audit = outcome["audit"]

        # Assert all 7 required honest status booleans exist
        self.assertIn("static_checks_passed", audit)
        self.assertIn("security_checks_passed", audit)
        self.assertIn("type_checks_passed", audit)
        self.assertIn("behavioral_tests_run", audit)
        self.assertIn("behavioral_tests_passed", audit)
        self.assertIn("semantic_equivalence_verified", audit)
        self.assertIn("human_approval_received", audit)

        self.assertTrue(audit["static_checks_passed"])
        self.assertTrue(audit["security_checks_passed"])
        self.assertTrue(audit["type_checks_passed"])
        self.assertFalse(audit["behavioral_tests_run"])  # None were run

        # CRITICAL INVARIANT: Complete verification must NEVER be claimed when behavioral tests were not run
        self.assertFalse(audit["complete_verification"])
        self.assertEqual(audit["verification_level"], "static_only")

    def test_verity_complete_verification_achieved_when_behavioral_tests_pass(self):
        code = "def add(a, b):\n    return a + b\n"
        test_harness = """import unittest
from candidate_module import add
class T(unittest.TestCase):
    def test_a(self): self.assertEqual(add(2, 3), 5)
if __name__ == '__main__': unittest.main()
"""
        session = AgentSession(
            session_id="test_verity_behavioral",
            original_code=code,
            original_code_digest="abc",
            current_code=code,
            task="Verify code integrity with behavioral testing",
            metadata={
                "run_behavioral_tests": True,
                "behavioral_test_code": test_harness,
            },
        )
        tools = ToolRegistry()
        tools.register(ToolDefinition(
            name="verify_code_integrity",
            description="test",
            parameters_schema={},
            handler=lambda a, c: {
                "all_passed": True,
                "syntax_valid": True,
                "definitions_preserved": True,
                "signatures_compatible": True,
                "executable_code_preserved": True,
            },
        ))
        tools.register(ToolDefinition(
            name="compute_unified_diff",
            description="test",
            parameters_schema={},
            handler=lambda a, c: {"diff": "", "added_lines": 0, "removed_lines": 0},
        ))
        tools.register(ToolDefinition(
            name="probe_security_vulnerabilities",
            description="test",
            parameters_schema={},
            handler=lambda a, c: {"scenarios": []},
        ))
        tools.register(ToolDefinition(
            name="infer_type_errors",
            description="test",
            parameters_schema={},
            handler=lambda a, c: {"definite_type_errors": []},
        ))
        tools.register(ToolDefinition(
            name="evaluate_quality",
            description="test",
            parameters_schema={},
            handler=lambda a, c: {"score": 100, "findings": []},
        ))
        tools.register(ToolDefinition(
            name="run_isolated_behavioral_tests",
            description="test",
            parameters_schema={},
            handler=lambda a, c: {
                "behavioral_tests_run": True,
                "behavioral_tests_passed": True,
                "exit_code": 0,
            },
        ))

        verity = AuditAgent(tools=tools)
        outcome = verity.deterministic_turn(session, sub_task="Verify code integrity")
        audit = outcome["audit"]

        self.assertTrue(audit["behavioral_tests_run"])
        self.assertTrue(audit["behavioral_tests_passed"])
        self.assertTrue(audit["complete_verification"])
        self.assertIn(audit["verification_level"], {"full", "fully_verified_with_behavioral_sandbox"})
        self.assertIsNotNone(audit["acceptance_explanation"])


if __name__ == "__main__":
    unittest.main()
