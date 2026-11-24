"""AST extraction and source locations."""

import ast
import logging
import re
import tokenize
from io import StringIO

from backend.rules import CC_THRESHOLD
from backend.security_flows import find_dynamic_template_flows
from backend.type_analyzer import find_definite_type_errors

logger = logging.getLogger(__name__)


def _describe_sorted_call(call):
    if not call.args:
        return "sorts the provided values"

    collection = ast.unparse(call.args[0])
    reverse = next(
        (keyword.value for keyword in call.keywords if keyword.arg == "reverse"), None
    )
    if isinstance(reverse, ast.Constant) and reverse.value is True:
        direction = "in descending order"
    elif (
        reverse is None or isinstance(reverse, ast.Constant) and reverse.value is False
    ):
        direction = "in ascending order"
    else:
        direction = "according to the reverse argument"

    key = next(
        (keyword.value for keyword in call.keywords if keyword.arg == "key"), None
    )
    key_detail = ""
    if isinstance(key, ast.Lambda) and isinstance(key.body, ast.Subscript):
        item_name = key.args.args[0].arg if key.args.args else "item"
        field_node = key.body.slice
        field = (
            field_node.value
            if isinstance(field_node, ast.Constant)
            and isinstance(field_node.value, str)
            else ast.unparse(field_node)
        )
        if isinstance(key.body.value, ast.Name) and key.body.value.id == item_name:
            key_detail = f" by each item's {field}"
    elif key is not None:
        key_detail = f" using {ast.unparse(key)} as the sort key"

    return f"sorts {collection} {direction}{key_detail}"


def _sorted_operations(node):
    operations = []
    for statement in node.body:
        value = (
            statement.value
            if isinstance(statement, (ast.Assign, ast.AnnAssign))
            else None
        )
        if isinstance(value, ast.Call) and _safe_call_name(value.func) == "sorted":
            operations.append(_describe_sorted_call(value))
    return operations


def _function_scope_nodes(function_node):
    yield function_node
    for child in ast.iter_child_nodes(function_node):
        if isinstance(
            child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)
        ):
            continue
        yield from _function_scope_nodes(child)


def _function_nesting_depth(function_node):
    block_nodes = (
        ast.If,
        ast.For,
        ast.AsyncFor,
        ast.While,
        ast.With,
        ast.AsyncWith,
        ast.Try,
        ast.Match,
    )
    max_depth = 0
    pending = [(child, 0) for child in function_node.body]
    while pending:
        node, depth = pending.pop()
        if isinstance(
            node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)
        ):
            continue
        if isinstance(node, block_nodes):
            depth += 1
            max_depth = max(max_depth, depth)
        pending.extend((child, depth) for child in ast.iter_child_nodes(node))
    return max_depth


def calculate_cc(tree_or_code):
    """Calculate an AST-derived cyclomatic complexity estimate from a Python AST node or source string.

    This is a structural *estimate* based on counting branch-inducing AST nodes
    (if/for/while/with/try/match/assert and boolean operator chains) rather than
    a full control-flow-graph (CFG) analysis. A proper CFG traversal is not
    performed; the result approximates the classic McCabe CC metric and is
    accurate for the common case but may differ from tool-based CFG CC for
    complex generators, comprehensions, or decorator-modified flow.
    """
    if isinstance(tree_or_code, str):
        tree_or_code = ast.parse(tree_or_code)

    decision_nodes = (
        ast.If,
        ast.For,
        ast.While,
        ast.ExceptHandler,
        ast.With,
        ast.IfExp,
        ast.AsyncFor,
        ast.AsyncWith,
        ast.match_case,
        ast.Assert,
    )
    complexity = 1
    if isinstance(tree_or_code, (ast.FunctionDef, ast.AsyncFunctionDef)):
        nodes = _function_scope_nodes(tree_or_code)
    else:
        nodes = ast.walk(tree_or_code)
    for node in nodes:
        if isinstance(node, decision_nodes):
            complexity += 1
            if isinstance(node, ast.match_case) and getattr(node, "guard", None):
                complexity += 1
        elif isinstance(node, ast.BoolOp):
            complexity += max(len(node.values) - 1, 0)
    return complexity


