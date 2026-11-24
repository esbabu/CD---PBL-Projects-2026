"""Step 4 tests: proposer ensemble, knowledge base rules, AST transformations, and contract adherence."""
from __future__ import annotations

from pathlib import Path
import pytest

from optagent.complexity.analyzer import Analyzer
from optagent.config import Settings
from optagent.intent.pipeline import IntentExtractor
from optagent.proposers.ensemble import ProposerEnsemble
from optagent.proposers.kb.catalog import RuleCatalog
from optagent.proposers.llm_proposer import LLMProposer
from optagent.proposers.schemas import Candidate
from optagent.schemas import Aspect, Constraints, Level, PreservationItem, Source

EX = Path(__file__).parent.parent / "examples"


def fast_settings(tmp_path, **kw):
    base = dict(
        sandbox_backend="local",
        runs_dir=str(tmp_path / "runs"),
        n_family=20,
        n_hypothesis=20,
        n_probe=5,
        fuzz_budget_s=0.0,
        max_mutants=5,
        scale_sizes=(10, 50, 100),
        scale_budget_s=1.0,
        case_timeout_s=2.0,
    )
    base.update(kw)
    return Settings(**base)


class FakeLLM:
    """Mock LLM client for deterministic testing without external API."""

    def __init__(self, code: str):
        self.code = code
        self.trace: list[dict] = []

    def complete_json(self, system: str, user: str, schema):
        self.trace.append({"system": system[:50], "user": user[:50]})
        return schema(
            rationale="FakeLLM test optimization",
            transform_ids=["llm_hash_opt"],
            claimed_time="O(n)",
            claimed_space="O(n)",
            code=self.code,
        )


# ---------------------------------------------------------------------------
# 1. Knowledge Base and Contract Filtering Tests
# ---------------------------------------------------------------------------
def test_catalog_filtering_never_violates_must_preserve():
    catalog = RuleCatalog.load()
    assert len(catalog.rules) > 0

    # If SORT_STABILITY is MUST, unstable_heap_selection must be filtered out
    contract = [
        PreservationItem(aspect=Aspect.SORT_STABILITY, level=Level.MUST, applicable=True, rationale="test", source=Source.STATIC),
        PreservationItem(aspect=Aspect.ARG_MUTATION, level=Level.MUST, applicable=True, rationale="test", source=Source.STATIC),
    ]
    constraints = Constraints()
    filtered = catalog.filter_applicable(contract, constraints, [])

    rule_ids = {r.id for r in filtered}
    assert "unstable_heap_selection" not in rule_ids
    assert "in_place_array_sort" not in rule_ids
    assert "list_to_set_membership" in rule_ids


# ---------------------------------------------------------------------------
# 2. Slow Two Sum Candidate Generation
# ---------------------------------------------------------------------------
def test_slow_two_sum_ensemble_emits_hash_bisect_candidate(tmp_path):
    s = fast_settings(tmp_path)
    src = (EX / "slow_two_sum.py").read_text(encoding="utf-8")
    intent = IntentExtractor(s, use_llm=False).run(src, source_name="slow_two_sum.py")
    analyzer = Analyzer(s, log=lambda *a: None)
    analysis = analyzer.analyze(intent)

    ensemble = ProposerEnsemble(s, use_llm=False)
    candidates = ensemble.propose_candidates(intent, analysis)

    assert len(candidates) >= 1
    c = candidates[0]
    assert "bisect" in c.source or "pos" in c.source
    assert "nested_loop_to_hash_index" in c.transform_ids
    assert c.claimed_time == "O(n log n)"


# ---------------------------------------------------------------------------
# 3. Dedupe Rank Candidate Generation
# ---------------------------------------------------------------------------
def test_dedupe_rank_ensemble_emits_set_dict_candidate(tmp_path):
    s = fast_settings(tmp_path)
    src = (EX / "dedupe_rank.py").read_text(encoding="utf-8")
    overrides = {"inputs": [{"args": [["apple", "banana", "apple", "cherry"], 2]}]}
    intent = IntentExtractor(s, use_llm=False).run(src, overrides=overrides, source_name="dedupe_rank.py")
    analyzer = Analyzer(s, log=lambda *a: None)
    analysis = analyzer.analyze(intent)

    ensemble = ProposerEnsemble(s, use_llm=False)
    candidates = ensemble.propose_candidates(intent, analysis)

    assert len(candidates) >= 1
    c = candidates[0]
    assert "seen_set" in c.source
    assert "list_to_set_membership" in c.transform_ids
    # Crucial: verify arg_mutation quirk is preserved!
    assert "words.append" in c.source and "__done__" in c.source


# ---------------------------------------------------------------------------
# 4. LLM Proposer with FakeLLM
# ---------------------------------------------------------------------------
def test_llm_proposer_with_fake_llm(tmp_path):
    s = fast_settings(tmp_path)
    src = (EX / "slow_two_sum.py").read_text(encoding="utf-8")
    intent = IntentExtractor(s, use_llm=False).run(src, source_name="slow_two_sum.py")
    analyzer = Analyzer(s, log=lambda *a: None)
    analysis = analyzer.analyze(intent)

    valid_optimized_code = (
        "def two_sum(nums, target):\n"
        "    seen = {}\n"
        "    for j, v in enumerate(nums):\n"
        "        if target - v in seen:\n"
        "            return [seen[target - v], j]\n"
        "        seen[v] = j\n"
        "    return []\n"
    )

    fake_llm = FakeLLM(valid_optimized_code)
    ensemble = ProposerEnsemble(s, llm=fake_llm, use_llm=True)
    candidates = ensemble.propose_candidates(intent, analysis)

    llm_cands = [c for c in candidates if c.proposer == "llm"]
    assert len(llm_cands) == 1
    cand = llm_cands[0]
    assert cand.source.strip() == valid_optimized_code.strip()
    assert cand.rationale == "FakeLLM test optimization"
    assert len(fake_llm.trace) > 0


def test_llm_proposer_rejects_syntax_error(tmp_path):
    s = fast_settings(tmp_path)
    src = (EX / "slow_two_sum.py").read_text(encoding="utf-8")
    intent = IntentExtractor(s, use_llm=False).run(src, source_name="slow_two_sum.py")
    analyzer = Analyzer(s, log=lambda *a: None)
    analysis = analyzer.analyze(intent)

    invalid_code = "def two_sum(nums, target): return ["
    fake_llm = FakeLLM(invalid_code)
    ensemble = ProposerEnsemble(s, llm=fake_llm, use_llm=True)
    candidates = ensemble.propose_candidates(intent, analysis)

    llm_cands = [c for c in candidates if c.proposer == "llm"]
    assert len(llm_cands) == 0
