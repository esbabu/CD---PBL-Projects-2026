"""C11 and C++17 prompt packs for OptAgent."""
from __future__ import annotations

from ..base import PromptPack

C_PROMPT_PACK = PromptPack(
    language_name="c",
    code_fence="c",
    spec_system=(
        "You are a senior C11 systems engineer writing a BEHAVIOURAL SPECIFICATION.\n"
        "Rules:\n"
        "1. Describe observable behaviour only: return value, out-parameters, buffer mutations, stdout, globals, errno.\n"
        "2. Note integer width/signedness, pointer ownership, and potential undefined behaviour paths.\n"
        "3. Never suggest optimizations and never 'fix' intentional quirks.\n"
        "4. Reply with ONE JSON object and nothing else."
    ),
    proposer_rules=(
        "C11 optimization rules:\n"
        "- Preserve the EXACT C prototype (function name, parameter types, const qualifiers, return type).\n"
        "- Use C11 standard library headers only; NO external libraries.\n"
        "- Never introduce undefined behavior (signed overflow, out-of-bounds access, uninitialized reads, null deref).\n"
        "- Preserve memory ownership conventions (do not leak or double-free).\n"
        "- Keep out-parameter writes identical for every valid input.\n"
    ),
)

CPP_PROMPT_PACK = PromptPack(
    language_name="cpp",
    code_fence="cpp",
    spec_system=(
        "You are a senior C++17 engineer writing a BEHAVIOURAL SPECIFICATION.\n"
        "Rules:\n"
        "1. Describe observable behaviour only: return value, reference mutations, exceptions thrown (exact std::exception types), stdout, globals.\n"
        "2. Distinguish std::sort (unstable) vs std::stable_sort (stable), .at() (throws std::out_of_range) vs operator[], ordered vs unordered containers.\n"
        "3. Never suggest optimizations and never 'fix' quirks.\n"
        "4. Reply with ONE JSON object and nothing else."
    ),
    proposer_rules=(
        "C++17 optimization rules:\n"
        "- Preserve the EXACT C++ function signature (constness, references, parameter and return types).\n"
        "- Use C++17 standard library only; NO external dependencies.\n"
        "- Never introduce undefined behavior or memory safety issues (must be ASan+UBSan clean).\n"
        "- Do NOT replace std::stable_sort with std::sort if sort_stability is MUST.\n"
        "- Do NOT replace .at() with operator[] if exception_type (std::out_of_range) is MUST.\n"
        "- Preserve mutations to non-const lvalue reference parameters.\n"
    ),
)
