"""
COBOL front end: parser and IR lowering
=========================================
COBOL has no tree-sitter grammar on PyPI, so this module parses it directly.

Supported
---------
* fixed format (sequence area 1-6, indicator column 7 — ``*`` / ``/`` comments,
  ``-`` continuation, code in 8-72) and free format (``*>`` comments);
* IDENTIFICATION (PROGRAM-ID), ENVIRONMENT (``SELECT f ASSIGN TO DYNAMIC var`` /
  ``ASSIGN USING var``), DATA DIVISION items: level, name, PIC, VALUE, OCCURS,
  group / child hierarchy, LINKAGE SECTION;
* PROCEDURE DIVISION [USING …], paragraphs and sections, and the statements
  ACCEPT, DISPLAY, MOVE, COMPUTE, ADD, SUBTRACT, MULTIPLY, DIVIDE, INITIALIZE,
  STRING, UNSTRING, CALL (static, dynamic, SYSTEM), EXEC SQL … END-EXEC
  (EXECUTE IMMEDIATE, PREPARE … FROM, static SQL with host variables),
  EXEC CICS (RECEIVE, WEB RECEIVE / READ, LINK, XCTL, SEND, WEB SEND), IF / ELSE /
  END-IF, EVALUATE / WHEN, PERFORM (out-of-line, inline … END-PERFORM, UNTIL,
  VARYING), OPEN, READ … INTO, WRITE … FROM, GOBACK, STOP RUN, EXIT;
* reference modification ``X(a:b)`` and subscripts ``T(i)``.

Lowering
--------
The PROCEDURE DIVISION becomes one ``IRFunction``. Paragraphs are basic blocks
inside a loop (header → every paragraph → header), because PERFORM can run any
paragraph in any order: data flow is flow-sensitive inside a paragraph and
flow-insensitive across paragraphs. Moving data into a group item also moves
it into the group's children, and moving into a child also reaches the group.

Not supported: COPY / REPLACE expansion, nested programs (each PROGRAM-ID is
lowered separately only if they follow each other), declaratives, and the
report writer. Unknown statements are skipped and listed in ``unsupported``.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from ..ir.ir_nodes import CallInfo, IRBlock, IRFunction, IRInstruction, IRModule, IROpcode
from .lower import FunctionInfo, LoweredModule

VERBS = {"ACCEPT", "DISPLAY", "MOVE", "COMPUTE", "ADD", "SUBTRACT", "MULTIPLY", "DIVIDE", "STRING", "UNSTRING",
         "CALL", "EXEC", "IF", "ELSE", "END-IF", "EVALUATE", "WHEN", "END-EVALUATE", "PERFORM", "END-PERFORM",
         "OPEN", "CLOSE", "READ", "WRITE", "REWRITE", "DELETE", "START", "GOBACK", "STOP", "EXIT", "INITIALIZE",
         "SET", "INSPECT", "GO", "CONTINUE", "NEXT", "END-READ", "END-WRITE", "END-STRING", "END-UNSTRING",
         "END-CALL", "END-COMPUTE", "END-ADD", "END-SUBTRACT", "END-MULTIPLY", "END-DIVIDE", "SEARCH", "SORT",
         "MERGE", "RELEASE", "RETURN", "CANCEL", "END-EXEC", "NOT", "AT", "INVALID", "ON"}
TERMINATORS = {"END-IF", "ELSE", "WHEN", "END-EVALUATE", "END-PERFORM"}
_TOKEN = re.compile(r"'(?:[^']|'')*'|\"(?:[^\"]|\"\")*\"|[A-Za-z0-9][A-Za-z0-9_-]*|>=|<=|[():.,=<>+\-*/]")
SYSTEM_CALLS = {"SYSTEM", "C$SYSTEM", "CBL_EXEC_RUN_UNIT", "CBL_OC_SYSTEM"}
SECRET_NAME = re.compile(r"(?i)(PASS(WORD|WD)?|PWD|SECRET|TOKEN|API-?KEY|CREDENTIAL|PRIVATE-?KEY|PIN-CODE)")


@dataclass
class Tok:
    text: str
    line: int
    col: int

    @property
    def up(self) -> str:
        return self.text.upper()

    @property
    def is_lit(self) -> bool:
        return self.text[:1] in "'\"" or bool(re.fullmatch(r"[+-]?\d+(\.\d+)?", self.text))


@dataclass
class DataItem:
    level: int
    name: str
    line: int
    pic: str = ""
    value: Optional[str] = None
    occurs: int = 0
    parent: Optional[str] = None
    children: List[str] = field(default_factory=list)
    section: str = ""


_DIVISION_EARLY = re.compile(r"^\s{0,6}(IDENTIFICATION|ID|ENVIRONMENT|DATA|PROCEDURE)\s+DIVISION", re.I)


def normalize(source: str) -> List[Tuple[int, str]]:
    """(line number, code text) with comments removed, for fixed or free format."""
    lines = source.splitlines()
    # fixed format puts DIVISION headers in Area A (column 8+); free format may start them anywhere before
    free = any(">>SOURCE" in l.upper() and "FREE" in l.upper() for l in lines[:5]) or any(
        _DIVISION_EARLY.match(l) for l in lines)
    out: List[Tuple[int, str]] = []
    for i, raw in enumerate(lines, 1):
        if free:
            code = raw.split("*>", 1)[0]
            if code.lstrip().startswith("*") and not code.lstrip().startswith("*>"):
                code = ""
        else:
            if len(raw) > 6 and raw[6] in "*/":
                code = ""
            else:
                code = raw[7:72] if len(raw) > 7 else ""
                code = code.split("*>", 1)[0]
                if len(raw) > 6 and raw[6] == "-" and out:          # continuation of a literal
                    cont = code.lstrip()
                    if cont[:1] in "'\"":
                        cont = cont[1:]
                    ln, prev = out[-1]
                    out[-1] = (ln, prev.rstrip().rstrip("'\"") + cont)
                    continue
        out.append((i, code))
    return out


def tokenize(source: str) -> List[Tok]:
    toks: List[Tok] = []
    for ln, code in normalize(source):
        for m in _TOKEN.finditer(code):
            toks.append(Tok(m.group(0), ln, m.start() + 7))
    return toks


class _Parser:
    def __init__(self, source: str, filepath: str):
        self.src = source
        self.toks = tokenize(source)
        self.i = 0
        self.items: Dict[str, DataItem] = {}
        self.program = "PROGRAM"
        self.using: List[str] = []
        self.dynamic_files: Dict[str, str] = {}      # file name → variable holding its path
        self.proc_start = len(self.toks)
        self.filepath = filepath

    # ── divisions ───────────────────────────────────────────────────────
    def parse_headers(self) -> None:
        t = self.toks
        n = len(t)
        i = 0
        section = ""
        stack: List[DataItem] = []
        while i < n:
            u = t[i].up
            if u == "PROGRAM-ID" and i + 2 < n:
                j = i + 1
                if t[j].text == ".":
                    j += 1
                self.program = t[j].text.strip("'\"").upper()
            elif u == "SELECT" and i + 1 < n:
                fname = t[i + 1].up
                j = i + 2
                while j < n and t[j].text != ".":
                    if t[j].up in ("DYNAMIC", "USING") and j + 1 < n and not t[j + 1].is_lit:
                        self.dynamic_files[fname] = t[j + 1].up
                    j += 1
                i = j
            elif u in ("WORKING-STORAGE", "LINKAGE", "LOCAL-STORAGE", "FILE") and i + 1 < n and t[i + 1].up == "SECTION":
                section = u
                stack = []
            elif u == "PROCEDURE" and i + 1 < n and t[i + 1].up == "DIVISION":
                j = i + 2
                if j < n and t[j].up == "USING":
                    j += 1
                    while j < n and t[j].text != ".":
                        if t[j].up not in ("BY", "REFERENCE", "VALUE", "CONTENT", ","):
                            self.using.append(t[j].up)
                        j += 1
                while j < n and t[j].text != ".":
                    j += 1
                self.proc_start = j + 1
                break
            elif section and re.fullmatch(r"\d{1,2}", t[i].text) and i + 1 < n and \
                    (i == 0 or t[i - 1].text == "." or t[i - 1].line != t[i].line):
                level = int(t[i].text)
                name = t[i + 1].up
                if name in ("FILLER", "."):
                    name = f"FILLER-{t[i].line}"
                item = DataItem(level, name, t[i].line, section=section)
                j = i + 2
                while j < n and t[j].text != ".":
                    w = t[j].up
                    if w in ("PIC", "PICTURE") and j + 1 < n:
                        k = j + 1
                        if t[k].up == "IS":
                            k += 1
                        pic = []
                        while k < n and t[k].text != "." and t[k].up not in ("VALUE", "OCCURS", "USAGE", "COMP",
                                                                             "COMP-3", "BINARY", "REDEFINES"):
                            pic.append(t[k].text)
                            k += 1
                        item.pic = "".join(pic)
                        j = k
                        continue
                    if w in ("VALUE", "VALUES") and j + 1 < n:
                        k = j + 1
                        if t[k].up == "IS":
                            k += 1
                        item.value = t[k].text if k < n else None
                    if w == "OCCURS" and j + 1 < n and t[j + 1].text.isdigit():
                        item.occurs = int(t[j + 1].text)
                    j += 1
                if level in (1, 77):
                    stack = [item]
                else:
                    while stack and stack[-1].level >= level:
                        stack.pop()
                    if stack:
                        item.parent = stack[-1].name
                        stack[-1].children.append(name)
                    stack.append(item)
                self.items[name] = item
                i = j
            i += 1


@dataclass
class _Stmt:
    verb: str
    toks: List[Tok]


class _Lowerer:
    """Builds the IR of the PROCEDURE DIVISION."""

    def __init__(self, p: _Parser, info: FunctionInfo):
        self.p, self.info, self.fn = p, info, info.fn
        self.cur: Optional[IRBlock] = None
        self._uid = self._t = 0
        self._counts: Dict[str, int] = {}
        self.line = 1

    def uid(self):
        self._uid += 1
        return self._uid

    def temp(self):
        self._t += 1
        return f"t{self._t}"

    def count(self, k):
        self._counts[k] = self._counts.get(k, 0) + 1
        return self._counts[k]

    def new_block(self, label, **meta):
        b = IRBlock(label=label, meta={k: str(v) for k, v in meta.items()})
        b.instructions.append(IRInstruction(IROpcode.LABEL, lineno=self.line, meta={"name": label}, uid=self.uid()))
        self.fn.blocks.append(b)
        return b

    def link(self, a, label):
        if a is None:
            return
        if label not in a.successors:
            a.successors.append(label)
        b = self.fn.get_block(label)
        if b is not None and a.label not in b.predecessors:
            b.predecessors.append(a.label)

    def emit(self, op, result=None, operands=None, tok: Optional[Tok] = None, call=None, **meta):
        if self.cur is None:
            self.cur = self.new_block(f"dead_{self.count('dead')}", kind="unreachable")
        line = tok.line if tok is not None else self.line
        ins = IRInstruction(op=op, result=result, operands=list(operands or []), lineno=line,
                            col=tok.col if tok is not None else 0, end_lineno=line,
                            meta={k: str(v) for k, v in meta.items()}, call=call, uid=self.uid())
        self.cur.instructions.append(ins)
        if result and not re.fullmatch(r"t\d+", result):
            self.fn.locals.add(result)
        return ins

    def jump_to(self, label):
        if self.cur is not None:
            self.emit(IROpcode.JUMP, operands=[label])
            self.link(self.cur, label)
            self.cur = None

    def start(self, label, **meta):
        prev = self.cur
        b = self.new_block(label, **meta)
        if prev is not None:
            prev.instructions.append(IRInstruction(IROpcode.JUMP, operands=[label], lineno=self.line, uid=self.uid()))
            self.link(prev, label)
        self.cur = b
        return b

    # ── operands ────────────────────────────────────────────────────────
    def const(self, tok: Tok) -> str:
        t = self.temp()
        val = tok.text[1:-1].replace("''", "'").replace('""', '"') if tok.text[:1] in "'\"" else tok.text
        self.emit(IROpcode.ASSIGN, result=t, tok=tok, kind="string" if tok.text[:1] in "'\"" else "const", const=val)
        return t

    def operand(self, toks: List[Tok], k: int) -> Tuple[Optional[str], int]:
        """Lower the operand starting at toks[k]; returns (operand, next index)."""
        if k >= len(toks):
            return None, k
        t = toks[k]
        if t.is_lit or t.up in ("SPACES", "SPACE", "ZERO", "ZEROS", "ZEROES", "HIGH-VALUES", "LOW-VALUES", "QUOTES",
                                "ALL", "NULL", "NULLS"):
            return self.const(t), k + 1
        if t.up == "FUNCTION" and k + 1 < len(toks):
            fname = toks[k + 1].up
            args, j = [], k + 2
            if j < len(toks) and toks[j].text == "(":
                depth, j = 1, j + 1
                while j < len(toks) and depth:
                    if toks[j].text == "(":
                        depth += 1
                    elif toks[j].text == ")":
                        depth -= 1
                    elif re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", toks[j].text) or toks[j].is_lit:
                        a, _ = self.operand(toks, j)
                        args.append(a)
                    j += 1
            r = self.temp()
            self.emit(IROpcode.CALL, result=r, operands=args, tok=t,
                      call=CallInfo(callee=f"FUNCTION.{fname}", raw_callee=f"FUNCTION {fname}", args=args),
                      chain=f"FUNCTION.{fname}")
            return r, j
        if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", t.text):
            return None, k + 1
        name = t.up
        j = k + 1
        # skip OF / IN qualification
        while j + 1 < len(toks) and toks[j].up in ("OF", "IN"):
            j += 2
        if j < len(toks) and toks[j].text == "(" and toks[j - 1].line == toks[j].line:
            # subscript T(i) or reference modification X(a:b)
            depth, k2, parts, cur = 1, j + 1, [], []
            while k2 < len(toks) and depth:
                tt = toks[k2]
                if tt.text == "(":
                    depth += 1
                elif tt.text == ")":
                    depth -= 1
                    if depth == 0:
                        break
                if tt.text == ":" and depth == 1:
                    parts.append(cur)
                    cur = []
                elif tt.text not in (",",):
                    cur.append(tt)
                k2 += 1
            parts.append(cur)
            idx_ops = []
            for part in parts:
                if part:
                    o, _ = self.operand(part, 0)
                    if o:
                        idx_ops.append(o)
            refmod = len(parts) > 1
            r = self.temp()
            self.emit(IROpcode.CALL, result=r, operands=idx_ops, tok=t,
                      call=CallInfo(callee="REFMOD", raw_callee=f"{name}({'ref-mod' if refmod else 'subscript'})",
                                    args=idx_ops), chain="REFMOD", base=name)
            s = self.temp()
            self.emit(IROpcode.SUBSCR, result=s, operands=[name] + idx_ops, tok=t, base_name=name)
            return s, k2 + 1
        return name, j

    def assign(self, target: str, value: Optional[str], tok: Tok) -> None:
        if value is None:
            return
        self.emit(IROpcode.ASSIGN, result=target, operands=[value], tok=tok)
        item = self.p.items.get(target)
        if item is not None:
            for ch in self._descendants(item):
                self.emit(IROpcode.ASSIGN, result=ch, operands=[target], tok=tok, kind="group")
            par = item.parent
            while par:                                     # the group now contains the data too
                self.emit(IROpcode.BINOP, result=par, operands=[par, target], tok=tok, operator="group")
                par = self.p.items[par].parent if par in self.p.items else None

    def _descendants(self, item: DataItem) -> List[str]:
        out = []
        for c in item.children:
            out.append(c)
            if c in self.p.items:
                out += self._descendants(self.p.items[c])
        return out

    # ── statements ──────────────────────────────────────────────────────
    def split(self, toks: List[Tok]) -> List[_Stmt]:
        """Group procedure tokens into statements (a verb and its operands)."""
        out: List[_Stmt] = []
        cur: Optional[_Stmt] = None
        in_exec = False
        for t in toks:
            u = t.up
            if in_exec:
                cur.toks.append(t)
                if u == "END-EXEC":
                    in_exec = False
                continue
            if t.text == ".":
                if cur is not None:
                    out.append(cur)
                    cur = None
                out.append(_Stmt(".", [t]))
                continue
            if u in VERBS and not (cur is not None and cur.verb in ("IF", "EVALUATE", "WHEN", "PERFORM") and
                                   u in ("NOT",)) and not (cur is not None and u in ("ON", "AT", "INVALID", "NOT")
                                                            and cur.verb in ("STRING", "UNSTRING", "READ", "WRITE",
                                                                             "CALL", "ADD", "COMPUTE", "DIVIDE")):
                if cur is not None:
                    out.append(cur)
                cur = _Stmt(u, [t])
                if u == "EXEC":
                    in_exec = True
                continue
            if cur is None:
                cur = _Stmt("LABEL?", [t])
            else:
                cur.toks.append(t)
        if cur is not None:
            out.append(cur)
        return out

    def run(self) -> None:
        p = self.p
        self.cur = self.new_block("entry", kind="entry")
        for u in p.using:                                   # LINKAGE parameters
            self.emit(IROpcode.ASSIGN, result=u, operands=[f"param:{u}"], kind="param")
        stmts = self.split(p.toks[p.proc_start:])
        # paragraphs: a name followed by "." at the start of a statement group
        paragraphs: List[Tuple[str, List[_Stmt]]] = [("<start>", [])]
        k = 0
        while k < len(stmts):
            s = stmts[k]
            if s.verb == "LABEL?" and len(s.toks) <= 2 and k + 1 < len(stmts) and stmts[k + 1].verb == ".":
                name = s.toks[0].up
                if len(s.toks) == 2 and s.toks[1].up == "SECTION":
                    name += " SECTION"
                paragraphs.append((name, []))
                k += 2
                continue
            paragraphs[-1][1].append(s)
            k += 1
        self.start("proc_header", kind="loop_header")
        self.emit(IROpcode.BRANCH, operands=["t0", "para_0", "exit_loop"], kind="loop")
        head = self.cur
        self.cur = None
        prev_end = None
        for idx, (name, body) in enumerate(paragraphs):
            lbl = f"para_{idx}"
            b = self.new_block(lbl, kind="paragraph", name=name)
            self.link(head, lbl)
            if prev_end is not None:
                prev_end.instructions.append(IRInstruction(IROpcode.JUMP, operands=[lbl], lineno=self.line,
                                                           uid=self.uid()))
                self.link(prev_end, lbl)
            self.cur = b
            self.block(body, 0)
            prev_end = self.cur
        if prev_end is not None:
            prev_end.instructions.append(IRInstruction(IROpcode.JUMP, operands=["proc_header"], lineno=self.line,
                                                       uid=self.uid()))
            self.link(prev_end, "proc_header")
        self.cur = None
        eb = self.new_block("exit_loop", kind="loop_exit")
        self.link(head, "exit_loop")
        self.cur = eb
        exit_b = self.new_block("exit", kind="exit")
        eb.instructions.append(IRInstruction(IROpcode.JUMP, operands=["exit"], lineno=self.line, uid=self.uid()))
        self.link(eb, "exit")
        for b in self.fn.blocks:
            if "exit" in b.successors and b.label not in exit_b.predecessors:
                exit_b.predecessors.append(b.label)

    def block(self, stmts: List[_Stmt], k: int, stop=frozenset()) -> int:
        """Lower statements from index k until a terminator in ``stop``; returns the next index."""
        while k < len(stmts):
            s = stmts[k]
            if s.verb in stop:
                return k
            if s.verb == "." and "." in stop:
                return k
            k = self.statement(stmts, k)
        return k

    def statement(self, stmts: List[_Stmt], k: int) -> int:
        s = stmts[k]
        v, toks = s.verb, s.toks
        head = toks[0]
        self.line = head.line
        args = toks[1:]
        if v in (".", "LABEL?", "CONTINUE", "EXIT", "END-STRING", "END-UNSTRING", "END-CALL", "END-READ",
                 "END-WRITE", "END-COMPUTE", "END-ADD", "END-SUBTRACT", "END-MULTIPLY", "END-DIVIDE", "END-EXEC",
                 "NEXT", "CLOSE", "NOT", "AT", "INVALID", "ON"):
            return k + 1
        if v == "ACCEPT" and args:
            target, j = args[0].up, 1
            src = "ACCEPT"
            if any(t.up == "FROM" for t in args) and any(t.up in ("DATE", "TIME", "DAY", "DAY-OF-WEEK") for t in args):
                src = "ACCEPT.SYSTEM"
            r = self.temp()
            self.emit(IROpcode.CALL, result=r, tok=head, call=CallInfo(callee=src, raw_callee="ACCEPT"), chain=src)
            self.assign(target, r, head)
            return k + 1
        if v == "DISPLAY":
            ops = []
            j = 0
            while j < len(args) and args[j].up not in ("UPON", "WITH"):
                o, j = self.operand(args, j)
                if o:
                    ops.append(o)
            self.emit(IROpcode.CALL, result=self.temp(), operands=ops, tok=head,
                      call=CallInfo(callee="DISPLAY", raw_callee="DISPLAY", args=ops), chain="DISPLAY")
            return k + 1
        if v == "MOVE":
            to = next((i for i, t in enumerate(args) if t.up == "TO"), None)
            if to is None:
                return k + 1
            src, _ = self.operand(args[:to], 1 if args and args[0].up == "CORRESPONDING" else 0)
            j = to + 1
            while j < len(args):
                if re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", args[j].text) and args[j].up not in ("OF", "IN"):
                    tgt = args[j].up
                    if j + 1 < len(args) and args[j + 1].text == "(":       # MOVE x TO T(i): index use
                        self.operand(args, j)
                    self.assign(tgt, src, head)
                j += 1
            return k + 1
        if v in ("COMPUTE", "ADD", "SUBTRACT", "MULTIPLY", "DIVIDE"):
            ops, targets = [], []
            j = 0
            split_kw = {"COMPUTE": "=", "ADD": "TO", "SUBTRACT": "FROM", "MULTIPLY": "BY", "DIVIDE": "INTO"}[v]
            seen_split = False
            while j < len(args):
                t = args[j]
                if t.up in (split_kw, "GIVING", "=") :
                    seen_split = True
                    j += 1
                    continue
                if t.up in ("ROUNDED", "ON", "SIZE", "ERROR", "NOT", "REMAINDER"):
                    j += 1
                    continue
                o, j2 = self.operand(args, j)
                if o:
                    (targets if (v == "COMPUTE" and not seen_split) or (v != "COMPUTE" and seen_split and
                                                                         re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", t.text))
                     else ops).append(o if not (v == "COMPUTE" and not seen_split) else t.up)
                j = max(j2, j + 1)
            r = self.temp()
            self.emit(IROpcode.BINOP, result=r, operands=ops + [x for x in targets if v != "COMPUTE"], tok=head,
                      operator=v.lower())
            for tg in targets:
                self.assign(tg, r, head)
            return k + 1
        if v == "INITIALIZE":
            for t in args:
                if re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", t.text):
                    self.assign(t.up, self.const(Tok("SPACES", t.line, t.col)), head)
            return k + 1
        if v == "STRING":
            into = next((i for i, t in enumerate(args) if t.up == "INTO"), None)
            srcs, j = [], 0
            while into is not None and j < into:
                t = args[j]
                if t.up == "DELIMITED":
                    j += 2 if j + 2 <= into and args[j + 1].up == "BY" else 1
                    if j < into and args[j].up in ("SIZE", "SPACE", "SPACES"):
                        j += 1
                    elif j < into:
                        j += 1
                    continue
                o, j = self.operand(args, j)
                if o:
                    srcs.append(o)
            if into is None or into + 1 >= len(args):
                return k + 1
            tgt = args[into + 1].up
            overflow = any(t.up == "OVERFLOW" for t in args)
            r = self.temp()
            self.emit(IROpcode.BUILD, result=r, operands=srcs, tok=head, kind="string")
            self.assign(tgt, r, head)
            if overflow:
                self.fn.decorators.append(f"overflow:{head.line}")
            return k + 1
        if v == "UNSTRING" and args:
            src, _ = self.operand(args, 0)
            into = next((i for i, t in enumerate(args) if t.up == "INTO"), None)
            if into is not None:
                for t in args[into + 1:]:
                    if t.up in ("DELIMITER", "COUNT", "TALLYING", "POINTER", "ON", "OVERFLOW", "NOT", "WITH"):
                        break
                    if re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", t.text):
                        self.assign(t.up, src, head)
            return k + 1
        if v == "CALL" and args:
            target = args[0]
            using = []
            j = 1
            if j < len(args) and args[j].up == "USING":
                j += 1
                while j < len(args) and args[j].up not in ("RETURNING", "ON", "EXCEPTION", "END-CALL", "GIVING"):
                    if args[j].up not in ("BY", "REFERENCE", "CONTENT", "VALUE", ","):
                        o, j = self.operand(args, j)
                        if o:
                            using.append(o)
                        continue
                    j += 1
            if target.is_lit:
                prog = target.text.strip("'\"").upper()
                callee = "CALL.SYSTEM" if prog in SYSTEM_CALLS else f"CALL.{prog}"
                ops = using
            else:
                callee = "CALL.DYNAMIC"
                ops = [target.up] + using
            r = self.temp()
            self.emit(IROpcode.CALL, result=r, operands=ops, tok=head,
                      call=CallInfo(callee=callee, raw_callee=f"CALL {target.text}", args=ops), chain=callee)
            return k + 1
        if v == "EXEC":
            self.exec_block(toks)
            return k + 1
        if v == "IF":
            return self.if_stmt(stmts, k)
        if v == "EVALUATE":
            return self.evaluate(stmts, k)
        if v == "PERFORM":
            return self.perform(stmts, k)
        if v in ("OPEN",):
            for t in args:
                f = t.up
                if f in self.p.dynamic_files:
                    var = self.p.dynamic_files[f]
                    self.emit(IROpcode.CALL, result=self.temp(), operands=[var], tok=t,
                              call=CallInfo(callee="OPEN.DYNAMIC", raw_callee=f"OPEN {f}", args=[var]),
                              chain="OPEN.DYNAMIC")
            return k + 1
        if v == "READ" and args:
            into = next((i for i, t in enumerate(args) if t.up == "INTO"), None)
            r = self.temp()
            self.emit(IROpcode.CALL, result=r, tok=head, call=CallInfo(callee="READ", raw_callee="READ"), chain="READ")
            if into is not None and into + 1 < len(args):
                self.assign(args[into + 1].up, r, head)
            return k + 1
        if v in ("WRITE", "REWRITE") and args:
            frm = next((i for i, t in enumerate(args) if t.up == "FROM"), None)
            if frm is not None and frm + 1 < len(args):
                self.assign(args[0].up, args[frm + 1].up, head)
            return k + 1
        if v in ("GOBACK", "STOP"):
            self.emit(IROpcode.RETURN, tok=head)
            self.link(self.cur, "exit")
            self.cur = None
            return k + 1
        if v in ("SET", "INSPECT", "GO", "SEARCH", "SORT", "MERGE", "RELEASE", "RETURN", "CANCEL", "DELETE", "START"):
            tag = f"{v} (not modelled)"
            if tag not in self.fn.unsupported:
                self.fn.unsupported.append(tag)
            return k + 1
        return k + 1

    def exec_block(self, toks: List[Tok]) -> None:
        kind = toks[1].up if len(toks) > 1 else ""
        body = toks[2:-1] if toks[-1].up == "END-EXEC" else toks[2:]
        words = [t.up for t in body]
        head = toks[0]

        def host(idx):            # :VAR after position idx
            for j in range(idx, len(body) - 1):
                if body[j].text == ":":
                    return body[j + 1].up
            return None
        if kind == "SQL":
            if "IMMEDIATE" in words:
                var = host(words.index("IMMEDIATE"))
                callee = "SQL.EXECUTE-IMMEDIATE"
            elif "PREPARE" in words and "FROM" in words:
                var = host(words.index("FROM"))
                callee = "SQL.PREPARE"
            else:
                # static SQL: host variables are bound, INTO variables receive database data
                if "INTO" in words:
                    j = words.index("INTO") + 1
                    while j < len(body) and words[j] not in ("FROM", "WHERE"):
                        if body[j].text == ":" and j + 1 < len(body):
                            r = self.temp()
                            self.emit(IROpcode.CALL, result=r, tok=head,
                                      call=CallInfo(callee="SQL.FETCH", raw_callee="EXEC SQL"), chain="SQL.FETCH")
                            self.assign(body[j + 1].up, r, head)
                        j += 1
                return
            if var:
                self.emit(IROpcode.CALL, result=self.temp(), operands=[var], tok=head,
                          call=CallInfo(callee=callee, raw_callee=f"EXEC SQL {callee.split('.')[1]}", args=[var]),
                          chain=callee)
            return
        if kind == "CICS":
            def opt(name):
                if name in words:
                    j = words.index(name)
                    if j + 2 < len(body) and body[j + 1].text == "(":
                        t = body[j + 2]
                        return t
                return None
            if "RECEIVE" in words or ("WEB" in words and ("READ" in words or "RECEIVE" in words)):
                tgt = opt("INTO") or opt("VALUE") or opt("SET")
                if tgt is not None and not tgt.is_lit:
                    r = self.temp()
                    callee = "CICS.WEB.RECEIVE" if "WEB" in words else "CICS.RECEIVE"
                    self.emit(IROpcode.CALL, result=r, tok=head, call=CallInfo(callee=callee, raw_callee="EXEC CICS"),
                              chain=callee)
                    self.assign(tgt.up, r, head)
            for verb in ("LINK", "XCTL"):
                if verb in words:
                    t = opt("PROGRAM")
                    if t is not None and not t.is_lit:
                        self.emit(IROpcode.CALL, result=self.temp(), operands=[t.up], tok=head,
                                  call=CallInfo(callee=f"CICS.{verb}", raw_callee=f"EXEC CICS {verb}", args=[t.up]),
                                  chain=f"CICS.{verb}")
            if "SEND" in words:
                t = opt("FROM")
                if t is not None and not t.is_lit:
                    callee = "CICS.WEB.SEND" if "WEB" in words else "CICS.SEND"
                    self.emit(IROpcode.CALL, result=self.temp(), operands=[t.up], tok=head,
                              call=CallInfo(callee=callee, raw_callee="EXEC CICS SEND", args=[t.up]), chain=callee)

    def condition(self, toks: List[Tok]) -> str:
        """Lower a condition (comparisons, IS NUMERIC, AND / OR / NOT) to a value for BRANCH."""
        ops = {"=": "==", "EQUAL": "==", ">": ">", "GREATER": ">", "<": "<", "LESS": "<", ">=": ">=", "<=": "<="}
        # split on AND / OR (left to right, no precedence beyond that)
        parts, conns, cur = [], [], []
        for t in toks:
            if t.up in ("AND", "OR"):
                parts.append(cur)
                conns.append(t.up)
                cur = []
            else:
                cur.append(t)
        parts.append(cur)
        vals = []
        for part in parts:
            words = [t.up for t in part if t.up not in ("IS", "THAN", "TO")]
            neg = words.count("NOT") % 2 == 1
            core = [t for t in part if t.up not in ("IS", "THAN", "TO", "NOT")]
            if core and core[-1].up in ("NUMERIC", "ALPHABETIC") and len(core) >= 2:
                subj, _ = self.operand(core, 0)
                pat = "[0-9]+" if core[-1].up == "NUMERIC" else "[A-Za-z ]+"
                r = self.temp()
                self.emit(IROpcode.CALL, result=r, operands=[subj], tok=core[0],
                          call=CallInfo(callee="matches", raw_callee="IS " + core[-1].up, method="matches",
                                        receiver=subj, const_kwargs={"#0": pat}), chain="matches")
            else:
                op_i = next((i for i, t in enumerate(core) if t.up in ops or t.text in ops), None)
                if op_i is None:
                    r = self.temp()
                    o, _ = self.operand(core, 0) if core else (None, 0)
                    self.emit(IROpcode.BINOP, result=r, operands=[o] if o else [], tok=part[0] if part else None,
                              kind="compare", operator="truth", taint_ops="0")
                else:
                    a, _ = self.operand(core[:op_i], 0)
                    b, _ = self.operand(core[op_i + 1:], 0)
                    op = ops.get(core[op_i].up, ops.get(core[op_i].text, "=="))
                    if core[op_i].up in ("GREATER", "LESS") and op_i + 2 < len(core) and core[op_i + 1].up == "OR":
                        op += "="
                    r = self.temp()
                    self.emit(IROpcode.BINOP, result=r, operands=[a or "", b or ""], tok=core[op_i], kind="compare",
                              operator=op, taint_ops="0")
            if neg:
                r2 = self.temp()
                self.emit(IROpcode.UNOP, result=r2, operands=[r], operator="!", taint_ops="0")
                r = r2
            vals.append(r)
        acc = vals[0]
        for conn, val in zip(conns, vals[1:]):
            r = self.temp()
            self.emit(IROpcode.BINOP, result=r, operands=[acc, val], kind="compare",
                      operator="&&" if conn == "AND" else "||", taint_ops="0")
            acc = r
        return acc

    def _cond_tokens(self, s: _Stmt) -> List[Tok]:
        return [t for t in s.toks[1:] if t.up != "THEN"]

    def if_stmt(self, stmts, k) -> int:
        s = stmts[k]
        n = self.count("branch")
        c = self.condition(self._cond_tokens(s))
        tl, fl, jl = f"branch_{n}_true", f"branch_{n}_false", f"branch_{n}_join"
        head = self.cur
        self.emit(IROpcode.BRANCH, operands=[c, tl, fl], tok=s.toks[0], kind="if")
        self.cur = None
        self.new_block(tl, kind="if_true")
        self.link(head, tl)
        self.cur = self.fn.get_block(tl)
        k = self.block(stmts, k + 1, frozenset({"ELSE", "END-IF", "."}))
        t_end = self.cur
        self.cur = None
        self.new_block(fl, kind="if_false")
        self.link(head, fl)
        self.cur = self.fn.get_block(fl)
        if k < len(stmts) and stmts[k].verb == "ELSE":
            k = self.block(stmts, k + 1, frozenset({"END-IF", "."}))
        f_end = self.cur
        if k < len(stmts) and stmts[k].verb == "END-IF":
            k += 1
        self.cur = None
        jb = self.new_block(jl, kind="join")
        for e in (t_end, f_end):
            if e is not None:
                e.instructions.append(IRInstruction(IROpcode.JUMP, operands=[jl], lineno=self.line, uid=self.uid()))
                self.link(e, jl)
        self.cur = jb
        return k

    def evaluate(self, stmts, k) -> int:
        s = stmts[k]
        n = self.count("switch")
        subj, _ = self.operand(s.toks[1:], 0)
        head = self.cur
        jl = f"switch_{n}_join"
        self.emit(IROpcode.BRANCH, operands=[subj or "", jl], tok=s.toks[0], kind="switch")
        ends = []
        k += 1
        i = 0
        while k < len(stmts) and stmts[k].verb == "WHEN":
            lbl = f"switch_{n}_case_{i}"
            i += 1
            self.cur = None
            self.new_block(lbl, kind="case")
            self.link(head, lbl)
            self.cur = self.fn.get_block(lbl)
            k = self.block(stmts, k + 1, frozenset({"WHEN", "END-EVALUATE", "."}))
            ends.append(self.cur)
        if k < len(stmts) and stmts[k].verb == "END-EVALUATE":
            k += 1
        self.cur = None
        jb = self.new_block(jl, kind="join")
        self.link(head, jl)
        for e in ends:
            if e is not None:
                e.instructions.append(IRInstruction(IROpcode.JUMP, operands=[jl], lineno=self.line, uid=self.uid()))
                self.link(e, jl)
        self.cur = jb
        return k

    def perform(self, stmts, k) -> int:
        s = stmts[k]
        words = [t.up for t in s.toks[1:]]
        inline = not words or words[0] in ("UNTIL", "VARYING", "WITH", "TEST") or (
            len(words) >= 2 and words[1] == "TIMES" and not any(w in self.p.items for w in words[:1]) and
            k + 1 < len(stmts) and stmts[k + 1].verb not in (".",) and self._has_end_perform(stmts, k))
        if not inline:
            return k + 1                    # out-of-line PERFORM: paragraphs are already reachable
        n = self.count("loop")
        hl, bl, el = f"loop_{n}_header", f"loop_{n}_body", f"loop_{n}_exit"
        self.start(hl, kind="loop_header")
        until = [t for t in s.toks[1:]]
        if "UNTIL" in words:
            c = self.condition(until[words.index("UNTIL") + 1:])
        else:
            c = self.temp()
            self.emit(IROpcode.ASSIGN, result=c, kind="const", const="")
        self.emit(IROpcode.BRANCH, operands=[c, el, bl], tok=s.toks[0], kind="loop")
        hb = self.cur
        self.cur = None
        self.new_block(bl, kind="loop_body")
        self.link(hb, bl)
        self.cur = self.fn.get_block(bl)
        k = self.block(stmts, k + 1, frozenset({"END-PERFORM", "."}))
        if k < len(stmts) and stmts[k].verb == "END-PERFORM":
            k += 1
        if self.cur is not None:
            self.cur.instructions.append(IRInstruction(IROpcode.JUMP, operands=[hl], lineno=self.line, uid=self.uid()))
            self.link(self.cur, hl)
        self.cur = None
        eb = self.new_block(el, kind="loop_exit")
        self.link(hb, el)
        self.cur = eb
        return k

    @staticmethod
    def _has_end_perform(stmts, k) -> bool:
        for s in stmts[k + 1:]:
            if s.verb == "END-PERFORM":
                return True
            if s.verb == ".":
                return False
        return False


def lower_cobol(source: str, filepath: str = "") -> LoweredModule:
    p = _Parser(source, filepath)
    p.parse_headers()
    first_proc = p.toks[p.proc_start].line if p.proc_start < len(p.toks) else 1
    last = p.toks[-1].line if p.toks else 1
    fn = IRFunction(name=p.program, params=list(p.using), qualname=p.program, source_lineno=first_proc,
                    end_lineno=last, source_file=filepath)
    info = FunctionInfo(fn=fn, node=None, name_line=first_proc)
    for u in p.using:
        info.param_types[u + "#linkage"] = "1"
    _Lowerer(p, info).run()
    mod = IRModule(source_file=filepath, functions=[fn])
    lm = LoweredModule("cobol", source, mod, {p.program: info}, None, None)
    lm.cobol = p                                  # data items for the COBOL pattern rules
    # STRING ... ON OVERFLOW lines: mark so the overflow sink is not reported there
    return lm


def cobol_patterns(mod: LoweredModule) -> List[dict]:
    """Hard-coded credentials in WORKING-STORAGE, and secrets written with DISPLAY."""
    p: _Parser = getattr(mod, "cobol", None)
    out: List[dict] = []
    if p is None:
        return out
    fn = next(iter(mod.functions.values())).fn
    for item in p.items.values():
        if SECRET_NAME.search(item.name) and item.value and item.value[:1] in "'\"":
            v = item.value.strip("'\"")
            if len(v.strip()) >= 4 and v.upper() not in ("SPACES", "CHANGEME", "PASSWORD"):
                out.append({"rule_id": "SEC003", "line": item.line, "col": 7, "function": fn.qualname,
                            "message": f"Hard-coded secret in data item {item.name} (VALUE '{v[:2]}****').",
                            "confidence": "medium",
                            "confidence_reasons": ["secret identified from the data item's name and a literal VALUE"]})
    for ins in fn.all_instructions():
        if ins.op == IROpcode.CALL and ins.call and ins.call.callee == "DISPLAY":
            for a in ins.call.args:
                if SECRET_NAME.search(a or ""):
                    out.append({"rule_id": "SEC050", "line": ins.lineno, "col": ins.col, "function": fn.qualname,
                                "message": f"Secret data item {a} is written with DISPLAY.", "confidence": "medium",
                                "confidence_reasons": ["sensitivity inferred from the name"]})
                    break
    return out
