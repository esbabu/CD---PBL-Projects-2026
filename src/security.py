"""
Security Module - Code safety validation before execution
Week 7: Security Risk & Robustness Analysis

This module performs static analysis on user-submitted code to detect
potentially dangerous patterns BEFORE execution. It addresses:
  - FR-13: Basic static checks before execution
  - FR-14: Block potentially dangerous code patterns

Security Risks Addressed:
  1. File system access (read/write/delete files)
  2. System command execution (os.system, subprocess)
  3. Network access (socket, urllib, requests)
  4. Code injection (exec, eval, compile on dynamic input)
  5. Process/environment manipulation (sys.exit, env vars)
  6. Module import of dangerous libraries

Important: Static validation is not an operating system-level sandbox.
It checks for configured dangerous patterns, but cannot guarantee that code
is completely safe against all conceivable attacks or evasions.
"""

import ast
import io
import re
import tokenize
from typing import List, Dict, Tuple, Set, Optional
from dataclasses import dataclass


class SecurityStatus:
    PASSED = "PASSED"
    WARNING = "WARNING"
    BLOCKED = "BLOCKED"
    ANALYSIS_INCOMPLETE = "ANALYSIS INCOMPLETE"


@dataclass
class SecurityWarning:
    """Represents a single security warning or scan finding."""
    level: str          # 'BLOCKED', 'WARNING', or 'ANALYSIS INCOMPLETE'
    category: str       # e.g., 'file_access', 'system_command', 'dangerous_import'
    message: str        # Human-friendly description
    line_number: int    # Line where the issue was found
    code_snippet: str   # The problematic code


