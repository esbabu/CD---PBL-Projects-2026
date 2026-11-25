"""
Fix strategies
===============
Deterministic, AST-based rewrites. Each strategy has a name, the rule it
handles and an ``apply(ctx)`` function that returns a :class:`Patch` with the
patched source, or ``patched=None`` and a note explaining why it does not apply.
Strategies only *propose* a patch; the agent accepts it only after
``verify.verify_patch`` has checked it with the analyzer.

  SEC005  sql-param-qmark      string-built query → "... = ?" + params tuple
          sql-param-format     same with "%s" placeholders (psycopg2 / MySQL / Django)
  SEC002  cmd-argv-list        os.system / shell=True → subprocess argument list, shell=False
          cmd-shlex-quote      keep the shell, wrap every untrusted part in shlex.quote()
  SEC010  yaml-safe-load       yaml.load(...) → yaml.safe_load(...)
  SEC004  hash-sha256          hashlib.md5/sha1 → hashlib.sha256
  SEC001  eval-literal-eval    eval(x) → ast.literal_eval(x)
  SEC018  xxe-disable-entities resolve_entities / external-entity features → False
  SEC024  regex-escape         re.<fn>(pattern, ...) → re.<fn>(re.escape(pattern), ...)
  SEC029  debug-off            app.run(debug=True) → debug=False
  SEC030  tls-verify-on        verify=False → verify=True
  SEC042  tar-data-filter      tar.extractall(dest) → tar.extractall(dest, filter="data")
  SEC043  jinja-autoescape     jinja2.Environment(...) → autoescape=True
  SEC044  cookie-secure        set_cookie(...) → secure=True, httponly=True
"""
from __future__ import annotations

import ast
import copy
import string
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Sequence, Tuple, Union

from .source import (Edit, apply_edits, calls_at, canonical, ensure_import, function_node,
                     import_aliases, imported_modules, module_name_for, py_string, scope_nodes,
                     segment, walk_scope)


@dataclass
class FixContext:
    """What a strategy sees: the current source, its AST and the finding to fix."""
    source: str
    tree: ast.Module
    finding: object                      # src.security.findings.Finding

    @classmethod
    def build(cls, source: str, finding) -> "FixContext":
        return cls(source, ast.parse(source), finding)

    @property
    def aliases(self) -> Dict[str, str]:
        return import_aliases(self.tree)

    def sink_calls(self) -> List[ast.Call]:
        return calls_at(self.tree, self.finding.function, self.finding.line, self.finding.col)


@dataclass
class Patch:
    patched: Optional[str]
    note: str


@dataclass(frozen=True)
class Strategy:
    name: str
    rule_id: str
    description: str
    apply: Callable[[FixContext], Patch]


def _skip(note: str) -> Patch:
    return Patch(None, note)


# ---------------------------------------------------------------------------
# Shared analysis: where does a string come from, and what is it made of?
# ---------------------------------------------------------------------------

def _binds(node: ast.AST, name: str) -> bool:
    """Does this node (re)bind ``name``?"""
    targets: List[ast.AST] = []
    if isinstance(node, ast.Assign):
        targets = node.targets
    elif isinstance(node, (ast.AnnAssign, ast.AugAssign, ast.NamedExpr)):
        targets = [node.target]
    elif isinstance(node, (ast.For, ast.AsyncFor)):
        targets = [node.target]
    elif isinstance(node, ast.withitem) and node.optional_vars is not None:
        targets = [node.optional_vars]
    elif isinstance(node, ast.ExceptHandler):
        return node.name == name
    elif isinstance(node, (ast.Global, ast.Nonlocal)):
        return name in node.names
    return any(isinstance(n, ast.Name) and n.id == name for t in targets for n in ast.walk(t))


def _bindings(ctx: FixContext, name: str) -> List[ast.AST]:
    return [n for n in walk_scope(scope_nodes(ctx.tree, ctx.finding.function)) if _binds(n, name)]