def _safe_call_name(node):
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = _safe_call_name(node.value)
        return f"{base}.{node.attr}" if base else node.attr
    if isinstance(node, ast.Call):
        return _safe_call_name(node.func)
    if isinstance(node, ast.Subscript):
        return _safe_call_name(node.value)
    return ""


def get_function_cc_info(source_code):
    """Compute per-function and file-level complexity context for generation."""
    tree = ast.parse(source_code)
    per_function = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            per_function[node.name] = calculate_cc(node)

    file_cc = calculate_cc(tree)
    lines = [
        "=== Cyclomatic Complexity Analysis ===",
        f"Overall file CC: {file_cc}",
        "",
        "Per-function CC:",
    ]
    for function_name, complexity in per_function.items():
        flag = (
            f"ABOVE THRESHOLD ({CC_THRESHOLD})"
            if complexity > CC_THRESHOLD
            else "BELOW THRESHOLD"
        )
        lines.append(f"  {function_name}: {complexity} [{flag}]")
    lines.extend(
        [
            "",
            f"Threshold is {CC_THRESHOLD}. For any function above the threshold, include a [CC Warning] note in the docstring and explain how to reduce complexity. For values at or below the threshold, include a [CC OK] note.",
        ]
    )
    return per_function, file_cc, "\n".join(lines)


def get_pretty_ast(source_code):
    """Return a pretty-printed AST dump."""
    return ast.dump(ast.parse(source_code), indent=4)


def _is_dynamic_string(node):
    if isinstance(node, ast.JoinedStr):
        return any(isinstance(value, ast.FormattedValue) for value in node.values)
    if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Mod)):
        return any(
            isinstance(part, (ast.Name, ast.Call, ast.JoinedStr))
            for part in (node.left, node.right)
        )
    if isinstance(node, ast.Call) and _safe_call_name(node.func).endswith(".format"):
        return bool(node.args or node.keywords)
    return False


def _is_literal_zero(node):
    if isinstance(node, ast.Constant):
        return (
            isinstance(node.value, (int, float, complex))
            and not isinstance(node.value, bool)
            and node.value == 0
        )
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
        return _is_literal_zero(node.operand)
    return False


