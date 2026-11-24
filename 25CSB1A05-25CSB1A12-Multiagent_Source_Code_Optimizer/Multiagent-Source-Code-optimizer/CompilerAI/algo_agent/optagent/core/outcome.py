"""Typed optimization outcomes, reason codes, and remediation catalog."""
from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field

from .provenance import ProvenanceSummary


class SupportLevel(str, Enum):
    FULL = "full"                    # executed, oracle tier A/B, verified
    VERIFIED_WEAK = "verified_weak"  # executed, oracle tier C/D: low confidence
    ANALYSIS_ONLY = "analysis_only"  # cannot execute: static+LLM analysis, UNVERIFIED
    REFUSED = "refused"              # syntax error, empty input, over size limit, unsupported language


class ReasonCode(str, Enum):
    SYNTAX_ERROR = "SYNTAX_ERROR"
    NO_ENTRY_FOUND = "NO_ENTRY_FOUND"
    ENTRY_AUTO_SELECTED = "ENTRY_AUTO_SELECTED"
    UNSUPPORTED_ENTRY_KIND = "UNSUPPORTED_ENTRY_KIND"
    MISSING_DEPENDENCY = "MISSING_DEPENDENCY"
    IMPORT_SIDE_EFFECT = "IMPORT_SIDE_EFFECT"
    NO_SEED_INPUTS = "NO_SEED_INPUTS"
    ORIGINAL_TIMEOUT = "ORIGINAL_TIMEOUT"
    ORIGINAL_CRASH = "ORIGINAL_CRASH"
    UNSERIALIZABLE_ARGS = "UNSERIALIZABLE_ARGS"
    SANDBOX_UNAVAILABLE = "SANDBOX_UNAVAILABLE"
    TOOLCHAIN_MISSING = "TOOLCHAIN_MISSING"
    BUILD_FAILED = "BUILD_FAILED"
    LLM_UNAVAILABLE = "LLM_UNAVAILABLE"
    LLM_INVALID_OUTPUT = "LLM_INVALID_OUTPUT"
    ORACLE_WEAK = "ORACLE_WEAK"
    LANGUAGE_UNSUPPORTED = "LANGUAGE_UNSUPPORTED"
    STAGE_ERROR = "STAGE_ERROR"
    INPUT_TOO_LARGE = "INPUT_TOO_LARGE"


REASON_REMEDIATION: dict[ReasonCode, str] = {
    ReasonCode.SYNTAX_ERROR: "Fix syntax errors in the source code before running optimization.",
    ReasonCode.NO_ENTRY_FOUND: "Define a callable function/method or provide a runnable stdin/stdout script.",
    ReasonCode.ENTRY_AUTO_SELECTED: "Pass `--entry <name>` or `entry` in the request to choose a different entry point.",
    ReasonCode.UNSUPPORTED_ENTRY_KIND: "Wrap core logic in a callable function or provide `hints` (e.g., `hints.instantiate` for templates).",
    ReasonCode.MISSING_DEPENDENCY: "Install the missing package in the configured sandbox image or configure `OPT_PY_IMAGES`.",
    ReasonCode.IMPORT_SIDE_EFFECT: "Move top-level I/O or heavy initialization inside `if __name__ == '__main__':`.",
    ReasonCode.NO_SEED_INPUTS: "Add type annotations, default arguments, a docstring example, or pass explicit `inputs` in overrides.",
    ReasonCode.ORIGINAL_TIMEOUT: "Supply smaller seed inputs or increase `case_timeout_s` so baseline cases finish cleanly.",
    ReasonCode.ORIGINAL_CRASH: "Ensure the original implementation succeeds on at least one valid input without crashing.",
    ReasonCode.UNSERIALIZABLE_ARGS: "Use JSON/primitive/dataclass/namedtuple arguments or supply `hints.ctor_args`.",
    ReasonCode.SANDBOX_UNAVAILABLE: "Start Docker or set `OPT_SANDBOX=local` (for Python/JS) to enable sandbox execution.",
    ReasonCode.TOOLCHAIN_MISSING: "Install the required compiler/runtime (node, clang/gcc) or build the corresponding image under `docker/`.",
    ReasonCode.BUILD_FAILED: "Check the compiler diagnostic log in `diagnostics.json` and fix missing headers or flags.",
    ReasonCode.LLM_UNAVAILABLE: "Start Ollama at the configured `OPT_API_BASE` URL and verify installed models with `python -m optagent.doctor`, or run with `OPT_LLM_MODE=off`.",
    ReasonCode.LLM_INVALID_OUTPUT: "The model returned malformed JSON or schema-invalid output; deterministic heuristic fallbacks were used.",
    ReasonCode.ORACLE_WEAK: "Add richer seed inputs or pass `accept_low_confidence=True` to accept candidates verified on a weak oracle (Tier C/D).",
    ReasonCode.LANGUAGE_UNSUPPORTED: "Use one of the supported languages: python, javascript, c, cpp.",
    ReasonCode.STAGE_ERROR: "Inspect `runs/<sha>/diagnostics.json` for the full stage exception trace.",
    ReasonCode.INPUT_TOO_LARGE: "Reduce source size below the configured limit or split the target function into a smaller module.",
}


class Reason(BaseModel):
    code: ReasonCode
    message: str
    remediation: str = ""
    stage: str = "triage"
    detail: dict[str, Any] = Field(default_factory=dict)

    def model_post_init(self, __context: Any) -> None:
        if not self.remediation:
            self.remediation = REASON_REMEDIATION.get(self.code, "")


class StageResult(BaseModel):
    name: str
    status: Literal["ok", "degraded", "skipped", "failed"]
    seconds: float = 0.0
    produced_by: list[str] = Field(default_factory=list)
    reasons: list[Reason] = Field(default_factory=list)


class OptimizeOutcome(BaseModel):
    support_level: SupportLevel
    reasons: list[Reason] = Field(default_factory=list)
    stages: list[StageResult] = Field(default_factory=list)
    provenance: ProvenanceSummary = Field(default_factory=ProvenanceSummary)
    strategy: str = "function"
    language: str = "python"
    entry_point: str | None = None
    low_confidence: bool = False
    unverified: bool = False
    syntax_report: Any = None
    module_outcome: Any = None


def render_troubleshooting_markdown() -> str:
    lines = [
        "## Troubleshooting (Reason Codes & Remediation)",
        "",
        "Generated from `optagent.core.outcome.REASON_REMEDIATION`.",
        "",
        "| Reason Code | Remediation |",
        "|---|---|",
    ]
    for code, rem in REASON_REMEDIATION.items():
        lines.append(f"| `{code.value}` | {rem} |")
    lines.append("")
    return "\n".join(lines)
