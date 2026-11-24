"""C++17 LanguageAdapter implementation (STL marshalling, exceptions, normalization, cross-stdlib)."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from ...oracle.schemas import CaseResult
from ...proposers.schemas import Candidate
from ...schemas import Aspect, FunctionFacts, Level, Source
from ..base import Capabilities, ContractRule, PromptPack, RulePack
from .adapter_c import CAdapter, NATIVE_DIR
from .prompts import CPP_PROMPT_PACK


def normalize_unordered_value(val: Any) -> Any:
    """Recursively sort `__uset__` -> `__set__` and `__udict__` -> `__dict__`.

    Iteration order of std::unordered_set and std::unordered_map is implementation-defined
    and therefore NOT observable behaviour to preserve.
    """
    if isinstance(val, list):
        return [normalize_unordered_value(x) for x in val]
    if isinstance(val, dict):
        if len(val) == 1:
            (k, inner), = val.items()
            if k == "__uset__":
                norm_items = [normalize_unordered_value(x) for x in inner]
                norm_items.sort(key=lambda x: json.dumps(x, sort_keys=True))
                return {"__set__": norm_items}
            if k == "__udict__":
                norm_pairs = [[normalize_unordered_value(a), normalize_unordered_value(b)] for a, b in inner]
                norm_pairs.sort(key=lambda pair: json.dumps(pair[0], sort_keys=True))
                return {"__dict__": norm_pairs}
            if k in ("__tuple__", "__set__", "__dict__", "__map__"):
                return {k: normalize_unordered_value(inner)}
        return {k: normalize_unordered_value(v) for k, v in val.items()}
    return val


def _cpp_propose_rules(intent: Any, analysis: Any) -> list[Candidate]:
    """Deterministic mechanical C++17 rewrite rules."""
    src: str = intent.source
    entry: str = intent.entry_point
    fn = intent.module_facts.functions.get(entry)
    if not fn:
        return []
    cands: list[Candidate] = []
    patterns = {p.kind for p in fn.cost_patterns} | {b.pattern for b in (analysis.bottlenecks or [])}

    # 1. std::find(seen.begin(), seen.end(), w) inside loop -> companion std::unordered_set
    if "linear_membership" in patterns or "std::find(" in src:
        m_find = re.search(
            r"std::find\s*\(\s*(\w+)\.begin\(\)\s*,\s*\1\.end\(\)\s*,\s*(\w+)\s*\)\s*==\s*\1\.end\(\)",
            src,
        )
        if m_find:
            vec_var, elem_var = m_find.groups()
            set_var = f"{vec_var}_set"
            m_decl = re.search(rf"(std::vector<([^>]+)>\s+{re.escape(vec_var)}\s*;)", src)
            if m_decl:
                elem_type = m_decl.group(2).strip()
                header_add = "" if "<unordered_set>" in src else "#include <unordered_set>\n"
                new_src = header_add + src.replace(
                    m_decl.group(1),
                    f"{m_decl.group(1)}\n    std::unordered_set<{elem_type}> {set_var};",
                    1,
                )
                new_src = new_src.replace(m_find.group(0), f"{set_var}.insert({elem_var}).second", 1)
                if new_src != src:
                    cands.append(Candidate(
                        id="cpp_rule_find_to_unordered_set",
                        proposer="rule",
                        source=new_src,
                        transform_ids=["cpp_linear_find_to_unordered_set"],
                        rationale=f"Replaced O(n) std::find on {vec_var} inside loop with O(1) std::unordered_set<{elem_type}>.",
                        claimed_time="O(n log n)" if fn.sort_uses else "O(n)",
                        claimed_space="O(n)",
                    ))

    # 2. Vector reserve() before push_back loop
    m_vec = re.search(r"(std::vector<[^>]+>\s+(\w+)\s*;)", src)
    if m_vec and f"{m_vec.group(2)}.push_back(" in src and f"{m_vec.group(2)}.reserve(" not in src:
        vname = m_vec.group(2)
        if fn.params:
            first_param = fn.params[0].name
            new_src = src.replace(
                m_vec.group(1),
                f"{m_vec.group(1)}\n    {vname}.reserve({first_param}.size());",
                1,
            )
            cands.append(Candidate(
                id="cpp_rule_vector_reserve",
                proposer="rule",
                source=new_src,
                transform_ids=["cpp_vector_reserve"],
                rationale=f"Pre-allocated {vname} with .reserve({first_param}.size()) to avoid repeated reallocations.",
                claimed_time=analysis.overall_time or "O(n)",
                claimed_space="O(n)",
            ))

    return cands


class CppAdapter(CAdapter):
    """LanguageAdapter for C++ (C++17 / C++20 via hints)."""

    id: str = "cpp"
    display: str = "C++ (C++17)"
    extensions: tuple[str, ...] = (".cpp", ".cc", ".cxx", ".hpp")
    caps: Capabilities = Capabilities(
        function_mode=True,
        program_mode=False,
        isolation_required=True,
        static_types=True,
        max_evidence_tier="T3",
        perturbation="malloc_perturb",
    )

    def prompt_pack(self) -> PromptPack:
        return CPP_PROMPT_PACK

    def contract_rules(self) -> list[ContractRule]:
        base = [r for r in super().contract_rules() if r.aspect != Aspect.SORT_STABILITY]

        def _has_stable_sort(fn: FunctionFacts, recs: list[Any], hints: dict[str, Any]) -> bool:
            return any(s.kind == "stable_sort" for s in fn.sort_uses)

        def _has_rvalue_ref(fn: FunctionFacts) -> bool:
            return any((p.annotation or "").strip().endswith("&&") for p in fn.params)

        base.append(ContractRule(
            aspect=Aspect.SORT_STABILITY,
            default_level=Level.MUST,
            applicable_fn=_has_stable_sort,
            rationale="Original uses std::stable_sort; equal keys must preserve relative order (replacing with std::sort breaks ties).",
            source=Source.STATIC,
        ))

        # Moved-from rvalue references (`T&&`) have valid-but-unspecified state -> arg_mutation MAY
        base.append(ContractRule(
            aspect=Aspect.ARG_MUTATION,
            default_level=Level.MUST,
            applicable_fn=lambda fn, recs, h: not _has_rvalue_ref(fn),
            rationale="Non-const reference parameters (T&) must preserve exact mutations; moved-from rvalue refs (T&&) are unspecified.",
            source=Source.STATIC,
        ))
        return base

    def normalize_result(self, r: CaseResult) -> CaseResult:
        """Canonicalize std::unordered_set (`__uset__`) and std::unordered_map (`__udict__`)."""
        norm_ret = normalize_unordered_value(r.ret)
        norm_mut = {k: normalize_unordered_value(v) for k, v in r.mut.items()}
        norm_glob = {k: normalize_unordered_value(v) for k, v in r.glob.items()}
        if norm_ret == r.ret and norm_mut == r.mut and norm_glob == r.glob:
            return r
        return r.model_copy(update={"ret": norm_ret, "mut": norm_mut, "glob": norm_glob})

    def rule_pack(self) -> RulePack:
        return RulePack(
            language="cpp",
            rules_yaml=NATIVE_DIR / "rules_cpp.yaml",
            propose_fn=_cpp_propose_rules,
        )
