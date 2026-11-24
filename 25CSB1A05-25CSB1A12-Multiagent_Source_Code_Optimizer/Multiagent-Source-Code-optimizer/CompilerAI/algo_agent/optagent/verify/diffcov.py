"""Changed-line coverage analysis (diffcov) for candidate transformations."""
from __future__ import annotations

import ast
import difflib
from dataclasses import dataclass, field
from pydantic import BaseModel, ConfigDict, Field


class DiffCovResult(BaseModel):
    """Report on changed lines and their coverage during execution."""
    model_config = ConfigDict(extra="allow")

    changed_lines: list[int] = Field(default_factory=list)
    executed_lines: list[int] = Field(default_factory=list)
    covered_lines: list[int] = Field(default_factory=list)
    missing_lines: list[int] = Field(default_factory=list)
    coverage_ratio: float = 1.0
    passed: bool = True


def get_executable_function_lines(source: str) -> set[int]:
    """Extract line numbers of executable statements inside functions in source."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return set()

    executable: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for child in ast.walk(node):
                if child is node:
                    continue
                if isinstance(child, ast.stmt):
                    # Skip docstrings
                    if (isinstance(child, ast.Expr) and
                            isinstance(getattr(child, "value", None), ast.Constant) and
                            isinstance(child.value.value, str)):
                        continue
                    if hasattr(child, "lineno"):
                        executable.add(child.lineno)
    return executable


def compute_changed_lines(original_source: str, candidate_source: str) -> set[int]:
    """Compute the set of 1-based line numbers in candidate that are changed and executable."""
    orig_lines = original_source.splitlines(keepends=True)
    cand_lines = candidate_source.splitlines(keepends=True)

    matcher = difflib.SequenceMatcher(None, orig_lines, cand_lines)
    raw_changed: set[int] = set()
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag in ("replace", "insert"):
            for line_no in range(j1 + 1, j2 + 1):
                raw_changed.add(line_no)

    executable = get_executable_function_lines(candidate_source)
    if not executable:
        # If no functions or statements inside functions, fallback to raw changed lines
        # that are not empty or comment-only
        fallback = set()
        for idx in raw_changed:
            if 1 <= idx <= len(cand_lines):
                line = cand_lines[idx - 1].strip()
                if line and not line.startswith("#"):
                    fallback.add(idx)
        return fallback

    return raw_changed & executable


def evaluate_diffcov(original_source: str, candidate_source: str,
                     executed_lines: set[int] | list[int],
                     min_ratio: float = 1.0) -> DiffCovResult:
    """Evaluate whether all changed lines were executed during verification."""
    changed = compute_changed_lines(original_source, candidate_source)
    exec_set = set(executed_lines)

    if not changed:
        return DiffCovResult(
            changed_lines=[],
            executed_lines=sorted(exec_set),
            covered_lines=[],
            missing_lines=[],
            coverage_ratio=1.0,
            passed=True,
        )

    covered = changed & exec_set
    missing = changed - exec_set
    ratio = len(covered) / len(changed)
    passed = ratio >= min_ratio

    return DiffCovResult(
        changed_lines=sorted(changed),
        executed_lines=sorted(exec_set),
        covered_lines=sorted(covered),
        missing_lines=sorted(missing),
        coverage_ratio=round(ratio, 4),
        passed=passed,
    )

