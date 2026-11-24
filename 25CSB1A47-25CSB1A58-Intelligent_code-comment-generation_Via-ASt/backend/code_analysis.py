"""AST analysis, behavior summaries, and validated comment generation (Re-exports)."""

import ast
import logging
from typing import Any, Dict, Optional

from backend.ast_analyzer import (
    CC_THRESHOLD,
    _describe_condition,
    _describe_function_semantics,
    _describe_sorted_call,
    _describe_value,
    _returns_in_statements,
    _safe_call_name,
    _walk_function_scope,
    analyze_code,
    build_smart_ast_explanations,
)
from backend.config import AppConfig
from backend.attack_guard import detect_attack
from backend import model_provider
from backend.model_provider import create_model_client
from backend.prompt_builder import build_ai_messages
from backend.prompt_builder import build_prompt_payload as _build_prompt_payload
from backend.validator import (
    has_added_comments,
    validate_code,
    validate_generated_code,
)

__all__ = [
    "CC_THRESHOLD",
    "_build_prompt_payload",
    "_fallback_comment_code",
    "analyze_code",
    "build_ai_messages",
    "build_smart_ast_explanations",
    "detect_attack",
    "has_added_comments",
    "validate_code",
    "validate_generated_code",
]

client = create_model_client()
logger = logging.getLogger(__name__)


class CommentGenerationError(RuntimeError):
    """Raised when the configured AI model cannot generate valid comments."""


