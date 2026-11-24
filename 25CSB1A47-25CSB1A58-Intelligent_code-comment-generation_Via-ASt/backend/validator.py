"""Generated-code and normalized-AST validation."""

import ast
import builtins
import symtable
import tokenize
from collections import Counter
from io import StringIO


def validate_code(source_code):
    try:
        compile(source_code, "<source>", "exec")
        return True
    except SyntaxError as exc:
        return str(exc)


def format_python_error(source_code):
    try:
        compile(source_code, "<stdin>", "exec")
        return None
    except SyntaxError as exc:
        line_str = exc.text if exc.text else ""
        if not line_str and exc.lineno is not None:
            lines = source_code.splitlines()
            if 0 < exc.lineno <= len(lines):
                line_str = lines[exc.lineno - 1] + "\n"

        offset = exc.offset or 1
        end_offset = getattr(exc, "end_offset", None)
        if end_offset and end_offset > offset:
            carets = "^" * (end_offset - offset)
        else:
            carets = "^" * 3  # Based on prompt "^^^"

        return f'  File "<stdin>", line {exc.lineno}\n    {line_str.rstrip()}\n    {" " * (offset - 1)}{carets}\nSyntaxError: {exc.msg}'


def _collect_assigned_names(node, names_set):
    if isinstance(node, ast.Name):
        names_set.add(node.id)
    elif isinstance(node, (ast.Tuple, ast.List)):
        for elt in node.elts:
            _collect_assigned_names(elt, names_set)
    elif isinstance(node, ast.Starred):
        _collect_assigned_names(node.value, names_set)


