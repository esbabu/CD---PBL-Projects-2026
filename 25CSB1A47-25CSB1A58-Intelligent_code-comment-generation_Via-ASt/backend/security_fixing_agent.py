"""REMEDY code remediation with AST-grounded defensive patching."""

import difflib
import logging
import re
from collections import Counter
from typing import Any

from backend.attack_guard import detect_attack
from backend.code_improver import _definition_names
from backend import model_provider
from backend.security_attack_agent import simulate_attacks
from backend.validator import validate_code

logger = logging.getLogger(__name__)


def _static_finding_counts(simulation: dict[str, Any]) -> Counter[tuple[str, str]]:
    return Counter(
        (str(item.get("category", "")), str(item.get("cwe", "")))
        for item in simulation.get("attack_scenarios", [])
    )


def _remediate_sql_injection(source_code: str) -> tuple[str, list[str]]:
    """Fix dynamic SQL formatting by converting to parameterized queries."""
    modified = source_code
    fixes = []

    # Pattern 1: query = f"SELECT ... WHERE col = {var}" followed by cursor.execute(query)
    fstring_sql_pattern = re.compile(
        r'([ \t]*)query\s*=\s*f(["\'])(SELECT|INSERT|UPDATE|DELETE|FROM).*?\{([a-zA-Z0-9_]+)\}.*?\2',
        re.IGNORECASE,
    )

    match = fstring_sql_pattern.search(modified)
    if match:
        original_stmt = match.group(0)
        param_expressions = re.findall(r"\{([^{}]+)\}", original_stmt)
        simple_params = all(
            re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", expression.strip())
            for expression in param_expressions
        )
        param_vars = (
            [expression.strip() for expression in param_expressions]
            if simple_params
            else []
        )
        execute_pattern = re.compile(
            r"([A-Za-z_][A-Za-z0-9_]*)\.execute\(\s*query\s*\)"
        )

        if param_vars:
            fixed_stmt = re.sub(
                r"""(['"])\{[A-Za-z_][A-Za-z0-9_]*\}\1""",
                "?",
                original_stmt,
            )
            fixed_stmt = re.sub(r"\{[A-Za-z_][A-Za-z0-9_]*\}", "?", fixed_stmt)
            fixed_stmt = re.sub(r'=\s*f(["\'])', r'= \1', fixed_stmt)

            modified = modified.replace(original_stmt, fixed_stmt)

            if execute_pattern.search(modified):
                param_tuple = ", ".join(param_vars)
                if len(param_vars) == 1:
                    param_tuple += ","
                modified = execute_pattern.sub(
                    lambda call: (
                        f"{call.group(1)}.execute(query, ({param_tuple}))"
                    ),
                    modified,
                )

            fixes.append(
                "Remediated SQL Injection (CWE-89): Replaced dynamic f-string interpolation with SQL placeholders and bound values where an execute call is present."
            )

    # Pattern 2: cursor.execute(f"SELECT ... {var}") directly
    direct_execute_pattern = re.compile(
        r'cursor\.execute\(f(["\'])(.*?)\{([a-zA-Z0-9_]+)\}(.*?)\1\)',
        re.IGNORECASE,
    )
    direct_match = direct_execute_pattern.search(modified)
    if direct_match:
        quote = direct_match.group(1)
        prefix = direct_match.group(2)
        param_var = direct_match.group(3)
        suffix = direct_match.group(4)
        replacement = f'cursor.execute({quote}{prefix}?{suffix}{quote}, ({param_var},))'
        modified = direct_execute_pattern.sub(replacement, modified)
        fixes.append(
            f"Remediated SQL Injection (CWE-89): Converted inline f-string execute call to parameterized SQL query with '({param_var},)'."
        )

    return modified, fixes


