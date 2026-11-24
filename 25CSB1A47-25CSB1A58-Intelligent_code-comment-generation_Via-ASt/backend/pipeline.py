"""Orchestrates analysis, code generation, and scoring."""

import ast

from backend.ast_analyzer import analyze_code
from backend.code_analysis import _fallback_comment_code, generate_commented_code
from backend.rules import apply_rules, build_review_score, summarize_quality
from backend.validator import validate_generated_code


def _security_control_comments(source_code, controls):
    """Return AST-anchored explanations for defensive controls in the candidate."""
    if not controls:
        return source_code, []

    control_text = " ".join(str(control).lower() for control in controls)
    tree = ast.parse(source_code)
    comments_by_line = {}
    sql_literals = {}

    def is_sql_query(value):
        lowered = value.lstrip().lower()
        return (
            lowered.startswith(("select ", "insert ", "update ", "delete ", "replace "))
            and any(marker in value for marker in ("?", "%s", ":"))
        )

    for candidate in ast.walk(tree):
        if (
            isinstance(candidate, (ast.Assign, ast.AnnAssign))
            and isinstance(candidate.value, ast.Constant)
            and isinstance(candidate.value.value, str)
        ):
            targets = (
                candidate.targets
                if isinstance(candidate, ast.Assign)
                else [candidate.target]
            )
            for target in targets:
                if isinstance(target, ast.Name):
                    sql_literals[target.id] = candidate.value.value

    def call_name(node):
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            prefix = call_name(node.value)
            return f"{prefix}.{node.attr}" if prefix else node.attr
        return ""

    def query_value(node):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value
        if isinstance(node, ast.Name):
            return sql_literals.get(node.id, "")
        return ""

    def add(node, message):
        line = getattr(node, "lineno", None)
        if line is None:
            return
        comment = f"# [AST-SECURITY] {message}"
        comments_by_line.setdefault(line, [])
        if comment not in comments_by_line[line]:
            comments_by_line[line].append(comment)

    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            imported = (
                [alias.name for alias in node.names]
                if isinstance(node, ast.Import)
                else [node.module or ""]
            )
            if (
                "defusedxml" in control_text
                and any(name.startswith("defusedxml") for name in imported)
            ):
                add(node, "Uses defusedxml to harden XML parsing against entity expansion.")
        elif isinstance(node, ast.Call):
            name = call_name(node.func).lower()
            if (
                any(
                    marker in control_text
                    for marker in (
                        "parameterized sql",
                        "parameterized quer",
                        "prepared statement",
                        "cwe-89",
                    )
                )
                and name.endswith(".execute")
                and len(node.args) >= 2
                and is_sql_query(query_value(node.args[0]))
            ):
                add(
                    node,
                    "Binds SQL values separately from the query using parameter placeholders.",
                )
            if (
                "safe subprocess" in control_text
                and name.startswith("subprocess.")
                and any(
                    keyword.arg == "shell"
                    and isinstance(keyword.value, ast.Constant)
                    and keyword.value.value is False
                    for keyword in node.keywords
                )
                and any(
                    isinstance(child, ast.Call)
                    and call_name(child.func).lower() == "shlex.split"
                    for child in ast.walk(node)
                )
            ):
                add(node, "Tokenizes command arguments with shlex.split and disables shell execution.")
            if "environment variable secret" in control_text and name == "os.getenv":
                add(node, "Reads configuration from the environment instead of embedding a secret.")
            if (
                ("path basename" in control_text or "os.path.basename" in control_text)
                and name == "os.path.basename"
            ):
                add(node, "Sanitizes the path component with os.path.basename before filesystem access.")
            if (
                "safe json" in control_text
                and name in {"json.load", "json.loads", "yaml.safe_load"}
            ):
                add(node, "Uses a data-only deserializer instead of unsafe object deserialization.")
            if (
                "tls" in control_text
                and name.startswith(("requests.", "httpx."))
                and any(
                    keyword.arg == "verify"
                    and isinstance(keyword.value, ast.Constant)
                    and keyword.value.value is True
                    for keyword in node.keywords
                )
            ):
                add(node, "Enforces TLS certificate verification for this network request.")
            if (
                "sha-256" in control_text
                and name in {"hashlib.sha256", "sha256"}
            ):
                add(node, "Uses SHA-256 rather than a deprecated weak hash.")
            if (
                "namedtemporaryfile" in control_text
                and name.endswith("namedtemporaryfile")
            ):
                add(node, "Creates a temporary file atomically to avoid name-allocation races.")
            if (
                ("redos" in control_text or "regular expression" in control_text)
                and name == "re.compile"
            ):
                add(node, "Uses the remediated regular-expression pattern to reduce backtracking risk.")
            if (
                "ast literal parsing" in control_text
                and name == "ast.literal_eval"
            ):
                add(node, "Parses a Python literal without evaluating arbitrary code.")
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            names = {
                target.id.lower() for target in targets if isinstance(target, ast.Name)
            }
            if (
                "debug mode disablement" in control_text
                and names.intersection({"debug"})
                and isinstance(node.value, ast.Constant)
                and node.value.value is False
            ):
                add(node, "Disables debug mode to avoid exposing interactive consoles and tracebacks.")

    if not comments_by_line:
        return source_code, []

    lines = source_code.splitlines(keepends=True)
    annotated = []
    emitted = []
    for line_number, line in enumerate(lines, start=1):
        for comment in comments_by_line.get(line_number, []):
            if comment not in line:
                ending = "\r\n" if line.endswith("\r\n") else "\n"
                annotated.append(" " * (len(line) - len(line.lstrip())) + comment + ending)
                emitted.append(comment)
        annotated.append(line)
    return "".join(annotated), emitted

    return "".join(annotated), emitted


