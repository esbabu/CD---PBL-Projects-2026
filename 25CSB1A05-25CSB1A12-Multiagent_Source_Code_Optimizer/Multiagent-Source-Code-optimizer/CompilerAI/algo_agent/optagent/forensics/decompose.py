"""Unit decomposition: parses code into individual units, extracts call graphs, implicit inputs/outputs, and classifies units."""
from __future__ import annotations

import ast
from typing import Any, Literal
from pydantic import BaseModel, Field


UnitClass = Literal[
    "local_pure",
    "state_coupled",
    "io_bound",
    "security_sensitive",
    "trivial",
    "script",
    "local",
]


class UnitSpec(BaseModel):
    name: str
    kind: Literal["function", "method", "script"]
    lineno: int
    end_lineno: int
    params: list[str] = Field(default_factory=list)
    unit_class: UnitClass = "local"
    implicit_inputs: list[str] = Field(default_factory=list)   # globals read, files, db, env
    implicit_outputs: list[str] = Field(default_factory=list)  # globals written, files written, stdout
    callees: list[str] = Field(default_factory=list)
    has_loops: bool = False
    is_recursive: bool = False
    security_concerns: list[str] = Field(default_factory=list)
    docstring: str | None = None
    source_slice: str = ""


class ImportSideEffect(BaseModel):
    lineno: int
    expression: str
    detail: str
    sink_type: str  # db, file, system, print, network


class ModuleDecomposition(BaseModel):
    units: dict[str, UnitSpec] = Field(default_factory=dict)
    call_graph: dict[str, list[str]] = Field(default_factory=dict)
    globals_declared: list[str] = Field(default_factory=list)
    import_side_effects: list[ImportSideEffect] = Field(default_factory=list)


