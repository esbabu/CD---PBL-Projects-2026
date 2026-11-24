from __future__ import annotations
import json
from typing import Callable

from ..runtime import canon


def _reductions(v, limit: int = 24) -> list:
    t = type(v)
    out: list = []
    if t is int:
        out = [x for x in (0, v // 2, v - 1 if v > 0 else v + 1) if x != v]
    elif t is float:
        out = [x for x in (0.0, float(int(v))) if x != v]
    elif t is str:
        n = len(v)
        out = ["", v[:n // 2], v[n // 2:]] + [v[:i] + v[i + 1:] for i in range(min(n, 20))]
    elif t in (list, tuple):
        n = len(v)
        items = list(v)
        cand = [[], items[:n // 2], items[n // 2:]]
        cand += [items[:i] + items[i + 1:] for i in range(min(n, 25))]
        for i in range(min(n, 8)):
            for r in _reductions(items[i], 2):
                cand.append(items[:i] + [r] + items[i + 1:])
        out = [tuple(c) if t is tuple else c for c in cand]
    elif t is set:
        out = [set(), *({x for x in v if x != y} for y in list(v)[:25])]
    elif t is dict:
        keys = list(v)
        out = [{}] + [{k: x for k, x in v.items() if k != d} for d in keys[:25]]
        for k in keys[:6]:
            for r in _reductions(v[k], 2):
                out.append({**v, k: r})
    return out[:limit * 3]


def _size(args, kwargs) -> int:
    return len(json.dumps([canon.encode(a) for a in args] + [canon.encode(kwargs)], default=str))


def shrink_args(args: list, kwargs: dict, fails: Callable[[list[tuple[list, dict]]], list[bool]],
                max_rounds: int = 25) -> tuple[list, dict]:
    """Greedy delta-debugging. `fails` evaluates a whole batch in ONE sandbox call."""
    cur_a, cur_k = args, kwargs
    for _ in range(max_rounds):
        cands: list[tuple[list, dict]] = []
        for i, a in enumerate(cur_a):
            for r in _reductions(a):
                cands.append(([*cur_a[:i], r, *cur_a[i + 1:]], cur_k))
        for k, a in cur_k.items():
            for r in _reductions(a):
                cands.append((cur_a, {**cur_k, k: r}))
        base = _size(cur_a, cur_k)
        scored = sorted(((_size(a, k), j) for j, (a, k) in enumerate(cands)))
        cands = [cands[j] for sz, j in scored if sz < base][:80]
        if not cands:
            break
        flags = fails(cands)
        pick = next((c for c, f in zip(cands, flags) if f), None)
        if pick is None:
            break
        cur_a, cur_k = pick
    return cur_a, cur_k