"""
Language-neutral taint analysis over the IR
============================================
A forward may-analysis on each function's CFG (worklist to a fixed point):

  State      variable → {origin → TaintInfo(contexts, trust, trace, uncertainty)}
  sources    ``specs.Source`` matched on calls, attribute chains (C# ``Request.Query``)
             and entry-point parameters (Spring / ASP.NET binding annotations,
             Rust extractor types, C ``main``'s ``argv``, COBOL LINKAGE items)
  transfer   assignments, operators, string building, field / element reads and
             stores, C output parameters (``fgets(buf, …)``), copy functions
             (``strcpy(dst, src)``), builder / mutator methods (``sb.append(x)``)
  sanitizers remove only the contexts they protect (``Integer.parseInt`` removes
             every injection context but keeps ``size`` / ``index``)
  refinement on branch edges: bounds checks (``n < sizeof buf``, ``strlen(s) < N``)
             clear size / index / buffer; ``x == "lit"`` / ``x.equals("lit")``
             clears everything; ``x.matches("[a-z]+")`` clears the contexts whose
             dangerous characters the pattern excludes
  calls      functions of the same file get summaries (parameter → return,
             parameter → sink), re-computed until no summary changes

Results are ``Hit`` records, turned into ``security.findings.Finding`` objects
by ``analyzer.py``.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field, replace
from typing import Dict, FrozenSet, List, Optional, Set, Tuple

from ..analysis.cfg_builder import build_cfg
from ..ir.ir_nodes import IRInstruction, IROpcode
from ..ir.lowering import contexts_cleared_by_charset, regex_allowed_chars
from .lower import FunctionInfo, LoweredModule
from .specs import ALL, MEMORY, LanguageSpec, Sink, Source

Step = Tuple[int, str, str, str]          # line, kind, text, function


@dataclass(frozen=True)
class TaintInfo:
    contexts: FrozenSet[str]
    description: str
    trust: str
    origin_line: int
    origin_function: str
    trace: Tuple[Step, ...] = ()
    unc: FrozenSet[str] = frozenset()
    symbolic: bool = False                # a parameter of an analysed function (not a real source)


Value = Dict[tuple, TaintInfo]
State = Dict[str, Value]


@dataclass
class Hit:
    rule_id: str
    function: str
    line: int
    col: int
    sink_name: str
    operation: str
    role: str
    info: TaintInfo
    resolution: str                     # exact | method-name
    context: str
    sink_uid: int = 0
    via: Tuple[str, ...] = ()

    def key(self):
        return (self.rule_id, self.function, self.sink_uid, self.role, self.info.description, self.info.origin_line)


def join(*vals: Value) -> Value:
    out: Value = {}
    for v in vals:
        for k, i in v.items():
            o = out.get(k)
            if o is None:
                out[k] = i
            elif o is i or (i.contexts <= o.contexts and i.unc <= o.unc and len(o.trace) <= len(i.trace)):
                continue                      # merging would not change o
            else:
                out[k] = replace(o, contexts=o.contexts | i.contexts, unc=o.unc | i.unc,
                                 trace=o.trace if len(o.trace) <= len(i.trace) else i.trace)
    return out


def _merge_into(st: "State", edge: "State") -> None:
    """st ⊔= edge, sharing unchanged values (the values are never mutated in place)."""
    for k, v in edge.items():
        cur = st.get(k)
        if cur is None:
            st[k] = v
        elif cur is not v:
            st[k] = join(cur, v)


def remove(v: Value, ctxs: FrozenSet[str]) -> Value:
    out = {}
    for k, i in v.items():
        left = i.contexts - ctxs
        if left:
            out[k] = replace(i, contexts=left)
    return out


def add_step(v: Value, step: Step) -> Value:
    return {k: replace(i, trace=i.trace + (step,)) if len(i.trace) < 24 else i for k, i in v.items()}


def _strip(p: str) -> Tuple[str, Optional[int]]:
    if "#" in p and p.rsplit("#", 1)[1].isdigit():
        a, b = p.rsplit("#", 1)
        return a, int(b)
    return p, None


def match_call(patterns, ins: IRInstruction) -> Optional[Tuple[str, Optional[int]]]:
    """('exact'|'method-name', format-arg index) when the call matches one of ``patterns``."""
    c = ins.call
    names = {c.callee, ins.meta.get("chain", "")}
    names.discard("")
    for raw in patterns:
        p, n = _strip(raw)
        if p.startswith("*."):
            suf = p[1:]
            if c.method and (c.callee.endswith(suf) or ins.meta.get("chain", "").endswith(suf)):
                return "method-name", n
            continue
        for nm in names:
            if nm == p or nm.endswith("." + p) or nm.replace("std.", "") == p:
                return "exact", n
    return None


SHELLS = {"sh", "bash", "zsh", "dash", "ksh", "cmd", "cmd.exe", "powershell", "pwsh", "/bin/sh", "/bin/bash",
          "/usr/bin/env"}
PROPAGATORS = {"toString", "format", "concat", "trim", "strip", "substring", "toLowerCase", "toUpperCase",
               "replace", "valueOf", "join", "split", "getBytes", "toCharArray", "String.format", "String.join",
               "ToString", "Trim", "Substring", "ToLower", "ToUpper", "Replace", "Format", "Concat", "Join",
               "Split", "to_string", "to_owned", "clone", "as_str", "to_lowercase", "to_uppercase", "trim_end",
               "trim_start", "into", "unwrap", "expect", "unwrap_or", "unwrap_or_default", "as_ref", "borrow",
               "iter", "collect", "map", "get", "getFirst", "getValue", "Value", "First", "FirstOrDefault",
               "c_str", "data", "str", "substr", "strdup", "format!", "concat!", "String.from", "build",
               "getParameterValues", "next", "decode", "Decode", "readAllBytes", "readLine", "lines",
               "nextToken", "toURI", "toURL", "resolve", "Combine", "GetFullPath", "Path.Combine", "join_path",
               "body", "uri", "as_bytes", "bytes", "chars", "to_vec", "ToArray", "ToList", "trim_matches",
               "Encoding.UTF8.GetString", "GetString", "new String", "new StringBuilder", "StringBuilder.toString",
               "Url", "Uri", "new Uri", "Paths.get", "getPath", "getName", "getAbsolutePath", "normalize"}


class FunctionAnalysis:
    def __init__(self, engine: "TaintEngine", info: FunctionInfo):
        self.e, self.info, self.fn = engine, info, info.fn
        self.q = info.fn.qualname
        self.defs: Dict[str, IRInstruction] = {}
        for i in self.fn.all_instructions():
            if i.result:
                self.defs.setdefault(i.result, i)
        self.lines = engine.lines
        self.ret: Value = {}
        self.hits: List[Hit] = []

    # ── helpers ─────────────────────────────────────────────────────────
    def step(self, ins: IRInstruction, kind: str, txt: str = "") -> Step:
        code = self.lines[ins.lineno - 1].strip() if 0 < ins.lineno <= len(self.lines) else ""
        return (ins.lineno, kind, txt or code[:140], self.q)

    def const_of(self, op: str) -> Optional[str]:
        d = self.defs.get(op)
        if d is not None and d.op == IROpcode.ASSIGN and "const" in d.meta:
            return d.meta["const"]
        return None

    def literal_prefix(self, op: str, depth: int = 0) -> str:
        if depth > 6:
            return ""
        c = self.const_of(op)
        if c is not None:
            return c
        d = self.defs.get(op)
        if d is None:
            return ""
        if d.op in (IROpcode.BINOP,) and d.meta.get("operator") == "+" and d.operands:
            return self.literal_prefix(d.operands[0], depth + 1)
        if d.op == IROpcode.BUILD and d.meta.get("kind") == "fstring" and d.operands:
            return self.literal_prefix(d.operands[0], depth + 1)
        if d.op == IROpcode.ASSIGN and len(d.operands) == 1:
            return self.literal_prefix(d.operands[0], depth + 1)
        if d.op == IROpcode.CALL and d.call and d.call.callee in ("format!", "String.format", "string.Format") \
                and d.call.args:
            return self.literal_prefix(d.call.args[0], depth + 1).split("{", 1)[0].split("%", 1)[0]
        if d.op == IROpcode.CALL and d.call and d.call.callee.startswith("new ") and d.call.args:
            return self.literal_prefix(d.call.args[0], depth + 1)
        return ""

    @staticmethod
    def fixed_destination(prefix: str) -> bool:
        if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*://[^/?#{}%@\\]+[/?#]", prefix):
            return True
        return len(prefix) >= 2 and prefix[0] == "/" and prefix[1] not in "/\\"

    def receiver_root_call(self, op: Optional[str], depth: int = 0) -> Optional[IRInstruction]:
        d = self.defs.get(op) if op else None
        while d is not None and depth < 12 and d.op == IROpcode.CALL and d.call and d.call.receiver:
            if d.call.callee.endswith("Command.new") or d.meta.get("chain", "").endswith("Command.new"):
                return d
            d = self.defs.get(d.call.receiver)
            depth += 1
        if d is not None and d.op == IROpcode.ASSIGN and d.operands:
            return self.receiver_root_call(d.operands[0], depth + 1)
        if d is not None and d.op == IROpcode.CALL and (d.call.callee.endswith("Command.new")
                                                        or d.meta.get("chain", "").endswith("Command.new")):
            return d
        return None

    def declares_html(self, op: Optional[str], depth: int = 0) -> bool:
        """A response builder chain that set ``content_type("text/html…")`` (actix / axum style)."""
        d = self.defs.get(op) if op else None
        while d is not None and depth < 12:
            if d.op == IROpcode.CALL and d.call:
                if d.call.method in ("content_type", "insert_header", "append_header") and \
                        "html" in " ".join(d.call.const_kwargs.values()).lower():
                    return True
                d = self.defs.get(d.call.receiver) if d.call.receiver else None
            elif d.op == IROpcode.ASSIGN and d.operands:
                d = self.defs.get(d.operands[0])
            else:
                return False
            depth += 1
        return False

    def get(self, state: State, op: Optional[str]) -> Value:
        if not op:
            return {}
        return state.get(op, {})

    # ── sources ─────────────────────────────────────────────────────────
    def source_value(self, src: Source, ins: IRInstruction, contexts=ALL) -> Value:
        key = ("src", src.description, ins.lineno, ins.uid)
        return {key: TaintInfo(frozenset(contexts), src.description, src.trust, ins.lineno, self.q,
                               (self.step(ins, "source", f"untrusted {src.description}: "
                                          + (self.lines[ins.lineno - 1].strip()[:120]
                                             if 0 < ins.lineno <= len(self.lines) else "")),))}

    def param_sources(self) -> Dict[str, Value]:
        out: Dict[str, Value] = {}
        spec, info = self.e.spec, self.info
        entry = self.fn.blocks[0].instructions[0] if self.fn.blocks else None
        for p in self.fn.params:
            ptype = info.param_types.get(p, "")
            decl = info.param_types.get(p + "#decl", "")
            for s in spec.sources:
                hit = False
                if s.kind == "param_annotation" and any(a in decl for a in s.patterns):
                    hit = True
                elif s.kind == "param_type":
                    if "main#argv" in s.patterns and self.fn.name == "main" and p in ("argv", "args", "envp"):
                        hit = True
                    elif "LINKAGE" in s.patterns and info.param_types.get(p + "#linkage"):
                        hit = True
                    elif ptype and ptype in s.patterns:
                        hit = True
                if hit and entry is not None:
                    key = ("param-src", s.description, p, self.q)
                    out[p] = {key: TaintInfo(ALL, f"{s.description} '{p}'", s.trust, self.fn.source_lineno, self.q,
                                             ((self.fn.source_lineno, "source",
                                               f"untrusted {s.description}: parameter '{p}'", self.q),))}
                    break
        # ASP.NET: public action methods of a controller receive request-bound simple parameters
        if self.e.language == "csharp" and (self.fn.class_name or "").endswith("Controller") \
                and "public" in info.modifiers and not out:
            for p in self.fn.params:
                ptype = info.param_types.get(p, "")
                if ptype in ("string", "String", "int", "long", "Guid", "object") or ptype.endswith("Dto") \
                        or ptype.endswith("Model") or ptype.endswith("Request"):
                    key = ("param-src", "controller action parameter", p, self.q)
                    out[p] = {key: TaintInfo(ALL, f"HTTP parameter '{p}' (ASP.NET controller action)", "remote",
                                             self.fn.source_lineno, self.q,
                                             ((self.fn.source_lineno, "source",
                                               f"untrusted HTTP parameter '{p}' bound by the controller action",
                                               self.q),),
                                             frozenset({"parameter assumed to be bound from the request "
                                                        "(public controller action)"}))}
        return out

    # ── analysis ────────────────────────────────────────────────────────
    def run(self, record: bool) -> None:
        cfg = build_cfg(self.fn)
        order = [b.label for b in self.fn.blocks]
        init: State = {}
        srcs = self.param_sources()
        for i, p in enumerate(self.fn.params):
            if p in srcs:
                init["param:" + p] = srcs[p]
            else:
                init["param:" + p] = {("param", self.q, i): TaintInfo(
                    ALL, f"parameter '{p}'", "unknown", self.fn.source_lineno, self.q,
                    ((self.fn.source_lineno, "param", f"parameter '{p}'", self.q),), symbolic=True)}
        out: Dict[str, State] = {}
        import heapq
        pos = {lbl: k for k, lbl in enumerate(order)}      # visit blocks in program order
        work = list(range(len(order)))
        queued = set(order)
        it = 0
        while work and it < 40 * max(1, len(order)):
            it += 1
            lbl = order[heapq.heappop(work)]
            queued.discard(lbl)
            node = cfg.nodes.get(lbl)
            if node is None:
                continue
            if lbl == order[0]:
                st = dict(init)
            else:
                st = {}
                for p in node.predecessors:
                    if p in out:
                        _merge_into(st, self.edge_state(p, lbl, out[p]))
            new = self.transfer_block(node.instructions, st, record=False)
            if out.get(lbl) != new:
                out[lbl] = new
                for s in node.successors:
                    if s not in queued and s in pos:
                        heapq.heappush(work, pos[s])
                        queued.add(s)
        if record:
            for lbl in order:
                node = cfg.nodes.get(lbl)
                if node is None:
                    continue
                st = dict(init) if lbl == order[0] else {}
                if lbl != order[0]:
                    for p in node.predecessors:
                        if p in out:
                            _merge_into(st, self.edge_state(p, lbl, out[p]))
                self.transfer_block(node.instructions, st, record=True)
        else:
            for lbl in order:
                if lbl in out:
                    pass

    def edge_state(self, pred: str, succ: str, st: State) -> State:
        b = self.fn.get_block(pred)
        term = next((i for i in reversed(b.instructions) if i.op == IROpcode.BRANCH), None) if b else None
        if term is None or term.meta.get("kind") != "if" or len(term.operands) < 3:
            return st
        on_true = succ == term.operands[1]
        if succ not in (term.operands[1], term.operands[2]):
            return st
        new = dict(st)
        self._refine(term.operands[0], on_true, new, 0)
        return new

    def _refine(self, cond: str, holds_in: bool, new: State, depth: int) -> None:
        """Apply the validation facts of ``cond`` being ``holds_in`` (recursing into ! / && / ||)."""
        negate = False
        d = self.defs.get(cond)
        while d is not None and d.op == IROpcode.UNOP and d.meta.get("operator") == "!":
            negate = not negate
            d = self.defs.get(d.operands[0])
        while d is not None and d.op == IROpcode.UNOP and d.meta.get("operator") in ("cast", "(") and d.operands:
            d = self.defs.get(d.operands[0])
        if d is None or depth > 8:
            return
        holds = holds_in != negate          # the condition is true on this edge
        if d.op == IROpcode.BINOP and d.meta.get("operator") in ("&&", "||") and len(d.operands) == 2:
            # A && B true → both true;  A || B false → both false;  otherwise nothing is known per part
            if (d.meta["operator"] == "&&") == holds:
                for o in d.operands:
                    self._refine(o, holds, new, depth + 1)
            return
        if d.op == IROpcode.BINOP and d.meta.get("kind") == "compare" and len(d.operands) == 2:
            op = d.meta.get("operator", "")
            a, b2 = d.operands
            if op in ("<", "<=", ">", ">="):
                # the side that is bounded above on this edge
                bounded = a if (op in ("<", "<=")) == holds else b2
                for var in self._subjects(bounded):
                    if var in new:
                        new[var] = remove(new[var], frozenset({"size", "index", "buffer"}))
            elif op in ("==",) and holds or op == "!=" and not holds:
                for x, y in ((a, b2), (b2, a)):
                    if self.const_of(y) is not None and x in new and not re.fullmatch(r"t\d+", x):
                        new[x] = {}
        elif d.op == IROpcode.CALL and d.call and d.call.receiver:
            m = d.call.method or ""
            recv = d.call.receiver
            lit = d.call.const_kwargs.get("#0")
            if m in ("equals", "Equals", "equalsIgnoreCase", "eq") and holds and lit is not None and recv in new:
                new[recv] = {}
            elif m in ("matches", "IsMatch", "is_match") and holds and lit is not None:
                subject = recv if m == "matches" else (d.call.args[0] if d.call.args else None)
                if m == "IsMatch" and len(d.call.args) >= 2:
                    lit = d.call.const_kwargs.get("#1", lit)
                allowed = regex_allowed_chars(lit, require_end_anchor=m != "matches")
                if subject and allowed is not None and subject in new:
                    new[subject] = remove(new[subject], frozenset(contexts_cleared_by_charset(allowed)) |
                                          (frozenset({"buffer"}) if re.search(r"\{\d*,?\d+\}$", lit.rstrip("$")) else
                                           frozenset()))
            elif m in ("contains", "Contains", "containsKey", "ContainsKey", "contains_key") and holds \
                    and d.call.args and d.call.args[0] in new and recv not in new:
                new[d.call.args[0]] = {}          # membership in an allow-list collection

    def _subjects(self, op: str) -> List[str]:
        """Variables bounded by a comparison operand: the variable itself, or X in strlen(X)."""
        out = [op] if op else []
        d = self.defs.get(op)
        if d is not None and d.op == IROpcode.CALL and d.call:
            nm = (d.call.method or d.call.callee.split(".")[-1])
            if nm in self.e.spec.strlen_funcs:
                out += [d.call.receiver] if d.call.receiver else []
                out += list(d.call.args[:1])
        elif d is not None and d.op == IROpcode.ATTR and d.meta.get("attr") in ("length", "Length", "Count", "len"):
            out += d.operands[:1]
        return [x for x in out if x]

    def transfer_block(self, instrs, st: State, record: bool) -> State:
        state = dict(st)
        for ins in instrs:
            self.transfer(ins, state, record)
        return state

    def transfer(self, ins: IRInstruction, state: State, record: bool) -> None:
        op = ins.op
        if op == IROpcode.ASSIGN:
            if ins.meta.get("kind") == "param":
                v = state.get(ins.operands[0], {})
            elif "const" in ins.meta:
                v = {}
            else:
                v = join(*[self.get(state, o) for o in ins.operands])
            if ins.result:
                if v and not re.fullmatch(r"t\d+", ins.result) and ins.meta.get("kind") != "param":
                    v = add_step(v, self.step(ins, "assign"))
                state[ins.result] = v
        elif op == IROpcode.BINOP:
            n = ins.meta.get("taint_ops")
            ops = ins.operands if n is None else ins.operands[:int(n)]
            state[ins.result] = join(*[self.get(state, o) for o in ops])
        elif op == IROpcode.UNOP:
            n = ins.meta.get("taint_ops")
            ops = ins.operands if n is None else ins.operands[:int(n)]
            state[ins.result] = join(*[self.get(state, o) for o in ops])
        elif op == IROpcode.BUILD:
            n = ins.meta.get("taint_ops")
            ops = ins.operands if n is None else ins.operands[:int(n)]
            state[ins.result] = join(*[self.get(state, o) for o in ops])
        elif op == IROpcode.ATTR:
            v = join(*[self.get(state, o) for o in ins.operands])
            chain = ins.meta.get("chain", "")
            for s in self.e.spec.sources:
                if s.kind == "attr" and any(chain == p or chain.endswith("." + p) or chain.startswith(p + ".")
                                            or ("." + p + ".") in chain for p in s.patterns):
                    v = join(v, self.source_value(s, ins))
                    break
            state[ins.result] = v
        elif op == IROpcode.SUBSCR:
            base = self.get(state, ins.operands[0]) if ins.operands else {}
            if ins.meta.get("index") == "iter":
                state[ins.result] = base
            else:
                state[ins.result] = base
                if record and len(ins.operands) > 1 and self.e.language in ("c", "cpp"):
                    self.sink_index(ins, state, ins.operands[1], "array read")
        elif op == IROpcode.STORE:
            val = self.get(state, ins.operands[0]) if ins.operands else {}
            base = ins.meta.get("base_name") or ""
            if record and ins.meta.get("kind") == "subscr" and len(ins.operands) > 2 and \
                    self.e.language in ("c", "cpp"):
                self.sink_index(ins, state, ins.operands[2], "array write")
            if base and val:
                state[base] = join(state.get(base, {}), add_step(val, self.step(ins, "store")))
        elif op == IROpcode.CALL:
            self.call(ins, state, record)
        elif op == IROpcode.RETURN:
            if ins.operands:
                self.ret = join(self.ret, self.get(state, ins.operands[0]))

    def sink_index(self, ins, state, idx_op, role) -> None:
        v = self.get(state, idx_op)
        for k, i in v.items():
            if "index" in i.contexts and not i.symbolic:
                self.hits.append(Hit("SEC054", self.q, ins.lineno, ins.col, "[]", role, "index", replace(
                    i, trace=i.trace + (self.step(ins, "sink", f"untrusted value used as {role} index"),)),
                    "exact", "index", ins.uid))

    def call(self, ins: IRInstruction, state: State, record: bool) -> None:
        c = ins.call
        spec = self.e.spec
        recv_v = self.get(state, c.receiver)
        arg_vs = [self.get(state, a) for a in c.args]
        kw_vs = {k: self.get(state, a) for k, a in c.keywords.items()}
        result: Value = {}
        handled = False
        # internal call → summary
        target = self.e.resolve(self, ins)
        if target is not None:
            summ = self.e.summaries.get(target.fn.qualname)
            handled = True
            if summ is not None:
                result = self.e.instantiate(summ["ret"], arg_vs, recv_v, ins, self)
                if record:
                    self.e.instantiate_sinks(summ["hits"], arg_vs, ins, self)
        # sources
        for s in spec.sources:
            if s.kind != "call":
                continue
            m = match_call(s.patterns, ins)
            if m is None:
                continue
            sv = self.source_value(s, ins)
            handled = True
            if s.out_args or s.from_arg is not None:
                idxs = list(s.out_args) + (list(range(s.from_arg, len(c.args))) if s.from_arg is not None else [])
                for k in idxs:
                    if k < len(c.args) and not re.fullmatch(r"t\d+", c.args[k]):
                        state[c.args[k]] = join(state.get(c.args[k], {}), sv)
                if not s.out_args and s.from_arg is None:
                    result = sv
                if s.kind == "call" and c.method in ("read_line", "read_to_string", "read_to_end") and c.args:
                    pass
            else:
                result = join(result, sv)
            break
        # sinks
        if record:
            self.check_sinks(ins, state, recv_v, arg_vs, kw_vs)
        # sanitizers
        for san in spec.sanitizers:
            if match_call(san.patterns, ins) is not None:
                base = join(recv_v, *arg_vs) if not handled else result
                result = remove(base, san.clears)
                result = add_step(result, self.step(ins, "sanitizer", f"{san.note}: {c.raw_callee}()"))
                handled = True
                break
        # C copy functions and output arguments
        fname = c.callee.split(".")[-1] if not c.method else ""
        if fname in spec.copy_into and not c.method:
            dst, srcs = spec.copy_into[fname]
            v = join(*[arg_vs[k] for k in srcs if k < len(arg_vs)])
            if dst >= 0 and dst < len(c.args) and v and not re.fullmatch(r"t\d+", c.args[dst]):
                state[c.args[dst]] = join(state.get(c.args[dst], {}), add_step(v, self.step(ins, "store")))
            if dst < 0:
                result = join(result, v)
            handled = True
        if not handled:
            method = c.method or c.callee.split(".")[-1]
            if method in spec.clean_methods or c.callee in spec.clean_methods:
                result = {}
            else:
                result = join(recv_v, *arg_vs, *kw_vs.values())
                if result and method not in PROPAGATORS and c.callee not in PROPAGATORS and                         not c.callee.startswith("new "):
                    why = f"value passes through unresolved call {c.raw_callee[:60]}()"
                    result = {k: replace(i, unc=i.unc | {why}) for k, i in result.items()}
            if c.method in spec.mutators and c.receiver and not re.fullmatch(r"t\d+", c.receiver):
                v = join(*arg_vs)
                if v:
                    state[c.receiver] = join(state.get(c.receiver, {}), add_step(v, self.step(ins, "store")))
        if ins.result:
            state[ins.result] = result

    # ── sinks ───────────────────────────────────────────────────────────
    def check_sinks(self, ins, state, recv_v, arg_vs, kw_vs) -> None:
        c = ins.call
        for sink in self.e.spec.sinks:
            m = match_call(sink.patterns, ins)
            if m is None:
                continue
            resolution, fmt_idx = m
            if not self.condition_ok(sink, ins, resolution):
                continue
            ctx = sink.context or self.e.rules[sink.rule_id].context or "code"
            operands: List[Tuple[str, Value]] = []
            if fmt_idx is not None:
                positions = [fmt_idx]
            elif sink.condition == "regex_static" and c.callee.startswith("Regex.") and len(arg_vs) >= 2:
                positions = [1]                     # Regex.Match(input, pattern): the pattern is argument 2
            elif sink.args == "*":
                positions = list(range(len(arg_vs)))
            else:
                positions = list(sink.args)
            for k in positions:
                if k < len(arg_vs):
                    if sink.condition == "url" and self.fixed_destination(self.literal_prefix(c.args[k])):
                        continue
                    operands.append((f"argument {k + 1}", arg_vs[k]))
            for kw in sink.kwargs:
                if kw in kw_vs:
                    operands.append((f"'{kw}'", kw_vs[kw]))
            if sink.use_receiver and c.receiver:
                operands.append(("receiver", recv_v))
            for role, v in operands:
                for key, info in v.items():
                    if ctx not in info.contexts:
                        continue
                    sstep = self.step(ins, "sink", f"reaches {sink.operation} {c.raw_callee[:60]}() as {role}")
                    self.hits.append(Hit(sink.rule_id, self.q, ins.lineno, ins.col, c.callee or c.raw_callee,
                                         sink.operation, role, replace(info, trace=info.trace + (sstep,)),
                                         resolution, ctx, ins.uid))

    def condition_ok(self, sink: Sink, ins, resolution: str) -> bool:
        c, cond = ins.call, sink.condition
        chain = (ins.meta.get("chain", "") + " " + c.callee + " " + ins.meta.get("receiver_name", "")).lower()
        if cond == "exec_receiver" and resolution == "method-name":
            return "runtime" in chain or "process" in chain
        if cond == "xpath_receiver":
            return "xpath" in chain or "xpath" in (ins.meta.get("rtype", "") or "").lower()
        if cond == "logger_receiver" and resolution == "method-name":
            return bool(re.search(r"\b(log|logger|_log|_logger|LOG|LOGGER)\b", ins.meta.get("receiver_name", ""),
                                  re.I))
        if cond == "sql_receiver" and resolution == "method-name":
            return bool(re.search(r"(conn|connection|db|database|context|ctx|cmd|command|tx|pool|client|stmt|"
                                  r"session|sql|dapper|transaction)", ins.meta.get("receiver_name", "") +
                                  ins.meta.get("chain", ""), re.I))
        if cond == "deser_receiver" and resolution == "method-name":
            return bool(re.search(r"formatter|losformatter|netdatacontract", ins.meta.get("receiver_name", "") +
                                  " " + self.info.var_types.get(ins.meta.get("receiver_name", ""), ""), re.I))
        if cond == "regex_static" and c.callee.startswith("Regex.") and len(c.args) >= 2:
            return True     # handled by positions below via args=(0,) → static form uses arg 2
        if cond == "session_receiver" and resolution == "method-name":
            return "session" in chain
        if cond == "shell_program":
            root = self.receiver_root_call(c.receiver)
            if root is None or not root.call.args:
                return False
            prog = root.call.const_kwargs.get("#0") or self.const_of(root.call.args[0]) or ""
            return prog.split("/")[-1] in SHELLS or prog in SHELLS
        if cond == "path_receiver" and resolution == "method-name":
            return "file" in chain or "openoptions" in chain
        if cond == "html_body":
            if c.callee in ("Html", "Html.from"):
                return True
            return self.declares_html(c.receiver)
        if cond == "panic_parse":
            return True
        if cond == "no_overflow_clause":
            return ins.meta.get("overflow") != "1"
        return True


class TaintEngine:
    def __init__(self, mod: LoweredModule, spec: LanguageSpec, rules):
        self.mod, self.spec, self.rules = mod, spec, rules
        self.language = mod.language
        self.lines = mod.source.splitlines()
        self.summaries: Dict[str, dict] = {}
        self.by_name: Dict[str, List[FunctionInfo]] = {}
        for info in mod.functions.values():
            self.by_name.setdefault(info.fn.name, []).append(info)
        self.hits: List[Hit] = []
        self.converged = True

    def resolve(self, fa: FunctionAnalysis, ins) -> Optional[FunctionInfo]:
        c = ins.call
        if c.callee.startswith("new ") or ins.meta.get("macro"):
            return None
        name = c.method or c.callee.split(".")[-1]
        if c.receiver and c.receiver not in ("this", "self") and not (
                ins.meta.get("receiver_name") in ("this", "self", "base")):
            # method on another object: only when its declared type is a class of this file
            rt = ins.meta.get("rtype", "")
            if not rt or rt not in self.mod.ir.classes:
                return None
        cands = [i for i in self.by_name.get(name, []) if len(i.fn.params) == len(c.args) or
                 (i.fn.params and i.fn.params[0] == "self" and len(i.fn.params) == len(c.args) + 1)]
        return cands[0] if len(cands) == 1 else None

    def instantiate(self, ret: Value, arg_vs, recv_v, ins, fa: FunctionAnalysis) -> Value:
        out: Value = {}
        for key, info in ret.items():
            if key[0] == "param":
                idx = key[2]
                actual = arg_vs[idx] if idx < len(arg_vs) else {}
                for k2, i2 in actual.items():
                    out[k2] = replace(i2, contexts=i2.contexts & info.contexts,
                                      trace=i2.trace + (fa.step(ins, "call", f"through {ins.call.raw_callee[:60]}()"),))
            else:
                out[key] = info
        return {k: v for k, v in out.items() if v.contexts}

    def instantiate_sinks(self, hits: List[Hit], arg_vs, ins, fa: FunctionAnalysis) -> None:
        for h in hits:
            key = ("param", h.function, None)
            # the hit's origin is one of the callee's parameters
            idx = next((i for i, p in enumerate(self.mod.functions[h.function].fn.params)
                        if h.info.description == f"parameter '{p}'"), None)
            if idx is None or idx >= len(arg_vs):
                continue
            for k2, i2 in arg_vs[idx].items():
                if h.context in i2.contexts:
                    call_step = fa.step(ins, "call", f"passes the value to {ins.call.raw_callee[:60]}()")
                    fa.hits.append(replace(h, info=replace(i2, trace=i2.trace + (call_step,) + h.info.trace[1:],
                                                           symbolic=i2.symbolic),
                                           via=(fa.q,) + h.via))

    def run(self) -> List[Hit]:
        infos = list(self.mod.functions.values())
        for rnd in range(6):
            changed = False
            for info in infos:
                fa = FunctionAnalysis(self, info)
                fa.run(record=True)
                param_hits = [h for h in fa.hits if h.info.symbolic]
                summ = {"ret": {k: v for k, v in fa.ret.items()}, "hits": param_hits}
                old = self.summaries.get(info.fn.qualname)
                sig = (sorted((str(k), tuple(sorted(v.contexts))) for k, v in summ["ret"].items()),
                       sorted((h.rule_id, h.line, h.info.description) for h in param_hits))
                if old is None or old.get("_sig") != sig:
                    summ["_sig"] = sig
                    self.summaries[info.fn.qualname] = summ
                    changed = True
            if not changed:
                break
        else:
            self.converged = False
        hits: Dict[tuple, Hit] = {}
        for info in infos:
            fa = FunctionAnalysis(self, info)
            fa.run(record=True)
            for h in fa.hits:
                if h.info.symbolic:
                    continue
                k = h.key()
                if k not in hits or len(h.info.trace) < len(hits[k].info.trace):
                    hits[k] = h
        self.hits = list(hits.values())
        return self.hits
