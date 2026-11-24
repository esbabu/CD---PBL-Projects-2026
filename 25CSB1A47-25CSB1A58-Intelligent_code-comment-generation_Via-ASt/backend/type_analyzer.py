"""Conservative checks for operations whose operand types are statically known.

Types come only from literals, simple built-in calls, assignments, and built-in
annotations. Unknown values stay unknown so this pass avoids speculative warnings.
"""

import ast
from collections.abc import Iterator

TypeName = str | None
TypeEnvironment = dict[str, TypeName]
TypeFinding = dict[str, int | str]

_BUILTIN_TYPES = {
    "bool": "bool",
    "bytes": "bytes",
    "complex": "complex",
    "dict": "dict",
    "float": "float",
    "int": "int",
    "list": "list",
    "set": "set",
    "str": "str",
    "tuple": "tuple",
    "List": "list",
    "Dict": "dict",
    "Set": "set",
    "Tuple": "tuple",
}
_NUMERIC_TYPES = {"bool", "int", "float", "complex"}
_SEQUENCE_TYPES = {"bytes", "list", "str", "tuple"}
_SEQUENCE_FORMAT_TYPES = {"tuple", "dict"}
_OPERATOR_NAMES = {
    ast.Add: "+",
    ast.Sub: "-",
    ast.Mult: "*",
    ast.Div: "/",
    ast.FloorDiv: "//",
    ast.Mod: "%",
    ast.Pow: "**",
}


def _target_names(target: ast.expr) -> Iterator[str]:
    """Yield names written by simple, unpacked, or starred assignment targets."""
    if isinstance(target, ast.Name):
        yield target.id
    elif isinstance(target, (ast.Tuple, ast.List)):
        for item in target.elts:
            yield from _target_names(item)
    elif isinstance(target, ast.Starred):
        yield from _target_names(target.value)


def _shadowed_builtins(tree: ast.AST) -> set[str]:
    """Collect names that make built-in call inference unsafe."""
    shadowed = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            shadowed.add(node.id)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            shadowed.add(node.name)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                arguments = (
                    node.args.posonlyargs + node.args.args + node.args.kwonlyargs
                )
                shadowed.update(arg.arg for arg in arguments)
                if node.args.vararg:
                    shadowed.add(node.args.vararg.arg)
                if node.args.kwarg:
                    shadowed.add(node.args.kwarg.arg)
        elif isinstance(node, ast.Import):
            shadowed.update(
                alias.asname or alias.name.split(".")[0] for alias in node.names
            )
        elif isinstance(node, ast.ImportFrom):
            shadowed.update(alias.asname or alias.name for alias in node.names)
    return shadowed


def _annotation_symbol(
    annotation: ast.expr,
    typing_modules: set[str],
    typing_names: dict[str, str],
) -> str | None:
    if isinstance(annotation, ast.Name):
        return typing_names.get(annotation.id, annotation.id)
    if (
        isinstance(annotation, ast.Attribute)
        and isinstance(annotation.value, ast.Name)
        and annotation.value.id in typing_modules
    ):
        return annotation.attr
    return None


def _annotation_type(
    annotation: ast.expr | None,
    typing_modules: set[str],
    typing_names: dict[str, str],
) -> TypeName:
    """Resolve annotations only when they name a supported built-in type."""
    if isinstance(annotation, (ast.Name, ast.Attribute)):
        symbol = _annotation_symbol(annotation, typing_modules, typing_names)
        return _BUILTIN_TYPES.get(symbol) if symbol is not None else None
    if isinstance(annotation, ast.Constant) and annotation.value is None:
        return "NoneType"
    if isinstance(annotation, ast.Subscript):
        annotation_name = _annotation_symbol(
            annotation.value, typing_modules, typing_names
        )
        if annotation_name == "Optional":
            return _annotation_type(
                annotation.slice, typing_modules, typing_names
            )
        base = (
            _BUILTIN_TYPES.get(annotation_name)
            if annotation_name is not None
            else None
        )
        if base is None:
            base = _annotation_type(
                annotation.value, typing_modules, typing_names
            )
        if base:
            return base
    if isinstance(annotation, ast.BinOp) and isinstance(annotation.op, ast.BitOr):
        left_type = _annotation_type(
            annotation.left, typing_modules, typing_names
        )
        right_type = _annotation_type(
            annotation.right, typing_modules, typing_names
        )
        if left_type == "NoneType" and right_type:
            return right_type
        if right_type == "NoneType" and left_type:
            return left_type
        if left_type and right_type and left_type == right_type:
            return left_type
    return None


