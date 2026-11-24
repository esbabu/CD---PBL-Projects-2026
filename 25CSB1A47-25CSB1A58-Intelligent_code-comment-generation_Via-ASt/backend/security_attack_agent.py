"""SENTINEL security intelligence with AST-grounded vulnerability analysis."""

import ast
import ipaddress
import re
from typing import Any
from urllib.parse import urlsplit

from backend.attack_guard import detect_attack
from backend.security_flows import (
    find_dynamic_template_flows,
    find_sql_source_evidence,
)
from backend.validator import validate_code

_SQL_KEYWORDS = re.compile(
    r"\b(?:SELECT|INSERT|UPDATE|DELETE|DROP|UNION|FROM|WHERE)\b",
    re.IGNORECASE,
)

_INSECURE_XML_CALLS = {
    "xml.etree.ElementTree.parse",
    "xml.etree.ElementTree.fromstring",
    "xml.etree.ElementTree.XML",
    "xml.dom.minidom.parse",
    "xml.dom.minidom.parseString",
    "xml.sax.parse",
    "xml.sax.parseString",
    "xmlrpc.client.ServerProxy",
    "lxml.etree.parse",
    "lxml.etree.fromstring",
    "lxml.etree.XML",
    "ElementTree.parse",
    "ElementTree.fromstring",
    "ElementTree.XML",
    "minidom.parse",
    "minidom.parseString",
}

_SSRF_CALLS = {
    "requests.get",
    "requests.post",
    "requests.put",
    "requests.delete",
    "requests.patch",
    "requests.head",
    "requests.request",
    "urllib.request.urlopen",
    "urllib.request.Request",
    "httpx.get",
    "httpx.post",
}


def _import_aliases(tree: ast.AST) -> dict[str, str]:
    aliases = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                local_name = alias.asname or alias.name.split(".")[0]
                aliases[local_name] = alias.name if alias.asname else local_name
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                local_name = alias.asname or alias.name
                aliases[local_name] = ".".join(
                    part for part in (module, alias.name) if part
                )
    return aliases


def _canonical_call_name(node: ast.expr, aliases: dict[str, str]) -> str:
    if isinstance(node, ast.Name):
        return aliases.get(node.id, node.id)
    if isinstance(node, ast.Attribute):
        base = _canonical_call_name(node.value, aliases)
        return f"{base}.{node.attr}" if base else node.attr
    return ast.unparse(node)


def _has_dynamic_sql_value(node: ast.AST) -> bool:
    if isinstance(node, ast.JoinedStr):
        return any(isinstance(value, ast.FormattedValue) for value in node.values)
    if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Mod)):
        return any(
            not isinstance(part, ast.Constant)
            for part in (node.left, node.right)
        )
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
        return node.func.attr == "format" and bool(node.args or node.keywords)
    return False


def _find_augmented_sql_flows(
    tree: ast.AST, source_code: str
) -> list[dict[str, Any]]:
    """Track SQL strings extended with dynamic values through execute sinks."""
    lines = source_code.splitlines()
    scopes = [tree]
    scopes.extend(
        node
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    )
    findings = []

    def scope_nodes(root):
        class ScopeVisitor(ast.NodeVisitor):
            def __init__(self):
                self.nodes = []

            def generic_visit(self, node):
                self.nodes.append(node)
                super().generic_visit(node)

            def visit_FunctionDef(self, node):
                self.nodes.append(node)
                if node is root:
                    for child in ast.iter_child_nodes(node):
                        self.visit(child)

            def visit_AsyncFunctionDef(self, node):
                self.nodes.append(node)
                if node is root:
                    for child in ast.iter_child_nodes(node):
                        self.visit(child)

            def visit_ClassDef(self, node):
                self.nodes.append(node)
                if node is root:
                    for child in ast.iter_child_nodes(node):
                        self.visit(child)

        visitor = ScopeVisitor()
        visitor.visit(root)
        return sorted(
            visitor.nodes,
            key=lambda item: (
                getattr(item, "lineno", 0),
                getattr(item, "col_offset", 0),
            ),
        )

    def is_dynamic(node, literal_names):
        if isinstance(node, ast.Constant):
            return False
        if isinstance(node, ast.Name):
            return node.id not in literal_names
        if isinstance(node, ast.JoinedStr):
            return any(
                is_dynamic(value.value, literal_names)
                for value in node.values
                if isinstance(value, ast.FormattedValue)
            )
        if isinstance(node, ast.Call):
            call_text = ast.unparse(node.func).lower()
            if call_text.startswith(("request.", "flask.request.")):
                return True
            return any(
                is_dynamic(value, literal_names)
                for value in node.args
            ) or any(
                is_dynamic(keyword.value, literal_names)
                for keyword in node.keywords
            )
        if isinstance(node, ast.BinOp):
            return is_dynamic(node.left, literal_names) or is_dynamic(
                node.right, literal_names
            )
        if isinstance(node, ast.Attribute):
            return is_dynamic(node.value, literal_names)
        if isinstance(node, ast.Subscript):
            return is_dynamic(node.value, literal_names) or is_dynamic(
                node.slice, literal_names
            )
        return True

    for scope in scopes:
        nodes = scope_nodes(scope)
        sql_names = set()
        augmented_sql = {}
        literal_names = set()

        for node in nodes:
            if isinstance(node, (ast.Assign, ast.AnnAssign)):
                value = node.value
                targets = (
                    node.targets
                    if isinstance(node, ast.Assign)
                    else [node.target]
                )
                value_text = ast.unparse(value) if value is not None else ""
                value_is_sql = bool(_SQL_KEYWORDS.search(value_text))
                for target in targets:
                    if not isinstance(target, ast.Name):
                        continue
                    name = target.id
                    if value_is_sql:
                        sql_names.add(name)
                        augmented_sql.pop(name, None)
                    elif isinstance(value, ast.Name) and value.id in sql_names:
                        sql_names.add(name)
                        if value.id in augmented_sql:
                            augmented_sql[name] = list(augmented_sql[value.id])
                    else:
                        sql_names.discard(name)
                        augmented_sql.pop(name, None)
                    if isinstance(value, ast.Constant):
                        literal_names.add(name)
                    else:
                        literal_names.discard(name)
            elif isinstance(node, ast.AugAssign) and isinstance(node.target, ast.Name):
                name = node.target.id
                if (
                    name in sql_names
                    and isinstance(node.op, ast.Add)
                    and is_dynamic(node.value, literal_names)
                ):
                    augmented_sql.setdefault(name, []).append(node)
            elif isinstance(node, ast.Call):
                if (
                    not isinstance(node.func, ast.Attribute)
                    or node.func.attr != "execute"
                    or not node.args
                    or not isinstance(node.args[0], ast.Name)
                ):
                    continue
                query_name = node.args[0].id
                updates = augmented_sql.get(query_name, [])
                if not updates:
                    continue
                for update in updates:
                    line_number = getattr(update, "lineno", 1)
                    line_index = line_number - 1
                    source_line = (
                        lines[line_index]
                        if 0 <= line_index < len(lines)
                        else ast.unparse(update)
                    )
                    findings.append({
                        "line": line_number,
                        "sink_line": getattr(node, "lineno", line_number),
                        "code": source_line.strip(),
                        "expression": ast.unparse(update),
                    })
    return findings


