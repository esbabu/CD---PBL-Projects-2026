"""Phase 2 tests: C11 adapter, clang/tree-sitter facts, codegen, canaries, UB, mutator, CBMC."""
from __future__ import annotations

import random
from pathlib import Path

from optagent.complexity.schemas import AnalysisBundle
from optagent.config import Settings
from optagent.lang.native.build import build_cache_key, prepare_build_dir, resolve_compile_flags
from optagent.lang.native.cbmc import generate_cbmc_miter, run_cbmc_equivalence
from optagent.lang.native.marshal import build_signature
from optagent.lang.pipeline_hooks import propose_for_language
from optagent.lang.registry import get_adapter
from optagent.lang.treesitter import parse_source
from optagent.oracle.compare import Comparator
from optagent.oracle.schemas import Case, CaseResult, GoldenRecord
from optagent.proposers.kb.catalog import RuleCatalog
from optagent.schemas import Aspect, Constraints, IntentBundle, Level, PreservationItem, Source, Spec, ValidationReport

EXAMPLES = Path(__file__).resolve().parents[1] / "examples" / "c"


def test_c_two_sum_facts_signature_and_codegen(tmp_path):
    ad = get_adapter("c")
    src = (EXAMPLES / "two_sum.c").read_text(encoding="utf-8")
    mod = ad.analyze(src, {})
    entry = ad.select_entry(mod, None)
    assert entry == "two_sum"
    fn = mod.functions[entry]
    assert fn.max_loop_depth == 2
    assert any(p.kind == "nested_loop" for p in fn.cost_patterns)

    sig = build_signature(fn, "c", {})
    assert sig.return_type.kind == "int"
    # nums paired with n; out marked as out-param
    by_name = {b.name: b for b in sig.params}
    assert by_name["nums"].length_param == "n"
    assert by_name["n"].is_length_for == "nums"
    assert by_name["out"].is_out_param is True

    ps = ad.param_schema(fn, {}, [])
    assert ps is not None
    # Visible args: nums (list[int]), target (int)
    assert [a.kind for a in ps.args] == ["list", "int"]

    driver_path, target_path = prepare_build_dir(src, "two_sum", "c", {}, tmp_path)
    assert driver_path.exists() and target_path.exists()
    driver_src = driver_path.read_text(encoding="utf-8")
    assert '#include "target.c"' in driver_src
    assert "optagent_canary_alloc" in driver_src
    assert "optagent_canary_check" in driver_src
    assert "OPTAGENT_DO_NOT_OPTIMIZE" in driver_src
    assert "fork()" in driver_src


def test_c_examples_all_parse_and_analyze():
    ad = get_adapter("c")
    for fname, expected_fn in (
        ("two_sum.c", "two_sum"),
        ("two_sum_right.c", "two_sum"),
        ("two_sum_wrong.c", "two_sum"),
        ("sum_overflow.c", "sum_overflow"),
        ("sum_overflow_ll.c", "sum_overflow"),
        ("oob_write.c", "oob_write"),
        ("oob_write_buggy.c", "oob_write"),
        ("uninit.c", "uninit"),
    ):
        src = (EXAMPLES / fname).read_text(encoding="utf-8")
        mod = ad.analyze(src, {})
        assert expected_fn in mod.functions


def test_c_oob_and_ub_and_uninit_comparator_semantics():
    ad = get_adapter("c")
    src = (EXAMPLES / "oob_write.c").read_text(encoding="utf-8")
    mod = ad.analyze(src, {})
    contract = [r.evaluate(mod.functions["oob_write"], [], {}) for r in ad.contract_rules()]
    cmp = Comparator(contract, Constraints())

    # 1. Canary / ASan OOB write -> memory_safety violation
    case = Case.make([[1, 2, 3]])
    g = GoldenRecord(case_id=case.id, result=CaseResult(status="ok", ret=9, return_type="int"))
    c_oob = CaseResult(status="ok", ret=9, return_type="int",
                       sanitizer="Canary red-zone corrupted on parameter arr (out-of-bounds write)")
    vs = cmp.compare(case, g, c_oob)
    assert any(v.aspect == "memory_safety" for v in vs)

    # 2. Uninitialized memory case marked `unstable` -> candidate does NOT fail
    g_uninit = GoldenRecord(case_id=case.id, result=CaseResult(status="ok", ret=165, return_type="int"),
                            unstable=["ret"])
    c_any = CaseResult(status="ok", ret=90, return_type="int")
    # With unstable status, no error
    g_uninit_status = GoldenRecord(case_id=case.id, result=CaseResult(status="ok", ret=165), unstable=["status"])
    assert cmp.compare(case, g_uninit_status, c_any) == []


def test_c_treesitter_mutator_and_rules():
    ad = get_adapter("c")
    src = (EXAMPLES / "two_sum.c").read_text(encoding="utf-8")
    mops = ad.mutation_ops()
    mutants = mops.generate(src, {"two_sum"}, 25, random.Random(7))
    assert len(mutants) >= 8
    for m in mutants:
        tree, _ = parse_source(m["source"], "c")
        assert not tree.root_node.has_error

    # Rule catalog & deterministic proposer
    cat = RuleCatalog.load(ad.rule_pack().rules_yaml)
    assert len(cat.rules) >= 8
    assert ad.cost_table()["strlen"] == "O(n)"

    # Hoist strlen rule
    strlen_src = """#include <string.h>
int count_a(const char *s) {
    int c = 0;
    for (int i = 0; i < strlen(s); i++) {
        if (s[i] == 'a') c++;
    }
    return c;
}
"""
    mod_s = ad.analyze(strlen_src, {})
    intent = IntentBundle(
        language="c", source_sha="c1234567890a", source_path="count_a.c", entry_point="count_a",
        source=strlen_src, module_facts=mod_s, spec=Spec(entry_point="count_a"),
        contract=[r.evaluate(mod_s.functions["count_a"], [], {}) for r in ad.contract_rules()],
        constraints=Constraints(), golden_seed=[], validation=ValidationReport(),
    )
    analysis = AnalysisBundle(source_sha="c1234567890a", entry_point="count_a", overall_time="O(n^2)", overall_space="O(1)")
    cands = propose_for_language(intent, analysis)
    assert any(c.id == "c_rule_hoist_strlen" for c in cands)


def test_c_cbmc_miter_and_flags():
    orig = (EXAMPLES / "two_sum.c").read_text(encoding="utf-8")
    cand = (EXAMPLES / "two_sum_right.c").read_text(encoding="utf-8")
    ad = get_adapter("c")
    mod = ad.analyze(orig, {})
    sig = build_signature(mod.functions["two_sum"], "c", {})
    miter = generate_cbmc_miter(orig, cand, sig, max_array_len=6)
    assert "__CPROVER_assume" in miter
    assert "assert(r_orig == r_cand);" in miter
    assert "assert(out_orig_out[0] == out_cand_out[0]);" in miter

    # Disabled CBMC skips cleanly and records bounds
    res = run_cbmc_equivalence(orig, cand, "two_sum", language="c", unwind=12, enabled=False)
    assert res.skipped is True
    assert res.details["unwind_bound"] == 12

    # Compile flags & cache key determinism
    s = Settings()
    f_opt = resolve_compile_flags("c", s, mode="opt")
    f_san = resolve_compile_flags("c", s, mode="san")
    assert "-O2" in f_opt and "-ffp-contract=off" in f_opt
    assert "-fsanitize=address,undefined" in f_san
    assert build_cache_key(orig, "two_sum", "c", f_opt) == build_cache_key(orig, "two_sum", "c", f_opt)