def analyze_code(source_code):
    """Return JSON-serializable AST facts and deterministic warnings."""
    try:
        tree = ast.parse(source_code)
    except SyntaxError as exc:
        logger.warning("AST analysis skipped because the source is not valid Python: %s", exc)
        return {
            "summary": {
                "functions": 0,
                "classes": 0,
                "imports": 0,
                "calls": 0,
                "branches": 0,
                "file_cc": 1,
                "statements": 0,
            },
            "functions": [],
            "classes": [],
            "imports": [],
            "calls": [],
            "branches": [],
            "exception_handlers": [],
            "zero_divisions": [],
            "hardcoded_secrets": [],
            "todo_comments": [],
            "placeholder_blocks": [],
            "type_errors": [],
            "template_injections": [],
            "module_docstring": False,
            "total_comments": 0,
            "warnings": [
                {
                    "rule_id": "SYNTAX001",
                    "severity": "error",
                    "message": f"Syntax error in your code: {exc.msg}",
                    "line": exc.lineno or 0,
                    "column": exc.offset or 0,
                }
            ],
        }
    type_errors = find_definite_type_errors(source_code)
    imports = []
    functions = []
    classes = []
    calls = []
    branches = []
    exception_handlers = []
    zero_divisions = []
    todo_comments = []
    placeholder_blocks = []
    dynamic_string_names = set()
    import_aliases = {}

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                local_name = alias.asname or alias.name.split(".")[0]
                import_aliases[local_name] = alias.name if alias.asname else local_name
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                local_name = alias.asname or alias.name
                import_aliases[local_name] = ".".join(
                    part for part in (node.module, alias.name) if part
                )

    # Use tokenize to extract comments and TODOs from actual comments instead of string literals
    total_comments = 0
    try:
        tokens = tokenize.generate_tokens(StringIO(source_code).readline)
        for tok_type, tok_string, start, end, line in tokens:
            if tok_type == tokenize.COMMENT:
                total_comments += 1
                if re.search(
                    r"(?i)\b(TODO|FIXME|HACK|XXX)\b", tok_string
                ):
                    todo_comments.append({"text": tok_string, "lineno": start[0]})
    except (tokenize.TokenError, IndentationError) as exc:
        logger.warning("Tokenize failed: %s", exc)

    for node in ast.walk(tree):
        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
                ast.ClassDef,
                ast.If,
                ast.For,
                ast.AsyncFor,
                ast.While,
                ast.With,
                ast.AsyncWith,
                ast.Try,
                ast.Match,
            ),
        ):
            body = getattr(node, "body", [])
            if not body or (len(body) == 1 and isinstance(body[0], ast.Pass)):
                placeholder_blocks.append(
                    {"type": type(node).__name__, "lineno": node.lineno}
                )

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and _is_dynamic_string(node.value):
            targets = node.targets
        elif isinstance(node, ast.AnnAssign) and _is_dynamic_string(node.value):
            targets = [node.target]
        else:
            continue
        dynamic_string_names.update(
            target.id for target in targets if isinstance(target, ast.Name)
        )

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(
                    {"name": alias.name, "asname": alias.asname, "lineno": node.lineno}
                )
        elif isinstance(node, ast.ImportFrom):
            imports.append(
                {
                    "name": node.module or "",
                    "level": node.level,
                    "lineno": node.lineno,
                    "symbols": [alias.name for alias in node.names],
                }
            )

    hardcoded_secrets = []
    secret_name_parts = (
        "secret",
        "password",
        "passwd",
        "token",
        "api_key",
        "apikey",
        "private_key",
        "access_key",
    )
    ignored_secret_values = (
        "changeme",
        "example",
        "placeholder",
        "your_",
        "dummy",
        "replace",
        "xxx",
    )
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            targets = node.targets
            value = node.value
        elif isinstance(node, ast.AnnAssign):
            targets = [node.target]
            value = node.value
        else:
            continue
        if not isinstance(value, ast.Constant) or not isinstance(value.value, str):
            continue
        if len(value.value) < 8 or any(
            marker in value.value.lower() for marker in ignored_secret_values
        ):
            continue
        for target in targets:
            if isinstance(target, ast.Name) and any(
                part in target.id.lower() for part in secret_name_parts
            ):
                hardcoded_secrets.append({"name": target.id, "lineno": node.lineno})

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            args = [arg.arg for arg in node.args.posonlyargs + node.args.args]
            if node.args.vararg:
                args.append(node.args.vararg.arg)
            args.extend(arg.arg for arg in node.args.kwonlyargs)
            if node.args.kwarg:
                args.append(node.args.kwarg.arg)
            functions.append(
                {
                    "name": node.name,
                    "lineno": node.lineno,
                    "args": args,
                    "returns": "present" if node.returns else "none",
                    "complexity": calculate_cc(node),
                    "length": getattr(node, "end_lineno", node.lineno)
                    - node.lineno
                    + 1,
                    "nesting_depth": _function_nesting_depth(node),
                    "docstring": bool(ast.get_docstring(node, clean=True)),
                }
            )
        elif isinstance(node, ast.ClassDef):
            methods = [
                child.name
                for child in node.body
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))
            ]
            classes.append(
                {
                    "name": node.name,
                    "lineno": node.lineno,
                    "methods": methods,
                    "docstring": bool(ast.get_docstring(node, clean=True)),
                }
            )
        elif isinstance(node, ast.Call):
            call_name = _safe_call_name(node.func)
            call = {
                "name": call_name,
                "lineno": node.lineno,
                "args": len(node.args),
                "keywords": [keyword.arg for keyword in node.keywords if keyword.arg],
            }
            parts = call_name.split(".")
            canonical_name = ".".join(
                [import_aliases.get(parts[0], parts[0]), *parts[1:]]
            )
            if canonical_name != call_name:
                call["canonical_name"] = canonical_name
            call["shell"] = any(
                keyword.arg == "shell"
                and isinstance(keyword.value, ast.Constant)
                and keyword.value.value is True
                for keyword in node.keywords
            )
            call["verify_disabled"] = any(
                keyword.arg == "verify"
                and isinstance(keyword.value, ast.Constant)
                and keyword.value.value is False
                for keyword in node.keywords
            )
            if canonical_name.endswith((".execute", ".executemany")) and node.args:
                query = node.args[0]
                call["dynamic_sql"] = _is_dynamic_string(query) or (
                    isinstance(query, ast.Name) and query.id in dynamic_string_names
                )
            calls.append(call)
        elif isinstance(node, ast.ExceptHandler):
            exception_type = ast.unparse(node.type) if node.type else None
            exception_types = (
                node.type.elts if isinstance(node.type, ast.Tuple) else [node.type]
            )
            broad = node.type is None or any(
                isinstance(item, ast.Name) and item.id in {"Exception", "BaseException"}
                for item in exception_types
            )
            exception_handlers.append(
                {
                    "type": exception_type,
                    "lineno": node.lineno,
                    "broad": broad,
                }
            )
        elif (
            isinstance(node, ast.BinOp)
            and isinstance(node.op, (ast.Div, ast.FloorDiv, ast.Mod))
            and _is_literal_zero(node.right)
        ):
            zero_divisions.append(
                {"lineno": node.lineno, "operation": type(node.op).__name__}
            )
        elif isinstance(
            node,
            (
                ast.If,
                ast.For,
                ast.While,
                ast.AsyncFor,
                ast.With,
                ast.AsyncWith,
                ast.Try,
                ast.Match,
                ast.IfExp,
            ),
        ):
            branches.append({"type": type(node).__name__, "lineno": node.lineno})

    file_cc = calculate_cc(tree)
    analysis_dict = {
        "summary": {
            "functions": len(functions),
            "classes": len(classes),
            "imports": len(imports),
            "calls": len(calls),
            "branches": len(branches),
            "file_cc": file_cc,
            "statements": len(tree.body),
        },
        "functions": functions,
        "classes": classes,
        "imports": imports,
        "calls": calls,
        "branches": branches,
        "exception_handlers": exception_handlers,
        "zero_divisions": zero_divisions,
        "hardcoded_secrets": hardcoded_secrets,
        "todo_comments": todo_comments,
        "placeholder_blocks": placeholder_blocks,
        "type_errors": type_errors,
        "template_injections": find_dynamic_template_flows(tree, source_code),
        "module_docstring": bool(ast.get_docstring(tree, clean=True)),
        "total_comments": total_comments,
    }
    from backend.rules import apply_rules

    analysis_dict["warnings"] = apply_rules(analysis_dict)
    return analysis_dict


