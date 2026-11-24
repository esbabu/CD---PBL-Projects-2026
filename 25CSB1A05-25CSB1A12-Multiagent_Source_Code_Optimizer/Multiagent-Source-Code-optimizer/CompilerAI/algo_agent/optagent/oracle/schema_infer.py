from __future__ import annotations
import random
from collections import Counter
from typing import Any

from pydantic import BaseModel


class VS(BaseModel):
    kind: str = "any"                    # int float bool str bytes none list tuple set dict union any
    elem: "VS | None" = None
    items: list["VS"] = []               # fixed-arity tuple
    key: "VS | None" = None
    val: "VS | None" = None
    lo: float = 0
    hi: float = 0
    min_len: int = 0
    max_len: int = 0
    alphabet: str = ""
    nullable: bool = False
    derived: bool = False                # int slot that is usually computable from the other args (e.g. a target)
    options: list["VS"] = []


VS.model_rebuild()


class ParamSchema(BaseModel):
    args: list[VS]
    kwargs: dict[str, VS] = {}


def _kind(v) -> str:
    if v is None: return "none"
    if isinstance(v, bool): return "bool"
    if isinstance(v, int): return "int"
    if isinstance(v, float): return "float"
    if isinstance(v, str): return "str"
    if isinstance(v, (bytes, bytearray)): return "bytes"
    if isinstance(v, tuple): return "tuple"
    if isinstance(v, list): return "list"
    if isinstance(v, (set, frozenset)): return "set"
    if isinstance(v, dict): return "dict"
    return "any"


def hashable(x):
    if isinstance(x, list):
        return tuple(hashable(i) for i in x)
    if isinstance(x, set):
        return frozenset(hashable(i) for i in x)
    if isinstance(x, dict):
        return tuple((hashable(k), hashable(v)) for k, v in x.items())
    return x


def infer(vals: list[Any]) -> VS:
    nullable = any(v is None for v in vals)
    vals = [v for v in vals if v is not None]
    if not vals:
        return VS(kind="none")
    kinds = sorted({_kind(v) for v in vals})
    if len(kinds) > 1:
        return VS(kind="union", nullable=nullable,
                  options=[infer([v for v in vals if _kind(v) == k]) for k in kinds])
    k = kinds[0]
    vs = VS(kind=k, nullable=nullable)
    if k in ("int", "float"):
        vs.lo, vs.hi = float(min(vals)), float(max(vals))
    elif k == "str":
        lens = [len(v) for v in vals]
        vs.min_len, vs.max_len = min(lens), max(lens)
        vs.alphabet = "".join(sorted(set("".join(vals))))[:64]
    elif k in ("list", "set", "tuple", "dict", "bytes"):
        lens = [len(v) for v in vals]
        vs.min_len, vs.max_len = min(lens), max(lens)
        if k == "dict":
            keys = [x for v in vals for x in v.keys()]
            values = [x for v in vals for x in v.values()]
            vs.key = infer(keys) if keys else VS(kind="int", lo=0, hi=9)
            vs.val = infer(values) if values else VS(kind="int", lo=0, hi=9)
        elif k == "tuple" and len(set(lens)) == 1 and lens[0] > 0:
            vs.items = [infer([v[i] for v in vals]) for i in range(lens[0])]
        elif k != "bytes":
            elems = [x for v in vals for x in v]
            vs.elem = infer(elems) if elems else VS(kind="int", lo=0, hi=9)
    return vs


def derive_ints(args: list, tail: bool = False, lens: bool = True, cap: int = 60) -> list[int]:
    """Integers an int-typed argument could 'naturally' equal: elements, pair sums, lengths."""
    nums: list[int] = []
    lns: list[int] = []
    for a in args:
        if isinstance(a, (list, tuple, set, frozenset)):
            lns.append(len(a))
            nums += [x for x in a if type(x) is int]
        elif isinstance(a, (str, dict, bytes)):
            lns.append(len(a))
    out: list[int] = []
    if tail and len(nums) >= 2:
        out.append(nums[-1] + nums[-2])
    sample = nums[:cap]
    out += sample
    for i in range(min(len(sample), 12)):
        for j in range(i + 1, min(len(sample), 12)):
            out.append(sample[i] + sample[j])
    if nums:
        out += [sum(sample), max(nums), min(nums)]
    if lens:
        out += lns + [x - 1 for x in lns if x > 0]
    return list(dict.fromkeys(out))


def infer_params(cases: list[tuple[list, dict]]) -> ParamSchema:
    arities = Counter(len(a) for a, _ in cases)
    n = arities.most_common(1)[0][0]
    use = [(a, k) for a, k in cases if len(a) == n]
    args = [infer([a[i] for a, _ in use]) for i in range(n)]
    names = set.intersection(*[set(k) for _, k in use]) if use else set()
    kwargs = {nm: infer([k[nm] for _, k in use]) for nm in sorted(names)}
    nontrivial, hits = 0, [0] * n
    for a, _ in use:
        if not any(isinstance(x, (list, tuple, set, str)) and len(x) >= 2 for x in a):
            continue
        nontrivial += 1
        pool = set(derive_ints(a, lens=False))
        for i, x in enumerate(a):
            if type(x) is int and x in pool:
                hits[i] += 1
    for i, vs in enumerate(args):
        if vs.kind == "int" and nontrivial and hits[i] >= 1 and hits[i] / nontrivial >= 0.25:
            vs.derived = True
    return ParamSchema(args=args, kwargs=kwargs)


def scalable(vs: VS) -> bool:
    return vs.kind in ("list", "str", "set", "dict", "bytes") or (vs.kind == "tuple" and not vs.items)