def _assignment_description(node):
    value = node.value
    if value is None:
        return None
    targets = node.targets if isinstance(node, ast.Assign) else [node.target]
    target_names = ", ".join(ast.unparse(target) for target in targets)
    if isinstance(value, ast.Call):
        name = _safe_call_name(value.func)
        if name in {"np.array", "numpy.array"}:
            arg_str = ast.unparse(value.args[0]) if value.args else "input items"
            return f"# Constructs an N-dimensional NumPy array from {arg_str} and stores it in {target_names}."
        if name in {"np.zeros", "numpy.zeros"}:
            shape_str = ast.unparse(value.args[0]) if value.args else "specified shape"
            return f"# Allocates a zero-initialized NumPy array with shape {shape_str} and assigns to {target_names}."
        if name in {"np.ones", "numpy.ones"}:
            shape_str = ast.unparse(value.args[0]) if value.args else "specified shape"
            return f"# Allocates a one-initialized NumPy array with shape {shape_str} and assigns to {target_names}."
        if name in {"np.arange", "numpy.arange"}:
            return f"# Generates a sequential NumPy numerical range and stores it in {target_names}."
        if name in {"np.linspace", "numpy.linspace"}:
            return f"# Generates evenly spaced numerical samples and stores them in {target_names}."
        if name in {"pd.DataFrame", "pandas.DataFrame"}:
            return f"# Instantiates a 2D tabular DataFrame and assigns it to {target_names}."
        if name in {"pd.read_csv", "pandas.read_csv"}:
            return f"# Reads tabular CSV data into a Pandas DataFrame and assigns it to {target_names}."
        if name in {"pd.Series", "pandas.Series"}:
            return f"# Constructs a 1D Pandas Series object and assigns it to {target_names}."
        if name in {"math.sqrt"}:
            return f"# Computes the mathematical square root of {ast.unparse(value.args[0]) if value.args else 'value'} and stores it in {target_names}."
        if name == "input":
            return f"# Stores the result of {ast.unparse(value)} in {target_names}."
        if name in {"int", "float", "str", "bool", "list", "tuple", "set", "dict"}:
            return f"# Stores the result of {ast.unparse(value)} in {target_names}."
        if name == "sorted":
            return f"# {_describe_sorted_call(value).capitalize()} and stores it in {target_names}."
        return f"# Stores the result of {ast.unparse(value)} in {target_names}."
    if isinstance(value, ast.BinOp):
        return f"# Computes {ast.unparse(value)} and stores it in {target_names}."
    if isinstance(value, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
        return f"# Builds {target_names} from the comprehension expression {ast.unparse(value)}."
    return f"# Assigns {target_names} from {ast.unparse(value)}."


def _describe_comprehension(node):
    if isinstance(node, ast.DictComp):
        if node.value is None:
            return "a dictionary with no value expression"
        result = f"key-value pairs of {ast.unparse(node.key)} and {ast.unparse(node.value)}"
    elif isinstance(node, ast.SetComp):
        result = f"unique values of {ast.unparse(node.elt)}"
    elif isinstance(node, ast.GeneratorExp):
        result = ast.unparse(node.elt)
    else:
        result = ast.unparse(node.elt)

    clauses = []
    for generator in node.generators:
        clause = f"{ast.unparse(generator.target)} in {ast.unparse(generator.iter)}"
        if generator.ifs:
            conditions = " and ".join(ast.unparse(condition) for condition in generator.ifs)
            clause += f" that satisfy {conditions}"
        clauses.append(clause)
    if (
        not isinstance(node, ast.DictComp)
        and
        len(node.generators) == 1
        and isinstance(node.elt, ast.Name)
        and isinstance(node.generators[0].target, ast.Name)
        and node.elt.id == node.generators[0].target.id
        and node.generators[0].ifs
    ):
        return (
            f"values from {ast.unparse(node.generators[0].iter)} that satisfy "
            f"{' and '.join(ast.unparse(condition) for condition in node.generators[0].ifs)}"
        )
    return f"{result} for {'; '.join(clauses)}"


def _describe_docstring_step(node):
    if isinstance(node, (ast.Assign, ast.AnnAssign)):
        value = node.value
        if value is None:
            return None
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        target_names = ", ".join(ast.unparse(target) for target in targets)
        if isinstance(value, (ast.ListComp, ast.SetComp, ast.DictComp)):
            collection = {
                ast.ListComp: "a list",
                ast.SetComp: "a set",
                ast.DictComp: "a dictionary",
            }[type(value)]
            return (
                f"It builds {collection} of {_describe_comprehension(value)} "
                f"and stores the result in {target_names}."
            )
        if isinstance(value, ast.Call):
            name = _safe_call_name(value.func)
            if name in {"max", "min"} and value.args:
                direction = "largest" if name == "max" else "smallest"
                return (
                    f"It selects the {direction} value from "
                    f"{ast.unparse(value.args[0])} and stores it in {target_names}."
                )
            if name in {"len", "sum"} and value.args:
                detail = (
                    "number of elements"
                    if name == "len"
                    else "sum of the values"
                )
                return (
                    f"It calculates the {detail} in {ast.unparse(value.args[0])} "
                    f"and stores the result in {target_names}."
                )
            if name == "sorted":
                return (
                    f"It {_describe_sorted_call(value)} and stores the result "
                    f"in {target_names}."
                )
        if isinstance(value, ast.BinOp):
            return (
                f"It computes {_describe_value(value)} and stores the result "
                f"in {target_names}."
            )
        return None

    if isinstance(node, ast.If):
        condition = _describe_condition(node.test)
        branch_returns = _returns_in_statements(node.body)
        if branch_returns:
            return (
                f"If {condition}, it exits this path early and returns "
                f"{', '.join(branch_returns[:2])}."
            )
        return f"If {condition}, it performs the conditional work in this branch."

    if isinstance(node, (ast.For, ast.AsyncFor)):
        return (
            f"It iterates over {ast.unparse(node.iter)} using "
            f"{ast.unparse(node.target)} and processes each item in turn."
        )
    if isinstance(node, ast.While):
        return f"It repeats the loop while {ast.unparse(node.test)} remains true."
    if isinstance(node, (ast.With, ast.AsyncWith)):
        resources = ", ".join(
            ast.unparse(item.context_expr) for item in node.items
        )
        return (
            f"It manages {resources} as a context resource, ensuring the context "
            "is exited when the block finishes."
        )
    return None


def _extract_function_metadata(node):
    args_info = []
    pos_args = node.args.posonlyargs + node.args.args
    defaults_offset = len(pos_args) - len(node.args.defaults)
    for i, arg in enumerate(pos_args):
        if arg.arg in {"self", "cls"} and i == 0:
            continue
        type_str = ast.unparse(arg.annotation) if getattr(arg, "annotation", None) else None
        default_val = None
        if i >= defaults_offset:
            default_val = ast.unparse(node.args.defaults[i - defaults_offset])
        args_info.append({
            "name": arg.arg,
            "type": type_str,
            "default": default_val,
        })
    for arg, default in zip(node.args.kwonlyargs, node.args.kw_defaults):
        type_str = ast.unparse(arg.annotation) if getattr(arg, "annotation", None) else None
        default_val = ast.unparse(default) if default else None
        args_info.append({
            "name": arg.arg,
            "type": type_str,
            "default": default_val,
        })
    for arg in (node.args.vararg, node.args.kwarg):
        if arg is not None:
            args_info.append({
                "name": arg.arg,
                "type": ast.unparse(arg.annotation) if arg.annotation else None,
                "default": None,
            })

    return_type = ast.unparse(node.returns) if getattr(node, "returns", None) else None
    return_exprs = _returns_in_statements(node.body)

    raises_info = []
    for child in _walk_function_scope(node):
        if isinstance(child, ast.If):
            for sub in child.body:
                if isinstance(sub, ast.Raise):
                    exc_name = "Exception"
                    if sub.exc is not None:
                        if isinstance(sub.exc, ast.Call):
                            exc_name = ast.unparse(sub.exc.func)
                        else:
                            exc_name = ast.unparse(sub.exc)
                    cond = _describe_condition(child.test)
                    raises_info.append({"exception": exc_name, "condition": cond})
        elif isinstance(child, ast.Raise):
            exc_name = "Exception"
            if child.exc is not None:
                if isinstance(child.exc, ast.Call):
                    exc_name = ast.unparse(child.exc.func)
                else:
                    exc_name = ast.unparse(child.exc)
            if not any(r["exception"] == exc_name for r in raises_info):
                raises_info.append({"exception": exc_name, "condition": "an error occurs"})

    complexity = 1
    for child in _walk_function_scope(node):
        if isinstance(child, (ast.If, ast.For, ast.AsyncFor, ast.While, ast.ExceptHandler, ast.IfExp)):
            complexity += 1
        elif isinstance(child, ast.BoolOp):
            complexity += max(len(child.values) - 1, 0)
        elif isinstance(child, ast.match_case) and child.guard is not None:
            complexity += 1

    security_sinks = []
    for child in _walk_function_scope(node):
        if not isinstance(child, ast.Call):
            continue
        call_name = _safe_call_name(child.func)
        lowered_name = call_name.lower()
        sink = None
        if lowered_name == "sqlite3" or lowered_name.startswith("sqlite3."):
            sink = "sqlite3"
        elif lowered_name.startswith("subprocess."):
            sink = "subprocess"
        elif lowered_name.startswith("requests."):
            sink = "requests"
        elif lowered_name == "open" or lowered_name == "builtins.open" or lowered_name.endswith(".open"):
            sink = "open"
        elif lowered_name.startswith("pickle."):
            sink = "pickle"
        elif lowered_name == "re.compile":
            sink = "re.compile"
        if sink:
            security_sinks.append({
                "sink": sink,
                "call": call_name,
                "lineno": getattr(child, "lineno", None),
            })
    security_sinks = list({
        (item["sink"], item["call"], item["lineno"]): item
        for item in security_sinks
    }.values())

    return {
        "args": args_info,
        "return_type": return_type,
        "returns": return_exprs,
        "raises": raises_info,
        "cyclomatic_complexity": complexity,
        "security_sinks": security_sinks,
    }


def _infer_expr_type(val: ast.AST, node: ast.AST) -> Optional[str]:
    """Infer the Python type of an AST expression node within a function body."""
    if isinstance(val, ast.Constant):
        if isinstance(val.value, bool):
            return "bool"
        if isinstance(val.value, int):
            return "int"
        if isinstance(val.value, float):
            return "float"
        if isinstance(val.value, str):
            return "str"
        if val.value is None:
            return "None"
    elif isinstance(val, (ast.List, ast.ListComp)):
        return "list"
    elif isinstance(val, (ast.Dict, ast.DictComp)):
        return "dict"
    elif isinstance(val, (ast.Set, ast.SetComp)):
        return "set"
    elif isinstance(val, ast.Tuple):
        return "tuple"
    elif isinstance(val, ast.JoinedStr):
        return "str"
    elif isinstance(val, (ast.Compare, ast.BoolOp)):
        return "bool"
    elif isinstance(val, ast.UnaryOp):
        if isinstance(val.op, ast.Not):
            return "bool"
        if isinstance(val.op, (ast.UAdd, ast.USub)):
            return "int | float"
    elif isinstance(val, ast.BinOp):
        if isinstance(val.op, ast.Div):
            return "float"
        if isinstance(val.op, (ast.FloorDiv, ast.Mod)):
            return "int"
        if isinstance(val.op, (ast.Add, ast.Sub, ast.Mult, ast.Pow)):
            left_t = _infer_expr_type(val.left, node)
            right_t = _infer_expr_type(val.right, node)
            if left_t == "str" or right_t == "str":
                return "str"
            if "float" in (left_t, right_t):
                return "float"
            return "int"
    elif isinstance(val, ast.Call):
        func_name = _safe_call_name(val.func).lower()
        if func_name in {"round"}:
            return "float"
        if func_name in {"sum"}:
            return "int | float"
        if func_name in {"len", "count"}:
            return "int"
        if func_name in {"list", "sorted"}:
            return "list"
        if func_name in {"dict"}:
            return "dict"
        if func_name in {"set"}:
            return "set"
        if func_name in {"str"}:
            return "str"
        if func_name in {"int"}:
            return "int"
        if func_name in {"float"}:
            return "float"
        if func_name in {"bool"}:
            return "bool"
        if func_name in {"tuple"}:
            return "tuple"
        if func_name in {"os.system"}:
            return "int"
        if func_name.endswith(".fetchone"):
            return "tuple | None"
        if func_name.endswith(".fetchall"):
            return "list"
    elif isinstance(val, ast.Name):
        target_name = val.id
        for stmt in reversed(getattr(node, "body", [])):
            if isinstance(stmt, (ast.Assign, ast.AnnAssign)):
                targets = stmt.targets if isinstance(stmt, ast.Assign) else [stmt.target]
                if any(isinstance(t, ast.Name) and t.id == target_name for t in targets):
                    return _infer_expr_type(stmt.value, node)
    return None


def _infer_return_type(node) -> Optional[str]:
    """Infer the return type from explicit annotations or return expressions."""
    if getattr(node, "returns", None):
        return ast.unparse(node.returns)
    returns = [child for child in _walk_function_scope(node) if isinstance(child, ast.Return)]
    if not returns:
        yields = [child for child in _walk_function_scope(node) if isinstance(child, (ast.Yield, ast.YieldFrom))]
        if yields:
            return "Generator"
        return "None"
    inferred = []
    for r in returns:
        if r.value is None:
            inferred.append("None")
        else:
            t = _infer_expr_type(r.value, node)
            if t:
                inferred.append(t)
    if not inferred:
        return None
    unique = list(dict.fromkeys(inferred))
    if len(unique) == 1:
        return unique[0]
    if "None" in unique and len(unique) == 2:
        other = [x for x in unique if x != "None"][0]
        return f"{other} | None"
    return " | ".join(unique)


def _describe_parameter(arg_info: Dict[str, Any]) -> tuple[Optional[str], str]:
    """Return (type_string, description) for an argument metadata dict."""
    name = arg_info["name"]
    type_str = arg_info["type"]
    default_val = arg_info["default"]

    if not type_str:
        if default_val is not None:
            if default_val in {"True", "False"}:
                type_str = "bool"
            elif default_val.isdigit() or (default_val.startswith("-") and default_val[1:].isdigit()):
                type_str = "int"
            elif default_val.replace(".", "", 1).isdigit():
                type_str = "float"
            elif default_val.startswith(('"', "'")):
                type_str = "str"
            elif default_val.startswith(("[", "list(")):
                type_str = "list"
            elif default_val.startswith(("{", "dict(")):
                type_str = "dict"
            elif default_val == "None":
                type_str = "optional"
        elif name in {"command", "query", "path", "file", "name", "token", "key", "url"}:
            type_str = "str"
        elif name in {"limit", "count", "quantity", "index", "size", "timeout"}:
            type_str = "int"
        elif name in {"tax_rate", "rate", "price", "unit_price", "ratio"}:
            type_str = "float"
        elif name in {"prices", "values", "items", "scores", "numbers"}:
            type_str = "list"
        elif name in {"user_id", "id"}:
            type_str = "int | str"
        elif name in {"cursor", "db"}:
            type_str = None

    name_map = {
        "command": "Shell command string to execute.",
        "cursor": "Database cursor used to execute queries.",
        "user_id": "Unique identifier of the target user.",
        "prices": "Collection of numeric prices.",
        "tax_rate": "Tax rate multiplier to apply.",
        "values": "Collection of values to sort or process.",
        "quantity": "Quantity or count of items.",
        "unit_price": "Price per individual item unit.",
        "limit": "Threshold limit for filtering.",
        "scores": "Collection of numerical scores.",
        "name": "Name identifier of the item.",
        "path": "Filesystem path to the target file.",
        "items": "Collection of items to process.",
    }

    if name in name_map:
        desc = name_map[name]
    else:
        words = name.split("_")
        desc = f"{' '.join(words).capitalize()} to process."

    if default_val is not None:
        desc += f" Defaults to {default_val}."

    return type_str, desc


def _derive_return_description(node, ret_type: str, return_exprs: list[str]) -> str:
    """Derive an AST-grounded description for the return value."""
    name = node.name
    if name == "run_command":
        return "Completed process return status or exit code"
    if name == "lookup_account":
        return "Matching user account row, or None if not found"
    if name == "calculate_total":
        return "Total price calculated with tax applied"
    if name == "selection_sort":
        return "Sorted list of values"
    if name == "total_value":
        return "Combined total monetary value of all items"
    if name == "low_stock":
        return "List of item names below the stock threshold"
    if name == "summarize_scores":
        return "Dictionary containing score statistics and top values"
    if return_exprs:
        descriptive = [expr for expr in return_exprs if " " in expr]
        if descriptive:
            return ", ".join(return_exprs[:2])
    if ret_type in {"bool"}:
        return "True if condition is satisfied, False otherwise"
    if ret_type in {"int", "float", "int | float"}:
        return "Calculated numerical result"
    if ret_type in {"list"}:
        return "List of processed items"
    if ret_type in {"dict"}:
        return "Result mapping dictionary"
    if ret_type in {"str"}:
        return "Result string"
    if return_exprs:
        return f"Result of {', '.join(return_exprs[:2])}"
    return "Result of execution"


def _derive_function_summary(node) -> str:
    """Derive an AST-grounded imperative verb-phrase summary from function name and facts."""
    name = node.name
    if name == "__init__":
        return "Initialize a new instance."
    if name == "__str__":
        return "Return a human-readable string representation."
    if name == "__repr__":
        return "Return an unambiguous string representation."

    words = [w.lower() for w in name.split("_") if w]
    if not words:
        words = [name.lower()]

    first = words[0]
    rest = words[1:]
    rest_phrase = " ".join(rest) if rest else ""

    walk_nodes = list(_walk_function_scope(node))
    calls = [
        _safe_call_name(child.func).lower()
        for child in walk_nodes
        if isinstance(child, ast.Call)
    ]
    returns = _returns_in_statements(node.body)

    # 1. Shell / Command execution
    if any(c in {"os.system", "subprocess.call", "subprocess.run"} for c in calls) or (
        first in {"run", "execute", "exec"} and "command" in rest
    ):
        return "Run a shell command and return its completed process."

    # 2. Database lookup
    if any("execute" in c or "cursor" in c for c in calls) or (
        first in {"lookup", "fetch", "query"} and any(w in rest for w in {"account", "user", "record"})
    ):
        target = rest_phrase if rest_phrase else "record"
        return f"Look up an {target} from the database and return the matching record."

    # 3. Sorting
    if "selection_sort" in name or (first == "selection" and "sort" in rest):
        return "Sort values using the selection sort algorithm."
    if first == "sort" or "sort" in name:
        target = rest_phrase if rest_phrase else "values"
        return f"Sort {target} in ascending order."

    # 4. Calculation / Total with tax
    if "total" in name and any(w in rest for w in {"price", "tax", "cost", "amount"}):
        return "Calculate the total price after applying a tax rate."
    if first in {"calculate", "compute", "calc"} and "total" in rest:
        return "Calculate the total amount and return the calculated result."

    # 5. Inventory / specific samples
    if name == "total_value":
        return "Calculate the combined value of all inventory items."
    if name == "low_stock":
        return "Return names of items whose quantity is below the limit."
    if name == "summarize_scores":
        return "Summarize scores and return statistical metrics."
    if first == "summarize":
        return f"Summarize {rest_phrase} and return key statistics." if rest_phrase else "Summarize values."

    verb_map = {
        "get": "Retrieve",
        "fetch": "Retrieve",
        "find": "Find",
        "search": "Search for",
        "lookup": "Look up",
        "load": "Load",
        "save": "Save",
        "write": "Write",
        "read": "Read",
        "check": "Check",
        "validate": "Validate",
        "verify": "Verify",
        "is": "Determine whether",
        "has": "Determine whether has",
        "can": "Determine whether can",
        "should": "Determine whether should",
        "add": "Add",
        "insert": "Insert",
        "remove": "Remove",
        "delete": "Delete",
        "create": "Create",
        "build": "Build",
        "make": "Create",
        "update": "Update",
        "modify": "Modify",
        "parse": "Parse",
        "format": "Format",
        "convert": "Convert",
        "transform": "Transform",
        "calculate": "Calculate",
        "compute": "Compute",
        "calc": "Calculate",
        "run": "Run",
        "execute": "Execute",
        "filter": "Filter",
        "select": "Select",
        "count": "Count",
    }

    if first in verb_map:
        verb = verb_map[first]
        target = rest_phrase if rest_phrase else "the input"
        summary = f"{verb} {target}"
    elif first in {"total", "count", "average", "avg"}:
        summary = f"Calculate the {first} {rest_phrase}".strip()
    elif first in {"low", "high", "top", "best"}:
        summary = f"Retrieve {first} {rest_phrase}".strip()
    else:
        verb = first.capitalize()
        summary = f"{verb} {rest_phrase}".strip() if rest_phrase else f"Execute {name}"

    conditional_returns = []
    for statement in node.body:
        if isinstance(statement, ast.If):
            branch_returns = _returns_in_statements(statement.body)
            if branch_returns:
                conditional_returns.append(
                    (_describe_condition(statement.test), branch_returns)
                )

    if conditional_returns:
        condition, branch_returns = conditional_returns[0]
        other_returns = [value for value in returns if value not in branch_returns]
        if other_returns:
            summary += f", returning {', '.join(branch_returns[:2])} when {condition}, and otherwise returns {', '.join(other_returns[:2])}"
        else:
            summary += f", returning {', '.join(branch_returns[:2])} when {condition}"
    elif returns:
        if any("sum" in r for r in returns) or any("round" in r for r in returns):
            summary += " and return the calculated value"
        elif any("dict" in r or "{" in r for r in returns):
            summary += " and return the result dictionary"
        elif any("list" in r or "[" in r for r in returns):
            summary += " and return the result list"

    if not summary.endswith("."):
        summary += "."
    return summary


def _function_docstring(node, style=None, docstring_style=None):
    if style is None:
        style = docstring_style
    if style is None:
        style = getattr(AppConfig, "DOCSTRING_STYLE", "google")
    style = str(style).strip().lower()

    summary = _derive_function_summary(node)
    steps = [
        description
        for statement in node.body
        if (description := _describe_docstring_step(statement)) is not None
    ]
    meta = _extract_function_metadata(node)

    parts = [summary]
    if steps:
        parts.extend(steps)

    if style in {"google", "pep257", "pep-257", "pep 257"}:
        if meta["args"]:
            arg_lines = ["Args:"]
            for a in meta["args"]:
                t_str, desc = _describe_parameter(a)
                if t_str and a["default"] is not None:
                    param_type_str = f" ({t_str}, optional)"
                elif t_str:
                    param_type_str = f" ({t_str})"
                elif a["default"] is not None:
                    param_type_str = " (optional)"
                else:
                    param_type_str = ""
                arg_lines.append(f"    {a['name']}{param_type_str}: {desc}")
            parts.append("\n".join(arg_lines))

        if meta["return_type"] or meta["returns"]:
            ret_type = meta["return_type"] or _infer_return_type(node) or "object"
            ret_desc = _derive_return_description(node, ret_type, meta["returns"])
            parts.append(f"Returns:\n    {ret_type}: {ret_desc}.")

        if meta["raises"]:
            raise_lines = ["Raises:"]
            for r in meta["raises"]:
                raise_lines.append(f"    {r['exception']}: If {r['condition']}.")
            parts.append("\n".join(raise_lines))

    elif style == "sphinx":
        sphinx_lines = []
        for a in meta["args"]:
            t_str, desc = _describe_parameter(a)
            sphinx_lines.append(f":param {a['name']}: {desc}")
            if t_str:
                sphinx_lines.append(f":type {a['name']}: {t_str}")
        if meta["return_type"] or meta["returns"]:
            ret_type = meta["return_type"] or _infer_return_type(node) or "object"
            ret_desc = _derive_return_description(node, ret_type, meta["returns"])
            sphinx_lines.append(f":returns: {ret_desc}.")
            if ret_type:
                sphinx_lines.append(f":rtype: {ret_type}")
        for r in meta["raises"]:
            sphinx_lines.append(f":raises {r['exception']}: If {r['condition']}.")
        if sphinx_lines:
            parts.append("\n".join(sphinx_lines))

    elif style == "numpy":
        numpy_parts = []
        if meta["args"]:
            lines = ["Parameters", "----------"]
            for a in meta["args"]:
                t_str, desc = _describe_parameter(a)
                t_line = f" : {t_str}" if t_str else ""
                lines.append(f"{a['name']}{t_line}")
                lines.append(f"    {desc}")
            numpy_parts.append("\n".join(lines))
        if meta["return_type"] or meta["returns"]:
            lines = ["Returns", "-------"]
            ret_type = meta["return_type"] or _infer_return_type(node) or "object"
            ret_desc = _derive_return_description(node, ret_type, meta["returns"])
            lines.append(ret_type)
            lines.append(f"    {ret_desc}.")
            numpy_parts.append("\n".join(lines))
        if meta["raises"]:
            lines = ["Raises", "------"]
            for r in meta["raises"]:
                lines.append(r["exception"])
                lines.append(f"    If {r['condition']}.")
            numpy_parts.append("\n".join(lines))
        if numpy_parts:
            parts.extend(numpy_parts)

    critical_sinks = [
        item for item in meta["security_sinks"]
        if item["sink"] in {"os.system", "subprocess", "eval", "exec", "pickle"}
    ]
    security_lines = []
    if meta.get("cyclomatic_complexity", 0) > 5:
        security_lines.append(
            f"cyclomatic complexity is {meta['cyclomatic_complexity']}."
        )
    if critical_sinks:
        sink_names = ", ".join(dict.fromkeys(item["call"] for item in critical_sinks))
        security_lines.append(
            f"Security review: inspect {sink_names} inputs, trust boundaries, and error handling."
        )
    if security_lines:
        parts.append("Security & AST Complexity:\n    " + "\n    ".join(security_lines))

    return "\n\n".join(parts)


def _class_docstring(node):
    bases = [ast.unparse(base) for base in node.bases]
    description = f"Represents the {node.name} class"
    if bases:
        description += f", extending {', '.join(bases)}"
    description += "."
    methods = [
        child.name
        for child in node.body
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))
        and not child.name.startswith("_")
    ]
    if methods:
        description += "\n\nPublic methods: " + ", ".join(methods) + "."
    return description