def _operation_is_valid(
    operator: ast.operator, left_type: str, right_type: str
) -> bool:
    """Check supported operand combinations without assuming user-defined behavior."""
    if isinstance(operator, ast.Add):
        return (left_type in _NUMERIC_TYPES and right_type in _NUMERIC_TYPES) or (
            left_type == right_type and left_type in _SEQUENCE_TYPES
        )

    if isinstance(operator, ast.Mult):
        return (
            (left_type in _NUMERIC_TYPES and right_type in _NUMERIC_TYPES)
            or (left_type in _SEQUENCE_TYPES and right_type in {"bool", "int"})
            or (right_type in _SEQUENCE_TYPES and left_type in {"bool", "int"})
        )

    if isinstance(operator, ast.Mod):
        if left_type == "str" and right_type in _SEQUENCE_FORMAT_TYPES:
            return True
        return (
            left_type != "complex"
            and right_type != "complex"
            and left_type in _NUMERIC_TYPES
            and right_type in _NUMERIC_TYPES
        )

    return left_type in _NUMERIC_TYPES and right_type in _NUMERIC_TYPES


def _operation_result_type(
    operator: ast.operator,
    left_type: str,
    right_type: str,
) -> str:
    """Infer a result type after the operand combination has been validated."""
    if (
        isinstance(operator, ast.Add)
        and left_type == right_type
        and left_type in _SEQUENCE_TYPES
    ):
        return left_type
    if isinstance(operator, ast.Mult) and left_type in _SEQUENCE_TYPES:
        return left_type
    if isinstance(operator, ast.Mult) and right_type in _SEQUENCE_TYPES:
        return right_type
    if isinstance(operator, ast.Mod) and left_type == "str":
        return "str"
    if "complex" in (left_type, right_type):
        return "complex"
    if "float" in (left_type, right_type) or isinstance(operator, ast.Div):
        return "float"
    return "int"


def _literal_type(node: ast.Constant) -> TypeName:
    """Return the built-in type represented by a supported literal."""
    value = node.value
    if value is None:
        return "NoneType"
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, int):
        return "int"
    if isinstance(value, float):
        return "float"
    if isinstance(value, complex):
        return "complex"
    if isinstance(value, str):
        return "str"
    if isinstance(value, bytes):
        return "bytes"
    return None


