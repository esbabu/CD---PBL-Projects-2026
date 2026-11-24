"""Tree-sitter parsing utilities shared across JavaScript, C, and C++."""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Iterator

from tree_sitter import Language, Node, Parser, Tree


@lru_cache(maxsize=8)
def get_ts_language(lang: str) -> Language:
    key = lang.lower()
    if key in ("js", "javascript"):
        import tree_sitter_javascript as tsjs
        return Language(tsjs.language())
    if key == "c":
        import tree_sitter_c as tsc
        return Language(tsc.language())
    if key in ("cpp", "c++", "cxx"):
        import tree_sitter_cpp as tscpp
        return Language(tscpp.language())
    raise ValueError(f"Unsupported tree-sitter language: {lang}")


def parse_source(source: str, lang: str) -> tuple[Tree, bytes]:
    """Parse source code with tree-sitter and return (tree, utf8_bytes)."""
    ts_lang = get_ts_language(lang)
    parser = Parser(ts_lang)
    src_bytes = source.encode("utf-8")
    tree = parser.parse(src_bytes)
    return tree, src_bytes


def node_text(node: Node, src_bytes: bytes) -> str:
    return src_bytes[node.start_byte:node.end_byte].decode("utf-8", errors="replace")


def walk(node: Node) -> Iterator[Node]:
    """Depth-first pre-order traversal of a tree-sitter subtree."""
    stack = [node]
    while stack:
        cur = stack.pop()
        yield cur
        children = cur.children
        for ch in reversed(children):
            stack.append(ch)


@dataclass
class FunctionSpan:
    name: str
    node: Node
    start_line: int      # 1-based
    end_line: int        # 1-based
    body_node: Node | None = None


def _c_declarator_name(node: Node, src_bytes: bytes) -> str | None:
    """Extract function identifier from C/C++ function_declarator subtree."""
    if node.type in ("identifier", "field_identifier", "destructor_name"):
        return node_text(node, src_bytes)
    if node.type == "qualified_identifier":
        return node_text(node, src_bytes)
    # Prefer direct declarator child
    decl = node.child_by_field_name("declarator")
    if decl is not None:
        return _c_declarator_name(decl, src_bytes)
    for ch in node.children:
        if ch.type in ("function_declarator", "pointer_declarator", "reference_declarator",
                       "parenthesized_declarator", "identifier", "qualified_identifier"):
            found = _c_declarator_name(ch, src_bytes)
            if found:
                return found
    return None


def find_functions(tree: Tree, src_bytes: bytes, lang: str) -> dict[str, FunctionSpan]:
    """Locate named functions in JS, C, or C++ source."""
    out: dict[str, FunctionSpan] = {}
    key = lang.lower()

    if key in ("js", "javascript"):
        for node in walk(tree.root_node):
            if node.type in ("function_declaration", "generator_function_declaration"):
                name_node = node.child_by_field_name("name")
                if name_node is not None:
                    name = node_text(name_node, src_bytes)
                    out[name] = FunctionSpan(
                        name=name,
                        node=node,
                        start_line=node.start_point[0] + 1,
                        end_line=node.end_point[0] + 1,
                        body_node=node.child_by_field_name("body"),
                    )
            elif node.type == "variable_declarator":
                name_node = node.child_by_field_name("name")
                val_node = node.child_by_field_name("value")
                if name_node is not None and val_node is not None and val_node.type in (
                    "arrow_function", "function_expression", "function", "generator_function"
                ):
                    name = node_text(name_node, src_bytes)
                    out[name] = FunctionSpan(
                        name=name,
                        node=val_node,
                        start_line=node.start_point[0] + 1,
                        end_line=val_node.end_point[0] + 1,
                        body_node=val_node.child_by_field_name("body"),
                    )
        return out

    # C / C++
    for node in walk(tree.root_node):
        if node.type == "function_definition":
            decl = node.child_by_field_name("declarator")
            if decl is None:
                continue
            name = _c_declarator_name(decl, src_bytes)
            if name:
                # Strip namespace qualifiers for lookup if simple name
                simple = name.split("::")[-1]
                out[simple] = FunctionSpan(
                    name=simple,
                    node=node,
                    start_line=node.start_point[0] + 1,
                    end_line=node.end_point[0] + 1,
                    body_node=node.child_by_field_name("body"),
                )
    return out


_STMT_TYPES = {
    # JS
    "expression_statement", "variable_declaration", "lexical_declaration",
    "return_statement", "if_statement", "for_statement", "for_in_statement",
    "while_statement", "do_statement", "switch_statement", "throw_statement",
    "break_statement", "continue_statement",
    # C / C++
    "declaration", "for_range_loop", "compound_assignment_expression",
    "case_statement", "goto_statement",
}


def executable_statement_lines(source: str, lang: str, reachable: set[str]) -> set[int]:
    """Return 1-based line numbers of executable statements inside reachable functions."""
    tree, src_bytes = parse_source(source, lang)
    spans = find_functions(tree, src_bytes, lang)
    lines: set[int] = set()
    for name in reachable:
        span = spans.get(name)
        if not span:
            continue
        body = span.body_node or span.node
        for sub in walk(body):
            if sub.type in _STMT_TYPES:
                lines.add(sub.start_point[0] + 1)
    return lines