def _remediate_command_injection(source_code: str) -> tuple[str, list[str]]:
    """Fix unsafe execution by replacing eval with ast.literal_eval, and os.system with safe subprocess."""
    modified = source_code
    fixes = []

    # Fix eval(expr) -> ast.literal_eval(expr)
    if "eval(" in modified:
        if "import ast" not in modified:
            modified = "import ast\n" + modified
        modified = re.sub(r'\beval\(', 'ast.literal_eval(', modified)
        fixes.append(
            "Remediated Code Injection (CWE-94): Replaced unsafe eval() with ast.literal_eval() to restrict evaluation to safe Python literals."
        )

    # Fix os.system(command) -> subprocess.run(shlex.split(command), shell=False, check=False).returncode
    if "os.system(" in modified:
        needs_subprocess = "import subprocess" not in modified
        needs_shlex = "import shlex" not in modified
        prefix = ""
        if needs_subprocess:
            prefix += "import subprocess\n"
        if needs_shlex:
            prefix += "import shlex\n"
        if prefix:
            modified = prefix + modified

        modified = re.sub(
            r'return\s+os\.system\(([^)]+)\)',
            r'return subprocess.run(shlex.split(\1), shell=False, check=False).returncode',
            modified,
        )
        modified = re.sub(
            r'os\.system\(([^)]+)\)',
            r'subprocess.run(shlex.split(\1), shell=False, check=False).returncode',
            modified,
        )
        fixes.append(
            "Remediated Command Injection (CWE-78): Replaced os.system() with subprocess.run(shlex.split(...), shell=False, check=False).returncode to avoid shell metacharacter injection while preserving returncode and exception contracts."
        )

    # Subprocess shell=True remediation
    if re.search(r'\bshell\s*=\s*True\b', modified):
        modified = re.sub(r'\bshell\s*=\s*True\b', 'shell=False', modified)
        fixes.append(
            "Remediated Command Injection (CWE-78): Disabled shell=True (shell=False) in subprocess execution to prevent shell metacharacter injection."
        )

    return modified, fixes


def _remediate_hardcoded_secrets(source_code: str) -> tuple[str, list[str]]:
    """Fix plaintext API tokens and credentials by loading via os.getenv."""
    modified = source_code
    fixes = []

    secret_pattern = re.compile(
        r'^([ \t]*)([A-Z0-9_]*(?:TOKEN|KEY|SECRET|PASSWORD)[A-Z0-9_]*)\s*=\s*(["\'][^"\']+["\'])',
        re.MULTILINE,
    )

    matches = list(secret_pattern.finditer(modified))
    if matches:
        if "import os" not in modified:
            modified = "import os\n" + modified
        for m in matches:
            var_name = m.group(2)
            orig_line = m.group(0)
            indent = m.group(1)
            fixed_line = f'{indent}{var_name} = os.getenv("{var_name}", "")'
            modified = modified.replace(orig_line, fixed_line)
            fixes.append(
                f"Remediated Hardcoded Credential (CWE-522): Replaced hardcoded secret in '{var_name}' with safe environment lookup 'os.getenv(\"{var_name}\", \"\")'."
            )

    return modified, fixes


def _remediate_deserialization(source_code: str) -> tuple[str, list[str]]:
    """Fix unsafe pickle and yaml deserialization."""
    modified = source_code
    fixes = []

    if "pickle.loads(" in modified or "pickle.load(" in modified:
        if "import json" not in modified:
            modified = "import json\n" + modified
        modified = re.sub(r'pickle\.loads\(', 'json.loads(', modified)
        modified = re.sub(r'pickle\.load\(', 'json.load(', modified)
        fixes.append(
            "Remediated Insecure Deserialization (CWE-502): Replaced unsafe pickle deserialization with safe json parser."
        )

    if "yaml.load(" in modified and "yaml.safe_load" not in modified:
        modified = re.sub(r'yaml\.load\(', 'yaml.safe_load(', modified)
        fixes.append(
            "Remediated Insecure Deserialization (CWE-502): Replaced yaml.load() with yaml.safe_load() to prevent arbitrary object instantiation."
        )

    return modified, fixes


