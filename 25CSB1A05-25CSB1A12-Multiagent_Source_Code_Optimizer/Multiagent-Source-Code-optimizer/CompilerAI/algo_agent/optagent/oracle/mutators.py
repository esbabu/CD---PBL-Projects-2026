from __future__ import annotations
import ast
import copy
import random
from dataclasses import dataclass, field

from .schema_infer import Gen, VS, derive_ints, hashable

BOUNDARY = [0, 1, -1, 2, -2, 7, 10, 100, 255, 256, 1000, 2 ** 15, 2 ** 31 - 1, -2 ** 31]
CAP = 2 ** 40


@dataclass
class Pool:
    ints: list[int] = field(default_factory=list)
    strs: list[str] = field(default_factory=list)


@dataclass
class MutCtx:
    gen: Gen
    pool: Pool
    max_len: int = 40

    @property
    def ps(self):
        return self.gen.ps


def _walk(v, ints: set, strs: set, d: int = 0) -> None:
    if d > 3:
        return
    if type(v) is int and abs(v) < 10 ** 9:
        ints.add(v)
    elif isinstance(v, str) and 0 < len(v) <= 12:
        strs.add(v)
    elif isinstance(v, (list, tuple, set, frozenset)):
        for x in list(v)[:30]:
            _walk(x, ints, strs, d + 1)
    elif isinstance(v, dict):
        for k, x in list(v.items())[:30]:
            _walk(k, ints, strs, d + 1)
            _walk(x, ints, strs, d + 1)


def build_pool(source: str, cases_py: list[tuple[list, dict]]) -> Pool:
    """Dictionary of interesting constants: literals from the source + values seen in inputs."""
    import re
    ints: set[int] = set()
    strs: set[str] = set()
    try:
        for n in ast.walk(ast.parse(source)):
            if isinstance(n, ast.Constant):
                if type(n.value) is int and abs(n.value) < 10 ** 9:
                    ints |= {n.value, n.value + 1, n.value - 1}
                elif isinstance(n.value, str) and 0 < len(n.value) <= 12:
                    strs.add(n.value)
    except SyntaxError:
        # Non-Python source (JS/C/C++): extract integer and short string literals via regex
        for m in re.finditer(r"(?<![\w.])(-?\d+)(?![\w.])", source):
            val = int(m.group(1))
            if abs(val) < 10 ** 9:
                ints |= {val, val + 1, val - 1}
        for m in re.finditer(r'["\']([^"\'\\]{1,12})["\']', source):
            strs.add(m.group(1))
    for a, k in cases_py:
        for v in list(a) + list(k.values()):
            _walk(v, ints, strs)
    return Pool(sorted(ints)[:200], sorted(strs)[:100])


def _clamp(x: int) -> int:
    return max(-CAP, min(CAP, x))


def _m_int(v: int, rng: random.Random, ctx: MutCtx) -> int:
    ops = [lambda: v + 1, lambda: v - 1, lambda: -v, lambda: v * 2, lambda: v // 2,
           lambda: 0, lambda: rng.choice(BOUNDARY), lambda: v + rng.randint(-10, 10)]
    if ctx.pool.ints:
        ops += [lambda: rng.choice(ctx.pool.ints)] * 2
    return _clamp(rng.choice(ops)())


def _m_float(v: float, rng: random.Random) -> float:
    return rng.choice([v + 1.0, v - 1.0, -v, v * 2, v / 2, 0.0, round(v), v + 0.5, 1.0, -1.0])


def _m_str(v: str, rng: random.Random, vs, ctx: MutCtx) -> str:
    alpha = list(set(v)) or list(getattr(vs, "alphabet", "") or "ab")
    s = list(v)
    op = rng.choice(["insert", "delete", "swap", "dup", "replace", "splice", "reverse", "sort", "trunc", "empty"])
    if op == "insert" and len(s) < ctx.max_len * 2:
        s.insert(rng.randint(0, len(s)), rng.choice(alpha))
    elif op == "delete" and s:
        s.pop(rng.randrange(len(s)))
    elif op == "swap" and len(s) >= 2:
        i = rng.randrange(len(s) - 1)
        s[i], s[i + 1] = s[i + 1], s[i]
    elif op == "dup" and s and len(s) < ctx.max_len * 2:
        i = rng.randrange(len(s))
        s.insert(i, s[i])
    elif op == "replace" and s:
        s[rng.randrange(len(s))] = rng.choice(alpha)
    elif op == "splice" and ctx.pool.strs:
        s = s[:rng.randint(0, len(s))] + list(rng.choice(ctx.pool.strs)) + s[rng.randint(0, len(s)):]
    elif op == "reverse":
        s.reverse()
    elif op == "sort":
        s.sort()
    elif op == "trunc":
        s = s[:rng.randint(0, len(s))]
    elif op == "empty":
        s = []
    return "".join(s)[:ctx.max_len * 2]


def _new_elem(vs, sib: list, rng: random.Random, ctx: MutCtx, d: int):
    r = rng.random()
    if sib and r < 0.45:
        return mutate_value(copy.deepcopy(rng.choice(sib)), vs, rng, ctx, d + 1)
    if sib and r < 0.65:
        return copy.deepcopy(rng.choice(sib))          # duplicates -> ties
    if vs is not None:
        return ctx.gen.value(vs)
    return rng.choice(ctx.pool.ints) if ctx.pool.ints else 0


