"""Shared AST provenance helpers for security-sensitive data flows."""

import ast
from typing import Any


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
                aliases[alias.asname or alias.name] = ".".join(
                    part for part in (module, alias.name) if part
                )
    return aliases


def _canonical_name(node: ast.expr, aliases: dict[str, str]) -> str:
    if isinstance(node, ast.Name):
        return aliases.get(node.id, node.id)
    if isinstance(node, ast.Attribute):
        base = _canonical_name(node.value, aliases)
        return f"{base}.{node.attr}" if base else node.attr
    return ""


def _request_source(call: ast.Call, aliases: dict[str, str]) -> dict[str, Any] | None:
    name = _canonical_name(call.func, aliases)
    if not name.startswith("flask.request."):
        return None
    return {
        "line": getattr(call, "lineno", 0),
        "description": f"Flask request data read by {name}",
        "confidence": "high",
    }


def _scope_nodes(root: ast.AST) -> list[ast.AST]:
    class ScopeVisitor(ast.NodeVisitor):
        def __init__(self) -> None:
            self.nodes = []

        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
            self.nodes.append(node)
            if node is root:
                for child in node.body:
                    self.visit(child)

        def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
            self.nodes.append(node)
            if node is root:
                for child in node.body:
                    self.visit(child)

        def visit_Lambda(self, node: ast.Lambda) -> None:
            self.nodes.append(node)
            if node is root:
                self.visit(node.body)

        def visit_ClassDef(self, node: ast.ClassDef) -> None:
            self.nodes.append(node)
            if node is root:
                for child in node.body:
                    self.visit(child)

        def generic_visit(self, node: ast.AST) -> None:
            self.nodes.append(node)
            super().generic_visit(node)

    visitor = ScopeVisitor()
    visitor.visit(root)
    return sorted(
        visitor.nodes,
        key=lambda node: (
            getattr(node, "lineno", 0),
            getattr(node, "col_offset", 0),
        ),
    )


def _scope_roots(tree: ast.AST) -> list[ast.AST]:
    return [
        tree,
        *(
            node
            for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
        ),
    ]


def _expression_sources(
    node: ast.AST,
    tracked: dict[str, dict[str, Any]],
    aliases: dict[str, str],
) -> list[dict[str, Any]]:
    sources = {}
    for child in ast.walk(node):
        if isinstance(child, ast.Call):
            source = _request_source(child, aliases)
            if source:
                sources[(source["line"], source["description"])] = source
        elif isinstance(child, ast.Name) and child.id in tracked:
            state = tracked[child.id]
            for source in state["sources"]:
                sources[(source["line"], source["description"])] = source
    return list(sources.values())


def find_dynamic_template_flows(tree: ast.AST, source_code: str) -> list[dict[str, Any]]:
    """Track Flask request values through assignments into render_template_string."""
    aliases = _import_aliases(tree)
    source_lines = source_code.splitlines()
    findings = []

    for root in _scope_roots(tree):
        tracked: dict[str, dict[str, Any]] = {}
        for node in _scope_nodes(root):
            if isinstance(node, (ast.Assign, ast.AnnAssign)):
                value = node.value
                if value is None:
                    continue
                sources = _expression_sources(value, tracked, aliases)
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                for target in targets:
                    if not isinstance(target, ast.Name):
                        continue
                    if sources:
                        tracked[target.id] = {
                            "sources": sources,
                            "template_line": getattr(node, "lineno", 0),
                        }
                    else:
                        tracked.pop(target.id, None)
            elif isinstance(node, ast.AugAssign) and isinstance(node.target, ast.Name):
                sources = _expression_sources(node.value, tracked, aliases)
                previous = tracked.get(node.target.id, {}).get("sources", [])
                combined = {
                    (source["line"], source["description"]): source
                    for source in [*previous, *sources]
                }
                if combined:
                    tracked[node.target.id] = {
                        "sources": list(combined.values()),
                        "template_line": getattr(node, "lineno", 0),
                    }
            elif isinstance(node, ast.Call):
                call_name = _canonical_name(node.func, aliases)
                if not call_name.endswith("render_template_string") or not node.args:
                    continue
                sources = _expression_sources(node.args[0], tracked, aliases)
                if not sources:
                    continue
                sink_line = getattr(node, "lineno", 0)
                template_line = getattr(node.args[0], "lineno", sink_line)
                if isinstance(node.args[0], ast.Name):
                    template_line = tracked.get(node.args[0].id, {}).get(
                        "template_line", template_line
                    )
                code = (
                    source_lines[sink_line - 1].strip()
                    if 0 < sink_line <= len(source_lines)
                    else ast.unparse(node)
                )
                findings.append(
                    {
                        "source_line": min(source["line"] for source in sources),
                        "source": "; ".join(source["description"] for source in sources),
                        "confidence": "high",
                        "template_line": template_line,
                        "sink_line": sink_line,
                        "sink": call_name,
                        "code": code,
                        "sources": sources,
                    }
                )

    unique = {}
    for finding in findings:
        key = (finding["source_line"], finding["sink_line"], finding["sink"])
        unique[key] = finding
    return list(unique.values())


def find_sql_source_evidence(tree: ast.AST, line: int) -> dict[str, Any]:
    """Describe SQL interpolation provenance without assuming a parameter is external."""
    aliases = _import_aliases(tree)
    dynamic_nodes = [
        node
        for node in ast.walk(tree)
        if getattr(node, "lineno", None) == line
        and isinstance(node, (ast.JoinedStr, ast.BinOp, ast.Call, ast.AugAssign))
    ]
    names = {
        child.id
        for node in dynamic_nodes
        for child in ast.walk(node)
        if isinstance(child, ast.Name)
    }
    for node in dynamic_nodes:
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                source = _request_source(child, aliases)
                if source:
                    return {
                        "source_line": source["line"],
                        "source": source["description"],
                        "confidence": source["confidence"],
                    }
    for function in ast.walk(tree):
        if not isinstance(function, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        arguments = (
            function.args.posonlyargs
            + function.args.args
            + function.args.kwonlyargs
        )
        if function.args.vararg:
            arguments.append(function.args.vararg)
        if function.args.kwarg:
            arguments.append(function.args.kwarg)
        parameter = next((arg.arg for arg in arguments if arg.arg in names), None)
        if parameter:
            return {
                "source_line": function.lineno,
                "source": (
                    f"Function parameter '{parameter}' (external origin is not shown)"
                ),
                "confidence": "medium",
            }
    return {
        "source_line": line,
        "source": "Dynamic value origin is not established by the submitted source",
        "confidence": "low",
    }