def check_undefined_names(source_code):
    try:
        tree = ast.parse(source_code)
        symbol_table = symtable.symtable(source_code, "<source>", "exec")
    except (SyntaxError, ValueError):
        return []

    builtins_names = set(dir(builtins))
    module_scope_names = {
        "__name__",
        "__file__",
        "__doc__",
        "__spec__",
        "__loader__",
        "__package__",
        "__builtins__",
        "__all__",
        "__path__",
        "__cached__",
        "__annotations__",
    }
    wildcard_import = any(
        isinstance(node, ast.ImportFrom)
        and any(alias.name == "*" for alias in node.names)
        for node in ast.walk(tree)
    )

    def child_table(parent, node):
        if isinstance(node, ast.ClassDef):
            expected_name, expected_type = node.name, "class"
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            expected_name, expected_type = node.name, "function"
        elif isinstance(node, ast.Lambda):
            expected_name, expected_type = "lambda", "function"
        elif isinstance(node, ast.ListComp):
            expected_name, expected_type = "listcomp", "function"
        elif isinstance(node, ast.SetComp):
            expected_name, expected_type = "setcomp", "function"
        elif isinstance(node, ast.DictComp):
            expected_name, expected_type = "dictcomp", "function"
        elif isinstance(node, ast.GeneratorExp):
            expected_name, expected_type = "genexpr", "function"
        else:
            return None
        candidates = [
            child
            for child in parent.get_children()
            if child.get_name() in {expected_name, f"<{expected_name}>"}
            and child.get_type() == expected_type
            and child.get_lineno() == node.lineno
        ]
        return candidates[0] if candidates else None

    def find_name_error(node, scope, local_names):
        if (
            node.id in local_names
            or node.id in builtins_names
            or node.id in module_scope_names
        ):
            return False
        try:
            symbol = scope.lookup(node.id)
        except KeyError:
            return True

        if scope.get_type() == "module":
            return not (symbol.is_assigned() or symbol.is_imported())
        if not symbol.is_global():
            return False
        try:
            module_symbol = symbol_table.lookup(node.id)
        except KeyError:
            return not wildcard_import
        return not (
            module_symbol.is_assigned()
            or module_symbol.is_imported()
            or wildcard_import
        )

    undefined = []
    seen = set()
    lines = source_code.splitlines()

    def visit(node, scope, local_names=frozenset()):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            if find_name_error(node, scope, local_names):
                key = (node.id, node.lineno, node.col_offset)
                if key not in seen:
                    seen.add(key)
                    line_text = (
                        lines[node.lineno - 1] if 0 < node.lineno <= len(lines) else ""
                    )
                    undefined.append(
                        {
                            "name": node.id,
                            "lineno": node.lineno,
                            "col": node.col_offset,
                            "line_text": line_text,
                        }
                    )
            return

        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for decorator in node.decorator_list:
                visit(decorator, scope, local_names)
            for default in node.args.defaults + node.args.kw_defaults:
                if default is not None:
                    visit(default, scope, local_names)
            arguments = node.args.posonlyargs + node.args.args + node.args.kwonlyargs
            for argument in arguments:
                if argument.annotation:
                    visit(argument.annotation, scope, local_names)
            for argument in (node.args.vararg, node.args.kwarg):
                if argument and argument.annotation:
                    visit(argument.annotation, scope, local_names)
            if node.returns:
                visit(node.returns, scope, local_names)
            for type_parameter in getattr(node, "type_params", ()):
                visit(type_parameter, scope, local_names)
            local_scope = child_table(scope, node)
            body_scope = local_scope or scope
            for statement in node.body:
                visit(statement, body_scope, local_names)
            return

        if isinstance(node, ast.ClassDef):
            for expression in node.decorator_list + node.bases:
                visit(expression, scope, local_names)
            for keyword in node.keywords:
                visit(keyword.value, scope, local_names)
            for type_parameter in getattr(node, "type_params", ()):
                visit(type_parameter, scope, local_names)
            local_scope = child_table(scope, node)
            body_scope = local_scope or scope
            for statement in node.body:
                visit(statement, body_scope, local_names)
            return

        if isinstance(node, ast.Lambda):
            for default in node.args.defaults + node.args.kw_defaults:
                if default is not None:
                    visit(default, scope, local_names)
            local_scope = child_table(scope, node)
            visit(node.body, local_scope or scope, local_names)
            return

        if isinstance(
            node, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)
        ):
            first_iter = node.generators[0].iter
            visit(first_iter, scope, local_names)
            target_names = set()
            for generator in node.generators:
                _collect_assigned_names(generator.target, target_names)
            comprehension_scope = child_table(scope, node) or scope
            comp_names = local_names | target_names
            for generator in node.generators:
                for condition in generator.ifs:
                    visit(condition, comprehension_scope, comp_names)
                if generator is not node.generators[0]:
                    visit(generator.iter, comprehension_scope, comp_names)
            if isinstance(node, ast.DictComp):
                visit(node.key, comprehension_scope, comp_names)
                visit(node.value, comprehension_scope, comp_names)
            else:
                visit(node.elt, comprehension_scope, comp_names)
            return

        for child in ast.iter_child_nodes(node):
            visit(child, scope, local_names)

    visit(tree, symbol_table)
    return undefined


def format_name_errors(undefined_names):
    if not undefined_names:
        return None
    errors = []
    for u in undefined_names:
        stripped = u["line_text"].lstrip()
        indent = len(u["line_text"]) - len(stripped)
        idx = stripped.find(u["name"])
        if idx == -1:
            idx = max(0, u["col"] - indent)
        caret_indent = " " * (idx)
        carets = "^" * len(u["name"])
        errors.append(
            f"Traceback (most recent call last):\n  File \"<stdin>\", line {u['lineno']}, in <module>\n    {stripped}\n    {caret_indent}{carets}\nNameError: name '{u['name']}' is not defined"
        )
    return "\n\n".join(errors)


def _strip_docstrings(node):
    if isinstance(
        node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
    ) and (
        node.body
        and isinstance(node.body[0], ast.Expr)
        and isinstance(node.body[0].value, ast.Constant)
        and isinstance(node.body[0].value.value, str)
    ):
        node.body = node.body[1:]
    for child in ast.iter_child_nodes(node):
        _strip_docstrings(child)
    return node


