from __future__ import annotations
import ast

from ..schemas import (CallSite, Effect, EffectKind as K, FunctionFacts, ModuleFacts,
                       ParamInfo, Pattern)

MUTATING_METHODS = {"append", "extend", "insert", "remove", "pop", "clear", "sort", "reverse",
                    "add", "discard", "update", "setdefault", "popitem", "appendleft", "popleft",
                    "extendleft", "rotate", "difference_update", "intersection_update",
                    "symmetric_difference_update"}
EXTERNAL_MUTATORS = {"random.shuffle": 0, "heapq.heappush": 0, "heapq.heappop": 0,
                     "heapq.heapify": 0, "heapq.heapreplace": 0, "heapq.heappushpop": 0,
                     "bisect.insort": 0, "bisect.insort_left": 0, "bisect.insort_right": 0}
IO_METHODS = {"write", "writelines", "read", "readline", "readlines", "read_text", "write_text",
              "read_bytes", "write_bytes", "flush"}
BUILTIN_EFFECTS = {"print": K.PRINT, "input": K.INPUT, "open": K.FILE_IO, "exec": K.DYNAMIC_EXEC,
                   "eval": K.DYNAMIC_EXEC, "compile": K.DYNAMIC_EXEC, "__import__": K.DYNAMIC_EXEC}
PREFIX_EFFECTS = {
    "random": K.RANDOM, "numpy.random": K.RANDOM, "secrets": K.RANDOM, "uuid": K.RANDOM,
    "time": K.TIME, "datetime.datetime.now": K.TIME, "datetime.datetime.today": K.TIME,
    "datetime.datetime.utcnow": K.TIME, "datetime.date.today": K.TIME,
    "os.getenv": K.ENV, "os.environ": K.ENV, "sys.argv": K.ENV,
    "sys.stdout": K.PRINT, "sys.stderr": K.PRINT, "sys.stdin": K.INPUT, "logging": K.PRINT,
    "os.path": None, "os": K.FILE_IO, "shutil": K.FILE_IO, "pathlib": K.FILE_IO,
    "tempfile": K.FILE_IO, "glob": K.FILE_IO, "sqlite3": K.FILE_IO, "subprocess": K.SUBPROCESS,
    "socket": K.NETWORK, "requests": K.NETWORK, "urllib": K.NETWORK, "http": K.NETWORK,
    "httpx": K.NETWORK, "aiohttp": K.NETWORK, "threading": K.CONCURRENCY,
    "multiprocessing": K.CONCURRENCY, "concurrent": K.CONCURRENCY, "asyncio": K.CONCURRENCY,
}
CTOR_KINDS = {"list": "list", "sorted": "list", "tuple": "tuple", "set": "set",
              "frozenset": "set", "dict": "dict", "defaultdict": "dict", "Counter": "dict",
              "OrderedDict": "dict", "deque": "deque", "range": "range", "str": "str"}
ANN_KINDS = {"list": "list", "sequence": "list", "mutablesequence": "list", "tuple": "tuple",
             "set": "set", "frozenset": "set", "abstractset": "set", "dict": "dict",
             "mapping": "dict", "defaultdict": "dict", "counter": "dict", "str": "str",
             "deque": "deque"}


def _unp(n):
    return ast.unparse(n) if n is not None else None


def _ann_kind(ann) -> str | None:
    base = ast.unparse(ann).lower().split("[")[0].split(".")[-1]
    return ANN_KINDS.get(base)


def root_name(n) -> str | None:
    while isinstance(n, (ast.Attribute, ast.Subscript)):
        n = n.value
    return n.id if isinstance(n, ast.Name) else None


def _effect_for(fq: str):
    if fq in BUILTIN_EFFECTS:
        return BUILTIN_EFFECTS[fq]
    parts = fq.split(".")
    for i in range(len(parts), 0, -1):
        p = ".".join(parts[:i])
        if p in PREFIX_EFFECTS:
            return PREFIX_EFFECTS[p]
    return None