def _parameters(ctx: FixContext) -> set:
    fn = function_node(ctx.tree, ctx.finding.function)
    if fn is None:
        return set()
    a = fn.args
    return {x.arg for x in a.posonlyargs + a.args + a.kwonlyargs} | \
        {x.arg for x in (a.vararg, a.kwarg) if x is not None}


def resolve(ctx: FixContext, expr: ast.AST, use_line: int) -> Tuple[Optional[ast.AST], Optional[ast.Assign], str]:
    """
    Follow ``final = query = "..." + x`` back to the expression that builds the
    string. Returns (value, defining assignment or None if inline, note).
    Gives up when a name is a parameter or is bound more than once.
    """
    assign = None
    for _ in range(6):
        if not isinstance(expr, ast.Name):
            return expr, assign, ""
        if expr.id in _parameters(ctx):
            return None, None, f"'{expr.id}' is a parameter; the string is built by the caller"
        binds = _bindings(ctx, expr.id)
        if len(binds) != 1 or not isinstance(binds[0], ast.Assign) or len(binds[0].targets) != 1 \
                or not isinstance(binds[0].targets[0], ast.Name) or binds[0].lineno >= use_line:
            return None, None, f"'{expr.id}' is assigned in several places (branches or loops)"
        assign = binds[0]
        expr = assign.value
    return None, None, "assignment chain too long"


Piece = Union[str, ast.AST]          # literal text, or an expression that is spliced in


def pieces_of(expr: ast.AST) -> Optional[List[Piece]]:
    """
    Split a string-building expression into literal text and spliced expressions:
    ``"a" + x + "b"``, f-strings, ``"... %s" % x`` and ``"... {}".format(x)``.
    None when the expression is not one of these shapes.
    """
    if isinstance(expr, ast.Constant) and isinstance(expr.value, str):
        return [expr.value]
    if isinstance(expr, ast.BinOp) and isinstance(expr.op, ast.Add):
        left, right = pieces_of(expr.left), pieces_of(expr.right)
        if left is None and right is None:
            return None
        return (left if left is not None else [expr.left]) + (right if right is not None else [expr.right])
    if isinstance(expr, ast.JoinedStr):
        out: List[Piece] = []
        for v in expr.values:
            if isinstance(v, ast.Constant):
                out.append(v.value)
            elif isinstance(v, ast.FormattedValue) and v.conversion == -1 and v.format_spec is None:
                out.append(v.value)
            else:
                return None
        return out
    if isinstance(expr, ast.BinOp) and isinstance(expr.op, ast.Mod) and \
            isinstance(expr.left, ast.Constant) and isinstance(expr.left.value, str):
        args = list(expr.right.elts) if isinstance(expr.right, ast.Tuple) else [expr.right]
        text, out, i = expr.left.value, [], 0
        buf = ""
        while i < len(text):
            if text[i] == "%":
                spec = text[i + 1:i + 2]
                if spec == "%":
                    buf += "%"
                elif spec in ("s", "d") and args:
                    out += [buf, args.pop(0)]
                    buf = ""
                else:
                    return None
                i += 2
            else:
                buf += text[i]
                i += 1
        return None if args else out + [buf]
    if isinstance(expr, ast.Call) and isinstance(expr.func, ast.Attribute) and expr.func.attr == "format" \
            and isinstance(expr.func.value, ast.Constant) and isinstance(expr.func.value.value, str) \
            and not expr.keywords:
        out, auto = [], 0
        for literal, field, spec, conv in string.Formatter().parse(expr.func.value.value):
            out.append(literal)
            if field is None:
                continue
            if spec or conv or not (field == "" or field.isdigit()):
                return None
            idx = auto if field == "" else int(field)
            auto += 1
            if idx >= len(expr.args):
                return None
            out.append(expr.args[idx])
        return out
    return None


def _merge(pieces: Sequence[Piece]) -> List[Piece]:
    """Join adjacent literal pieces and drop empty ones."""
    out: List[Piece] = []
    for p in pieces:
        if isinstance(p, str):
            if not p:
                continue
            if out and isinstance(out[-1], str):
                out[-1] += p
                continue
        out.append(p)
    return out