def run_pipeline(
    source_code: str,
    analysis: dict | None = None,
    docstring_style: str | None = None,
    security_controls: list[str] | None = None,
) -> dict:
    """Analyze source, generate comments, and score findings.

    Routes may pass an existing analysis when they have already performed
    preflight checks, avoiding a second AST walk for the same source.
    """
    if analysis is None:
        analysis = analyze_code(source_code)

    warnings = analysis.get("warnings")
    if warnings is None:
        warnings = apply_rules(analysis)
    analysis["warnings"] = warnings

    generation_source, required_security_comments = _security_control_comments(
        source_code, security_controls
    )
    commented_code, method = generate_commented_code(
        generation_source, analysis, docstring_style=docstring_style
    )
    if any(comment not in commented_code for comment in required_security_comments):
        commented_code = _fallback_comment_code(
            generation_source, analysis, docstring_style=docstring_style
        )
        method = "ast"
    validation = validate_generated_code(source_code, commented_code)
    if method == "ast" and analysis.get("type_errors"):
        generation_notice = (
            "Definite type errors were detected, so deterministic AST comments "
            "were used instead of AI-generated comments."
        )
    elif method == "ast" and required_security_comments:
        generation_notice = (
            "Deterministic AST comments were used to preserve verified defensive "
            "control annotations."
        )
    elif method == "ast":
        generation_notice = (
            "The AI provider was unavailable or returned unusable comments, "
            "so detailed deterministic AST comments were generated instead."
        )
        generation_notice += (
            " Check the API key and provider credits to restore AI-generated "
            "comments."
        )
    else:
        generation_notice = None

    quality_summary = summarize_quality(warnings)
    quality_score = quality_summary["score"]
    review_score = build_review_score(warnings)

    return {
        "commented_code": commented_code,
        "source": source_code,
        "quality_score": quality_score,
        "quality_summary": quality_summary,
        "review_score": review_score,
        "analysis": analysis,
        "validation": validation,
        "method": method,
        "generation_notice": generation_notice,
    }