def _depth(node, d: int) -> int:
    """Syntactic loop-nesting depth (a hint, NOT complexity: two-pointer loops are depth 1 but O(n))."""
    if isinstance(node, (ast.For, ast.AsyncFor)):
        best = max(d + 1, _depth(node.iter, d))
        for s in node.body + node.orelse:
            best = max(best, _depth(s, d + 1))
        return best
    if isinstance(node, ast.While):
        best = d + 1
        for s in [node.test] + node.body + node.orelse:
            best = max(best, _depth(s, d + 1))
        return best
    if isinstance(node, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
        n = len(node.generators)
        best = d + n
        for i, g in enumerate(node.generators):
            best = max(best, _depth(g.iter, d + i))
            for c in g.ifs:
                best = max(best, _depth(c, d + n))
        elts = [node.key, node.value] if isinstance(node, ast.DictComp) else [node.elt]
        return max([best] + [_depth(e, d + n) for e in elts])
    return max([d] + [_depth(c, d) for c in ast.iter_child_nodes(node)])


class _Ctx:
    def __init__(self, tree: ast.Module):
        self.aliases: dict[str, str] = {}
        self.fn_names: set[str] = set()
        self.functions: list[ast.FunctionDef | ast.AsyncFunctionDef] = []
        self.method_meta: dict[str, dict[str, object]] = {}
        self.class_fields: dict[str, list[tuple[str, str | None]]] = {}
        self.main_calls: set[str] = set()
        self.module_vars: set[str] = set()
        self.mutable_globals: set[str] = set()
        self.side_effects: list[str] = []
        for node in tree.body:
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                self.register_import(node)
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self.fn_names.add(node.name)
                self.functions.append(node)
            elif isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                val = getattr(node, "value", None)
                mutable = isinstance(val, (ast.List, ast.Dict, ast.Set, ast.ListComp,
                                           ast.DictComp, ast.SetComp, ast.Call))
                for t in targets:
                    for n in ast.walk(t):
                        if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store):
                            self.module_vars.add(n.id)
                            if mutable:
                                self.mutable_globals.add(n.id)
            elif isinstance(node, ast.ClassDef):
                # Record class annotated fields (for dataclass / namedtuple seed generation)
                fields: list[tuple[str, str | None]] = []
                ctor_params: list[str] = []
                for item in node.body:
                    if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                        fields.append((item.target.id, _unp(item.annotation)))
                    elif isinstance(item, ast.FunctionDef) and item.name == "__init__":
                        ctor_params = [a.arg for a in item.args.args[1:]]
                if fields:
                    self.class_fields[node.name] = fields
                # Extract callable methods as Class.method
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and not (
                        item.name.startswith("__") and item.name.endswith("__")
                    ):
                        decs = [ast.unparse(d) for d in item.decorator_list]
                        mkind = "instance"
                        if any(d == "staticmethod" or d.endswith(".staticmethod") for d in decs):
                            mkind = "static"
                        elif any(d == "classmethod" or d.endswith(".classmethod") for d in decs):
                            mkind = "classmethod"
                        elif any(d == "property" or d.endswith(".property") for d in decs):
                            mkind = "property"
                        qual_name = f"{node.name}.{item.name}"
                        self.fn_names.add(qual_name)
                        self.functions.append(item)
                        self.method_meta[id(item)] = {
                            "qual_name": qual_name,
                            "class_name": node.name,
                            "method_name": item.name,
                            "method_kind": mkind,
                            "ctor_params": ctor_params,
                        }
            elif isinstance(node, ast.If) and "__name__" in ast.unparse(node.test):
                for sub in ast.walk(node):
                    if isinstance(sub, ast.Call):
                        if isinstance(sub.func, ast.Name):
                            self.main_calls.add(sub.func.id)
                        elif isinstance(sub.func, ast.Attribute):
                            self.main_calls.add(sub.func.attr)
                continue
            elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
                continue
            else:
                self.side_effects.append(f"line {node.lineno}: {ast.unparse(node)[:80]}")

    def register_import(self, node):
        if isinstance(node, ast.Import):
            for a in node.names:
                self.aliases[a.asname or a.name.split(".")[0]] = a.name if a.asname else a.name.split(".")[0]
        else:
            mod = "." * node.level + (node.module or "")
            for a in node.names:
                self.aliases[a.asname or a.name] = f"{mod}.{a.name}"


