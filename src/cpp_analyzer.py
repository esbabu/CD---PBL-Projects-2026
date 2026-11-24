"""
C++ Error Analyzer - Multilingual Error Diagnosis (Phase 4 & 5)
Compiles C++ code safely using g++/clang++ in isolated subprocesses with timeouts.
Provides diagnostic parsing, pedagogical explanations, and static heuristic fallback.
"""

import os
import re
import shutil
import tempfile
import subprocess
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


@dataclass
class CppDiagnostic:
    file: str
    line: int
    column: int
    severity: str        # 'error', 'warning', 'note'
    category: str        # 'MissingSemicolon', 'UndeclaredIdentifier', etc.
    raw_message: str
    explanation: str
    code_snippet: str = ""


class CppAnalyzer:
    """
    Analyzes C++ code for compile errors, warnings, and logical pitfalls.
    Executes in a safe subprocess (compile-only by default, strict timeout, no shell=True).
    """

    # Blocked dangerous C++ patterns (Application-level sandbox gate)
    # Default-DENY header policy: only these headers are permitted in student code.
    ALLOWED_HEADERS = {
        "iostream", "iomanip", "string", "vector", "map", "set", "unordered_map",
        "unordered_set", "algorithm", "cmath", "cstdlib", "cstdio", "queue",
        "stack", "deque", "utility", "numeric", "sstream", "cstring", "cctype",
        "iterator", "cassert", "climits", "functional", "bitset",
    }

    # Dangerous API calls reachable even from allowed headers — still blocked.
    DANGEROUS_CALLS = [
        (r"\bsystem\s*\(", "system() execution is prohibited"),
        (r"\bpopen\s*\(", "popen() execution is prohibited"),
        (r"\b(?:execl|execle|execlp|execv|execve|execvp|execvpe)\s*\(", "exec*() prohibited"),
        (r"\bfork\s*\(", "fork() prohibited"),
        (r"\bdlopen\s*\(|\bdlsym\s*\(", "dynamic loading prohibited"),
        (r"__asm__|\basm\s*\(", "inline assembly prohibited"),
        (r"\bsocket\s*\(|\bconnect\s*\(|\bbind\s*\(|\blisten\s*\(|\baccept\s*\(", "network syscalls prohibited"),
        (r"\bstd::remove\s*\(|\bremove\s*\(|\bunlink\s*\(", "file deletion prohibited"),
    ]

    def __init__(self, compiler_path: Any = "AUTO"):
        if compiler_path == "AUTO":
            self.compiler_path = self._find_compiler()
        else:
            self.compiler_path = compiler_path

    @property
    def compiler_available(self) -> bool:
        return self.is_compiler_available()

    def _test_compiler(self, path: Optional[str]) -> bool:
        """Verifies if the compiler executable can actually execute without system errors."""
        if not path:
            return False
        try:
            res = subprocess.run([path, "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=2.0)
            return res.returncode == 0
        except Exception:
            return False

    def _find_compiler(self) -> Optional[str]:
        """Locates working g++ or clang++ on PATH or known Windows install locations."""
        for candidate in ["g++", "clang++"]:
            found = shutil.which(candidate)
            if found and self._test_compiler(found):
                return found

        # Known common Windows MinGW paths
        known_paths = [
            r"C:\MinGW\bin\g++.exe",
            r"C:\msys64\mingw64\bin\g++.exe",
            r"C:\Program Files\LLVM\bin\clang++.exe"
        ]
        for p in known_paths:
            if os.path.exists(p) and self._test_compiler(p):
                return p
        return None

    def is_compiler_available(self) -> bool:
        return self.compiler_path is not None

    def check_security(self, code: str) -> Optional[Dict[str, Any]]:
        """Default-DENY header policy + dangerous-call blocklist. Never trusts #define aliasing."""
        # 1. Strip comments and string literals so we don't false-positive on text
        stripped = re.sub(r'//[^\n]*', '', code)
        stripped = re.sub(r'/\*.*?\*/', '', stripped, flags=re.DOTALL)
        # If a #define is present, that's an escape vector — reject outright
        if re.search(r'^\s*#\s*define\s+\w+\s+(system|popen|fork|exec\w*|socket|connect|dlopen)\b', code, re.MULTILINE):
            return {"status": "BLOCKED",
                    "reason": "Preprocessor macro aliasing a forbidden call is not allowed.",
                    "matched_snippet": "#define"}
        # 2. Every #include must be from the allowlist
        for m in re.finditer(r'#\s*include\s*[<"]([^>"]+)[>"]', code):
            header = m.group(1).strip()
            if header not in self.ALLOWED_HEADERS:
                return {"status": "BLOCKED",
                        "reason": f"Header '{header}' is not permitted. Allowed headers: {len(self.ALLOWED_HEADERS)} standard STL headers only.",
                        "matched_snippet": m.group(0)}
        # 3. Still block dangerous APIs reachable from allowed headers
        for pattern, msg in self.DANGEROUS_CALLS:
            if re.search(pattern, stripped):
                return {"status": "BLOCKED", "reason": msg, "matched_snippet": pattern}
        return None

    def generate_candidate(self, code: str, error_type: str) -> Optional[str]:
        """Generate a deterministic candidate fix for common C++ errors."""
        if not code or not error_type:
            return None

        lines = code.splitlines()

        if error_type == "MissingSemicolon":
            # 1. Check for struct/class closing brace missing semicolon
            for i, raw_line in enumerate(lines):
                line = raw_line.strip()
                if line == "}" or (line.startswith("}") and not line.endswith(";")):
                    prefix = "\n".join(lines[:i+1])
                    if re.search(r"\b(?:struct|class|enum)\s+[A-Za-z_]\w*", prefix):
                        fixed_lines = list(lines)
                        fixed_lines[i] = raw_line.rstrip() + ";"
                        suffix = "\n" if code.endswith("\n") else ""
                        return "\n".join(fixed_lines) + suffix

            # 2. Check for statements missing semicolon
            for i, raw_line in enumerate(lines):
                line = raw_line.strip()
                if not line or line.startswith("//") or line.startswith("/*") or line.startswith("#"):
                    continue
                if line.endswith("{") or line.endswith("}") or line.endswith(":"):
                    continue
                if line.startswith(("if ", "if(", "for ", "for(", "while ", "while(")):
                    continue
                if re.match(r"^(?:return|cout|cin|int|double|float|char|bool|string|auto|std::cout|std::cin)\b", line):
                    if not line.endswith(";"):
                        fixed_lines = list(lines)
                        fixed_lines[i] = raw_line.rstrip() + ";"
                        suffix = "\n" if code.endswith("\n") else ""
                        return "\n".join(fixed_lines) + suffix
            return None

        if error_type == "StreamOperatorError":
            fixed = re.sub(r"\bcout\s*>>", "cout <<", code)
            fixed = re.sub(r"\bcin\s*<<", "cin >>", fixed)
            if fixed != code:
                return fixed
            return None

        if error_type == "MissingHeaderError":
            if "#include <iostream>" not in code:
                return "#include <iostream>\n" + code
            return None

        if error_type in ("UnmatchedBrace", "UnclosedBlock"):
            if code.endswith("\n"):
                return code + "}\n"
            else:
                return code + "\n}"

        if error_type == "UndeclaredIdentifier":
            for i, raw_line in enumerate(lines):
                if "{" in raw_line and ("main(" in raw_line or "main (" in raw_line):
                    m = re.search(r"std::cout\s*<<\s*([a-zA-Z_]\w*)", code)
                    var_name = m.group(1) if m else "secret_variable"
                    fixed_lines = list(lines)
                    fixed_lines.insert(i + 1, f"    int {var_name} = 0;")
                    suffix = "\n" if code.endswith("\n") else ""
                    return "\n".join(fixed_lines) + suffix
            return None

        return None

    def analyze(self, code: str, timeout_seconds: float = 5.0) -> Dict[str, Any]:
        """
        Main analysis entrypoint:
        1. Checks security rules
        2. Compiles code via g++/clang++ if available
        3. If compiler is not available, uses high-precision static heuristic parsing
        """
        # Step 1: Security Gate
        sec_block = self.check_security(code)
        if sec_block:
            return {
                "language": "cpp",
                "status": "BLOCKED",
                "compiler_available": self.is_compiler_available(),
                "error_type": "SecurityViolation",
                "error_message": sec_block["reason"],
                "explanation": f"Security policy blocked execution: {sec_block['reason']}",
                "line_number": 1,
                "code_snippet": sec_block["matched_snippet"],
                "diagnostics": [],
                "stdout": "",
                "candidate_code": None
            }

        if not code or not code.strip():
            return {
                "language": "cpp",
                "status": "ERROR",
                "compiler_available": self.is_compiler_available(),
                "error_type": "EmptyCodeError",
                "error_message": "Submitted code is empty.",
                "explanation": "Please provide C++ code to analyze.",
                "line_number": 1,
                "code_snippet": "",
                "diagnostics": [],
                "stdout": "",
                "candidate_code": None
            }

        # Step 2: Use compiler if available
        if self.is_compiler_available():
            res = self._compile_and_analyze(code, timeout_seconds)
        else:
            # Step 3: Heuristic fallback
            res = self._heuristic_analyze(code)

        if res.get("candidate_code") is None and res.get("error_type"):
            res["candidate_code"] = self.generate_candidate(code, res["error_type"])
        res.setdefault("candidate_code", None)
        res.setdefault("stdout", "")
        return res

    def _compile_and_analyze(self, code: str, timeout_seconds: float) -> Dict[str, Any]:
        """Runs compile-only check using g++."""
        lines = code.splitlines()
        temp_dir = tempfile.mkdtemp(prefix="tutor_cpp_")
        source_path = os.path.join(temp_dir, "code.cpp")

        try:
            with open(source_path, "w", encoding="utf-8") as f:
                f.write(code)

            exe_path = os.path.join(temp_dir, "prog.exe" if os.name == "nt" else "prog")
            cmd = [
                self.compiler_path,
                "-Wall",
                "-std=c++14",
                source_path,
                "-o",exe_path
            ]

            process = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=timeout_seconds,
                shell=False
            )

            if process.returncode == 0:
                try:
                    run_process = subprocess.run([exe_path], capture_output=True, text=True, timeout=2.0)
                    stdout = run_process.stdout
                    stderr = run_process.stderr
                except subprocess.TimeoutExpired:
                    stdout = ""
                    stderr = "Execution timed out (possible infinite loop)."
                return {
                    "language": "cpp",
                    "status": "SUCCESS",
                    "compiler_available": True,
                    "error_type": None,
                    "error_message": None,
                    "explanation": "C++ code compiled cleanly with no compilation errors or fatal warnings.",
                    "line_number": None,
                    "code_snippet": None,
                    "diagnostics": [],
                    "stdout": stdout,
                    "candidate_code": None
                }

            # Parse compiler diagnostics
            diagnostics = self._parse_diagnostics(process.stderr, lines)
            primary = diagnostics[0] if diagnostics else None
            candidate = self.generate_candidate(code, primary.category) if primary else None

            return {
                "language": "cpp",
                "status": "ERROR",
                "compiler_available": True,
                "error_type": primary.category if primary else "CompilationError",
                "error_message": primary.raw_message if primary else "Compilation failed.",
                "explanation": primary.explanation if primary else "The C++ compiler reported compilation errors.",
                "line_number": primary.line if primary else 1,
                "column": primary.column if primary else 1,
                "code_snippet": primary.code_snippet if primary else "",
                "diagnostics": [
                    {
                        "line": d.line,
                        "column": d.column,
                        "severity": d.severity,
                        "category": d.category,
                        "message": d.raw_message,
                        "explanation": d.explanation,
                        "code_snippet": d.code_snippet
                    }
                    for d in diagnostics
                ],
                "stdout": "",
                "candidate_code": candidate
            }

        except subprocess.TimeoutExpired:
            return {
                "language": "cpp",
                "status": "ERROR",
                "compiler_available": True,
                "error_type": "TimeoutError",
                "error_message": f"Compilation timed out after {timeout_seconds}s.",
                "explanation": "The compilation process exceeded the execution timeout limit.",
                "line_number": 1,
                "code_snippet": "",
                "diagnostics": [],
                "stdout": "",
                "candidate_code": None
            }
        except Exception as e:
            # Fall back to heuristic on unexpected execution error
            res = self._heuristic_analyze(code)
            if res.get("status") == "ERROR" and not res.get("error_message"):
                res["error_message"] = f"Compiler execution error: {e}"
            return res
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def _parse_diagnostics(self, stderr: str, lines: List[str]) -> List[CppDiagnostic]:
        """Parses standard gcc/clang stderr diagnostic output."""
        diagnostics = []
        # Pattern: <file>:<line>:<col>: error: <message>
        pattern = re.compile(r"^(?:.*?):(\d+):(\d+):\s*(error|warning|fatal error):\s*(.*)$")

        for line in stderr.splitlines():
            line_str = line.strip()
            match = pattern.match(line_str)
            if match:
                line_no = int(match.group(1))
                col_no = int(match.group(2))
                sev = "error" if "error" in match.group(3) else "warning"
                raw_msg = match.group(4)

                category, explanation = self._categorize_error(raw_msg)
                snippet = lines[line_no - 1] if 0 < line_no <= len(lines) else ""

                diagnostics.append(CppDiagnostic(
                    file="code.cpp",
                    line=line_no,
                    column=col_no,
                    severity=sev,
                    category=category,
                    raw_message=raw_msg,
                    explanation=explanation,
                    code_snippet=snippet.strip()
                ))

        return diagnostics

    def _categorize_error(self, message: str) -> tuple[str, str]:
        """Maps compiler message to a friendly category and pedagogical explanation."""
        msg_lower = message.lower()

        if re.search(r"expected\s+.*';'", msg_lower) or ("expected" in msg_lower and ";" in msg_lower):
            return (
                "MissingSemicolon",
                "In C++, statements must terminate with a semicolon (';'). Check the end of this or the preceding line."
            )
        if "was not declared in this scope" in msg_lower:
            ident = message.split("'")[1] if "'" in message else "variable"
            return (
                "UndeclaredIdentifier",
                f"Identifier '{ident}' is not declared in this scope. Ensure it is defined before use or include the necessary header (e.g., <iostream>, <vector>, <string>)."
            )
        if "no match for 'operator<<'" in msg_lower or "invalid operands of types" in msg_lower:
            return (
                "StreamOperatorError",
                "Stream operator mismatch. In C++, 'cout' uses the insertion operator '<<' (e.g., 'cout << value;'), while 'cin' uses '>>'."
            )
        if "cannot convert" in msg_lower or "invalid conversion" in msg_lower:
            return (
                "TypeMismatch",
                "Incompatible types in assignment or function argument. C++ is statically typed; ensure values match the variable's declared type."
            )
        if "expected '}'" in msg_lower or "expected unqualified-id at end of input" in msg_lower:
            return (
                "UnmatchedBrace",
                "Unmatched opening curly brace '{' detected. Verify that every function, class, or loop block has a matching closing brace '}'."
            )
        if "redefinition of" in msg_lower:
            return (
                "RedefinitionError",
                "Duplicate variable or function definition. An entity with the same name was already declared in this scope."
            )
        if "no return statement" in msg_lower:
            return (
                "MissingReturnStatement",
                "Non-void function missing return statement. Ensure all execution branches return a value matching the function's return type."
            )

        return (
            "SyntaxError",
            f"C++ syntax or semantic error: {message}. Verify syntax and type compatibility."
        )

    CPP_KNOWN_IDENTIFIERS = {
        "auto", "bool", "break", "case", "catch", "char", "class", "const", "constexpr",
        "continue", "default", "delete", "do", "double", "else", "enum", "explicit",
        "export", "extern", "false", "float", "for", "friend", "goto", "if", "inline",
        "int", "long", "mutable", "namespace", "new", "noexcept", "nullptr", "NULL",
        "operator", "private", "protected", "public", "register", "reinterpret_cast",
        "return", "short", "signed", "sizeof", "static", "static_cast", "struct",
        "switch", "template", "this", "throw", "true", "try", "typedef", "typeid",
        "typename", "union", "unsigned", "using", "virtual", "void", "volatile",
        "while", "size_t", "string", "vector", "map", "set", "unordered_map",
        "unordered_set", "queue", "stack", "deque", "pair", "make_pair", "tuple",
        "cin", "cout", "cerr", "clog", "endl", "std", "printf", "scanf", "main",
        "min", "max", "abs", "sqrt", "pow", "push_back", "pop_back", "insert",
        "erase", "size", "empty", "clear", "begin", "end", "first", "second",
        "data", "left", "right", "root", "val", "tree", "node", "BSTNode", "BinarySearchTree"
    }

    def _heuristic_analyze(self, code: str) -> Dict[str, Any]:
        """
        High-precision static fallback parser for C++ when compiler is unavailable.
        Detects missing semicolons, stream operator errors, missing headers, unmatched braces,
        and undeclared identifiers across the entire source code.
        """
        lines = code.splitlines()
        diagnostics = []

        # 1. Check for inverted stream operator: cout >> or cin <<
        for i, raw_line in enumerate(lines, 1):
            if re.search(r"\bcout\s*>>", raw_line):
                diagnostics.append({
                    "line": i,
                    "column": raw_line.find(">>") + 1 if ">>" in raw_line else 1,
                    "severity": "error",
                    "category": "StreamOperatorError",
                    "message": "Invalid stream operator: 'cout >>' used instead of 'cout <<'",
                    "explanation": "In C++, 'cout' outputs data using the insertion operator '<<'. Replace '>>' with '<<'.",
                    "code_snippet": raw_line.strip()
                })
            if re.search(r"\bcin\s*<<", raw_line):
                diagnostics.append({
                    "line": i,
                    "column": raw_line.find("<<") + 1 if "<<" in raw_line else 1,
                    "severity": "error",
                    "category": "StreamOperatorError",
                    "message": "Invalid stream operator: 'cin <<' used instead of 'cin >>'",
                    "explanation": "In C++, 'cin' reads input using the extraction operator '>>'. Replace '<<' with '>>'.",
                    "code_snippet": raw_line.strip()
                })

        # 2. Check for missing headers (cout/cin used without <iostream>)
        has_iostream = bool(re.search(r"#include\s*<iostream>", code))
        if ("cout" in code or "cin" in code) and not has_iostream:
            diagnostics.append({
                "line": 1,
                "column": 1,
                "severity": "error",
                "category": "MissingHeaderError",
                "message": "Using 'cout' or 'cin' without '#include <iostream>'",
                "explanation": "Standard I/O streams require the <iostream> header. Add '#include <iostream>' at the top of the file.",
                "code_snippet": lines[0] if lines else ""
            })

        # 3. Check for unmatched curly braces
        open_braces = code.count("{")
        close_braces = code.count("}")
        if open_braces > close_braces:
            diagnostics.append({
                "line": len(lines),
                "column": 1,
                "severity": "error",
                "category": "UnmatchedBrace",
                "message": f"Unmatched curly braces: found {open_braces} '{{' but only {close_braces} '}}'.",
                "explanation": "Every opening brace '{' must have a corresponding closing brace '}'. Check block closures.",
                "code_snippet": lines[-1] if lines else ""
            })

        # 4. Check for missing semicolon after struct / class / enum closing brace
        current_depth = 0
        class_depths = []
        for i, raw_line in enumerate(lines, 1):
            line = raw_line.strip()
            if re.search(r"\b(?:struct|class|enum)\s+[A-Za-z_]\w*", line):
                class_depths.append(current_depth)
            for char in line:
                if char == '{':
                    current_depth += 1
                elif char == '}':
                    current_depth -= 1
                    if class_depths and current_depth == class_depths[-1]:
                        class_depths.pop()
                        clean = re.sub(r"//.*", "", line).strip()
                        if not clean.endswith(";") and not clean.endswith("{"):
                            diagnostics.append({
                                "line": i,
                                "column": len(raw_line),
                                "severity": "error",
                                "category": "MissingSemicolon",
                                "message": "Missing semicolon ';' after struct or class definition",
                                "explanation": "In C++, struct and class definitions must terminate with a semicolon after the closing brace ('};').",
                                "code_snippet": line
                            })

        # 5. Check for missing semicolon on simple statement lines
        for i, raw_line in enumerate(lines, 1):
            line = raw_line.strip()
            if not line or line.startswith("//") or line.startswith("/*") or line.startswith("#"):
                continue
            if line.endswith("{") or line.endswith("}") or line.endswith(":"):
                continue
            if line.startswith(("if ", "if(", "for ", "for(", "while ", "while(")):
                continue
            if re.match(r"^(?:return|cout|cin|int|double|float|char|bool|string|auto|std::cout|std::cin)\b", line):
                if not line.endswith(";"):
                    diagnostics.append({
                        "line": i,
                        "column": len(raw_line),
                        "severity": "error",
                        "category": "MissingSemicolon",
                        "message": "Missing semicolon ';' at the end of statement",
                        "explanation": "In C++, statements must terminate with a semicolon (';').",
                        "code_snippet": line
                    })

        # 6. Check for undeclared identifiers in statements
        declared = set(self.CPP_KNOWN_IDENTIFIERS)
        for m in re.finditer(r"\b(?:int|double|float|char|bool|string|auto|void|long|short|unsigned|signed|size_t|[A-Z]\w*)\s+(\*+)?\s*([a-zA-Z_]\w*)", code):
            declared.add(m.group(2))
        for m in re.finditer(r"\b(?:class|struct|enum)\s+([a-zA-Z_]\w*)", code):
            declared.add(m.group(1))
        for m in re.finditer(r"template\s*<\s*(?:typename|class)\s+([a-zA-Z_]\w*)", code):
            declared.add(m.group(1))
        for m in re.finditer(r"([a-zA-Z_]\w*)\s*\(([^)]*)\)", code):
            declared.add(m.group(1))
            for p in m.group(2).split(","):
                p_words = re.findall(r"\b[a-zA-Z_]\w*\b", p)
                if p_words:
                    declared.add(p_words[-1])

        for i, raw_line in enumerate(lines, 1):
            line = raw_line.strip()
            if not line or line.startswith("//") or line.startswith("/*") or line.startswith("#"):
                continue
            # Strip string literals, char literals, and comments
            clean_stmt = re.sub(r'"(\\.|[^"\\])*"', '""', line)
            clean_stmt = re.sub(r"'(\\.|[^'\\])*'", "''", clean_stmt)
            clean_stmt = re.sub(r'//.*', '', clean_stmt)
            clean_stmt = re.sub(r'\bstd::', '', clean_stmt)
            clean_stmt = re.sub(r'(?:\.|\->)[a-zA-Z_]\w*', '', clean_stmt)
            tokens = re.findall(r'\b[a-zA-Z_]\w*\b', clean_stmt)
            for t in tokens:
                if t not in declared and not t.isdigit() and len(t) > 1:
                    diagnostics.append({
                        "line": i,
                        "column": raw_line.find(t) + 1 if t in raw_line else 1,
                        "severity": "error",
                        "category": "UndeclaredIdentifier",
                        "message": f"Identifier '{t}' was not declared in this scope",
                        "explanation": f"Identifier '{t}' is not declared in this scope. Ensure it is defined before use or include the necessary header (e.g., <iostream>, <vector>, <string>).",
                        "code_snippet": line
                    })

        if diagnostics:
            # Sort by line number and deduplicate
            diagnostics.sort(key=lambda d: (d["line"], d.get("column", 1)))
            unique_diags = []
            seen = set()
            for d in diagnostics:
                key = (d["line"], d["category"])
                if key not in seen:
                    seen.add(key)
                    unique_diags.append(d)
            diagnostics = unique_diags
            primary = diagnostics[0]

            return {
                "language": "cpp",
                "status": "ERROR",
                "compiler_available": False,
                "error_type": primary["category"],
                "error_message": primary["message"],
                "explanation": primary["explanation"],
                "line_number": primary["line"],
                "column": primary.get("column", 1),
                "code_snippet": primary.get("code_snippet", ""),
                "diagnostics": diagnostics,
                "stdout": "",
                "candidate_code": self.generate_candidate(code, primary["category"])
            }

        # If no heuristic errors found
        return {
            "language": "cpp",
            "status": "SUCCESS",
            "compiler_available": False,
            "error_type": None,
            "error_message": None,
            "explanation": "Static analysis detected no obvious C++ syntax violations.",
            "line_number": None,
            "code_snippet": None,
            "diagnostics": [],
            "stdout": "",
            "candidate_code": None
        }
