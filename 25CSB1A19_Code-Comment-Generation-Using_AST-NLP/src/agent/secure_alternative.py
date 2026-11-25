"""Generate a conservative secure alternative for common Python security findings."""

import ast


class SecureAlternativeBuilder:
    """Create a safer code alternative using deterministic AST transformations."""

    def build(self, source_code, issues):
        try:
            tree = ast.parse(source_code)
        except SyntaxError:
            return {
                "code": "",
                "changes": [],
                "limitations": ["The source code contains a syntax error, so a secure rewrite cannot be generated."],
            }

        self.changes = []
        self.needs_ast = False
        self.needs_os = False
        self.needs_shlex = False
        self.needs_hashlib = False
        self.needs_json = False
        self.needs_secrets = False

        transformer = _SecurityTransformer(self)
        tree = transformer.visit(tree)
        ast.fix_missing_locations(tree)

        self._ensure_imports(tree)
        ast.fix_missing_locations(tree)

        try:
            secure_code = ast.unparse(tree)
        except Exception:
            secure_code = source_code
            self.changes.append("Could not format the transformed AST; original source was retained.")

        limitations = self._limitations(issues)
        return {
            "code": secure_code,
            "changes": self.changes,
            "limitations": limitations,
        }

    def _ensure_imports(self, tree):
        existing = set()
        for node in tree.body:
            if isinstance(node, ast.Import):
                existing.update(alias.name.split('.')[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                existing.add(node.module.split('.')[0])

        imports = []
        if self.needs_ast and "ast" not in existing:
            imports.append(ast.Import(names=[ast.alias(name="ast", asname=None)]))
        if self.needs_os and "os" not in existing:
            imports.append(ast.Import(names=[ast.alias(name="os", asname=None)]))
        if self.needs_shlex and "shlex" not in existing:
            imports.append(ast.Import(names=[ast.alias(name="shlex", asname=None)]))
        if self.needs_hashlib and "hashlib" not in existing:
            imports.append(ast.Import(names=[ast.alias(name="hashlib", asname=None)]))
        if self.needs_json and "json" not in existing:
            imports.append(ast.Import(names=[ast.alias(name="json", asname=None)]))
        if self.needs_secrets and "secrets" not in existing:
            imports.append(ast.Import(names=[ast.alias(name="secrets", asname=None)]))

        if imports:
            tree.body = imports + tree.body

    def _limitations(self, issues):
        ids = {issue.get("id") for issue in issues}
        limitations = []
        if "SEC005" in ids:
            limitations.append("SQL injection needs a parameterized query chosen for the specific database API; review the query manually.")
        if "SEC009" in ids:
            limitations.append("Unsafe pickle deserialization cannot be safely converted automatically without knowing the data schema; prefer JSON or another safe format.")
        if "SEC012" in ids:
            limitations.append("Hardcoded endpoints were not blindly replaced because the correct configuration key depends on the deployment environment.")
        if "SEC003" in ids:
            limitations.append("Secret values are moved to environment variables; configure the matching environment variables before running the alternative.")
        if "SEC002" in ids:
            limitations.append("Command construction must still be validated against the application's allowed command set.")
        if "SEC001" in ids:
            limitations.append("Dynamic execution was replaced with literal parsing where possible; do not execute arbitrary user input.")
        return limitations


class _SecurityTransformer(ast.NodeTransformer):
    def __init__(self, builder):
        self.b = builder

    def visit_Call(self, node):
        self.generic_visit(node)

        # SEC001: eval(user_input) -> ast.literal_eval(user_input)
        if isinstance(node.func, ast.Name) and node.func.id == "eval":
            node.func = ast.Attribute(
                value=ast.Name(id="ast", ctx=ast.Load()),
                attr="literal_eval",
                ctx=ast.Load(),
            )
            self.b.needs_ast = True
            self.b.changes.append("Replaced eval() with ast.literal_eval() to prevent arbitrary code execution.")
            return node

        # SEC002: subprocess.run(..., shell=True) -> subprocess.run(..., check=True)
        if isinstance(node.func, ast.Attribute) and node.func.attr == "run":
            shell_true = any(
                kw.arg == "shell"
                and isinstance(kw.value, ast.Constant)
                and kw.value.value is True
                for kw in node.keywords
            )
            if shell_true:
                node.keywords = [kw for kw in node.keywords if kw.arg != "shell"]
                if not any(kw.arg == "check" for kw in node.keywords):
                    node.keywords.append(ast.keyword(arg="check", value=ast.Constant(value=True)))

                if node.args and not isinstance(node.args[0], (ast.List, ast.Tuple)):
                    node.args[0] = ast.Call(
                        func=ast.Attribute(
                            value=ast.Name(id="shlex", ctx=ast.Load()),
                            attr="split",
                            ctx=ast.Load(),
                        ),
                        args=[node.args[0]],
                        keywords=[],
                    )
                    self.b.needs_shlex = True
                self.b.changes.append("Removed shell=True and switched command execution to an argument list with check=True.")
            return node

        # SEC004: hashlib.md5/sha1 -> hashlib.sha256
        if isinstance(node.func, ast.Attribute) and node.func.attr.lower() in {"md5", "sha1"}:
            node.func = ast.Attribute(
                value=ast.Name(id="hashlib", ctx=ast.Load()),
                attr="sha256",
                ctx=ast.Load(),
            )
            self.b.needs_hashlib = True
            self.b.changes.append("Replaced weak MD5/SHA-1 hashing with SHA-256.")
            return node

        # SEC010: yaml.load(...) -> yaml.safe_load(...)
        if isinstance(node.func, ast.Attribute) and node.func.attr == "load":
            if isinstance(node.func.value, ast.Name) and node.func.value.id == "yaml":
                node.func.attr = "safe_load"
                self.b.changes.append("Replaced yaml.load() with yaml.safe_load().")
                return node

        # SEC011: random.choice(...) -> secrets.choice(...)
        if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
            if node.func.value.id == "random" and node.func.attr == "choice":
                node.func.value.id = "secrets"
                self.b.needs_secrets = True
                self.b.changes.append("Replaced random.choice() with secrets.choice() for security-sensitive randomness.")
                return node

        return node

    def visit_Assign(self, node):
        self.generic_visit(node)
        # SEC003: password="..." -> password=os.getenv("PASSWORD")
        if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            for target in node.targets:
                if isinstance(target, ast.Name) and _looks_like_secret(target.id):
                    env_name = target.id.upper()
                    node.value = ast.Call(
                        func=ast.Attribute(
                            value=ast.Name(id="os", ctx=ast.Load()),
                            attr="getenv",
                            ctx=ast.Load(),
                        ),
                        args=[ast.Constant(value=env_name)],
                        keywords=[],
                    )
                    self.b.needs_os = True
                    self.b.changes.append(f"Moved hardcoded secret '{target.id}' to the {env_name} environment variable.")
                    break
        return node

    def visit_ExceptHandler(self, node):
        self.generic_visit(node)
        if node.type is None:
            node.type = ast.Name(id="Exception", ctx=ast.Load())
            self.b.changes.append("Replaced bare except with except Exception.")
        return node

    def visit_Assert(self, node):
        self.generic_visit(node)
        # assert condition, message -> if not condition: raise ValueError(message)
        raise_call = ast.Call(
            func=ast.Name(id="ValueError", ctx=ast.Load()),
            args=[node.msg] if node.msg else [ast.Constant(value="Validation failed")],
            keywords=[],
        )
        replacement = ast.If(
            test=ast.UnaryOp(op=ast.Not(), operand=node.test),
            body=[ast.Raise(exc=raise_call, cause=None)],
            orelse=[],
        )
        self.b.changes.append("Replaced assert-based runtime validation with an explicit ValueError check.")
        return ast.copy_location(replacement, node)

    def visit_FunctionDef(self, node):
        self.generic_visit(node)
        return self._fix_mutable_defaults(node)

    def visit_AsyncFunctionDef(self, node):
        self.generic_visit(node)
        return self._fix_mutable_defaults(node)

    def _fix_mutable_defaults(self, node):
        mutable_positions = []
        defaults = list(node.args.defaults)
        first = len(node.args.posonlyargs) + len(node.args.args) - len(defaults)
        for idx, default in enumerate(defaults):
            if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                arg_index = first + idx
                if 0 <= arg_index < len(node.args.posonlyargs) + len(node.args.args):
                    arg = (node.args.posonlyargs + node.args.args)[arg_index]
                    defaults[idx] = ast.Constant(value=None)
                    mutable_positions.append((arg.arg, default))

        if mutable_positions:
            node.args.defaults = defaults
            init_nodes = []
            for name, original in mutable_positions:
                constructor = _constructor_for_literal(original)
                init_nodes.append(
                    ast.If(
                        test=ast.Compare(
                            left=ast.Name(id=name, ctx=ast.Load()),
                            ops=[ast.Is()],
                            comparators=[ast.Constant(value=None)],
                        ),
                        body=[ast.Assign(
                            targets=[ast.Name(id=name, ctx=ast.Store())],
                            value=constructor,
                        )],
                        orelse=[],
                    )
                )
            node.body = init_nodes + node.body
            self.b.changes.append(f"Replaced mutable default arguments in {node.name} with None initialization.")
        return node


def _looks_like_secret(name):
    lowered = name.lower()
    return any(token in lowered for token in (
        "password", "passwd", "secret", "api_key", "apikey", "token",
        "access_key", "private_key", "auth_key", "credentials",
    ))


def _constructor_for_literal(node):
    if isinstance(node, ast.List):
        return ast.List(elts=[], ctx=ast.Load())
    if isinstance(node, ast.Dict):
        return ast.Dict(keys=[], values=[])
    if isinstance(node, ast.Set):
        return ast.Set(elts=[])
    return ast.Constant(value=None)