class UnitDecomposer:
    """Decomposes source code into units and static dependencies."""

    @classmethod
    def decompose_python(cls, source: str) -> ModuleDecomposition:
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return ModuleDecomposition()

        source_lines = source.splitlines()
        globals_declared = []
        import_side_effects = []
        units: dict[str, UnitSpec] = {}
        call_graph: dict[str, list[str]] = {}

        # 1. Identify module globals and top-level side effects
        for node in tree.body:
            if isinstance(node, (ast.Assign, ast.AnnAssign)):
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                for t in targets:
                    if isinstance(t, ast.Name):
                        globals_declared.append(t.id)

                # Check if RHS has side effects (e.g. sqlite3.connect("students.db"))
                rhs_effects = cls._detect_call_effects(node.value)
                if rhs_effects:
                    line_txt = source_lines[node.lineno - 1] if node.lineno <= len(source_lines) else ""
                    for eff in rhs_effects:
                        import_side_effects.append(ImportSideEffect(
                            lineno=node.lineno,
                            expression=line_txt.strip(),
                            detail=eff["detail"],
                            sink_type=eff["type"],
                        ))

            elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
                # Top level call (like print or setup)
                line_txt = source_lines[node.lineno - 1] if node.lineno <= len(source_lines) else ""
                rhs_effects = cls._detect_call_effects(node.value)
                for eff in rhs_effects:
                    import_side_effects.append(ImportSideEffect(
                        lineno=node.lineno,
                        expression=line_txt.strip(),
                        detail=eff["detail"],
                        sink_type=eff["type"],
                    ))

        # 2. Extract function units and script block
        for node in tree.body:
            if isinstance(node, ast.FunctionDef):
                unit = cls._analyze_function(node, source_lines, globals_declared)
                units[unit.name] = unit
                call_graph[unit.name] = unit.callees

            elif isinstance(node, ast.If):
                # Check for if __name__ == "__main__":
                if cls._is_main_guard(node):
                    script_unit = cls._analyze_script_block(node, source_lines, globals_declared)
                    units["module"] = script_unit
                    call_graph["module"] = script_unit.callees

        return ModuleDecomposition(
            units=units,
            call_graph=call_graph,
            globals_declared=globals_declared,
            import_side_effects=import_side_effects,
        )

    @classmethod
    def _is_main_guard(cls, node: ast.If) -> bool:
        if isinstance(node.test, ast.Compare):
            left = node.test.left
            if isinstance(left, ast.Name) and left.id == "__name__":
                for comp in node.test.comparators:
                    if isinstance(comp, ast.Constant) and comp.value == "__main__":
                        return True
        return False

    @classmethod
    def _detect_call_effects(cls, node: ast.AST) -> list[dict[str, str]]:
        effects = []
        for n in ast.walk(node):
            if isinstance(n, ast.Call):
                callee = cls._get_callee_name(n.func)
                if "sqlite3" in callee or "connect" in callee:
                    effects.append({"type": "db", "detail": f"Database initialization: {callee}"})
                elif "open" in callee:
                    effects.append({"type": "file", "detail": f"File opened at import: {callee}"})
                elif "system" in callee or "popen" in callee or "subprocess" in callee:
                    effects.append({"type": "system", "detail": f"Command execution at import: {callee}"})
                elif "print" in callee:
                    effects.append({"type": "print", "detail": f"Stdout printed at import: {callee}"})
                elif "socket" in callee or "requests" in callee:
                    effects.append({"type": "network", "detail": f"Network call at import: {callee}"})
        return effects

    @classmethod
    def _get_callee_name(cls, node: ast.AST) -> str:
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            base = cls._get_callee_name(node.value)
            return f"{base}.{node.attr}" if base else node.attr
        return ""

    @classmethod
    def _analyze_function(cls, node: ast.FunctionDef, lines: list[str], module_globals: list[str]) -> UnitSpec:
        params = [a.arg for a in node.args.args]
        implicit_in = set()
        implicit_out = set()
        callees = []
        has_loops = False
        is_rec = False
        sec_concerns = []

        # Find variables written locally
        local_writes = set(params)
        for sub in ast.walk(node):
            if isinstance(sub, ast.For):
                has_loops = True
                if isinstance(sub.target, ast.Name):
                    local_writes.add(sub.target.id)
            elif isinstance(sub, ast.While):
                has_loops = True
            elif isinstance(sub, ast.Assign):
                for t in sub.targets:
                    if isinstance(t, ast.Name):
                        local_writes.add(t.id)

        # Walk AST to find implicit inputs/outputs, callees, effects
        for sub in ast.walk(node):
            if isinstance(sub, ast.Call):
                cname = cls._get_callee_name(sub.func)
                if cname:
                    callees.append(cname.split(".")[-1])
                if cname == node.name:
                    is_rec = True

                # Security / IO patterns
                if "md5" in cname or "hashlib" in cname:
                    sec_concerns.append("weak_hash_md5")
                if "open" in cname:
                    implicit_in.add("file:read")
                if "pickle.load" in cname:
                    implicit_in.add("pickle:load")
                    sec_concerns.append("unsafe_deserialization")
                if "os.system" in cname:
                    implicit_out.add("system:command")
                    sec_concerns.append("command_injection")
                if "os.remove" in cname:
                    implicit_out.add("file:delete")
                    sec_concerns.append("arbitrary_file_deletion")
                if "execute" in cname or "cursor" in cname:
                    implicit_in.add("db:query")
                    # Check for SQL concat
                    for arg in sub.args:
                        if isinstance(arg, ast.BinOp) and isinstance(arg.op, ast.Add):
                            sec_concerns.append("sql_injection")
                if "print" in cname:
                    implicit_out.add("stdout")
                    if "password" in repr(ast.dump(sub)).lower():
                        sec_concerns.append("password_hashes_leakage")

            elif isinstance(sub, ast.Name) and isinstance(sub.ctx, ast.Load):
                if sub.id in module_globals and sub.id not in local_writes:
                    implicit_in.add(f"global:{sub.id}")

            elif isinstance(sub, ast.Name) and isinstance(sub.ctx, ast.Store):
                if sub.id in module_globals:
                    implicit_out.add(f"global:{sub.id}")

            elif isinstance(sub, ast.Subscript) and isinstance(sub.ctx, ast.Store):
                if isinstance(sub.value, ast.Name) and sub.value.id in module_globals:
                    implicit_out.add(f"global:{sub.value.id}")

        # Check for in-place mutation like students.append or students.remove
        for sub in ast.walk(node):
            if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Attribute):
                if isinstance(sub.func.value, ast.Name) and sub.func.value.id in module_globals:
                    if sub.func.attr in ("append", "remove", "extend", "pop", "insert", "sort", "reverse", "clear"):
                        implicit_out.add(f"global:{sub.func.value.id}")

        # Classification
        # Priority: security_sensitive > io_bound > state_coupled > local
        unit_class: UnitClass = "local"
        if sec_concerns:
            unit_class = "security_sensitive"
        elif any(io_sig in "".join(implicit_in | implicit_out) for io_sig in ["file:", "db:", "system:"]):
            unit_class = "io_bound"
        elif any(g.startswith("global:") for g in (implicit_in | implicit_out)):
            unit_class = "state_coupled"
        else:
            unit_class = "local"

        slice_txt = "\n".join(lines[node.lineno - 1 : node.end_lineno]) if lines else ""

        return UnitSpec(
            name=node.name,
            kind="function",
            lineno=node.lineno,
            end_lineno=node.end_lineno or node.lineno,
            params=params,
            unit_class=unit_class,
            implicit_inputs=sorted(list(implicit_in)),
            implicit_outputs=sorted(list(implicit_out)),
            callees=callees,
            has_loops=has_loops,
            is_recursive=is_rec,
            security_concerns=sorted(list(set(sec_concerns))),
            docstring=ast.get_docstring(node),
            source_slice=slice_txt,
        )

    @classmethod
    def _analyze_script_block(cls, node: ast.If, lines: list[str], module_globals: list[str]) -> UnitSpec:
        callees = []
        for sub in ast.walk(node):
            if isinstance(sub, ast.Call):
                cname = cls._get_callee_name(sub.func)
                if cname:
                    callees.append(cname.split(".")[-1])

        slice_txt = "\n".join(lines[node.lineno - 1 : node.end_lineno]) if lines else ""

        return UnitSpec(
            name="module",
            kind="script",
            lineno=node.lineno,
            end_lineno=node.end_lineno or node.lineno,
            params=[],
            unit_class="script",
            implicit_inputs=[],
            implicit_outputs=["stdout"],
            callees=callees,
            has_loops=False,
            is_recursive=False,
            security_concerns=[],
            source_slice=slice_txt,
        )
