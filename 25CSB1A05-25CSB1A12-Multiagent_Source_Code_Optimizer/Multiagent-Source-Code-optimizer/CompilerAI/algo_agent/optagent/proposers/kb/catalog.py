"""Catalog of transformation rules loaded from rules.yaml."""
from __future__ import annotations

from pathlib import Path
from typing import Any
import yaml
from pydantic import BaseModel, Field

from ...complexity.schemas import Bottleneck
from ...schemas import Constraints, Level, PreservationItem

DEFAULT_RULES_YAML = Path(__file__).with_name("rules.yaml")


class Rule(BaseModel):
    id: str
    name: str
    pattern: str
    category: str
    preconditions: list[str] = Field(default_factory=list)
    breaks: list[str] = Field(default_factory=list)
    expected_gain: str = ""
    description: str = ""


class RuleCatalog:
    def __init__(self, rules: list[Rule]):
        self.rules = rules

    @classmethod
    def load(cls, path: Path | None = None) -> "RuleCatalog":
        p = path or DEFAULT_RULES_YAML
        if not p.exists():
            return cls([])
        raw = yaml.safe_load(p.read_text(encoding="utf-8"))
        rules = [Rule.model_validate(r) for r in raw.get("rules", [])]
        return cls(rules)

    def filter_applicable(
        self,
        contract: list[PreservationItem],
        constraints: Constraints,
        bottlenecks: list[Bottleneck],
    ) -> list[Rule]:
        """Filter rules ensuring NO rule violates any 'must_preserve' aspect."""
        must_preserve_aspects = {
            it.aspect.value for it in contract if it.level == Level.MUST and it.applicable
        }
        active_patterns = {b.pattern for b in bottlenecks}

        applicable: list[Rule] = []
        for r in self.rules:
            # Rule 8: NEVER propose a rule that breaks a must_preserve aspect
            if any(b in must_preserve_aspects for b in r.breaks):
                continue

            # Check constraints
            if not constraints.allow_new_dependencies and "new_dependency" in r.preconditions:
                continue

            applicable.append(r)

        # Rank rules: rules matching an active bottleneck pattern come first
        applicable.sort(key=lambda r: (r.pattern in active_patterns, r.id), reverse=True)
        return applicable