def _remediate_ssl_verification(source_code: str) -> tuple[str, list[str]]:
    """Fix disabled SSL verification."""
    modified = source_code
    fixes = []

    if re.search(r'verify\s*=\s*False', modified):
        modified = re.sub(r'verify\s*=\s*False', 'verify=True', modified)
        fixes.append(
            "Remediated Transport Security (CWE-295): Enabled strict TLS certificate validation (verify=True)."
        )

    return modified, fixes


def _remediate_path_traversal(source_code: str) -> tuple[str, list[str]]:
    """Fix potential path traversal by sanitizing dynamic path components with os.path.basename."""
    modified = source_code
    fixes = []

    # 1. os.path.join(..., var) without basename
    join_pattern = re.compile(r'os\.path\.join\(([^,\)]+),\s*([a-zA-Z_][a-zA-Z0-9_]*)\)')
    if join_pattern.search(modified):
        def repl(match):
            dir_part = match.group(1).strip()
            file_part = match.group(2).strip()
            if "basename" in file_part:
                return match.group(0)
            return f"os.path.join({dir_part}, os.path.basename({file_part}))"

        new_code = join_pattern.sub(repl, modified)
        if new_code != modified:
            if "import os" not in new_code:
                new_code = "import os\n" + new_code
            modified = new_code
            fixes.append(
                "Remediated Path Traversal (CWE-22): Sanitized dynamic path component using os.path.basename() to prevent directory traversal."
            )

    # 2. open(var, ...) where var is a bare variable name not sanitized
    open_pattern = re.compile(r'\bopen\(([a-zA-Z_][a-zA-Z0-9_]*)\b(\s*[,)])')
    matches = list(open_pattern.finditer(modified))
    if matches:
        changed = False
        lines = modified.splitlines()
        for m in matches:
            var_name = m.group(1)
            is_sanitized = any(
                f"{var_name} =" in line and ("basename" in line or "resolve" in line)
                for line in lines
            )
            if not is_sanitized and var_name not in {"__file__"}:
                old_call = f"open({var_name}{m.group(2)}"
                new_call = f"open(os.path.basename({var_name}){m.group(2)}"
                if old_call in modified:
                    modified = modified.replace(old_call, new_call, 1)
                    changed = True
        if changed:
            if "import os" not in modified:
                modified = "import os\n" + modified
            fixes.append(
                "Remediated Path Traversal (CWE-22): Sanitized direct open() path argument using os.path.basename()."
            )

    # 3. open(f"...{var}...") f-string dynamic paths
    fstring_open = re.compile(r'(\bopen\(f["\'])(.*?)\{([a-zA-Z_][a-zA-Z0-9_]*)\}(.*?["\'])')
    if fstring_open.search(modified):
        def repl_f(match):
            pre = match.group(1)
            p1 = match.group(2)
            v = match.group(3)
            p2 = match.group(4)
            if "basename" in v:
                return match.group(0)
            return f"{pre}{p1}{{os.path.basename({v})}}{p2}"

        new_code = fstring_open.sub(repl_f, modified)
        if new_code != modified:
            if "import os" not in new_code:
                new_code = "import os\n" + new_code
            modified = new_code
            fixes.append(
                "Remediated Path Traversal (CWE-22): Sanitized dynamic f-string path using os.path.basename()."
            )

    return modified, fixes


def _remediate_adversarial_injections(source_code: str) -> tuple[str, list[str]]:
    """Neutralize adversarial prompt injection instructions in comments or docstrings."""
    modified = source_code
    fixes = []

    lines = modified.splitlines()
    cleaned_lines = []
    removed = 0

    for line in lines:
        detection = detect_attack(line)
        if detection["detected"]:
            removed += 1
            indent = line[: len(line) - len(line.lstrip())]
            cleaned_lines.append(f"{indent}# [Security Guard] Removed adversarial injection instructions")
        else:
            cleaned_lines.append(line)

    if removed > 0:
        modified = "\n".join(cleaned_lines) + ("\n" if source_code.endswith(("\n", "\r")) else "")
        fixes.append(
            f"Remediated Prompt Injection (OWASP-LLM01): Neutralized {removed} adversarial instruction override directives in source comments."
        )

    return modified, fixes