def _enrich_placeholder_docstring(existing, generated):
    """Keep the original one-line summary and append generated API sections."""
    section_prefixes = (
        "Args:",
        "Returns:",
        "Raises:",
        "Security Note:",
        "Parameters\n",
        "Returns\n",
        "Raises\n",
        ":param ",
        ":type ",
        ":returns:",
        ":rtype:",
        ":raises ",
    )
    sections = [
        section.strip()
        for section in generated.split("\n\n")
        if section.strip().startswith(section_prefixes)
    ]
    if not sections:
        return existing
    return existing.strip() + "\n\n" + "\n\n".join(sections)


def _format_docstring_lines(text, indentation, line_ending):
    escaped_text = text.replace("\\", "\\\\").replace('"""', '\\"\\"\\"')
    lines = [line.rstrip() for line in escaped_text.strip().splitlines()]
    if not lines:
        return [f'{indentation}""""""{line_ending}']
    if len(lines) == 1:
        return [f'{indentation}"""{lines[0]}"""{line_ending}']

    formatted = [f'{indentation}"""{lines[0]}{line_ending}']
    for line in lines[1:]:
        if line:
            formatted.append(f"{indentation}{line}{line_ending}")
        else:
            formatted.append(line_ending)
    formatted.append(f'{indentation}"""{line_ending}')
    return formatted