def _rebound_between(ctx: FixContext, exprs: Sequence[ast.AST], start: int, end: int) -> Optional[str]:
    """Is any name used in ``exprs`` rebound strictly between two lines?"""
    names = {n.id for e in exprs for n in ast.walk(e) if isinstance(n, ast.Name)}
    for name in names:
        if any(start < b.lineno < end for b in _bindings(ctx, name)):
            return name
    return None


# ---------------------------------------------------------------------------
# SEC005 — parameterised SQL
# ---------------------------------------------------------------------------

_VALUE_POSITION = ("=", "<", ">", "LIKE", "(", ",", "LIMIT", "OFFSET")
_FORMAT_DRIVERS = {"django", "psycopg2", "psycopg", "pymysql", "MySQLdb", "mysql", "asyncpg"}


def build_parameterised(pieces: Sequence[Piece], source: str, placeholder: str) -> Tuple[Optional[str], List[str], str]:
    """
    Turn query pieces into (sql text, parameter expressions). Quotes around a
    spliced value are removed; '%'+x+'%' around LIKE values moves into the
    parameter. Refuses when a value is spliced where SQL expects an identifier
    or keyword (ORDER BY col, WHERE <clause>) — a placeholder cannot go there.
    """
    pieces = _merge(pieces)          # a private copy: neighbouring text is trimmed in place
    sql, params = "", []
    for i, p in enumerate(pieces):
        if isinstance(p, str):
            continue
        nxt = pieces[i + 1] if i + 1 < len(pieces) and isinstance(pieces[i + 1], str) else ""
        prev = pieces[i - 1] if i > 0 and isinstance(pieces[i - 1], str) else ""
        lead, trail = "", ""
        if prev.endswith("'%") and nxt.startswith("%'"):
            prev, nxt, lead, trail = prev[:-2], nxt[2:], '"%" + ', ' + "%"'
        elif prev.endswith("'") and nxt.startswith("'"):
            prev, nxt = prev[:-1], nxt[1:]
        if not prev.rstrip().upper().endswith(_VALUE_POSITION):
            context = " ".join(prev.split()[-3:])
            return None, [], ("the untrusted value is spliced in as SQL syntax "
                              f"(after '{context}'), not as a value; use an allow-list")
        if i > 0 and isinstance(pieces[i - 1], str):
            pieces[i - 1] = prev
        if i + 1 < len(pieces) and isinstance(pieces[i + 1], str):
            pieces[i + 1] = nxt
        params.append(f"{lead}{segment(source, p)}{trail}")
    if not params:
        return None, [], "the query has no spliced value"
    for p in pieces:
        if isinstance(p, str):
            sql += p.replace("%", "%%") if placeholder == "%s" else p
        else:
            sql += placeholder
    if sql.count("'") % 2:
        return None, [], "quotes in the query do not balance after removing the splices"
    return sql, params, ""


def _sql_fix(placeholder: str) -> Callable[[FixContext], Patch]:
    def apply(ctx: FixContext) -> Patch:
        mods = imported_modules(ctx.tree)
        if placeholder == "?" and mods & _FORMAT_DRIVERS and "sqlite3" not in mods:
            return _skip("the module uses a %s-style driver (" + ", ".join(sorted(mods & _FORMAT_DRIVERS)) + ")")
        if placeholder == "%s" and "sqlite3" in mods and not mods & _FORMAT_DRIVERS:
            return _skip("sqlite3 uses ? placeholders, not %s")
        for call in ctx.sink_calls():
            if not (isinstance(call.func, ast.Attribute) and call.func.attr in ("execute", "executemany")):
                continue
            if len(call.args) != 1 or call.keywords:
                return _skip("the execute() call already passes more than the query")
            value, assign, why = resolve(ctx, call.args[0], call.lineno)
            if value is None:
                return _skip(why)
            pieces = pieces_of(value)
            if pieces is None:
                return _skip("the query is not built by concatenation, an f-string, % or .format()")
            sql, params, why = build_parameterised(pieces, ctx.source, placeholder)
            if sql is None:
                return _skip(why)
            tuple_text = "(" + ", ".join(params) + ("," if len(params) == 1 else "") + ")"
            if assign is None:
                edits = [Edit.replace(call.args[0], f"{py_string(sql)}, {tuple_text}")]
            else:
                param_nodes = [p for p in pieces if not isinstance(p, str)]
                name = _rebound_between(ctx, param_nodes, assign.end_lineno, call.lineno)
                if name:
                    return _skip(f"'{name}' changes between building and running the query")
                arg = call.args[0]
                edits = [Edit.replace(assign.value, py_string(sql)),
                         Edit.insert(arg.end_lineno, arg.end_col_offset, f", {tuple_text}")]
            return Patch(apply_edits(ctx.source, edits),
                         f"parameterised query with {len(params)} {placeholder} placeholder(s)")
        return _skip("no execute()/executemany() call at the reported line")
    return apply


