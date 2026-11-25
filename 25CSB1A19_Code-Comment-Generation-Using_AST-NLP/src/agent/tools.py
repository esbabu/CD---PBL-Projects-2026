import ast
import re


def inspect_ast(source_code):
    result = {
        "valid_python": False,
        "functions": [],
        "classes": [],
        "imports": [],
        "calls": [],
        "loops": 0,
        "conditionals": 0,
        "lines": len(source_code.splitlines()),
    }
    try:
        tree = ast.parse(source_code)
    except SyntaxError as error:
        result["syntax_error"] = f"Line {error.lineno}: {error.msg}"
        return result

    result["valid_python"] = True
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            result["functions"].append({"name": node.name, "line": node.lineno})
        elif isinstance(node, ast.ClassDef):
            result["classes"].append({"name": node.name, "line": node.lineno})
        elif isinstance(node, ast.Import):
            result["imports"].extend(name.name for name in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            result["imports"].append(node.module)
        elif isinstance(node, ast.Call):
            result["calls"].append(_call_name(node))
        elif isinstance(node, (ast.For, ast.While, ast.AsyncFor)):
            result["loops"] += 1
        elif isinstance(node, (ast.If, ast.IfExp, ast.Match)):
            result["conditionals"] += 1
    return result


def run_local_security_analysis(source_code):
    """Local defensive checks; no external API is required."""
    issues = []
    try:
        tree = ast.parse(source_code)
    except SyntaxError:
        return issues

    lines = source_code.splitlines()

    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id in {"eval", "exec", "compile"}:
                issues.append(_issue("SEC001", "critical", node, tree,
                    f"Dangerous use of {node.func.id}(). It can execute dynamically controlled code.",
                    "Avoid dynamic execution; use explicit parsing or validated operations."))

    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr == "run":
                for keyword in node.keywords:
                    if (keyword.arg == "shell" and isinstance(keyword.value, ast.Constant)
                            and keyword.value.value is True):
                        issues.append(_issue("SEC002", "critical", node, tree,
                            "subprocess.run() uses shell=True.",
                            "Avoid shell=True when processing untrusted input."))

    secret_pattern = re.compile(r"(password|passwd|secret|api[_-]?key|token)", re.I)
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and secret_pattern.search(target.id):
                    if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                        issues.append(_issue("SEC003", "high", node, tree,
                            f"Possible hardcoded secret in '{target.id}'.",
                            "Use environment variables or a secure secret store."))

    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and _call_name(node) in {"md5", "sha1"}:
            issues.append(_issue("SEC004", "medium", node, tree,
                f"Weak cryptographic algorithm: {_call_name(node)}.",
                "Use a modern cryptographic algorithm such as SHA-256 where appropriate."))

    for number, line in enumerate(lines, 1):
        upper = line.upper()
        if any(k in upper for k in ("SELECT", "INSERT", "UPDATE", "DELETE")):
            if "+" in line and ("execute" in line.lower() or "cursor" in line.lower()):
                issues.append({
                    "id": "SEC005", "severity": "high", "line": number,
                    "function": "module",
                    "message": "Possible SQL query construction using string concatenation.",
                    "fix": "Use parameterized queries instead of string concatenation.",
                })

    for node in ast.walk(tree):
        if isinstance(node, ast.ExceptHandler) and node.type is None:
            issues.append(_issue("SEC006", "medium", node, tree,
                "Bare except catches all exceptions.", "Catch specific exception types."))

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for default in node.args.defaults:
                if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                    issues.append({
                        "id": "SEC007", "severity": "low", "line": node.lineno,
                        "function": node.name,
                        "message": "Mutable default argument detected.",
                        "fix": "Use None as the default and create the mutable object inside the function.",
                    })

    for node in ast.walk(tree):
        if isinstance(node, ast.Assert):
            issues.append(_issue("SEC008", "low", node, tree,
                "assert statement used for runtime validation.",
                "Use explicit exception handling for security-critical validation."))

    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and _call_name(node) in {"load", "loads"}:
            if "pickle" in _attribute_chain(node):
                issues.append(_issue("SEC009", "high", node, tree,
                    "pickle deserialization can execute malicious payloads.",
                    "Avoid untrusted pickle data; use a safe serialization format."))

    for node in ast.walk(tree):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr == "load" and isinstance(node.func.value, ast.Name)
                and node.func.value.id == "yaml"):
            has_loader = any(k.arg == "Loader" for k in node.keywords)
            if not has_loader:
                issues.append(_issue("SEC010", "high", node, tree,
                    "yaml.load() used without an explicit safe loader.",
                    "Use yaml.safe_load() or SafeLoader."))

    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and _call_name(node) in {"random", "randint", "choice", "randrange"}:
            issues.append(_issue("SEC011", "medium", node, tree,
                "Standard random module may be insecure for security-sensitive values.",
                "Use the secrets module for security-sensitive random values."))

    url_pattern = re.compile(r"https?://|\b(?:\d{1,3}\.){3}\d{1,3}\b")
    for number, line in enumerate(lines, 1):
        if url_pattern.search(line):
            issues.append({
                "id": "SEC012", "severity": "low", "line": number,
                "function": "module", "message": "Hardcoded URL or IP address detected.",
                "fix": "Move environment-specific endpoints to configuration.",
            })
    return issues


def run_quality_analysis(source_code):
    findings = []
    try:
        tree = ast.parse(source_code)
    except SyntaxError:
        return findings

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            branches = sum(isinstance(child, (ast.If, ast.For, ast.While, ast.AsyncFor, ast.Try, ast.IfExp))
                           for child in ast.walk(node))
            if branches > 10:
                findings.append({"id": "P002", "severity": "warning", "line": node.lineno,
                                 "function": node.name, "message": "High control-flow complexity."})
            if _max_control_depth(node) >= 4:
                findings.append({"id": "P005", "severity": "warning", "line": node.lineno,
                                 "function": node.name, "message": "Deep control-flow nesting."})
    return findings


def _issue(pattern_id, severity, node, tree, message, fix):
    return {"id": pattern_id, "severity": severity, "line": node.lineno,
            "function": _find_function(tree, node.lineno), "message": message, "fix": fix}


def _call_name(node):
    if isinstance(node.func, ast.Name):
        return node.func.id
    if isinstance(node.func, ast.Attribute):
        return node.func.attr
    return ""


def _attribute_chain(node):
    names = []
    current = node.func if isinstance(node, ast.Call) else node
    while isinstance(current, ast.Attribute):
        names.append(current.attr)
        current = current.value
    if isinstance(current, ast.Name):
        names.append(current.id)
    return names


def _find_function(tree, line_number):
    current = "module"
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            end_line = getattr(node, "end_lineno", node.lineno)
            if node.lineno <= line_number <= end_line:
                current = node.name
    return current


def _max_control_depth(node):
    def walk(current, depth):
        best = depth
        for child in ast.iter_child_nodes(current):
            child_depth = depth + 1 if isinstance(child, (ast.If, ast.For, ast.While, ast.AsyncFor, ast.Try)) else depth
            best = max(best, walk(child, child_depth))
        return best
    return walk(node, 0)