def _find_dynamic_sql(tree: ast.AST, source_code: str) -> list[dict[str, Any]]:
    """Detect SQL expressions that interpolate or concatenate non-literal values."""
    findings = []
    lines = source_code.splitlines()
    seen = set()

    for node in ast.walk(tree):
        text_repr = ast.unparse(node)
        if (
            not _has_dynamic_sql_value(node)
            or not _SQL_KEYWORDS.search(text_repr)
        ):
            continue
        key = (getattr(node, "lineno", 1), text_repr)
        if key in seen:
            continue
        seen.add(key)
        line_idx = getattr(node, "lineno", 1) - 1
        source_line = lines[line_idx] if 0 <= line_idx < len(lines) else text_repr
        findings.append({
            "line": getattr(node, "lineno", 1),
            "code": source_line.strip(),
            "expression": text_repr,
        })

    for finding in _find_augmented_sql_flows(tree, source_code):
        key = (finding["line"], finding["expression"])
        if key not in seen:
            seen.add(key)
            findings.append(finding)
    return findings


def _find_command_injections(tree: ast.AST, source_code: str) -> list[dict[str, Any]]:
    """Detect dynamic execution and shell-enabled subprocess calls."""
    findings = []
    lines = source_code.splitlines()
    aliases = _import_aliases(tree)

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            call_name = _canonical_call_name(node.func, aliases)
            if call_name.startswith("builtins."):
                call_name = call_name[len("builtins."):]

            if call_name in {"eval", "exec", "compile", "os.system", "os.popen"}:
                line_idx = getattr(node, "lineno", 1) - 1
                source_line = lines[line_idx] if 0 <= line_idx < len(lines) else call_name
                findings.append({
                    "call": call_name,
                    "kind": "code_execution" if call_name in {"eval", "exec", "compile"} else "shell_execution",
                    "line": getattr(node, "lineno", 1),
                    "code": source_line.strip(),
                })
            elif (
                call_name.startswith("subprocess.")
                or call_name in {"Popen", "call", "check_call", "check_output", "run"}
            ):
                has_shell = any(
                    isinstance(kw.value, ast.Constant) and kw.value.value is True
                    for kw in node.keywords
                    if kw.arg == "shell"
                )
                if has_shell:
                    line_idx = getattr(node, "lineno", 1) - 1
                    source_line = lines[line_idx] if 0 <= line_idx < len(lines) else call_name
                    findings.append({
                        "call": call_name,
                        "kind": "shell_execution",
                        "line": getattr(node, "lineno", 1),
                        "code": source_line.strip(),
                        "shell": True,
                    })
    return findings


def _find_path_traversals(tree: ast.AST, source_code: str) -> list[dict[str, Any]]:
    """Detect dynamic file operations that may allow directory traversal."""
    findings = []
    lines = source_code.splitlines()
    aliases = _import_aliases(tree)

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            call_name = _canonical_call_name(node.func, aliases)

            if call_name in {"open", "os.path.join", "pathlib.Path"}:
                if node.args and isinstance(node.args[0], (ast.JoinedStr, ast.BinOp, ast.Name)):
                    line_idx = getattr(node, "lineno", 1) - 1
                    source_line = lines[line_idx] if 0 <= line_idx < len(lines) else call_name
                    unparsed = ast.unparse(node)
                    if "basename" not in unparsed and "resolve" not in unparsed:
                        if isinstance(node.args[0], ast.Name):
                            var_id = node.args[0].id
                            if any(
                                f"{var_id} =" in line and ("basename" in line or "resolve" in line)
                                for line in lines
                            ):
                                continue
                        findings.append({
                            "call": call_name,
                            "line": getattr(node, "lineno", 1),
                            "code": source_line.strip(),
                        })
    return findings


def _find_deserializations(tree: ast.AST, source_code: str) -> list[dict[str, Any]]:
    """Detect unsafe pickle or yaml deserialization."""
    findings = []
    lines = source_code.splitlines()
    aliases = _import_aliases(tree)

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            call_name = _canonical_call_name(node.func, aliases)
            if call_name in {"pickle.loads", "pickle.load", "yaml.load"}:
                line_idx = getattr(node, "lineno", 1) - 1
                source_line = lines[line_idx] if 0 <= line_idx < len(lines) else call_name
                findings.append({
                    "call": call_name,
                    "line": getattr(node, "lineno", 1),
                    "code": source_line.strip(),
                })
    return findings


def _find_hardcoded_secrets(tree: ast.AST) -> list[dict[str, Any]]:
    """Detect plaintext tokens, passwords, and API keys."""
    findings = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                target_name = ast.unparse(target).lower()
                if any(k in target_name for k in ("token", "password", "secret", "api_key", "credential")):
                    if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                        val = node.value.value.strip()
                        if val and not val.startswith("os.getenv") and len(val) >= 4:
                            findings.append({
                                "name": ast.unparse(target),
                                "line": getattr(node, "lineno", 1),
                                "code": "<credential assignment redacted>",
                            })
        elif isinstance(node, ast.AnnAssign):
            target_name = ast.unparse(node.target).lower()
            if (
                isinstance(node.value, ast.Constant)
                and isinstance(node.value.value, str)
                and node.value.value.strip()
                and len(node.value.value.strip()) >= 4
                and any(
                    key in target_name
                    for key in ("token", "password", "secret", "api_key", "credential")
                )
            ):
                findings.append({
                    "name": ast.unparse(node.target),
                    "line": getattr(node, "lineno", 1),
                    "code": "<credential assignment redacted>",
                })
    return findings


def _find_ssl_verification_disabled(tree: ast.AST, source_code: str) -> list[dict[str, Any]]:
    """Detect disabled SSL/TLS certificate verification in HTTP requests."""
    findings = []
    lines = source_code.splitlines()

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            for kw in node.keywords:
                if kw.arg == "verify" and isinstance(kw.value, ast.Constant) and kw.value.value is False:
                    line_idx = getattr(node, "lineno", 1) - 1
                    source_line = lines[line_idx] if 0 <= line_idx < len(lines) else "verify=False"
                    findings.append({
                        "line": getattr(node, "lineno", 1),
                        "code": source_line.strip(),
                    })
    return findings


def _find_insecure_xml(tree: ast.AST, source_code: str) -> list[dict[str, Any]]:
    """Detect standard XML parsers vulnerable to XML External Entity (XXE) expansion (CWE-611)."""
    findings = []
    lines = source_code.splitlines()
    aliases = _import_aliases(tree)

    if "defusedxml" in source_code:
        return []

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            call_name = _canonical_call_name(node.func, aliases)
            if (
                call_name in _INSECURE_XML_CALLS
                or call_name.endswith("ElementTree.parse")
                or call_name.endswith("ElementTree.fromstring")
                or call_name.endswith("ElementTree.XML")
                or call_name.endswith("minidom.parse")
                or call_name.endswith("minidom.parseString")
            ):
                line_idx = getattr(node, "lineno", 1) - 1
                source_line = lines[line_idx] if 0 <= line_idx < len(lines) else call_name
                findings.append({
                    "call": call_name,
                    "line": getattr(node, "lineno", 1),
                    "code": source_line.strip(),
                })
    return findings


def _is_vulnerable_regex(pattern_str: str) -> bool:
    """Identify catastrophic backtracking ReDoS regex patterns (CWE-1333)."""
    if not isinstance(pattern_str, str) or len(pattern_str) < 3:
        return False
    # 1. Nested quantifiers: group with + or * having outer + or *
    # e.g. (a+)+, (a*)*, (x+x+)+, ([a-z]+)*, (\d+)+
    if re.search(r"\([^)]*?[+*][^)]*?\)[+*]", pattern_str):
        return True
    # 2. Ambiguous alternations with repetition: (a|aa)+, (a|a?)+, etc.
    if re.search(r"\(([a-zA-Z0-9_]+)\|\1[a-zA-Z0-9_]+\)[+*]", pattern_str):
        return True
    if re.search(r"\(([a-zA-Z0-9_]+)\?[a-zA-Z0-9_]*\|\1\)[+*]", pattern_str):
        return True
    if re.search(r"\([a-zA-Z0-9_]+(?:\?|\*|\+)\|[a-zA-Z0-9_]+(?:\?|\*|\+)\)[+*]", pattern_str):
        return True
    return False


