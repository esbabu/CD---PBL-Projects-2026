"""Tests for src/code_formatter.py: clang-format integration and pure-Python beautifier."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_SRC_DIR = _PROJECT_ROOT / "src"
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from code_formatter import (
    fallback_beautify_cpp,
    format_cpp_code,
    format_cpp_with_engine,
    is_clang_format_available,
)
from compiler_runner import check_compile, run_cpp_compiler


class TestCodeFormatter(unittest.TestCase):
    """Unit and integration tests for C++ code formatting."""

    def test_is_clang_format_available_returns_bool(self):
        result = is_clang_format_available()
        self.assertIsInstance(result, bool)

    def test_fallback_beautify_cpp_basic_indentation(self):
        raw_code = """
int main() {
int x = 10;
if (x > 5) {
x = x + 1;
}
return 0;
}
"""
        formatted = fallback_beautify_cpp(raw_code)
        lines = formatted.strip().splitlines()
        self.assertEqual(lines[0], "int main() {")
        self.assertEqual(lines[1], "    int x = 10;")
        self.assertEqual(lines[2], "    if (x > 5) {")
        self.assertEqual(lines[3], "        x = x + 1;")
        self.assertEqual(lines[4], "    }")
        self.assertEqual(lines[5], "    return 0;")
        self.assertEqual(lines[6], "}")

    def test_fallback_beautify_preserves_strings_and_comments(self):
        raw_code = """#include <iostream>

// This comment has { braces } and ; semicolons
int main() {
    const char* msg = "hello { world } ; tricky";
    std::cout << msg << std::endl;
    return 0;
}
"""
        formatted = fallback_beautify_cpp(raw_code)
        self.assertIn("#include <iostream>", formatted)
        self.assertIn("// This comment has { braces } and ; semicolons", formatted)
        self.assertIn('"hello { world } ; tricky"', formatted)

    def test_fallback_beautify_handles_preprocessor(self):
        raw_code = """
#include <iostream>
#define MAX_VAL 100

int main() {
    int y = MAX_VAL;
    return 0;
}
"""
        formatted = fallback_beautify_cpp(raw_code)
        lines = [l for l in formatted.splitlines() if l.strip()]
        self.assertTrue(lines[0].startswith("#include"))
        self.assertTrue(lines[1].startswith("#define"))
        self.assertEqual(lines[0], "#include <iostream>")
        self.assertEqual(lines[1], "#define MAX_VAL 100")

    def test_fallback_beautify_empty_and_whitespace(self):
        self.assertEqual(fallback_beautify_cpp(""), "")
        self.assertEqual(fallback_beautify_cpp("   \n\n  \t  "), "")

    def test_format_cpp_with_engine_fallback(self):
        with patch("code_formatter.is_clang_format_available", return_value=False):
            code = "int main(){return 0;}"
            formatted, engine = format_cpp_with_engine(code)
            self.assertEqual(engine, "fallback")
            self.assertIn("return 0;", formatted)

    def test_format_cpp_code_convenience_function(self):
        with patch("code_formatter.is_clang_format_available", return_value=False):
            code = "int main() {\nint a = 1;\nreturn a;\n}"
            formatted = format_cpp_code(code)
            self.assertIsInstance(formatted, str)
            self.assertIn("    int a = 1;", formatted)

    def test_clang_format_subprocess_success(self):
        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_proc.stdout = "int main() {\n    return 0;\n}\n"
        mock_proc.stderr = ""

        with patch("code_formatter.is_clang_format_available", return_value=True):
            with patch("subprocess.run", return_value=mock_proc) as mock_run:
                formatted, engine = format_cpp_with_engine("int main(){return 0;}", style="Google")
                self.assertEqual(engine, "clang-format")
                self.assertEqual(formatted, "int main() {\n    return 0;\n}\n")
                mock_run.assert_called_once()
                args, kwargs = mock_run.call_args
                self.assertIn("-style=Google", args[0])

    def test_clang_format_subprocess_failure_falls_back(self):
        mock_proc = MagicMock()
        mock_proc.returncode = 1
        mock_proc.stdout = ""
        mock_proc.stderr = "clang-format error"

        with patch("code_formatter.is_clang_format_available", return_value=True):
            with patch("subprocess.run", return_value=mock_proc):
                code = "int main() {\nint x = 5;\nreturn x;\n}"
                formatted, engine = format_cpp_with_engine(code, fallback_on_error=True)
                self.assertEqual(engine, "fallback")
                self.assertIn("    int x = 5;", formatted)

    def test_formatted_code_compiles_cleanly(self):
        source = """
#include <iostream>
#include <vector>

int main() {
std::vector<int> nums = {1, 2, 3};
for (int n : nums) {
std::cout << n << std::endl;
}
return 0;
}
"""
        formatted = format_cpp_code(source)
        verdict = check_compile(formatted)
        self.assertFalse(verdict.blocked)
        self.assertEqual(verdict.action, "allow")

        with tempfile.NamedTemporaryFile(suffix=".cpp", delete=False, mode="w", encoding="utf-8") as f:
            f.write(formatted)
            tmp_path = f.name
        try:
            compile_res = run_cpp_compiler(tmp_path)
            compile_errors = [e for e in compile_res if e.get("type") in ("error", "fatal error")]
            self.assertEqual(compile_errors, [], f"Formatted code had compiler errors: {compile_errors}")
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def test_gui_format_integration(self):
        from gui import AppGUI
        self.assertTrue(hasattr(AppGUI, "format_code"))

    def test_web_server_api_format_endpoint(self):
        from http.server import ThreadingHTTPServer
        from http.client import HTTPConnection
        import threading
        import json
        import time
        import web_server

        server = ThreadingHTTPServer(("127.0.0.1", 0), web_server.CompilerWebHandler)
        port = server.server_address[1]
        token = web_server.SESSION_TOKEN
        t = threading.Thread(target=server.serve_forever, daemon=True)
        t.start()
        time.sleep(0.05)
        try:
            conn = HTTPConnection("127.0.0.1", port, timeout=10)
            body = json.dumps({"code": "int main(){\nint x=1;\nreturn x;\n}"}).encode("utf-8")
            conn.request(
                "POST",
                "/api/format",
                body=body,
                headers={
                    "Host": f"127.0.0.1:{port}",
                    "Content-Type": "application/json",
                    "Content-Length": str(len(body)),
                    "X-Guard-Token": token,
                },
            )
            res = conn.getresponse()
            self.assertEqual(res.status, 200)
            data = json.loads(res.read().decode("utf-8"))
            conn.close()

            self.assertTrue(data.get("ok"))
            self.assertIn("formatted", data)
            self.assertIn("engine", data)
            self.assertIn(data["engine"], ("clang-format", "fallback"))
            self.assertIn("return x;", data["formatted"])
        finally:
            server.shutdown()
            server.server_close()


if __name__ == "__main__":
    unittest.main()
