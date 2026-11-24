"""Phase 1 tests: JavaScript adapter, facts, JSDoc schema, mutator, rules, and examples."""
from __future__ import annotations

import random
import shutil
from pathlib import Path

import pytest

from optagent.complexity.schemas import AnalysisBundle
from optagent.config import Settings
from optagent.lang.pipeline_hooks import propose_for_language
from optagent.lang.registry import get_adapter
from optagent.lang.treesitter import SourceEditor, parse_source
from optagent.oracle.compare import Comparator
from optagent.oracle.schemas import Case, CaseResult, GoldenRecord
from optagent.proposers.kb.catalog import RuleCatalog
from optagent.schemas import Aspect, Constraints, IntentBundle, Level, PreservationItem, Source, Spec, ValidationReport

EXAMPLES = Path(__file__).resolve().parents[1] / "examples" / "js"


def test_js_two_sum_static_facts_and_schema():
    ad = get_adapter("javascript")
    src = (EXAMPLES / "two_sum.js").read_text(encoding="utf-8")
    mod = ad.analyze(src, {})
    entry = ad.select_entry(mod, None)
    assert entry == "two_sum"
    fn = mod.functions[entry]
    assert [p.name for p in fn.params] == ["nums", "target"]
    assert fn.max_loop_depth == 2
    assert any(p.kind == "nested_loop" for p in fn.cost_patterns)

    # JSDoc-derived ParamSchema
    ps = ad.param_schema(fn, {}, [])
    assert ps is not None
    assert [a.kind for a in ps.args] == ["list", "int"]

    # Executable lines
    lines, reach = ad.executable_lines(src, mod, entry)
    assert "two_sum" in reach
    assert len(lines) >= 3


def test_js_dedupe_rank_facts_mutations_and_contract():
    ad = get_adapter("javascript")
    src = (EXAMPLES / "dedupe_rank.js").read_text(encoding="utf-8")
    mod = ad.analyze(src, {})
    fn = mod.functions["dedupe_rank"]
    assert "words" in fn.mutated_params
    assert any(p.kind == "linear_membership" for p in fn.cost_patterns)
    assert len(fn.sort_uses) == 1

    rules = {r.aspect: r for r in ad.contract_rules()}
    assert Aspect.KEY_ENUMERATION_ORDER in rules
    assert Aspect.PROTOTYPE_STATE in rules
    assert Aspect.ASYNC_SEMANTICS in rules
    assert Aspect.SORT_STABILITY in rules


def test_js_treesitter_mutator_generates_valid_mutants():
    ad = get_adapter("javascript")
    src = (EXAMPLES / "two_sum.js").read_text(encoding="utf-8")
    mops = ad.mutation_ops()
    assert mops.generate is not None
    mutants = mops.generate(src, {"two_sum"}, 25, random.Random(42))
    assert len(mutants) >= 8
    ops = {m["op"] for m in mutants}
    assert "compare" in ops
    for m in mutants:
        tree, _ = parse_source(m["source"], "javascript")
        assert not tree.root_node.has_error


def test_js_source_editor_byte_ranges():
    src = "function f(a, b) { return a + b; }\n"
    idx = src.index("+")
    edited = SourceEditor(src).replace(idx, idx + 1, "-").apply()
    assert edited == "function f(a, b) { return a - b; }\n"


def test_js_rule_catalog_respects_key_enumeration_order():
    ad = get_adapter("javascript")
    pack = ad.rule_pack()
    cat = RuleCatalog.load(pack.rules_yaml)
    assert len(cat.rules) >= 8

    # When key_enumeration_order is MUST, rules breaking it are filtered out
    contract_strict = [
        PreservationItem(aspect=Aspect.KEY_ENUMERATION_ORDER, level=Level.MUST, applicable=True, rationale="", source=Source.DEFAULT)
    ]
    applicable = cat.filter_applicable(contract_strict, Constraints(), [])
    ids = {r.id for r in applicable}
    assert "js_object_to_map_counts" not in ids
    assert "js_map_to_object" not in ids
    assert "js_list_to_set_includes" in ids


def test_js_proposers_generate_valid_candidates():
    ad = get_adapter("javascript")
    for fname, expected_id in (("two_sum.js", "js_rule_nested_map_bsearch"),
                               ("dedupe_rank.js", "js_rule_list_to_set_includes")):
        src = (EXAMPLES / fname).read_text(encoding="utf-8")
        mod = ad.analyze(src, {})
        entry = ad.select_entry(mod, None)
        intent = IntentBundle(
            language="javascript",
            source_sha="abc123456789",
            source_path=fname,
            entry_point=entry,
            source=src,
            module_facts=mod,
            spec=Spec(entry_point=entry),
            contract=[r.evaluate(mod.functions[entry], [], {}) for r in ad.contract_rules()],
            constraints=Constraints(),
            golden_seed=[],
            validation=ValidationReport(),
        )
        analysis = AnalysisBundle(source_sha="abc123456789", entry_point=entry, overall_time="O(n^2)", overall_space="O(n)")
        cands = propose_for_language(intent, analysis)
        assert any(c.id == expected_id for c in cands)
        for c in cands:
            tree, _ = parse_source(c.source, "javascript")
            assert not tree.root_node.has_error


def test_js_cost_table_and_profiles():
    ad = get_adapter("javascript")
    costs = ad.cost_table()
    assert costs["Array.prototype.includes"] == "O(n)"
    assert costs["Array.prototype.sort"] == "O(n log n)"
    assert costs["Set.prototype.has"] == "O(1)"
    assert ad.bench_profile().gc_between_reps is True
    assert "fs" in ad.security_profile()["forbidden_modules"]


@pytest.mark.skipif(shutil.which("node") is None, reason="Node.js 22 not installed on host PATH")
def test_js_live_sandbox_two_sum_right_and_wrong(tmp_path):
    """End-to-end live Node execution: right passes, wrong fails on [1, 1, 2], 3."""
    from optagent.runtime.sandbox import RunOpts, Sandbox
    ad = get_adapter("javascript")
    sb = Sandbox(Settings(sandbox_backend="local"), backend="local", profile=ad.sandbox_profile({}))
    cases = [
        Case.make([[2, 7, 11, 15], 9]),
        Case.make([[1, 1, 2], 3]),
        Case.make([[], 5]),
    ]
    orig = sb.run(EXAMPLES / "two_sum.js", "two_sum", cases, RunOpts(hashseed=0, cov=True))
    right = sb.run(EXAMPLES / "two_sum_right.js", "two_sum", cases, RunOpts(hashseed=0))
    wrong = sb.run(EXAMPLES / "two_sum_wrong.js", "two_sum", cases, RunOpts(hashseed=0))

    assert [r.ret for r in orig] == [[0, 1], [0, 2], []]
    assert [r.ret for r in right] == [[0, 1], [0, 2], []]
    assert wrong[1].ret == [1, 2]  # caught difference on 3-element input [1, 1, 2], 3
