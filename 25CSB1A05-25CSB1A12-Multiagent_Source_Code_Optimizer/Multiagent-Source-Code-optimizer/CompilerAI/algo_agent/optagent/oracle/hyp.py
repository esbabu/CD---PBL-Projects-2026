from __future__ import annotations

from hypothesis import HealthCheck, Phase, given, seed as hseed, settings
from hypothesis import strategies as st

from .schema_infer import ParamSchema, VS

_HASHABLE = {"int", "str", "float", "bool", "tuple"}


def _strategy(vs: VS, max_len: int):
    k = vs.kind
    if k == "bool":
        s = st.booleans()
    elif k == "int":
        lo, hi = int(vs.lo), int(vs.hi)
        span = max(hi - lo, 8)
        s = st.integers(min_value=0 if lo >= 0 else lo - span // 2, max_value=hi + span // 2 + 1)
    elif k == "float":
        s = st.floats(min_value=min(vs.lo, 0) - 10, max_value=max(vs.hi, 0) + 10,
                      allow_nan=False, allow_infinity=False)
    elif k == "str":
        s = st.text(alphabet=vs.alphabet or "abc", max_size=max_len)
    elif k == "bytes":
        s = st.binary(max_size=max_len)
    elif k == "none":
        s = st.none()
    elif k in ("list", "set") or (k == "tuple" and not vs.items):
        ev = vs.elem or VS(kind="int", lo=0, hi=9)
        inner = _strategy(ev, max_len)
        if k == "set":
            inner = inner if ev.kind in _HASHABLE else st.just(0)
            s = st.sets(inner, max_size=max_len)
        elif k == "tuple":
            s = st.lists(inner, max_size=max_len).map(tuple)
        else:
            s = st.lists(inner, max_size=max_len)
    elif k == "tuple":
        s = st.tuples(*[_strategy(i, max_len) for i in vs.items])
    elif k == "dict":
        kv, vv = vs.key or VS(kind="int"), vs.val or VS(kind="int")
        ks = _strategy(kv, max_len) if kv.kind in _HASHABLE else st.integers(0, 20)
        s = st.dictionaries(ks, _strategy(vv, max_len), max_size=max_len)
    elif k == "union":
        s = st.one_of(*[_strategy(o, max_len) for o in vs.options])
    else:
        s = st.integers(-5, 5)
    return st.one_of(st.none(), s) if vs.nullable else s


def hypothesis_inputs(ps: ParamSchema, n: int, seed: int, max_len: int = 40) -> list[tuple[list, dict]]:
    """Generate-only use of Hypothesis: returns up to n structured examples, reproducibly."""
    arg_s = [_strategy(v, max_len) for v in ps.args]
    names = sorted(ps.kwargs)
    kw_s = [_strategy(ps.kwargs[k], max_len) for k in names]
    top = st.tuples(st.tuples(*arg_s), st.tuples(*kw_s))
    out: list[tuple[list, dict]] = []

    @settings(max_examples=n, database=None, deadline=None, phases=[Phase.generate],
              suppress_health_check=list(HealthCheck))
    @hseed(seed)
    @given(top)
    def collect(x):
        a, k = x
        out.append((list(a), dict(zip(names, k))))

    collect()
    return out