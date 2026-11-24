"""Retrieval of relevant transformation rules from KB."""
from __future__ import annotations

import re
from typing import Any
from ..complexity.schemas import Bottleneck
from .kb.catalog import Rule


def _tokenize(text: str) -> set[str]:
    return set(re.findall(r"\w+", text.lower()))


class RuleRetriever:
    def __init__(self, rules: list[Rule]):
        self.rules = rules

    def retrieve(self, source: str, bottlenecks: list[Bottleneck], top_k: int = 5) -> list[Rule]:
        """Rank rules by similarity to source code and active bottlenecks."""
        if not self.rules:
            return []

        src_tokens = _tokenize(source)
        bn_patterns = {b.pattern.lower() for b in bottlenecks}
        bn_text = " ".join(b.detail + " " + b.code for b in bottlenecks).lower()

        scored: list[tuple[float, Rule]] = []
        for r in self.rules:
            score = 0.0
            r_pattern = r.pattern.lower()
            if r_pattern in bn_patterns:
                score += 10.0
            if r_pattern in bn_text:
                score += 5.0

            # Lexical overlap
            rule_tokens = _tokenize(r.name + " " + r.description + " " + " ".join(r.preconditions))
            overlap = len(src_tokens & rule_tokens)
            score += float(overlap)

            scored.append((score, r))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [r for _, r in scored[:top_k]]