class Gen:
    """Seeded, schema-driven generator of python values."""

    def __init__(self, ps: ParamSchema, rng: random.Random, max_len: int = 40):
        self.ps, self.rng, self.max_len = ps, rng, max_len

    # ---- scalars ----
    def _int(self, vs: VS) -> int:
        r = self.rng
        lo, hi = int(vs.lo), int(vs.hi)
        span = max(hi - lo, 8)
        low = (0 if r.random() < 0.85 else -span // 4) if lo >= 0 else lo - span // 2
        high = hi + span // 2 + 1
        if r.random() < 0.12:
            return r.choice([lo, hi, lo - 1, hi + 1, 0, 1, -1])
        return max(-10 ** 9, min(10 ** 9, r.randint(low, high)))

    def _float(self, vs: VS) -> float:
        r = self.rng
        lo, hi = float(vs.lo), float(vs.hi)
        span = max(hi - lo, 4.0)
        if r.random() < 0.1:
            return r.choice([0.0, lo, hi, 1.0, -1.0, 0.5])
        return round(r.uniform(lo - span / 4, hi + span / 4), 3)

    def _len(self, vs: VS) -> int:
        r = self.rng
        if r.random() < 0.2 and vs.max_len >= vs.min_len:
            return min(r.randint(vs.min_len, max(vs.max_len, vs.min_len)), self.max_len)
        return min(r.choice([0, 1, 2, 3, 4, 5, 6, 8, 10, 13, 17, 25, 34]), self.max_len)

    def _str(self, L: int, alphabet: str, fam: str) -> str:
        r = self.rng
        alphabet = alphabet or "abc"
        if fam == "all_equal":
            return r.choice(alphabet) * L
        if fam == "few_unique":
            sub = "".join(r.sample(alphabet, min(2, len(alphabet))))
            return "".join(r.choice(sub) for _ in range(L))
        s = [r.choice(alphabet) for _ in range(L)]
        if fam == "sorted":
            s.sort()
        elif fam == "reversed":
            s.sort(reverse=True)
        return "".join(s)

    def _shape(self, elems: list, fam: str) -> list:
        r = self.rng
        if not elems or fam == "random":
            return elems
        try:
            if fam == "sorted":
                return sorted(elems)
            if fam == "reversed":
                return sorted(elems, reverse=True)
        except TypeError:
            return elems
        if fam == "all_equal":
            return [elems[0]] * len(elems)
        if fam == "few_unique":
            pool = elems[:3]
            return [r.choice(pool) for _ in elems]
        return elems

    # ---- recursive ----
    def value(self, vs: VS, n: int | None = None, fam: str = "random", d: int = 0) -> Any:
        r = self.rng
        if d > 4:
            return None
        if vs.nullable and r.random() < 0.06:
            return None
        k = vs.kind
        if k == "none": return None
        if k == "bool": return r.random() < 0.5
        if k == "int": return self._int(vs)
        if k == "float": return self._float(vs)
        if k == "str":
            return self._str(n if n is not None else self._len(vs), vs.alphabet, fam)
        if k == "bytes":
            return bytes(r.randint(0, 255) for _ in range(n if n is not None else self._len(vs)))
        if k in ("list", "set", "tuple") and not (k == "tuple" and vs.items):
            L = n if n is not None else self._len(vs)
            ev = vs.elem or VS(kind="int", lo=0, hi=9)
            elems = self._shape([self.value(ev, None, "random", d + 1) for _ in range(L)], fam)
            if k == "set":
                return {hashable(x) for x in elems}
            return tuple(elems) if k == "tuple" else elems
        if k == "tuple":
            return tuple(self.value(i, None, "random", d + 1) for i in vs.items)
        if k == "dict":
            L = n if n is not None else self._len(vs)
            kv, vv = vs.key or VS(kind="int", lo=0, hi=9), vs.val or VS(kind="int", lo=0, hi=9)
            return {hashable(self.value(kv, None, "random", d + 1)): self.value(vv, None, "random", d + 1)
                    for _ in range(L)}
        if k == "union":
            return self.value(r.choice(vs.options), n, fam, d + 1)
        return r.randint(-5, 5)

    # ---- whole calls ----
    def _relate(self, args: list, mode: str) -> None:
        r = self.rng
        for i, vs in enumerate(self.ps.args):
            if vs.kind != "int" or not vs.derived or i >= len(args):
                continue
            if mode == "hit":
                c = derive_ints(args, tail=True, lens=False)
                if c:
                    args[i] = c[0]
            elif mode == "miss":
                nums = [abs(x) for a in args if isinstance(a, (list, tuple, set)) for x in a if type(x) is int]
                args[i] = (max(nums) * 2 if nums else 10 ** 6) + 1000003
            elif mode == "mixed" and r.random() < 0.5:
                c = derive_ints(args, lens=False)
                if c:
                    args[i] = r.choice(c)

    def case(self, family: str = "random") -> tuple[list, dict]:
        args = [self.value(vs, None, family) for vs in self.ps.args]
        kwargs = {k: self.value(vs, None, family) for k, vs in self.ps.kwargs.items()}
        self._relate(args, "mixed")
        return args, kwargs

    def scaled(self, family: str, n: int, mode: str) -> tuple[list, dict]:
        has_coll = any(scalable(v) for v in self.ps.args)
        args = []
        for vs in self.ps.args:
            if scalable(vs):
                args.append(self.value(vs, n=n, fam=family))
            elif vs.kind == "int" and not has_coll:
                args.append(n)                       # e.g. fib(n): the int IS the size
            else:
                args.append(self.value(vs))
        kwargs = {k: self.value(vs) for k, vs in self.ps.kwargs.items()}
        self._relate(args, mode)
        return args, kwargs