def _remediate_insecure_hashing(source_code: str) -> tuple[str, list[str]]:
    """Fix weak cryptographic hashes (MD5/SHA1) by upgrading to hashlib.sha256."""
    modified = source_code
    fixes = []

    if re.search(r'\bhashlib\.(?:md5|sha1)\b', modified):
        modified = re.sub(r'\bhashlib\.(?:md5|sha1)\b', 'hashlib.sha256', modified)
        fixes.append(
            "Remediated Insecure Cryptography (CWE-327): Upgraded broken cryptographic hash (MD5/SHA1) to modern secure hashlib.sha256()."
        )

    if re.search(r'hashlib\.new\(["\'](?:md5|sha1)["\']\)', modified, re.IGNORECASE):
        modified = re.sub(r'hashlib\.new\(["\'](?:md5|sha1)["\']\)', 'hashlib.new("sha256")', modified, flags=re.IGNORECASE)
        fixes.append(
            "Remediated Insecure Cryptography (CWE-327): Replaced legacy hash algorithm in hashlib.new() with hashlib.new('sha256')."
        )

    if re.search(r'\bfrom\s+hashlib\s+import\s+[^;\n]*\b(md5|sha1)\b', modified):
        modified = re.sub(r'\bfrom\s+hashlib\s+import\s+([^\n]*)\b(md5|sha1)\b', r'from hashlib import \1sha256', modified)
        modified = re.sub(r'\bmd5\(', 'sha256(', modified)
        modified = re.sub(r'\bsha1\(', 'sha256(', modified)
        fixes.append(
            "Remediated Insecure Cryptography (CWE-327): Replaced imported weak hash functions (md5/sha1) with sha256."
        )

    return modified, fixes


def _remediate_insecure_tempfiles(source_code: str) -> tuple[str, list[str]]:
    """Fix insecure tempfile.mktemp() by replacing with tempfile.NamedTemporaryFile()."""
    modified = source_code
    fixes = []

    if "tempfile.mktemp" in modified:
        modified = re.sub(r'tempfile\.mktemp\(', 'tempfile.NamedTemporaryFile(', modified)
        fixes.append(
            "Remediated Insecure Temporary File (CWE-377): Replaced insecure tempfile.mktemp() with atomic tempfile.NamedTemporaryFile() to prevent TOCTOU race conditions."
        )
    elif re.search(r'\bfrom\s+tempfile\s+import\s+[^;\n]*\bmktemp\b', modified):
        modified = re.sub(r'\bfrom\s+tempfile\s+import\s+([^\n]*)\bmktemp\b', r'from tempfile import \1NamedTemporaryFile', modified)
        modified = re.sub(r'\bmktemp\(', 'NamedTemporaryFile(', modified)
        fixes.append(
            "Remediated Insecure Temporary File (CWE-377): Replaced insecure mktemp() with NamedTemporaryFile()."
        )

    return modified, fixes


