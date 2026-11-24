"""Schemas for Step 9: Evaluation harness, benchmark metrics, ablations, and self-improvement."""
from __future__ import annotations

from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class ProgramCost(BaseModel):
    """Cost metrics incurred per task/program optimization."""
    model_config = ConfigDict(extra="allow")

    candidates_explored: int = 0
    elapsed_s: float = 0.0
    llm_calls: int = 0
    llm_tokens_prompt: int = 0
    llm_tokens_completion: int = 0
    estimated_cost_usd: float = 0.0


class DistributionStats(BaseModel):
    """Statistical summary for metric distributions across a benchmark suite."""
    model_config = ConfigDict(extra="allow")

    min: float = 0.0
    p25: float = 0.0
    median: float = 0.0
    p75: float = 0.0
    p90: float = 0.0
    max: float = 0.0
    mean: float = 0.0
    geom_mean: float = 0.0


class TaskSpec(BaseModel):
    """Specification of a benchmark or regression task."""
    model_config = ConfigDict(extra="allow")

    name: str
    source: str
    entry: str | None = None
    overrides: dict[str, Any] | None = None
    benchmark: str = "custom"                # pie | effibench | mercury | ecco | custom
    metadata: dict[str, Any] = Field(default_factory=dict)
    expected_speedup_min: float = 1.0
    expected_asymptotic_improvement: bool = False


class TaskEvaluation(BaseModel):
    """Evaluation metrics for a single task."""
    model_config = ConfigDict(extra="allow")

    name: str
    benchmark: str = "custom"
    verified: bool = False
    evidence_tier: str = "T0"
    speedup: float = 1.0
    mem_ratio: float = 1.0
    asymptotic_improved: bool = False
    complexity_before: str = "O(?)"
    complexity_after: str = "O(?)"
    false_claim: bool = False
    elapsed_s: float = 0.0
    passed_oracle: bool = False
    cost: ProgramCost = Field(default_factory=ProgramCost)
    failure_reason: str | None = None


class AblationVariant(BaseModel):
    """Configuration for an ablation experiment."""
    model_config = ConfigDict(extra="allow")

    id: str
    name: str
    category: str                            # proposer | verifier | search
    description: str = ""
    disabled_components: list[str] = Field(default_factory=list)


class AblationResult(BaseModel):
    """Results of running an ablation variant across a test suite."""
    model_config = ConfigDict(extra="allow")

    variant: AblationVariant
    total_tasks: int = 0
    correctness_rate: float = 0.0
    avg_speedup: float = 1.0
    false_claim_rate: float = 0.0
    elapsed_s: float = 0.0
    delta_correctness: float = 0.0           # vs baseline
    delta_speedup: float = 0.0               # vs baseline


class PreferencePair(BaseModel):
    """Pairwise preference record for DPO/RLHF self-improvement fine-tuning."""
    model_config = ConfigDict(extra="allow")

    task_name: str
    entry_point: str
    prompt: str
    original_code: str
    chosen_code: str
    rejected_code: str
    reward_chosen: float
    reward_rejected: float
    chosen_tier: str
    rejected_tier: str
    margin: float = 0.0
    rationale: str = ""


class EvalSuiteResult(BaseModel):
    """Aggregated metrics across a benchmark suite."""
    model_config = ConfigDict(extra="allow")

    schema_version: int = 1
    total_tasks: int = 0
    correctness_rate: float = 0.0            # Fraction of tasks preserving correctness
    avg_speedup: float = 1.0                 # Geometric mean of speedups
    speedup_distribution: DistributionStats = Field(default_factory=DistributionStats)
    memory_distribution: DistributionStats = Field(default_factory=DistributionStats)
    asymptotic_improvement_rate: float = 0.0
    asymptotic_transitions: list[str] = Field(default_factory=list)
    false_claim_rate: float = 0.0
    task_evaluations: list[TaskEvaluation] = Field(default_factory=list)
    avg_cost_per_program: ProgramCost = Field(default_factory=ProgramCost)
    ablations: list[AblationResult] = Field(default_factory=list)
    preference_pairs: list[PreferencePair] = Field(default_factory=list)
    elapsed_s: float = 0.0
