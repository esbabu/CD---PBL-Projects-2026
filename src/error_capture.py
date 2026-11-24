"""
Error Capture Module - Catches and formats Python errors
Week 5
"""

import sys
import traceback
from typing import Dict, Optional, Tuple
from io import StringIO

try:
    from .security import CodeSecurityValidator
except ImportError:
    from security import CodeSecurityValidator

_ISOLATED_RUNNER = r'''
import sys, json, io
try:
    import resource
    resource.setrlimit(resource.RLIMIT_CPU, (3, 3))
    resource.setrlimit(resource.RLIMIT_AS, (256*1024*1024, 256*1024*1024))
    resource.setrlimit(resource.RLIMIT_FSIZE, (0, 0))
    try:
        resource.setrlimit(resource.RLIMIT_NPROC, (0, 0))
    except Exception:
        pass
except ImportError:
    pass  # Windows: POSIX rlimits unavailable; subprocess timeout is the guard
src = sys.stdin.read()

out, err = io.StringIO(), io.StringIO()
old_out, old_err, old_in = sys.stdout, sys.stderr, sys.stdin
sys.stdout, sys.stderr, sys.stdin = out, err, io.StringIO("")
ns = {"__name__": "__main__", "__builtins__": __builtins__}
result = {"ok": True, "stdout": "", "stderr": "", "error_type": None,
          "error_msg": None, "tb": None, "line": None}
try:
    exec(compile(src, "<student>", "exec"), ns, ns)
except SyntaxError as e:
    result.update(ok=False, error_type="SyntaxError", error_msg=e.msg,
                  line=e.lineno, tb=f"SyntaxError: {e.msg} (line {e.lineno})")
except BaseException as e:
    import traceback as _tb
    frames = _tb.extract_tb(e.__traceback__)
    result.update(ok=False, error_type=type(e).__name__, error_msg=str(e),
                  line=frames[-1].lineno if frames else None,
                  tb="".join(_tb.format_exception(type(e), e, e.__traceback__)))
finally:
    sys.stdout, sys.stderr, sys.stdin = old_out, old_err, old_in
result["stdout"] = out.getvalue()
result["stderr"] = err.getvalue()
print("__RESULT__" + json.dumps(result))
'''