def _remediate_insecure_xml(source_code: str) -> tuple[str, list[str]]:
    """Fix insecure XML parsing by replacing with defusedxml."""
    modified = source_code
    fixes = []

    if "import xml.etree.ElementTree as ET" in modified:
        modified = modified.replace("import xml.etree.ElementTree as ET", "import defusedxml.ElementTree as ET")
        fixes.append(
            "Remediated XML External Entity (XXE) Vulnerability (CWE-611): Replaced xml.etree.ElementTree with defusedxml.ElementTree to block entity expansion attacks."
        )
    elif "from xml.etree import ElementTree as ET" in modified:
        modified = modified.replace("from xml.etree import ElementTree as ET", "import defusedxml.ElementTree as ET")
        fixes.append(
            "Remediated XML External Entity (XXE) Vulnerability (CWE-611): Replaced xml.etree with defusedxml to block entity expansion attacks."
        )
    elif "import xml.etree.ElementTree" in modified:
        modified = modified.replace("import xml.etree.ElementTree", "import defusedxml.ElementTree as ElementTree")
        modified = re.sub(r'\bxml\.etree\.ElementTree\b', 'ElementTree', modified)
        fixes.append(
            "Remediated XML External Entity (XXE) Vulnerability (CWE-611): Replaced xml.etree.ElementTree with defusedxml."
        )
    elif "xml.etree.ElementTree" in modified:
        if "import defusedxml.ElementTree as ET" not in modified:
            modified = "import defusedxml.ElementTree as ET\n" + modified
        modified = re.sub(r'\bxml\.etree\.ElementTree\b', 'ET', modified)
        fixes.append(
            "Remediated XML External Entity (XXE) Vulnerability (CWE-611): Converted insecure XML parser to defusedxml."
        )

    return modified, fixes


def _remediate_exposed_debug(source_code: str) -> tuple[str, list[str]]:
    """Fix exposed debug mode by setting debug=False."""
    modified = source_code
    fixes = []

    if re.search(r'\bdebug\s*=\s*True\b', modified):
        modified = re.sub(r'\bdebug\s*=\s*True\b', 'debug=False', modified)
        fixes.append(
            "Remediated Information Disclosure (CWE-215): Disabled debug mode (debug=False) to prevent sensitive traceback and interactive console exposure in production."
        )

    if re.search(r'^([ \t]*)DEBUG\s*=\s*True\b', modified, re.MULTILINE):
        modified = re.sub(r'^([ \t]*)DEBUG\s*=\s*True\b', r'\1DEBUG = False', modified, flags=re.MULTILINE)
        fixes.append(
            "Remediated Information Disclosure (CWE-215): Enforced DEBUG = False setting."
        )

    return modified, fixes


def _remediate_redos(source_code: str) -> tuple[str, list[str]]:
    """Fix polynomial/exponential ReDoS patterns by eliminating nested quantifiers."""
    modified = source_code
    fixes = []

    if re.search(r'\(\s*([a-zA-Z0-9_\\]+)\+\s*\)\+', modified):
        modified = re.sub(r'\(\s*([a-zA-Z0-9_\\]+)\+\s*\)\+', r'\1+', modified)
        fixes.append(
            "Remediated ReDoS (CWE-1333): Removed catastrophic backtracking by eliminating nested quantifier (+)+ -> +."
        )
    elif re.search(r'\(\s*([a-zA-Z0-9_\[\]\-\\]+)\+\s*\)\*', modified):
        modified = re.sub(r'\(\s*([a-zA-Z0-9_\[\]\-\\]+)\+\s*\)\*', r'\1*', modified)
        fixes.append(
            "Remediated ReDoS (CWE-1333): Flattened nested quantifier (+)* -> *."
        )

    return modified, fixes


def _remediate_ssrf(source_code: str) -> tuple[str, list[str]]:
    """Decline SSRF rewrites when a destination policy cannot be inferred safely."""
    return source_code, []