def _describe_value(node):
    if node is None:
        return "None"
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Constant):
        return repr(node.value)
    if isinstance(node, ast.Call):
        name = _safe_call_name(node.func)
        if name == "len" and node.args:
            return f"the number of elements in {ast.unparse(node.args[0])}"
        if name == "sum" and node.args:
            return f"the sum of {ast.unparse(node.args[0])}"
        return ast.unparse(node)
    if isinstance(node, ast.BinOp):
        operations = {
            ast.Add: "the sum of",
            ast.Sub: "the difference between",
            ast.Mult: "the product of",
            ast.Div: "the quotient of",
            ast.Mod: "the remainder of",
        }
        operation = operations.get(type(node.op))
        if operation:
            return f"{operation} {ast.unparse(node.left)} and {ast.unparse(node.right)}"
    if isinstance(node, (ast.ListComp, ast.SetComp, ast.GeneratorExp)):
        element = _describe_value(node.elt)
        clauses = []
        for generator in node.generators:
            clause = f"each {ast.unparse(generator.target)} in {ast.unparse(generator.iter)}"
            if generator.ifs:
                conditions = " and ".join(
                    ast.unparse(condition) for condition in generator.ifs
                )
                clause += f" that satisfies {conditions}"
            clauses.append(clause)
        collection = (
            "a set containing"
            if isinstance(node, ast.SetComp)
            else "a generator yielding"
            if isinstance(node, ast.GeneratorExp)
            else "a list containing"
        )
        return f"{collection} {element} for {' and '.join(clauses)}"
    if isinstance(node, ast.DictComp):
        if node.value is None:
            return "a dictionary with no value expression"
        clauses = []
        for generator in node.generators:
            clause = f"each {ast.unparse(generator.target)} in {ast.unparse(generator.iter)}"
            if generator.ifs:
                conditions = " and ".join(
                    ast.unparse(condition) for condition in generator.ifs
                )
                clause += f" that satisfies {conditions}"
            clauses.append(clause)
        return (
            f"a dictionary mapping {ast.unparse(node.key)} to "
            f"{ast.unparse(node.value)} for {' and '.join(clauses)}"
        )
    return ast.unparse(node)