# ---------------------------------------------------------------------------
# SEC002 — command injection
# ---------------------------------------------------------------------------

_SHELL_STRING_CALLS = {"os.system", "os.popen", "subprocess.getoutput", "subprocess.getstatusoutput"}
_SUBPROCESS_CALLS = {"subprocess.run", "subprocess.call", "subprocess.check_call",
                     "subprocess.check_output", "subprocess.Popen"}
_SHELL_META = set("|&;<>()$`\\\"'*?[]{}~#!\n")


def _shell_kw(call: ast.Call) -> Optional[ast.keyword]:
    return next((k for k in call.keywords if k.arg == "shell"), None)


def _command_call(ctx: FixContext) -> Tuple[Optional[ast.Call], str]:
    aliases = ctx.aliases
    for call in ctx.sink_calls():
        name = canonical(call.func, aliases)
        kw = _shell_kw(call)
        shell_true = kw is not None and isinstance(kw.value, ast.Constant) and kw.value.value is True
        if (name in _SHELL_STRING_CALLS or (name in _SUBPROCESS_CALLS and shell_true)) and call.args:
            return call, name
    return None, ""


def _tokens(pieces: Sequence[Piece]) -> Optional[List[List[Piece]]]:
    """Split command pieces into argv tokens; None if the literal text uses shell syntax."""
    tokens: List[List[Piece]] = [[]]
    for p in _merge(pieces):
        if not isinstance(p, str):
            tokens[-1].append(p)
            continue
        for ch in p:
            if ch in _SHELL_META:
                return None
            if ch.isspace():
                if tokens[-1]:
                    tokens.append([])
            elif tokens[-1] and isinstance(tokens[-1][-1], str):
                tokens[-1][-1] += ch
            else:
                tokens[-1].append(ch)
    return [t for t in tokens if t]


def _token_text(token: List[Piece], source: str) -> str:
    parts = [py_string(p) if isinstance(p, str) else
             (segment(source, p) if len(token) == 1 else f"str({segment(source, p)})") for p in token]
    return " + ".join(parts)


def _cmd_argv(ctx: FixContext) -> Patch:
    call, name = _command_call(ctx)
    if call is None:
        return _skip("no shell command call at the reported line")
    if name in ("os.popen", "subprocess.getstatusoutput"):
        return _skip(f"{name}() returns a different type than subprocess.run()")
    value, assign, why = resolve(ctx, call.args[0], call.lineno)
    if value is None:
        return _skip(why)
    pieces = pieces_of(value)
    if pieces is None:
        return _skip("the whole command string comes from outside; nothing safe to split")
    tokens = _tokens(pieces)
    if tokens is None:
        return _skip("the command uses shell syntax (pipes, redirection, quotes or globs)")
    if not tokens or not all(isinstance(p, str) for p in tokens[0]):
        return _skip("the untrusted value chooses the program itself")
    param_nodes = [p for p in pieces if not isinstance(p, str)]
    if assign is not None:
        name_changed = _rebound_between(ctx, param_nodes, assign.end_lineno, call.lineno)
        if name_changed:
            return _skip(f"'{name_changed}' changes between building and running the command")
    argv = "[" + ", ".join(_token_text(t, ctx.source) for t in tokens) + "]"
    if name in ("os.system", "subprocess.getoutput"):
        tail = ", capture_output=True, text=True).stdout" if name == "subprocess.getoutput" else ")"
        edits = [Edit.replace(call, f"subprocess.run({argv}, shell=False, check=True{tail}")]
        patched = ensure_import(apply_edits(ctx.source, edits), "subprocess")
    else:
        kw = _shell_kw(call)
        edits = [Edit.replace(call.args[0], argv), Edit.replace(kw.value, "False")]
        if name == "subprocess.run" and not any(k.arg == "check" for k in call.keywords):
            edits.append(Edit.insert(kw.value.end_lineno, kw.value.end_col_offset, ", check=True"))
        patched = apply_edits(ctx.source, edits)
    return Patch(patched, f"argument list with {len(tokens)} item(s), shell=False")