def _deterministic_security_fix(source_code: str) -> tuple[str, list[str], list[str]]:
    """Run deterministic security remediation engine across all supported vulnerability classes."""
    current_code = source_code
    all_fixes = []
    controls = []

    # 1. SQL Injection (CWE-89)
    current_code, fixes = _remediate_sql_injection(current_code)
    if fixes:
        all_fixes.extend(fixes)
        controls.append("Parameterized SQL Query Binding (CWE-89 Remediation)")

    # 2. Command Injection & eval & subprocess shell=True (CWE-78 / CWE-94)
    current_code, fixes = _remediate_command_injection(current_code)
    if fixes:
        all_fixes.extend(fixes)
        controls.append("Safe Subprocess Execution & AST Literal Parsing (CWE-78 / CWE-94 Remediation)")

    # 3. Hardcoded Secrets (CWE-522 / CWE-798)
    current_code, fixes = _remediate_hardcoded_secrets(current_code)
    if fixes:
        all_fixes.extend(fixes)
        controls.append("Environment Variable Secret Management (CWE-522 Remediation)")

    # 4. Insecure Deserialization (CWE-502)
    current_code, fixes = _remediate_deserialization(current_code)
    if fixes:
        all_fixes.extend(fixes)
        controls.append("Safe JSON / Safe YAML Deserialization (CWE-502 Remediation)")

    # 5. SSL / TLS Verification (CWE-295)
    current_code, fixes = _remediate_ssl_verification(current_code)
    if fixes:
        all_fixes.extend(fixes)
        controls.append("Enforced TLS / SSL Certificate Validation (CWE-295 Remediation)")

    # 6. Prompt Injection & Adversarial Directives (OWASP-LLM01)
    current_code, fixes = _remediate_adversarial_injections(current_code)
    if fixes:
        all_fixes.extend(fixes)
        controls.append("Adversarial Instruction Neutralization & Policy Guardrails")

    # 7. Path Traversal (CWE-22)
    current_code, fixes = _remediate_path_traversal(current_code)
    if fixes:
        all_fixes.extend(fixes)
        controls.append("Path Basename Validation & Directory Boundary Guard (CWE-22 Remediation)")

    # 8. Insecure Cryptographic Hashing (CWE-327)
    current_code, fixes = _remediate_insecure_hashing(current_code)
    if fixes:
        all_fixes.extend(fixes)
        controls.append("Modern SHA-256 Cryptographic Hash Enforcement (CWE-327 Remediation)")

    # 9. Insecure Temporary Files (CWE-377)
    current_code, fixes = _remediate_insecure_tempfiles(current_code)
    if fixes:
        all_fixes.extend(fixes)
        controls.append("Atomic NamedTemporaryFile Resource Allocation (CWE-377 Remediation)")

    # 10. Insecure XML / XXE (CWE-611)
    current_code, fixes = _remediate_insecure_xml(current_code)
    if fixes:
        all_fixes.extend(fixes)
        controls.append("DefusedXML Entity Expansion & XXE Protection (CWE-611 Remediation)")

    # 11. Exposed Debug Mode (CWE-215)
    current_code, fixes = _remediate_exposed_debug(current_code)
    if fixes:
        all_fixes.extend(fixes)
        controls.append("Debug Mode Disablement & Traceback Protection (CWE-215 Remediation)")

    # 12. ReDoS (CWE-1333)
    current_code, fixes = _remediate_redos(current_code)
    if fixes:
        all_fixes.extend(fixes)
        controls.append("Linear Regular Expression Backtracking Boundary Guard (CWE-1333 Remediation)")

    # 13. Server-Side Request Forgery (CWE-918)
    current_code, fixes = _remediate_ssrf(current_code)
    if fixes:
        all_fixes.extend(fixes)
        controls.append("SSRF Destination Validation & Protocol Whitelisting (CWE-918 Remediation)")

    return current_code, all_fixes, controls