def _find_redos_patterns(tree: ast.AST, source_code: str) -> list[dict[str, Any]]:
    """Detect regular expressions vulnerable to polynomial or exponential ReDoS (CWE-1333)."""
    findings = []
    lines = source_code.splitlines()
    aliases = _import_aliases(tree)

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            call_text = _canonical_call_name(node.func, aliases)
            if any(call_text.startswith(prefix) for prefix in ("re.", "regex.")) or call_text in {
                "compile", "search", "match", "findall", "finditer", "sub", "subn"
            }:
                if node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
                    pattern_str = node.args[0].value
                    if _is_vulnerable_regex(pattern_str):
                        line_idx = getattr(node, "lineno", 1) - 1
                        source_line = lines[line_idx] if 0 <= line_idx < len(lines) else pattern_str
                        findings.append({
                            "line": getattr(node, "lineno", 1),
                            "code": source_line.strip(),
                            "pattern": pattern_str,
                        })
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                target_name = ast.unparse(target).lower()
                if any(k in target_name for k in ("pattern", "regex", "redos")):
                    if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                        pattern_str = node.value.value
                        if _is_vulnerable_regex(pattern_str):
                            line_idx = getattr(node, "lineno", 1) - 1
                            source_line = lines[line_idx] if 0 <= line_idx < len(lines) else pattern_str
                            findings.append({
                                "line": getattr(node, "lineno", 1),
                                "code": source_line.strip(),
                                "pattern": pattern_str,
                            })
    return findings


def _find_ssrf(tree: ast.AST, source_code: str) -> list[dict[str, Any]]:
    """Detect outbound requests whose destination is not statically constrained."""
    findings = []
    lines = source_code.splitlines()
    aliases = _import_aliases(tree)
    literal_urls = {}
    literal_host_sets = {}
    for candidate in ast.walk(tree):
        if isinstance(candidate, (ast.Assign, ast.AnnAssign)):
            targets = (
                candidate.targets
                if isinstance(candidate, ast.Assign)
                else [candidate.target]
            )
            value = candidate.value
            for target in targets:
                if not isinstance(target, ast.Name):
                    continue
                if isinstance(value, ast.Constant) and isinstance(value.value, str):
                    literal_urls[target.id] = value.value
                elif isinstance(value, (ast.Set, ast.List, ast.Tuple)) and all(
                    isinstance(item, ast.Constant)
                    and isinstance(item.value, str)
                    for item in value.elts
                ):
                    literal_host_sets[target.id] = {
                        item.value.lower().rstrip(".") for item in value.elts
                    }

    def private_or_local_destination(url):
        try:
            host = urlsplit(url).hostname
        except ValueError:
            return True
        if not host:
            return True
        host = host.lower().rstrip(".")
        if host in {
            "localhost",
            "metadata.google.internal",
            "metadata.azure.com",
            "metadata",
        } or host.endswith((".localhost", ".local", ".internal")):
            return True
        try:
            return not ipaddress.ip_address(host.split("%", 1)[0]).is_global
        except ValueError:
            return False

    def has_exact_host_allowlist_guard(function, url_expression, call):
        if function is None:
            return False
        parsed_names = set()
        for candidate in ast.walk(function):
            if not isinstance(candidate, (ast.Assign, ast.AnnAssign)):
                continue
            value = candidate.value
            if not (
                isinstance(value, ast.Call)
                and _canonical_call_name(value.func, aliases)
                in {
                    "urllib.parse.urlparse",
                    "urllib.parse.urlsplit",
                    "urlparse",
                    "urlsplit",
                }
                and value.args
                and ast.dump(value.args[0]) == ast.dump(url_expression)
            ):
                continue
            targets = (
                candidate.targets
                if isinstance(candidate, ast.Assign)
                else [candidate.target]
            )
            parsed_names.update(
                target.id for target in targets if isinstance(target, ast.Name)
            )

        for statement in getattr(function, "body", []):
            if not isinstance(statement, ast.If):
                continue
            if getattr(statement, "end_lineno", statement.lineno) >= call.lineno:
                continue
            tests = [statement.test]
            tests.extend(
                node
                for node in ast.walk(statement.test)
                if isinstance(node, ast.Compare)
            )
            for test in tests:
                if not (
                    isinstance(test, ast.Compare)
                    and len(test.ops) == 1
                    and len(test.comparators) == 1
                    and isinstance(test.left, ast.Attribute)
                    and test.left.attr == "hostname"
                    and isinstance(test.left.value, ast.Name)
                    and test.left.value.id in parsed_names
                ):
                    continue
                allowed_hosts = test.comparators[0]
                allowed = (
                    {
                        item.value.lower().rstrip(".")
                        for item in allowed_hosts.elts
                    }
                    if isinstance(allowed_hosts, (ast.Set, ast.List, ast.Tuple))
                    and all(
                        isinstance(item, ast.Constant)
                        and isinstance(item.value, str)
                        for item in allowed_hosts.elts
                    )
                    else literal_host_sets.get(allowed_hosts.id, set())
                    if isinstance(allowed_hosts, ast.Name)
                    else set()
                )
                if not allowed:
                    continue
                rejected_branch = (
                    statement.body
                    if isinstance(test.ops[0], ast.NotIn)
                    else statement.orelse
                    if isinstance(test.ops[0], ast.In)
                    else []
                )
                if any(
                    isinstance(item, (ast.Raise, ast.Return))
                    for item in rejected_branch
                ):
                    return True
        return False

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            call_name = _canonical_call_name(node.func, aliases)
            if call_name in _SSRF_CALLS or (
                isinstance(node.func, ast.Attribute)
                and node.func.attr in {"get", "post", "put", "delete", "head", "patch", "urlopen"}
                and call_name.startswith(("requests.", "urllib.", "httpx."))
            ):
                url_expression = (
                    node.args[0]
                    if node.args
                    else next(
                        (kw.value for kw in node.keywords if kw.arg == "url"),
                        None,
                    )
                )
                if url_expression is None:
                    continue
                literal_url = (
                    url_expression.value
                    if isinstance(url_expression, ast.Constant)
                    and isinstance(url_expression.value, str)
                    else literal_urls.get(url_expression.id, "")
                    if isinstance(url_expression, ast.Name)
                    else ""
                )
                if literal_url and not private_or_local_destination(literal_url):
                    continue

                containing_functions = [
                    scope
                    for scope in ast.walk(tree)
                    if isinstance(scope, (ast.FunctionDef, ast.AsyncFunctionDef))
                    and scope.lineno <= node.lineno <= scope.end_lineno
                ]
                function = min(
                    containing_functions,
                    key=lambda scope: scope.end_lineno - scope.lineno,
                    default=None,
                )
                guarded_by_allowlist = has_exact_host_allowlist_guard(
                    function, url_expression, node
                )
                line_idx = getattr(node, "lineno", 1) - 1
                source_line = (
                    lines[line_idx] if 0 <= line_idx < len(lines) else call_name
                )
                findings.append({
                    "call": call_name,
                    "line": getattr(node, "lineno", 1),
                    "code": source_line.strip(),
                    "confidence": 0.55 if guarded_by_allowlist else 0.85,
                    "status": "needs_review" if guarded_by_allowlist else "vulnerable",
                    "allowlist_guard": guarded_by_allowlist,
                })
    return findings


