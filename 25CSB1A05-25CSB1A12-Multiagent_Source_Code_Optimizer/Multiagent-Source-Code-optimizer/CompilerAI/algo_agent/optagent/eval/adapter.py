"""Dataset adapters for loading benchmark tasks (PIE, EffiBench, Mercury, ECCO, local files)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any
import yaml

from .schemas import TaskSpec


def load_task_from_files(
    source_path: str | Path,
    overrides_path: str | Path | None = None,
    name: str | None = None,
    benchmark: str = "custom",
) -> TaskSpec:
    """Load a benchmark task from a Python source file and optional YAML overrides."""
    sp = Path(source_path)
    src = sp.read_text(encoding="utf-8")
    overrides: dict[str, Any] | None = None
    if overrides_path:
        op = Path(overrides_path)
        if op.exists():
            overrides = yaml.safe_load(op.read_text(encoding="utf-8"))

    task_name = name or sp.stem
    return TaskSpec(
        name=task_name,
        source=src,
        entry=None,
        overrides=overrides,
        benchmark=benchmark,
    )


def load_dataset_json(json_path: str | Path, benchmark: str = "custom") -> list[TaskSpec]:
    """Load tasks from a standard JSON format file."""
    jp = Path(json_path)
    content = jp.read_text(encoding="utf-8").strip()
    if not content:
        return []
    data = json.loads(content)
    tasks: list[TaskSpec] = []
    items = data if isinstance(data, list) else data.get("tasks", [])
    for it in items:
        tasks.append(
            TaskSpec(
                name=it.get("task_id", it.get("name", "task")),
                source=it["source"],
                entry=it.get("entry_point"),
                overrides=it.get("overrides"),
                benchmark=benchmark,
                metadata=it.get("metadata", {}),
            )
        )
    return tasks


def load_dataset_jsonl(jsonl_path: str | Path, benchmark: str = "custom") -> list[TaskSpec]:
    """Load tasks from a JSON-Lines file."""
    jp = Path(jsonl_path)
    tasks: list[TaskSpec] = []
    for line in jp.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        it = json.loads(line)
        tasks.append(
            TaskSpec(
                name=it.get("task_id", it.get("name", "task")),
                source=it.get("source") or it.get("code") or it.get("input_code", ""),
                entry=it.get("entry_point") or it.get("entry"),
                overrides=it.get("overrides"),
                benchmark=benchmark,
                metadata=it.get("metadata", {}),
            )
        )
    return tasks


def load_pie_dataset(path: str | Path) -> list[TaskSpec]:
    """Adapter for PIE (Python Code Optimization Benchmark) dataset."""
    p = Path(path)
    raw_items: list[dict] = []
    if p.suffix == ".jsonl":
        for line in p.read_text(encoding="utf-8").splitlines():
            if line.strip():
                raw_items.append(json.loads(line))
    else:
        loaded = json.loads(p.read_text(encoding="utf-8"))
        raw_items = loaded if isinstance(loaded, list) else loaded.get("problems", [])

    tasks: list[TaskSpec] = []
    for it in raw_items:
        task_id = str(it.get("problem_id", it.get("task_id", "pie_task")))
        # In PIE, input_code is the slow/unoptimized submission
        source = it.get("input_code", it.get("slow_code", it.get("source", "")))
        entry = it.get("entry_point", None)

        overrides = {}
        if "test_cases" in it:
            overrides["inputs"] = [{"args": tc.get("input", tc)} for tc in it["test_cases"]]
        elif "unit_tests" in it:
            overrides["unit_tests"] = it["unit_tests"]

        metadata = {
            "reference_code": it.get("reference_code", it.get("fast_code")),
            "cpu_time_limit": it.get("cpu_time_limit"),
        }

        tasks.append(
            TaskSpec(
                name=f"pie_{task_id}",
                source=source,
                entry=entry,
                overrides=overrides or None,
                benchmark="pie",
                metadata=metadata,
                expected_speedup_min=1.5,
            )
        )
    return tasks


def load_effibench_dataset(path: str | Path) -> list[TaskSpec]:
    """Adapter for EffiBench (Code Efficiency Benchmark for LLMs) dataset."""
    p = Path(path)
    raw_items = json.loads(p.read_text(encoding="utf-8"))
    items = raw_items if isinstance(raw_items, list) else raw_items.get("tasks", [])

    tasks: list[TaskSpec] = []
    for it in items:
        task_id = it.get("task_id", it.get("id", "effibench_task"))
        source = it.get("unoptimized_code", it.get("source", it.get("canonical_solution", "")))
        entry = it.get("entry_point")

        overrides = {}
        if "inputs" in it:
            overrides["inputs"] = it["inputs"]
        elif "test" in it:
            overrides["test_code"] = it["test"]

        tasks.append(
            TaskSpec(
                name=f"effibench_{task_id}",
                source=source,
                entry=entry,
                overrides=overrides or None,
                benchmark="effibench",
                metadata={"prompt": it.get("prompt")},
                expected_speedup_min=1.2,
            )
        )
    return tasks


def load_mercury_dataset(path: str | Path) -> list[TaskSpec]:
    """Adapter for Mercury (Competitive Programming Efficiency Benchmark) dataset."""
    p = Path(path)
    raw_items = json.loads(p.read_text(encoding="utf-8"))
    items = raw_items if isinstance(raw_items, list) else raw_items.get("problems", [])

    tasks: list[TaskSpec] = []
    for it in items:
        task_id = it.get("id", it.get("task_id", "mercury_task"))
        source = it.get("code", it.get("solution", it.get("source", "")))
        entry = it.get("entry_point", "solve")

        overrides = {}
        if "test_cases" in it:
            overrides["inputs"] = [{"args": tc.get("args", [tc.get("input")])} for tc in it["test_cases"]]

        metadata = {
            "time_limit_ms": it.get("time_limit", 2000),
            "memory_limit_mb": it.get("memory_limit", 256),
        }

        tasks.append(
            TaskSpec(
                name=f"mercury_{task_id}",
                source=source,
                entry=entry,
                overrides=overrides or None,
                benchmark="mercury",
                metadata=metadata,
                expected_speedup_min=1.5,
            )
        )
    return tasks


def load_ecco_dataset(path: str | Path) -> list[TaskSpec]:
    """Adapter for ECCO (Empirical Code Complexity and Optimization) dataset."""
    p = Path(path)
    raw_items = json.loads(p.read_text(encoding="utf-8"))
    items = raw_items if isinstance(raw_items, list) else raw_items.get("benchmarks", [])

    tasks: list[TaskSpec] = []
    for it in items:
        task_id = it.get("task_id", it.get("name", "ecco_task"))
        source = it.get("unoptimized_code", it.get("source", ""))
        entry = it.get("entry_point")

        overrides = {}
        if "inputs" in it:
            overrides["inputs"] = it["inputs"]

        metadata = {
            "claimed_complexity": it.get("complexity", "O(n^2)"),
            "target_complexity": it.get("target_complexity", "O(n)"),
        }

        tasks.append(
            TaskSpec(
                name=f"ecco_{task_id}",
                source=source,
                entry=entry,
                overrides=overrides or None,
                benchmark="ecco",
                metadata=metadata,
                expected_speedup_min=2.0,
                expected_asymptotic_improvement=True,
            )
        )
    return tasks


def load_benchmark_dataset(path: str | Path, benchmark_type: str = "auto") -> list[TaskSpec]:
    """Auto-detecting and format-specific loader for all supported benchmarks."""
    p = Path(path)
    b_type = benchmark_type.lower()

    if b_type == "pie":
        return load_pie_dataset(p)
    if b_type == "effibench":
        return load_effibench_dataset(p)
    if b_type == "mercury":
        return load_mercury_dataset(p)
    if b_type == "ecco":
        return load_ecco_dataset(p)

    # Auto-detect mode
    if p.suffix == ".jsonl":
        first_line = p.read_text(encoding="utf-8").splitlines()[0]
        sample = json.loads(first_line)
    else:
        content = p.read_text(encoding="utf-8").strip()
        data = json.loads(content)
        sample = data[0] if isinstance(data, list) and data else data

    if "problem_id" in sample and ("input_code" in sample or "slow_code" in sample):
        return load_pie_dataset(p)
    if "canonical_solution" in sample or "prompt" in sample:
        return load_effibench_dataset(p)
    if "time_limit" in sample or "memory_limit" in sample:
        return load_mercury_dataset(p)
    if "unoptimized_code" in sample and "target_complexity" in sample:
        return load_ecco_dataset(p)

    if p.suffix == ".jsonl":
        return load_dataset_jsonl(p)
    return load_dataset_json(p)