class CodeSecurityValidator:
    """
    Validates user code for security risks before execution.

    Uses AST-based analysis for valid code and tokenization/regex fallback
    for malformed code with syntax errors.
    """

    # Modules that should NEVER be imported in a learning environment
    BLOCKED_MODULES = {
        'os',
        # System command execution
        'subprocess', 'commands',
        # Low-level OS access
        'ctypes', 'multiprocessing',
        # Network access
        'socket', 'http', 'urllib', 'requests', 'ftplib',
        'xmlrpc', 'smtplib', 'poplib', 'imaplib',
        # Code manipulation
        'importlib', 'code', 'codeop',
        # System internals
        'signal', 'resource',
    }

    # Dangerous functions that get BLOCKED when invoked
    BLOCKED_FUNCTIONS = {
        'exec', 'eval', 'compile',      # Dynamic code execution
        '__import__', 
        'getattr', 'setattr','delattr','vars',   #attribute manipulation bypass primitives               # Dynamic imports
        'globals', 'locals',           # Scope manipulation
        'breakpoint',                   # Debugger access
    }

    # Dangerous method calls on specific modules — these get BLOCKED
    BLOCKED_MODULE_CALLS = {
        'os': [
            'system', 'popen', 'exec', 'execl', 'execle', 'execlp',
            'execv', 'execve', 'execvp', 'execvpe', 'spawn', 'spawnl',
            'spawnle', 'spawnlp', 'spawnlpe', 'spawnv', 'spawnve',
            'spawnvp', 'spawnvpe', 'fork', 'kill', 'killpg',
            'remove', 'unlink', 'rmdir', 'removedirs',
            'rename', 'renames', 'replace',
            'chmod', 'chown', 'chroot', 'link', 'symlink',
            'environ', 'putenv', 'unsetenv'
        ],
        'shutil': [
            'rmtree', 'move', 'copy', 'copy2', 'copytree',
            'disk_usage', 'chown'
        ],
        'sys': ['exit', '_exit'],
        'pathlib': [
            'unlink', 'rmdir', 'rename', 'replace', 'chmod',
            'symlink_to', 'link_to'
        ],
    }

    # Patterns that generate WARNINGs (not blocked, but flagged)
    WARNING_PATTERNS = {
        'file_open': r'\bopen\s*\(',
        'file_write': r'\.(write|writelines)\s*\(',
    }

    def __init__(self):
        self.warnings: List[SecurityWarning] = []
        self.status: str = SecurityStatus.PASSED
        self.module_aliases: Dict[str, str] = {}
        self.imported_symbols: Dict[str, Tuple[str, str]] = {}
        self.locally_defined_symbols: Set[str] = set()

    def validate(self, code: str) -> Tuple[bool, List[SecurityWarning]]:
        """
        Validate code for security risks.

        Args:
            code: The Python source code to validate

        Returns:
            Tuple of (is_safe: bool, warnings: list of SecurityWarning)
            is_safe is True only if status is PASSED or WARNING.
            is_safe is False if status is BLOCKED or ANALYSIS INCOMPLETE.
        """
        self.warnings = []
        self.status = SecurityStatus.PASSED
        self.module_aliases = {}
        self.imported_symbols = {}
        self.locally_defined_symbols = set()

        if not code or not code.strip():
            return True, self.warnings

        ast_scan_done = False
        try:
            tree = ast.parse(code)
            self._ast_scan(tree, code)
            ast_scan_done = True
        except SyntaxError:
            # Code has syntax errors — fall back to token-aware scanner
            pass
        except Exception as e:
            # Unexpected parsing failure
            self.warnings.append(SecurityWarning(
                level=SecurityStatus.ANALYSIS_INCOMPLETE,
                category='parsing_error',
                message=f"AST parsing encountered an unexpected failure: {e}",
                line_number=1,
                code_snippet=""
            ))
            self.status = SecurityStatus.ANALYSIS_INCOMPLETE
            return False, self.warnings

        if not ast_scan_done:
            self._robust_fallback_scan(code)

        # Compute status
        has_blocked = any(w.level == SecurityStatus.BLOCKED for w in self.warnings)
        has_incomplete = any(w.level == SecurityStatus.ANALYSIS_INCOMPLETE for w in self.warnings)
        has_warning = any(w.level == SecurityStatus.WARNING for w in self.warnings)

        if has_blocked:
            self.status = SecurityStatus.BLOCKED
            is_safe = False
        elif has_incomplete:
            self.status = SecurityStatus.ANALYSIS_INCOMPLETE
            is_safe = False
        elif has_warning:
            self.status = SecurityStatus.WARNING
            is_safe = True
        else:
            self.status = SecurityStatus.PASSED
            is_safe = True

        return is_safe, self.warnings

    def _ast_scan(self, tree: ast.AST, code: str) -> None:
        """Scan the AST for dangerous constructs with alias and scope resolution."""
        lines = code.split('\n')

        # Pass 1: Build definitions and import symbol table
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                self.locally_defined_symbols.add(node.name)
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        self.locally_defined_symbols.add(target.id)

            elif isinstance(node, ast.Import):
                for alias in node.names:
                    root = alias.name.split('.')[0]
                    target_asname = alias.asname or alias.name
                    self.module_aliases[target_asname] = alias.name

                    if root in self.BLOCKED_MODULES:
                        self.warnings.append(SecurityWarning(
                            level=SecurityStatus.BLOCKED,
                            category='dangerous_import',
                            message=(f"Import of prohibited module '{alias.name}' is not allowed. "
                                     f"This module can access system resources outside the learning environment."),
                            line_number=node.lineno,
                            code_snippet=self._safe_get_line(lines, node.lineno)
                        ))

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    root = node.module.split('.')[0]
                    for alias in node.names:
                        target_asname = alias.asname or alias.name
                        self.imported_symbols[target_asname] = (node.module, alias.name)

                        # Check if importing directly from a blocked module
                        if root in self.BLOCKED_MODULES:
                            self.warnings.append(SecurityWarning(
                                level=SecurityStatus.BLOCKED,
                                category='dangerous_import',
                                message=(f"Import from prohibited module '{node.module}' is not allowed. "
                                         f"This module can access system resources outside the learning environment."),
                                line_number=node.lineno,
                                code_snippet=self._safe_get_line(lines, node.lineno)
                            ))
                        # Check if importing a prohibited function from a partially blocked module (e.g., from os import system)
                        elif node.module in self.BLOCKED_MODULE_CALLS:
                            if alias.name in self.BLOCKED_MODULE_CALLS[node.module]:
                                self.warnings.append(SecurityWarning(
                                    level=SecurityStatus.BLOCKED,
                                    category='dangerous_import',
                                    message=(f"Import of prohibited function '{alias.name}' from '{node.module}' "
                                             f"is not allowed. This function can modify system resources."),
                                    line_number=node.lineno,
                                    code_snippet=self._safe_get_line(lines, node.lineno)
                                ))

        # Pass 2: Check function and method calls
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                self._check_ast_call(node, lines)

    def _check_ast_call(self, node: ast.Call, lines: List[str]) -> None:
        """Check if an AST Call node represents a dangerous or warned operation."""
        # Case A: Direct call (e.g. eval(), system(), open())
        if isinstance(node.func, ast.Name):
            func_name = node.func.id

            # 1. Prohibited built-ins (eval, exec, etc.)
            if func_name in self.BLOCKED_FUNCTIONS:
                self.warnings.append(SecurityWarning(
                    level=SecurityStatus.BLOCKED,
                    category='dangerous_function',
                    message=(f"Use of '{func_name}()' is not allowed. "
                             f"This function can execute arbitrary code and is a security risk."),
                    line_number=node.lineno,
                    code_snippet=self._safe_get_line(lines, node.lineno)
                ))

            # 2. Prohibited functions imported into local namespace
            elif func_name in self.imported_symbols:
                orig_mod, orig_name = self.imported_symbols[func_name]
                root_mod = orig_mod.split('.')[0]
                is_prohibited_call = (
                    root_mod in self.BLOCKED_MODULES or
                    (orig_mod in self.BLOCKED_MODULE_CALLS and orig_name in self.BLOCKED_MODULE_CALLS[orig_mod])
                )
                if is_prohibited_call:
                    self.warnings.append(SecurityWarning(
                        level=SecurityStatus.BLOCKED,
                        category='dangerous_function',
                        message=(f"Call to prohibited function '{func_name}()' (imported from '{orig_mod}.{orig_name}') "
                                 f"is not allowed. This can modify system resources."),
                        line_number=node.lineno,
                        code_snippet=self._safe_get_line(lines, node.lineno)
                    ))

            # 3. File open warning (only if not shadowed by a user-defined function)
            elif func_name == 'open':
                if func_name not in self.locally_defined_symbols:
                    self.warnings.append(SecurityWarning(
                        level=SecurityStatus.WARNING,
                        category='file_open',
                        message=self._get_warning_message('file_open'),
                        line_number=node.lineno,
                        code_snippet=self._safe_get_line(lines, node.lineno)
                    ))

        # Case B: Method call on an object / module (e.g. os.system, my_os.system, sh.rmtree)
        elif isinstance(node.func, ast.Attribute):
            method_name = node.func.attr

            if isinstance(node.func.value, ast.Name):
                obj_name = node.func.value.id
                # Resolve module alias if present
                resolved_mod = self.module_aliases.get(obj_name, obj_name)

                # Direct call on blocked module (e.g., sp.run)
                root_resolved = resolved_mod.split('.')[0]
                if root_resolved in self.BLOCKED_MODULES:
                    self.warnings.append(SecurityWarning(
                        level=SecurityStatus.BLOCKED,
                        category='dangerous_module_call',
                        message=(f"Call on prohibited module '{resolved_mod}.{method_name}()' is not allowed."),
                        line_number=node.lineno,
                        code_snippet=self._safe_get_line(lines, node.lineno)
                    ))
                elif resolved_mod in self.BLOCKED_MODULE_CALLS:
                    if method_name in self.BLOCKED_MODULE_CALLS[resolved_mod]:
                        self.warnings.append(SecurityWarning(
                            level=SecurityStatus.BLOCKED,
                            category='dangerous_method',
                            message=(f"Call to '{resolved_mod}.{method_name}()' is not allowed. "
                                     f"This can modify system resources outside the learning environment."),
                            line_number=node.lineno,
                            code_snippet=self._safe_get_line(lines, node.lineno)
                        ))

            # Check file write calls: .write() or .writelines()
            if method_name in ('write', 'writelines'):
                self.warnings.append(SecurityWarning(
                    level=SecurityStatus.WARNING,
                    category='file_write',
                    message=self._get_warning_message('file_write'),
                    line_number=node.lineno,
                    code_snippet=self._safe_get_line(lines, node.lineno)
                ))

    def _robust_fallback_scan(self, code: str) -> None:
        """
        Tokenization-aware fallback scan used when AST parsing fails.
        Prevents false positives on comments and string literals.
        """
        lines = code.split('\n')
        token_scan_succeeded = False

        try:
            tokens = list(tokenize.tokenize(io.BytesIO(code.encode('utf-8')).readline))
            token_scan_succeeded = True
            self._scan_tokens(tokens, lines)
        except Exception:
            # Tokenize failed (e.g., unterminated multi-line string or malformed encoding)
            token_scan_succeeded = False

        if not token_scan_succeeded:
            self._scan_sanitized_regex(lines)

    def _scan_tokens(self, tokens: List[tokenize.TokenInfo], lines: List[str]) -> None:
        """Analyze code tokens ignoring comments and string literals."""
        n = len(tokens)
        alias_map = {}
        imported_symbols = {}

        # First pass over tokens: detect imports and aliases
        i = 0
        while i < n:
            tok = tokens[i]

            # Ignore comments and docstrings
            if tok.type in (tokenize.COMMENT, tokenize.STRING):
                i += 1
                continue

            # Detect: import <module> [as <alias>]
            if tok.type == tokenize.NAME and tok.string == 'import':
                i += 1
                while i < n and tokens[i].type == tokenize.NAME:
                    mod_name = tokens[i].string
                    root_mod = mod_name.split('.')[0]
                    as_name = mod_name

                    if i + 2 < n and tokens[i + 1].string == 'as' and tokens[i + 2].type == tokenize.NAME:
                        as_name = tokens[i + 2].string
                        i += 2

                    alias_map[as_name] = mod_name

                    if root_mod in self.BLOCKED_MODULES:
                        self.warnings.append(SecurityWarning(
                            level=SecurityStatus.BLOCKED,
                            category='dangerous_import',
                            message=(f"Import of '{mod_name}' is not allowed. "
                                     f"This module can access system resources outside the learning environment."),
                            line_number=tok.start[0],
                            code_snippet=self._safe_get_line(lines, tok.start[0])
                        ))
                    i += 1
                    if i < n and tokens[i].string == ',':
                        i += 1
                        continue
                    break

            # Detect: from <module> import <name> [as <alias>]
            elif tok.type == tokenize.NAME and tok.string == 'from':
                i += 1
                if i < n and tokens[i].type == tokenize.NAME:
                    from_mod = tokens[i].string
                    root_mod = from_mod.split('.')[0]
                    i += 1
                    if i < n and tokens[i].string == 'import':
                        i += 1
                        while i < n and tokens[i].type == tokenize.NAME:
                            sym_name = tokens[i].string
                            as_name = sym_name
                            if i + 2 < n and tokens[i + 1].string == 'as' and tokens[i + 2].type == tokenize.NAME:
                                as_name = tokens[i + 2].string
                                i += 2

                            imported_symbols[as_name] = (from_mod, sym_name)

                            if root_mod in self.BLOCKED_MODULES:
                                self.warnings.append(SecurityWarning(
                                    level=SecurityStatus.BLOCKED,
                                    category='dangerous_import',
                                    message=(f"Import from '{from_mod}' is not allowed. "
                                             f"This module can access system resources outside the learning environment."),
                                    line_number=tok.start[0],
                                    code_snippet=self._safe_get_line(lines, tok.start[0])
                                ))
                            elif from_mod in self.BLOCKED_MODULE_CALLS and sym_name in self.BLOCKED_MODULE_CALLS[from_mod]:
                                self.warnings.append(SecurityWarning(
                                    level=SecurityStatus.BLOCKED,
                                    category='dangerous_import',
                                    message=(f"Import of prohibited function '{sym_name}' from '{from_mod}' is not allowed."),
                                    line_number=tok.start[0],
                                    code_snippet=self._safe_get_line(lines, tok.start[0])
                                ))

                            i += 1
                            if i < n and tokens[i].string == ',':
                                i += 1
                                continue
                            break
            i += 1

        # Second pass: detect calls
        i = 0
        while i < n:
            tok = tokens[i]
            if tok.type in (tokenize.COMMENT, tokenize.STRING):
                i += 1
                continue

            # Check for direct calls: NAME followed by '('
            if tok.type == tokenize.NAME:
                name = tok.string
                next_tok = tokens[i + 1] if i + 1 < n else None
                prev_tok = tokens[i - 1] if i > 0 else None

                # Is this an attribute access like obj.attr?
                if prev_tok and prev_tok.string == '.':
                    # Attribute check: obj.method
                    # Find previous name before '.'
                    if i >= 2 and tokens[i - 2].type == tokenize.NAME:
                        obj_name = tokens[i - 2].string
                        resolved_mod = alias_map.get(obj_name, obj_name)
                        root_mod = resolved_mod.split('.')[0]

                        if root_mod in self.BLOCKED_MODULES or (resolved_mod in self.BLOCKED_MODULE_CALLS and name in self.BLOCKED_MODULE_CALLS[resolved_mod]):
                            self.warnings.append(SecurityWarning(
                                level=SecurityStatus.BLOCKED,
                                category='dangerous_method',
                                message=(f"Call to '{resolved_mod}.{name}()' is not allowed."),
                                line_number=tok.start[0],
                                code_snippet=self._safe_get_line(lines, tok.start[0])
                            ))

                    # Check warning for .write( or .writelines(
                    if name in ('write', 'writelines') and next_tok and next_tok.string == '(':
                        self.warnings.append(SecurityWarning(
                            level=SecurityStatus.WARNING,
                            category='file_write',
                            message=self._get_warning_message('file_write'),
                            line_number=tok.start[0],
                            code_snippet=self._safe_get_line(lines, tok.start[0])
                        ))

                elif next_tok and next_tok.string == '(':
                    # Direct call: name(...)
                    if name in self.BLOCKED_FUNCTIONS:
                        self.warnings.append(SecurityWarning(
                            level=SecurityStatus.BLOCKED,
                            category='dangerous_function',
                            message=(f"Use of '{name}()' is not allowed. Dynamic execution is a security risk."),
                            line_number=tok.start[0],
                            code_snippet=self._safe_get_line(lines, tok.start[0])
                        ))
                    elif name in imported_symbols:
                        mod, sym = imported_symbols[name]
                        if mod.split('.')[0] in self.BLOCKED_MODULES or (mod in self.BLOCKED_MODULE_CALLS and sym in self.BLOCKED_MODULE_CALLS[mod]):
                            self.warnings.append(SecurityWarning(
                                level=SecurityStatus.BLOCKED,
                                category='dangerous_function',
                                message=(f"Call to prohibited function '{name}()' (imported from '{mod}.{sym}') is not allowed."),
                                line_number=tok.start[0],
                                code_snippet=self._safe_get_line(lines, tok.start[0])
                            ))
                    elif name == 'open':
                        self.warnings.append(SecurityWarning(
                            level=SecurityStatus.WARNING,
                            category='file_open',
                            message=self._get_warning_message('file_open'),
                            line_number=tok.start[0],
                            code_snippet=self._safe_get_line(lines, tok.start[0])
                        ))
            i += 1

    def _scan_sanitized_regex(self, lines: List[str]) -> None:
        """
        Regex fallback when tokenization itself fails.
        Strips comments and basic strings to avoid obvious false positives.
        """
        for line_num, line in enumerate(lines, 1):
            raw = line.strip()
            if not raw or raw.startswith('#'):
                continue

            # Strip inline comments: text after # not in quotes
            sanitized = re.sub(r'#.*$', '', raw).strip()
            # Remove string literals from the line to avoid string content false positives
            code_only = re.sub(r'(["\'])(?:(?=(\\?))\2.)*?\1', '', sanitized)

            # Blocked imports
            import_match = re.search(r'\b(?:from\s+(\S+)\s+import|import\s+(\S+))', code_only)
            if import_match:
                module = import_match.group(1) or import_match.group(2)
                root_module = module.split('.')[0]
                if root_module in self.BLOCKED_MODULES:
                    self.warnings.append(SecurityWarning(
                        level=SecurityStatus.BLOCKED,
                        category='dangerous_import',
                        message=(f"Import of '{module}' is not allowed. "
                                 f"This module can access system resources outside the learning environment."),
                        line_number=line_num,
                        code_snippet=raw
                    ))

            # Blocked functions (eval, exec, etc.)
            for func in self.BLOCKED_FUNCTIONS:
                if re.search(r'\b' + re.escape(func) + r'\s*\(', code_only):
                    self.warnings.append(SecurityWarning(
                        level=SecurityStatus.BLOCKED,
                        category='dangerous_function',
                        message=f"Use of '{func}()' is not allowed.",
                        line_number=line_num,
                        code_snippet=raw
                    ))

            # Blocked module calls (e.g. os.system)
            for mod, methods in self.BLOCKED_MODULE_CALLS.items():
                for m in methods:
                    if re.search(r'\b' + re.escape(mod) + r'\.' + re.escape(m) + r'\s*\(', code_only):
                        self.warnings.append(SecurityWarning(
                            level=SecurityStatus.BLOCKED,
                            category='dangerous_method',
                            message=f"Call to '{mod}.{m}()' is not allowed.",
                            line_number=line_num,
                            code_snippet=raw
                        ))

            # Warning patterns
            for pattern_name, pattern in self.WARNING_PATTERNS.items():
                if re.search(pattern, code_only):
                    self.warnings.append(SecurityWarning(
                        level=SecurityStatus.WARNING,
                        category=pattern_name,
                        message=self._get_warning_message(pattern_name),
                        line_number=line_num,
                        code_snippet=raw
                    ))

    def _safe_get_line(self, lines: List[str], line_number: int) -> str:
        """Safely get a line from the source code."""
        if 1 <= line_number <= len(lines):
            return lines[line_number - 1].strip()
        return ""

    def _get_warning_message(self, pattern_name: str) -> str:
        """Get a human-friendly warning message for a pattern."""
        messages = {
            'file_open': ("File access detected. Be careful when opening files — "
                          "make sure you're not reading sensitive data."),
            'file_write': ("File write detected. Writing to files can overwrite "
                           "important data. Make sure this is intentional."),
        }
        return messages.get(pattern_name, "Potentially risky operation detected.")

    def format_warnings(self) -> str:
        """Format all warnings into a human-readable string."""
        if not self.warnings:
            return "[OK] No issues detected by the configured security checks. (Note: Static analysis is not a complete security sandbox.)"

        output = []
        blocked = [w for w in self.warnings if w.level == SecurityStatus.BLOCKED]
        incomplete = [w for w in self.warnings if w.level == SecurityStatus.ANALYSIS_INCOMPLETE]
        warned = [w for w in self.warnings if w.level == SecurityStatus.WARNING]

        if blocked:
            output.append("[BLOCKED] — Code will NOT be executed:\n")
            for w in blocked:
                output.append(f"  Line {w.line_number}: {w.message}")
                output.append(f"    Code: {w.code_snippet}")
                output.append("")

        if incomplete:
            output.append("[ANALYSIS INCOMPLETE] — Verification could not finish reliably:\n")
            for w in incomplete:
                output.append(f"  Line {w.line_number}: {w.message}")
                output.append("")

        if warned:
            output.append("[WARNING] — Code will run, but review these:\n")
            for w in warned:
                output.append(f"  Line {w.line_number}: {w.message}")
                output.append(f"    Code: {w.code_snippet}")
                output.append("")

        return '\n'.join(output)


if __name__ == "__main__":
    validator = CodeSecurityValidator()

    # Test dangerous alias code
    code = """
import os as my_os
my_os.system('rm -rf /')
"""
    is_safe, warnings = validator.validate(code)
    print("Safe:", is_safe, "Status:", validator.status)
    print(validator.format_warnings())