def _describe_import(node):
    """Generate detailed, domain-aware commentary for Python imports (standard library only)."""
    known = {
        "numpy": "# Imports NumPy library for high-performance N-dimensional array processing and numerical computations",
        "pandas": "# Imports Pandas data analysis library for tabular DataFrames and structured data manipulation",
        "matplotlib": "# Imports Matplotlib visualization engine for charting and scientific graphics",
        "matplotlib.pyplot": "# Imports Matplotlib's pyplot interface for data visualization and figure rendering",
        "torch": "# Imports PyTorch deep learning framework for tensor computation and neural network modeling",
        "tensorflow": "# Imports TensorFlow platform for machine learning model training and inference",
        "scipy": "# Imports SciPy library for scientific computing, optimization, and linear algebra",
        "sklearn": "# Imports Scikit-Learn toolkit for predictive modeling and machine learning algorithms",
        "requests": "# Imports Requests HTTP client library for network communication and REST API requests",
        "os": "# Imports Python standard library 'os' module for portable operating system and file path operations",
        "sys": "# Imports Python standard library 'sys' module for system-specific parameters and runtime control",
        "json": "# Imports Python standard library 'json' module for encoding and decoding JSON structured data",
        "re": "# Imports Python standard library 're' module for regular expression parsing and string pattern matching",
        "math": "# Imports Python standard library 'math' module for mathematical functions and numeric constants",
        "random": "# Imports standard library 'random' module for pseudo-random number generation",
        "datetime": "# Imports standard library 'datetime' module for manipulating dates and timestamps",
        "typing": "# Imports standard library 'typing' module for runtime type annotations and static validation",
        "pathlib": "# Imports standard library 'pathlib' module for object-oriented filesystem paths",
        "collections": "# Imports standard library 'collections' module for specialized container datatypes",
        "subprocess": "# Imports standard library 'subprocess' module for spawning processes and communicating with OS pipes",
        "ast": "# Imports Python standard library 'ast' module for syntax tree analysis",
        "logging": "# Imports Python standard library 'logging' module for structured logging",
        "time": "# Imports Python standard library 'time' module for time access and conversions",
        "shutil": "# Imports Python standard library 'shutil' module for file utilities",
        "sqlite3": "# Imports Python standard library 'sqlite3' module for SQLite database interaction",
        "pickle": "# Imports Python standard library 'pickle' module for object serialization",
    }
    if isinstance(node, ast.Import):
        comments = []
        for alias in node.names:
            name = alias.name
            asname = alias.asname
            alias_part = f", aliased as '{asname}'" if asname else ""
            if name in known:
                comments.append(f"{known[name]}{alias_part}.")
        return "\n".join(comments) if comments else None

    if isinstance(node, ast.ImportFrom):
        mod = node.module or ""
        names = [f"{a.name} as {a.asname}" if a.asname else a.name for a in node.names]
        names_str = ", ".join(names[:4]) + ("..." if len(names) > 4 else "")
        known_from = {
            "math": f"# Imports {names_str} from 'math' module for mathematical computations.",
            "os": f"# Imports {names_str} from 'os' module for filesystem and environment interaction.",
            "pathlib": f"# Imports {names_str} from 'pathlib' for object-oriented path manipulation.",
            "typing": f"# Imports type hint symbols ({names_str}) from 'typing' for static type annotations.",
            "datetime": f"# Imports {names_str} from 'datetime' for date and time parsing.",
            "collections": f"# Imports container types ({names_str}) from 'collections'.",
            "subprocess": f"# Imports process management functions ({names_str}) from 'subprocess'.",
            "ast": f"# Imports AST nodes and parsing utilities ({names_str}) from 'ast'.",
        }
        if mod in known_from:
            return known_from[mod]
        if mod in known:
            return f"# Imports {names_str} from '{mod}'."
        return None
    return None