class _FnVisitor(ast.NodeVisitor):
    def __init__(self, fn, ctx: _Ctx):
        self.fn, self.ctx = fn, ctx
        a = fn.args
        pos = a.posonlyargs + a.args
        allargs = pos + a.kwonlyargs + [x for x in (a.vararg, a.kwarg) if x]
        self.params = [x.arg for x in allargs]
        self.global_decl = {n for node in ast.walk(fn) if isinstance(node, ast.Global) for n in node.names}
        self.local_names = (self._locals(fn) | set(self.params)) - self.global_decl
        self.alias = {p: p for p in self.params}          # local name -> parameter it may alias
        self.types = {x.arg: k for x in allargs if x.annotation and (k := _ann_kind(x.annotation))}
        self.loop = 0
        self.loops = 0
        self.effects: list[Effect] = []
        self.patterns: list[Pattern] = []
        self.sorts: list[Pattern] = []
        self.unordered: list[Pattern] = []
        self.call_sites: list[CallSite] = []
        self.callees_local: set[str] = set()
        self.callees_ext: set[str] = set()
        self.mutated: set[str] = set()
        self.reads_globals: set[str] = set()
        self.raises: set[str] = set()
        self.handled: set[str] = set()
        self.implicit: set[str] = set()
        self.float_reasons: set[str] = set()
        self.hash_id = False
        self.is_gen = False
        self.ret_alias = False

    # ---------- helpers ----------
    @staticmethod
    def _locals(fn) -> set[str]:
        names = set()
        for n in ast.walk(fn):
            if isinstance(n, ast.Name) and isinstance(n.ctx, (ast.Store, ast.Del)):
                names.add(n.id)
            elif isinstance(n, ast.arg):
                names.add(n.arg)
            elif isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and n is not fn:
                names.add(n.name)
            elif isinstance(n, ast.ExceptHandler) and n.name:
                names.add(n.name)
        return names

    def _is_global(self, name) -> bool:
        return name is not None and name in self.ctx.module_vars and \
            (name not in self.local_names or name in self.global_decl)

    def _qual(self, node) -> str | None:
        parts = []
        while isinstance(node, ast.Attribute):
            parts.append(node.attr)
            node = node.value
        if not isinstance(node, ast.Name):
            return None
        if node.id in self.local_names:
            return None
        return ".".join([self.ctx.aliases.get(node.id, node.id)] + parts[::-1])

    def _effect(self, kind, node, detail, certainty="definite"):
        e = Effect(kind=kind, line=getattr(node, "lineno", 0), detail=detail, certainty=certainty)
        if e not in self.effects:
            self.effects.append(e)

    def _pat(self, bucket, kind, node, detail):
        p = Pattern(kind=kind, line=getattr(node, "lineno", 0), in_loop=self.loop > 0, detail=detail)
        if p not in bucket:
            bucket.append(p)

    def _write_through(self, root, node, detail):
        if root is None:
            return
        if root in self.alias:
            p = self.alias[root]
            self.mutated.add(p)
            self._effect(K.ARG_MUTATION, node, f"{detail} (parameter '{p}')")
        elif self._is_global(root):
            self._effect(K.GLOBAL_WRITE, node, f"{detail} (module-level '{root}')")

    def _kind(self, e) -> str | None:
        if isinstance(e, (ast.List, ast.ListComp)):
            return "list"
        if isinstance(e, ast.Tuple):
            return "tuple"
        if isinstance(e, (ast.Set, ast.SetComp)):
            return "set"
        if isinstance(e, (ast.Dict, ast.DictComp)):
            return "dict"
        if isinstance(e, (ast.JoinedStr,)) or (isinstance(e, ast.Constant) and isinstance(e.value, str)):
            return "str"
        if isinstance(e, ast.Name):
            return self.types.get(e.id)
        if isinstance(e, ast.Subscript) and isinstance(e.slice, ast.Slice):
            return self._kind(e.value)
        if isinstance(e, ast.BinOp) and isinstance(e.op, ast.Add):
            lk = self._kind(e.left)
            return lk if lk in ("str", "list", "tuple") else None
        if isinstance(e, ast.Call):
            if isinstance(e.func, ast.Name):
                return CTOR_KINDS.get(e.func.id)
            if isinstance(e.func, ast.Attribute):
                m = e.func.attr
                if m in ("split", "splitlines", "readlines"):
                    return "list"
                if m == "values":
                    return "dictvalues"
                if m == "keys":
                    return "dictkeys"
        return None

    def _check_unordered(self, expr, node, how):
        if self._kind(expr) == "set":
            self._pat(self.unordered, "unordered_iteration", node, how)

    def _sort(self, node, kind):
        key = any(k.arg == "key" for k in node.keywords)
        rev = any(k.arg == "reverse" for k in node.keywords)
        self._pat(self.sorts, kind, node, f"key={key}, reverse={rev}")
        if self.loop:
            self._pat(self.patterns, "sort_in_loop", node, f"{kind} inside a loop: O(k log k) per iteration")

    # ---------- statements ----------
    def _store(self, t, value):
        if isinstance(t, ast.Name):
            if t.id in self.global_decl:
                self._effect(K.GLOBAL_WRITE, t, f"rebinds module-level '{t.id}'")
                return
            new_alias = None
            if isinstance(value, (ast.Name, ast.Attribute, ast.Subscript)) and \
                    not (isinstance(value, ast.Subscript) and isinstance(value.slice, ast.Slice)):
                r = root_name(value)
                if r in self.alias:
                    new_alias = self.alias[r]
            self.alias.pop(t.id, None)
            self.types.pop(t.id, None)
            if new_alias:
                self.alias[t.id] = new_alias
            if value is not None and (k := self._kind(value)):
                self.types[t.id] = k
        elif isinstance(t, (ast.Tuple, ast.List)):
            for e in t.elts:
                self._store(e, None)
        elif isinstance(t, ast.Starred):
            self._store(t.value, None)
        else:
            self.visit(t)
            self._write_through(root_name(t), t, "item/attribute assignment")

    def visit_Assign(self, node):
        self.visit(node.value)
        t0 = node.targets[0]
        if self.loop and isinstance(node.value, ast.BinOp) and isinstance(node.value.op, ast.Add) \
                and isinstance(t0, ast.Name) and isinstance(node.value.left, ast.Name) \
                and node.value.left.id == t0.id and self.types.get(t0.id) in ("str", "list"):
            self._pat(self.patterns, f"{self.types[t0.id]}_rebuild_in_loop", node,
                      f"`{t0.id} = {t0.id} + ...` copies the whole {self.types[t0.id]} every iteration")
        for t in node.targets:
            self._store(t, node.value)

    def visit_AnnAssign(self, node):
        if node.value:
            self.visit(node.value)
        self._store(node.target, node.value)
        if isinstance(node.target, ast.Name) and (k := _ann_kind(node.annotation)):
            self.types[node.target.id] = k

    def visit_AugAssign(self, node):
        self.visit(node.value)
        t = node.target
        if isinstance(t, ast.Name):
            if t.id in self.global_decl:
                self._effect(K.GLOBAL_WRITE, node, f"augmented assignment to module-level '{t.id}'")
            elif t.id in self.alias:
                self._effect(K.ARG_MUTATION, node,
                             f"`{t.id} op= ...` mutates parameter '{self.alias[t.id]}' in place if it is a list/set/dict",
                             "possible")
            if self.loop and isinstance(node.op, ast.Add) and self.types.get(t.id) == "str":
                self._pat(self.patterns, "str_concat_in_loop", node,
                          f"`{t.id} += ...` on str inside a loop (quadratic copying in the worst case)")
        else:
            self.visit(t)
            self._write_through(root_name(t), node, "augmented item/attribute assignment")

    def visit_Delete(self, node):
        for t in node.targets:
            if isinstance(t, (ast.Subscript, ast.Attribute)):
                self.visit(t)
                self._write_through(root_name(t), t, "del on item/attribute")

    def visit_For(self, node):
        self.visit(node.iter)
        self._check_unordered(node.iter, node, "for-loop over a set (order depends on hashing)")
        r = root_name(node.iter) if isinstance(node.iter, (ast.Name, ast.Attribute, ast.Subscript)) else None
        elem_alias = self.alias.get(r) if r else None
        for n in ast.walk(node.target):
            if isinstance(n, ast.Name):
                self.alias.pop(n.id, None)
                self.types.pop(n.id, None)
                if elem_alias:
                    self.alias[n.id] = elem_alias
        self.loop += 1
        self.loops += 1
        for s in node.body + node.orelse:
            self.visit(s)
        self.loop -= 1

    visit_AsyncFor = visit_For

    def visit_While(self, node):
        self.loops += 1
        self.loop += 1
        self.visit(node.test)
        for s in node.body + node.orelse:
            self.visit(s)
        self.loop -= 1

    def _comp(self, node):
        n = len(node.generators)
        self.loops += n
        for g in node.generators:
            self._check_unordered(g.iter, g.iter, "comprehension over a set (order depends on hashing)")
        self.loop += n
        self.generic_visit(node)
        self.loop -= n

    visit_ListComp = visit_SetComp = visit_DictComp = visit_GeneratorExp = _comp

    def visit_Return(self, node):
        v = node.value
        if isinstance(v, (ast.Name, ast.Attribute, ast.Subscript)) and \
                not (isinstance(v, ast.Subscript) and isinstance(v.slice, ast.Slice)):
            if root_name(v) in self.alias:
                self.ret_alias = True
        self.generic_visit(node)

    def visit_Raise(self, node):
        e = node.exc
        if e is None:
            name = "<re-raise>"
        else:
            tgt = e.func if isinstance(e, ast.Call) else e
            name = self._qual(tgt) or ast.unparse(tgt)
        self.raises.add(name)
        self.generic_visit(node)

    def visit_Try(self, node):
        for h in node.handlers:
            self.handled.add("<bare>" if h.type is None else ast.unparse(h.type))
        self.generic_visit(node)

    def visit_Yield(self, node):
        self.is_gen = True
        self.generic_visit(node)

    visit_YieldFrom = visit_Yield

    def visit_Import(self, node):
        self.ctx.register_import(node)

    visit_ImportFrom = visit_Import

    # ---------- expressions ----------
    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load) and self._is_global(node.id):
            self.reads_globals.add(node.id)
            if node.id in self.ctx.mutable_globals:
                self._effect(K.GLOBAL_READ, node, f"reads mutable module-level '{node.id}'", "possible")

    def visit_Attribute(self, node):
        if self._qual(node) in ("os.environ", "sys.argv"):
            self._effect(K.ENV, node, f"reads {self._qual(node)}")
        self.generic_visit(node)

    def visit_Constant(self, node):
        if isinstance(node.value, float):
            self.float_reasons.add(f"float literal {node.value!r}")

    def visit_Subscript(self, node):
        if isinstance(node.slice, ast.Slice):
            if self.loop:
                self._pat(self.patterns, "slice_copy_in_loop", node, "slicing copies O(k) elements each iteration")
        else:
            self.implicit.add("IndexError/KeyError (subscript)")
        self.generic_visit(node)

    def visit_BinOp(self, node):
        if isinstance(node.op, (ast.Div, ast.FloorDiv, ast.Mod)):
            r = node.right
            if not (isinstance(r, ast.Constant) and isinstance(r.value, (int, float)) and r.value != 0):
                self.implicit.add("ZeroDivisionError")
            if isinstance(node.op, ast.Div):
                self.float_reasons.add("true division (/) yields float")
        self.generic_visit(node)

    def visit_Compare(self, node):
        for op, comp in zip(node.ops, node.comparators):
            if isinstance(op, (ast.In, ast.NotIn)):
                k = self._kind(comp)
                if k in ("list", "tuple", "str", "dictvalues"):
                    self._pat(self.patterns, "linear_membership", node,
                              f"`in` over a {k}: O(len) per test; a set/dict would be O(1)")
                elif k is None and self.loop:
                    self._pat(self.patterns, "unknown_membership", node,
                              "`in` on a value of unknown type inside a loop (O(n) if list/tuple/str)")
        self.generic_visit(node)

    def visit_Call(self, node):
        f = node.func
        fq = self._qual(f)
        if fq:
            if (kind := _effect_for(fq)) is not None:
                self._effect(kind, node, f"call to {fq}")
            if fq in ("hash", "id"):
                self.hash_id = True
            if fq in EXTERNAL_MUTATORS and len(node.args) > EXTERNAL_MUTATORS[fq]:
                self._write_through(root_name(node.args[EXTERNAL_MUTATORS[fq]]), node,
                                    f"{fq}() mutates its argument")
            if fq == "sorted":
                self._sort(node, "sorted")
            if fq.startswith(("math.", "numpy.", "statistics.")) or fq == "float":
                self.float_reasons.add(f"call to {fq}")
            if fq in ("int", "float"):
                self.implicit.add(f"ValueError (from {fq}())")
            if fq == "next":
                self.implicit.add("StopIteration (from next())")
            if node.args and fq in ("list", "tuple", "iter"):
                self._check_unordered(node.args[0], node, f"{fq}() over a set (order depends on hashing)")
            if self.loop and node.args and fq in ("list", "tuple", "dict", "set"):
                self._pat(self.patterns, "container_rebuild_in_loop", node,
                          f"{fq}(...) copies its argument every iteration")
            if self.loop and fq in ("min", "max", "sum") and len(node.args) == 1 \
                    and not isinstance(node.args[0], (ast.List, ast.Tuple, ast.Set)):
                self._pat(self.patterns, "linear_builtin_in_loop", node,
                          f"{fq}() over a collection inside a loop: O(n) per iteration")
            if self.loop and fq in ("copy.deepcopy", "copy.copy"):
                self._pat(self.patterns, "container_rebuild_in_loop", node, f"{fq} inside a loop")
        if isinstance(f, ast.Attribute):
            m, root, rk = f.attr, root_name(f.value), self._kind(f.value)
            if m in MUTATING_METHODS and rk not in ("str", "tuple", "range"):
                self._write_through(root, node, f".{m}() call")
            if m in ("pop", "insert") and node.args and isinstance(node.args[0], ast.Constant) \
                    and node.args[0].value == 0 and rk != "deque":
                self._pat(self.patterns, f"{m}_front", node,
                          f"list.{m}(0) shifts every element: O(n); use collections.deque")
            if m in ("remove", "index", "count") and rk in ("list", "tuple", "str"):
                self._pat(self.patterns, "linear_method", node, f".{m}() on a {rk} is O(n)")
            if m in ("remove", "index"):
                self.implicit.add(f"ValueError (from .{m}())")
            if m == "sort":
                self._sort(node, "list.sort")
            if m == "copy" and self.loop:
                self._pat(self.patterns, "container_rebuild_in_loop", node, ".copy() inside a loop")
            if m == "pop" and rk == "set":
                self._pat(self.unordered, "unordered_iteration", node, "set.pop() returns an arbitrary element")
            if m in IO_METHODS and not (fq and _effect_for(fq)):
                self._effect(K.FILE_IO, node, f".{m}() looks like stream I/O", "possible")
        if isinstance(f, ast.Name) and f.id in self.ctx.fn_names and f.id not in self.local_names:
            self.callees_local.add(f.id)
            roots = []
            for a in node.args:
                r = root_name(a) if isinstance(a, (ast.Name, ast.Attribute, ast.Subscript)) and \
                    not (isinstance(a, ast.Subscript) and isinstance(a.slice, ast.Slice)) else None
                roots.append(self.alias.get(r) if r in self.alias else
                             (f"@global:{r}" if self._is_global(r) else None))
            self.call_sites.append(CallSite(callee=f.id, line=node.lineno, arg_roots=roots))
        else:
            self.callees_ext.add(fq or ast.unparse(f)[:60])
        self.generic_visit(node)

    # ---------- result ----------
    def build(self) -> FunctionFacts:
        fn, a = self.fn, self.fn.args
        meta = self.ctx.method_meta.get(id(fn))
        qual_name = str(meta["qual_name"]) if meta else fn.name
        pos = a.posonlyargs + a.args
        defaults = [None] * (len(pos) - len(a.defaults)) + list(a.defaults)
        params = [ParamInfo(name=x.arg, annotation=_unp(x.annotation), default=_unp(d)) for x, d in zip(pos, defaults)]
        if meta and meta.get("method_kind") in ("instance", "classmethod", "property") and params:
            # Strip receiver (`self` / `cls`) from external call signature
            params = params[1:]
        if a.vararg:
            params.append(ParamInfo(name=a.vararg.arg, annotation=_unp(a.vararg.annotation), kind="vararg"))
        params += [ParamInfo(name=x.arg, annotation=_unp(x.annotation), default=_unp(d), kind="kwonly")
                   for x, d in zip(a.kwonlyargs, a.kw_defaults)]
        if a.kwarg:
            params.append(ParamInfo(name=a.kwarg.arg, annotation=_unp(a.kwarg.annotation), kind="kwarg"))
        extra: dict = {}
        if meta:
            extra.update({
                "class_name": meta["class_name"],
                "method_name": meta["method_name"],
                "method_kind": meta["method_kind"],
                "ctor_params": meta["ctor_params"],
            })
        if self.ctx.class_fields:
            extra["class_fields"] = self.ctx.class_fields
        short_name = str(meta["method_name"]) if meta else fn.name
        if fn.name in self.ctx.main_calls or short_name in self.ctx.main_calls or qual_name in self.ctx.main_calls:
            extra["called_in_main"] = True
        return FunctionFacts(
            name=qual_name, lineno=fn.lineno, end_lineno=fn.end_lineno or fn.lineno, params=params,
            returns_annotation=_unp(fn.returns), docstring=ast.get_docstring(fn),
            decorators=[ast.unparse(d) for d in fn.decorator_list],
            is_generator=self.is_gen, is_async=isinstance(fn, ast.AsyncFunctionDef),
            callees_local=sorted(self.callees_local), callees_external=sorted(self.callees_ext),
            call_sites=self.call_sites, effects=self.effects, mutated_params=sorted(self.mutated),
            reads_globals=sorted(self.reads_globals), raises=sorted(self.raises),
            handled_exceptions=sorted(self.handled), implicit_raises=sorted(self.implicit),
            loop_count=self.loops, max_loop_depth=_depth(fn, 0) if False else
            max([_depth(s, 0) for s in fn.body] or [0]),
            float_reasons=sorted(self.float_reasons), sort_uses=self.sorts,
            unordered_iterations=self.unordered, cost_patterns=self.patterns,
            uses_hash_or_id=self.hash_id, may_return_input_alias=self.ret_alias,
            extra=extra)