def _find_insecure_hashing(tree: ast.AST, source_code: str) -> list[dict[str, Any]]:
    """Detect cryptographically weak hash functions like MD5 and SHA-1 (CWE-327)."""
    findings = []
    lines = source_code.splitlines()
    aliases = _import_aliases(tree)

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            call_name = _canonical_call_name(node.func, aliases)
            is_insecure = False
            if call_name in {"hashlib.md5", "hashlib.sha1", "md5", "sha1"}:
                is_insecure = True
            elif call_name == "hashlib.new" and node.args:
                first_arg = node.args[0]
                if isinstance(first_arg, ast.Constant) and str(first_arg.value).lower() in {"md5", "sha1"}:
                    is_insecure = True
            if is_insecure:
                line_idx = getattr(node, "lineno", 1) - 1
                source_line = lines[line_idx] if 0 <= line_idx < len(lines) else call_name
                findings.append({
                    "call": call_name,
                    "line": getattr(node, "lineno", 1),
                    "code": source_line.strip(),
                })
    return findings


def _find_insecure_tempfiles(tree: ast.AST, source_code: str) -> list[dict[str, Any]]:
    """Detect insecure temporary file creation via tempfile.mktemp (CWE-377)."""
    findings = []
    lines = source_code.splitlines()
    aliases = _import_aliases(tree)

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            call_name = _canonical_call_name(node.func, aliases)
            if call_name in {"tempfile.mktemp", "mktemp"}:
                line_idx = getattr(node, "lineno", 1) - 1
                source_line = lines[line_idx] if 0 <= line_idx < len(lines) else call_name
                findings.append({
                    "call": call_name,
                    "line": getattr(node, "lineno", 1),
                    "code": source_line.strip(),
                })
    return findings


def _find_exposed_debug_mode(tree: ast.AST, source_code: str) -> list[dict[str, Any]]:
    """Detect exposed debug/development modes in production code (CWE-215)."""
    findings = []
    lines = source_code.splitlines()

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            for kw in node.keywords:
                if kw.arg == "debug" and isinstance(kw.value, ast.Constant) and kw.value.value is True:
                    line_idx = getattr(node, "lineno", 1) - 1
                    source_line = lines[line_idx] if 0 <= line_idx < len(lines) else "debug=True"
                    findings.append({
                        "line": getattr(node, "lineno", 1),
                        "code": source_line.strip(),
                        "call": ast.unparse(node.func),
                    })
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in {"DEBUG", "debug"}:
                    if isinstance(node.value, ast.Constant) and node.value.value is True:
                        line_idx = getattr(node, "lineno", 1) - 1
                        source_line = lines[line_idx] if 0 <= line_idx < len(lines) else "DEBUG = True"
                        findings.append({
                            "line": getattr(node, "lineno", 1),
                            "code": source_line.strip(),
                            "call": target.id,
                        })
    return findings


def _find_insecure_file_permissions(tree: ast.AST, source_code: str) -> list[dict[str, Any]]:
    """Detect overly permissive file creation masks or chmod 0o777 (CWE-732)."""
    findings = []
    lines = source_code.splitlines()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func_name = ast.unparse(node.func)
            if func_name in {"os.chmod", "chmod"}:
                for arg in node.args[1:]:
                    if (
                        isinstance(arg, ast.Constant)
                        and isinstance(arg.value, int)
                        and (arg.value & 0o777) in {0o777, 0o666}
                    ):
                        line_idx = getattr(node, "lineno", 1) - 1
                        code = lines[line_idx].strip() if 0 <= line_idx < len(lines) else ast.unparse(node)
                        findings.append({
                            "line": getattr(node, "lineno", 1),
                            "code": code,
                            "mode": oct(arg.value),
                        })
            elif func_name in {"os.umask", "umask"}:
                if node.args and isinstance(node.args[0], ast.Constant) and node.args[0].value == 0:
                    line_idx = getattr(node, "lineno", 1) - 1
                    code = lines[line_idx].strip() if 0 <= line_idx < len(lines) else ast.unparse(node)
                    findings.append({
                        "line": getattr(node, "lineno", 1),
                        "code": code,
                        "mode": "0",
                    })
    return findings


def _find_sensitive_log_exposure(tree: ast.AST, source_code: str) -> list[dict[str, Any]]:
    """Detect credentials, tokens, or passwords logged or printed (CWE-532)."""
    findings = []
    lines = source_code.splitlines()
    sensitive_words = re.compile(
        r"\b(?:password|passwd|pwd|token|secret|api_key|credit_card|auth_token)\b",
        re.IGNORECASE,
    )
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            call_name = ast.unparse(node.func)
            if any(call_name.startswith(pfx) for pfx in ("logging.", "logger.", "log.", "print")):
                args_text = " ".join(ast.unparse(arg) for arg in node.args)
                if sensitive_words.search(args_text):
                    line_idx = getattr(node, "lineno", 1) - 1
                    code = lines[line_idx].strip() if 0 <= line_idx < len(lines) else ast.unparse(node)
                    findings.append({
                        "line": getattr(node, "lineno", 1),
                        "code": code,
                        "call": call_name,
                        "leak_marker": args_text[:80],
                    })
    return findings


def _find_authentication_weaknesses(tree: ast.AST, source_code: str) -> list[dict[str, Any]]:
    """Detect hardcoded passwords used directly in equality checks (CWE-287)."""
    findings = []
    lines = source_code.splitlines()
    auth_names = {"password", "passwd", "secret_key", "admin_password", "token", "auth_token"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Compare):
            if isinstance(node.left, ast.Name) and node.left.id.lower() in auth_names:
                for comparator in node.comparators:
                    if isinstance(comparator, ast.Constant) and isinstance(comparator.value, str):
                        line_idx = getattr(node, "lineno", 1) - 1
                        code = lines[line_idx].strip() if 0 <= line_idx < len(lines) else ast.unparse(node)
                        findings.append({
                            "line": getattr(node, "lineno", 1),
                            "code": code,
                            "variable": node.left.id,
                        })
    return findings


def _find_toctou_race_conditions(tree: ast.AST, source_code: str) -> list[dict[str, Any]]:
    """Detect Time-of-Check to Time-of-Use (TOCTOU) file race conditions (CWE-367)."""
    findings = []
    lines = source_code.splitlines()
    for node in ast.walk(tree):
        if isinstance(node, ast.If):
            test_str = ast.unparse(node.test)
            if any(m in test_str for m in ("os.path.exists", "os.path.isfile", "exists(")):
                body_str = "\n".join(ast.unparse(stmt) for stmt in node.body)
                if any(sink in body_str for sink in ("open(", "os.remove(", "os.unlink(", "os.rename(")):
                    line_idx = getattr(node, "lineno", 1) - 1
                    code = lines[line_idx].strip() if 0 <= line_idx < len(lines) else test_str
                    findings.append({
                        "line": getattr(node, "lineno", 1),
                        "code": code,
                        "check": test_str,
                    })
    return findings