def _cmd_shlex(ctx: FixContext) -> Patch:
    call, name = _command_call(ctx)
    if call is None:
        return _skip("no shell command call at the reported line")
    value, assign, why = resolve(ctx, call.args[0], call.lineno)
    if value is None:
        return _skip(why)
    pieces = pieces_of(value)
    if pieces is None:
        return _skip("the whole command string comes from outside; quoting it would not help")
    merged = _merge(pieces)
    if not merged or not isinstance(merged[0], str) or not merged[0].strip():
        return _skip("the untrusted value chooses the program itself")
    spliced = [p for p in pieces if not isinstance(p, str)]
    if isinstance(value, ast.JoinedStr):
        new = copy.deepcopy(value)
        for v in new.values:
            if isinstance(v, ast.FormattedValue):
                v.value = ast.Call(ast.Attribute(ast.Name("shlex", ast.Load()), "quote", ast.Load()),
                                   [v.value], [])
        edits = [Edit.replace(value, ast.unparse(new))]
    else:
        edits = [Edit.replace(p, f"shlex.quote(str({segment(ctx.source, p)}))") for p in spliced]
    patched = ensure_import(apply_edits(ctx.source, edits), "shlex")
    return Patch(patched, f"{len(spliced)} untrusted part(s) wrapped in shlex.quote()")


# ---------------------------------------------------------------------------
# SEC010 / SEC004 / SEC001 — API swaps
# ---------------------------------------------------------------------------

_YAML_SAFE = {"yaml.load": "safe_load", "yaml.unsafe_load": "safe_load", "yaml.full_load": "safe_load",
              "yaml.load_all": "safe_load_all", "yaml.unsafe_load_all": "safe_load_all",
              "yaml.full_load_all": "safe_load_all"}


def _module_prefix(ctx: FixContext, module: str) -> Tuple[str, bool]:
    """Local name to use for ``module`` and whether an import must be added."""
    local = module_name_for(ctx.tree, module)
    return (local, False) if local else (module, True)


def _yaml_safe(ctx: FixContext) -> Patch:
    aliases = ctx.aliases
    for call in ctx.sink_calls():
        safe = _YAML_SAFE.get(canonical(call.func, aliases))
        if not safe:
            continue
        stream = call.args[0] if call.args else next((k.value for k in call.keywords if k.arg == "stream"), None)
        if stream is None:
            return _skip("yaml.load() call without a stream argument")
        prefix, need_import = _module_prefix(ctx, "yaml")
        patched = apply_edits(ctx.source, [Edit.replace(call, f"{prefix}.{safe}({segment(ctx.source, stream)})")])
        return Patch(ensure_import(patched, "yaml") if need_import else patched, f"yaml.{safe}()")
    return _skip("no unsafe yaml load at the reported line")


