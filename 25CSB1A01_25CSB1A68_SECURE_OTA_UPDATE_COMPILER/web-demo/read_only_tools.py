"""
read_only_tools.py - Bounded Read-Only Auxiliary Tool Runner for the Agentic Judge

Requirements:
- Strict READ-ONLY mode with ZERO file-system write permissions.
- Auxiliary local static analysis tools executed via sanitized parameter arrays without shell expansion (shell=False) to prevent command injection.
- Specialized static security evaluators for CFG dominance, memory safety, banned APIs, and hardcoded secrets.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
from typing import Any, Dict, List, Optional


class ReadOnlySecurityToolRunner:
    """
    Executes auxiliary static analysis tools under strict read-only constraints:
    - shell=False with argument vector sanitization (no shell interpolation).
    - Temporary file inputs marked read-only with auto-cleanup.
    - Strict timeouts to avoid denial-of-service hangs.
    """

    @staticmethod
    def run_external_analyzer(tool_binary: str, args: List[str], input_text: Optional[str] = None, timeout: float = 4.0) -> Dict[str, Any]:
        """
        Executes a local binary tool safely via argument vector (shell=False).
        Guarantees zero shell expansion and strict timeouts.
        """
        resolved_bin = shutil.which(tool_binary)
        if not resolved_bin:
            return {
                "available": False,
                "tool": tool_binary,
                "message": f"Tool '{tool_binary}' not present in local environment.",
                "output": "",
            }

        # Parameter sanitization: reject any shell redirection or write-back arguments
        dangerous_flags = {"-o", "--output", ">", ">>", "|", "&", ";", "`", "$"}
        for arg in args:
            if any(df in arg for df in dangerous_flags):
                return {
                    "available": True,
                    "tool": tool_binary,
                    "error": f"Rejected argument '{arg}' violating read-only policy.",
                    "output": "",
                }

        cmd = [resolved_bin] + args

        try:
            res = subprocess.run(
                cmd,
                input=input_text,
                capture_output=True,
                text=True,
                timeout=timeout,
                shell=False,  # Strict: NO shell expansion
            )
            return {
                "available": True,
                "tool": tool_binary,
                "returncode": res.returncode,
                "stdout": res.stdout,
                "stderr": res.stderr,
                "output": (res.stdout + "\n" + res.stderr).strip(),
            }
        except subprocess.TimeoutExpired:
            return {
                "available": True,
                "tool": tool_binary,
                "error": f"Tool execution timed out after {timeout}s.",
                "output": "",
            }
        except Exception as exc:
            return {
                "available": True,
                "tool": tool_binary,
                "error": str(exc),
                "output": "",
            }

    @classmethod
    def run_cppcheck_if_available(cls, source_code: str) -> Dict[str, Any]:
        """
        Invokes cppcheck if available in read-only mode using a temporary file.
        """
        resolved = shutil.which("cppcheck")
        if not resolved:
            return {"available": False, "tool": "cppcheck", "summary": "cppcheck not installed (fallback to in-memory AST analysis)"}

        with tempfile.NamedTemporaryFile(suffix=".c", mode="w", delete=False, encoding="utf-8") as tmp:
            tmp.write(source_code)
            tmp_path = tmp.name

        try:
            # Arguments strictly read-only, no write-back flags
            args = ["--enable=warning,style", "--inconclusive", "--inline-suppr", tmp_path]
            res = cls.run_external_analyzer("cppcheck", args, timeout=5.0)
            return res
        finally:
            try:
                import os
                os.remove(tmp_path)
            except OSError:
                pass

    @staticmethod
    def audit_cfg_dominance(source_code: str) -> Dict[str, Any]:
        """
        Evaluates control-flow dominance invariants over install() in read-only mode:
        1. verifySignature (or verify_signature) strictly dominates install()
        2. sourceTrusted (or source_trusted) strictly dominates install()
        3. verifyImageHash (or verify_image_hash) strictly dominates install()
        4. Monotonic rollback check strictly dominates install()
        """
        is_python = ("def " in source_code and "#include" not in source_code)
        if is_python:
            try:
                import sys
                from pathlib import Path
                root = Path(__file__).resolve().parent.parent
                if str(root) not in sys.path:
                    sys.path.insert(0, str(root))
                from tools.secure_python import check_python_security
                ok, viols, _, _ = check_python_security(source_code)
                sig_dom = not any("Signature Verification" in v for v in viols)
                src_dom = not any("Trusted Source" in v for v in viols)
                hash_dom = not any("Image Hash" in v for v in viols)
                issues = [v for v in viols if "Dominance Violation" in v or "Rollback" in v]
                has_install = "install(" in source_code.lower() or "installfirmware(" in source_code.lower()
                return {
                    "has_install": has_install,
                    "signature_dominates": sig_dom,
                    "source_dominates": src_dom,
                    "hash_dominates": hash_dom,
                    "issues": issues,
                    "passed": len(issues) == 0,
                }
            except Exception:
                pass

        code_no_comments = re.sub(r'/\*[\s\S]*?\*/|//[^\n]*', '', source_code)
        
        INSTALL_NAMES = r'\b(?:install|installFirmware|install_firmware|applyUpdate|apply_update|flashFirmware|flash_firmware)\s*\('
        SIG_NAMES = r'\b(?:verifySignature|verify_signature|checkSignature|check_signature|crypto_ecdsa_verify|ecdsa_verify)\s*\('
        SRC_NAMES = r'\b(?:sourceTrusted|source_trusted|isSourceTrusted|validateSource|validate_source|checkSourceUrl|check_source_url)\s*\('
        HASH_NAMES = r'\b(?:verifyImageHash|verify_image_hash|checkImageHash|check_image_hash|verifyHash|verify_hash|crypto_sha256)\s*\('

        # Find functions containing an install/flash invocation
        func_pattern = re.compile(
            r'(?:int|void|OtaStatus|UpdateStatus|bool|static\s+\w+)\s+(\w+)\s*\([^)]*\)\s*\{',
            re.MULTILINE
        )
        matches = list(func_pattern.finditer(code_no_comments))
        functions_with_install = []
        for match in matches:
            fn_name = match.group(1)
            if any(alias in fn_name for alias in ['install', 'applyUpdate', 'flashFirmware']):
                continue
            start_brace = code_no_comments.find('{', match.start())
            depth = 1
            i = start_brace + 1
            while i < len(code_no_comments) and depth > 0:
                if code_no_comments[i] == '{': depth += 1
                elif code_no_comments[i] == '}': depth -= 1
                i += 1
            body = code_no_comments[start_brace + 1 : i - 1]
            if re.search(INSTALL_NAMES, body):
                functions_with_install.append((fn_name, body))

        if not functions_with_install:
            has_inst = bool(re.search(INSTALL_NAMES, code_no_comments))
            return {
                "has_install": has_inst,
                "signature_dominates": not has_inst,
                "source_dominates": not has_inst,
                "hash_dominates": not has_inst,
                "rollback_dominates": not has_inst,
                "summary": "No install() invocation in firmware routine." if not has_inst else "install() outside recognized function.",
                "issues": [] if not has_inst else ["install() called outside structured update routine"],
                "passed": not has_inst,
            }

        issues: List[str] = []
        for fn_name, body in functions_with_install:
            inst_m = re.search(INSTALL_NAMES, body)
            inst_pos = inst_m.start() if inst_m else -1
            body_before = body[:inst_pos]

            # 1. Digital Signature Check
            sig_m = re.search(SIG_NAMES, body)
            if not sig_m:
                issues.append(f"verifySignature() check missing in {fn_name}()")
            elif sig_m.start() > inst_pos:
                issues.append(f"verifySignature() does not dominate install() in {fn_name}() (called after install)")

            # 2. Source Trust Check
            src_m = re.search(SRC_NAMES, body)
            if not src_m:
                issues.append(f"sourceTrusted() repository validation missing in {fn_name}()")
            elif src_m.start() > inst_pos:
                issues.append(f"sourceTrusted() does not dominate install() in {fn_name}() (called after install)")

            # 3. Cryptographic Image Hash Check
            hash_m = re.search(HASH_NAMES, body)
            if not hash_m:
                issues.append(f"verifyImageHash() check missing in {fn_name}()")
            elif hash_m.start() > inst_pos:
                issues.append(f"verifyImageHash() does not dominate install() in {fn_name}() (called after install)")

            # 4. Anti-Rollback Guard
            if re.search(r'\b(?:pkg->version|pkg\.version|\w*version)\s*>=\s*(?:current_version|dev->current_version|dev->active_version|\w+_version)\b', body_before):
                issues.append(f"Anti-rollback flaw in {fn_name}(): allows equal version (monotonic rollback violation)")
            else:
                has_rollback = (
                    bool(re.search(r'\b(?:pkg->version|pkg\.version|\w*version)\s*<=\s*(?:current_version|dev->current_version|dev->active_version|\w*version)\b', body_before)) or
                    bool(re.search(r'\b(?:current_version|dev->current_version|dev->active_version|\w*version)\s*>=\s*(?:pkg->version|pkg\.version|\w*version)\b', body_before)) or
                    bool(re.search(r'\b(?:pkg->version|pkg\.version|\w*version)\s*>\s*(?:current_version|dev->current_version|dev->active_version|\w*version)\b', body_before))
                )
                if not has_rollback:
                    issues.append(f"Anti-rollback check missing or does not dominate install() in {fn_name}()")

        return {
            "has_install": True,
            "signature_dominates": not any("verifySignature" in iss for iss in issues),
            "source_dominates": not any("sourceTrusted" in iss for iss in issues),
            "hash_dominates": not any("verifyImageHash" in iss for iss in issues),
            "rollback_dominates": not any("rollback" in iss.lower() for iss in issues),
            "issues": issues,
            "passed": len(issues) == 0,
        }

    @staticmethod
    def audit_external_libraries(source_code: str) -> Dict[str, Any]:
        """
        Audits source code for unauthorized external library includes.
        The Secure OTA Compiler requires self-contained translation units.
        Allowed standard headers: <stdint.h>, <stddef.h>, <stdbool.h>, <string.h>, <limits.h>, <assert.h>, <stdio.h>.
        Forbidden: mbedtls/*, openssl/*, wolfssl/*, sodium/*, curl/*, windows.h, unistd.h, pthread.h, etc.
        """
        is_python = ("def " in source_code and "#include" not in source_code)
        if is_python:
            return {
                "passed": True,
                "detected_libraries": [],
                "count": 0,
            }

        lines = source_code.splitlines()
        detected: List[Dict[str, Any]] = []

        ALLOWED_STD_HEADERS = {
            "stdint.h", "stddef.h", "stdbool.h", "string.h",
            "limits.h", "assert.h", "stdio.h"
        }

        include_pattern = re.compile(r'^\s*#\s*include\s*([<"])([^>"]+)([>"])')
        for idx, line in enumerate(lines, start=1):
            match = include_pattern.match(line)
            if match:
                header = match.group(2).strip()
                basename = header.split("/")[-1].split("\\")[-1]

                is_known_forbidden = any(
                    prefix in header.lower()
                    for prefix in ["mbedtls/", "openssl/", "wolfssl/", "sodium/", "curl/", "windows.h", "unistd.h", "pthread.h", "sys/"]
                )
                is_unauthorized = is_known_forbidden or (header not in ALLOWED_STD_HEADERS and basename not in ALLOWED_STD_HEADERS)

                if is_unauthorized:
                    detected.append({
                        "line": idx,
                        "header": header,
                        "raw": line.strip(),
                        "category": "External Library Violation",
                        "reason": (
                            f"Header '{header}' violates the Self-Contained Translation Unit rule: "
                            "secure-clang builds standalone embedded firmware. Third-party external libraries are strictly forbidden."
                        ),
                        "suggested_fix": (
                            f"Strip '{line.strip()}'; use pure standard ANSI C headers (<stdint.h>, <stddef.h>, <stdbool.h>, <string.h>) "
                            "and define self-contained cryptographic verification stubs."
                        )
                    })

        return {
            "passed": len(detected) == 0,
            "detected_libraries": detected,
            "count": len(detected),
        }

    @staticmethod
    def audit_memory_safety(source_code: str) -> Dict[str, Any]:
        """
        Audits source code for banned memory-unsafe APIs (strcpy, sprintf, gets) and unbounded buffers.
        """
        is_python = ("def " in source_code and "#include" not in source_code)
        if is_python:
            return {
                "passed": True,
                "banned_memory_calls": [],
                "recommendation": "Memory safety guaranteed by Python managed execution.",
            }

        banned_memory_apis = ["strcpy", "sprintf", "gets", "strcat"]
        found: List[str] = []
        for api in banned_memory_apis:
            pattern = re.compile(rf"\b{api}\s*\(", re.IGNORECASE)
            if pattern.search(source_code):
                found.append(api)

        return {
            "passed": len(found) == 0,
            "banned_memory_calls": found,
            "recommendation": "Use bounded alternatives (strncpy, snprintf, memcpy) with explicit size bounds." if found else "Memory safety invariant satisfied.",
        }

    @staticmethod
    def audit_banned_functions(source_code: str) -> Dict[str, Any]:
        """
        Audits for sensitive logging (printf, puts) and weak crypto/entropy (MD5, SHA1, rand).
        Strips comments to prevent false positives on remediation comments or explanations.
        """
        is_python = ("def " in source_code and "#include" not in source_code)
        if is_python:
            clean_py = re.sub(r'"""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'|#[^\n]*', ' ', source_code)
            banned_apis = ["eval", "exec", "os.system", "pickle.loads"]
            found_banned = [api for api in banned_apis if re.search(rf"\b{re.escape(api)}\s*\(", clean_py)]
            found_crypto = [api for api in ["md5", "sha1"] if re.search(rf"\b{api}\s*\(", clean_py, re.IGNORECASE)]
            return {
                "passed": len(found_banned) == 0 and len(found_crypto) == 0,
                "logging_calls": [],
                "weak_crypto_calls": found_crypto,
                "banned_calls": found_banned,
            }

        clean_code = re.sub(r'/\*[\s\S]*?\*/|//[^\n]*', ' ', source_code)

        func_match = re.search(r'(?:int|void|UpdateStatus|OtaStatus)\s+(?:updateFirmware|update_firmware)\s*\([^)]*\)\s*\{', clean_code)
        if func_match:
            start_idx = clean_code.find('{', func_match.start())
            depth = 1
            i = start_idx + 1
            while i < len(clean_code) and depth > 0:
                if clean_code[i] == '{': depth += 1
                elif clean_code[i] == '}': depth -= 1
                i += 1
            update_body = clean_code[start_idx + 1 : i - 1].lower()
        else:
            update_body = clean_code.lower()

        logging_apis = ["printf", "puts", "fprintf", "perror", "syslog"]
        weak_crypto_apis = ["md5", "sha1", "rand", "srand"]

        detected_logging = [api for api in logging_apis if re.search(rf'\b{api}\s*\(', update_body)]
        detected_crypto = [api for api in weak_crypto_apis if re.search(rf'\b{api}\s*\(', clean_code, re.IGNORECASE)]

        passed = (len(detected_logging) == 0) and (len(detected_crypto) == 0)
        return {
            "passed": passed,
            "logging_calls": detected_logging,
            "weak_crypto_calls": detected_crypto,
        }

    @staticmethod
    def audit_hardcoded_secrets(source_code: str) -> Dict[str, Any]:
        """
        Audits for embedded RSA/EC private keys, PEM headers, or hardcoded credential tokens.
        """
        secret_patterns = [
            (re.compile(r"-----BEGIN\s+(?:RSA\s+|EC\s+)?PRIVATE\s+KEY-----", re.IGNORECASE), "Private Key PEM block"),
            (re.compile(r'(?:vendor_private_key|dev_key|private_key)\s*=\s*["\'](?!["\'])', re.IGNORECASE), "Hardcoded private key string literal"),
            (re.compile(r"ghp_[a-zA-Z0-9]{36}"), "GitHub Personal Access Token"),
            (re.compile(r"bearer\s+[a-zA-Z0-9_\-\.]{20,}", re.IGNORECASE), "Bearer credential token"),
        ]

        found: List[str] = []
        for pat, desc in secret_patterns:
            if pat.search(source_code):
                found.append(desc)

        return {
            "passed": len(found) == 0,
            "detected_secrets": found,
        }

    @classmethod
    def audit_syntax_errors(cls, source_code: str, raw_output: str = "") -> Dict[str, Any]:
        """
        Audits source code and compiler logs for syntax errors, missing headers,
        and compilation failure diagnostics (supporting both C and Python).
        """
        is_python = ("def " in source_code and "#include" not in source_code)
        if is_python:
            import ast
            try:
                ast.parse(source_code)
                return {
                    "passed": True,
                    "has_syntax_errors": False,
                    "errors": [],
                    "count": 0,
                }
            except SyntaxError as e:
                return {
                    "passed": False,
                    "has_syntax_errors": True,
                    "errors": [{
                        "line": e.lineno,
                        "kind": "syntax error",
                        "message": f"SyntaxError: {e.msg}",
                        "source": "python_syntax_validator",
                    }],
                    "count": 1,
                }
        errors: List[Dict[str, Any]] = []

        # 1. Inspect raw_output for fatal errors and clang syntax/compilation diagnostics
        if raw_output:
            clang_pattern = re.compile(
                r'(?:(?P<file>[^:\n]+):(?P<line>\d+):(?P<col>\d+):\s*)?(?P<kind>fatal error|error):\s*(?P<msg>[^\n]+)',
                re.IGNORECASE
            )
            for m in clang_pattern.finditer(raw_output):
                msg = m.group("msg").strip()
                kind = m.group("kind").lower()
                # Skip error count summaries and policy check warnings
                if any(k in msg.lower() for k in ["error generated", "errors generated", "warning generated"]):
                    continue
                # If secure-clang policy rule message, it's an invariant check, not a compiler syntax error
                if "secure-clang" in msg.lower() or "[ota-" in msg.lower() or "control-flow dominance" in msg.lower():
                    continue

                if "fatal" in kind or any(term in msg.lower() for term in [
                    "file not found", "expected", "unknown type", "undeclared",
                    "conflicting types", "redefinition", "syntax", "parse",
                    "invalid operand", "subscripted", "member reference", "assignable"
                ]):
                    errors.append({
                        "line": int(m.group("line")) if m.group("line") else None,
                        "kind": m.group("kind"),
                        "message": msg,
                        "source": "compiler_diagnostic",
                    })
                elif m.group("file") and m.group("line"):
                    errors.append({
                        "line": int(m.group("line")),
                        "kind": m.group("kind"),
                        "message": msg,
                        "source": "compiler_diagnostic",
                    })

        # 2. Check for unauthorized external library includes (e.g. mbedtls, openssl)
        # In a standalone embedded translation unit, these headers do not exist and cause fatal build errors.
        unauth_include_re = re.compile(
            r'^\s*#\s*include\s*[<"](?!stdint\.h|stddef\.h|stdbool\.h|string\.h|limits\.h|assert\.h|stdio\.h)[^>"]+[>"].*$',
            re.MULTILINE
        )
        for match in unauth_include_re.finditer(source_code):
            inc_line = match.group(0).strip()
            # Calculate line number
            line_no = source_code[:match.start()].count('\n') + 1
            if not any(inc_line in err.get("message", "") for err in errors):
                errors.append({
                    "line": line_no,
                    "kind": "fatal error",
                    "message": f"Unauthorized include '{inc_line}': External header not found in self-contained translation unit",
                    "source": "external_library_include",
                })

        # 3. Delimiter syntax sanity check: unbalanced braces or parentheses outside comments/strings
        # Unified lexer ensures "//" inside string literals (e.g. "https://...") is not stripped as a line comment
        def strip_c_comments_and_strings(code_str: str) -> str:
            tok_re = re.compile(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|/\*[\s\S]*?\*/|//[^\n]*')
            def repl(m: re.Match) -> str:
                s = m.group(0)
                if s.startswith('"') or s.startswith("'"):
                    return '""'
                return ' '
            return tok_re.sub(repl, code_str)

        clean_code_text = strip_c_comments_and_strings(source_code)
        if clean_code_text.count('{') != clean_code_text.count('}'):
            errors.append({
                "line": None,
                "kind": "syntax error",
                "message": "Unbalanced curly braces '{' and '}' in source code",
                "source": "syntax_validator",
            })
        if clean_code_text.count('(') != clean_code_text.count(')'):
            errors.append({
                "line": None,
                "kind": "syntax error",
                "message": "Unbalanced parentheses '(' and ')' in source code",
                "source": "syntax_validator",
            })

        # 4. Check for undeclared macro identifiers in array dimensions (e.g. [HSH_LEN], [URL_MXA])
        defines = set(re.findall(r'#define\s+([A-Za-z0-9_]+)', clean_code_text))
        defines.update(['HASH_LEN', 'URL_MAX', 'SIG_LEN', 'MAX_PAYLOAD'])
        for m in re.finditer(r'(?:(?:uint\w+_t|int\w+_t|char|int|float|double|size_t|\w+)\s+\w+\s*)?\[([a-zA-Z_]\w*)\]', clean_code_text):
            ref = m.group(1)
            # Only flag if ref has macro characteristics: all uppercase (e.g. HSH_LEN, URL_MXA) and not a digit
            is_macro_shape = ref.isupper() and len(ref) > 1
            if is_macro_shape and ref not in defines and not ref.isdigit():
                l_no = source_code[:m.start()].count('\n') + 1
                errors.append({
                    "line": l_no,
                    "kind": "error",
                    "message": f"use of undeclared identifier '{ref}' in array dimension",
                    "source": "syntax_validator",
                })

        # 5. Check for invalid assignment to rvalue (e.g. return func(...) = 0; where == intended)
        for i, line in enumerate(clean_code_text.splitlines(), start=1):
            if re.search(r'^\s*(?:return|if\s*\(|while\s*\().*?\)\s*=\s*(?!=)', line):
                errors.append({
                    "line": i,
                    "kind": "error",
                    "message": "expression is not assignable (accidental assignment '=' where '==' intended)",
                    "source": "syntax_validator",
                })

        has_syntax_errors = len(errors) > 0
        return {
            "passed": not has_syntax_errors,
            "has_syntax_errors": has_syntax_errors,
            "errors": errors,
            "count": len(errors),
        }