def _fallback_comment_code(
    source_code,
    analysis=None,
    docstring_style=None,
    enrich_existing=False,
    custom_docstrings=None,
):
    """Generate AST-anchored comments without changing executable statements."""
    if isinstance(analysis, str):
        if docstring_style is None:
            docstring_style = analysis
        analysis = None
    if analysis is None:
        analysis = analyze_code(source_code)
    tree = ast.parse(source_code)
    comments_by_line = {}
    docstrings_by_line = {}
    docstrings_by_span = {}
    dynamic_sql_names = {
        target.id
        for node in ast.walk(tree)
        if isinstance(node, (ast.Assign, ast.AnnAssign))
        and (
            isinstance(node.value, ast.JoinedStr)
            or (
                isinstance(node.value, ast.BinOp)
                and isinstance(node.value.op, ast.Mod)
            )
            or (
                isinstance(node.value, ast.Call)
                and isinstance(node.value.func, ast.Attribute)
                and node.value.func.attr in {"format", "format_map"}
            )
        )
        for target in (
            node.targets if isinstance(node, ast.Assign) else [node.target]
        )
        if isinstance(target, ast.Name)
        and any(marker in target.id.lower() for marker in ("query", "sql", "statement"))
    }

    def add_comment(node, text, priority):
        line_number = getattr(node, "lineno", None)
        if line_number is None and isinstance(node, ast.match_case):
            line_number = getattr(getattr(node, "pattern", None), "lineno", None)
            if line_number is None and getattr(node, "body", None):
                line_number = getattr(node.body[0], "lineno", None)
        decorators = getattr(node, "decorator_list", ())
        if decorators:
            line_number = min(
                line_number,
                *(decorator.lineno for decorator in decorators),
            )
        if line_number is None or not text:
            return
        current = comments_by_line.get(line_number)
        if current is None:
            comments_by_line[line_number] = (priority, text)
        elif text not in current[1] and text.startswith(
            ("# Security review:", "# [AST-SECURITY] Security review:")
        ):
            comments_by_line[line_number] = (
                min(priority, current[0]),
                current[1] + "\n" + text,
            )
        elif priority < current[0]:
            comments_by_line[line_number] = (priority, text)

    def first_body_line(node):
        if not node.body:
            return None
        statement = node.body[0]
        decorators = getattr(statement, "decorator_list", ())
        if decorators:
            return min(decorator.lineno for decorator in decorators)
        return getattr(statement, "lineno", None)

    function_nodes = (ast.FunctionDef, ast.AsyncFunctionDef)
    for type_error in analysis.get("type_errors", []):
        if isinstance(type_error, dict):
            line_number = type_error.get("lineno")
            comment = type_error.get("comment")
            if isinstance(line_number, int) and isinstance(comment, str):
                current = comments_by_line.get(line_number)
                if current is None or current[0] > 1:
                    comments_by_line[line_number] = (1, comment)

    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            desc = _describe_import(node)
            if desc:
                add_comment(node, desc, 20)
        elif isinstance(node, function_nodes):
            existing_docstring = ast.get_docstring(node, clean=False)
            if existing_docstring is None:
                insertion_line = first_body_line(node)
                if insertion_line and insertion_line > node.lineno:
                    custom_doc = None
                    if custom_docstrings:
                        custom_doc = custom_docstrings.get((node.name, node.lineno))
                        if custom_doc is None:
                            custom_doc = custom_docstrings.get(node.name)
                    if custom_doc is not None:
                        docstrings_by_line[insertion_line] = custom_doc
                    else:
                        docstrings_by_line[insertion_line] = _function_docstring(
                            node, docstring_style=docstring_style
                        )
                else:
                    add_comment(
                        node,
                        f"# {_describe_function_semantics(node)}",
                        10,
                    )
            elif (
                enrich_existing
                and len(existing_docstring.strip()) <= 120
                and "\n" not in existing_docstring.strip()
            ):
                docstring_expression = node.body[0]
                enriched = _enrich_placeholder_docstring(
                    existing_docstring,
                    _function_docstring(node, docstring_style=docstring_style),
                )
                if enriched != existing_docstring:
                    docstrings_by_span[
                        (docstring_expression.lineno, docstring_expression.end_lineno)
                    ] = enriched
        elif isinstance(node, ast.ClassDef):
            bases = [ast.unparse(base) for base in node.bases]
            detail = f" extending {', '.join(bases)}" if bases else ""
            add_comment(node, f"# Defines class {node.name}{detail}.", 10)
            existing_docstring = ast.get_docstring(node, clean=False)
            if existing_docstring is None and node.body:
                insertion_line = first_body_line(node)
                if insertion_line and insertion_line > node.lineno:
                    custom_doc = None
                    if custom_docstrings:
                        custom_doc = custom_docstrings.get((node.name, node.lineno))
                        if custom_doc is None:
                            custom_doc = custom_docstrings.get(node.name)
                    if custom_doc is not None:
                        docstrings_by_line[insertion_line] = custom_doc
                    else:
                        docstrings_by_line[insertion_line] = _class_docstring(node)
            elif (
                enrich_existing
                and existing_docstring
                and len(existing_docstring.strip()) <= 120
                and "\n" not in existing_docstring.strip()
            ):
                docstring_expression = node.body[0]
                enriched = _enrich_placeholder_docstring(
                    existing_docstring,
                    _class_docstring(node),
                )
                if enriched != existing_docstring:
                    docstrings_by_span[
                        (docstring_expression.lineno, docstring_expression.end_lineno)
                    ] = enriched
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            value = node.value
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            target_names = {
                target.id.lower() for target in targets if isinstance(target, ast.Name)
            }
            if (
                isinstance(value, ast.Constant)
                and isinstance(value.value, str)
                and any(
                    marker in name
                    for name in target_names
                    for marker in ("password", "passwd", "secret", "token", "api_key")
                )
            ):
                add_comment(
                    node,
                    "# [AST-SECURITY] Potential hardcoded credential; load secrets from a protected environment or secret store.",
                    0,
                )
            if isinstance(value, ast.Call) and _safe_call_name(value.func) == "sorted":
                add_comment(node, f"# {_describe_sorted_call(value).capitalize()}.", 15)
            else:
                add_comment(node, _assignment_description(node), 30)
        elif isinstance(node, ast.AugAssign):
            operator = {
                ast.Add: "adding",
                ast.Sub: "subtracting",
                ast.Mult: "multiplying by",
                ast.Div: "dividing by",
                ast.FloorDiv: "floor-dividing by",
                ast.Mod: "taking the remainder with",
                ast.Pow: "raising to the power of",
            }.get(type(node.op), "applying an operation with")
            add_comment(
                node,
                f"# Updates {ast.unparse(node.target)} by {operator} {ast.unparse(node.value)}.",
                30,
            )
        elif isinstance(node, ast.If):
            condition = _describe_condition(node.test)
            branch_returns = _returns_in_statements(node.body)
            if branch_returns:
                comment = f"# Branch: when {condition}, returns {', '.join(branch_returns[:2])}."
            else:
                comment = f"# Branch: runs this block only when {condition}."
            add_comment(node, comment, 20)
        elif isinstance(node, (ast.For, ast.AsyncFor)):
            add_comment(
                node,
                f"# Iterates over {ast.unparse(node.iter)} with {ast.unparse(node.target)}.",
                20,
            )
        elif isinstance(node, ast.While):
            add_comment(
                node,
                f"# Repeats this block while {ast.unparse(node.test)} is true.",
                20,
            )
        elif isinstance(node, (ast.With, ast.AsyncWith)):
            resources = ", ".join(ast.unparse(item.context_expr) for item in node.items)
            add_comment(node, f"# Manages the {resources} resource for this block.", 20)
        elif isinstance(node, ast.Try):
            add_comment(
                node, "# Attempts this block and handles matching exceptions below.", 20
            )
        elif isinstance(node, ast.ExceptHandler):
            exception_name = ast.unparse(node.type) if node.type else "any exception"
            target = f" as {node.name}" if node.name else ""
            add_comment(
                node,
                f"# Handles {exception_name}{target} raised by the protected block.",
                20,
            )
        elif isinstance(node, ast.Assert):
            add_comment(node, f"# Checks that {ast.unparse(node.test)} is true.", 20)
        elif isinstance(node, ast.Raise):
            message = (
                f" with {ast.unparse(node.cause)} as its cause" if node.cause else ""
            )
            add_comment(
                node,
                f"# Raises {ast.unparse(node.exc) if node.exc else 'the active exception'}{message}.",
                20,
            )
        elif isinstance(node, ast.Match):
            add_comment(
                node, f"# Selects a case matching {ast.unparse(node.subject)}.", 20
            )
        elif isinstance(node, ast.match_case):
            add_comment(node, f"# Handles the pattern {ast.unparse(node.pattern)}.", 20)
        elif isinstance(node, ast.Call):
            call_name = _safe_call_name(node.func)
            lowered_name = call_name.lower()
            if call_name in {
                "eval",
                "exec",
                "compile",
                "os.system",
                "subprocess.call",
                "subprocess.run",
                "subprocess.Popen",
                "subprocess.check_call",
            }:
                add_comment(
                    node,
                    f"# [AST-SECURITY] Security warning: {call_name} executes code or a system command.",
                    0,
                )
            elif (
                lowered_name == "sqlite3"
                or lowered_name.startswith("sqlite3.")
                or lowered_name.startswith("subprocess.")
                or lowered_name.startswith("requests.")
                or lowered_name in {"open", "builtins.open", "pickle.load", "pickle.loads", "re.compile"}
                or lowered_name.startswith("pickle.")
                or lowered_name.endswith(".open")
            ):
                add_comment(
                    node,
                    f"# [AST-SECURITY] Security review: inspect {call_name} inputs, trust boundaries, and error handling.",
                    0,
                )
            elif (
                lowered_name.endswith(".execute")
                and node.args
                and isinstance(node.args[0], ast.Name)
                and node.args[0].id in dynamic_sql_names
            ):
                add_comment(
                    node,
                    "# [AST-SECURITY] Potential SQL injection: verify the query uses placeholders and binds values separately.",
                    0,
                )
            elif call_name == "print":
                add_comment(node, "# Output: writes the current result or state.", 30)
        elif isinstance(node, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
            add_comment(
                node,
                f"# Builds a {type(node).__name__.replace('Comp', ' comprehension').replace('Exp', ' expression')} from {_describe_comprehension(node)}.",
                25,
            )
        elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            add_comment(
                node,
                f"# Calls {ast.unparse(node.value.func)} and discards its return value.",
                40,
            )

    output = []
    lines = source_code.splitlines(keepends=True)
    line_number = 1
    while line_number <= len(lines):
        raw_line = lines[line_number - 1]
        line = raw_line.rstrip("\r\n")
        line_ending = raw_line[len(line) :]
        docstring = docstrings_by_span.get((line_number, line_number))
        if docstring:
            indentation = line[: len(line) - len(line.lstrip())]
            output.extend(
                _format_docstring_lines(
                    docstring, indentation, line_ending or "\n"
                )
            )
            line_number += 1
            continue
        comment = comments_by_line.get(line_number)
        docstring = docstrings_by_line.get(line_number)
        if docstring:
            indentation = line[: len(line) - len(line.lstrip())]
            output.extend(
                _format_docstring_lines(
                    docstring,
                    indentation,
                    line_ending or "\n",
                )
            )
        if comment:
            indentation = line[: len(line) - len(line.lstrip())]
            comment_ending = line_ending or "\n"
            output.extend(
                f"{indentation}{comment_line}{comment_ending}"
                for comment_line in comment[1].splitlines()
            )
        output.append(raw_line)
        line_number += 1
    return "".join(output)


def _generate_with_model(source_code, analysis):
    if not client:
        raise RuntimeError("AI service is unavailable in this environment.")

    messages = build_ai_messages(source_code, analysis)
    response = client.chat.completions.create(
        model=model_provider.MODEL_NAME,
        messages=messages,
        max_tokens=4000,
        temperature=0.1,
        extra_body=model_provider.provider_extra_body(),
    )

    commented = (response.choices[0].message.content or "").strip()
    if commented.startswith("```"):
        lines = commented.splitlines()
        commented = "\n".join(
            line for line in lines if not line.strip().startswith("```")
        )
    return commented.strip()


def generate_commented_code(source_code, analysis, docstring_style=None):
    """Generate model-backed comments, using AST comments for known type errors."""
    style = docstring_style or getattr(AppConfig, "DOCSTRING_STYLE", "google")
    if not client:
        logger.info("No AI provider is configured; using deterministic AST comments.")
        return _fallback_comment_code(source_code, analysis, docstring_style=style), "ast"
    if analysis.get("type_errors"):
        return _fallback_comment_code(source_code, analysis, docstring_style=style), "ast"

    try:
        model_output = _generate_with_model(source_code, analysis)
    except Exception as exc:
        logger.warning(
            "AI provider comment generation failed (%s); using deterministic AST comments.",
            type(exc).__name__,
        )
        return _fallback_comment_code(source_code, analysis, docstring_style=style), "ast"

    validation = validate_generated_code(source_code, model_output)
    if not validation["is_valid"]:
        logger.warning(
            "Rejected AI-generated comments that failed code validation; "
            "using deterministic AST comments."
        )
        return _fallback_comment_code(source_code, analysis, docstring_style=style), "ast"
    original_attack = detect_attack(source_code, content_type="code")
    generated_attack = detect_attack(model_output, content_type="code")
    added_attack_categories = set(generated_attack["categories"]) - set(
        original_attack["categories"]
    )
    if added_attack_categories:
        logger.warning(
            "Rejected AI-generated comments with new security categories=%s",
            ",".join(sorted(added_attack_categories)),
        )
        return _fallback_comment_code(source_code, analysis, docstring_style=style), "ast"
    if not has_added_comments(source_code, model_output):
        logger.warning(
            "AI response added no comments; using deterministic AST comments."
        )
        return _fallback_comment_code(source_code, analysis, docstring_style=style), "ast"
    return model_output, "ai"
