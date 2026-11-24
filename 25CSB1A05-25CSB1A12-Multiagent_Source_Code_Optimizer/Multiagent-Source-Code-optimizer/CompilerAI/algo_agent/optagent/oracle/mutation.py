from __future__ import annotations
import ast
import copy
import random
import tempfile
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from ..config import Settings
from ..runtime.sandbox import RunOpts, Sandbox
from .compare import Comparator
from .golden import make_golden
from .mutators import MutCtx, mutate_args
from .schemas import Case, GoldenRecord, MutantInfo, MutationReport, split_of

CMP = {ast.Lt: [ast.LtE, ast.GtE], ast.LtE: [ast.Lt, ast.Gt], ast.Gt: [ast.GtE, ast.LtE],
       ast.GtE: [ast.Gt, ast.Lt], ast.Eq: [ast.NotEq], ast.NotEq: [ast.Eq], ast.In: [ast.NotIn],
       ast.NotIn: [ast.In], ast.Is: [ast.IsNot], ast.IsNot: [ast.Is]}
BIN = {ast.Add: [ast.Sub], ast.Sub: [ast.Add], ast.Mult: [ast.Add, ast.FloorDiv],
       ast.FloorDiv: [ast.Mult], ast.Div: [ast.Mult], ast.Mod: [ast.Mult], ast.Pow: [ast.Mult]}
SYM = {ast.Add: "+", ast.Sub: "-", ast.Mult: "*", ast.FloorDiv: "//", ast.Div: "/", ast.Mod: "%",
       ast.Pow: "**", ast.Lt: "<", ast.LtE: "<=", ast.Gt: ">", ast.GtE: ">=", ast.Eq: "==",
       ast.NotEq: "!=", ast.In: "in", ast.NotIn: "not in", ast.Is: "is", ast.IsNot: "is not"}
CALL_SWAP = {"min": "max", "max": "min", "any": "all", "all": "any"}
METH_SWAP = {"startswith": "endswith", "endswith": "startswith", "lower": "upper", "upper": "lower",
             "lstrip": "rstrip", "rstrip": "lstrip"}


def _name(n): return ast.Name(id=n, ctx=ast.Load())
def _const(v): return ast.Constant(value=v)
def _not(e): return ast.UnaryOp(op=ast.Not(), operand=e)
def _pass(node): return ast.copy_location(ast.Pass(), node)


def _call_alts(node: ast.Call):
    f = node.func
    if isinstance(f, ast.Name):
        if f.id == "range" and node.args:
            for i, a in enumerate(node.args):
                for opn, sym in ((ast.Add, "+"), (ast.Sub, "-")):
                    n = copy.copy(node)
                    n.args = list(node.args)
                    n.args[i] = ast.BinOp(left=a, op=opn(), right=_const(1))
                    yield "range-bound", f"range arg {i} {sym} 1", n
        if f.id in CALL_SWAP:
            n = copy.copy(node)
            n.func = _name(CALL_SWAP[f.id])
            yield "call-swap", f"{f.id} → {CALL_SWAP[f.id]}", n
        if f.id == "sorted" and node.args:
            yield "drop-sort", "sorted(x) → list(x)", ast.Call(func=_name("list"), args=[node.args[0]], keywords=[])
        if f.id in ("list", "tuple", "set", "dict") and len(node.args) == 1 and not node.keywords:
            yield "alias", f"{f.id}(x) → x (copy removed)", node.args[0]
    if isinstance(f, ast.Attribute):
        if f.attr == "copy" and not node.args:
            yield "alias", ".copy() removed (aliasing)", f.value
        if f.attr in METH_SWAP:
            n = copy.copy(node)
            n.func = ast.Attribute(value=f.value, attr=METH_SWAP[f.attr], ctx=ast.Load())
            yield "method-swap", f".{f.attr} → .{METH_SWAP[f.attr]}", n
        if f.attr == "pop":
            if not node.args:
                n = copy.copy(node)
                n.args = [_const(0)]
                yield "pop-end", ".pop() → .pop(0)", n
            elif isinstance(node.args[0], ast.Constant) and node.args[0].value == 0:
                n = copy.copy(node)
                n.args = []
                yield "pop-end", ".pop(0) → .pop()", n
    for i, kw in enumerate(node.keywords):
        if kw.arg == "key":
            n = copy.copy(node)
            n.keywords = node.keywords[:i] + node.keywords[i + 1:]
            yield "drop-key", "key= removed (ordering/stability)", n
        if kw.arg == "reverse" and isinstance(kw.value, ast.Constant) and isinstance(kw.value.value, bool):
            n = copy.copy(node)
            n.keywords = list(node.keywords)
            n.keywords[i] = ast.keyword(arg="reverse", value=_const(not kw.value.value))
            yield "flip-reverse", "reverse flag flipped", n


