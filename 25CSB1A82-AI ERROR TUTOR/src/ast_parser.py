"""
AST Parser Module - Extracts code context using Abstract Syntax Tree
"""

import ast
import re
import builtins
from typing import Dict, List, Optional, Any


class ASTContextExtractor:
    """Extracts contextual information from Python code using AST."""

    def __init__(self):
        self.tree: Optional[ast.AST] = None
        self.source_lines: List[str] = []

    def parse(self, code: str) -> bool:
        self.source_lines = code.split('\n')
        try:
            self.tree = ast.parse(code)
            return True
        except SyntaxError:
            self.tree = None
            return False

    def get_context_at_line(self, line_number: int) -> Dict[str, Any]:
        if not self.tree:
            return self._get_fallback_context(line_number)

        context = {
            'line_number': line_number,
            'line_content': self._get_line(line_number),
            'enclosing_function': None,
            'enclosing_class': None,
            'node_type': None,
            'variables_in_scope': [],
            'imports': [],
            'function_calls': []
        }

        inside_function = False

        for node in ast.walk(self.tree):
            if not hasattr(node, 'lineno'):
                continue

            if node.lineno == line_number and context['node_type'] is None:
                context['node_type'] = type(node).__name__

            if isinstance(node, ast.FunctionDef):
                if self._node_contains_line(node, line_number):
                    context['enclosing_function'] = node.name
                    context['variables_in_scope'].extend(
                        self._get_function_variables(node)
                    )
                    inside_function = True

            elif isinstance(node, ast.ClassDef):
                if self._node_contains_line(node, line_number):
                    context['enclosing_class'] = node.name

            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                context['imports'].extend(self._get_imports(node))

            elif isinstance(node, ast.Call) and node.lineno == line_number:
                context['function_calls'].append(self._get_call_info(node))

        if not inside_function:
            context['variables_in_scope'] = self._get_module_level_variables(line_number)

        return context

    def _get_module_level_variables(self, up_to_line: int) -> List[str]:
        variables = []
        if not self.tree:
            return variables

        for node in ast.iter_child_nodes(self.tree):
            if not hasattr(node, 'lineno') or node.lineno > up_to_line:
                continue

            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id not in variables:
                        variables.append(target.id)

            elif isinstance(node, ast.FunctionDef):
                if node.name not in variables:
                    variables.append(node.name)

            elif isinstance(node, ast.ClassDef):
                if node.name not in variables:
                    variables.append(node.name)

        return variables

    def get_all_definitions(self) -> Dict[str, List[str]]:
        if not self.tree:
            return {'functions': [], 'classes': [], 'variables': []}

        definitions = {
            'functions': [],
            'classes': [],
            'variables': []
        }

        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef):
                definitions['functions'].append(node.name)
            elif isinstance(node, ast.ClassDef):
                definitions['classes'].append(node.name)
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        definitions['variables'].append(target.id)

        return definitions

    def analyze_error_context(self, error_info: Dict) -> Dict[str, Any]:
        code = error_info.get('full_code', '')
        line_num = error_info.get('line_number')

        self.parse(code)

        enhanced_context = {
            'error_type': error_info.get('error_type'),
            'error_message': error_info.get('message'),
            'line_number': line_num,
            'ast_context': self.get_context_at_line(line_num) if line_num else {},
            'definitions': self.get_all_definitions(),
            'similar_names': self._find_similar_names(error_info),
            'suggestions': self._generate_suggestions(error_info)
        }

        return enhanced_context

    def _get_line(self, line_number: int) -> str:
        if 1 <= line_number <= len(self.source_lines):
            return self.source_lines[line_number - 1]
        return ""

    def _node_contains_line(self, node: ast.AST, line: int) -> bool:
        if not hasattr(node, 'lineno') or not hasattr(node, 'end_lineno'):
            return False
        return node.lineno <= line <= (node.end_lineno or node.lineno)

    def _get_function_variables(self, func_node: ast.FunctionDef) -> List[str]:
        variables = [arg.arg for arg in func_node.args.args]

        for node in ast.walk(func_node):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        variables.append(target.id)

        return variables

    def _get_imports(self, node: ast.AST) -> List[str]:
        imports = []
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.extend(alias.name for alias in node.names)
        return imports

    def _get_call_info(self, node: ast.Call) -> Dict:
        call_info = {'name': None, 'args_count': len(node.args)}

        if isinstance(node.func, ast.Name):
            call_info['name'] = node.func.id
        elif isinstance(node.func, ast.Attribute):
            call_info['name'] = node.func.attr

        return call_info

    def _get_fallback_context(self, line_number: int) -> Dict[str, Any]:
        context = {
            'line_number': line_number,
            'line_content': self._get_line(line_number),
            'enclosing_function': 'unknown',
            'enclosing_class': 'unknown',
            'node_type': 'SyntaxError Fallback',
            'variables_in_scope': [],
            'imports': [],
            'function_calls': [],
            'parse_failed': True,
            'parser_used': 'Regex Fallback'
        }

        regex_vars = []
        for line in self.source_lines[:line_number]:
            match = re.match(r'^\s*([a-zA-Z_]\w*)\s*=', line)
            if match:
                regex_vars.append(match.group(1))

        context['variables_in_scope'] = list(set(regex_vars))
        return context

    def _find_similar_names(self, error_info: Dict) -> List[str]:
        if error_info.get('error_type') != 'NameError':
            return []

        message = error_info.get('message', '')
        if "name '" in message:
            undefined = message.split("'")[1]
            definitions = self.get_all_definitions()
            all_names = (definitions['functions'] +
                         definitions['classes'] +
                         definitions['variables'] +
                         dir(builtins))

            candidates = []
            for name in all_names:
                dist = self._levenshtein_distance(name, undefined)
                if dist <= 2:
                    candidates.append((name, dist))

            candidates.sort(key=lambda x: x[1])

            return [name for name, dist in candidates]

        return []

    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)

        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]

    def _generate_suggestions(self, error_info: Dict) -> List[str]:
        error_type = error_info.get('error_type', '')

        suggestion_map = {
            'SyntaxError': [
                "Check for missing colons after if/for/while/def/class statements",
                "Ensure all parentheses, brackets, and braces are properly closed",
                "Check for proper string quote matching"
            ],
            'IndentationError': [
                "Use consistent indentation (4 spaces recommended)",
                "Ensure code inside functions/loops is properly indented"
            ],
            'NameError': [
                "Check for typos in variable/function names",
                "Ensure the variable is defined before use",
                "Check if you need to import a module"
            ],
            'TypeError': [
                "Check the types of operands in operations",
                "Use type conversion functions (str(), int(), float())",
                "Verify function arguments match expected types"
            ]
        }

        return suggestion_map.get(error_type, ["Review the error message carefully"])