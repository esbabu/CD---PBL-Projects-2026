"""
Source helpers for the fix agent
=================================
Everything the strategies need to edit code *exactly*, using only positions
from Python's own ``ast`` (no regular expressions on raw source):

* ``function_node``  — the ``def`` a finding's qualified name refers to
                       (``Repository.search``, ``closure_capture.inner``)
* ``allowed_lines``  — the 1-based lines a patch for that finding may touch
* ``calls_at``       — the call nodes at a finding's line (sink candidates)
* ``import_aliases`` / ``canonical`` — resolve ``sp.call`` → ``subprocess.call``
* ``Edit`` / ``apply_edits`` — replace node spans; ``col_offset`` values are
                       UTF-8 byte offsets, so edits are done on encoded lines
* ``ensure_import``  — add ``import x`` after the existing top-level imports
"""
from __future__ import annotations

import ast
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Set

FunctionNode = (ast.FunctionDef, ast.AsyncFunctionDef)


# ---------------------------------------------------------------------------
# Functions and line spans
# ---------------------------------------------------------------------------

def _walk_defs(body, prefix: str = ""):
    """(qualname, node) for every function and class, nested ones included."""
    for node in body:
        if isinstance(node, FunctionNode + (ast.ClassDef,)):
            q = f"{prefix}{node.name}"
            yield q, node
            yield from _walk_defs(node.body, q + ".")
        elif isinstance(node, (ast.If, ast.Try, ast.With, ast.For, ast.While)):
            # defs inside module-level if/try blocks keep the enclosing prefix
            for field in ("body", "orelse", "finalbody", "handlers"):
                yield from _walk_defs(getattr(node, field, []) or [], prefix)
        elif isinstance(node, ast.ExceptHandler):
            yield from _walk_defs(node.body, prefix)


def function_node(tree: ast.Module, qualname: str) -> Optional[ast.AST]:
    """The ``def`` named by the analyzer's qualified name, or None (module level)."""
    for q, node in _walk_defs(tree.body):
        if q == qualname and isinstance(node, FunctionNode):
            return node
    return None


def node_span(node: ast.AST) -> range:
    """1-based lines of a def including its decorators."""
    start = min([node.lineno] + [d.lineno for d in getattr(node, "decorator_list", [])])
    return range(start, node.end_lineno + 1)


def allowed_lines(tree: ast.Module, qualname: str, n_lines: int) -> Set[int]:
    """
    Lines a patch for a finding in ``qualname`` may change: the body of that
    function, or — for module-level findings — every line outside a def/class.
    """
    node = function_node(tree, qualname)
    if node is not None:
        return set(node_span(node))
    inside = set()
    for top in tree.body:
        if isinstance(top, FunctionNode + (ast.ClassDef,)):
            inside.update(node_span(top))
    return set(range(1, n_lines + 1)) - inside


def scope_nodes(tree: ast.Module, qualname: str) -> List[ast.AST]:
    """The statements that belong to the finding's scope (function body or module body)."""
    node = function_node(tree, qualname)
    if node is not None:
        return list(node.body)
    return [s for s in tree.body if not isinstance(s, FunctionNode + (ast.ClassDef,))]


def walk_scope(stmts: Iterable[ast.AST]):
    """ast.walk over statements without descending into nested defs, classes or lambdas."""
    stack = list(stmts)
    while stack:
        node = stack.pop()
        yield node
        for child in ast.iter_child_nodes(node):
            if not isinstance(child, FunctionNode + (ast.ClassDef, ast.Lambda)):
                stack.append(child)


def calls_at(tree: ast.Module, qualname: str, line: int, col: Optional[int] = None) -> List[ast.Call]:
    """Calls in the finding's scope that start on ``line`` (exact column first)."""
    calls = [n for n in walk_scope(scope_nodes(tree, qualname))
             if isinstance(n, ast.Call) and n.lineno == line]
    calls.sort(key=lambda c: (c.col_offset != col, c.col_offset))
    return calls