def _sub_alts(node: ast.Subscript):
    s = node.slice
    if isinstance(s, ast.Slice):
        if s.lower is None and s.upper is None and s.step is None:
            yield "alias", "x[:] → x (copy removed)", node.value
        for part in ("lower", "upper"):
            e = getattr(s, part)
            if e is None:
                continue
            for opn, sym in ((ast.Add, "+"), (ast.Sub, "-")):
                n, s2 = copy.copy(node), copy.copy(s)
                setattr(s2, part, ast.BinOp(left=e, op=opn(), right=_const(1)))
                n.slice = s2
                yield "slice-bound", f"slice {part} {sym} 1", n
    elif isinstance(s, ast.Constant) and type(s.value) is int and s.value in (0, -1):
        n = copy.copy(node)
        n.slice = _const(-1 if s.value == 0 else 0)
        yield "index", f"[{s.value}] → [{-1 if s.value == 0 else 0}]", n
    elif isinstance(s, (ast.Name, ast.BinOp)):
        for opn, sym in ((ast.Add, "+"), (ast.Sub, "-")):
            n = copy.copy(node)
            n.slice = ast.BinOp(left=s, op=opn(), right=_const(1))
            yield "index", f"index {sym} 1", n


def alts(node):
    T = type(node)
    if T is ast.BinOp:
        for t in BIN.get(type(node.op), ()):
            n = copy.copy(node)
            n.op = t()
            yield "arith", f"{SYM[type(node.op)]} → {SYM[t]}", n
    elif T is ast.Compare:
        for i, o in enumerate(node.ops):
            for t in CMP.get(type(o), ()):
                n = copy.copy(node)
                n.ops = node.ops[:i] + [t()] + node.ops[i + 1:]
                yield "compare", f"{SYM[type(o)]} → {SYM[t]}", n
    elif T is ast.BoolOp:
        n = copy.copy(node)
        n.op = ast.Or() if isinstance(node.op, ast.And) else ast.And()
        yield "boolop", "and ↔ or", n
    elif T is ast.UnaryOp and isinstance(node.op, ast.Not):
        yield "not-removal", "`not` removed", node.operand
    elif T is ast.Constant:
        v = node.value
        if isinstance(v, bool):
            yield "const", f"{v} → {not v}", _const(not v)
        elif isinstance(v, int):
            for nv in (v + 1, v - 1):
                yield "const", f"{v} → {nv}", _const(nv)
            if v != 0:
                yield "const", f"{v} → 0", _const(0)
        elif isinstance(v, float):
            yield "const", f"{v} → {v + 1.0}", _const(v + 1.0)
        elif isinstance(v, str):
            yield "const", "string literal changed", _const(v + "x")
    elif T in (ast.If, ast.While, ast.IfExp):
        n = copy.copy(node)
        n.test = _not(node.test)
        yield "negate-cond", "condition negated", n
    elif T is ast.comprehension:
        for i in range(len(node.ifs)):
            n = copy.copy(node)
            n.ifs = list(node.ifs)
            n.ifs[i] = _not(node.ifs[i])
            yield "negate-cond", "comprehension filter negated", n
    elif T is ast.Return and node.value is not None and not (
            isinstance(node.value, ast.Constant) and node.value.value is None):
        yield "return-none", "return value → None", ast.copy_location(ast.Return(value=_const(None)), node)
    elif T is ast.AugAssign:
        if type(node.op) in (ast.Add, ast.Sub):
            n = copy.copy(node)
            n.op = ast.Sub() if isinstance(node.op, ast.Add) else ast.Add()
            yield "arith", "augmented op flipped", n
        yield "stmt-delete", "statement deleted", _pass(node)
    elif T in (ast.Assign, ast.AnnAssign, ast.Delete):
        yield "stmt-delete", "statement deleted", _pass(node)
    elif T is ast.Expr and isinstance(node.value, ast.Call):
        yield "stmt-delete", "call statement deleted", _pass(node)
    elif T is ast.Break:
        yield "loop-ctl", "break → continue", ast.copy_location(ast.Continue(), node)
    elif T is ast.Continue:
        yield "loop-ctl", "continue → break", ast.copy_location(ast.Break(), node)
    elif T is ast.Call:
        yield from _call_alts(node)
    elif T is ast.Subscript:
        yield from _sub_alts(node)


