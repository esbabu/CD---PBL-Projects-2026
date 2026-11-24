"""Core language adapter protocol and supporting dataclasses for OptAgent."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Protocol, runtime_checkable

from ..oracle.schema_infer import ParamSchema
from ..oracle.schemas import CaseResult
from ..runtime.sandbox import SandboxProfile
from ..schemas import Aspect, FunctionFacts, Level, ModuleFacts, PreservationItem, Source


@dataclass(frozen=True)
class Capabilities:
    """Declares what an adapter supports and its evidence ceiling."""
    function_mode: bool = True
    program_mode: bool = False
    isolation_required: bool = False
    static_types: bool = False
    max_evidence_tier: str = "T4"       # python "T4", javascript "T2", c/cpp "T3"
    perturbation: str = "hashseed"      # "hashseed" | "prng_seed" | "malloc_perturb"


@dataclass
class BuildResult:
    """Result of compiling or preparing a target file for execution."""
    ok: bool
    artifact_path: Path | None = None
    log: str = ""
    compiler_version: str = ""
    flags: list[str] = field(default_factory=list)


@dataclass
class PromptPack:
    """Language-specific LLM prompt templates (falls back to Python prompts)."""
    language_name: str = "python"
    code_fence: str = "python"
    spec_system: str = ""
    spec_user: str = ""
    refine_user: str = ""
    input_system: str = ""
    input_user: str = ""
    predict_system: str = ""
    predict_user: str = ""
    proposer_rules: str = ""


@dataclass
class ContractRule:
    """Per-language contract aspect rule injected into Step 1 contract building."""
    aspect: Aspect
    default_level: Level
    applicable_fn: Callable[[FunctionFacts, list[Any], dict[str, Any]], bool] | None = None
    rationale: str = ""
    source: Source = Source.DEFAULT

    def evaluate(self, fn: FunctionFacts, records: list[Any], hints: dict[str, Any]) -> PreservationItem:
        app = self.applicable_fn(fn, records, hints) if self.applicable_fn else True
        return PreservationItem(
            aspect=self.aspect,
            level=self.default_level,
            applicable=app,
            rationale=self.rationale,
            source=self.source,
        )


@dataclass
class MutationOps:
    """Language-specific mutant generator hook."""
    language: str
    generate: Callable[[str, set[str], int, Any], list[dict[str, Any]]] | None = None
    file_extension: str = ".py"


@dataclass
class RulePack:
    """Language-specific deterministic rewrite rules and catalog path."""
    language: str
    rules_yaml: Path | None = None
    propose_fn: Callable[[Any, Any], list[Any]] | None = None


@dataclass
class BenchProfile:
    """Language-specific benchmarking configuration."""
    language: str
    warmups: int = 2
    reps: int = 5
    gc_between_reps: bool = False
    report_cold_and_warm: bool = False
    cpu_time: bool = False
    extra_flags: list[str] = field(default_factory=list)


@dataclass
class Rung:
    """Language-specific verification rung hook."""
    name: str
    run: Callable[..., Any]
    grants_tier: str | None = None
    advisory: bool = False


@runtime_checkable
class LanguageAdapter(Protocol):
    """Protocol implemented by every language backend (Python, JS, C, C++)."""
    id: str
    display: str
    extensions: tuple[str, ...]
    caps: Capabilities

    # Step 1
    def analyze(self, source: str, hints: dict[str, Any]) -> ModuleFacts: ...
    def select_entry(self, mod: ModuleFacts, requested: str | None) -> str: ...
    def signature(self, fn: FunctionFacts) -> str: ...
    def seed_inputs(self, fn: FunctionFacts, hints: dict[str, Any]) -> list[dict[str, Any]]: ...
    def param_schema(self, fn: FunctionFacts, hints: dict[str, Any], seeds: list[Any]) -> ParamSchema | None: ...
    def prompt_pack(self) -> PromptPack: ...
    def contract_rules(self) -> list[ContractRule]: ...

    # Step 2
    def sandbox_profile(self, hints: dict[str, Any]) -> SandboxProfile: ...
    def build(self, source: str, entry: str, hints: dict[str, Any], workdir: Path) -> BuildResult: ...
    def executable_lines(self, source: str, mod: ModuleFacts, entry: str) -> tuple[set[int], set[str]]: ...
    def mutation_ops(self) -> MutationOps: ...
    def normalize_result(self, r: CaseResult) -> CaseResult: ...

    # Steps 3 to 7
    def cost_table(self) -> dict[str, str]: ...
    def rule_pack(self) -> RulePack: ...
    def kb_dir(self) -> Path: ...
    def verify_rungs(self) -> list[Rung]: ...
    def bench_profile(self) -> BenchProfile: ...
    def security_profile(self) -> dict[str, Any]: ...
