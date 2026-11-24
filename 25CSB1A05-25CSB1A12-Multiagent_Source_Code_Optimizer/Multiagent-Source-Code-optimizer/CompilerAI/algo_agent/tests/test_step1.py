from pathlib import Path

from optagent.analysis.static_facts import analyze_source
from optagent.config import Settings
from optagent.runtime import canon
from optagent.runtime.executor import Executor

DR = (Path(__file__).parent.parent / "examples" / "dedupe_rank.py").read_text()


def test_static_detects_mutation_and_patterns():
    f = analyze_source(DR).functions["dedupe_rank"]
    assert f.mutated_params == ["words"]
    kinds = {p.kind for p in f.cost_patterns}
    assert "linear_membership" in kinds
    assert any(s.kind == "list.sort" and "key=True" in s.detail for s in f.sort_uses)


def test_interprocedural_mutation():
    src = "def helper(x):\n    x.append(1)\n\ndef main(a):\n    helper(a)\n    return len(a)\n"
    m = analyze_source(src)
    assert m.functions["main"].mutated_params == ["a"]
    assert m.root_functions == ["main"]


def test_global_cache_is_flagged():
    src = "_c = {}\ndef f(n):\n    _c[n] = n\n    return n\n"
    f = analyze_source(src).functions["f"]
    assert any(e.kind.value == "global_write" for e in f.effects)


def test_canon_roundtrip():
    v = {"a": (1, 2.5), "b": {3, 4}, "c": float("nan")}
    back = canon.decode(canon.encode(v))
    assert back["a"] == (1, 2.5) and back["b"] == {3, 4} and back["c"] != back["c"]


def test_executor_records_mutation_and_exception(tmp_path):
    p = tmp_path / "m.py"
    p.write_text(DR)
    ex = Executor(Settings())
    r = ex.run_case(p, "dedupe_rank", [["a", "b", "a"], 1], {}, "user")
    assert r.status == "ok" and r.mutated_args == ["arg0"]
    r2 = ex.run_case(p, "dedupe_rank", [None, 1], {}, "user")
    assert r2.status == "exception" and r2.exc_type == "TypeError"


def test_hash_order_nondeterminism_detected(tmp_path):
    p = tmp_path / "s.py"
    p.write_text("def f(xs):\n    return list(set(xs))\n")
    words = [f"w{i}" for i in range(15)]
    r = Executor(Settings()).run_case(p, "f", [words], {}, "user")
    assert "return" in r.nondeterministic_fields