# ---------------------------------------------------------------------------
# Names
# ---------------------------------------------------------------------------

def import_aliases(tree: ast.Module) -> Dict[str, str]:
    """Local name → dotted name for every import in the module."""
    out: Dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                if a.asname:
                    out[a.asname] = a.name
                else:
                    root = a.name.split(".")[0]
                    out.setdefault(root, root)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            for a in node.names:
                out[a.asname or a.name] = f"{node.module}.{a.name}"
    return out


def canonical(expr: ast.AST, aliases: Dict[str, str]) -> str:
    """Dotted name of ``expr`` with import aliases resolved ('' if not a plain name chain)."""
    parts = []
    while isinstance(expr, ast.Attribute):
        parts.append(expr.attr)
        expr = expr.value
    if not isinstance(expr, ast.Name):
        return ""
    parts.append(aliases.get(expr.id, expr.id))
    return ".".join(reversed(parts))


def module_name_for(tree: ast.Module, module: str) -> Optional[str]:
    """The local name under which ``module`` itself is imported (``import yaml`` → 'yaml')."""
    for node in tree.body:
        if isinstance(node, ast.Import):
            for a in node.names:
                if a.name == module:
                    return a.asname or a.name
    return None


def imported_modules(tree: ast.Module) -> Set[str]:
    """Top-level package names imported anywhere in the module."""
    mods = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            mods.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            mods.add(node.module.split(".")[0])
    return mods


# ---------------------------------------------------------------------------
# Exact edits
# ---------------------------------------------------------------------------

@dataclass
class Edit:
    """Replace the text between two (1-based line, byte column) positions."""
    line: int
    col: int
    end_line: int
    end_col: int
    text: str

    @classmethod
    def replace(cls, node: ast.AST, text: str) -> "Edit":
        return cls(node.lineno, node.col_offset, node.end_lineno, node.end_col_offset, text)

    @classmethod
    def insert(cls, line: int, col: int, text: str) -> "Edit":
        return cls(line, col, line, col, text)


def apply_edits(source: str, edits: List[Edit]) -> str:
    """Apply non-overlapping edits (positions refer to the unedited source)."""
    lines = [l.encode("utf-8") for l in source.splitlines(keepends=True)]
    ordered = sorted(edits, key=lambda e: (e.line, e.col), reverse=True)
    for a, b in zip(ordered[1:], ordered):
        if (a.end_line, a.end_col) > (b.line, b.col):
            raise ValueError("overlapping edits")
    for e in ordered:
        head = lines[e.line - 1][:e.col]
        tail = lines[e.end_line - 1][e.end_col:]
        lines[e.line - 1:e.end_line] = [head + e.text.encode("utf-8") + tail]
    return b"".join(lines).decode("utf-8")


def segment(source: str, node: ast.AST) -> str:
    return ast.get_source_segment(source, node) or ast.unparse(node)


def line_indent(source: str, line: int) -> str:
    text = source.splitlines()[line - 1]
    return text[:len(text) - len(text.lstrip())]


def ensure_import(source: str, module: str) -> str:
    """Add ``import module`` unless the module is already imported under its own name."""
    tree = ast.parse(source)
    if module_name_for(tree, module) == module:
        return source
    insert_after = 0
    for node in tree.body:
        is_doc = (isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant)
                  and isinstance(node.value.value, str) and node is tree.body[0])
        if isinstance(node, (ast.Import, ast.ImportFrom)) or is_doc:
            insert_after = node.end_lineno
        else:
            break
    lines = source.splitlines(keepends=True)
    if lines and not lines[-1].endswith("\n"):
        lines[-1] += "\n"
    lines.insert(insert_after, f"import {module}\n")
    return "".join(lines)


def py_string(text: str) -> str:
    """A Python string literal for ``text``, preferring double quotes."""
    if '"' not in text and "\\" not in text and "\n" not in text:
        return f'"{text}"'
    return repr(text)