def _describe_condition(node):
    if (
        isinstance(node, ast.UnaryOp)
        and isinstance(node.op, ast.Not)
        and isinstance(node.operand, ast.Name)
    ):
        return f"{node.operand.id} is falsy"
    if isinstance(node, ast.Name):
        return f"{node.id} is truthy"
    return ast.unparse(node)


def _walk_function_scope(node):
    yield node
    for child in ast.iter_child_nodes(node):
        if isinstance(
            child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)
        ):
            continue
        yield from _walk_function_scope(child)


def _returns_in_statements(statements):
    returns = []
    for statement in statements:
        if isinstance(
            statement, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)
        ):
            continue
        for child in _walk_function_scope(statement):
            if isinstance(child, ast.Return):
                returns.append(_describe_value(child.value))
    return list(dict.fromkeys(returns))


def _describe_function_semantics(node):
    args = [
        arg.arg for arg in node.args.posonlyargs + node.args.args + node.args.kwonlyargs
    ]
    returns = _returns_in_statements(node.body)
    conditional_returns = []
    for child in _walk_function_scope(node):
        if isinstance(child, ast.If):
            branch_returns = _returns_in_statements(child.body)
            if branch_returns:
                conditional_returns.append(
                    (_describe_condition(child.test), branch_returns)
                )

    argument_text = ", ".join(args) if args else "no explicit arguments"
    sort_operations = _sorted_operations(node)
    if sort_operations and returns:
        return (
            f"Function {node.name} accepts {argument_text}. It "
            f"{' and '.join(sort_operations[:2])} and returns {returns[0]}."
        )
    if conditional_returns and returns:
        condition, branch_returns = conditional_returns[0]
        other_returns = [value for value in returns if value not in branch_returns]
        if other_returns:
            return (
                f"Function {node.name} accepts {argument_text}, returns {', '.join(branch_returns[:2])} "
                f"when {condition}, and otherwise returns {', '.join(other_returns[:2])}."
            )
        return f"Function {node.name} accepts {argument_text} and returns {', '.join(branch_returns[:2])} when {condition}."
    if returns:
        return f"Function {node.name} accepts {argument_text} and returns {', '.join(returns[:3])}."

    yields = [
        ast.unparse(child.value) if child.value is not None else "values"
        for child in _walk_function_scope(node)
        if isinstance(child, (ast.Yield, ast.YieldFrom))
    ]
    if yields:
        return f"Generator function {node.name} accepts {argument_text} and yields {', '.join(yields[:2])}."

    conditions = [
        _describe_condition(child.test)
        for child in _walk_function_scope(node)
        if isinstance(child, ast.If)
    ]
    if conditions:
        return f"Function {node.name} accepts {argument_text} and runs conditional work when {', '.join(dict.fromkeys(conditions[:3]))}."
    return f"Function {node.name} accepts {argument_text} and has no explicit return value."


def build_smart_ast_explanations(source_code):
    """Build behavior explanations from functions and their scoped AST nodes."""
    try:
        tree = ast.parse(source_code)
    except SyntaxError:
        return []

    explanations = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            explanations.append(
                {
                    "function": node.name,
                    "line": node.lineno,
                    "reason": _describe_function_semantics(node),
                    "kind": "function",
                }
            )
            for child in _walk_function_scope(node):
                if isinstance(child, ast.If):
                    branch_returns = _returns_in_statements(child.body)
                    condition = _describe_condition(child.test)
                    if branch_returns:
                        reason = f"When {condition}, this branch returns {', '.join(branch_returns[:2])}."
                    else:
                        reason = f"This branch runs only when {condition}."
                    explanations.append(
                        {
                            "function": node.name,
                            "line": child.lineno,
                            "reason": reason,
                            "kind": "branch",
                        }
                    )
    return explanations