def _hash_sha256(ctx: FixContext) -> Patch:
    aliases = ctx.aliases
    for call in ctx.sink_calls():
        name = canonical(call.func, aliases)
        if any(k.arg == "usedforsecurity" for k in call.keywords):
            return _skip("usedforsecurity= is set; the use is declared non-security")
        if name in ("hashlib.md5", "hashlib.sha1"):
            prefix, need_import = _module_prefix(ctx, "hashlib")
            patched = apply_edits(ctx.source, [Edit.replace(call.func, f"{prefix}.sha256")])
            patched = ensure_import(patched, "hashlib") if need_import else patched
        elif name == "hashlib.new" and call.args and isinstance(call.args[0], ast.Constant) \
                and str(call.args[0].value).lower().replace("-", "") in ("md5", "sha1"):
            patched = apply_edits(ctx.source, [Edit.replace(call.args[0], '"sha256"')])
        else:
            continue
        return Patch(patched, "SHA-256 (stored digests change; passwords need a KDF such as hashlib.scrypt)")
    return _skip("no MD5/SHA-1 call at the reported line")


def _eval_literal(ctx: FixContext) -> Patch:
    aliases = ctx.aliases
    for call in ctx.sink_calls():
        if canonical(call.func, aliases) not in ("eval", "builtins.eval"):
            continue
        if len(call.args) != 1 or call.keywords:
            return _skip("eval() is given globals/locals; literal_eval takes one argument")
        patched = apply_edits(ctx.source, [Edit.replace(call.func, "ast.literal_eval")])
        return Patch(ensure_import(patched, "ast"), "ast.literal_eval() accepts only literals")
    return _skip("no eval() call at the reported line (exec/compile cannot be made safe automatically)")


_XXE_FEATURES = ("feature_external_ges", "feature_external_pes")


def _xxe_disable(ctx: FixContext) -> Patch:
    """Switch external entities back off where the reported function turned them on."""
    aliases = ctx.aliases
    edits = []
    for node in walk_scope(scope_nodes(ctx.tree, ctx.finding.function)):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if (isinstance(func, ast.Attribute) and func.attr == "setFeature" and len(node.args) == 2
                and canonical(node.args[0], aliases).endswith(_XXE_FEATURES)
                and isinstance(node.args[1], ast.Constant) and node.args[1].value is True):
            edits.append(Edit.replace(node.args[1], "False"))
        elif canonical(func, aliases) == "lxml.etree.XMLParser":
            for kw in node.keywords:
                if kw.arg == "resolve_entities" and isinstance(kw.value, ast.Constant) and kw.value.value is True:
                    edits.append(Edit.replace(kw.value, "False"))
    if not edits:
        return _skip("external entities are not switched on inside this function")
    return Patch(apply_edits(ctx.source, edits), "external entities disabled (entity references are no longer expanded)")


# ---------------------------------------------------------------------------
# Settings rules (SEC029, SEC030, SEC042, SEC043, SEC044) and sanitiser wraps (SEC019, SEC024)
# ---------------------------------------------------------------------------

def _set_keyword(source: str, call: ast.Call, name: str, value: str) -> Edit:
    """Edit that sets ``name=value`` on ``call``: replace the keyword's value, or append it."""
    for kw in call.keywords:
        if kw.arg == name:
            return Edit.replace(kw.value, value)
    text = segment(source, call)
    body = text[:-1].rstrip()
    sep = "" if body.endswith(("(", ",")) else ", "
    return Edit.replace(call, f"{body}{sep}{name}={value})")


def _keyword_fix(predicate, name: str, value: str, note: str):
    """Strategy: on the reported line, set keyword ``name=value`` on the call matching predicate."""
    def apply(ctx: FixContext) -> Patch:
        aliases = ctx.aliases
        for call in ctx.sink_calls():
            if predicate(call, canonical(call.func, aliases)):
                return Patch(apply_edits(ctx.source, [_set_keyword(ctx.source, call, name, value)]), note)
        return _skip("no matching call on the reported line")
    return apply


def _is_kw(call: ast.Call, name: str, value) -> bool:
    return any(k.arg == name and isinstance(k.value, ast.Constant) and k.value.value is value
               for k in call.keywords)


