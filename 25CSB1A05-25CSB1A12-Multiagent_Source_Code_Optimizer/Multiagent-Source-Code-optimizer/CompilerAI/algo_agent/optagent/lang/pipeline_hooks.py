"""Steps 3-8 multi-language integration helpers (lives in optagent/lang/)."""
from __future__ import annotations

from typing import Any

from ..proposers.kb.catalog import RuleCatalog
from ..proposers.schemas import Candidate
from ..verify.schemas import RungResult
from .registry import get_adapter, list_adapters

_TIER_ORDER = {"REJECTED": -1, "T0": 0, "T1": 1, "T2": 2, "T3": 3, "T4": 4}


def cap_tier_by_capability(tier: str, max_tier: str) -> tuple[str, str | None]:
    """Enforce adapter.caps.max_evidence_tier (e.g. JS <= T2, C/C++ <= T3)."""
    if _TIER_ORDER.get(tier, 0) > _TIER_ORDER.get(max_tier, 4):
        return max_tier, f"language evidence ceiling ({max_tier})"
    return tier, None


def propose_for_language(intent: Any, analysis: Any) -> list[Candidate]:
    """Run language-specific rule catalog filtering + deterministic rule proposer."""
    lang = getattr(intent, "language", "python")
    if lang == "python":
        return []
    adapter = get_adapter(lang)
    pack = adapter.rule_pack()
    catalog = RuleCatalog.load(pack.rules_yaml) if pack.rules_yaml else RuleCatalog([])
    applicable_ids = {
        r.id for r in catalog.filter_applicable(
            intent.contract, intent.constraints, analysis.bottlenecks
        )
    }
    raw_cands = pack.propose_fn(intent, analysis) if pack.propose_fn else []
    # Respect contract: never emit candidates whose transform_id was filtered out by must_preserve
    filtered: list[Candidate] = []
    for c in raw_cands:
        if c.transform_ids and applicable_ids and not any(tid in applicable_ids for tid in c.transform_ids):
            continue
        filtered.append(c)
    return filtered


def run_language_r1(adapter: Any, candidate_source: str, entry: str, hints: dict[str, Any] | None = None) -> RungResult:
    """Language-aware R1 compile/parse & entry-point check."""
    try:
        mod = adapter.analyze(candidate_source, hints or {})
    except Exception as e:
        return RungResult(rung="R1_compile", passed=False, reason=f"Parse/syntax error ({adapter.id}): {e}")
    if entry not in mod.functions:
        return RungResult(
            rung="R1_compile",
            passed=False,
            reason=f"Candidate ({adapter.id}) does not define function '{entry}'.",
        )
    return RungResult(rung="R1_compile", passed=True, details={"language": adapter.id})


def run_language_extra_rungs(oracle: Any, candidate_source: str) -> tuple[list[RungResult], bool, str | None]:
    """Execute adapter-defined verification rungs (sanitizers, CBMC) and return (results, all_passed, granted_tier)."""
    adapter = getattr(oracle, "adapter", None)
    if adapter is None or adapter.id == "python":
        return [], True, None
    results: list[RungResult] = []
    granted: str | None = None
    for rung in adapter.verify_rungs():
        rr = rung.run(oracle, candidate_source)
        results.append(rr)
        if not rr.passed and not rr.skipped and not rung.advisory:
            return results, False, None
        if rr.passed and not rr.skipped and rung.grants_tier:
            if granted is None or _TIER_ORDER.get(rung.grants_tier, 0) > _TIER_ORDER.get(granted, 0):
                granted = rung.grants_tier
    return results, True, granted


def list_language_metadata() -> list[dict[str, Any]]:
    """Return UI/API metadata (badges, capabilities, contract aspects, security profiles) for all languages."""
    out: list[dict[str, Any]] = []
    for lid in list_adapters():
        ad = get_adapter(lid)
        out.append({
            "id": ad.id,
            "display": ad.display,
            "extensions": list(ad.extensions),
            "capabilities": {
                "function_mode": ad.caps.function_mode,
                "program_mode": ad.caps.program_mode,
                "isolation_required": ad.caps.isolation_required,
                "static_types": ad.caps.static_types,
                "max_evidence_tier": ad.caps.max_evidence_tier,
                "perturbation": ad.caps.perturbation,
            },
            "aspects": [r.aspect.value for r in ad.contract_rules()],
            "security_profile": ad.security_profile(),
            "bench_profile": {
                "warmups": ad.bench_profile().warmups,
                "reps": ad.bench_profile().reps,
                "gc_between_reps": ad.bench_profile().gc_between_reps,
                "cpu_time": ad.bench_profile().cpu_time,
            },
        })
    return out
