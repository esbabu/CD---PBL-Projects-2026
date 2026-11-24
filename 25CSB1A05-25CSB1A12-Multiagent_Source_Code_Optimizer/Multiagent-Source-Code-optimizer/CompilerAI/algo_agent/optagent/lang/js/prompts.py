"""JavaScript-specific prompt pack for LLM spec, input, prediction, and candidate generation."""
from __future__ import annotations

from ..base import PromptPack

JS_PROMPT_PACK = PromptPack(
    language_name="javascript",
    code_fence="javascript",
    spec_system=(
        "You are a senior JavaScript program-analysis engineer writing a BEHAVIOURAL SPECIFICATION.\n"
        "Rules:\n"
        "1. Describe observable JS behaviour only: return value, argument mutation (push/splice/sort), thrown errors, console output.\n"
        "2. Pay strict attention to JS quirks: Array.prototype.sort default lexicographic order & ES2019 stability, "
        "Object integer-like key enumeration order vs Map insertion order, === vs ==, NaN, -0, undefined vs null, Promise vs sync.\n"
        "3. Never suggest optimizations and never 'fix' bugs or quirks.\n"
        "4. Reply with ONE JSON object and nothing else."
    ),
    proposer_rules=(
        "JavaScript optimization rules:\n"
        "- Preserve the exact function name, signature, and export style.\n"
        "- Use standard JavaScript / Node built-ins only; NO external npm packages.\n"
        "- Preserve argument mutations (e.g., array.push) and return aliasing if MUST.\n"
        "- Do NOT replace Map with plain Object when keys may be integer-like strings (breaks key_enumeration_order).\n"
        "- Do NOT mutate Object.prototype or Array.prototype.\n"
        "- Preserve Promise / async return semantics.\n"
    ),
)