class AmbiguousEntry(Exception):
    def __init__(self, candidates):
        super().__init__(f"Several candidate entry points: {candidates}. Pass --entry.")
        self.candidates = candidates


def analyze_source(source: str) -> ModuleFacts:
    tree = ast.parse(source)
    ctx = _Ctx(tree)
    facts: dict[str, FunctionFacts] = {}
    mutated: dict[str, set[str]] = {}
    for fn in ctx.functions:
        v = _FnVisitor(fn, ctx)
        for s in fn.body:
            v.visit(s)
        built = v.build()
        facts[built.name] = built
        mutated[built.name] = set(v.mutated)

    # interprocedural: helper(param) that mutates its argument => caller mutates its own param
    changed = True
    while changed:
        changed = False
        for f in facts.values():
            for cs in f.call_sites:
                g = facts.get(cs.callee)
                if not g:
                    continue
                pos = [p.name for p in g.params if p.kind == "positional"]
                for i, root in enumerate(cs.arg_roots):
                    if root is None or i >= len(pos) or pos[i] not in mutated[g.name]:
                        continue
                    if root.startswith("@global:"):
                        eff = Effect(kind=K.GLOBAL_WRITE, line=cs.line,
                                     detail=f"passes module-level '{root[8:]}' to {g.name}(), which mutates it")
                    else:
                        if root in mutated[f.name]:
                            continue
                        mutated[f.name].add(root)
                        changed = True
                        eff = Effect(kind=K.ARG_MUTATION, line=cs.line,
                                     detail=f"{g.name}() mutates the argument passed from parameter '{root}'")
                    if eff not in f.effects:
                        f.effects.append(eff)

    # recursion
    def reach(start):
        seen, stack = set(), list(facts[start].callees_local)
        while stack:
            x = stack.pop()
            if x not in seen:
                seen.add(x)
                stack += facts[x].callees_local
        return seen

    for name, f in facts.items():
        f.mutated_params = sorted(mutated[name])
        f.is_recursive = name in f.callees_local
        f.in_recursive_cycle = name in reach(name)
        f.branching_self_calls = sum(1 for c in f.call_sites if c.callee == name)
        memo = any("cache" in d or "memo" in d for d in f.decorators)
        if f.branching_self_calls >= 2 and not memo:
            f.cost_patterns.append(Pattern(kind="branching_recursion_no_memo", line=f.lineno, in_loop=False,
                                           detail=f"{f.branching_self_calls} self-calls per frame, no memoization decorator: "
                                                  "possibly exponential if subproblems overlap"))

    # transitive effect kinds (ARG_MUTATION is per-parameter, so not propagated)
    kinds = {n: {e.kind for e in f.effects} for n, f in facts.items()}
    changed = True
    while changed:
        changed = False
        for n, f in facts.items():
            for c in f.callees_local:
                add = kinds[c] - {K.ARG_MUTATION} - kinds[n]
                if add:
                    kinds[n] |= add
                    changed = True
    called = {c for f in facts.values() for c in f.callees_local if c != f.name} if facts else set()
    for n, f in facts.items():
        f.transitive_effect_kinds = sorted(kinds[n], key=lambda k: k.value)

    return ModuleFacts(
        functions=facts, imports=dict(ctx.aliases), module_vars=sorted(ctx.module_vars),
        mutable_module_vars=sorted(ctx.mutable_globals), module_side_effects=ctx.side_effects,
        root_functions=[n for n in facts if n not in called])


