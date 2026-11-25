"""
Memory-safety analysis for C and C++ (use after free, double free, unchecked allocation)
==========================================================================================
Forward data-flow over each function's CFG.

State per program point:
  freed_may   pointer → line of a free/delete on SOME path reaching here
  freed_must  pointers freed on EVERY path reaching here
  unchecked   pointers holding a malloc/calloc/realloc result not yet compared with NULL

Transfer:
  free(p) / delete p      double free if p ∈ freed_may (high when p ∈ freed_must), then p is freed
  p = …                   p is no longer freed (reassigned) and no longer unchecked unless the new
                          value is an allocation
  use of p                use after free if p ∈ freed_may (dereference, index, field, call argument)
  branch on p             p is checked (``if (p)``, ``if (!p)``, ``p == NULL``)
  dereference of p        unchecked allocation if p ∈ unchecked

Aliases (``q = p``) are not tracked; that is a documented limitation.
"""
from __future__ import annotations

import re
from typing import Dict, FrozenSet, List, Optional, Set, Tuple

from ..analysis.cfg_builder import build_cfg
from ..ir.ir_nodes import IROpcode
from .lower import FunctionInfo, LoweredModule
from .specs import SPECS

Raw = Dict[str, object]
_DEREF_CALLS = {"memcpy", "memmove", "memset", "strcpy", "strncpy", "strcat", "strncat", "sprintf", "snprintf",
                "fgets", "fread", "fwrite", "read", "recv", "strlen", "puts", "printf", "fputs", "sscanf",
                "gets", "strcmp", "strchr", "strstr", "qsort", "bzero"}
_NOT_A_USE = {"free", "delete", "delete[]", "cfree", "g_free", "kfree"}


def _var(info: FunctionInfo, op: Optional[str], defs) -> Optional[str]:
    """Variable behind an operand: the name itself, or the variable a cast / temp copies."""
    seen = 0
    while op and re.fullmatch(r"t\d+", op) and seen < 6:
        d = defs.get(op)
        if d is None or d.op not in (IROpcode.UNOP, IROpcode.ASSIGN) or not d.operands or \
                d.meta.get("deref") == "1" or d.meta.get("operator") not in (None, "cast", ""):
            return None
        op = d.operands[0]
        seen += 1
    return op if op and not re.fullmatch(r"t\d+", op) and not op.startswith("param:") else None


class _State:
    __slots__ = ("may", "must", "unchecked")

    def __init__(self, may=None, must=None, unchecked=None):
        self.may: Dict[str, int] = dict(may or {})
        self.must: Set[str] = set(must or ())
        self.unchecked: Dict[str, int] = dict(unchecked or {})

    def copy(self):
        return _State(self.may, self.must, self.unchecked)

    def key(self):
        return (tuple(sorted(self.may.items())), tuple(sorted(self.must)), tuple(sorted(self.unchecked.items())))


def _join(states: List[_State]) -> _State:
    if not states:
        return _State()
    out = states[0].copy()
    for s in states[1:]:
        for k, v in s.may.items():
            out.may.setdefault(k, v)
        out.must &= s.must
        for k, v in s.unchecked.items():
            out.unchecked.setdefault(k, v)
    return out