def _wrap_sanitizer(callees: Tuple[str, ...], arg_index: int, module: str, func: str, note: str):
    """Strategy: wrap argument ``arg_index`` of the sink call in ``module.func(...)``."""
    def apply(ctx: FixContext) -> Patch:
        aliases = ctx.aliases
        for call in ctx.sink_calls():
            name = canonical(call.func, aliases)
            if callees and name not in callees and not (
                    isinstance(call.func, ast.Attribute) and call.func.attr in callees):
                continue
            if len(call.args) <= arg_index:
                continue
            arg = call.args[arg_index]
            if isinstance(arg, ast.Call) and canonical(arg.func, aliases).endswith(func):
                return _skip("the argument is already sanitised")
            prefix, need_import = _module_prefix(ctx, module)
            patched = apply_edits(ctx.source, [Edit.replace(arg, f"{prefix}.{func}({segment(ctx.source, arg)})")])
            return Patch(ensure_import(patched, module) if need_import else patched, note)
        return _skip("no matching call on the reported line")
    return apply


STRATEGIES: List[Strategy] = [
    Strategy("sql-param-qmark", "SEC005", "parameterised query with ? placeholders", _sql_fix("?")),
    Strategy("sql-param-format", "SEC005", "parameterised query with %s placeholders", _sql_fix("%s")),
    Strategy("cmd-argv-list", "SEC002", "subprocess argument list with shell=False", _cmd_argv),
    Strategy("cmd-shlex-quote", "SEC002", "shlex.quote() around untrusted parts", _cmd_shlex),
    Strategy("yaml-safe-load", "SEC010", "yaml.safe_load()", _yaml_safe),
    Strategy("hash-sha256", "SEC004", "hashlib.sha256()", _hash_sha256),
    Strategy("eval-literal-eval", "SEC001", "ast.literal_eval()", _eval_literal),
    Strategy("xxe-disable-entities", "SEC018", "external entities switched off", _xxe_disable),
    Strategy("regex-escape", "SEC024", "re.escape() around the user-supplied pattern",
             _wrap_sanitizer(("re.compile", "re.search", "re.match", "re.fullmatch", "re.findall",
                              "re.finditer", "re.sub", "re.subn", "re.split"), 0, "re", "escape",
                             "user input is escaped before it is used as a pattern")),
    Strategy("debug-off", "SEC029", "debug=False",
             _keyword_fix(lambda c, n: isinstance(c.func, ast.Attribute) and c.func.attr == "run"
                          and _is_kw(c, "debug", True), "debug", "False", "debug mode switched off")),
    Strategy("tls-verify-on", "SEC030", "verify=True",
             _keyword_fix(lambda c, n: _is_kw(c, "verify", False), "verify", "True",
                          "certificate verification switched back on")),
    Strategy("tar-data-filter", "SEC042", "extractall(..., filter='data')",
             _keyword_fix(lambda c, n: isinstance(c.func, ast.Attribute) and c.func.attr in ("extractall", "extract"),
                          "filter", '"data"', "tar members filtered with the 'data' filter")),
    Strategy("jinja-autoescape", "SEC043", "autoescape=True",
             _keyword_fix(lambda c, n: n in ("jinja2.Environment", "jinja2.environment.Environment"),
                          "autoescape", "True", "template auto-escaping switched on")),
    Strategy("cookie-secure", "SEC044", "secure=True, httponly=True",
             lambda ctx: _cookie_flags(ctx)),
]


def _cookie_flags(ctx: FixContext) -> Patch:
    for call in ctx.sink_calls():
        if isinstance(call.func, ast.Attribute) and call.func.attr == "set_cookie":
            src = ctx.source
            patched = apply_edits(src, [_set_keyword(src, call, "secure", "True")])
            call2 = next(c for c in calls_at(ast.parse(patched), ctx.finding.function, call.lineno, call.col_offset)
                         if isinstance(c.func, ast.Attribute) and c.func.attr == "set_cookie")
            patched = apply_edits(patched, [_set_keyword(patched, call2, "httponly", "True")])
            return Patch(patched, "cookie marked Secure and HttpOnly")
    return _skip("no set_cookie() call on the reported line")


def strategies_for(rule_id: str, registry: Sequence[Strategy] = STRATEGIES) -> List[Strategy]:
    return [s for s in registry if s.rule_id == rule_id]