class _Mutator(ast.NodeTransformer):
    """target=-1 enumerates sites; target=k applies exactly the k-th alternative."""

    def __init__(self, target: int, reachable: set[str]):
        self.target, self.n, self.reachable, self.depth = target, -1, reachable, 0
        self.infos: list[tuple[int, str, str, int]] = []

    def visit_FunctionDef(self, node):
        if self.depth == 0 and node.name not in self.reachable:
            return node
        self.depth += 1
        node.body = [self.visit(s) for s in node.body]
        self.depth -= 1
        return node

    def visit_AsyncFunctionDef(self, node):
        return node

    def visit(self, node):
        if self.depth == 0 and not isinstance(node, (ast.Module, ast.FunctionDef)):
            return node
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
            return node                                   # docstrings
        for op, desc, new in alts(node):
            self.n += 1
            self.infos.append((self.n, op, desc, getattr(node, "lineno", 0)))
            if self.n == self.target:
                return new
        return super().visit(node)


def _stratified(infos, k: int, rng: random.Random):
    groups = defaultdict(list)
    for i in infos:
        groups[i[1]].append(i)
    for g in groups.values():
        rng.shuffle(g)
    out = []
    while len(out) < k and any(groups.values()):
        for g in list(groups.values()):
            if g and len(out) < k:
                out.append(g.pop())
    return out


class MutationTester:
    def __init__(self, sb: Sandbox, s: Settings, comparator: Comparator, log=print):
        self.sb, self.s, self.cmp, self.log = sb, s, comparator, log
        self.kill_score: Counter = Counter()
        self.mutants: dict[int, dict] = {}

    def generate(self, source: str, reachable: set[str], rng: random.Random) -> list[dict]:
        tree = ast.parse(source)
        enum = _Mutator(-1, reachable)
        enum.visit(copy.deepcopy(tree))
        chosen = _stratified(enum.infos, self.s.max_mutants, rng)
        base = ast.unparse(tree)
        seen, out = {base}, []
        for idx, op, desc, line in chosen:
            t2 = copy.deepcopy(tree)
            new = _Mutator(idx, reachable).visit(t2)
            ast.fix_missing_locations(new)
            try:
                msrc = ast.unparse(new)
                compile(msrc, "<mutant>", "exec")
            except Exception:
                continue
            if msrc in seen:
                continue
            seen.add(msrc)
            out.append({"id": len(out), "op": op, "desc": desc, "line": line, "source": msrc})
        return out

    def _plan(self, vis: list[Case], hold: list[Case]):
        plan = []
        vis = sorted(vis, key=lambda c: (-self.kill_score[c.id], c.size))
        for lst, isv in ((vis, True), (hold, False)):
            i, step = 0, 16
            while i < len(lst):
                plan.append((lst[i:i + step], isv))
                i += step
                step *= 4
        return plan

    def run(self, entry: str, source: str, reachable: set[str], cases: list[Case],
            golden: dict[str, GoldenRecord], covered_lines: set[int], props_path: str | None,
            rng: random.Random) -> MutationReport:
        s = self.s
        muts = self.generate(source, reachable, rng)
        self.log(f"  mutation testing: {len(muts)} mutants over {len(cases)} cases")
        vis = [c for c in cases if split_of(c, s.holdout_pct) == "visible"]
        hold = [c for c in cases if split_of(c, s.holdout_pct) == "holdout"]
        opts = RunOpts(timeout=s.mutant_case_timeout_s, props_path=props_path)
        tmp = tempfile.TemporaryDirectory(prefix="optagent_mut_")
        self._tmp = tmp

        ext = getattr(self, "_ext", ".py")

        def test(m: dict) -> MutantInfo:
            path = Path(tmp.name) / f"mutant_{m['id']}{ext}"
            path.write_text(m["source"], encoding="utf-8")
            info = MutantInfo(id=m["id"], line=m["line"], op=m["op"], desc=m["desc"], status="survived",
                              line_covered=m["line"] in covered_lines)
            first = True
            for chunk, isv in self._plan(vis, hold):
                res = self.sb.run_batch(path, entry, chunk, opts)
                if first and res and res[0].status == "load_error":
                    info.status = "invalid"
                    return info
                first = False
                for c, r in zip(chunk, res):
                    errs = [v for v in self.cmp.compare(c, golden[c.id], r) if v.severity == "error"]
                    if errs:
                        info.status, info.killed_by, info.aspect, info.by_visible = "killed", c.id, errs[0].aspect, isv
                        self.kill_score[c.id] += 1
                        return info
            return info

        with ThreadPoolExecutor(self.s.workers) as ex:
            infos = list(ex.map(test, muts))
        for m in muts:
            self.mutants[m["id"]] = m
        return self.summarize(infos)

    @staticmethod
    def summarize(infos: list[MutantInfo]) -> MutationReport:
        valid = [i for i in infos if i.status != "invalid"]
        killed = [i for i in valid if i.status == "killed"]
        surv = [i for i in valid if i.status == "survived"]
        rep = MutationReport(
            total=len(valid), killed=len(killed), survived=len(surv), invalid=len(infos) - len(valid),
            score=round(len(killed) / len(valid), 3) if valid else 0.0,
            score_visible_only=round(sum(i.by_visible for i in killed) / len(valid), 3) if valid else 0.0,
            survivors_on_covered_lines=sum(i.line_covered for i in surv),
            survivors_on_uncovered_lines=sum(not i.line_covered for i in surv),
            mutants=infos)
        pk: Counter = Counter()
        for i in killed:
            if i.aspect and i.aspect.startswith("property:"):
                pk[i.aspect] += 1
        rep.prop_kills = dict(pk)
        return rep