def analyze_memory(mod: LoweredModule) -> List[Raw]:
    if mod.language not in ("c", "cpp"):
        return []
    spec = SPECS[mod.language]
    out: List[Raw] = []
    seen = set()

    def add(rule, ins, fn, msg, conf, reasons):
        k = (rule, ins.lineno, msg.split("'")[1] if "'" in msg else "")
        if k in seen:
            return
        seen.add(k)
        out.append({"rule_id": rule, "line": ins.lineno, "col": ins.col, "function": fn, "message": msg,
                    "confidence": conf, "confidence_reasons": reasons, "analysis": "memory-flow"})

    for info in mod.functions.values():
        fn = info.fn
        defs = {i.result: i for i in fn.all_instructions() if i.result}
        cfg = build_cfg(fn)
        order = [b.label for b in fn.blocks]
        states_out: Dict[str, _State] = {}

        def transfer(block_instrs, st: _State, record: bool):
            st = st.copy()
            for ins in block_instrs:
                c = ins.call if ins.op == IROpcode.CALL else None
                name = (c.callee if c is not None and not c.method else "") if c is not None else ""
                is_free = c is not None and (name in spec.free_funcs or name in ("delete", "delete[]"))
                if is_free and c.args:
                    v = _var(info, c.args[0], defs)
                    if v:
                        if record and v in st.may:
                            sure = v in st.must
                            add("SEC057", ins, fn.qualname,
                                f"'{v}' is freed again (first freed on line {st.may[v]}).",
                                "high" if sure else "medium",
                                [] if sure else ["the earlier free happens only on some paths"])
                        st.may[v] = ins.lineno
                        st.must.add(v)
                        st.unchecked.pop(v, None)
                    continue
                # uses of a freed / unchecked pointer
                used: List[Tuple[str, str]] = []
                if ins.op == IROpcode.UNOP and ins.meta.get("deref") == "1":
                    used.append((ins.operands[0], "dereference"))
                elif ins.op == IROpcode.SUBSCR and ins.meta.get("index") != "iter" and ins.operands:
                    used.append((ins.operands[0], "index"))
                elif ins.op == IROpcode.ATTR and ins.operands:
                    used.append((ins.operands[0], "field access"))
                elif ins.op == IROpcode.STORE and ins.meta.get("base_name") and ins.meta.get("kind") in ("subscr", "deref", "attr"):
                    used.append((ins.meta["base_name"], "write"))
                elif c is not None and name not in _NOT_A_USE:
                    for a in c.args:
                        used.append((a, f"argument to {c.raw_callee[:30]}()"))
                    if c.receiver:
                        used.append((c.receiver, "method call"))
                for op_, how in used:
                    v = _var(info, op_, defs) if op_ else None
                    if not v:
                        continue
                    if record and v in st.may:
                        sure = v in st.must
                        add("SEC056", ins, fn.qualname,
                            f"'{v}' is used ({how}) after it was freed on line {st.may[v]}.",
                            "high" if sure else "medium",
                            [] if sure else ["the free happens only on some paths to this use"])
                    if record and v in st.unchecked and (how in ("dereference", "index", "write", "field access")
                                                         or (c is not None and name in _DEREF_CALLS)):
                        add("SEC058", ins, fn.qualname,
                            f"'{v}' (allocated on line {st.unchecked[v]}) is used without checking for NULL.",
                            "medium", ["allocation failure is rare but possible; the result is never compared "
                                       "with NULL before this use"])
                        st.unchecked.pop(v, None)
                # assignments
                if ins.op == IROpcode.ASSIGN and ins.result and not re.fullmatch(r"t\d+", ins.result):
                    st.may.pop(ins.result, None)
                    st.must.discard(ins.result)
                    st.unchecked.pop(ins.result, None)
                    src = ins.operands[0] if ins.operands else None
                    d = defs.get(src)
                    while d is not None and d.op == IROpcode.UNOP and d.meta.get("operator") == "cast":
                        d = defs.get(d.operands[0])
                    if d is not None and d.op == IROpcode.CALL and d.call and not d.call.method and \
                            d.call.callee in ("malloc", "calloc", "realloc", "strdup", "strndup", "aligned_alloc"):
                        st.unchecked[ins.result] = ins.lineno
                if ins.op == IROpcode.BRANCH and ins.operands:
                    for v in _branch_vars(ins.operands[0], defs, info):
                        st.unchecked.pop(v, None)
            return st

        work = list(order)
        n = 0
        while work and n < 40 * max(1, len(order)):
            n += 1
            lbl = work.pop(0)
            node = cfg.nodes.get(lbl)
            if node is None:
                continue
            ins_state = _State() if lbl == order[0] else _join([states_out[p] for p in node.predecessors
                                                                if p in states_out])
            new = transfer(node.instructions, ins_state, record=False)
            if lbl not in states_out or states_out[lbl].key() != new.key():
                states_out[lbl] = new
                for s in node.successors:
                    if s not in work:
                        work.append(s)
        for lbl in order:
            node = cfg.nodes.get(lbl)
            if node is None:
                continue
            ins_state = _State() if lbl == order[0] else _join([states_out[p] for p in node.predecessors
                                                                if p in states_out])
            transfer(node.instructions, ins_state, record=True)
    return out


def _branch_vars(op, defs, info, depth=0) -> Set[str]:
    out: Set[str] = set()
    if depth > 4 or not op:
        return out
    v = _var(info, op, defs)
    if v:
        out.add(v)
        return out
    d = defs.get(op)
    if d is not None and d.op in (IROpcode.BINOP, IROpcode.UNOP):
        for o in d.operands:
            out |= _branch_vars(o, defs, info, depth + 1)
    return out
