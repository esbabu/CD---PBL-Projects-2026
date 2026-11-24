"""PythonAdapter: thin wrapper delegating directly to existing Python pipeline."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from ..analysis.inputs import annotation_inputs, heuristic_seed_inputs
from ..analysis.static_facts import analyze_source, select_entry as py_select_entry
from ..complexity.static_cost import CALL_COSTS
from ..llm import prompts as P
from ..oracle.builder import executable_lines as py_executable_lines
from ..oracle.schema_infer import ParamSchema
from ..oracle.schemas import CaseResult
from ..proposers.kb.catalog import DEFAULT_RULES_YAML
from ..runtime.sandbox import PYTHON_PROFILE, SandboxProfile
from ..schemas import FunctionFacts, ModuleFacts
from .base import (
    BenchProfile,
    BuildResult,
    Capabilities,
    ContractRule,
    MutationOps,
    PromptPack,
    RulePack,
    Rung,
)


class PythonAdapter:
    """Thin wrapper over existing Python implementation (no logic moved)."""

    id: str = "python"
    display: str = "Python 3"
    extensions: tuple[str, ...] = (".py", ".pyw")
    caps: Capabilities = Capabilities(
        function_mode=True,
        program_mode=True,
        isolation_required=False,
        static_types=False,
        max_evidence_tier="T4",
        perturbation="hashseed",
    )

    # ---------- Step 1 ----------
    def analyze(self, source: str, hints: dict[str, Any]) -> ModuleFacts:
        return analyze_source(source)

    def select_entry(self, mod: ModuleFacts, requested: str | None) -> str:
        if not mod.functions and not requested:
            return "__script__"
        return py_select_entry(mod, requested, auto_select=True)

    def signature(self, fn: FunctionFacts) -> str:
        return P.signature_of(fn)

    def seed_inputs(self, fn: FunctionFacts | None, hints: dict[str, Any]) -> list[dict[str, Any]]:
        return heuristic_seed_inputs(
            fn,
            source=str(hints.get("_source", "")),
            strategy=str(hints.get("_strategy", "function")),
        )

    def param_schema(self, fn: FunctionFacts, hints: dict[str, Any], seeds: list[Any]) -> ParamSchema | None:
        return None  # infer from seeds using existing infer_params

    def prompt_pack(self) -> PromptPack:
        return PromptPack(
            language_name="python",
            code_fence="python",
            spec_system=P.SPEC_SYSTEM,
            spec_user=P.SPEC_USER,
            refine_user=P.REFINE_USER,
            input_system=P.INPUT_SYSTEM,
            input_user=P.INPUT_USER,
            predict_system=P.PREDICT_SYSTEM,
            predict_user=P.PREDICT_USER,
            proposer_rules="Keep identical Python function signature and standard library only.",
        )

    def contract_rules(self) -> list[ContractRule]:
        return []  # existing build_contract handles all Python aspects

    # ---------- Step 2 ----------
    def sandbox_profile(self, hints: dict[str, Any]) -> SandboxProfile:
        return PYTHON_PROFILE

    def build(self, source: str, entry: str, hints: dict[str, Any], workdir: Path) -> BuildResult:
        p = workdir / "target.py"
        p.write_text(source, encoding="utf-8")
        return BuildResult(ok=True, artifact_path=p)

    def executable_lines(self, source: str, mod: ModuleFacts, entry: str) -> tuple[set[int], set[str]]:
        return py_executable_lines(source, mod, entry)

    def mutation_ops(self) -> MutationOps:
        return MutationOps(language="python", generate=None, file_extension=".py")

    def normalize_result(self, r: CaseResult) -> CaseResult:
        return r

    # ---------- Steps 3 to 7 ----------
    def cost_table(self) -> dict[str, str]:
        return dict(CALL_COSTS)

    def rule_pack(self) -> RulePack:
        return RulePack(language="python", rules_yaml=DEFAULT_RULES_YAML, propose_fn=None)

    def kb_dir(self) -> Path:
        return DEFAULT_RULES_YAML.parent

    def verify_rungs(self) -> list[Rung]:
        return []

    def bench_profile(self) -> BenchProfile:
        return BenchProfile(language="python", warmups=2, reps=5)

    def security_profile(self) -> dict[str, Any]:
        return {
            "language": "python",
            "static_tools": ["ruff", "bandit"],
            "isolation": "docker_recommended",
            "forbidden_imports": ["os.system", "subprocess", "socket", "urllib", "http"],
            "sandbox_flags": ["--network", "none", "--read-only", "--cap-drop", "ALL"],
        }
