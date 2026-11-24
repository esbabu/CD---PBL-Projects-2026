"""Phase 3 tests: C++17 adapter, STL marshalling, exceptions, normalization, rules, mutator."""
from __future__ import annotations

import random
from pathlib import Path

from optagent.complexity.schemas import AnalysisBundle
from optagent.lang.native.adapter_cpp import normalize_unordered_value
from optagent.lang.native.build import prepare_build_dir
from optagent.lang.native.marshal import build_signature, parse_native_type
from optagent.lang.pipeline_hooks import propose_for_language
from optagent.lang.registry import get_adapter
from optagent.lang.treesitter import parse_source
from optagent.oracle.compare import Comparator
from optagent.oracle.schemas import Case, CaseResult, GoldenRecord
from optagent.proposers.kb.catalog import RuleCatalog
from optagent.schemas import Aspect, Constraints, IntentBundle, Level, PreservationItem, Source, Spec, ValidationReport

EXAMPLES = Path(__file__).resolve().parents[1] / "examples" / "cpp"


def test_cpp_stl_type_parsing():
    t_vec = parse_native_type("std::vector<std::string>&", "cpp")
    assert t_vec.kind == "vector" and t_vec.is_ref is True and t_vec.elem.kind == "string"

    t_umap = parse_native_type("std::unordered_map<std::string, int>", "cpp")
    assert t_umap.kind == "umap" and t_umap.elem.kind == "string" and t_umap.val_type.kind == "int"

    t_opt = parse_native_type("std::optional<double>", "cpp")
    assert t_opt.kind == "optional" and t_opt.elem.kind == "float"

    t_pair = parse_native_type("std::pair<int, std::string>", "cpp")
    assert t_pair.kind == "pair" and t_pair.elem.kind == "int" and t_pair.val_type.kind == "string"

    t_rval = parse_native_type("std::vector<int>&&", "cpp")
    assert t_rval.kind == "vector" and t_rval.is_rvalue_ref is True


def test_cpp_dedupe_rank_facts_contract_and_codegen(tmp_path):
    ad = get_adapter("cpp")
    src = (EXAMPLES / "dedupe_rank.cpp").read_text(encoding="utf-8")
    mod = ad.analyze(src, {})
    entry = ad.select_entry(mod, None)
    assert entry == "dedupe_rank"
    fn = mod.functions[entry]

    assert "words" in fn.mutated_params
    assert "std::out_of_range" in fn.implicit_raises
    assert any(s.kind == "stable_sort" for s in fn.sort_uses)
    assert any(p.kind == "linear_membership" for p in fn.cost_patterns)

    # Contract rules: sort_stability is MUST & applicable because std::stable_sort is used
    contract = [r.evaluate(fn, [], {}) for r in ad.contract_rules()]
    by_aspect = {c.aspect: c for c in contract}
    assert by_aspect[Aspect.SORT_STABILITY].level == Level.MUST
    assert by_aspect[Aspect.SORT_STABILITY].applicable is True

    # Rule catalog blocks swapping stable_sort -> std::sort when sort_stability is MUST
    cat = RuleCatalog.load(ad.rule_pack().rules_yaml)
    applicable = cat.filter_applicable(contract, Constraints(), [])
    ids = {r.id for r in applicable}
    assert "cpp_stable_to_unstable_sort" not in ids
    assert "cpp_linear_find_to_unordered_set" in ids

    # Driver C++ codegen includes STL marshalling and exception demangling
    driver_path, _ = prepare_build_dir(src, "dedupe_rank", "cpp", {}, tmp_path)
    dsrc = driver_path.read_text(encoding="utf-8")
    assert '#include "target.cpp"' in dsrc
    assert "abi::__cxa_demangle" in dsrc
    assert "catch (const std::exception &e)" in dsrc
    assert "<non-std>" in dsrc


def test_cpp_unordered_normalization_no_violation():
    """Section 13: unordered_map return with different iteration order -> NO violation after normalize_result."""
    ad = get_adapter("cpp")
    r_orig = ad.normalize_result(CaseResult(
        status="ok",
        ret={"__udict__": [["zebra", 1], ["apple", 3], ["mango", 2]]},
        return_type="std::unordered_map<std::string, int>",
    ))
    r_cand = ad.normalize_result(CaseResult(
        status="ok",
        ret={"__udict__": [["mango", 2], ["zebra", 1], ["apple", 3]]},
        return_type="std::unordered_map<std::string, int>",
    ))
    assert r_orig.ret == {"__dict__": [["apple", 3], ["mango", 2], ["zebra", 1]]}
    assert r_cand.ret == r_orig.ret

    contract = [
        PreservationItem(aspect=Aspect.RETURN_VALUE, level=Level.MUST, applicable=True, rationale="", source=Source.DEFAULT),
        PreservationItem(aspect=Aspect.RETURN_ORDER, level=Level.MUST, applicable=True, rationale="", source=Source.DEFAULT),
    ]
    cmp = Comparator(contract, Constraints())
    case = Case.make([["zebra", "apple", "mango"]])
    g = GoldenRecord(case_id=case.id, result=r_orig)
    assert cmp.compare(case, g, r_cand) == []

    # Also verify __uset__ -> sorted __set__
    assert normalize_unordered_value({"__uset__": [3, 1, 2]}) == {"__set__": [1, 2, 3]}


def test_cpp_exception_type_violation_caught():
    """Replacing .at() with operator[] drops std::out_of_range -> caught by Comparator."""
    contract = [
        PreservationItem(aspect=Aspect.RETURN_VALUE, level=Level.MUST, applicable=True, rationale="", source=Source.DEFAULT),
        PreservationItem(aspect=Aspect.EXCEPTION_TYPE, level=Level.MUST, applicable=True, rationale="", source=Source.DEFAULT),
    ]
    cmp = Comparator(contract, Constraints())
    case = Case.make([["a"], 50])
    g = GoldenRecord(
        case_id=case.id,
        result=CaseResult(status="exception", exc_type="std::out_of_range", exc_msg="vector::_M_range_check"),
    )
    c_no_throw = CaseResult(status="ok", ret=["a"], return_type="std::vector<std::string>")
    vs = cmp.compare(case, g, c_no_throw)
    assert len(vs) == 1
    assert "original raises but candidate returns" in vs[0].detail


def test_cpp_treesitter_mutator_and_proposer():
    ad = get_adapter("cpp")
    src = (EXAMPLES / "dedupe_rank.cpp").read_text(encoding="utf-8")
    mops = ad.mutation_ops()
    mutants = mops.generate(src, {"dedupe_rank"}, 25, random.Random(11))
    assert len(mutants) >= 8
    for m in mutants:
        tree, _ = parse_source(m["source"], "cpp")
        assert not tree.root_node.has_error

    mod = ad.analyze(src, {})
    intent = IntentBundle(
        language="cpp", source_sha="cpp123456789", source_path="dedupe_rank.cpp", entry_point="dedupe_rank",
        source=src, module_facts=mod, spec=Spec(entry_point="dedupe_rank"),
        contract=[r.evaluate(mod.functions["dedupe_rank"], [], {}) for r in ad.contract_rules()],
        constraints=Constraints(), golden_seed=[], validation=ValidationReport(),
    )
    analysis = AnalysisBundle(source_sha="cpp123456789", entry_point="dedupe_rank", overall_time="O(n^2)", overall_space="O(n)")
    cands = propose_for_language(intent, analysis)
    assert any(c.id == "cpp_rule_find_to_unordered_set" for c in cands)
    for c in cands:
        tree, _ = parse_source(c.source, "cpp")
        assert not tree.root_node.has_error