def _m_seq(v, vs, rng: random.Random, ctx: MutCtx, d: int) -> list:
    items = list(v)
    n = len(items)
    evs = vs.elem if (vs is not None and vs.kind in ("list", "set", "tuple")) else None
    op = rng.choice(["insert", "insert", "delete", "swap", "dup", "mutate", "mutate", "mutate",
                     "reverse", "sort", "truncate", "grow", "equalize"])
    if n == 0 and op not in ("insert", "grow"):
        op = "insert"
    if op in ("insert", "grow"):
        for _ in range(1 if op == "insert" else rng.randint(2, 8)):
            if len(items) < ctx.max_len:
                items.insert(rng.randint(0, len(items)), _new_elem(evs, items, rng, ctx, d))
    elif op == "delete":
        items.pop(rng.randrange(n))
    elif op == "swap" and n >= 2:
        i, j = rng.sample(range(n), 2)
        items[i], items[j] = items[j], items[i]
    elif op == "dup" and n < ctx.max_len:
        i = rng.randrange(n)
        items.insert(i, copy.deepcopy(items[i]))
    elif op == "mutate":
        i = rng.randrange(n)
        items[i] = mutate_value(items[i], evs, rng, ctx, d + 1)
    elif op == "reverse":
        items.reverse()
    elif op == "sort":
        try:
            items.sort()
        except TypeError:
            pass
    elif op == "truncate":
        items = items[:rng.randint(0, n)]
    elif op == "equalize":
        x = items[rng.randrange(n)]
        items = [copy.deepcopy(x) for _ in items]
    return items


def _m_dict(v: dict, vs, rng: random.Random, ctx: MutCtx, d: int) -> dict:
    out = dict(v)
    kvs = vs.key if vs is not None else None
    vvs = vs.val if vs is not None else None
    keys = list(out)
    op = rng.choice(["mutate", "mutate", "add", "delete", "swap"])
    if not keys or op == "add":
        if len(out) < ctx.max_len:
            out[hashable(_new_elem(kvs, keys, rng, ctx, d))] = _new_elem(vvs, list(out.values()), rng, ctx, d)
    elif op == "delete":
        del out[rng.choice(keys)]
    elif op == "swap" and len(keys) >= 2:
        a, b = rng.sample(keys, 2)
        out[a], out[b] = out[b], out[a]
    else:
        k = rng.choice(keys)
        out[k] = mutate_value(out[k], vvs, rng, ctx, d + 1)
    return out


def mutate_value(v, vs, rng: random.Random, ctx: MutCtx, d: int = 0):
    if d > 4 or v is None:
        return v
    t = type(v)
    try:
        if t is bool: return not v
        if t is int: return _m_int(v, rng, ctx)
        if t is float: return _m_float(v, rng)
        if t is str: return _m_str(v, rng, vs, ctx)
        if t is list: return _m_seq(v, vs, rng, ctx, d)
        if t is tuple:
            if vs is not None and vs.items and len(vs.items) == len(v):
                i = rng.randrange(len(v))
                lst = list(v)
                lst[i] = mutate_value(lst[i], vs.items[i], rng, ctx, d + 1)
                return tuple(lst)
            return tuple(_m_seq(v, vs, rng, ctx, d))
        if t is set:
            return {hashable(x) for x in _m_seq(list(v), vs, rng, ctx, d)}
        if t is dict: return _m_dict(v, vs, rng, ctx, d)
    except Exception:
        return v
    return v


def _confusion(rng: random.Random):
    return rng.choice([None, "", [], 0, -1, "x", 1.5, {}, (1, 2), [None], [[]], True])


def mutate_args(args: list, kwargs: dict, rng: random.Random, ctx: MutCtx, probe: bool = False,
                force_probe: bool = False, others: list | None = None) -> tuple[list, dict]:
    args, kwargs = copy.deepcopy(args), copy.deepcopy(kwargs)
    slots = [("a", i) for i in range(len(args))] + [("k", k) for k in kwargs]
    if not slots:
        return args, kwargs
    for _ in range(rng.choice([1, 1, 1, 2, 2, 3, 4])):
        kind, key = rng.choice(slots)
        cur = args[key] if kind == "a" else kwargs[key]
        vs = (ctx.ps.args[key] if key < len(ctx.ps.args) else None) if kind == "a" else ctx.ps.kwargs.get(key)
        if force_probe or (probe and rng.random() < 0.05):
            new = _confusion(rng)
        elif others and rng.random() < 0.12:
            oa, ok_ = rng.choice(others)
            src = oa if kind == "a" else ok_
            new = copy.deepcopy(src[key]) if (kind == "a" and key < len(oa)) or (kind == "k" and key in ok_) else cur
        else:
            new = mutate_value(cur, vs, rng, ctx, 0)
        if kind == "a":
            args[key] = new
        else:
            kwargs[key] = new
    if rng.random() < 0.3:
        c = derive_ints(args)
        for i, x in enumerate(args):
            if type(x) is int and c and rng.random() < 0.5:
                args[i] = rng.choice(c)
    return args, kwargs