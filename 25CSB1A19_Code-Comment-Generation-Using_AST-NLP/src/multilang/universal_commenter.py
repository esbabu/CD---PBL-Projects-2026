"""Multi-language rule-based documentation generator.

Supported source languages: Python, C, C++, Java, JavaScript and TypeScript.
Tree-sitter is used when installed; a conservative declaration scanner is kept as
an offline fallback. The non-Python path is rule-based (the T5/Neurosymbolic
models in this project remain Python-AST specific).
"""
from __future__ import annotations

from pathlib import Path
import re
from typing import Optional

try:
    from tree_sitter_language_pack import get_parser as _get_tree_sitter_parser
except Exception:  # Optional dependency; fallback scanner remains available.
    _get_tree_sitter_parser = None


SUPPORTED_LANGUAGES = {
    ".py": "python", ".pyw": "python",
    ".c": "c", ".h": "c",
    ".cc": "cpp", ".cpp": "cpp", ".cxx": "cpp", ".hpp": "cpp", ".hh": "cpp", ".hxx": "cpp",
    ".java": "java",
    ".js": "javascript", ".jsx": "javascript", ".mjs": "javascript", ".cjs": "javascript",
    ".ts": "typescript", ".tsx": "tsx", ".mts": "typescript", ".cts": "typescript",
}

LANGUAGE_LABELS = {
    "python": "Python", "c": "C", "cpp": "C++", "java": "Java",
    "javascript": "JavaScript", "typescript": "TypeScript", "tsx": "TypeScript (TSX)",
}

TARGET_NODE_TYPES = {
    "python": {"function_definition", "class_definition"},
    "c": {"function_definition"},
    "cpp": {"function_definition", "class_specifier", "struct_specifier"},
    "java": {"method_declaration", "constructor_declaration", "class_declaration", "interface_declaration", "enum_declaration"},
    "javascript": {"function_declaration", "generator_function_declaration", "method_definition", "class_declaration"},
    "typescript": {"function_declaration", "generator_function_declaration", "method_definition", "class_declaration", "abstract_class_declaration"},
    "tsx": {"function_declaration", "generator_function_declaration", "method_definition", "class_declaration", "abstract_class_declaration"},
}