class SurvivorHunter:
    """For each surviving mutant, search for an input that tells it apart from the original."""

    def __init__(self, sb: Sandbox, s: Settings, comparator: Comparator, ctx: MutCtx, src, entry: str,
                 props_path: str | None, rng: random.Random, log=print):
        self.sb, self.s, self.cmp, self.ctx = sb, s, comparator, ctx
        self.src, self.entry, self.props, self.rng, self.log = src, entry, props_path, rng, log

    def _differential(self, mpath: Path, kids: list[Case]):
        orig = self.sb.run(self.src, self.entry, kids, RunOpts(props_path=self.props))
        mut = self.sb.run(mpath, self.entry, kids, RunOpts(timeout=self.s.mutant_case_timeout_s,
                                                           props_path=self.props))
        for c, ro, rm in zip(kids, orig, mut):
            if ro.status not in ("ok", "exception"):
                continue
            quick = GoldenRecord(case_id=c.id, result=ro)
            if not any(v.severity == "error" for v in self.cmp.compare(c, quick, rm)):
                continue
            g, _, lines = make_golden(self.sb, self.src, self.entry, [c], props_path=self.props)
            if c.id not in g:
                continue
            rm2 = self.sb.run_batch(mpath, self.entry, [c], RunOpts(timeout=self.s.mutant_case_timeout_s,
                                                                    props_path=self.props))[0]
            if any(v.severity == "error" for v in self.cmp.compare(c, g[c.id], rm2)):
                return c, g[c.id], lines.get(c.id, set())
        return None

    def hunt(self, m: dict, mpath: Path, parents: list[Case], extra: list[Case] | None = None):
        if extra:
            hit = self._differential(mpath, extra)
            if hit:
                return hit
        rng, done = self.rng, 0
        while done < self.s.hunt_inputs_per_survivor:
            kids = []
            for _ in range(128):
                a, k = rng.choice(parents).py()
                a2, k2 = mutate_args(a, k, rng, self.ctx)
                c = Case.make(a2, k2, "mutant_killer", f"hunt:{m['op']}")
                if c.size <= 30000:
                    kids.append(c)
            hit = self._differential(mpath, kids)
            if hit:
                return hit
            done += len(kids)
        return None