def rank_entries(mod: ModuleFacts, source: str = "") -> list[dict]:
    """Deterministic heuristic entry ranker (Workstream B2)."""
    if not mod.functions:
        return []
    caller_counts: dict[str, int] = {n: 0 for n in mod.functions}
    for fn in mod.functions.values():
        for c in fn.callees_local:
            if c in caller_counts and c != fn.name:
                caller_counts[c] += 1

    classes = {f.extra.get("class_name") for f in mod.functions.values() if f.extra.get("class_name")}
    single_class = len(classes) == 1

    ranked: list[dict] = []
    for name, fn in mod.functions.items():
        score = 0
        signals: list[str] = []
        short = name.split(".")[-1]
        if fn.extra.get("called_in_main"):
            score += 100
            signals.append("called_in_main")
        if short.lower() in ("main", "solve", "solution", "run"):
            score += 40
            signals.append("preferred_name")
        if single_class and fn.extra.get("class_name"):
            score += 30
            signals.append("single_class_method")
        if caller_counts.get(name, 0) == 0:
            score += 20
            signals.append("root_function")
        else:
            score -= 10 * caller_counts[name]
        if fn.loop_count > 0:
            score += min(25, 5 * fn.loop_count)
            signals.append(f"loops={fn.loop_count}")
        if fn.is_recursive:
            score += 10
            signals.append("recursive")
        if fn.docstring:
            score += 5
            signals.append("has_docstring")
        if not short.startswith("_"):
            score += 5
        ranked.append({"name": name, "score": score, "signals": signals})

    ranked.sort(key=lambda r: (-r["score"], r["name"]))
    return ranked


def select_entry(mod: ModuleFacts, requested: str | None, *, auto_select: bool = False) -> str:
    if requested:
        if requested in mod.functions:
            return requested
        # Allow bare method name if unique
        matches = [k for k in mod.functions if k.endswith(f".{requested}")]
        if len(matches) == 1:
            return matches[0]
        raise ValueError(f"'{requested}' not found. Functions: {list(mod.functions)}")
    if len(mod.functions) == 1:
        return next(iter(mod.functions))
    pref = [n for n in mod.root_functions if n.split(".")[-1].lower() in ("main", "solve", "solution", "run")]
    if len(pref) == 1:
        return pref[0]
    if len(mod.root_functions) == 1:
        return mod.root_functions[0]
    ranked = rank_entries(mod)
    if ranked:
        # Auto-pick if there is a clear non-tied winner (e.g. called in __main__ or strictly higher score)
        if auto_select or (len(ranked) >= 2 and ranked[0]["score"] > ranked[1]["score"] + 15):
            return ranked[0]["name"]
    raise AmbiguousEntry(mod.root_functions)