class ErrorCapture:

    def __init__(self):
        self.last_error: Optional[Dict] = None
        self.security_validator = CodeSecurityValidator()

    def _run_isolated_python(self, code: str, timeout: float = 3.0) -> dict:
        """Run Python in a subprocess with CPU/memory/file rlimits. Never in-process."""
        import subprocess, sys, json, os, site
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        # Ensure site-packages are on PYTHONPATH so installed libs (numpy, etc.) are found
        site_packages = site.getsitepackages()
        extra_path = os.pathsep.join(site_packages) if site_packages else ""
        if extra_path:
            env["PYTHONPATH"] = extra_path + os.pathsep + env.get("PYTHONPATH", "")
        # Remove PYTHONISOLATED / PYTHONNOUSERSITE if present — we want site-packages
        env.pop("PYTHONISOLATED", None)
        env.pop("PYTHONNOUSERSITE", None)
        try:
            p = subprocess.run(
                [sys.executable, "-c", _ISOLATED_RUNNER],
                input=code, capture_output=True, text=True, timeout=timeout,
                env=env,
            )
            for line in (p.stdout or "").splitlines():
                if line.startswith("__RESULT__"):
                    return json.loads(line[len("__RESULT__"):])
            return {"ok": False, "error_type": "IsolatedExecutionFailure",
                    "error_msg": (p.stderr or "")[:400] or "subprocess crashed",
                    "stdout": "", "tb": None, "line": None}
        except subprocess.TimeoutExpired:
            return {"ok": False, "error_type": "TimeoutError",
                    "error_msg": f"Code exceeded {timeout}s (possible infinite loop).",
                    "stdout": "", "tb": None, "line": None}

    def execute_code(self, code: str) -> Tuple[bool, Optional[Dict]]:
        """
        Execute Python code and capture any errors.

        First validates code for security risks. If dangerous patterns
        are found (BLOCKED level), the code is NOT executed.

        Args:
            code:  Python code string to execute

        Returns:
            Tuple of (success: bool, error_info: dict or None)
            On success with no warnings: (True, None)
            On success with warnings: (True, {'security_warnings': [...]})
            On security block: (False, {error_type: 'SecurityError', ...})
            On error: (False, {error_type: '...', ...})
        """
        # Step 0: Security validation BEFORE execution
        is_safe, warnings = self.security_validator.validate(code)

        if not is_safe:
            # Code contains blocked patterns — do NOT execute
            blocked = [w for w in warnings if w.level == 'BLOCKED']
            warning_messages = '; '.join(w.message for w in blocked)

            error_info = {
                'error_type': 'SecurityError',
                'message': f"Code blocked for safety: {warning_messages}",
                'line_number': blocked[0].line_number if blocked else None,
                'offset': None,
                'code_context': blocked[0].code_snippet if blocked else code,
                'raw_traceback': self.security_validator.format_warnings(),
                'full_code': code,
                'security_warnings': warnings
            }

            self.last_error = error_info
            return False, error_info
        result = self._run_isolated_python(code)
        success = result["ok"]
        error_info = None
        if not success:
            line_no = result.get("line")
            error_info = {
                'error_type': result.get("error_type") or "RuntimeError",
                'message': result.get("error_msg") or "",
                'line_number': line_no,
                'offset': None,
                'code_context': self._get_context_lines(code, line_no) if line_no else code,
                'raw_traceback': result.get("tb") or f"{result.get('error_type')}: {result.get('error_msg')}",
                'full_code': code,
            }
        else:
        # CAPTURE STDOUT ON SUCCESS
            error_info = {
                'error_type': None,
                'message': None,
                'line_number': None,
                'offset': None,
                'code_context': None,
                'raw_traceback': None,
                'full_code': code,
                'stdout': result.get("stdout", "")  # <--- THIS
            }
        # Attach any security warnings (WARNING level) to the result
        if warnings:
            if error_info is None:
                # Code ran successfully but has warnings — create a minimal
                # info dict with ONLY security_warnings to avoid missing-key
                # issues if anyone accesses error_info fields downstream
                error_info = {
                    'error_type': None,
                    'message': None,
                    'line_number': None,
                    'offset': None,
                    'code_context': None,
                    'raw_traceback': None,
                    'full_code': code,
                    'security_warnings': warnings
                }
            else:
                error_info['security_warnings'] = warnings

        self.last_error = error_info
        return success, error_info

    def _format_syntax_error(self, error: SyntaxError, code: str) -> Dict:
        """Format syntax errors with context."""
        return {
            'error_type': 'SyntaxError',
            'message': str(error.msg) if error.msg else str(error),
            'line_number': error.lineno,
            'offset': error.offset,
            'code_context': self._get_context_lines(code, error.lineno),
            'raw_traceback': f"SyntaxError: {error.msg} (line {error.lineno})",
            'full_code': code
        }

    def _format_runtime_error(self, error: BaseException, code: str) -> Dict:
        """Format runtime errors with full traceback."""

        if isinstance(error, SystemExit):
            return {
                'error_type': 'SystemExit',
                'message': f"Program attempted to exit with code: {error.code}",
                'line_number': None,
                'offset': None,
                'code_context': "sys.exit() called",
                'raw_traceback': "SystemExit triggered explicitly.",
                'full_code': code
            }

        tb = traceback.extract_tb(error.__traceback__)
        line_number = tb[-1].lineno if tb else None

        return {
            'error_type': type(error).__name__,
            'message': str(error),
            'line_number': line_number,
            'offset': None,
            'code_context': self._get_context_lines(code, line_number) if line_number else code,
            'raw_traceback': ''.join(traceback.format_exception(type(error), error, error.__traceback__)),
            'full_code': code
        }

    def _get_context_lines(self, code: str, line_number: int, context: int = 3) -> str:
        """Extract lines around the error for context."""
        if not line_number:
            return code

        lines = code.split('\n')
        start = max(0, line_number - context - 1)
        end = min(len(lines), line_number + context)

        context_lines = []
        for i, line in enumerate(lines[start:end], start=start + 1):
            marker = ">>> " if i == line_number else "    "
            context_lines.append(f"{marker}{i}:  {line}")

        return '\n'.join(context_lines)


def capture_error(code: str) -> Tuple[bool, Optional[Dict]]:
    """Capture errors from code execution."""
    capturer = ErrorCapture()
    return capturer.execute_code(code)


if __name__ == "__main__":

    # Test 1: Normal error
    test_code = """
result = 10 / 0
"""
    success, error = capture_error(test_code)

    if not success:
        print("\n--- Error Captured! ---")
        print(f"Type:    {error['error_type']}")
        print(f"Message: {error['message']}")

        if error.get('line_number'):
            print(f"Line:    {error['line_number']}")
            print(f"\nContext:\n{error['code_context']}")
        else:
            print("Line:    Unknown")

    else:
        print("Execution successful!")

    # Test 2: Dangerous code
    print("\n" + "=" * 50)
    dangerous_code = """
import os
os.system('rm -rf /')
"""
    success, error = capture_error(dangerous_code)
    if not success:
        print("\n--- Security Block! ---")
        print(f"Type:    {error['error_type']}")
        print(f"Message: {error['message']}")