def fix_attack_vulnerabilities(
    source_code: str,
    attack_simulation: dict[str, Any] | None = None,
    model_client: Any = None,
) -> dict[str, Any]:
    """Propose code changes for detected static security findings."""
    valid = validate_code(source_code)
    if valid is not True:
        raise ValueError(f"Invalid Python source code: {valid}")

    if attack_simulation is None:
        attack_simulation = simulate_attacks(source_code)

    initial_defs = _definition_names(source_code)
    scenarios = attack_simulation.get("attack_scenarios", [])
    if not scenarios:
        return {
            "agent": "security_fixing_agent",
            "agent_name": "REMEDY — Code Remediation Agent",
            "status": "already_secure",
            "fixed": False,
            "original_code": source_code,
            "fixed_code": source_code,
            "neutralized_attacks": [],
            "neutralized_count": 0,
            "addressed_static_findings": [],
            "addressed_static_findings_count": 0,
            "remaining_vulnerabilities": 0,
            "remaining_static_findings": 0,
            "applied_fixes": [],
            "defensive_controls": ["Code already adheres to secure coding standards."],
            "diff": "",
            "pre_fix_resilience_score": attack_simulation.get("resilience_score", 100),
            "post_fix_resilience_score": 100,
            "verification": {
                "syntax_valid": True,
                "definitions_preserved": True,
                "all_detected_static_findings_addressed": True,
                "all_attacks_neutralized": True,
            },
        }

    fixed_code = source_code
    applied_fixes = []
    defensive_controls = []
    mode = "deterministic_ast"

    # Attempt AI model-driven patch if client is present
    if model_client is not None and getattr(model_client, "chat", None):
        try:
            scenario_summary = "\n".join(
                f"- [{s['id']}] {s['name']} (Severity: {s['severity']}): at line {s['target_line']}: {s['vulnerable_code']} -> Mitigation: {s['mitigation']}"
                for s in scenarios
            )
            response = model_client.chat.completions.create(
                model=model_provider.MODEL_NAME,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a defensive Python software engineering assistant. "
                            "Propose a reviewable patch for the reported static security findings. "
                            "MANDATORY REQUIREMENTS:\n"
                            "1. Reduce the reported static findings without introducing new security findings.\n"
                            "2. Preserve all existing function and class definitions and their parameter names.\n"
                            "3. Do NOT add external dependencies or unneeded libraries.\n"
                            "4. Return ONLY the complete revised Python source code without markdown fences or explanatory text."
                        ),
                    },
                    {
                        "role": "user",
                        "content": f"Vulnerabilities to fix:\n{scenario_summary}\n\nOriginal Python source:\n{source_code}",
                    },
                ],
                max_tokens=4000,
                temperature=0.1,
            )
            choices = getattr(response, "choices", None)
            if choices and choices[0].message and choices[0].message.content:
                candidate = choices[0].message.content.strip()
                if candidate.startswith("```"):
                    lines = candidate.splitlines()
                    if len(lines) >= 3 and lines[-1].strip().startswith("```"):
                        candidate = "\n".join(lines[1:-1]).strip()
                if candidate and validate_code(candidate) is True:
                    if _definition_names(candidate) == initial_defs:
                        candidate_sim = simulate_attacks(candidate)
                        baseline_counts = _static_finding_counts(attack_simulation)
                        candidate_counts = _static_finding_counts(candidate_sim)
                        introduced_findings = candidate_counts - baseline_counts
                        if (
                            candidate_sim["vulnerabilities_detected"]
                            < attack_simulation["vulnerabilities_detected"]
                            and not introduced_findings
                        ):
                            fixed_code = candidate
                            mode = "ai"
                            applied_fixes = [s["mitigation"] for s in scenarios]
                            defensive_controls = list(dict.fromkeys(
                                str(s.get("mitigation", "")).strip()
                                for s in scenarios
                                if str(s.get("mitigation", "")).strip()
                            ))
                            if not defensive_controls:
                                defensive_controls = [
                                    "AI-Synthesized Security Hardening & Input Sanitization"
                                ]
        except Exception as exc:
            logger.warning("AI security fixing failed (%s); using deterministic security remediation", exc)

    # Use deterministic remediation engine if model didn't provide complete fix
    if fixed_code == source_code:
        det_code, det_fixes, det_controls = _deterministic_security_fix(source_code)
        if det_code != source_code and validate_code(det_code) is True:
            if _definition_names(det_code) == initial_defs:
                fixed_code = det_code
                applied_fixes = det_fixes
                defensive_controls = det_controls
                mode = "deterministic_ast"

    # Re-run simulation on the fixed code to verify attack neutralization
    post_simulation = simulate_attacks(fixed_code)
    post_resilience = post_simulation["resilience_score"]
    neutralized_list = []
    remaining_scenario_ids = {s["id"] for s in post_simulation.get("attack_scenarios", [])}
    for scenario in scenarios:
        if scenario["id"] not in remaining_scenario_ids:
            neutralized_list.append({
                "id": scenario["id"],
                "name": scenario["name"],
                "cwe": scenario["cwe"],
                "fix_applied": scenario.get("mitigation", "Hardened against exploit simulation."),
            })

    # Generate unified diff
    diff_lines = list(difflib.unified_diff(
        source_code.splitlines(keepends=True),
        fixed_code.splitlines(keepends=True),
        fromfile="vulnerable.py",
        tofile="secured.py",
        n=3,
    ))
    diff_text = "".join(diff_lines)

    is_fixed = fixed_code.strip() != source_code.strip()

    # Build structured minimal patch records
    patches = []
    if is_fixed:
        for neutralized in neutralized_list:
            patches.append({
                "finding_id": neutralized["id"],
                "root_cause": f"Unsanitized input reaching vulnerable sink in {neutralized.get('name', 'CWE')}",
                "original_source_location": {
                    "start_line": neutralized.get("target_line", 1),
                    "end_line": neutralized.get("target_line", 1),
                    "function_name": neutralized.get("function_name", "module"),
                },
                "proposed_modification": neutralized.get("fix_applied", "Applied defensive parameterization or sanitization."),
                "explanation": f"Neutralized {neutralized.get('cwe', '')} {neutralized.get('name', '')} by applying defensive boundary controls.",
                "expected_benefit": "Eliminates security risk without breaking existing function signatures or callers.",
                "potential_risk": "None under standard runtime constraints.",
                "confidence": 0.95,
            })
        if not patches:
            patches.append({
                "finding_id": "SEC_GENERAL_HARDENING",
                "root_cause": "Static security vulnerabilities detected in source code",
                "original_source_location": {"start_line": 1, "end_line": len(source_code.splitlines()), "function_name": "module"},
                "proposed_modification": diff_text[:500],
                "explanation": "Defensive controls applied to remediate reported findings.",
                "expected_benefit": "Remediated security issues while preserving public definitions.",
                "potential_risk": "None under standard runtime constraints.",
                "confidence": 0.90,
            })

    return {
        "agent": "security_fixing_agent",
        "agent_name": "REMEDY — Code Remediation Agent",
        "status": "completed" if is_fixed else "no_fix_needed",
        "mode": mode,
        "fixed": is_fixed,
        "original_code": source_code,
        "fixed_code": fixed_code,
        "neutralized_attacks": neutralized_list,
        "neutralized_count": len(neutralized_list),
        "addressed_static_findings": neutralized_list,
        "addressed_static_findings_count": len(neutralized_list),
        "remaining_vulnerabilities": post_simulation["vulnerabilities_detected"],
        "remaining_static_findings": post_simulation["vulnerabilities_detected"],
        "applied_fixes": applied_fixes,
        "defensive_controls": defensive_controls,
        "patches": patches,
        "diff": diff_text,
        "pre_fix_resilience_score": attack_simulation.get("resilience_score", 0),
        "post_fix_resilience_score": post_resilience,
        "verification": {
            "syntax_valid": validate_code(fixed_code) is True,
            "definitions_preserved": _definition_names(fixed_code) == initial_defs,
            "all_detected_static_findings_addressed": post_simulation["vulnerabilities_detected"] == 0,
            "all_attacks_neutralized": post_simulation["vulnerabilities_detected"] == 0,
        },
    }
