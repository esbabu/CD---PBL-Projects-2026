"""Typed WorkflowIntent and WorkflowProfile domain models and policy engine for NEXUS.

Enforces deterministic agent selection, strict DAG dependencies, read-only
invariants, safe model-assisted planning, and explicit intent classification.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set


class WorkflowIntent(str, Enum):
    """Explicit user engineering intents for NEXUS workflows."""

    ARCHITECTURE_ANALYSIS = "architecture_analysis"
    SECURITY_SCAN = "security_scan"
    SECURITY_REMEDIATION = "security_remediation"
    DOCUMENTATION = "documentation"
    OPTIMIZATION = "optimization"
    FULL_REVIEW = "full_review"
    CUSTOM = "custom"


@dataclass(frozen=True)
class WorkflowProfile:
    """Deterministic policy rules governing agent selection, safety, and dependencies."""

    intent: WorkflowIntent
    name: str
    description: str
    allowed_agents: List[str]
    read_only: bool
    requires_approval: bool
    verification_required: bool
    default_dependencies: Dict[str, List[str]]
    agent_reasons: Dict[str, str] = field(default_factory=dict)


# Stage numbers matching the standard pipeline
_AGENT_STAGE: Dict[str, int] = {
    "architect": 1,
    "optimizer": 2,
    "red_team": 3,
    "blue_team": 4,
    "docstring": 5,
    "audit": 6,
}

_AGENT_DISPLAY_NAMES: Dict[str, str] = {
    "architect": "ATLAS — Architecture Intelligence Agent",
    "optimizer": "FORGE — Code Engineering Agent",
    "red_team": "SENTINEL — Security Intelligence Agent",
    "blue_team": "REMEDY — Code Remediation Agent",
    "docstring": "SCRIBE — Documentation Intelligence Agent",
    "audit": "VERITY — Quality & Verification Agent",
}

_AGENT_DEFAULT_DESCRIPTIONS: Dict[str, str] = {
    "architect": "Analyze project structure, dependencies, and complexity; recommend architecture improvements.",
    "optimizer": "Analyze algorithmic complexity and synthesize non-regressive performance optimizations.",
    "red_team": "Perform static security analysis and report vulnerability evidence, locations, and risk.",
    "blue_team": "Use published security findings to prepare and validate a defensive code patch.",
    "docstring": "Use AST findings to prepare validated technical documentation and PEP-257 docstrings.",
    "audit": "Independently verify syntax, definition integrity, security regressions, and quality evidence.",
}

_AGENT_DEFAULT_TOOLS: Dict[str, List[str]] = {
    "architect": ["inspect_ast_structure", "infer_type_errors", "inspect_undefined_names"],
    "optimizer": ["detect_optimization_targets", "synthesize_optimization"],
    "red_team": ["probe_security_vulnerabilities"],
    "blue_team": ["synthesize_defensive_patch"],
    "docstring": ["inspect_ast_structure", "explain_ast_semantics"],
    "audit": ["verify_code_integrity", "compute_unified_diff", "probe_security_vulnerabilities", "evaluate_quality"],
}


POLICY_TABLE: Dict[WorkflowIntent, WorkflowProfile] = {
    WorkflowIntent.ARCHITECTURE_ANALYSIS: WorkflowProfile(
        intent=WorkflowIntent.ARCHITECTURE_ANALYSIS,
        name="Architecture Analysis",
        description="Inspect AST structure, call graph topology, and cyclomatic complexity (read-only).",
        allowed_agents=["architect"],
        read_only=True,
        requires_approval=False,
        verification_required=False,
        default_dependencies={"architect": []},
        agent_reasons={
            "architect": "Perceives AST topology, function definitions, class hierarchies, and complexity metrics without modifying source code."
        },
    ),
    WorkflowIntent.SECURITY_SCAN: WorkflowProfile(
        intent=WorkflowIntent.SECURITY_SCAN,
        name="Security Vulnerability Scan",
        description="Probe code for security vulnerabilities and injection sinks without patching (read-only).",
        allowed_agents=["red_team"],
        read_only=True,
        requires_approval=False,
        verification_required=False,
        default_dependencies={"red_team": []},
        agent_reasons={
            "red_team": "Probes code for injection sinks, insecure deserialization, SSRF, and credential leaks without modifying source code."
        },
    ),
    WorkflowIntent.SECURITY_REMEDIATION: WorkflowProfile(
        intent=WorkflowIntent.SECURITY_REMEDIATION,
        name="Security Remediation",
        description="Scan for vulnerabilities, synthesize defensive hardening patches, and verify non-regression.",
        allowed_agents=["red_team", "blue_team", "audit"],
        read_only=False,
        requires_approval=True,
        verification_required=True,
        default_dependencies={
            "red_team": [],
            "blue_team": ["red_team"],
            "audit": ["blue_team"],
        },
        agent_reasons={
            "red_team": "Identifies vulnerabilities, CWE classes, and sink locations requiring remediation.",
            "blue_team": "Synthesizes defensive code patches to neutralize identified flaws.",
            "audit": "Verifies that defensive patches preserve syntax and do not introduce regressions.",
        },
    ),
    WorkflowIntent.DOCUMENTATION: WorkflowProfile(
        intent=WorkflowIntent.DOCUMENTATION,
        name="Technical Documentation",
        description="Extract callable signatures and synthesize PEP-257 docstrings.",
        allowed_agents=["architect", "docstring", "audit"],
        read_only=False,
        requires_approval=True,
        verification_required=True,
        default_dependencies={
            "architect": [],
            "docstring": ["architect"],
            "audit": ["docstring"],
        },
        agent_reasons={
            "architect": "Extracts AST callable signatures, parameters, return types, and class context.",
            "docstring": "Synthesizes PEP-257 docstrings detailing parameters, return types, and logic explanations.",
            "audit": "Verifies that added docstrings preserve executable AST semantics and syntax.",
        },
    ),
    WorkflowIntent.OPTIMIZATION: WorkflowProfile(
        intent=WorkflowIntent.OPTIMIZATION,
        name="Algorithmic Optimization",
        description="Inspect loop complexity, optimize nested iterations, and verify behavioral equivalence.",
        allowed_agents=["architect", "optimizer", "audit"],
        read_only=False,
        requires_approval=True,
        verification_required=True,
        default_dependencies={
            "architect": [],
            "optimizer": ["architect"],
            "audit": ["optimizer"],
        },
        agent_reasons={
            "architect": "Extracts loop structures, call hierarchies, and architectural findings required for optimization.",
            "optimizer": "Refactors algorithmic bottlenecks, nested loops, and eager list allocations.",
            "audit": "Verifies syntax, definition preservation, and behavioral non-regression of optimizations.",
        },
    ),
    WorkflowIntent.FULL_REVIEW: WorkflowProfile(
        intent=WorkflowIntent.FULL_REVIEW,
        name="Full Project Review",
        description="Comprehensive multi-agent engineering lifecycle: architecture, optimization, red-team scan, blue-team defense, docstrings, and independent audit.",
        allowed_agents=["architect", "optimizer", "red_team", "blue_team", "docstring", "audit"],
        read_only=False,
        requires_approval=True,
        verification_required=True,
        default_dependencies={
            "architect": [],
            "red_team": [],
            "optimizer": ["architect"],
            "blue_team": ["red_team", "optimizer"],
            "docstring": ["architect", "blue_team"],
            "audit": ["optimizer", "blue_team", "docstring"],
        },
        agent_reasons={
            "architect": "Maps AST topology and modular dependencies.",
            "red_team": "Probes for CWE vulnerabilities and injection sinks.",
            "optimizer": "Identifies and resolves algorithmic bottlenecks after architecture inspection.",
            "blue_team": "Synthesizes defensive patches for detected security flaws.",
            "docstring": "Generates comprehensive PEP-257 docstrings for callables.",
            "audit": "Conducts independent quality, syntax, and security regression certification.",
        },
    ),
    WorkflowIntent.CUSTOM: WorkflowProfile(
        intent=WorkflowIntent.CUSTOM,
        name="Custom Workflow",
        description="User-defined workflow with explicit task graph and custom agent assignments.",
        allowed_agents=["architect", "optimizer", "red_team", "blue_team", "docstring", "audit"],
        read_only=False,
        requires_approval=True,
        verification_required=True,
        default_dependencies={
            "architect": [],
            "red_team": [],
            "optimizer": ["architect"],
            "blue_team": ["red_team", "optimizer"],
            "docstring": ["architect", "blue_team"],
            "audit": ["optimizer", "blue_team", "docstring"],
        },
        agent_reasons={
            "architect": "Custom stage: Architecture analysis.",
            "optimizer": "Custom stage: Performance optimization.",
            "red_team": "Custom stage: Security analysis.",
            "blue_team": "Custom stage: Defensive remediation.",
            "docstring": "Custom stage: Technical documentation.",
            "audit": "Custom stage: Verification audit.",
        },
    ),
}


# Intent Classification Regexes using Word Boundaries (\b)
_FULL_REVIEW_PATTERNS = [
    re.compile(r"\b(full\s+([a-z\-,\s]+\s+)?(review|audit|workflow|pipeline|swarm)|complete\s+([a-z\-,\s]+\s+)?review|end[- ]to[- ]end\s+([a-z\-,\s]+\s+)?(review|workflow|audit)|comprehensive\s+([a-z\-,\s]+\s+)?review)\b", re.I),
    re.compile(r"\b(all\s+six\s+specialists|full\s+swarm|complete\s+project\s+review)\b", re.I),
    re.compile(r"\b(performance\s+and\s+security\s+audit|security\s+and\s+performance\s+audit)\b", re.I),
]

_SECURITY_REMEDIATION_PATTERNS = [
    re.compile(r"\b(fix|patch|remediat\w*|harden\w*|defensive\s+patch\w*|neutraliz\w*)\b", re.I),
]
_SECURITY_WORDS = re.compile(r"\b(secur\w*|vulnerab\w*|cwe|attack\w*|flaw\w*|finding\w*|injection|sink\w*)\b", re.I)

_SECURITY_SCAN_PATTERNS = [
    re.compile(r"\b(security\s+(audit|scan|probe|review|check)|vulnerab\w*\s+scan|scan\s+for\s+vulnerab\w*|security\s+only|audit\s+security\s+only|scan\s+only)\b", re.I),
    re.compile(r"\b(scan\s+(for\s+)?(security\s+)?vulnerab\w*|probe\s+security)\b", re.I),
]

_OPTIMIZATION_PATTERNS = [
    re.compile(r"\b(optim\w*|bottleneck\w*|algorithmic\s+complexity|reduce\s+complexity|speed\s*up|performance\s+tuning|optimize\s+(this\s+)?(function|method|code|loop)|nested\s+loops)\b", re.I),
]

_DOCUMENTATION_PATTERNS = [
    re.compile(r"\b(docstring\w*|documentation|document\s+code|pep[- ]?257|comment\s+generation|document\s+callables|synthesize\s+(exhaustive\s+)?docstrings?)\b", re.I),
    re.compile(r"\b(explain\s+semantics|explain\s+this\s+code|explain\s+code|^explain$)\b", re.I),
]

_ARCHITECTURE_PATTERNS = [
    re.compile(r"\b(ast\s+(structure|topology|analysis)|call\s+graph|class\s+hierarchy|modular\s+analysis|architecture\s+analysis|inspect\s+ast|analyze\s+python\s+(code\s+)?ast|analyze\s+python\s+ast)\b", re.I),
    re.compile(r"\b(analyze\s+(this\s+)?code|inspect\s+(this\s+)?code|code\s+analysis)\b", re.I),
]

_VAGUE_TASKS = {
    "",
    "help",
    "run",
    "do it",
    "start",
    "go",
    "test",
    "please",
    "assist",
    "analyze",
    "check",
}


def classify_intent(task: str, explicit_intent: Optional[str] = None) -> WorkflowIntent:
    """Classify the user's explicit intent using word boundaries and priority rules.

    Raises ValueError on vague or empty inputs rather than silently launching a full review.
    """
    if explicit_intent:
        try:
            return WorkflowIntent(explicit_intent.strip().lower())
        except ValueError:
            pass

    normalized = (task or "").strip()
    if not normalized or normalized.lower() in _VAGUE_TASKS:
        raise ValueError(
            "Please specify an engineering task or select one of the suggested workflow profiles "
            "(e.g. 'Analyze Python AST structure', 'Scan for security vulnerabilities', "
            "'Fix security findings', 'Generate docstrings', or 'Optimize this function')."
        )

    task_lower = normalized.lower()

    # 1. Full Review Priority (Explicit compound phrase or multi-domain request)
    for pat in _FULL_REVIEW_PATTERNS:
        if pat.search(task_lower):
            return WorkflowIntent.FULL_REVIEW

    # Multi-domain detection: if user requests 2 or more distinct engineering disciplines
    has_sec = bool(re.search(r"\b(secur\w*|vulnerab\w*|cwe|attack\w*|flaw\w*|threat\w*)\b", task_lower))
    has_opt = bool(re.search(r"\b(optim\w*|speed\s*up|fast\w*|performance|bottleneck\w*)\b", task_lower))
    has_doc = bool(re.search(r"\b(docstring\w*|document\w*|pep[- ]?257|comment\w*|spec\w*)\b", task_lower))
    has_arch_or_qual = bool(
        re.search(
            r"\b(quality|code\s+quality|ast\s+(structure|topology)|call\s+graph|class\s+hierarchy|modular\s+analysis)\b",
            task_lower,
        )
    )
    domain_count = sum([has_sec, has_opt, has_doc, has_arch_or_qual])
    if domain_count >= 2:
        return WorkflowIntent.FULL_REVIEW

    # 2. Security Remediation (Must contain remediation action AND security terms)
    has_security_words = bool(_SECURITY_WORDS.search(task_lower))
    has_remediation_action = any(pat.search(task_lower) for pat in _SECURITY_REMEDIATION_PATTERNS)
    if has_security_words and has_remediation_action:
        return WorkflowIntent.SECURITY_REMEDIATION

    # 3. Security Scan (Security words without remediation actions, or with scan/probe/only)
    for pat in _SECURITY_SCAN_PATTERNS:
        if pat.search(task_lower):
            return WorkflowIntent.SECURITY_SCAN
    if has_security_words and not has_remediation_action:
        return WorkflowIntent.SECURITY_SCAN

    # 4. Optimization (Must have optimization verbs/terms)
    # Check that "complexity" isn't merely part of an AST topology analysis
    for pat in _OPTIMIZATION_PATTERNS:
        if pat.search(task_lower):
            # Guard: If task is explicitly "Analyze Python AST ... complexity ... call graph", it's architecture
            if not any(arch_pat.search(task_lower) for arch_pat in _ARCHITECTURE_PATTERNS):
                return WorkflowIntent.OPTIMIZATION

    # 5. Documentation
    for pat in _DOCUMENTATION_PATTERNS:
        if pat.search(task_lower):
            return WorkflowIntent.DOCUMENTATION

    # 6. Architecture Analysis
    for pat in _ARCHITECTURE_PATTERNS:
        if pat.search(task_lower):
            return WorkflowIntent.ARCHITECTURE_ANALYSIS

    # If it mentioned optimize after all:
    if "optimize" in task_lower or "optim" in task_lower:
        return WorkflowIntent.OPTIMIZATION

    # Fallback to Custom if user provided an articulated objective
    if len(normalized.split()) >= 3:
        return WorkflowIntent.CUSTOM

    raise ValueError(
        f"Could not determine engineering intent from '{normalized}'. "
        "Please provide a specific engineering goal or select a workflow preset."
    )


def validate_dag(plan: List[Dict[str, Any]], profile: Optional[WorkflowProfile] = None) -> None:
    """Validate that a task plan forms a strict, cycle-free DAG with valid dependencies and permissions.

    Enforces:
    - Non-empty plan.
    - All task IDs are valid specialist keys.
    - All task IDs belong to profile.allowed_agents (if profile provided).
    - All dependencies reference existing upstream tasks.
    - No circular dependencies (DFS cycle detection).
    - Input requirement integrity (e.g. optimizer depending on architect).
    - Parallel execution validity (parallel=True only when dependencies is empty).
    """
    if not isinstance(plan, list) or not plan:
        raise ValueError("Task plan must be a non-empty list of task specifications.")

    task_ids: Set[str] = set()
    for task in plan:
        if not isinstance(task, dict):
            raise ValueError("Each task in the plan must be a dictionary.")
        tid = task.get("task_id") or task.get("agent_key")
        if not tid or tid not in _AGENT_STAGE:
            raise ValueError(f"Invalid specialist task ID: {tid!r}.")
        if tid in task_ids:
            raise ValueError(f"Duplicate task ID in plan: {tid!r}.")
        task_ids.add(tid)

    if profile is not None:
        disallowed = task_ids - set(profile.allowed_agents)
        if disallowed:
            raise ValueError(
                f"Plan contains agents not permitted for intent '{profile.intent.value}': {sorted(disallowed)}."
            )

    # Dependency existence check
    for task in plan:
        tid = task["task_id"]
        deps = task.get("dependencies", [])
        if not isinstance(deps, list):
            raise ValueError(f"Task '{tid}' dependencies must be a list.")
        for dep in deps:
            if dep not in task_ids:
                raise ValueError(
                    f"Task '{tid}' depends on '{dep}', which is not present in the task plan."
                )
            if dep == tid:
                raise ValueError(f"Task '{tid}' cannot depend on itself.")

    # Cycle Detection using 3-color DFS
    # 0 = unvisited, 1 = visiting (in recursion stack), 2 = visited
    state: Dict[str, int] = {tid: 0 for tid in task_ids}
    adj: Dict[str, List[str]] = {
        task["task_id"]: task.get("dependencies", []) for task in plan
    }

    def dfs(node: str, path: List[str]) -> None:
        state[node] = 1
        path.append(node)
        for dep in adj.get(node, []):
            if state[dep] == 1:
                cycle_str = " -> ".join(path + [dep])
                raise ValueError(f"Cycle detected in task dependencies: {cycle_str}")
            if state[dep] == 0:
                dfs(dep, path)
        path.pop()
        state[node] = 2

    for tid in task_ids:
        if state[tid] == 0:
            dfs(tid, [])

    # Input Requirement & Dependency Invariants
    for task in plan:
        tid = task["task_id"]
        deps = task.get("dependencies", [])
        is_parallel = task.get("parallel", False)

        # A task with dependencies cannot execute in parallel at startup
        if deps and is_parallel:
            task["parallel"] = False

        # If optimizer is present and architect is present, optimizer must depend on architect
        if tid == "optimizer" and "architect" in task_ids:
            if "architect" not in deps:
                raise ValueError(
                    "Optimizer Agent (FORGE) consumes architecture_findings and must declare 'architect' as a dependency."
                )

        # If blue_team is present, it must depend on red_team
        if tid == "blue_team" and "red_team" in task_ids:
            if "red_team" not in deps:
                raise ValueError(
                    "Remediation Agent (REMEDY) consumes vulnerability findings and must declare 'red_team' as a dependency."
                )

        # If audit is present, it cannot be a root task when other tasks exist
        if tid == "audit" and len(task_ids) > 1:
            if not deps:
                raise ValueError(
                    "Verification Agent (VERITY) must depend on preceding workflow stages to verify deliverables."
                )


def build_deterministic_plan(
    intent: WorkflowIntent,
    task_description: str = "",
) -> List[Dict[str, Any]]:
    """Build the deterministic task plan DAG for a validated WorkflowIntent."""
    profile = POLICY_TABLE.get(intent, POLICY_TABLE[WorkflowIntent.CUSTOM])
    plan: List[Dict[str, Any]] = []

    for agent_key in profile.allowed_agents:
        stage = _AGENT_STAGE[agent_key]
        name = _AGENT_DISPLAY_NAMES[agent_key]
        desc = _AGENT_DEFAULT_DESCRIPTIONS[agent_key]
        tools = list(_AGENT_DEFAULT_TOOLS[agent_key])
        deps = list(profile.default_dependencies.get(agent_key, []))
        why = profile.agent_reasons.get(agent_key, desc)

        is_root = len(deps) == 0

        plan.append(
            {
                "task_id": agent_key,
                "stage": stage,
                "agent_key": agent_key,
                "assigned_agent": agent_key,
                "agent_name": name,
                "name": name,
                "objective": why,
                "description": desc,
                "why": why,
                "reason": why,
                "input_requirements": ["source_code"] + ([f"{dep}_findings" for dep in deps]),
                "expected_output": f"Validated deliverables from {name}",
                "dependencies": deps,
                "priority": "high" if agent_key in {"architect", "red_team", "blue_team"} else "medium",
                "risk_level": "high" if agent_key == "blue_team" else "medium" if agent_key == "optimizer" else "low",
                "required_tools": tools,
                "approval_requirements": {
                    "requires_approval": profile.requires_approval and agent_key in {"optimizer", "blue_team", "docstring"},
                    "reason": "Code modification candidate requires operator approval." if profile.requires_approval else "Read-only analysis.",
                },
                "completion_criteria": f"Successfully finished {agent_key} operational cycle without unhandled exceptions.",
                "parallel": is_root,
                "status": "pending",
            }
        )

    validate_dag(plan, profile)
    return plan


def validate_model_plan(
    raw_model_response: Any,
    profile: WorkflowProfile,
    tool_registry: Any = None,
) -> Optional[List[Dict[str, Any]]]:
    """Validate untrusted model-assisted plan against schema, allowlists, and DAG rules.

    Returns the validated plan or None to trigger deterministic fallback.
    """
    if not isinstance(raw_model_response, dict):
        return None

    tasks = raw_model_response.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        return None

    validated_plan: List[Dict[str, Any]] = []
    seen_ids: Set[str] = set()

    for item in tasks:
        if not isinstance(item, dict):
            return None

        tid = item.get("task_id") or item.get("assigned_agent")
        if not tid or tid not in profile.allowed_agents:
            # Model cannot add agents outside the approved profile
            return None

        if tid in seen_ids:
            return None
        seen_ids.add(tid)

        deps = item.get("dependencies", [])
        if not isinstance(deps, list):
            return None

        # Verify tools are allowlisted
        tools = item.get("required_tools", _AGENT_DEFAULT_TOOLS.get(tid, []))
        if not isinstance(tools, list):
            tools = _AGENT_DEFAULT_TOOLS.get(tid, [])
        else:
            allowed_specialist_tools = set(_AGENT_DEFAULT_TOOLS.get(tid, []))
            # Filter to strictly allowlisted tools
            tools = [t for t in tools if isinstance(t, str) and t in allowed_specialist_tools]
            if not tools:
                tools = list(_AGENT_DEFAULT_TOOLS.get(tid, []))

        stage = _AGENT_STAGE.get(tid, 1)
        name = _AGENT_DISPLAY_NAMES.get(tid, tid)
        desc = item.get("description") or _AGENT_DEFAULT_DESCRIPTIONS.get(tid, "")
        why = profile.agent_reasons.get(tid, desc)

        is_root = len(deps) == 0

        validated_plan.append(
            {
                "task_id": tid,
                "stage": stage,
                "agent_key": tid,
                "assigned_agent": tid,
                "agent_name": name,
                "name": name,
                "objective": str(item.get("objective") or why),
                "description": desc,
                "why": why,
                "reason": why,
                "input_requirements": item.get("input_requirements") or ["source_code"],
                "expected_output": str(item.get("expected_output") or f"Deliverable from {name}"),
                "dependencies": deps,
                "priority": str(item.get("priority") or "medium"),
                "risk_level": str(item.get("risk_level") or "low"),
                "required_tools": tools,
                "approval_requirements": item.get("approval_requirements") or {
                    "requires_approval": profile.requires_approval and tid in {"optimizer", "blue_team", "docstring"}
                },
                "completion_criteria": str(item.get("completion_criteria") or "Completed execution"),
                "parallel": is_root,
                "status": "pending",
            }
        )

    # Validate the full graph
    try:
        validate_dag(validated_plan, profile)
    except ValueError:
        return None

    return validated_plan