class _TypeAnalyzer:
    """Walk statements while tracking only types known with high confidence."""

    def __init__(self, tree: ast.Module) -> None:
        self.tree = tree
        self.findings: list[TypeFinding] = []
        self.shadowed = _shadowed_builtins(tree)
        self.typing_modules: set[str] = set()
        self.typing_names: dict[str, str] = {}
        for node in tree.body:
            if isinstance(node, ast.Import):
                self.typing_modules.update(
                    alias.asname or alias.name
                    for alias in node.names
                    if alias.name == "typing"
                )
            elif isinstance(node, ast.ImportFrom) and node.module == "typing":
                self.typing_names.update(
                    {
                        alias.asname or alias.name: alias.name
                        for alias in node.names
                    }
                )

    def _check_operation(
        self,
        node: ast.BinOp | ast.AugAssign,
        left_type: TypeName,
        right_type: TypeName,
    ) -> TypeName:
        if left_type is None or right_type is None:
            return None
        operator_name = _OPERATOR_NAMES.get(type(node.op))
        if operator_name is None:
            return None

        if _operation_is_valid(node.op, left_type, right_type):
            return _operation_result_type(node.op, left_type, right_type)

        self.findings.append(
            {
                "lineno": node.lineno,
                "expression": ast.unparse(node),
                "left_type": left_type,
                "right_type": right_type,
                "operator": operator_name,
            }
        )
        return None

    def _infer(self, node: ast.expr, environment: TypeEnvironment) -> TypeName:
        """Infer an expression type and record definite incompatible operations."""
        if isinstance(node, ast.Constant):
            return _literal_type(node)
        if isinstance(node, ast.Name):
            return environment.get(node.id)
        if isinstance(node, ast.BinOp):
            left_type = self._infer(node.left, environment)
            right_type = self._infer(node.right, environment)
            return self._check_operation(node, left_type, right_type)
        if isinstance(node, ast.Call):
            for argument in node.args:
                self._infer(argument, environment)
            for keyword in node.keywords:
                self._infer(keyword.value, environment)
            if isinstance(node.func, ast.Name) and node.func.id not in self.shadowed:
                if node.func.id == "input":
                    return "str"
                if node.func.id in _BUILTIN_TYPES:
                    return _BUILTIN_TYPES[node.func.id]
            self._infer(node.func, environment)
            return None
        if isinstance(node, ast.JoinedStr):
            for value in node.values:
                self._infer(value, environment)
            return "str"
        if isinstance(node, ast.List):
            for item in node.elts:
                self._infer(item, environment)
            return "list"
        if isinstance(node, ast.Tuple):
            for item in node.elts:
                self._infer(item, environment)
            return "tuple"
        if isinstance(node, ast.Set):
            for item in node.elts:
                self._infer(item, environment)
            return "set"
        if isinstance(node, ast.Dict):
            for key, value in zip(node.keys, node.values):
                if key is not None:
                    self._infer(key, environment)
                self._infer(value, environment)
            return "dict"
        if isinstance(node, ast.UnaryOp):
            operand_type = self._infer(node.operand, environment)
            if isinstance(node.op, ast.Not):
                return "bool"
            return operand_type
        if isinstance(node, ast.IfExp):
            self._infer(node.test, environment)
            body_type = self._infer(node.body, environment)
            else_type = self._infer(node.orelse, environment)
            return body_type if body_type == else_type else None
        if isinstance(node, ast.Compare):
            self._infer(node.left, environment)
            for comparator in node.comparators:
                self._infer(comparator, environment)
            return "bool"
        if isinstance(node, ast.BoolOp):
            for value in node.values:
                self._infer(value, environment)
            return None
        if isinstance(node, ast.Subscript):
            self._infer(node.value, environment)
            self._infer(node.slice, environment)
            return None

        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.expr):
                self._infer(child, environment)
        return None

    def _bind(
        self,
        target: ast.expr,
        inferred_type: TypeName,
        environment: TypeEnvironment,
    ) -> None:
        """Bind a known type, or forget it when the new value is unknown."""
        for name in _target_names(target):
            if inferred_type is None:
                environment.pop(name, None)
            else:
                environment[name] = inferred_type

    def _process_block(
        self,
        statements: list[ast.stmt],
        environment: TypeEnvironment,
    ) -> None:
        """Analyze one scope, copying environments at uncertain control-flow joins."""
        for statement in statements:
            if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for default in statement.args.defaults + statement.args.kw_defaults:
                    if default is not None:
                        self._infer(default, environment)
                local_environment = {}
                all_arguments = (
                    statement.args.posonlyargs
                    + statement.args.args
                    + statement.args.kwonlyargs
                )
                for argument in all_arguments:
                    local_environment[argument.arg] = _annotation_type(
                        argument.annotation,
                        self.typing_modules,
                        self.typing_names,
                    )
                if statement.args.vararg:
                    local_environment[statement.args.vararg.arg] = _annotation_type(
                        statement.args.vararg.annotation,
                        self.typing_modules,
                        self.typing_names,
                    )
                if statement.args.kwarg:
                    local_environment[statement.args.kwarg.arg] = _annotation_type(
                        statement.args.kwarg.annotation,
                        self.typing_modules,
                        self.typing_names,
                    )
                self._process_block(statement.body, local_environment)
                environment.pop(statement.name, None)
                continue
            if isinstance(statement, ast.ClassDef):
                self._process_block(statement.body, {})
                environment.pop(statement.name, None)
                continue
            if isinstance(statement, (ast.Assign, ast.AnnAssign)):
                value_type = (
                    self._infer(statement.value, environment)
                    if statement.value
                    else None
                )
                targets = (
                    statement.targets
                    if isinstance(statement, ast.Assign)
                    else [statement.target]
                )
                for target in targets:
                    self._bind(target, value_type, environment)
                continue
            if isinstance(statement, ast.AugAssign):
                left_type = self._infer(statement.target, environment)
                right_type = self._infer(statement.value, environment)
                result_type = self._check_operation(statement, left_type, right_type)
                self._bind(statement.target, result_type, environment)
                continue
            if isinstance(statement, ast.If):
                self._infer(statement.test, environment)
                body_environment = environment.copy()
                self._process_block(statement.body, body_environment)
                else_environment = environment.copy()
                self._process_block(statement.orelse, else_environment)
                shared_names = body_environment.keys() & else_environment.keys()
                environment.clear()
                environment.update(
                    {
                        name: body_environment[name]
                        for name in shared_names
                        if body_environment[name] == else_environment[name]
                    }
                )
                continue
            if isinstance(statement, (ast.For, ast.AsyncFor)):
                self._infer(statement.iter, environment)
                body_environment = environment.copy()
                self._bind(statement.target, None, body_environment)
                self._process_block(statement.body, body_environment)
                self._process_block(statement.orelse, environment.copy())
                continue
            if isinstance(statement, ast.While):
                self._infer(statement.test, environment)
                self._process_block(statement.body, environment.copy())
                self._process_block(statement.orelse, environment.copy())
                continue
            if isinstance(statement, (ast.With, ast.AsyncWith)):
                local_environment = environment.copy()
                for item in statement.items:
                    self._infer(item.context_expr, environment)
                    if item.optional_vars:
                        self._bind(item.optional_vars, None, local_environment)
                self._process_block(statement.body, local_environment)
                continue
            if isinstance(statement, ast.Try):
                self._process_block(statement.body, environment.copy())
                for handler in statement.handlers:
                    handler_environment = environment.copy()
                    if handler.type:
                        self._infer(handler.type, environment)
                    if handler.name:
                        handler_environment.pop(handler.name, None)
                    self._process_block(handler.body, handler_environment)
                self._process_block(statement.orelse, environment.copy())
                self._process_block(statement.finalbody, environment.copy())
                continue
            if isinstance(statement, ast.Match):
                self._infer(statement.subject, environment)
                for case in statement.cases:
                    case_environment = environment.copy()
                    if case.guard:
                        self._infer(case.guard, case_environment)
                    self._process_block(case.body, case_environment)
                continue
            if isinstance(statement, (ast.Return, ast.Expr, ast.Raise, ast.Assert)):
                for _, value in ast.iter_fields(statement):
                    if isinstance(value, ast.expr):
                        self._infer(value, environment)
                    elif isinstance(value, list):
                        for item in value:
                            if isinstance(item, ast.expr):
                                self._infer(item, environment)

    def analyze(self) -> list[TypeFinding]:
        """Analyze the module and return all definite operand mismatches."""
        self._process_block(self.tree.body, {})
        return self.findings


def find_definite_type_errors(source_code: str) -> list[TypeFinding]:
    """Find only operand mismatches proven by literals, built-ins, or annotations."""
    tree = ast.parse(source_code)
    findings = _TypeAnalyzer(tree).analyze()
    for finding in findings:
        message = (
            f"Known incompatible operands ({finding['left_type']} {finding['operator']} "
            f"{finding['right_type']}) in '{finding['expression']}'. This will raise "
            "TypeError if the expression is evaluated; convert explicitly according to intent."
        )
        finding["message"] = message
        finding["comment"] = (
            f"# Type error: {finding['left_type']} {finding['operator']} "
            f"{finding['right_type']} is incompatible and raises TypeError if evaluated."
        )
    return findings
