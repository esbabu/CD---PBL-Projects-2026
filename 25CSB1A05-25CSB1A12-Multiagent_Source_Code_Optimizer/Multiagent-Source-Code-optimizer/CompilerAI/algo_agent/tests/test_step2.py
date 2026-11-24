import ast
import random
from pathlib import Path

import pytest

from optagent.config import Settings
from optagent.intent.pipeline import IntentExtractor
from optagent.oracle.builder import OracleBuilder
from optagent.oracle.mutation import MutationTester
from optagent.oracle.oracle import Oracle
from optagent.oracle.schema_infer import infer_params
from optagent.oracle.schemas import Case, split_of
from optagent.runtime import canon
from optagent.runtime.sandbox import Sandbox

EX = Path(__file__).parent.parent / "examples"


def fast_settings(tmp_path, **kw):
    base = dict(sandbox_backend="local", runs_dir=str(tmp_path / "runs"), n_family=60, n_hypothesis=60,
                n_probe=10, fuzz_budget_s=10.0, fuzz_max_rounds=6, max_mutants=25, workers=2,
                hunt_max_survivors=4, hunt_inputs_per_survivor=128, scale_sizes=(10, 100, 1000),
                scale_budget_s=1.0, case_timeout_s=2.0)
    base.update(kw)
    return Settings(**base)


def test_case_ids_are_stable_and_split_is_deterministic():
    a, b = Case.make([[1, 2], 3]), Case.make([[1, 2], 3])
    assert a.id == b.id
    assert split_of(Case.make([[1], 2], origin="user"), 30) == "visible"
    assert split_of(a.model_copy(update={"origin": "family"}), 30) == split_of(a.model_copy(update={"origin": "family"}), 30)


def test_digest_multiset():
    a, b = canon.encode([3, 1, 2]), canon.encode([1, 2, 3])
    assert canon.digest(a) != canon.digest(b)
    assert canon.digest(a, True) == canon.digest(b, True)


def test_derived_target_detected():
    data = [([[1, 2, 3], 5], {}), ([[4, 5], 9], {}), ([[2, 2, 7], 4], {}), ([[1, 5, 9], 14], {})]
    ps = infer_params(data)
    assert ps.args[0].kind == "list" and ps.args[1].kind == "int" and ps.args[1].derived


def test_sandbox_timeout_and_recovery(tmp_path):
    p = tmp_path / "f.py"
    p.write_text("def f(x):\n    while x == 1:\n        pass\n    return x\n")
    sb = Sandbox(fast_settings(tmp_path, case_timeout_s=1.0))
    res = sb.run_batch(p, "f", [Case.make([x]) for x in (0, 1, 2)])
    assert [r.status for r in res] == ["ok", "timeout", "ok"]


def test_mutants_compile_and_differ(tmp_path):
    src = (EX / "slow_two_sum.py").read_text()
    ms = MutationTester(None, fast_settings(tmp_path), None).generate(src, {"two_sum"}, random.Random(1))
    assert len(ms) >= 8
    base = ast.unparse(ast.parse(src))
    for m in ms:
        compile(m["source"], "m", "exec")
        assert m["source"] != base
    assert {"compare", "arith", "range-bound"} <= {m["op"] for m in ms}


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("oracle")
    s = fast_settings(tmp)
    intent = IntentExtractor(s, use_llm=False).run((EX / "slow_two_sum.py").read_text(),
                                                    source_name="slow_two_sum.py")
    bundle = OracleBuilder(s, use_llm=False, log=lambda *a, **k: None).build(intent)
    return Oracle(bundle, s), bundle


def test_oracle_strength(built):
    _, b = built
    assert b.strength.line_coverage >= 0.9
    assert b.strength.n_holdout > 0
    assert b.mutation is not None and b.mutation.score >= 0.5      # loose bound: tier is reported, not asserted
    assert b.scaling


def test_right_candidate_passes(built):
    oracle, _ = built
    v = oracle.check((EX / "fast_two_sum_right.py").read_text(), fresh=100, scale=True)
    assert v.passed, v.feedback
    assert v.scale and all(r["match"] for r in v.scale)


def test_wrong_candidate_is_caught_and_shrunk(built):
    oracle, _ = built
    v = oracle.check((EX / "fast_two_sum_wrong.py").read_text(), fresh=150)
    assert not v.passed
    ce = v.counterexamples[0]
    assert ce.violations[0].aspect == "return_value"
    args = ce.shrunk_args or ce.args
    assert len(args[0]) <= 8
    assert "Counterexample 1" in v.feedback


def test_syntax_error_and_missing_entry(built):
    oracle, _ = built
    assert not oracle.check("def two_sum(:").passed
    assert "two_sum" in oracle.check("def other(x):\n    return x\n").feedback