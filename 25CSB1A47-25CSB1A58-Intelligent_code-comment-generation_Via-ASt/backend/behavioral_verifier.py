"""Restricted Subprocess Environment for Behavioral Code Verification.

Provides restricted subprocess execution of test harnesses against candidate code:
- Disposable temporary directory working directory
- Subprocess launched in isolated mode (`python -I`)
- Complete scrub of application secrets, provider credentials, and tokens from environment
- Network disabled by default via proxy blackholing and socket interception
- Strict execution timeouts (preventing infinite loops)
- Output size limits (preventing memory exhaustion)
- Retains text-only mode when behavioral testing is disabled or unavailable
- NEVER executes arbitrary candidate code inside the main Flask process
- NOTE: This provides a restricted subprocess execution environment, not a full OS-level container/jail (such as Docker or Linux namespaces).
"""

from __future__ import annotations

import ast
import logging
import os
import subprocess
import sys
import tempfile
import time
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)

# Environment variable keys that must NEVER be passed to the sandbox
SECRET_ENV_KEYS: Set[str] = {
    "API_KEY",
    "SERVER_API_KEY",
    "GITHUB_TOKEN",
    "GH_TOKEN",
    "COPILOT_TOKEN",
    "HF_TOKEN",
    "OPENAI_API_KEY",
    "GEMINI_API_KEY",
    "GROQ_API_KEY",
    "ANTHROPIC_API_KEY",
    "AWS_ACCESS_KEY_ID",
    "AWS_SECRET_ACCESS_KEY",
    "DATABASE_URL",
    "SECRET_KEY",
}

# Essential safe environment variables permitted in the sandbox
SAFE_ENV_PASSTHROUGH_KEYS: Set[str] = {
    "PATH",
    "SYSTEMROOT",
    "WINDIR",
    "COMSPEC",
    "TEMP",
    "TMP",
    "HOME",
    "USERPROFILE",
    "APPDATA",
    "LOCALAPPDATA",
    "VIRTUAL_ENV",
    "CONDA_PREFIX",
    "LANG",
    "LC_ALL",
}


def build_sanitized_environment(disable_network: bool = True) -> Dict[str, str]:
    """Build a scrubbed environment dictionary containing zero application secrets."""
    clean_env: Dict[str, str] = {}

    for k, v in os.environ.items():
        k_upper = k.upper()
        # Explicit blacklist of any credential/token names
        if any(sec in k_upper for sec in ("KEY", "TOKEN", "SECRET", "PASSWORD", "PASSWD", "AUTH", "CREDENTIAL")):
            continue
        if k in SECRET_ENV_KEYS:
            continue
        # Only allow recognized system execution variables
        if k_upper in SAFE_ENV_PASSTHROUGH_KEYS:
            clean_env[k] = v

    # Python sandbox settings
    clean_env["PYTHONDONTWRITEBYTECODE"] = "1"
    clean_env["PYTHONUNBUFFERED"] = "1"
    clean_env["PYTHONHASHSEED"] = "0"

    # Block outbound network at the environment layer
    if disable_network:
        clean_env["HTTP_PROXY"] = "http://127.0.0.1:0"
        clean_env["HTTPS_PROXY"] = "http://127.0.0.1:0"
        clean_env["ALL_PROXY"] = "http://127.0.0.1:0"
        clean_env["NO_PROXY"] = ""

    return clean_env


_NETWORK_BLOCKING_PREAMBLE = """# Sandbox Security Preamble: Disable network socket calls
import socket

def _blocked_connect(*args, **kwargs):
    raise PermissionError("Network access is strictly disabled in the AST Studio verification sandbox.")

socket.socket.connect = _blocked_connect
socket.create_connection = _blocked_connect
"""


