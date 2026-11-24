"""LLM-based code rewrite proposer with contract and counterexample feedback."""
from __future__ import annotations

import ast
from pydantic import BaseModel, Field

from ..complexity.schemas import AnalysisBundle, Bottleneck
from ..config import Settings
from ..llm.client import LLMClient, LLMError
from ..schemas import Constraints, IntentBundle, Level
from .kb.catalog import Rule
from .retrieval import RuleRetriever
from .schemas import Candidate

PROPOSE_SYSTEM = """You are a principal algorithmic optimization engineer.
Your task is to write an EQUIVALENT, asymptotically faster implementation of a Python function.

Rules:
1. Output ONLY a valid JSON object matching the requested schema.
2. The rewritten code must have the EXACT SAME function name and parameter signature.
3. You MUST PRESERVE all behaviours listed under MUST PRESERVE in the contract (e.g. argument mutations, return values, element order, exception types).
4. Do NOT drop necessary side-effects or quirks that the contract requires preserving.
5. If feedback/counterexamples from previous verification attempts are provided, your rewrite MUST fix those exact failures.
6. The code must be self-contained and use standard library only unless constraints allow new dependencies."""

PROPOSE_USER = """FUNCTION TO OPTIMIZE:
```python
{source}
```

PRESERVATION CONTRACT (NON-NEGOTIABLE):
{contract_text}

CONSTRAINTS:
{constraints_text}

PERFORMANCE BOTTLENECKS (from static & empirical profiler):
{bottlenecks_text}

RECOMMENDED TRANSFORMATION STRATEGIES FROM KNOWLEDGE BASE:
{kb_text}
{feedback_text}

Write an equivalent, faster implementation. Reply with ONE JSON object:
{{
  "rationale": "Explanation of the algorithm paradigm change and why it preserves contract",
  "transform_ids": ["name_of_strategy"],
  "claimed_time": "O(...)",
  "claimed_space": "O(...)",
  "code": "def {entry}(...):\\n    ..."
}}"""


class LLMRewrite(BaseModel):
    rationale: str = ""
    transform_ids: list[str] = Field(default_factory=list)
    claimed_time: str = ""
    claimed_space: str = ""
    code: str = ""


class LLMProposer:
    def __init__(self, llm: LLMClient | Any, settings: Settings | None = None):
        self.llm = llm
        self.s = settings or Settings()

    def propose(
        self,
        intent: IntentBundle,
        analysis: AnalysisBundle,
        retrieved_rules: list[Rule] | None = None,
        feedback: str = "",
        parent_candidate: Candidate | None = None,
    ) -> Candidate | None:
        """Call LLM to propose an algorithmic optimization."""
        if not self.llm:
            return None

        # Build contract summary
        must_preserve = [
            f"- {it.aspect.value}: {it.rationale}"
            for it in intent.contract
            if it.level == Level.MUST and it.applicable
        ]
        may_change = [
            f"- {it.aspect.value}: {it.rationale}"
            for it in intent.contract
            if it.level == Level.MAY and it.applicable
        ]
        contract_text = "MUST PRESERVE:\n" + "\n".join(must_preserve)
        if may_change:
            contract_text += "\n\nMAY CHANGE:\n" + "\n".join(may_change)

        # Build bottlenecks text
        bn_text = "\n".join(
            f"- L{b.line} [{b.pattern}] {b.share_of_time:.1%} runtime: {b.code} ({b.detail})"
            for b in analysis.bottlenecks[:5]
        ) or "None detected"

        # Build KB rules text
        kb_text = "\n".join(
            f"- {r.name} ({r.id}): {r.description} (Expected: {r.expected_gain})"
            for r in (retrieved_rules or [])
        ) or "Standard algorithmic paradigms (hash maps, binary search, two pointers, DP)."

        # Feedback block
        feedback_text = ""
        if feedback:
            feedback_text = f"\nVERIFICATION FEEDBACK FROM PREVIOUS ATTEMPT:\n{feedback}\nFix these issues!"

        constraints_text = (
            f"allow_approximation: {intent.constraints.allow_approximation}, "
            f"allow_new_dependencies: {intent.constraints.allow_new_dependencies}, "
            f"optimize_for: {intent.constraints.optimize_for}"
        )

        user_prompt = PROPOSE_USER.format(
            source=parent_candidate.source if parent_candidate else intent.source,
            entry=intent.entry_point,
            contract_text=contract_text,
            constraints_text=constraints_text,
            bottlenecks_text=bn_text,
            kb_text=kb_text,
            feedback_text=feedback_text,
        )

        try:
            resp: LLMRewrite = self.llm.complete_json(PROPOSE_SYSTEM, user_prompt, LLMRewrite)
        except Exception:
            return None

        code = resp.code.strip()
        if not code:
            return None

        # Verify candidate parses using the language's own parser
        lang = getattr(intent, "language", "python")
        if lang != "python":
            try:
                from ..lang.registry import get_adapter
                ad = get_adapter(lang)
                mod = ad.analyze(code, {})
                if intent.entry_point != "__script__" and intent.entry_point not in mod.functions:
                    return None
            except Exception:
                return None
        else:
            try:
                tree = ast.parse(code)
                entry = intent.entry_point
                if entry != "__script__":
                    if "." in entry:
                        cls_n, meth_n = entry.split(".", 1)
                        ok_entry = any(
                            isinstance(c, ast.ClassDef) and c.name == cls_n and any(
                                isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef)) and m.name == meth_n
                                for m in c.body
                            )
                            for c in tree.body
                        )
                    else:
                        ok_entry = any(
                            isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == entry
                            for n in tree.body
                        )
                    if not ok_entry:
                        return None
            except SyntaxError:
                return None

        return Candidate.make(
            source=code,
            proposer="llm",
            parent_id=parent_candidate.id if parent_candidate else None,
            transform_ids=resp.transform_ids or ["llm_rewrite"],
            rationale=resp.rationale,
            claimed_time=resp.claimed_time,
            claimed_space=resp.claimed_space,
        )

