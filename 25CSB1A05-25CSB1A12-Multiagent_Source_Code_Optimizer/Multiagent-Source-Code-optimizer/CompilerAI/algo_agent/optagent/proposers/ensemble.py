"""Ensemble orchestrator for generating code rewrite candidates."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..complexity.schemas import AnalysisBundle
from ..config import Settings
from ..llm.client import LLMClient
from ..schemas import IntentBundle
from .kb.catalog import RuleCatalog
from .llm_proposer import LLMProposer
from .retrieval import RuleRetriever
from .rule_engine import RuleEngine
from .schemas import Candidate


class ProposerEnsemble:
    """Ensemble of rule-based and LLM-based rewrite generators.

    PROPOSERS NEVER VERIFY AND NEVER RUN CODE.
    """

    def __init__(
        self,
        settings: Settings | None = None,
        llm: LLMClient | Any | None = None,
        use_llm: bool = False,
    ):
        self.s = settings or Settings()
        self.catalog = RuleCatalog.load()
        self.rule_engine = RuleEngine(self.catalog)
        self.retriever = RuleRetriever(self.catalog.rules)

        self.use_llm = use_llm
        if llm is not None:
            self.llm = llm
            self.use_llm = True
        elif use_llm:
            self.llm = LLMClient(self.s.spec_model, self.s, "proposer")
        else:
            self.llm = None

        self.llm_proposer = LLMProposer(self.llm, self.s) if self.llm else None

    def propose_candidates(
        self,
        intent: IntentBundle,
        analysis: AnalysisBundle,
        feedback: str = "",
        parent: Candidate | None = None,
    ) -> list[Candidate]:
        """Generate a diverse set of candidate rewrites from rules and LLM."""
        candidates: list[Candidate] = []
        seen_sources: set[str] = {intent.source.strip()}
        if parent:
            seen_sources.add(parent.source.strip())

        # 1. Rule Engine (deterministic, mechanical rewrites)
        if getattr(intent, "language", "python") != "python":
            from ..lang.pipeline_hooks import propose_for_language
            rule_cands = propose_for_language(intent, analysis)
        else:
            rule_cands = self.rule_engine.propose(intent, analysis)
        for c in rule_cands:
            cleaned = c.source.strip()
            if cleaned not in seen_sources:
                seen_sources.add(cleaned)
                candidates.append(c)

        # 2. LLM Proposer (if enabled or injected)
        if self.use_llm and self.llm_proposer:
            applicable = self.catalog.filter_applicable(
                intent.contract, intent.constraints, analysis.bottlenecks
            )
            retrieved = self.retriever.retrieve(
                intent.source, analysis.bottlenecks, top_k=5
            )
            # Combine applicable and retrieved
            rules_for_prompt = [r for r in retrieved if r.id in {a.id for a in applicable}] or applicable[:4]

            llm_cand = self.llm_proposer.propose(
                intent, analysis, rules_for_prompt, feedback=feedback, parent_candidate=parent
            )
            if llm_cand and llm_cand.source.strip() not in seen_sources:
                seen_sources.add(llm_cand.source.strip())
                candidates.append(llm_cand)

            # Save LLM trace if trace exists
            if hasattr(self.llm, "trace") and self.llm.trace:
                out_dir = Path(self.s.runs_dir) / intent.source_sha / "proposers"
                out_dir.mkdir(parents=True, exist_ok=True)
                (out_dir / "llm_trace.json").write_text(
                    json.dumps(self.llm.trace, indent=2), encoding="utf-8"
                )

        return candidates