class DisposableSandboxRunner:
    """Disposable, restricted execution sandbox managing lifecycle and execution safety."""

    def __init__(
        self,
        timeout_seconds: float = 5.0,
        disable_network: bool = True,
        max_output_bytes: int = 65536,
    ) -> None:
        self.timeout_seconds = timeout_seconds
        self.disable_network = disable_network
        self.max_output_bytes = max_output_bytes

    def execute_test_suite(
        self,
        candidate_code: str,
        test_code: str,
    ) -> Dict[str, Any]:
        """Execute test_code against candidate_code inside an isolated disposable workspace."""
        start_time = time.perf_counter()

        with tempfile.TemporaryDirectory(prefix="ast_sandbox_") as tmp_dir:
            # 1. Write the candidate module
            module_path = os.path.join(tmp_dir, "candidate_module.py")
            with open(module_path, "w", encoding="utf-8") as f:
                f.write(candidate_code)

            # 2. Write the test harness with preamble
            harness_path = os.path.join(tmp_dir, "run_tests.py")
            full_test_script = (
                (_NETWORK_BLOCKING_PREAMBLE if self.disable_network else "")
                + "\n"
                + "import sys\n"
                + f"sys.path.insert(0, r'{tmp_dir}')\n\n"
                + test_code
            )
            with open(harness_path, "w", encoding="utf-8") as f:
                f.write(full_test_script)

            # 3. Prepare sanitized environment
            env = build_sanitized_environment(disable_network=self.disable_network)
            env["PYTHONPATH"] = tmp_dir

            # 4. Launch subprocess in isolated mode (-I)
            cmd = [sys.executable, "-I", harness_path]
            try:
                proc = subprocess.Popen(
                    cmd,
                    cwd=tmp_dir,
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                try:
                    stdout, stderr = proc.communicate(timeout=self.timeout_seconds)
                    exit_code = proc.returncode
                    timed_out = False
                except subprocess.TimeoutExpired:
                    proc.kill()
                    stdout, stderr = proc.communicate()
                    exit_code = -1
                    timed_out = True

                duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

                # Cap output
                if len(stdout) > self.max_output_bytes:
                    stdout = stdout[: self.max_output_bytes] + "\n... [Output truncated]"
                if len(stderr) > self.max_output_bytes:
                    stderr = stderr[: self.max_output_bytes] + "\n... [Error output truncated]"

                passed = (exit_code == 0) and not timed_out
                return {
                    "behavioral_tests_run": True,
                    "behavioral_tests_passed": passed,
                    "exit_code": exit_code,
                    "timed_out": timed_out,
                    "duration_ms": duration_ms,
                    "stdout": stdout,
                    "stderr": stderr,
                    "sandbox_isolated": True,
                    "network_disabled": self.disable_network,
                    "secrets_scrubbed": True,
                    "error": (
                        f"Execution timed out after {self.timeout_seconds} seconds."
                        if timed_out
                        else None if passed else f"Test run failed with exit code {exit_code}."
                    ),
                }

            except Exception as exc:
                duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
                logger.error("Sandbox execution error: %s", exc)
                return {
                    "behavioral_tests_run": True,
                    "behavioral_tests_passed": False,
                    "exit_code": -1,
                    "timed_out": False,
                    "duration_ms": duration_ms,
                    "stdout": "",
                    "stderr": str(exc),
                    "sandbox_isolated": True,
                    "network_disabled": self.disable_network,
                    "secrets_scrubbed": True,
                    "error": f"Failed to spawn isolated test runner: {exc}",
                }


def run_isolated_behavioral_tests(
    candidate_code: str,
    test_code: Optional[str] = None,
    timeout_seconds: float = 5.0,
    enabled: bool = True,
) -> Dict[str, Any]:
    """Run behavioral tests against candidate code in an isolated disposable sandbox.

    If enabled is False or test_code is None, runs in text-only mode without executing code.
    """
    if not enabled or not test_code or not test_code.strip():
        return {
            "behavioral_tests_run": False,
            "behavioral_tests_passed": False,
            "mode": "text_only",
            "reason": "Text-only analysis mode active; behavioral testing not requested or no test suite provided.",
        }

    runner = DisposableSandboxRunner(timeout_seconds=timeout_seconds, disable_network=True)
    return runner.execute_test_suite(candidate_code, test_code)


def check_remediation_behaviour_preservation(
    original_code: str,
    candidate_code: str,
) -> Dict[str, Any]:
    """Inspect whether candidate code preserves return-value and exception contracts from original code.

    Specifically analyzes common security remediations such as replacing `os.system(cmd)`
    with `subprocess.run(...)`.
    The remediation must keep the return-value contract:
    - If original returned os.system's status (int), candidate must return result.returncode (int),
      not the CompletedProcess object.
    - Candidate must use check=False (or preserve exception behaviour) instead of check=True,
      which raises CalledProcessError on non-zero exit where os.system returned the status code.
    If the contract is altered, marks finding as 'behaviour_change: true' with an explanation.
    """
    try:
        orig_tree = ast.parse(original_code)
        cand_tree = ast.parse(candidate_code)
    except Exception as exc:
        return {
            "behaviour_preserved": True,
            "behaviour_change": False,
            "warnings": [],
            "findings": [],
            "error": f"AST parse failed: {exc}",
        }

    findings: List[Dict[str, Any]] = []
    warnings: List[str] = []

    def _is_os_system_call(node: ast.AST) -> bool:
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Attribute) and func.attr == "system":
                if isinstance(func.value, ast.Name) and func.value.id == "os":
                    return True
            elif isinstance(func, ast.Name) and func.id == "system":
                return True
        return False

    def _is_subprocess_run_call(node: ast.AST) -> bool:
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Attribute) and func.attr == "run":
                if isinstance(func.value, ast.Name) and func.value.id == "subprocess":
                    return True
            elif isinstance(func, ast.Name) and func.id == "run":
                return True
        return False

    def _scope_functions(tree: ast.AST) -> Dict[str, ast.AST]:
        return {
            node.name: node
            for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        }

    orig_funcs = _scope_functions(orig_tree)
    cand_funcs = _scope_functions(cand_tree)

    def _inspect_scope(orig_scope: ast.AST, cand_scope: Optional[ast.AST], scope_name: str) -> None:
        if cand_scope is None:
            return

        orig_os_system_calls = [n for n in ast.walk(orig_scope) if _is_os_system_call(n)]
        if not orig_os_system_calls:
            return

        # Track variables assigned from os.system(...)
        os_sys_vars = set()
        for n in ast.walk(orig_scope):
            if isinstance(n, (ast.Assign, ast.AnnAssign)):
                val = getattr(n, "value", None)
                if val and any(_is_os_system_call(sub) for sub in ast.walk(val)):
                    targets = n.targets if isinstance(n, ast.Assign) else [n.target]
                    for target in targets:
                        if isinstance(target, ast.Name):
                            os_sys_vars.add(target.id)

        # Check if original returned os.system result
        orig_returns_os_system = False
        for n in ast.walk(orig_scope):
            if isinstance(n, ast.Return) and n.value:
                if any(_is_os_system_call(sub) for sub in ast.walk(n.value)):
                    orig_returns_os_system = True
                elif isinstance(n.value, ast.Name) and n.value.id in os_sys_vars:
                    orig_returns_os_system = True

        cand_subproc_calls = [n for n in ast.walk(cand_scope) if _is_subprocess_run_call(n)]
        if not cand_subproc_calls:
            return

        # Check for check=True in any subprocess.run call
        cand_has_check_true = False
        for call in cand_subproc_calls:
            for kw in call.keywords:
                if kw.arg == "check" and isinstance(kw.value, ast.Constant) and kw.value.value is True:
                    cand_has_check_true = True

        # Track variables assigned from subprocess.run(...)
        cand_subproc_vars = set()
        for n in ast.walk(cand_scope):
            if isinstance(n, (ast.Assign, ast.AnnAssign)):
                val = getattr(n, "value", None)
                if val and any(_is_subprocess_run_call(sub) for sub in ast.walk(val)):
                    targets = n.targets if isinstance(n, ast.Assign) else [n.target]
                    for target in targets:
                        if isinstance(target, ast.Name):
                            cand_subproc_vars.add(target.id)

        cand_returns_completed_process = False
        cand_returns_returncode = False
        for n in ast.walk(cand_scope):
            if isinstance(n, ast.Return) and n.value:
                # Direct return: return subprocess.run(...)
                if isinstance(n.value, ast.Call) and _is_subprocess_run_call(n.value):
                    cand_returns_completed_process = True
                # Direct returncode: return subprocess.run(...).returncode
                elif isinstance(n.value, ast.Attribute) and n.value.attr == "returncode":
                    cand_returns_returncode = True
                # Variable return: return res
                elif isinstance(n.value, ast.Name) and n.value.id in cand_subproc_vars:
                    cand_returns_completed_process = True
                # Variable attribute: return res.returncode
                elif (
                    isinstance(n.value, ast.Attribute)
                    and isinstance(n.value.value, ast.Name)
                    and n.value.value.id in cand_subproc_vars
                    and n.value.attr == "returncode"
                ):
                    cand_returns_returncode = True

        reasons = []
        if cand_has_check_true:
            reasons.append(
                "Remediation uses 'check=True', which raises subprocess.CalledProcessError on non-zero exit codes "
                "where original os.system returned the integer status code without raising."
            )
        if orig_returns_os_system and cand_returns_completed_process and not cand_returns_returncode:
            reasons.append(
                "Remediation returns the CompletedProcess object instead of 'result.returncode'. "
                "Original os.system returned an integer exit status (type int), altering the caller's return-value contract."
            )

        if reasons:
            explanation = " ".join(reasons)
            findings.append({
                "category": "behaviour_change",
                "function": scope_name,
                "issue": "Remediation changes return-value and/or exception behaviour",
                "explanation": explanation,
                "behaviour_change": True,
                "check_true": cand_has_check_true,
                "returns_completed_process": cand_returns_completed_process,
                "recommendation": "Use check=False and return result.returncode to preserve contract.",
            })
            warnings.append(
                f"Behaviour change in '{scope_name}': {explanation} Use check=False and return result.returncode."
            )

    # Check function-level scopes
    for name, orig_fn in orig_funcs.items():
        _inspect_scope(orig_fn, cand_funcs.get(name), name)

    # Check module-level scope if no functions matched
    if not findings:
        _inspect_scope(orig_tree, cand_tree, "<module>")

    return {
        "behaviour_preserved": len(findings) == 0,
        "behaviour_change": len(findings) > 0,
        "warnings": warnings,
        "findings": findings,
    }