def _scenario_ast_evidence(
    tree: ast.AST, scenario: dict[str, Any]
) -> dict[str, Any]:
    """Resolve each static finding to its source AST node and a review comment."""
    line = scenario.get("target_line", 0)
    line_nodes = [
        node for node in ast.walk(tree) if getattr(node, "lineno", None) == line
    ]
    category = str(scenario.get("category", "")).lower()
    aliases = _import_aliases(tree)
    node_label = "ast.Module (no source-level AST node resolved)"
    sink_symbol = None
    sink_line = scenario.get("sink_line", line)

    def call_symbol(call: ast.Call) -> str:
        return _canonical_call_name(call.func, aliases)

    calls = [node for node in line_nodes if isinstance(node, ast.Call)]
    if "sql" in category:
        dynamic_nodes = [
            node
            for node in line_nodes
            if isinstance(node, (ast.JoinedStr, ast.BinOp))
            or (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "format"
            )
        ]
        dynamic_node = dynamic_nodes[0] if dynamic_nodes else None
        if dynamic_node is None:
            dynamic_node = next(
                (
                    node
                    for node in line_nodes
                    if isinstance(node, ast.AugAssign)
                    and isinstance(node.op, ast.Add)
                ),
                None,
            )
        dynamic_names = set()
        if dynamic_node is not None:
            for parent in ast.walk(tree):
                if (
                    isinstance(parent, (ast.Assign, ast.AnnAssign))
                    and getattr(parent, "lineno", None) == line
                    and parent.value is not None
                    and any(child is dynamic_node for child in ast.walk(parent.value))
                ):
                    targets = parent.targets if isinstance(parent, ast.Assign) else [parent.target]
                    dynamic_names.update(
                        target.id for target in targets if isinstance(target, ast.Name)
                    )

        sql_calls = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "execute"
            and (
                node in calls
                or getattr(node, "lineno", None) == sink_line
                or any(
                    isinstance(argument, ast.JoinedStr)
                    or any(
                        isinstance(child, ast.Name) and child.id in dynamic_names
                        for child in ast.walk(argument)
                    )
                    for argument in node.args
                )
            )
        ]
        if dynamic_node is not None:
            if isinstance(dynamic_node, ast.JoinedStr):
                node_label = "ast.JoinedStr (f-string interpolation)"
            elif isinstance(dynamic_node, ast.BinOp):
                node_label = "ast.BinOp (dynamic SQL construction)"
            elif isinstance(dynamic_node, ast.AugAssign):
                node_label = "ast.AugAssign (dynamic SQL append)"
            else:
                node_label = "ast.Call (str.format SQL construction)"
        elif calls:
            node_label = "ast.Call"
        if sql_calls:
            sink_symbol = call_symbol(sql_calls[0])
            node_label += f" -> ast.Call -> {sink_symbol}"
            sink_line = getattr(sql_calls[0], "lineno", sink_line)
    elif "template" in category or "cross-site scripting" in category:
        template_call = next(
            (
                call
                for call in calls
                if call_symbol(call).endswith("render_template_string")
            ),
            None,
        )
        if template_call:
            sink_symbol = call_symbol(template_call)
            sink_line = getattr(template_call, "lineno", sink_line)
            node_label = f"ast.Call -> {sink_symbol} (dynamic template rendering)"
    elif "credential" in category:
        assignment = next(
            (node for node in line_nodes if isinstance(node, (ast.Assign, ast.AnnAssign))),
            None,
        )
        if assignment is not None:
            node_label = "ast.Assign (hardcoded credential)"
            targets = (
                assignment.targets
                if isinstance(assignment, ast.Assign)
                else [assignment.target]
            )
            sink_symbol = next(
                (target.id for target in targets if isinstance(target, ast.Name)),
                None,
            )
    elif "debug" in category or "information disclosure" in category:
        debug_call = next(
            (
                call
                for call in calls
                if any(keyword.arg == "debug" for keyword in call.keywords)
            ),
            None,
        )
        if debug_call is not None:
            sink_symbol = call_symbol(debug_call)
            node_label = f"ast.Call -> {sink_symbol}(debug=True)"
        else:
            assignment = next(
                (node for node in line_nodes if isinstance(node, ast.Assign)), None
            )
            if assignment is not None:
                node_label = "ast.Assign (debug mode enabled)"
                sink_symbol = next(
                    (
                        target.id
                        for target in assignment.targets
                        if isinstance(target, ast.Name)
                    ),
                    None,
                )
    elif calls:
        call = calls[0]
        sink_symbol = call_symbol(call)
        has_shell_true = any(
            keyword.arg == "shell"
            and isinstance(keyword.value, ast.Constant)
            and keyword.value.value is True
            for keyword in call.keywords
        )
        if sink_symbol.startswith("subprocess.") and has_shell_true:
            node_label = f"ast.Call -> {sink_symbol}(shell=True)"
        else:
            node_label = f"ast.Call -> {sink_symbol}"
    elif line_nodes:
        node = next(
            (item for item in line_nodes if isinstance(item, ast.Assign)),
            line_nodes[0],
        )
        node_label = f"ast.{type(node).__name__}"

    cwe_match = re.search(r"\bCWE-\d+\b", str(scenario.get("cwe", "")))
    cwe_label = cwe_match.group(0) if cwe_match else "OWASP-LLM01"
    mitigation = " ".join(str(scenario.get("mitigation", "")).split())
    comment = (
        f"# [AST-SEC {cwe_label}] {scenario.get('name', 'Potential security issue')}. "
        f"{mitigation}"
    )
    return {
        "ast_node_type": node_label,
        "ast_sink_symbol": sink_symbol,
        "ast_sink_line": sink_line,
        "ast_security_comment": comment,
    }


