"""
security_patcher.py — Automated High-Precision Security Patch Generator for C/C++.
==================================================================================
Generates precise, compilable line-level remediations for detected security
vulnerabilities (CWE-121, CWE-120, CWE-134, CWE-208, CWE-798, CWE-476, etc.)
so that the Optimization Agent can surface actionable security fixes with diffs
and Accept/Undo actions in the Optimization tab.
"""

from __future__ import annotations

import difflib
import re
from typing import Any, Dict, List, Optional, Tuple


class SecurityPatcher:
    """
    Applies deterministic, secure coding fixes for common C/C++ vulnerabilities.
    """

    @classmethod
    def patch_code(
        cls,
        source_code: str,
        vulnerabilities: Optional[List[Dict[str, Any]]] = None,
        file_path: str = "<source>",
    ) -> Tuple[str, List[Dict[str, Any]], str]:
        """
        Produce patched source code, transformation records, and unified diff.

        Returns:
            (patched_code, transformations, unified_diff)
        """
        if not source_code:
            return source_code, [], ""

        if isinstance(vulnerabilities, str):
            file_path = vulnerabilities
            vulnerabilities = None

        if vulnerabilities is None:
            try:
                from rules_and_scanners.security_rules import scan_security_rules
            except ImportError:
                try:
                    from src.analysis.security_rules import scan_security_rules
                except ImportError:
                    from security_rules import scan_security_rules
            try:
                vulnerabilities = scan_security_rules(source_code, file_path)
            except Exception:
                vulnerabilities = []

        if not vulnerabilities:
            return source_code, [], ""

        lines = source_code.splitlines()
        transformations: List[Dict[str, Any]] = []

        # Sort vulnerabilities by line number descending so modifying later lines
        # doesn't alter line offsets of earlier lines if multi-line insertions occur.
        # But we can also index lines 0-based.
        vulns_by_line: Dict[int, List[Dict[str, Any]]] = {}
        for v in vulnerabilities:
            l = v.get("line")
            if l is not None and 1 <= l <= len(lines):
                vulns_by_line.setdefault(l, []).append(v)

        # Work on a copy of lines
        patched_lines = list(lines)
        applied_lines: set[int] = set()

        for line_no in sorted(vulns_by_line.keys(), reverse=True):
            orig_idx = line_no - 1
            orig_line = patched_lines[orig_idx]
            vulns = vulns_by_line[line_no]

            # Try patching the line for the highest priority vulnerability on this line
            patched = False
            for v in vulns:
                vtype = str(v.get("type", "")).lower()
                cwe = str(v.get("cwe_id", "")).upper()
                desc = v.get("description", "")
                rec = v.get("recommendation", "")

                new_line, fix_desc = cls._patch_line(orig_line, vtype, cwe, desc, rec)
                if new_line is not None and new_line != orig_line:
                    patched_lines[orig_idx] = new_line
                    applied_lines.add(line_no)
                    transformations.append({
                        "type": "security_fix",
                        "severity": v.get("severity", "high"),
                        "cwe_id": cwe or v.get("cwe_id"),
                        "line": line_no,
                        "description": f"Security Fix [Line {line_no}]: {fix_desc}",
                        "original_line": orig_line.strip(),
                        "replacement_line": new_line.strip(),
                        "related_finding": v.get("id") or vtype,
                    })
                    patched = True
                    break

        if not transformations:
            return source_code, [], ""

        # Re-sort transformations ascending by line number for clean UI display
        transformations.sort(key=lambda t: t.get("line") or 0)

        # Assemble patched code
        newline_char = "\r\n" if "\r\n" in source_code else "\n"
        patched_code = newline_char.join(patched_lines)
        if source_code.endswith("\n") or source_code.endswith("\r\n"):
            patched_code += newline_char

        # Build unified diff
        diff_lines = list(difflib.unified_diff(
            source_code.splitlines(keepends=True),
            patched_code.splitlines(keepends=True),
            fromfile=f"a/{file_path}",
            tofile=f"b/{file_path} (security_hardened)",
            n=2,
        ))
        diff = "".join(diff_lines)

        return patched_code, transformations, diff

    @classmethod
    def _patch_line(
        cls,
        line: str,
        vtype: str,
        cwe: str,
        desc: str,
        rec: str,
    ) -> Tuple[Optional[str], str]:
        """
        Attempts to generate a safe replacement for a single line of code.
        """
        indent = line[: len(line) - len(line.lstrip())]
        stripped = line.strip()

        # ── 1. Format String Bug (CWE-134) ────────────────────────────────────
        # printf(s) -> printf("%s", s)
        m_printf = re.search(r'\bprintf\s*\(\s*([a-zA-Z0-9_]+(\[[^\]]+\]|\->[a-zA-Z0-9_]+|\.[a-zA-Z0-9_]+)?)\s*\)', stripped)
        if m_printf and not m_printf.group(1).startswith('"') and ("format" in vtype or cwe == "CWE-134"):
            arg = m_printf.group(1)
            patched = re.sub(
                r'\bprintf\s*\(\s*' + re.escape(arg) + r'\s*\)',
                f'printf("%s", {arg})',
                stripped,
                count=1,
            )
            return f"{indent}{patched}", f"Use string literal format specifier: printf(\"%s\", {arg})"

        # fprintf(fp, s) -> fprintf(fp, "%s", s)
        m_fprintf = re.search(r'\bfprintf\s*\(\s*([^,]+)\s*,\s*([a-zA-Z0-9_]+(\[[^\]]+\]|\->[a-zA-Z0-9_]+|\.[a-zA-Z0-9_]+)?)\s*\)', stripped)
        if m_fprintf and not m_fprintf.group(2).startswith('"') and ("format" in vtype or cwe == "CWE-134"):
            fp, arg = m_fprintf.group(1), m_fprintf.group(2)
            patched = re.sub(
                r'\bfprintf\s*\(\s*' + re.escape(fp) + r'\s*,\s*' + re.escape(arg) + r'\s*\)',
                f'fprintf({fp}, "%s", {arg})',
                stripped,
                count=1,
            )
            return f"{indent}{patched}", f"Use string literal format specifier: fprintf({fp}, \"%s\", {arg})"

        # ── 2. Unsafe sprintf -> snprintf (CWE-121, CWE-120) ──────────────────
        m_sprintf = re.search(r'\bsprintf\s*\(\s*([a-zA-Z0-9_]+)\s*,\s*(.+)\)', stripped)
        if m_sprintf and ("sprintf" in vtype or "buffer" in vtype or cwe in ("CWE-120", "CWE-121")):
            dest = m_sprintf.group(1)
            rest = m_sprintf.group(2)
            # If rest is a non-literal variable e.g. sprintf(buf, user)
            if not rest.strip().startswith('"'):
                patched = f"snprintf({dest}, sizeof({dest}), \"%s\", {rest});"
            else:
                patched = f"snprintf({dest}, sizeof({dest}), {rest});"
            return f"{indent}{patched}", f"Replace unbounded sprintf with bounded snprintf({dest}, sizeof({dest}), ...)"

        # ── 3. Unsafe strcpy -> strncpy with null-termination (CWE-121, CWE-120)
        m_strcpy = re.search(r'\bstrcpy\s*\(\s*([a-zA-Z0-9_]+)\s*,\s*([^)]+)\)', stripped)
        if m_strcpy and ("strcpy" in vtype or "overflow" in vtype or cwe in ("CWE-120", "CWE-121")):
            dest = m_strcpy.group(1)
            src = m_strcpy.group(2)
            patched = f"strncpy({dest}, {src}, sizeof({dest}) - 1); {dest}[sizeof({dest}) - 1] = '\\0';"
            return f"{indent}{patched}", f"Replace unsafe strcpy with bounded strncpy({dest}, {src}, sizeof({dest}) - 1) and explicit null termination"

        # ── 4. Unsafe strcat -> strncat (CWE-121, CWE-120) ────────────────────
        m_strcat = re.search(r'\bstrcat\s*\(\s*([a-zA-Z0-9_]+)\s*,\s*([^)]+)\)', stripped)
        if m_strcat and ("strcat" in vtype or cwe in ("CWE-120", "CWE-121")):
            dest = m_strcat.group(1)
            src = m_strcat.group(2)
            patched = f"strncat({dest}, {src}, sizeof({dest}) - strlen({dest}) - 1);"
            return f"{indent}{patched}", f"Replace unsafe strcat with bounded strncat on {dest}"

        # ── 5. Unsafe gets -> fgets (CWE-242) ─────────────────────────────────
        m_gets = re.search(r'\bgets\s*\(\s*([a-zA-Z0-9_]+)\s*\)', stripped)
        if m_gets and ("gets" in vtype or cwe == "CWE-242"):
            buf = m_gets.group(1)
            patched = f"fgets({buf}, sizeof({buf}), stdin);"
            return f"{indent}{patched}", f"Replace inherently unsafe gets({buf}) with fgets({buf}, sizeof({buf}), stdin)"

        # ── 6. Timing Side Channel strcmp -> Constant-time compare (CWE-208) ───
        # e.g.: return strcmp(pw, SECRET) == 0;
        m_strcmp = re.search(r'strcmp\s*\(\s*([^,]+)\s*,\s*([^)]+)\s*\)\s*==\s*0', stripped)
        if m_strcmp and ("timing" in vtype or "side_channel" in vtype or cwe == "CWE-208"):
            arg1 = m_strcmp.group(1).strip()
            arg2 = m_strcmp.group(2).strip()
            patched = re.sub(
                r'strcmp\s*\(\s*' + re.escape(arg1) + r'\s*,\s*' + re.escape(arg2) + r'\s*\)\s*==\s*0',
                f'([&]() {{ int d = 0; size_t i = 0; for (; {arg1}[i] && {arg2}[i]; ++i) d |= ({arg1}[i] ^ {arg2}[i]); return (d == 0 && {arg1}[i] == {arg2}[i]); }}())',
                stripped,
                count=1,
            )
            return f"{indent}{patched}", f"Replace non-constant-time strcmp with constant-time equality compare to eliminate CWE-208 timing leak"

        # ── 7. Hardcoded Secrets & Passwords (CWE-798, CWE-1392) ──────────────
        m_secret = re.search(r'const\s+char\*\s+([A-Za-z0-9_]+)\s*=\s*"([^"]+)";', stripped)
        if m_secret and any(k in vtype or k in desc.lower() for k in ("secret", "password", "hardcoded", "credential")) or cwe in ("CWE-798", "CWE-1392"):
            var_name = m_secret.group(1)
            patched = f'const char* {var_name} = std::getenv("{var_name}") ? std::getenv("{var_name}") : "REDACTED";  // Hardcoded secret removed'
            return f"{indent}{patched}", f"Externalize hardcoded credential {var_name} to secure environment variable lookup"

        # ── 8. Mismatched deallocation (new[] with delete) (CWE-762) ──────────
        m_del = re.search(r'\bdelete\s+([a-zA-Z0-9_]+)\s*;', stripped)
        if m_del and ("new_delete" in vtype or "mismatch" in vtype or cwe == "CWE-762"):
            var = m_del.group(1)
            patched = f"delete[] {var};"
            return f"{indent}{patched}", f"Use delete[] {var} for array allocation (CWE-762 fix)"

        # ── 9. Off-by-one loop write <= sizeof (CWE-193, CWE-787) ─────────────
        m_off = re.search(r'for\s*\(\s*(int|size_t)\s+([a-zA-Z0-9_]+)\s*=\s*0\s*;\s*\2\s*<=\s*([a-zA-Z0-9_]+)\s*;', stripped)
        if m_off and ("off_by_one" in vtype or "out_of_bounds" in vtype or cwe in ("CWE-193", "CWE-787")):
            t_type, var, limit = m_off.group(1), m_off.group(2), m_off.group(3)
            patched = stripped.replace(f"{var} <= {limit}", f"{var} < {limit}", 1)
            return f"{indent}{patched}", f"Correct off-by-one loop condition: {var} < {limit}"

        # ── 10. Insecure Randomness rand() (CWE-338) ──────────────────────────
        if "rand()" in stripped and ("prng" in vtype or "random" in vtype or cwe == "CWE-338"):
            patched = stripped.replace("rand()", "((int)(std::random_device{}() & 0x7FFFFFFF))")
            return f"{indent}{patched}", "Replace predictable rand() with cryptographic std::random_device"

        # ── 11. Overly permissive file permissions (CWE-732) ──────────────────
        if any(p in stripped for p in ("0666", "0777")) and ("permission" in vtype or cwe == "CWE-732"):
            patched = stripped.replace("0666", "0600").replace("0777", "0700")
            return f"{indent}{patched}", "Restrict file permissions from world-writable to owner-only (0600)"

        # ── 12. Password written to log output (CWE-532) ───────────────────────
        if any(k in stripped.lower() for k in ("password", "secret", "token")) and ("log" in vtype or cwe == "CWE-532"):
            # If printing password
            m_log = re.search(r'(std::cout|printf|fprintf|syslog)\s*\(.*?\b([a-zA-Z0-9_]*password[a-zA-Z0-9_]*)\b.*?\)', stripped, re.IGNORECASE)
            if m_log:
                pw_var = m_log.group(2)
                patched = stripped.replace(pw_var, '"[REDACTED]"')
                return f"{indent}{patched}", f"Redact sensitive variable '{pw_var}' in log/console output"

        # ── 13. Double free protection (CWE-415) ──────────────────────────────
        m_free = re.search(r'\bfree\s*\(\s*([a-zA-Z0-9_]+)\s*\);', stripped)
        if m_free and ("double_free" in vtype or "doublefree" in vtype or cwe == "CWE-415"):
            ptr = m_free.group(1)
            patched = f"if ({ptr}) {{ free({ptr}); {ptr} = NULL; }}"
            return f"{indent}{patched}", f"Set pointer {ptr} to NULL after free to prevent double-free"

        # ── 14. Uncontrolled Recursion base-case check (CWE-674) ──────────────
        if ("recursion" in vtype or cwe == "CWE-674") and "if" not in stripped:
            patched = f"if (depth > 1000) return 0;\n{line}"
            return f"{patched}", "Add stack exhaustion guard / depth limit for recursive call"

        # ── 15. Python Dangerous eval -> ast.literal_eval (CWE-94) ───────────
        if "eval(" in stripped and ("eval" in vtype or cwe == "CWE-94"):
            patched = re.sub(r'\beval\s*\(', 'ast.literal_eval(', stripped)
            return f"{indent}{patched}", "Replace unsafe eval() with ast.literal_eval() for safe literal evaluation"

        # ── 16. Python / Java Insecure MD5 Hash -> SHA-256 (CWE-328) ──────────
        if "hashlib.md5(" in stripped and ("md5" in vtype or cwe == "CWE-328"):
            patched = stripped.replace("hashlib.md5(", "hashlib.sha256(")
            return f"{indent}{patched}", "Upgrade broken MD5 hash to cryptographically secure SHA-256 (hashlib.sha256)"

        if 'MessageDigest.getInstance("MD5")' in stripped or "MessageDigest.getInstance('MD5')" in stripped:
            patched = stripped.replace('"MD5"', '"SHA-256"').replace("'MD5'", "'SHA-256'")
            return f"{indent}{patched}", "Upgrade Java MessageDigest from MD5 to secure SHA-256"

        # ── 17. Python Insecure Temporary File mktemp -> NamedTemporaryFile (CWE-377)
        if "tempfile.mktemp(" in stripped and ("mktemp" in vtype or cwe == "CWE-377"):
            patched = stripped.replace("tempfile.mktemp()", "tempfile.NamedTemporaryFile().name")
            return f"{indent}{patched}", "Replace insecure tempfile.mktemp() with safe NamedTemporaryFile()"

        # ── 18. Python / Java TLS Verification Disabled (CWE-295) ─────────────
        if "verify=False" in stripped and ("tls" in vtype or "cert" in vtype or cwe == "CWE-295"):
            patched = stripped.replace("verify=False", "verify=True")
            return f"{indent}{patched}", "Enable strict TLS certificate validation (verify=True)"

        # ── 19. Python Flask debug=True in Production (CWE-489) ───────────────
        if "debug=True" in stripped and ("debug" in vtype or cwe == "CWE-489"):
            patched = stripped.replace("debug=True", "debug=False")
            return f"{indent}{patched}", "Disable interactive debug mode for production deployment (debug=False)"

        # ── 20. Java Insecure PRNG Random -> SecureRandom (CWE-338) ───────────
        if "new Random()" in stripped and ("random" in vtype or "prng" in vtype or cwe == "CWE-338"):
            patched = stripped.replace("new Random()", "new java.security.SecureRandom()")
            return f"{indent}{patched}", "Replace predictable java.util.Random with cryptographic SecureRandom"

        return None, ""
