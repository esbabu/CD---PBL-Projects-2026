"""Architectural enforcement tests for Heuristic vs LLM separation (Workstream D)."""
from __future__ import annotations

import ast
import socket
from pathlib import Path
import pytest

from optagent.agent import OptimizerAgent, OptimizeRequest
from optagent.config import Settings
from optagent.core.outcome import SupportLevel
from optagent.core.provenance import ComponentKind, get_component_registry
from optagent.search.schemas import SearchBudget

OPTAGENT_ROOT = Path(__file__).resolve().parent.parent / "optagent"
FORBIDDEN_HTTP_LIBS = {"litellm", "openai", "anthropic", "httpx", "requests", "aiohttp"}


def test_no_llm_or_http_imports_outside_llm_package():
    """No module outside `optagent/llm/` may import HTTP/LLM client libraries directly."""
    violations: list[str] = []
    for pyfile in sorted(OPTAGENT_ROOT.rglob("*.py")):
        if "__pycache__" in pyfile.parts:
            continue
        rel = pyfile.relative_to(OPTAGENT_ROOT).as_posix()
        if rel.startswith("llm/") or rel in ("doctor.py", "service/app.py"):
            continue
        tree = ast.parse(pyfile.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    top = alias.name.split(".")[0]
                    if top in FORBIDDEN_HTTP_LIBS:
                        violations.append(f"{rel}:{node.lineno}: import {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    top = node.module.split(".")[0]
                    if top in FORBIDDEN_HTTP_LIBS:
                        violations.append(f"{rel}:{node.lineno}: from {node.module} import ...")
    assert not violations, "Direct LLM/HTTP imports outside optagent/llm/:\n" + "\n".join(violations)


def test_no_litellm_anywhere_in_codebase():
    """litellm must be completely removed from optagent/."""
    hits: list[str] = []
    for pyfile in sorted(OPTAGENT_ROOT.rglob("*.py")):
        if "__pycache__" in pyfile.parts:
            continue
        tree = ast.parse(pyfile.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for a in node.names:
                    if a.name.split(".")[0] == "litellm":
                        hits.append(str(pyfile))
            elif isinstance(node, ast.ImportFrom) and node.module and node.module.split(".")[0] == "litellm":
                hits.append(str(pyfile))
    assert not hits, f"Found forbidden litellm imports: {hits}"


def test_heuristic_path_works_with_llm_off_and_sockets_blocked(tmp_path, monkeypatch):
    """LLM_MODE=off must make zero network calls and still produce FULL/VERIFIED_WEAK."""
    def _deny_socket(*args, **kwargs):
        raise RuntimeError("Network sockets are blocked in LLM_MODE=off test!")

    monkeypatch.setattr(socket, "create_connection", _deny_socket)

    s = Settings(
        sandbox_backend="local",
        llm_mode="off",
        runs_dir=str(tmp_path / "runs"),
        memory_db_path=str(tmp_path / "mem.db"),
        n_family=8,
        n_hypothesis=8,
        n_probe=3,
        n_adversarial=2,
        fuzz_budget_s=0.3,
        fuzz_max_rounds=1,
        max_mutants=3,
        scale_sizes=(10, 20),
        ladder_fresh_inputs=20,
        ladder_fuzz_budget_s=0.3,
        bench_warmups=1,
        bench_reps=2,
        search_max_depth=1,
        search_max_candidates=2,
    )
    src = (
        "def two_sum(nums: list[int], target: int) -> list[int]:\n"
        "    for i in range(len(nums)):\n"
        "        for j in range(i + 1, len(nums)):\n"
        "            if nums[i] + nums[j] == target:\n"
        "                return [i, j]\n"
        "    return []\n"
    )
    agent = OptimizerAgent(s, log=lambda *a: None)
    res = agent.run(OptimizeRequest(source=src, use_llm=False, llm_mode="off", budget=SearchBudget(max_candidates=2, max_time_s=10.0)))
    assert res.status == "ok"
    assert res.outcome is not None
    assert res.outcome.support_level in (SupportLevel.FULL, SupportLevel.VERIFIED_WEAK)
    assert res.outcome.provenance.llm_calls == 0
    assert res.outcome.provenance.counts["heuristic"] >= 1


def test_component_registry_populated():
    import optagent.core.triage  # noqa: F401
    import optagent.analysis.inputs  # noqa: F401

    entries = get_component_registry()
    assert len(entries) >= 3
    assert any(e.kind == ComponentKind.HEURISTIC for e in entries)