def simulate_attacks(source_code: str, model_client: Any = None) -> dict[str, Any]:
    """Statically assess Python source without executing it or its inputs."""
    del model_client  # Retained for compatibility with existing agent callers.
    valid = validate_code(source_code)
    if valid is not True:
        raise ValueError(f"Invalid Python source code: {valid}")

    tree = ast.parse(source_code)
    scenarios = []

    # 1. SQL Injection (CWE-89)
    sql_findings = _find_dynamic_sql(tree, source_code)
    for idx, f in enumerate(sql_findings, start=1):
        scenarios.append({
            "id": f"SIM-SQLI-{idx:03d}",
            "name": "Potential SQL Injection",
            "category": "SQL Injection",
            "cwe": "CWE-89: Improper Neutralization of Special Elements used in an SQL Command",
            "severity": "critical",
            "risk_score": 95,
            "target_line": f["line"],
            "vulnerable_code": f["code"],
            "attack_payload": "Synthetic untrusted input marker (not executed)",
            "simulation_trace": (
                f"Static analysis found dynamic SQL expression '{f['expression']}'. "
                "No database connection or input payload was used."
            ),
            "impact": (
                "A parameter inserted into SQL text can alter query structure if an "
                "untrusted caller controls it; the submitted source does not establish "
                "the parameter's external origin."
            ),
            "status": "vulnerable",
            **({"sink_line": f["sink_line"]} if f.get("sink_line") else {}),
            "mitigation": "Use parameterized queries with placeholders (? or %s) instead of string formatting.",
        })

    # Dynamic templates built from request data bypass normal template autoescaping.
    template_findings = find_dynamic_template_flows(tree, source_code)
    for idx, finding in enumerate(template_findings, start=1):
        scenarios.append({
            "id": f"SIM-TPL-{idx:03d}",
            "name": "Untrusted Data in Dynamic HTML Template",
            "category": "HTML Injection / Template Injection",
            "cwe": "CWE-79: Improper Neutralization of Input During Web Page Generation",
            "severity": "high",
            "risk_score": 88,
            "target_line": finding["sink_line"],
            "source_line": finding["source_line"],
            "source": finding["source"],
            "template_line": finding["template_line"],
            "sink_line": finding["sink_line"],
            "sink": finding["sink"],
            "source_to_sink": (
                f"Line {finding['source_line']} -> line {finding['template_line']} "
                f"-> {finding['sink']} at line {finding['sink_line']}"
            ),
            "confidence": finding["confidence"],
            "vulnerable_code": finding["code"],
            "attack_payload": "Synthetic untrusted request-data marker (not executed)",
            "simulation_trace": (
                f"Static analysis traced {finding['source']} at line "
                f"{finding['source_line']} into a dynamically constructed template "
                f"at line {finding['template_line']}, then to "
                f"{finding['sink']} at line {finding['sink_line']}. "
                "The source was not executed."
            ),
            "impact": (
                "Request data inserted into template source can become literal HTML "
                "or template syntax, enabling reflected XSS and potentially server-side "
                "template injection."
            ),
            "status": "vulnerable",
            "mitigation": (
                "Render a regular template with render_template('greet.html', name=name) "
                "and let the template engine autoescape the context value."
            ),
        })

    # 2. Dynamic Code / Shell Execution (CWE-78 / CWE-94)
    cmd_findings = _find_command_injections(tree, source_code)
    for idx, f in enumerate(cmd_findings, start=1):
        call_name = f.get("call", "eval")
        is_code_execution = f.get("kind") == "code_execution"
        scenarios.append({
            "id": f"SIM-CMDI-{idx:03d}",
            "name": (
                "Dynamic Code Execution"
                if is_code_execution
                else "Shell Command Execution"
            ),
            "category": "Code Injection" if is_code_execution else "Command Injection",
            "cwe": (
                "CWE-94: Improper Control of Generation of Code"
                if is_code_execution
                else "CWE-78: Improper Neutralization of Special Elements used in an OS Command"
            ),
            "severity": "critical",
            "risk_score": 98,
            "target_line": f["line"],
            "vulnerable_code": f["code"],
            "attack_payload": "Synthetic untrusted input marker (not executed)",
            "simulation_trace": (
                f"Static analysis found a call to '{call_name}'. "
                "No source code, shell command, or payload was executed."
            ),
            "impact": "If supplied with untrusted data, this call may execute unintended code or commands.",
            "status": "vulnerable",
            "mitigation": "Avoid eval/exec; use ast.literal_eval for data parsing; use subprocess.run with argument list and shell=False.",
        })

    # 3. Path Traversal (CWE-22)
    path_findings = _find_path_traversals(tree, source_code)
    for idx, f in enumerate(path_findings, start=1):
        scenarios.append({
            "id": f"SIM-TRAV-{idx:03d}",
            "name": "Potential Path Traversal",
            "category": "Path Traversal",
            "cwe": "CWE-22: Improper Limitation of a Pathname to a Restricted Directory",
            "severity": "high",
            "risk_score": 85,
            "target_line": f["line"],
            "vulnerable_code": f["code"],
            "attack_payload": "Synthetic path input marker (not executed)",
            "simulation_trace": (
                "Static analysis found a path built from a dynamic value without a "
                "visible containment check. No filesystem path was opened."
            ),
            "impact": "An unchecked dynamic path may escape its intended directory.",
            "status": "vulnerable",
            "mitigation": "Use os.path.basename() or pathlib.Path.resolve() and verify the target path resides within an allowed directory.",
        })

    # 4. Insecure Deserialization (CWE-502)
    deser_findings = _find_deserializations(tree, source_code)
    for idx, f in enumerate(deser_findings, start=1):
        scenarios.append({
            "id": f"SIM-DESER-{idx:03d}",
            "name": "Potential Unsafe Deserialization",
            "category": "Insecure Deserialization",
            "cwe": "CWE-502: Deserialization of Untrusted Data",
            "severity": "critical",
            "risk_score": 95,
            "target_line": f["line"],
            "vulnerable_code": f["code"],
            "attack_payload": "Synthetic serialized-input marker (not executed)",
            "simulation_trace": (
                f"Static analysis found a call to '{f['call']}'. "
                "No serialized data was loaded."
            ),
            "impact": "Untrusted serialized data may execute code during deserialization.",
            "status": "vulnerable",
            "mitigation": "Replace pickle with safe serialization formats like json or yaml.safe_load.",
        })

    # 5. Hardcoded Credentials (CWE-798 / CWE-522)
    secret_findings = _find_hardcoded_secrets(tree)
    for idx, f in enumerate(secret_findings, start=1):
        scenarios.append({
            "id": f"SIM-CRED-{idx:03d}",
            "name": "Hardcoded Secret & Credential Disclosure",
            "category": "Credential Exposure",
            "cwe": "CWE-522: Insufficiently Protected Credentials / CWE-798: Use of Hard-coded Credentials",
            "severity": "high",
            "risk_score": 88,
            "target_line": f["line"],
            "vulnerable_code": f["code"],
            "attack_payload": "Synthetic secret-discovery marker (not executed)",
            "simulation_trace": (
                f"Static analysis found a string literal assigned to '{f['name']}'. "
                "The literal value is not included in this report."
            ),
            "impact": "A committed credential may be exposed to anyone with source access.",
            "status": "vulnerable",
            "mitigation": "Load secrets via environment variables (os.getenv) or a secrets manager.",
        })

    # 6. Disabled TLS / SSL Verification (CWE-295)
    ssl_findings = _find_ssl_verification_disabled(tree, source_code)
    for idx, f in enumerate(ssl_findings, start=1):
        scenarios.append({
            "id": f"SIM-SSL-{idx:03d}",
            "name": "TLS Verification Disabled",
            "category": "Transport Security",
            "cwe": "CWE-295: Improper Certificate Validation",
            "severity": "medium",
            "risk_score": 70,
            "target_line": f["line"],
            "vulnerable_code": f["code"],
            "attack_payload": "Synthetic certificate-validation marker (not executed)",
            "simulation_trace": (
                "Static analysis found TLS verification disabled. "
                "No network request or interception was performed."
            ),
            "impact": "Disabling certificate verification can expose connections to interception.",
            "status": "vulnerable",
            "mitigation": "Ensure SSL verification remains enabled (verify=True).",
        })

    # 7. XML External Entity (XXE) Injection (CWE-611)
    xml_findings = _find_insecure_xml(tree, source_code)
    for idx, f in enumerate(xml_findings, start=1):
        scenarios.append({
            "id": f"SIM-XXE-{idx:03d}",
            "name": "XML External Entity (XXE) Injection",
            "category": "XML Injection",
            "cwe": "CWE-611: Improper Restriction of XML External Entity Reference",
            "severity": "high",
            "risk_score": 86,
            "target_line": f["line"],
            "vulnerable_code": f["code"],
            "attack_payload": "Synthetic untrusted XML entity marker (not executed)",
            "simulation_trace": (
                f"Static analysis identified insecure XML parser call '{f['call']}'. "
                "Untrusted XML input may trigger entity expansion or arbitrary file read."
            ),
            "impact": "Malicious XML documents can abuse DTD entities to read local files or execute SSRF.",
            "status": "vulnerable",
            "mitigation": "Use defusedxml (e.g., defusedxml.ElementTree) or disable entity resolution in parser.",
        })

    # 8. Regular Expression Denial of Service (ReDoS) (CWE-1333)
    redos_findings = _find_redos_patterns(tree, source_code)
    for idx, f in enumerate(redos_findings, start=1):
        scenarios.append({
            "id": f"SIM-REDOS-{idx:03d}",
            "name": "Regular Expression Denial of Service (ReDoS)",
            "category": "Denial of Service",
            "cwe": "CWE-1333: Inefficient Regular Expression Complexity",
            "severity": "medium",
            "risk_score": 75,
            "target_line": f["line"],
            "vulnerable_code": f["code"],
            "attack_payload": "Synthetic catastrophic-backtracking input marker (not executed)",
            "simulation_trace": (
                f"Static analysis identified regex pattern '{f.get('pattern', '')}' with nested or ambiguous quantifiers. "
                "Unbounded backtracking can freeze execution."
            ),
            "impact": "Crafted input matching ambiguous sub-patterns triggers exponential backtracking, consuming 100% CPU.",
            "status": "vulnerable",
            "mitigation": "Refactor regular expression to remove nested quantifiers (e.g. rewrite (a+)+ to a+) or apply input length limits.",
        })

    # 9. Server-Side Request Forgery (SSRF) (CWE-918)
    ssrf_findings = _find_ssrf(tree, source_code)
    for idx, f in enumerate(ssrf_findings, start=1):
        guarded = f.get("allowlist_guard", False)
        scenarios.append({
            "id": f"SIM-SSRF-{idx:03d}",
            "name": (
                "Potential SSRF (destination allowlist needs runtime verification)"
                if guarded
                else "Server-Side Request Forgery (SSRF)"
            ),
            "category": "Server-Side Request Forgery",
            "cwe": "CWE-918: Server-Side Request Forgery (SSRF)",
            "severity": "medium" if guarded else "high",
            "risk_score": 60 if guarded else 88,
            "target_line": f["line"],
            "vulnerable_code": f["code"],
            "attack_payload": "Synthetic internal-destination marker (not executed)",
            "simulation_trace": (
                f"Static analysis identified outbound HTTP request '{f['call']}'. "
                + (
                    "A call-site hostname allowlist is present, but static analysis cannot prove DNS results "
                    "are restricted to public IP addresses."
                    if guarded
                    else "The dynamic destination is not constrained by a recognized call-site hostname allowlist."
                )
                + " No network request was made."
            ),
            "impact": "Attacker-controlled URLs allow internal network scanning or access to cloud metadata services.",
            "status": f.get("status", "vulnerable"),
            "confidence": f.get("confidence", 0.85),
            "mitigation": "Use an explicit destination allowlist and validate every resolved address against loopback, private, link-local, reserved, and metadata ranges before connecting.",
        })

    # 10. Insecure Cryptographic Hashing (CWE-327)
    hash_findings = _find_insecure_hashing(tree, source_code)
    for idx, f in enumerate(hash_findings, start=1):
        scenarios.append({
            "id": f"SIM-HASH-{idx:03d}",
            "name": "Weak Cryptographic Hash Function",
            "category": "Insecure Cryptography",
            "cwe": "CWE-327: Use of a Broken or Risky Cryptographic Algorithm",
            "severity": "medium",
            "risk_score": 72,
            "target_line": f["line"],
            "vulnerable_code": f["code"],
            "attack_payload": "Synthetic collision/preimage marker (not executed)",
            "simulation_trace": (
                f"Static analysis found legacy broken hash algorithm '{f['call']}'. "
                "MD5 and SHA-1 suffer from collision and length-extension vulnerabilities."
            ),
            "impact": "Cryptographic collisions allow forged digital signatures, undetected tampering, or rapid password cracking.",
            "mitigation": "Upgrade to hashlib.sha256 or hashlib.sha3_256 for integrity verification, or argon2/bcrypt for passwords.",
        })

    # 11. Insecure Temporary Files (CWE-377)
    tmp_findings = _find_insecure_tempfiles(tree, source_code)
    for idx, f in enumerate(tmp_findings, start=1):
        scenarios.append({
            "id": f"SIM-TMP-{idx:03d}",
            "name": "Insecure Temporary File Creation",
            "category": "Insecure File Management",
            "cwe": "CWE-377: Insecure Temporary File",
            "severity": "medium",
            "risk_score": 68,
            "target_line": f["line"],
            "vulnerable_code": f["code"],
            "attack_payload": "Synthetic symlink race marker (not executed)",
            "simulation_trace": (
                f"Static analysis found '{f['call']}()' which generates filenames without atomicity, "
                "creating time-of-check to time-of-use (TOCTOU) race conditions."
            ),
            "impact": "A local attacker can create a symlink at the predicted filename before file open, leading to arbitrary file overwrite.",
            "mitigation": "Replace tempfile.mktemp() with tempfile.NamedTemporaryFile() or tempfile.mkstemp() to atomically create and open the file.",
        })

    # 12. Exposed Debug Mode (CWE-215)
    debug_findings = _find_exposed_debug_mode(tree, source_code)
    for idx, f in enumerate(debug_findings, start=1):
        scenarios.append({
            "id": f"SIM-DEBUG-{idx:03d}",
            "name": "Exposed Debug/Development Mode",
            "category": "Information Disclosure",
            "cwe": "CWE-215: Insertion of Sensitive Information Into Debugging Code",
            "severity": "high",
            "risk_score": 82,
            "target_line": f["line"],
            "vulnerable_code": f["code"],
            "attack_payload": "Synthetic interactive traceback marker (not executed)",
            "simulation_trace": (
                "Static analysis found debug mode explicitly enabled (debug=True / DEBUG = True). "
                "In web frameworks, debug mode exposes interactive tracebacks and console code execution."
            ),
            "impact": "Interactive debug consoles allow remote code execution, and stack traces reveal system internals and secrets.",
            "mitigation": "Set debug=False or configure debug mode via environment variable (e.g., os.getenv('DEBUG', 'False').lower() == 'true').",
        })

    # 13. Insecure File Permissions (CWE-732)
    perm_findings = _find_insecure_file_permissions(tree, source_code)
    for idx, f in enumerate(perm_findings, start=1):
        scenarios.append({
            "id": f"SIM-PERM-{idx:03d}",
            "name": "Insecure File Permissions / Excessive Privilege",
            "category": "Insecure File Permissions",
            "cwe": "CWE-732: Incorrect Permission Assignment for Critical Resource",
            "severity": "high",
            "risk_score": 80,
            "target_line": f["line"],
            "vulnerable_code": f["code"],
            "attack_payload": "Synthetic world-writable permission marker (not executed)",
            "simulation_trace": (
                f"Static analysis found overly permissive file mode '{f['mode']}'. "
                "World-writable files allow unprivileged local users to tamper with application data."
            ),
            "impact": "Unrestricted file permissions allow unauthorized modification or execution by any local user.",
            "mitigation": "Restrict file permissions using 0o600 for confidential files or 0o700 for directories.",
        })

    # 14. Sensitive Information Exposure in Logs (CWE-532)
    log_findings = _find_sensitive_log_exposure(tree, source_code)
    for idx, f in enumerate(log_findings, start=1):
        scenarios.append({
            "id": f"SIM-LOG-{idx:03d}",
            "name": "Sensitive Information Exposure in Logs or Print",
            "category": "Sensitive Information Exposure",
            "cwe": "CWE-532: Insertion of Sensitive Information into Log File",
            "severity": "medium",
            "risk_score": 75,
            "target_line": f["line"],
            "vulnerable_code": f["code"],
            "attack_payload": "Synthetic credential leakage marker (not executed)",
            "simulation_trace": (
                f"Static analysis found sensitive credential variable printed or logged: '{f['leak_marker']}'. "
                "Logs are often stored in plain text or aggregated to shared monitoring tools."
            ),
            "impact": "Credentials written to application logs can be harvested by attackers or unauthorized staff.",
            "mitigation": "Scrub or mask sensitive variables before logging, or use dedicated secret masking formatters.",
        })

    # 15. Authentication Weakness / Hardcoded Password Comparison (CWE-287)
    auth_findings = _find_authentication_weaknesses(tree, source_code)
    for idx, f in enumerate(auth_findings, start=1):
        scenarios.append({
            "id": f"SIM-AUTH-{idx:03d}",
            "name": "Hardcoded Password in Authentication Logic",
            "category": "Authentication Weakness",
            "cwe": "CWE-287: Improper Authentication",
            "severity": "critical",
            "risk_score": 92,
            "target_line": f["line"],
            "vulnerable_code": f["code"],
            "attack_payload": "Synthetic hardcoded authentication bypass marker (not executed)",
            "simulation_trace": (
                f"Static analysis identified direct comparison of variable '{f['variable']}' with a hardcoded literal. "
                "Hardcoded credentials cannot be safely rotated without code deployment."
            ),
            "impact": "Anyone with access to the source code can authenticate without valid account credentials.",
            "mitigation": "Verify passwords against salted hashes (e.g. bcrypt or argon2) stored securely in a database.",
        })

    # 16. Time-of-Check to Time-of-Use (TOCTOU) Race Condition (CWE-367)
    toctou_findings = _find_toctou_race_conditions(tree, source_code)
    for idx, f in enumerate(toctou_findings, start=1):
        scenarios.append({
            "id": f"SIM-TOCTOU-{idx:03d}",
            "name": "Time-of-Check to Time-of-Use (TOCTOU) Race Condition",
            "category": "Race Condition",
            "cwe": "CWE-367: Time-of-check Time-of-use (TOCTOU) Race Condition",
            "severity": "medium",
            "risk_score": 70,
            "target_line": f["line"],
            "vulnerable_code": f["code"],
            "attack_payload": "Synthetic filesystem race condition marker (not executed)",
            "simulation_trace": (
                f"Static analysis found check '{f['check']}' followed by a file operation. "
                "The state of the file can change between the existence check and actual file operation."
            ),
            "impact": "Concurrent processes or symlink attacks can alter the file between check and access.",
            "mitigation": "Use atomic operations or exception handling (EAFP: try/except FileNotFoundError) instead of pre-checking exists().",
        })

    # 13. Separate prompt-injection findings from generic static code-security findings.
    attack_detection = detect_attack(source_code, content_type="code")
    if attack_detection["detected"]:
        for category in attack_detection["categories"]:
            if category in {
                "code_security_risk",
                "sql_injection",
                "insecure_cryptography",
                "insecure_temporary_file",
                "xxe_injection",
                "redos_risk",
                "ssrf_risk",
                "exposed_debug_mode",
            } and scenarios:
                continue
            if category in {"code_security_risk", "sql_injection"}:
                display_category = "Static Code Security Risk"
                category_name = "Static Code Security"
                cwe = "CWE-89: SQL Injection" if category == "sql_injection" else "Static security analysis"
                impact = "Dynamic SQL construction allows query manipulation." if category == "sql_injection" else "A static security rule identified potentially unsafe code."
                mitigation = "Use parameterized queries with bind placeholders (? or %s)." if category == "sql_injection" else "Review the specific static security finding and apply its recommended mitigation."
            elif category in {"credential_exfiltration", "private_data_exfiltration", "sensitive_data_transfer"}:
                display_category = "Sensitive Data Handling Risk"
                category_name = "Sensitive Data Handling"
                cwe = "Sensitive data exposure risk"
                impact = "Source patterns may expose credentials or private information."
                mitigation = "Keep secrets in a secrets manager and prevent sensitive data from reaching untrusted outputs."
            else:
                display_category = "Untrusted Instruction or Data Risk"
                category_name = "Untrusted AI Input"
                cwe = "OWASP-LLM01: Prompt Injection"
                impact = "Untrusted text may influence an AI system or expose sensitive information."
                mitigation = "Treat source comments and strings as untrusted data; enforce instruction/data separation."
            scenarios.append({
                "id": f"SIM-INJ-{len(scenarios)+1:03d}",
                "name": f"{display_category}: {category.replace('_', ' ').title()}",
                "category": category_name,
                "cwe": cwe,
                "severity": attack_detection["severity"],
                "risk_score": attack_detection["risk_score"],
                "target_line": 0,
                "vulnerable_code": "# Untrusted source content detected; content omitted",
                "attack_payload": "Synthetic untrusted-content marker (not executed)",
                "simulation_trace": (
                    "Static analysis detected a risky source pattern. "
                    "No AI prompt, source code, or payload was executed."
                ),
                "impact": impact,
                "status": "vulnerable",
                "mitigation": mitigation,
            })

    for scenario in scenarios:
        evidence = _scenario_ast_evidence(tree, scenario)
        scenario.update(evidence)
        scenario.setdefault("analysis_type", "static_ast")
        scenario.setdefault("dynamically_verified", False)
        scenario.setdefault("confidence", scenario.get("confidence", "high"))
        scenario.setdefault("remediation", scenario.get("mitigation", "Review and fix finding."))
        scenario.setdefault(
            "affected_location",
            {
                "line": scenario.get("target_line", 1),
                "code": scenario.get("vulnerable_code", ""),
            },
        )
        if "sql" in str(scenario.get("category", "")).lower():
            scenario.update(find_sql_source_evidence(tree, scenario["target_line"]))
            if evidence.get("ast_sink_line"):
                scenario["sink_line"] = evidence["ast_sink_line"]
            scenario["source_to_sink"] = (
                f"{scenario.get('source')} -> {scenario.get('ast_sink_symbol') or 'SQL execution'} "
                f"at line {scenario.get('sink_line', scenario['target_line'])}"
            )
        elif "template" in str(scenario.get("category", "")).lower():
            scenario["ast_sink_line"] = scenario["sink_line"]

    total_checks = 14
    vulnerable_count = len(scenarios)

    if vulnerable_count == 0:
        resilience_score = 100
        defense_verdict = "No findings in these static checks (not a security certification)"
    else:
        penalty = sum(s["risk_score"] for s in scenarios)
        resilience_score = max(5, round(100 - (penalty / len(scenarios)) * (vulnerable_count / (vulnerable_count + 1))))
        defense_verdict = f"Vulnerable · {vulnerable_count} Simulated Attack Vector(s) Succeeded"

    risk_counts = {
        "critical": sum(1 for s in scenarios if s["severity"] == "critical"),
        "high": sum(1 for s in scenarios if s["severity"] == "high"),
        "medium": sum(1 for s in scenarios if s["severity"] == "medium"),
        "low": sum(1 for s in scenarios if s["severity"] == "low"),
    }

    return {
        "agent": "security_attack_simulation",
        "agent_name": "Static Python Security Analyzer",
        "status": "completed",
        "assessment_type": "static_analysis",
        "simulation_only": True,
        "execution_status": "not_executed",
        "total_simulations_run": total_checks,
        "total_checks_run": total_checks,
        "vulnerabilities_detected": vulnerable_count,
        "resilience_score": resilience_score,
        "defense_verdict": defense_verdict,
        "risk_breakdown": risk_counts,
        "attack_scenarios": scenarios,
        "is_vulnerable": vulnerable_count > 0,
        "summary": (
            f"Completed {total_checks} static security checks. "
            f"Detected {vulnerable_count} potential finding(s) "
            f"({risk_counts['critical']} Critical, {risk_counts['high']} High). "
            f"Static risk score: {resilience_score}/100; this is not a security certification."
        ),
    }