def _scope_docstrings(tree):
    class DocstringScopeVisitor(ast.NodeVisitor):
        def __init__(self):
            self.result = {}
            self.scope_path = []

        def _visit_scope(self, node, name):
            self.scope_path.append(name)
            scope_key = (type(node).__name__, ".".join(self.scope_path))
            self.result[scope_key] = ast.get_docstring(node, clean=False)
            self.generic_visit(node)
            self.scope_path.pop()

        def visit_Module(self, node):
            self.result[("Module", "<module>")] = ast.get_docstring(
                node, clean=False
            )
            self.generic_visit(node)

        def visit_ClassDef(self, node):
            self._visit_scope(node, node.name)

        def visit_FunctionDef(self, node):
            self._visit_scope(node, node.name)

        def visit_AsyncFunctionDef(self, node):
            self._visit_scope(node, node.name)

    visitor = DocstringScopeVisitor()
    visitor.visit(tree)
    return visitor.result


def _docstring_is_short_enrichment(original_docstring, generated_docstring):
    if not original_docstring or not generated_docstring:
        return False
    if "\n" in original_docstring.strip() or len(original_docstring.strip()) > 120:
        return False
    if not generated_docstring.startswith(original_docstring):
        return False
    added_text = generated_docstring[len(original_docstring) :].strip()
    section_markers = (
        "Args:",
        "Returns:",
        "Raises:",
        "Security Note:",
        ":param ",
        ":returns:",
        ":raises ",
        "Parameters\n",
        "Returns\n",
        "Raises\n",
    )
    return bool(added_text) and any(
        marker in added_text for marker in section_markers
    )


def _comment_tokens(source_code):
    try:
        return Counter(
            token.string
            for token in tokenize.generate_tokens(StringIO(source_code).readline)
            if token.type == tokenize.COMMENT
        )
    except (tokenize.TokenError, IndentationError):
        return Counter()


def has_added_comments(original_code, generated_code):
    """Return whether generated code adds a comment token or a docstring."""
    original_comments = _comment_tokens(original_code)
    generated_comments = _comment_tokens(generated_code)
    if any(
        count > original_comments[comment]
        for comment, count in generated_comments.items()
    ):
        return True

    try:
        original_tree = ast.parse(original_code)
        generated_tree = ast.parse(generated_code)
    except SyntaxError:
        return False

    def docstrings(tree):
        return Counter(
            docstring
            for node in ast.walk(tree)
            if isinstance(
                node,
                (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef),
            )
            if (docstring := ast.get_docstring(node, clean=False)) is not None
        )

    original_docstrings = docstrings(original_tree)
    generated_docstrings = docstrings(generated_tree)
    return any(
        count > original_docstrings[docstring]
        for docstring, count in generated_docstrings.items()
    )


def _normalize_ast(tree):
    return ast.dump(_strip_docstrings(tree), include_attributes=False)


def validate_generated_code(
    original_code, generated_code, allow_docstring_enrichment=False
):
    """Validate that generation preserves executable logic."""
    issues = []
    try:
        compile(original_code, "<original>", "exec")
        original_ast = ast.parse(original_code)
    except SyntaxError as exc:
        return {"is_valid": False, "issues": [f"Original code is invalid: {exc}"]}
    try:
        compile(generated_code, "<generated>", "exec")
        generated_ast = ast.parse(generated_code)
    except SyntaxError as exc:
        return {"is_valid": False, "issues": [f"Generated code is invalid: {exc}"]}

    original_docstrings = _scope_docstrings(original_ast)
    generated_docstrings = _scope_docstrings(generated_ast)
    if _normalize_ast(original_ast) != _normalize_ast(generated_ast):
        issues.append("Executable logic changed after comment generation.")
    else:
        for scope_key, original_docstring in original_docstrings.items():
            generated_docstring = generated_docstrings.get(scope_key)
            if (
                original_docstring is not None
                and generated_docstring != original_docstring
                and not (
                    allow_docstring_enrichment
                    and _docstring_is_short_enrichment(
                        original_docstring, generated_docstring
                    )
                )
            ):
                issues.append(
                    f"An existing docstring changed or was removed in {scope_key[1] or scope_key[0]}."
                )
                break
    return {"is_valid": not issues, "issues": issues}