class UniversalCommenter:
    def __init__(self):
        self.parser_cache = {}

    def detect_language(self, filename=None, code=None):
        if filename:
            language = SUPPORTED_LANGUAGES.get(Path(filename).suffix.lower())
            if language:
                return language
        if not code:
            return None
        samples = code[:8000]
        if re.search(r"^\s*(?:async\s+)?def\s+\w+\s*\(|^\s*class\s+\w+\s*[:(]", samples, re.M):
            return "python"
        if re.search(r"\b(public|private|protected)\s+(static\s+)?(class|interface|enum)\b|public\s+static\s+void\s+main\s*\(", samples):
            return "java"
        if re.search(r"\b(namespace|template\s*<|std::|cout\s*<<)\b", samples):
            return "cpp"
        if re.search(r"\b(int|void|char|float|double)\s+\w+\s*\([^;{}]*\)\s*\{", samples):
            return "c"
        if re.search(r"\b(interface|type)\s+\w+\s*(?:=|\{)|:\s*(string|number|boolean)\b", samples):
            return "typescript"
        if re.search(r"\b(function\s+\w+|const\s+\w+\s*=\s*(?:async\s*)?\([^)]*\)\s*=>|console\.log\s*\()", samples):
            return "javascript"
        return None

    def get_parser(self, language):
        if _get_tree_sitter_parser is None:
            return None
        if language not in self.parser_cache:
            aliases = {"tsx": "tsx"}
            self.parser_cache[language] = _get_tree_sitter_parser(aliases.get(language, language))
        return self.parser_cache[language]

    def parse_code(self, code, language):
        source_bytes = code.encode("utf-8")
        try:
            parser = self.get_parser(language)
        except Exception:
            # A grammar may not yet be downloaded/cached. Use the fallback scanner
            # and report that limitation instead of crashing the whole GUI.
            parser = None
        if parser is None:
            return None, source_bytes
        tree = parser.parse(source_bytes)
        return tree, source_bytes

    @staticmethod
    def _node_text(node, source_bytes):
        return source_bytes[node.start_byte:node.end_byte].decode("utf-8", errors="replace")

    def _extract_name(self, node, source_bytes):
        name_node = node.child_by_field_name("name")
        if name_node is not None:
            return self._node_text(name_node, source_bytes)
        declarator = node.child_by_field_name("declarator")
        if declarator is not None:
            stack = [declarator]
            while stack:
                current = stack.pop(0)
                if current.type in {"identifier", "field_identifier", "type_identifier", "operator_name"}:
                    return self._node_text(current, source_bytes)
                stack[0:0] = list(current.children)
        # Function pointer and grammar variants: first identifier on declaration head.
        for child in node.children:
            if child.type in {"identifier", "type_identifier", "field_identifier"}:
                return self._node_text(child, source_bytes)
        return "unnamed"

    @staticmethod
    def _humanize(name):
        words = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", name).replace("_", " ").strip()
        return re.sub(r"\s+", " ", words).capitalize() or "the operation"

    def _describe_node(self, node, source_bytes):
        name = self._extract_name(node, source_bytes)
        low = node.type.lower()
        if "class" in low or "struct" in low or "interface" in low or "enum" in low:
            return name, f"Defines the {self._humanize(name)} type."
        if "constructor" in low:
            return name, f"Initializes an instance of {self._humanize(name)}."
        body = node.child_by_field_name("body")
        body_text = self._node_text(body, source_bytes) if body is not None else self._node_text(node, source_bytes)
        summary = f"Performs the {self._humanize(name)} operation."
        if re.search(r"\breturn\b", body_text):
            summary = f"Performs the {self._humanize(name)} operation and returns a result."
        return name, summary

    def _tree_sitter_targets(self, root, language, source_bytes):
        wanted = TARGET_NODE_TYPES.get(language, set())
        targets = []
        stack = [root]
        while stack:
            node = stack.pop()
            if node.type in wanted:
                name, description = self._describe_node(node, source_bytes)
                node_text = self._node_text(node, source_bytes)
                signature = node_text.split("{", 1)[0].split(":", 1)[0].strip()
                targets.append({"type": node.type, "name": name, "description": description,
                                "signature": signature, "start_line": node.start_point.row,
                                "start_byte": node.start_byte, "end_byte": node.end_byte,
                                "parser": "tree-sitter"})
            # Arrow functions are commonly attached to variable declarators.
            if language in {"javascript", "typescript", "tsx"} and node.type == "variable_declarator":
                value = node.child_by_field_name("value")
                name_node = node.child_by_field_name("name")
                if value is not None and value.type in {"arrow_function", "function_expression", "generator_function"} and name_node is not None:
                    name = self._node_text(name_node, source_bytes)
                    node_text = self._node_text(node, source_bytes)
                    targets.append({"type": "arrow_function", "name": name,
                                    "description": f"Performs the {self._humanize(name)} operation.",
                                    "signature": node_text.split("=>", 1)[0].strip(),
                                    "start_line": node.start_point.row, "start_byte": node.start_byte,
                                    "end_byte": node.end_byte, "parser": "tree-sitter"})
            stack.extend(reversed(node.children))
        # Avoid duplicates caused by wrapper nodes and nested grammar nodes.
        seen, unique = set(), []
        for target in sorted(targets, key=lambda x: (x["start_line"], x["name"])):
            key = (target["start_line"], target["name"], target["type"])
            if key not in seen:
                seen.add(key); unique.append(target)
        return unique

    def _fallback_targets(self, code, language):
        """Conservative declaration scanner used when Tree-sitter is unavailable."""
        patterns = {
            "python": [
                (r"^\s*(?:async\s+)?def\s+([A-Za-z_]\w*)\s*\(", "function"),
                (r"^\s*class\s+([A-Za-z_]\w*)\b", "class"),
            ],
            "c": [(r"^\s*[\w:*&\s]+?\b([A-Za-z_]\w*)\s*\([^;{}]*\)\s*\{", "function")],
            "cpp": [(r"^\s*[\w:*&<>\s]+?\b([A-Za-z_]\w*)\s*\([^;{}]*\)\s*(?:const\s*)?\{", "function"),
                    (r"^\s*(?:class|struct)\s+([A-Za-z_]\w*)\b", "class")],
            "java": [(r"^\s*(?:public|protected|private|static|final|abstract|synchronized|native|default|\s)+[\w<>.?\[\], ]+\s+([A-Za-z_]\w*)\s*\([^;{}]*\)\s*(?:throws\s+[\w., ]+)?\{", "function"),
                     (r"^\s*(?:public|protected|private)?\s*(?:abstract\s+)?(?:class|interface|enum)\s+([A-Za-z_]\w*)\b", "class")],
            "javascript": [(r"^\s*(?:export\s+)?(?:async\s+)?function\*?\s+([A-Za-z_$][\w$]*)\s*\(", "function"),
                           (r"^\s*(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?(?:\([^)]*\)|[A-Za-z_$][\w$]*)\s*=>", "function"),
                           (r"^\s*class\s+([A-Za-z_$][\w$]*)\b", "class")],
            "typescript": [(r"^\s*(?:export\s+)?(?:async\s+)?function\*?\s+([A-Za-z_$][\w$]*)\s*\(", "function"),
                            (r"^\s*(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?(?:\([^)]*\)|[A-Za-z_$][\w$]*)\s*=>", "function"),
                            (r"^\s*(?:export\s+)?(?:abstract\s+)?class\s+([A-Za-z_$][\w$]*)\b", "class"),
                            (r"^\s*(?:export\s+)?interface\s+([A-Za-z_$][\w$]*)\b", "class")],
            "tsx": [(r"^\s*(?:export\s+)?(?:async\s+)?function\*?\s+([A-Za-z_$][\w$]*)\s*\(", "function"),
                    (r"^\s*(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?(?:\([^)]*\)|[A-Za-z_$][\w$]*)\s*=>", "function"),
                    (r"^\s*(?:export\s+)?(?:abstract\s+)?class\s+([A-Za-z_$][\w$]*)\b", "class")],
        }
        targets = []
        lines = code.splitlines()
        for index, line in enumerate(lines):
            for pattern, kind in patterns.get(language, []):
                match = re.search(pattern, line)
                if match:
                    name = match.group(1)
                    description = (f"Defines the {self._humanize(name)} type." if kind == "class"
                                   else f"Performs the {self._humanize(name)} operation.")
                    targets.append({"type": kind, "name": name, "description": description,
                                    "signature": line.strip(), "start_line": index,
                                    "start_byte": None, "end_byte": None,
                                    "parser": "declaration-scan-fallback"})
                    break
        return targets

    @staticmethod
    def _comment_block(language, target):
        name = target["name"]
        summary = target["description"]
        if language == "python":
            return f"# {summary}"
        params = []
        sig = target.get("signature", "")
        match = re.search(r"\((.*?)\)", sig)
        if match:
            raw = match.group(1)
            for part in raw.split(","):
                candidate = re.sub(r"=.*$", "", part).strip()
                candidate = re.sub(r"^\.\.\.", "", candidate)
                if ":" in candidate:
                    candidate = candidate.split(":", 1)[0].strip()
                else:
                    candidate = candidate.split()[-1].strip() if candidate.split() else ""
                candidate = re.sub(r"[^A-Za-z0-9_$].*$", "", candidate)
                if candidate and candidate not in {"this", "self"} and candidate not in params:
                    params.append(candidate)
        lines = ["/**", f" * {summary}"]
        for param in params:
            lines.append(f" * @param {param} Parameter used by {name}.")
        lines.append(" */")
        return "\n".join(lines)

    @staticmethod
    def _has_preceding_comment(lines, line_index, language):
        idx = line_index - 1
        while idx >= 0 and not lines[idx].strip():
            idx -= 1
        if idx < 0:
            return False
        previous = lines[idx].lstrip()
        if language == "python":
            return previous.startswith("#")
        return previous.startswith(("//", "/*", "*", "*/"))

    def generate_comments(self, code, filename=None, language=None):
        language = language or self.detect_language(filename, code)
        if language not in TARGET_NODE_TYPES:
            raise ValueError("Unsupported or undetected language. Select Python, C, C++, Java, JavaScript or TypeScript.")
        tree, source_bytes = self.parse_code(code, language)
        parser_mode = "tree-sitter" if tree is not None else "declaration-scan-fallback"
        if tree is not None and tree.root_node.has_error:
            raise SyntaxError(f"The {LANGUAGE_LABELS.get(language, language)} source contains syntax errors. Fix them before generating comments.")
        targets = self._tree_sitter_targets(tree.root_node, language, source_bytes) if tree is not None else self._fallback_targets(code, language)
        lines = code.splitlines()
        insertions = {}
        for target in targets:
            line_index = target["start_line"]
            if line_index < 0 or line_index >= len(lines) or line_index in insertions:
                continue
            if self._has_preceding_comment(lines, line_index, language):
                continue
            original_line = lines[line_index]
            indentation = original_line[:len(original_line) - len(original_line.lstrip())]
            block = self._comment_block(language, target)
            insertions[line_index] = "\n".join(indentation + line for line in block.splitlines())
        output_lines = list(lines)
        for line_index in sorted(insertions, reverse=True):
            output_lines.insert(line_index, insertions[line_index])
        annotated = "\n".join(output_lines)
        report = {
            "language": language,
            "language_label": LANGUAGE_LABELS.get(language, language),
            "parser": parser_mode,
            "syntax_valid": True if tree is None else not tree.root_node.has_error,
            "total_targets": len(targets),
            "comments_generated": len(insertions),
            "targets": targets,
            "note": ("Tree-sitter parsing was used." if tree is not None else
                     "Tree-sitter grammar was unavailable; a conservative declaration scanner was used. Install requirements-multilang.txt and ensure the language grammar can be downloaded for stronger parsing."),
        }
        return annotated, report
