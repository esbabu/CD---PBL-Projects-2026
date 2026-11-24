"""
Java Error Analyzer - Multilingual Error Diagnosis (Phase 4 & 5)
Compiles Java code safely using javac when available in isolated subprocesses with timeouts.
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
class JavaDiagnostic:
    file: str
    line: int
    column: int
    severity: str        # 'error', 'warning'
    category: str        # 'MissingSemicolon', 'CannotFindSymbol', etc.
    raw_message: str
    explanation: str
    code_snippet: str = ""


class JavaAnalyzer:
    """
    Analyzes Java code for compile errors, warnings, and logical pitfalls.
    Executes in a safe subprocess (compile-only by default, strict timeout, no shell=True).
    Provides graceful heuristic fallback when javac is not installed.
    """

    # Blocked dangerous Java patterns (Application-level sandbox gate)
    # Default-DENY package policy.
    ALLOWED_IMPORTS = {
        "java.util", "java.util.stream", "java.util.function",
        "java.math", "java.lang",
    }
    ALLOWED_IMPORT_PREFIXES = ("java.util.", "java.math.", "java.lang.")

    # Dangerous APIs reachable even from allowed packages — still blocked.
    DANGEROUS_CALLS = [
        (r"Runtime\s*\.\s*getRuntime\s*\(\s*\)\s*\.\s*exec", "Runtime.exec prohibited"),
        (r"\bnew\s+ProcessBuilder\b", "ProcessBuilder prohibited"),
        (r"System\s*\.\s*exit\s*\(", "System.exit prohibited"),
        (r"\bClass\s*\.\s*forName\b", "reflection (Class.forName) prohibited"),
        (r"\.getMethod\s*\(|\.getDeclaredMethod\s*\(", "reflection prohibited"),
        (r"\.getRuntime\s*\(\s*\)", "Runtime access prohibited"),
        (r"\bFiles\s*\.\s*delete|\bFile\s*\.\s*delete", "file deletion prohibited"),
    ]

    def __init__(self, compiler_path: Any = "AUTO"):
        if compiler_path == "AUTO":
            self.compiler_path = self._find_compiler()
        else:
            self.compiler_path = compiler_path

    @property
    def compiler_available(self) -> bool:
        return self.is_compiler_available()

    def _find_compiler(self) -> Optional[str]:
        """Locates javac on PATH or known JAVA_HOME locations."""
        found = shutil.which("javac")
        if found:
            return found

        java_home = os.environ.get("JAVA_HOME")
        if java_home:
            candidate = os.path.join(java_home, "bin", "javac.exe" if os.name == "nt" else "javac")
            if os.path.exists(candidate):
                return candidate
        return None

    def is_compiler_available(self) -> bool:
        return self.compiler_path is not None

    def check_security(self, code: str) -> Optional[Dict[str, Any]]:
        """Default-DENY import policy + dangerous-call blocklist."""
        stripped = re.sub(r'//[^\n]*', '', code)
        stripped = re.sub(r'/\*.*?\*/', '', stripped, flags=re.DOTALL)
        stripped = re.sub(r'"(?:[^"\\]|\\.)*"', '""', stripped)  # strip string literals

        for m in re.finditer(r'^\s*import\s+([\w.]+)\s*;', code, re.MULTILINE):
            pkg = m.group(1)
            if pkg in self.ALLOWED_IMPORTS:
                continue
            if any(pkg.startswith(p) for p in self.ALLOWED_IMPORT_PREFIXES):
                continue
            return {"status": "BLOCKED",
                    "reason": f"Package '{pkg}' is not permitted. Allowed: java.util, java.math, java.lang only.",
                    "matched_snippet": m.group(0).strip()}

        for pattern, msg in self.DANGEROUS_CALLS:
            if re.search(pattern, stripped):
                return {"status": "BLOCKED", "reason": msg, "matched_snippet": pattern}
        return None

    def _extract_class_name(self, code: str) -> str:
        """Extracts the public class name or first class name to name the .java file."""
        pub_match = re.search(r"\bpublic\s+class\s+([A-Za-z_]\w*)", code)
        if pub_match:
            return pub_match.group(1)
        any_match = re.search(r"\bclass\s+([A-Za-z_]\w*)", code)
        if any_match:
            return any_match.group(1)
        return "Solution"

    def generate_candidate(self, code: str, error_type: str) -> Optional[str]:
        """Generate a deterministic candidate fix for common Java errors."""
        if not code or not error_type:
            return None

        lines = code.splitlines()

        if error_type == "MissingSemicolon":
            for i, raw_line in enumerate(lines):
                line = raw_line.strip()
                if not line or line.startswith("//") or line.startswith("/*") or line.startswith("*") or line.startswith("@"):
                    continue
                if line.endswith("{") or line.endswith("}") or line.endswith(":"):
                    continue
                if re.match(r"^(?:public|private|protected|class|interface|if|for|while|try|catch|finally|else)\b", line):
                    continue
                if re.match(r"^(?:return|System\.out|int|double|float|boolean|String|char|long)\b", line):
                    if not line.endswith(";"):
                        fixed_lines = list(lines)
                        fixed_lines[i] = raw_line.rstrip() + ";"
                        suffix = "\n" if code.endswith("\n") else ""
                        return "\n".join(fixed_lines) + suffix
            return None

        if error_type in ("UnmatchedBrace", "UnclosedBlock"):
            if code.endswith("\n"):
                return code + "}\n"
            else:
                return code + "\n}"

        if error_type == "TypoError":
            fixed = code.replace("System.out.printl(", "System.out.println(")
            fixed = re.sub(r"\bSystem\.out\.printl\b", "System.out.println", fixed)
            if fixed != code:
                return fixed
            return None

        if error_type == "CaseSensitivityError":
            fixed = re.sub(r"\bsystem\.out\.", "System.out.", code)
            if fixed != code:
                return fixed
            return None

        if error_type == "MissingImport":
            if "import java.util.Scanner;" not in code:
                return "import java.util.Scanner;\n" + code
            return None

        if error_type == "MissingClassDeclaration":
            indented = "\n".join("        " + l for l in code.splitlines())
            return f"public class Solution {{\n    public static void main(String[] args) {{\n{indented}\n    }}\n}}\n"

        return None

    def analyze(self, code: str, timeout_seconds: float = 5.0) -> Dict[str, Any]:
        """
        Main analysis entrypoint:
        1. Checks security rules
        2. Compiles code via javac if available
        3. If compiler is not available, uses high-precision static heuristic parsing
        """
        # Step 1: Security Gate
        sec_block = self.check_security(code)
        if sec_block:
            return {
                "language": "java",
                "status": "BLOCKED",
                "compiler_available": self.is_compiler_available(),
                "error_type": "SecurityViolation",
                "error_message": sec_block["reason"],
                "explanation": f"Security policy blocked execution: {sec_block['reason']}",
                "line_number": 1,
                "code_snippet": sec_block["matched_snippet"],
                "stdout": "",
                "candidate_code": None,
                "diagnostics": []
            }

        if not code or not code.strip():
            return {
                "language": "java",
                "status": "ERROR",
                "compiler_available": self.is_compiler_available(),
                "error_type": "EmptyCodeError",
                "error_message": "Submitted code is empty.",
                "explanation": "Please provide Java code to analyze.",
                "line_number": 1,
                "code_snippet": "",
                "stdout": "",
                "candidate_code": None,
                "diagnostics": []
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

    def _compile_and_analyze(self, code: str, timeout_seconds: float = 5.0) -> Dict[str, Any]:
        """Runs compile check using javac, then executes the class to capture stdout."""
        lines = code.splitlines()
        class_name = self._extract_class_name(code)
        temp_dir = tempfile.mkdtemp(prefix="tutor_java_")
        source_path = os.path.join(temp_dir, f"{class_name}.java")

        try:
            with open(source_path, "w", encoding="utf-8") as f:
                f.write(code)

            cmd = [
                self.compiler_path,
                "-Xlint:all",
                source_path
            ]

            # 1. COMPILE
            process = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=timeout_seconds,
                shell=False
            )

            if process.returncode != 0:
                # Compilation failed -> Return error diagnostics
                diagnostics = self._parse_diagnostics(process.stderr or process.stdout, lines)
                primary = diagnostics[0] if diagnostics else None
                candidate = self.generate_candidate(code, primary.category) if primary else None

                return {
                    "language": "java",
                    "status": "ERROR",
                    "compiler_available": True,
                    "error_type": primary.category if primary else "CompilationError",
                    "error_message": primary.raw_message if primary else "Compilation failed.",
                    "explanation": primary.explanation if primary else "The Java compiler reported compilation errors.",
                    "line_number": primary.line if primary else 1,
                    "column": primary.column if primary else 1,
                    "code_snippet": primary.code_snippet if primary else "",
                    "stdout": "",
                    "candidate_code": candidate,
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
                    ]
                }

            # 2. EXECUTE (since compilation succeeded)
            run_cmd = ["java", "-cp", temp_dir, class_name]
            try:
                run_process = subprocess.run(
                    run_cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=3.0,  # Strict execution timeout for infinite loops
                    shell=False
                )
                
                # If the program throws a runtime exception, capture it as an ERROR
                if run_process.returncode != 0 and run_process.stderr.strip():
                    return {
                        "language": "java",
                        "status": "ERROR",
                        "compiler_available": True,
                        "error_type": "RuntimeException",
                        "error_message": run_process.stderr.strip().split("\n")[0],
                        "explanation": "Your Java code compiled, but threw a runtime exception during execution.",
                        "line_number": 1,
                        "code_snippet": "",
                        "stdout": run_process.stdout,
                        "candidate_code": None,
                        "diagnostics": []
                    }

                # Success + Capture Output
                return {
                    "language": "java",
                    "status": "SUCCESS",
                    "compiler_available": True,
                    "error_type": None,
                    "error_message": None,
                    "explanation": "Java code compiled and executed successfully.",
                    "line_number": None,
                    "code_snippet": None,
                    "stdout": run_process.stdout,
                    "candidate_code": None,
                    "diagnostics": []
                }

            except subprocess.TimeoutExpired:
                return {
                    "language": "java",
                    "status": "ERROR",
                    "compiler_available": True,
                    "error_type": "TimeoutError",
                    "error_message": "Execution timed out (possible infinite loop).",
                    "explanation": "The program exceeded the 3.0s execution limit.",
                    "line_number": 1,
                    "code_snippet": "",
                    "stdout": "",
                    "candidate_code": None,
                    "diagnostics": []
                }

        except subprocess.TimeoutExpired:
            # Compile timeout
            return {
                "language": "java",
                "status": "ERROR",
                "compiler_available": True,
                "error_type": "TimeoutError",
                "error_message": f"Compilation timed out after {timeout_seconds}s.",
                "explanation": "The compilation process exceeded the execution timeout limit.",
                "line_number": 1,
                "code_snippet": "",
                "stdout": "",
                "candidate_code": None,
                "diagnostics": []
            }
        except Exception as e:
            # Fall back to heuristic on unexpected execution error
            res = self._heuristic_analyze(code)
            res["error_message"] = f"Compiler execution error: {e}. " + (res.get("error_message") or "")
            return res
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def _parse_diagnostics(self, output: str, lines: List[str]) -> List[JavaDiagnostic]:
        """Parses standard javac stderr/stdout diagnostic output."""
        diagnostics = []
        # Pattern: <file>:<line>: error: <message>
        pattern = re.compile(r"^(?:.*?):(\d+):\s*(error|warning):\s*(.*)$")

        for line in output.splitlines():
            line_str = line.strip()
            match = pattern.match(line_str)
            if match:
                line_no = int(match.group(1))
                sev = match.group(2)
                raw_msg = match.group(3)

                category, explanation = self._categorize_error(raw_msg)
                snippet = lines[line_no - 1] if 0 < line_no <= len(lines) else ""

                diagnostics.append(JavaDiagnostic(
                    file="Solution.java",
                    line=line_no,
                    column=1,
                    severity=sev,
                    category=category,
                    raw_message=raw_msg,
                    explanation=explanation,
                    code_snippet=snippet.strip()
                ))

        return diagnostics

    def _categorize_error(self, message: str) -> tuple[str, str]:
        """Maps javac message to a friendly category and pedagogical explanation."""
        msg_lower = message.lower()

        if "';' expected" in msg_lower:
            return (
                "MissingSemicolon",
                "In Java, every statement must end with a semicolon (';'). Check the end of this line."
            )
        if "cannot find symbol" in msg_lower:
            return (
                "CannotFindSymbol",
                "The Java compiler cannot locate this symbol (variable, method, or class). Ensure it is declared, correctly spelled, and required packages are imported."
            )
        if "incompatible types" in msg_lower:
            return (
                "IncompatibleTypes",
                "Type mismatch. Java is strongly typed; the assigned value or expression does not match the variable's declared type."
            )
        if "missing return statement" in msg_lower:
            return (
                "MissingReturnStatement",
                "This method is declared with a non-void return type, but is missing a return statement in one or more code paths."
            )
        if "reached end of file while parsing" in msg_lower:
            return (
                "UnclosedBlock",
                "Unmatched opening curly brace '{'. Ensure every class and method declaration has a matching closing brace '}'."
            )
        if "should be declared in a file named" in msg_lower:
            return (
                "ClassNameMismatch",
                "In Java, a public class must reside in a file whose name matches the class name exactly (including case)."
            )

        return (
            "SyntaxError",
            f"Java syntax error: {message}. Check statement syntax and type definitions."
        )

    def _heuristic_analyze(self, code: str) -> Dict[str, Any]:
        """
        High-precision static fallback parser for Java when javac is unavailable.
        Detects missing class wraps, System.out typos, missing semicolons, unmatched braces,
        and missing return statements across the entire source code.
        """
        lines = code.splitlines()
        diagnostics = []

        # 1. Check if class wrapper is missing
        has_class = bool(re.search(r"\bclass\s+[A-Za-z_]\w*", code))
        if not has_class:
            diagnostics.append({
                "line": 1,
                "column": 1,
                "severity": "error",
                "category": "MissingClassDeclaration",
                "message": "All Java code must be enclosed within a class declaration.",
                "explanation": "Java is an object-oriented language. Wrap your code inside a class (e.g., 'public class Solution { ... }').",
                "code_snippet": lines[0] if lines else ""
            })

        # 2. Check for System.out typos and casing errors
        for i, raw_line in enumerate(lines, 1):
            if re.search(r"\bSystem\.out\.printl\b", raw_line):
                diagnostics.append({
                    "line": i,
                    "column": raw_line.find("System.out.printl") + 1,
                    "severity": "error",
                    "category": "TypoError",
                    "message": "Typo in 'System.out.printl': did you mean 'System.out.println'?",
                    "explanation": "In Java, standard output methods are 'System.out.println()' and 'System.out.print()'.",
                    "code_snippet": raw_line.strip()
                })
            if re.search(r"\bsystem\.out\.print", raw_line):
                diagnostics.append({
                    "line": i,
                    "column": raw_line.find("system.out") + 1,
                    "severity": "error",
                    "category": "CaseSensitivityError",
                    "message": "Java is case-sensitive: 'system' must be capitalized as 'System'.",
                    "explanation": "The 'System' class belongs to 'java.lang' and must begin with an uppercase 'S'.",
                    "code_snippet": raw_line.strip()
                })

        # 3. Check for missing Scanner import
        if re.search(r"\bnew\s+Scanner\s*\(", code) and not re.search(r"import\s+java\.util\.(?:Scanner|\*)\s*;", code):
            diagnostics.append({
                "line": 1,
                "column": 1,
                "severity": "error",
                "category": "MissingImport",
                "message": "Scanner used without importing 'java.util.Scanner'",
                "explanation": "Add 'import java.util.Scanner;' at the top of your Java file.",
                "code_snippet": lines[0] if lines else ""
            })

        # 4. Check for unmatched curly braces
        open_braces = code.count("{")
        close_braces = code.count("}")
        if open_braces > close_braces:
            diagnostics.append({
                "line": len(lines),
                "column": 1,
                "severity": "error",
                "category": "UnclosedBlock",
                "message": f"Unmatched curly braces: found {open_braces} '{{' but only {close_braces} '}}'.",
                "explanation": "Every opening brace '{' must have a matching closing brace '}'. Check class and method boundaries.",
                "code_snippet": lines[-1] if lines else ""
            })

        # 5. Check for missing semicolon on simple statement lines
        for i, raw_line in enumerate(lines, 1):
            line = raw_line.strip()
            if not line or line.startswith("//") or line.startswith("/*") or line.startswith("*") or line.startswith("@"):
                continue
            if line.endswith("{") or line.endswith("}"):
                continue
            if re.match(r"^(?:public|private|protected|class|interface|if|for|while|try|catch|finally|else)\b", line):
                continue
            if re.match(r"^(?:return|System\.out|int|double|float|boolean|String|char|long)\b", line):
                if not line.endswith(";"):
                    diagnostics.append({
                        "line": i,
                        "column": len(raw_line),
                        "severity": "error",
                        "category": "MissingSemicolon",
                        "message": "Missing semicolon ';' at the end of statement",
                        "explanation": "In Java, statements must terminate with a semicolon (';').",
                        "code_snippet": line
                    })

        # 6. Check for non-void method missing return statement
        method_pattern = re.compile(r"\b(?:public|private|protected)?\s*(?:static\s+)?(int|double|float|boolean|String|char|long|[A-Z]\w*)\s+([a-zA-Z_]\w*)\s*\([^)]*\)\s*\{")
        for m in method_pattern.finditer(code):
            ret_type = m.group(1)
            method_name = m.group(2)
            if ret_type in ("void", "class"):
                continue
            start_pos = m.end() - 1
            brace_count = 0
            end_pos = -1
            for pos in range(start_pos, len(code)):
                if code[pos] == '{':
                    brace_count += 1
                elif code[pos] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end_pos = pos
                        break
            if end_pos != -1:
                raw_body = code[start_pos:end_pos]
                clean_body = re.sub(r"//.*", "", raw_body)
                clean_body = re.sub(r"/\*.*?\*/", "", clean_body, flags=re.DOTALL)
                if not re.search(r"\breturn\b", clean_body):
                    line_no = code[:start_pos].count('\n') + 1
                    diagnostics.append({
                        "line": line_no,
                        "column": 1,
                        "severity": "error",
                        "category": "MissingReturnStatement",
                        "message": f"Method '{method_name}' is declared to return '{ret_type}' but does not return a value.",
                        "explanation": f"Non-void method '{method_name}' must return a value of type '{ret_type}'.",
                        "code_snippet": m.group(0)
                    })

        if diagnostics:
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
                "language": "java",
                "status": "ERROR",
                "compiler_available": False,
                "error_type": primary["category"],
                "error_message": primary["message"],
                "explanation": primary["explanation"],
                "line_number": primary["line"],
                "column": primary.get("column", 1),
                "code_snippet": primary.get("code_snippet", ""),
                "stdout": "",
                "candidate_code": self.generate_candidate(code, primary["category"]),
                "diagnostics": diagnostics
            }

        # If no heuristic errors found
        return {
            "language": "java",
            "status": "SUCCESS",
            "compiler_available": False,
            "error_type": None,
            "error_message": None,
            "explanation": "Static analysis detected no obvious Java syntax violations.",
            "line_number": None,
            "code_snippet": None,
            "stdout": "",
            "candidate_code": None,
            "diagnostics": []
        }
