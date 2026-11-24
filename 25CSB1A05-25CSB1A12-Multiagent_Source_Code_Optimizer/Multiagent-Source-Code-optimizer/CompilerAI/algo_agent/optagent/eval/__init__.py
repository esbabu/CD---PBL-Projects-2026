"""Step 9 Evaluation: Benchmarking harness, regression suite, metrics, ablations, and self-improvement."""
from .ablation import AblationRunner, DEFAULT_PROPOSER_VARIANTS, DEFAULT_VERIFIER_VARIANTS
from .adapter import (
    load_benchmark_dataset,
    load_dataset_json,
    load_dataset_jsonl,
    load_ecco_dataset,
    load_effibench_dataset,
    load_mercury_dataset,
    load_pie_dataset,
    load_task_from_files,
)
from .harness import EvalHarness
from .metrics import build_suite_result, compute_distribution, detect_asymptotic_improvement
from .schemas import (
    AblationResult,
    AblationVariant,
    DistributionStats,
    EvalSuiteResult,
    PreferencePair,
    ProgramCost,
    TaskEvaluation,
    TaskSpec,
)
from .self_improve import PreferenceHarvester, reward_from_candidate

__all__ = [
    "EvalHarness",
    "TaskSpec",
    "TaskEvaluation",
    "EvalSuiteResult",
    "ProgramCost",
    "DistributionStats",
    "AblationVariant",
    "AblationResult",
    "PreferencePair",
    "AblationRunner",
    "PreferenceHarvester",
    "reward_from_candidate",
    "load_task_from_files",
    "load_dataset_json",
    "load_dataset_jsonl",
    "load_pie_dataset",
    "load_effibench_dataset",
    "load_mercury_dataset",
    "load_ecco_dataset",
    "load_benchmark_dataset",
    "compute_distribution",
    "detect_asymptotic_improvement",
    "build_suite_result",
    "DEFAULT_PROPOSER_VARIANTS",
    "DEFAULT_VERIFIER_VARIANTS",
]
