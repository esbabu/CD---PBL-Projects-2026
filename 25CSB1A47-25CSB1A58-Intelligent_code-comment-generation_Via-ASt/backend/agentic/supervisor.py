"""Dependency-aware supervisor for the stateful agentic workflow."""

from __future__ import annotations

import ast
import difflib
import hashlib
import json
import logging
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional

from backend import model_provider
from backend.config import AppConfig
from backend.model_provider import provider_ready
from backend.agentic.agents.specialists import (
    ArchitectAgent,
    AuditAgent,
    BlueTeamAgent,
    DocstringAgent,
    OptimizerAgent,
    RedTeamAgent,
)
from backend.agentic.intent import (
    POLICY_TABLE,
    WorkflowIntent,
    WorkflowProfile,
    build_deterministic_plan,
    classify_intent,
    validate_dag,
    validate_model_plan,
)
from backend.agentic.session import AgentSession
from backend.agentic.provider_adapter import ProviderAdapterError
from backend.agentic.tools.registry import ToolRegistry
from backend.patch_safety import validate_patch_structural_safety
from backend.validator import validate_code, validate_generated_code

logger = logging.getLogger(__name__)

MAX_CONCURRENT_SPECIALISTS: int = 3

_AGENT_STAGE = {
    "architect": 1,
    "optimizer": 2,
    "red_team": 3,
    "blue_team": 4,
    "docstring": 5,
    "audit": 6,
}


class SupervisorAgent:
    """Inspect goals/code, delegate dependent tasks, and independently audit candidates."""

    def __init__(
        self,
        tools: ToolRegistry,
        model_client: Any = None,
        model_name: Optional[str] = None,
        event_callback: Optional[Callable[[str, Dict[str, Any]], None]] = None,
    ) -> None:
        self.tools = tools
        self.model_client = model_client
        self.model_name = model_name or model_provider.MODEL_NAME
        self.emit_event = event_callback or (lambda event, payload: None)
        self.swarm = {
            "architect": ArchitectAgent(tools, model_client),
            "optimizer": OptimizerAgent(tools, model_client),
            "red_team": RedTeamAgent(tools, model_client),
            "blue_team": BlueTeamAgent(tools, model_client),
            "docstring": DocstringAgent(tools, model_client),
            "audit": AuditAgent(tools, model_client),
        }
        for agent_key, agent in self.swarm.items():
            agent.agent_key = agent_key

    def perceive(self, session: AgentSession) -> Dict[str, Any]:
        """PERCEIVE: Inspect user objective, analyze AST topology, type integrity, and security metrics."""
        architecture = self._supervisor_tool(
            session,
            "inspect_ast_structure",
            {"source_code": session.original_code},
            task_id="planning_ast",
        )
        if architecture.get("status") != "success":
            raise RuntimeError(
                "Supervisor could not inspect the original source for planning: "
                + architecture.get("error", "AST analysis failed.")
            )
        structure = architecture.get("result", {})
        functions = structure.get("functions", [])
        classes = structure.get("classes", [])
        missing_docstrings = [
            item for item in functions if not item.get("docstring")
        ]
        complexity = structure.get("file_cyclomatic_complexity", 1)

        goal = session.task.strip()
        goal_lower = goal.lower()
        full_review = not goal_lower or (
            "improve code quality and security" in goal_lower
        ) or any(
            word in goal_lower
            for word in ("full", "complete", "comprehensive", "end-to-end", "all")
        )
        performance_requested = full_review or any(
            word in goal_lower
            for word in ("optim", "performance", "speed", "fast", "complexity")
        )
        documentation_requested = full_review or any(
            word in goal_lower
            for word in ("docstring", "documentation", "comment", "explain", "spec")
        )
        if (
            missing_docstrings
            and not any(
                word in goal_lower
                for word in ("security only", "security audit", "vulnerability scan")
            )
        ):
            documentation_requested = documentation_requested or any(
                word in goal_lower for word in ("quality", "improve", "review")
            )
        remediation_requested = any(
            word in goal_lower
            for word in ("fix", "patch", "remediat", "harden", "defense", "defensive")
        )

        mode = session.metadata.get("execution_mode", "deterministic")
        model_ready = bool(
            mode != "deterministic"
            and self.model_client is not None
            and getattr(self.model_client, "chat", None)
            and AppConfig.AI_PROVIDER != "ast"
            and provider_ready(self.model_client)
        )

        return {
            "goal": goal,
            "goal_lower": goal_lower,
            "full_review": full_review,
            "performance_requested": performance_requested,
            "documentation_requested": documentation_requested,
            "remediation_requested": remediation_requested,
            "structure": structure,
            "functions": functions,
            "classes": classes,
            "missing_docstrings": missing_docstrings,
            "complexity": complexity,
            "model_ready": model_ready,
        }

    def _model_assisted_plan(
        self,
        session: AgentSession,
        perception: Dict[str, Any],
        profile: WorkflowProfile,
    ) -> Optional[List[Dict[str, Any]]]:
        """Ask model provider to perceive objective, AST facts, and formulate plan within the approved profile."""
        if session.metadata.get("execution_mode") == "deterministic":
            return None
        model_client = getattr(session, "model_client", None) or self.model_client
        if not model_client or not getattr(model_client, "chat", None):
            if session.metadata.get("require_model"):
                raise RuntimeError("The required AI model client is unavailable.")
            return None

        prompt = (
            f"User Goal: {perception['goal']}\n"
            f"Approved Workflow Profile: {profile.name} ({profile.intent.value})\n"
            f"Allowed Specialists: {profile.allowed_agents}\n"
            f"Read-Only Invariant: {profile.read_only}\n\n"
            f"Perceived AST Structure Facts:\n"
            f"- Functions ({len(perception['functions'])}): {[f.get('name') for f in perception['functions']]}\n"
            f"- Classes ({len(perception['classes'])}): {[c.get('name') for c in perception['classes']]}\n"
            f"- Missing Docstrings: {[f.get('name') for f in perception['missing_docstrings']]}\n"
            f"- Cyclomatic Complexity: {perception['complexity']}\n\n"
            "Produce an autonomous multi-agent task execution plan as a valid JSON object with key 'tasks'.\n"
            "Each task must contain:\n"
            f"  'task_id': one of {profile.allowed_agents}\n"
            "  'objective': specific single-sentence objective\n"
            "  'input_requirements': list of inputs required\n"
            "  'expected_output': concrete deliverable expected\n"
            "  'dependencies': list of prerequisite task_ids within this plan\n"
            "  'priority': high | medium | low\n"
            "  'risk_level': high | medium | low\n"
            "  'required_tools': list of registered tools needed\n"
            "  'approval_requirements': object or boolean\n"
            "  'completion_criteria': explicit condition for completion\n"
            "Constraint: Do not add any agents outside the allowed specialists."
        )
        try:
            resp = model_client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are NEXUS, an autonomous AI multi-agent orchestrator. Return only valid JSON."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,
                max_tokens=1000,
            )
            raw = resp.choices[0].message.content or ""
            cleaned = raw.strip()
            if cleaned.startswith("```"):
                lines = cleaned.splitlines()
                if len(lines) >= 3 and lines[-1].strip().startswith("```"):
                    cleaned = "\n".join(lines[1:-1]).strip()
            parsed = json.loads(cleaned)
            tasks = parsed.get("tasks", [])
            if not isinstance(tasks, list) or not tasks:
                if session.metadata.get("require_model"):
                    raise RuntimeError("The required model returned an empty workflow plan.")
                return None
            return parsed
        except Exception as exc:
            if session.metadata.get("require_model"):
                logger.warning(
                    "Required model-assisted planning failed (%s).",
                    type(exc).__name__,
                )
                if isinstance(exc, ProviderAdapterError):
                    raise
                raise RuntimeError(
                    f"Required model-assisted planning failed ({type(exc).__name__})."
                ) from exc
            logger.warning("Model-assisted planning failed (%s), falling back to deterministic planning.", exc)
            return None

    def generate_plan(self, session: AgentSession) -> List[Dict[str, Any]]:
        """Build a structured, goal- and AST-aware task graph with complete metadata."""
        if session.plan:
            validate_dag(session.plan)
            return session.plan

        goal = (session.task or "").strip()
        explicit_intent = session.metadata.get("intent")

        try:
            intent = classify_intent(goal, explicit_intent=explicit_intent)
        except ValueError as exc:
            if explicit_intent:
                try:
                    intent = WorkflowIntent(explicit_intent.strip().lower())
                except ValueError:
                    raise exc
            else:
                raise exc

        profile = POLICY_TABLE.get(intent, POLICY_TABLE[WorkflowIntent.CUSTOM])
        session.metadata["intent"] = intent.value
        session.metadata["profile_name"] = profile.name
        session.metadata["read_only"] = profile.read_only
        session.metadata["verification_required"] = profile.verification_required

        deterministic_plan = build_deterministic_plan(intent, goal)
        perception = self.perceive(session)
        perception["intent"] = intent.value

        planning_mode = "deterministic_policy"
        if perception["model_ready"]:
            raw_model_tasks = self._model_assisted_plan(session, perception, profile)
            if raw_model_tasks:
                validated_model_plan = validate_model_plan(raw_model_tasks, profile, self.tools)
                if validated_model_plan:
                    session.plan = validated_model_plan
                    planning_mode = "model-assisted"
                    session.metadata["planning"] = {
                        "mode": planning_mode,
                        "intent": intent.value,
                        "goal": goal,
                        "selected_agents": [item["agent_key"] for item in validated_model_plan],
                        "why_agents": profile.agent_reasons,
                        "function_count": perception["structure"].get("function_count", 0),
                        "class_count": perception["structure"].get("class_count", 0),
                        "cyclomatic_complexity": perception["complexity"],
                        "model_assisted": True,
                    }
                    return validated_model_plan

        session.plan = deterministic_plan
        session.metadata["planning"] = {
            "mode": planning_mode,
            "intent": intent.value,
            "goal": goal,
            "selected_agents": [item["agent_key"] for item in deterministic_plan],
            "why_agents": profile.agent_reasons,
            "function_count": perception["structure"].get("function_count", 0),
            "class_count": perception["structure"].get("class_count", 0),
            "cyclomatic_complexity": perception["complexity"],
            "model_assisted": False,
        }
        return deterministic_plan

    plan = generate_plan

    def _emit_legacy_event(
        self, session: AgentSession, event: str, agent: str, **details: Any
    ) -> None:
        """Keep existing event names available to older API clients."""
        session.emit_event(
            event,
            agent=agent,
            status=details.pop("status", session.status),
            **details,
        )

    def _run_agent_task(
        self, session: AgentSession, task: Dict[str, Any]
    ) -> Dict[str, Any]:
        agent_key = task["agent_key"]
        agent = self.swarm[agent_key]
        task_id = task["task_id"]
        started = time.perf_counter()
        started_at = datetime.now(timezone.utc).isoformat()
        session.update_task(
            task_id,
            status="in_progress",
            started_at=started_at,
        )
        session.emit_event(
            "agent_started",
            agent=agent_key,
            status="running",
            task_id=task_id,
            stage=task["stage"],
            task=task["name"],
            description=task["description"],
            execution_mode=(
                "model"
                if getattr(agent.model_client, "chat", None)
                else "deterministic"
            ),
            model_name=agent.model_name,
        )
        self._emit_legacy_event(
            session,
            "subagent_started",
            agent.name,
            status="running",
            task_id=task_id,
            stage=task["stage"],
            agent_key=agent_key,
            task=task["name"],
        )

        try:
            turn_count = 0
            while turn_count < 4:
                result = agent.execute_turn(
                    session,
                    sub_task=task["description"],
                    task_id=task_id,
                )
                turn_count += 1
                if result.get("status") != "in_progress":
                    break
            if (
                result.get("status") == "in_progress"
                and session.has_successful_tool_observation(agent_key, task_id)
            ):
                result = agent.finish_from_observations(
                    session, task_id, execution_mode="model"
                )
            elif result.get("status") == "in_progress":
                result = agent._run_deterministic_turn(
                    session,
                    sub_task=task["description"],
                    fallback_reason="model_turn_limit_without_successful_tool",
                    task_id=task_id,
                )
            if result.get("status") == "pending_approval":
                duration_ms = round((time.perf_counter() - started) * 1000, 3)
                session.update_task(
                    task_id,
                    status="awaiting_approval",
                    duration_ms=duration_ms,
                    pending_tool=result.get("tool"),
                )
                session.set_status("awaiting_approval")
                return {
                    "task_id": task_id,
                    "agent_key": agent_key,
                    "status": "awaiting_approval",
                    "duration_ms": duration_ms,
                    "result": result,
                }
            if result.get("status") != "completed":
                raise RuntimeError(
                    f"{agent.name} did not complete within the bounded turn limit."
                )

            if result.get("candidate_code") is not None:
                candidate_str = result["candidate_code"]
                session.emit_event(
                    "candidate_proposed",
                    agent=agent_key,
                    status="proposed",
                    task_id=task_id,
                    stage=task["stage"],
                    candidate_execution_mode=result.get("candidate_execution_mode", "deterministic"),
                    candidate_length=len(candidate_str) if isinstance(candidate_str, str) else 0,
                    code_changed=candidate_str != session.current_code,
                )

            findings = (
                result.get("findings")
                or result.get("vulnerabilities")
                or result.get("opportunities")
                or []
            )
            if not isinstance(findings, list):
                raise TypeError(f"{agent.name} returned non-list findings.")
            published = session.publish_findings(
                agent_key, findings, task_id=task_id
            )
            duration_ms = round((time.perf_counter() - started) * 1000, 3)
            completed_at = datetime.now(timezone.utc).isoformat()
            execution_mode = result.get("execution_mode", "deterministic")
            summary = result.get("summary", "")
            session.update_task(
                task_id,
                status="completed",
                summary=summary,
                findings=published,
                findings_count=len(published),
                started_at=started_at,
                completed_at=completed_at,
                duration_ms=duration_ms,
                execution_mode=execution_mode,
                candidate_execution_mode=result.get("candidate_execution_mode"),
                fallback_reason=result.get("fallback_reason"),
                turn_count=turn_count,
                candidate_proposed=bool(result.get("candidate_code")),
            )
            event_data = {
                "task_id": task_id,
                "stage": task["stage"],
                "agent_key": agent_key,
                "summary": summary,
                "findings": published,
                "findings_count": len(published),
                "started_at": started_at,
                "completed_at": completed_at,
                "duration_ms": duration_ms,
                "execution_mode": execution_mode,
                "turn_count": turn_count,
                "fallback_reason": result.get("fallback_reason"),
                "candidate_proposed": bool(result.get("candidate_code")),
                "code_modified": False,
                "candidate_execution_mode": result.get(
                    "candidate_execution_mode"
                ),
            }
            session.emit_event(
                "agent_completed",
                agent=agent_key,
                status="completed",
                **event_data,
            )
            self._emit_legacy_event(
                session,
                "subagent_completed",
                agent.name,
                status="completed",
                **event_data,
            )
            return {
                "task_id": task_id,
                "agent_key": agent_key,
                "status": "completed",
                "duration_ms": duration_ms,
                "execution_mode": execution_mode,
                "result": result,
            }
        except Exception as exc:
            duration_ms = round((time.perf_counter() - started) * 1000, 3)
            completed_at = datetime.now(timezone.utc).isoformat()
            session.update_task(
                task_id,
                status="failed",
                error=str(exc),
                completed_at=completed_at,
                duration_ms=duration_ms,
            )
            failure = {
                "task_id": task_id,
                "stage": task["stage"],
                "agent_key": agent_key,
                "error": str(exc),
                "error_type": type(exc).__name__,
                "duration_ms": duration_ms,
                "completed_at": completed_at,
            }
            session.emit_event(
                "agent_failed",
                agent=agent_key,
                status="failed",
                **failure,
            )
            self._emit_legacy_event(
                session,
                "subagent_failed",
                agent.name,
                status="failed",
                **failure,
            )
            logger.exception("Agent task %s failed", task_id)
            return {
                "task_id": task_id,
                "agent_key": agent_key,
                "status": "failed",
                "duration_ms": duration_ms,
                "error": str(exc),
            }

    def _supervisor_tool(
        self,
        session: AgentSession,
        tool_name: str,
        arguments: Dict[str, Any],
        *,
        task_id: str,
    ) -> Dict[str, Any]:
        path = arguments.get("path") or arguments.get("file")
        start_line = arguments.get("start_line")
        end_line = arguments.get("end_line")
        line_range = None
        if start_line is not None and end_line is not None:
            line_range = f"{start_line}-{end_line}"
        elif start_line is not None:
            line_range = f"{start_line}"

        session.emit_event(
            "tool_started",
            agent="SupervisorAgent",
            status="running",
            task_id=task_id,
            tool=tool_name,
            argument_names=sorted(arguments),
            path=path,
            start_line=start_line,
            end_line=end_line,
            line_range=line_range,
        )
        result = self.tools.execute(tool_name, arguments, context=session)
        duration_ms = float(result.get("execution_time_ms", 0.0))
        session.record_tool_observation(
            "SupervisorAgent", task_id, tool_name, arguments, result, duration_ms
        )
        res_data = result.get("result") if isinstance(result.get("result"), dict) else {}
        event_path = path or res_data.get("path")
        event_start = start_line if start_line is not None else res_data.get("start_line")
        event_end = end_line if end_line is not None else res_data.get("end_line")
        if line_range is None and event_start is not None and event_end is not None:
            event_line_range = f"{event_start}-{event_end}"
        else:
            event_line_range = line_range

        session.emit_event(
            "tool_completed",
            agent="SupervisorAgent",
            status=result.get("status", "error"),
            task_id=task_id,
            tool=tool_name,
            duration_ms=duration_ms,
            path=event_path,
            start_line=event_start,
            end_line=event_end,
            line_range=event_line_range,
            observation={
                "status": result.get("status"),
                "result_keys": sorted(result.get("result", {}))
                if isinstance(result.get("result"), dict)
                else [],
                "error": result.get("error"),
                "path": event_path,
                "line_range": event_line_range,
            },
        )
        return result

    @staticmethod
    def _definition_manifest(source_code: str) -> List[str]:
        def dump_nodes(nodes: List[ast.AST]) -> str:
            return json.dumps(
                [ast.dump(node, include_attributes=False) for node in nodes],
                separators=(",", ":"),
            )

        class DefinitionVisitor(ast.NodeVisitor):
            def __init__(self) -> None:
                self.scope: List[str] = []
                self.manifest: List[str] = []

            def visit_ClassDef(self, node: ast.ClassDef) -> None:
                self.manifest.append(
                    "|".join(
                        (
                            "ClassDef",
                            ".".join([*self.scope, node.name]),
                            dump_nodes(node.bases),
                            dump_nodes(node.keywords),
                            dump_nodes(node.decorator_list),
                        )
                    )
                )
                self.scope.append(node.name)
                self.generic_visit(node)
                self.scope.pop()

            def _visit_function(
                self, node: ast.FunctionDef | ast.AsyncFunctionDef
            ) -> None:
                self.manifest.append(
                    "|".join(
                        (
                            type(node).__name__,
                            ".".join([*self.scope, node.name]),
                            ast.dump(node.args, include_attributes=False),
                            ast.dump(node.returns, include_attributes=False)
                            if node.returns
                            else "",
                            dump_nodes(node.decorator_list),
                            node.type_comment or "",
                        )
                    )
                )
                self.scope.append(node.name)
                self.generic_visit(node)
                self.scope.pop()

            def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
                self._visit_function(node)

            def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
                self._visit_function(node)

        visitor = DefinitionVisitor()
        visitor.visit(ast.parse(source_code))
        return sorted(visitor.manifest)

    @staticmethod
    def _import_manifest(source_code: str) -> List[str]:
        tree = ast.parse(source_code)
        return sorted(
            ast.dump(node, include_attributes=False)
            for node in ast.walk(tree)
            if isinstance(node, (ast.Import, ast.ImportFrom))
        )

    @staticmethod
    def _import_roots(source_code: str) -> set[str]:
        tree = ast.parse(source_code)
        roots = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                roots.update(alias.name.split(".", 1)[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                roots.add(node.module.split(".", 1)[0])
        return roots

    @staticmethod
    def _security_counts(tool_result: Dict[str, Any]) -> Counter:
        scenarios = tool_result.get("result", {}).get("scenarios", [])
        return Counter(
            (
                item.get("cwe", ""),
                item.get("category", ""),
                item.get("name", ""),
            )
            for item in scenarios
            if isinstance(item, dict)
        )

    def _audit_from_observations(
        self, session: AgentSession, task_id: str
    ) -> Dict[str, Any]:
        observations = {
            item["tool"]: item["result"]
            for item in session.tool_observations
            if item["agent"] == "audit" and item["task_id"] == task_id
        }
        required_tools = {
            "verify_code_integrity",
            "probe_security_vulnerabilities",
            "evaluate_quality",
            "compute_unified_diff",
        }
        missing_tools = sorted(
            name
            for name in required_tools
            if observations.get(name, {}).get("status") != "success"
        )
        integrity = observations.get("verify_code_integrity", {}).get("result", {})
        if not integrity:
            integrity_tool = self._supervisor_tool(
                session,
                "verify_code_integrity",
                {
                    "original_code": session.original_code,
                    "candidate_code": session.current_code,
                    "allow_executable_changes": True,
                },
                task_id="supervisor_integrity_check",
            )
            integrity = integrity_tool.get("result", {})

        current_security = observations.get(
            "probe_security_vulnerabilities", {}
        ).get("result", {})
        quality = observations.get("evaluate_quality", {}).get("result", {})
        diff = observations.get("compute_unified_diff", {}).get("result", {})
        if not diff:
            diff_tool = self._supervisor_tool(
                session,
                "compute_unified_diff",
                {
                    "original_code": session.original_code,
                    "candidate_code": session.current_code,
                },
                task_id="supervisor_diff_check",
            )
            diff = diff_tool.get("result", {})

        initial_findings = session.get_findings("red_team")
        initial_counts = Counter(
            (item.get("cwe", ""), item.get("category", ""), item.get("name", ""))
            for item in initial_findings
        )
        current_findings = current_security.get("scenarios", []) or initial_findings
        current_counts = Counter(
            (item.get("cwe", ""), item.get("category", ""), item.get("name", ""))
            for item in current_findings
            if isinstance(item, dict)
        )
        regressions = list((current_counts - initial_counts).elements())
        audit_task = session.tasks.get("audit", {})
        has_audit_task = bool(audit_task)

        from backend.agentic.verification_contract import build_unified_audit
        from backend.agentic.verification_contract import (
            approval_record_for_current_code,
        )

        approval_record = approval_record_for_current_code(session)

        audit = build_unified_audit(
            integrity_result=integrity,
            security_findings=current_findings,
            security_regressions=regressions,
            type_errors=observations.get("infer_type_errors", {}).get("result", {}).get("definite_type_errors", []),
            behavioral_results=observations.get("run_isolated_behavioral_tests", {}).get("result"),
            is_approved=approval_record is not None,
            code_changed=session.current_code.strip() != session.original_code.strip(),
            quality_result=quality,
            diff_data=diff,
            approval_record=approval_record,
            missing_tools=missing_tools if has_audit_task else [],
            security_checked=bool("probe_security_vulnerabilities" in observations or initial_findings),
            types_checked=bool("infer_type_errors" in observations),
        )
        session.final_audit = audit
        session.emit_event(
            "verification_completed",
            agent="audit",
            status=audit["status"],
            verification_level=audit["verification_level"],
            audit=audit,
        )
        session.emit_event(
            "artifact_verified",
            agent="audit",
            status=audit["status"],
            task_id=task_id,
            audit=audit,
            checks={
                "syntax_valid": audit["checks"]["syntax"]["status"] == "passed",
                "definitions_preserved": audit["checks"]["definitions"]["status"] == "passed",
                "all_passed": audit["passed"],
            },
        )
        return audit

    def _validate_and_apply_candidate(
        self,
        session: AgentSession,
        task: Dict[str, Any],
        result: Dict[str, Any],
    ) -> Dict[str, Any]:
        agent_key = task["agent_key"]
        candidate = result.get("candidate_code")
        before = session.current_code
        outcome: Dict[str, Any] = {
            "agent_key": agent_key,
            "status": "no_candidate",
            "changed": False,
            "checks": {},
        }
        if candidate is None or candidate == before:
            if candidate is not None:
                session.record_modification(
                    {
                        "agent": agent_key,
                        "status": "no_op",
                        "before_digest": hashlib.sha256(
                            before.encode("utf-8")
                        ).hexdigest(),
                    }
                )
            return outcome

        checkpoint = session.create_checkpoint(
            f"Before {agent_key} candidate",
            {"task_id": task["task_id"], "agent": agent_key},
        )
        before_digest = hashlib.sha256(before.encode("utf-8")).hexdigest()
        candidate_digest = (
            hashlib.sha256(candidate.encode("utf-8")).hexdigest()
            if isinstance(candidate, str)
            else ""
        )
        errors: List[str] = []
        checks: Dict[str, Any] = {}
        if not isinstance(candidate, str):
            errors.append("Candidate source must be a string.")
        elif len(candidate) > 50000:
            errors.append("Candidate exceeds the source size limit.")
        else:
            syntax_result = validate_code(candidate)
            checks["syntax_valid"] = syntax_result is True
            if syntax_result is not True:
                errors.append(f"Candidate syntax validation failed: {syntax_result}")
            else:
                checks["definitions_preserved"] = (
                    self._definition_manifest(before)
                    == self._definition_manifest(candidate)
                )
                if not checks["definitions_preserved"]:
                    errors.append("Candidate changed a function or class definition/signature.")
                original_imports = Counter(self._import_manifest(before))
                candidate_imports = Counter(self._import_manifest(candidate))
                new_imports = candidate_imports - original_imports
                new_import_statements = list(new_imports.elements())
                candidate_new_roots = (
                    self._import_roots(candidate) - self._import_roots(before)
                )
                allowed_blue_imports = {"ast", "json", "os", "shlex", "subprocess"}
                approved_new_imports = (
                    agent_key == "blue_team"
                    and candidate_new_roots.issubset(allowed_blue_imports)
                )
                checks["new_imports"] = new_import_statements
                checks["approved_new_imports"] = (
                    sorted(candidate_new_roots) if approved_new_imports else []
                )
                if new_imports and not approved_new_imports:
                    errors.append("Candidate introduced an unreviewed import.")

                # Comprehensive AST structural safety check
                structural_check = validate_patch_structural_safety(
                    before,
                    candidate,
                    allowed_new_imports=allowed_blue_imports if agent_key == "blue_team" else None,
                )
                checks["structural_safety"] = structural_check["checks"]
                if not structural_check["is_safe"]:
                    for iss in structural_check["issues"]:
                        if iss not in errors:
                            errors.append(iss)
                static_regression_tools = {
                    "infer_type_errors": "definite_type_errors",
                    "inspect_undefined_names": "undefined_names",
                }
                for tool_name, finding_key in static_regression_tools.items():
                    baseline_result = self._supervisor_tool(
                        session,
                        tool_name,
                        {"source_code": before},
                        task_id=task["task_id"],
                    )
                    candidate_result = self._supervisor_tool(
                        session,
                        tool_name,
                        {"source_code": candidate},
                        task_id=task["task_id"],
                    )
                    if (
                        baseline_result.get("status") != "success"
                        or candidate_result.get("status") != "success"
                    ):
                        errors.append(
                            f"Static regression check '{tool_name}' could not be completed."
                        )
                        checks[f"{tool_name}_completed"] = False
                        continue
                    baseline_findings = baseline_result.get("result", {}).get(
                        finding_key, []
                    )
                    candidate_findings = candidate_result.get("result", {}).get(
                        finding_key, []
                    )

                    def fingerprint(item: Any) -> str:
                        if isinstance(item, dict):
                            stable = {
                                key: value
                                for key, value in item.items()
                                if key
                                not in {
                                    "line",
                                    "lineno",
                                    "column",
                                    "col_offset",
                                    "end_lineno",
                                    "end_col_offset",
                                    "finding_id",
                                    "published_at",
                                    "task_id",
                                    "source_agent",
                                }
                            }
                            return json.dumps(stable, sort_keys=True, default=str)
                        return json.dumps(item, sort_keys=True, default=str)

                    regressions = list(
                        (
                            Counter(fingerprint(item) for item in candidate_findings)
                            - Counter(fingerprint(item) for item in baseline_findings)
                        ).elements()
                    )
                    checks[f"{tool_name}_regressions"] = regressions
                    if regressions:
                        errors.append(
                            f"Candidate introduced new findings in '{tool_name}'."
                        )
                if agent_key == "docstring":
                    documentation_check = validate_generated_code(before, candidate)
                    checks["documentation_preserved_executable_ast"] = (
                        documentation_check.get("is_valid", False)
                    )
                    if not checks["documentation_preserved_executable_ast"]:
                        errors.extend(documentation_check.get("issues", []))

                before_security = self._supervisor_tool(
                    session,
                    "probe_security_vulnerabilities",
                    {"source_code": before},
                    task_id=task["task_id"],
                )
                after_security = self._supervisor_tool(
                    session,
                    "probe_security_vulnerabilities",
                    {"source_code": candidate},
                    task_id=task["task_id"],
                )
                if (
                    before_security.get("status") != "success"
                    or after_security.get("status") != "success"
                ):
                    checks["security_check_completed"] = False
                    errors.append("Static security regression check could not be completed.")
                else:
                    before_counts = self._security_counts(before_security)
                    after_counts = self._security_counts(after_security)
                    regressions = after_counts - before_counts
                    checks["security_check_completed"] = True
                    checks["security_regressions"] = list(regressions.elements())
                    checks["security_findings_before"] = sum(before_counts.values())
                    checks["security_findings_after"] = sum(after_counts.values())
                    if regressions:
                        errors.append("Candidate introduced new static security findings.")
                    if (
                        agent_key == "blue_team"
                        and before_counts
                        and sum(after_counts.values()) >= sum(before_counts.values())
                    ):
                        errors.append(
                            "REMEDY candidate did not reduce the reported static findings."
                        )

        accepted = not errors
        needs_approval = accepted and candidate != before
        if not accepted:
            if not session.rollback_to(checkpoint.id):
                raise RuntimeError(
                    f"Could not roll back rejected candidate to checkpoint '{checkpoint.id}'."
                )
        diff = "".join(
            difflib.unified_diff(
                before.splitlines(keepends=True),
                candidate.splitlines(keepends=True),
                fromfile="original.py",
                tofile="candidate.py",
            )
        ) if needs_approval else ""
        outcome = {
            "agent_key": agent_key,
            "status": "awaiting_approval" if needs_approval else "rejected",
            "changed": False,
            "checks": checks,
            "errors": errors,
            "rejection_explanation": "; ".join(errors) if errors else None,
            "acceptance_explanation": "Candidate passed all structural safety and non-regression checks." if accepted else None,
            "checkpoint_id": checkpoint.id,
            "before_digest": before_digest,
            "candidate_digest": candidate_digest,
            "diff": diff,
            "generation_mode": result.get(
                "candidate_execution_mode", result.get("execution_mode")
            ),
            "after_digest": before_digest,
            "behavioral_tests_run": False,
        }
        if needs_approval:
            session.pending_approval = {
                "agent": agent_key,
                "task_id": task["task_id"],
                "tool": "apply_candidate",
                "candidate_code": candidate,
                "candidate_digest": candidate_digest,
                "before_digest": before_digest,
                "checkpoint_id": checkpoint.id,
                "candidate_validation": checks,
                "diff": diff,
            }
            session.approval_status = "pending"
            session.set_status("awaiting_approval")
        session.record_modification(outcome)
        task_updates = {
            "candidate_status": outcome["status"],
            "candidate_validation": checks,
            "candidate_errors": errors,
            "code_modified": False,
        }
        if needs_approval:
            task_updates["status"] = "awaiting_approval"
        session.update_task(task["task_id"], **task_updates)
        session.emit_event(
            "candidate_validated",
            agent=agent_key,
            status="pending_approval" if needs_approval else outcome["status"],
            task_id=task["task_id"],
            stage=task["stage"],
            code_modified=outcome["changed"],
            candidate_status=outcome["status"],
            candidate_errors=errors,
            candidate_validation=checks,
        )
        if errors:
            session.emit_event(
                "review_critique",
                agent="audit",
                target_agent=agent_key,
                status="rejected",
                task_id=task["task_id"],
                stage=task["stage"],
                critique=errors,
                candidate_status="rejected",
                candidate_errors=errors,
                feedback_loop=True,
            )
            session.send_message(
                "SupervisorAgent",
                agent_key,
                "Candidate rejected by deterministic validation: "
                + "; ".join(errors),
                evidence_finding_ids=[
                    finding.get("finding_id")
                    for finding in session.get_findings(agent_key)
                    if finding.get("finding_id")
                ],
            )
        else:
            session.emit_event(
                "artifact_verified",
                agent="audit",
                target_agent=agent_key,
                status="verified",
                task_id=task["task_id"],
                stage=task["stage"],
                code_modified=outcome["changed"],
                validation=checks,
            )
            if needs_approval:
                session.emit_event(
                    "approval_required",
                    agent=agent_key,
                    status="pending",
                    task_id=task["task_id"],
                    tool="apply_candidate",
                    candidate_code=candidate,
                    candidate_digest=candidate_digest,
                    diff=diff,
                    candidate_validation=checks,
                )
            session.send_message(
                "SupervisorAgent",
                agent_key,
                "Candidate passed the recorded syntax, definition, import, and static-security checks.",
                evidence_finding_ids=[
                    finding.get("finding_id")
                    for finding in session.get_findings(agent_key)
                    if finding.get("finding_id")
                ],
            )
        return outcome

    def _skip_task(
        self, session: AgentSession, task: Dict[str, Any], reason: str
    ) -> None:
        session.update_task(task["task_id"], status="skipped", skip_reason=reason)
        session.emit_event(
            "agent_completed",
            agent=task["agent_key"],
            status="skipped",
            task_id=task["task_id"],
            stage=task["stage"],
            summary=reason,
            findings=[],
            findings_count=0,
            duration_ms=0.0,
        )
        self._emit_legacy_event(
            session,
            "subagent_skipped",
            task["agent_name"],
            status="skipped",
            task_id=task["task_id"],
            stage=task["stage"],
            agent_key=task["agent_key"],
            reason=reason,
        )

    def run(self, session: AgentSession) -> Dict[str, Any]:
        """Run adaptive multi-agent execution loop implementing:
        PERCEIVE → PLAN → DELEGATE → ACT → OBSERVE → EVALUATE → REPLAN → VERIFY → REPORT
        """
        session.set_status("planning")

        # 1. PERCEIVE & PREFLIGHT
        if session.cancel_requested:
            session.set_status("cancelled")
            cancelled_payload = {
                "status": "cancelled",
                "session_id": session.session_id,
                "original_code": session.original_code,
                "final_code": session.current_code,
                "code_changed": session.current_code.strip() != session.original_code.strip(),
                "plan": session.plan,
                "tasks": session.tasks,
                "trajectory_steps": len(session.trajectory),
                "model_call_count": int(session.metadata.get("model_call_count", 0)),
            }
            session.emit_event(
                "workflow_cancelled",
                agent="SupervisorAgent",
                **cancelled_payload,
            )
            return cancelled_payload

        # 2. PLAN
        if not session.plan:
            plan = self.generate_plan(session)
        else:
            plan = session.plan
        for task in plan:
            if task["task_id"] not in session.tasks:
                session.assign_task(task)

        session.emit_event(
            "plan_created",
            agent="SupervisorAgent",
            status="planned",
            goal=session.task,
            plan=plan,
            planning=session.metadata.get("planning", {}),
            execution_mode=session.metadata.get("execution_mode", "deterministic"),
        )
        candidate_outcomes: List[Dict[str, Any]] = list(
            session.metadata.get("candidate_outcomes", [])
        )

        # 3. ADAPTIVE LOOP CONTROLS (No unlimited loops: bounded by iterations, tasks, wall-clock, and budgets)
        workflow_start_time = time.perf_counter()
        timeout_seconds = float(session.metadata.get("timeout_seconds", 120.0))
        max_iterations = int(session.metadata.get("max_iterations", 8))
        max_tasks = int(session.metadata.get("max_tasks", 16))
        max_review_cycles = int(session.metadata.get("max_review_cycles", 5))
        iteration = 0
        tasks_executed = 0
        retry_counts: Dict[str, int] = {}

        while True:
            # Cancellation check
            if session.cancel_requested:
                session.set_status("cancelled")
                cancelled_payload = {
                    "status": "cancelled",
                    "session_id": session.session_id,
                    "original_code": session.original_code,
                    "final_code": session.current_code,
                    "code_changed": session.current_code.strip() != session.original_code.strip(),
                    "plan": session.plan,
                    "tasks": session.tasks,
                    "trajectory_steps": len(session.trajectory),
                    "model_call_count": int(session.metadata.get("model_call_count", 0)),
                }
                session.emit_event(
                    "workflow_cancelled",
                    agent="SupervisorAgent",
                    **cancelled_payload,
                )
                return cancelled_payload

            # Wall-clock timeout check
            if time.perf_counter() - workflow_start_time > timeout_seconds:
                logger.warning(
                    "Workflow session %s reached wall-clock timeout (%ss)",
                    session.session_id,
                    timeout_seconds,
                )
                break

            # Iteration & task count guardrails
            if iteration >= max_iterations or tasks_executed >= max_tasks:
                logger.warning(
                    "Workflow session %s reached loop limits (iterations=%s, tasks=%s)",
                    session.session_id,
                    iteration,
                    tasks_executed,
                )
                break
            iteration += 1

            # 4. DELEGATE (Find Ready Tasks in Current Plan Graph)
            pending = [
                task
                for task in session.plan
                if session.tasks[task["task_id"]]["status"] in {"pending", "in_progress"}
            ]
            if not pending:
                break

            ready: List[Dict[str, Any]] = []
            for task in pending:
                dependency_states = [
                    session.tasks.get(dependency, {}).get("status")
                    for dependency in task.get("dependencies", [])
                ]
                if not all(
                    state in {"completed", "skipped", "failed"}
                    for state in dependency_states
                ):
                    continue
                if task["agent_key"] != "audit" and "failed" in dependency_states:
                    self._skip_task(
                        session, task, "A required upstream task failed."
                    )
                    continue
                if (
                    task["agent_key"] == "blue_team"
                    and not session.get_findings("red_team")
                ):
                    self._skip_task(
                        session,
                        task,
                        "SENTINEL published no findings requiring remediation.",
                    )
                    continue
                ready.append(task)

            if not ready:
                awaiting = [
                    task
                    for task in session.plan
                    if session.tasks[task["task_id"]]["status"] == "awaiting_approval"
                ]
                if awaiting:
                    session.set_status("awaiting_approval")
                    return {
                        "status": "awaiting_approval",
                        "session_id": session.session_id,
                        "task": session.task,
                        "execution_mode": session.metadata.get("execution_mode", "deterministic"),
                        "max_review_cycles": session.metadata.get("max_review_cycles", 5),
                        "pending_approval": session.pending_approval,
                        "plan": session.plan,
                        "tasks": session.tasks,
                    }
                if any(
                    session.tasks[task["task_id"]]["status"] in {"pending", "in_progress"}
                    for task in session.plan
                ):
                    raise RuntimeError("Supervisor task graph has unresolved dependencies.")
                break

            # 5. ACT (Execute Ready Batch)
            parallel_tasks = [task for task in ready if task.get("parallel") and not task.get("dependencies")]
            sequential_tasks = [task for task in ready if not task.get("parallel") or task.get("dependencies")]
            batch = parallel_tasks[:MAX_CONCURRENT_SPECIALISTS] or sequential_tasks[:1]
            batch_results: Dict[str, Dict[str, Any]] = {}
            try:
                with ThreadPoolExecutor(
                    max_workers=max(1, min(MAX_CONCURRENT_SPECIALISTS, len(batch))),
                    thread_name_prefix="agentic-specialist",
                ) as executor:
                    futures = {
                        executor.submit(self._run_agent_task, session, task): task
                        for task in batch
                    }
                    for future in as_completed(futures):
                        task = futures[future]
                        batch_results[task["task_id"]] = future.result()
            except RuntimeError as exc:
                if "shutdown" in str(exc).lower() or "cannot schedule new futures" in str(exc).lower():
                    for task in batch:
                        if task["task_id"] not in batch_results:
                            batch_results[task["task_id"]] = self._run_agent_task(session, task)
                else:
                    raise
            tasks_executed += len(batch)

            # 6. OBSERVE & EVALUATE & REPLAN
            for task in batch:
                task_result = batch_results[task["task_id"]]
                if task_result["status"] == "awaiting_approval":
                    session.set_status("awaiting_approval")
                    return {
                        "status": "awaiting_approval",
                        "session_id": session.session_id,
                        "task": session.task,
                        "execution_mode": session.metadata.get("execution_mode", "deterministic"),
                        "max_review_cycles": session.metadata.get("max_review_cycles", 5),
                        "pending_approval": session.pending_approval,
                        "plan": session.plan,
                        "tasks": session.tasks,
                    }
                if task_result["status"] != "completed":
                    continue
                result = task_result["result"]
                if result.get("candidate_code") is not None:
                    outcome = self._validate_and_apply_candidate(
                        session, task, result
                    )
                    candidate_outcomes.append(outcome)
                    session.metadata["candidate_outcomes"] = candidate_outcomes
                    result["candidate_validation"] = outcome

                    if outcome.get("status") == "awaiting_approval":
                        return {
                            "status": "awaiting_approval",
                            "session_id": session.session_id,
                            "task": session.task,
                            "execution_mode": session.metadata.get("execution_mode", "deterministic"),
                            "max_review_cycles": session.metadata.get("max_review_cycles", 5),
                            "pending_approval": session.pending_approval,
                            "plan": session.plan,
                            "tasks": session.tasks,
                            "candidate_outcomes": candidate_outcomes,
                        }

                    # Closed-Loop Self-Correction Retry when candidate rejected
                    if outcome.get("status") == "rejected":
                        agent_key = task["agent_key"]
                        retries = retry_counts.get(agent_key, 0)
                        if retries < max_review_cycles:
                            retry_counts[agent_key] = retries + 1
                            critique_errors = outcome.get("errors", [])
                            session.update_task(task["task_id"], status="pending")
                            task["status"] = "pending"
                            session.emit_event(
                                "workflow_replanned",
                                agent="SupervisorAgent",
                                status="replanned",
                                reason="Self-correction retry after validation critique",
                                target_agent=agent_key,
                                review_cycle=retries + 1,
                                max_cycles=max_review_cycles,
                                critique=critique_errors,
                            )
                            session.emit_event(
                                "plan_updated",
                                agent="SupervisorAgent",
                                status="updated",
                                plan=session.plan,
                                reason=f"Retrying {agent_key} after critique",
                            )

                # Real Agent Communication: Structured Handoffs
                if task["agent_key"] == "red_team":
                    findings = session.get_findings("red_team")
                    finding_ids = [item["finding_id"] for item in findings if item.get("finding_id")]
                    locations = [item.get("line") or item.get("lineno") for item in findings if item.get("line") or item.get("lineno")]
                    has_blue_in_plan = any(item["agent_key"] == "blue_team" for item in session.plan)

                    # Dynamic Delegation: ONLY if the workflow profile is NOT read-only and explicitly allows remediation
                    profile_intent = session.metadata.get("intent")
                    is_read_only = bool(session.metadata.get("read_only", False))
                    allows_remediation = profile_intent in {
                        WorkflowIntent.SECURITY_REMEDIATION.value,
                        WorkflowIntent.FULL_REVIEW.value,
                        WorkflowIntent.CUSTOM.value,
                    }

                    if findings and not has_blue_in_plan and not is_read_only and allows_remediation:
                        blue_task = {
                            "task_id": "blue_team",
                            "stage": 4,
                            "agent_key": "blue_team",
                            "assigned_agent": "blue_team",
                            "agent_name": "REMEDY — Code Remediation Agent",
                            "name": "REMEDY — Code Remediation Agent",
                            "objective": "Synthesize targeted defensive patch for findings discovered by SENTINEL.",
                            "description": "Use published security findings to prepare and validate a defensive code candidate.",
                            "input_requirements": ["source_code", "upstream_security_findings"],
                            "expected_output": "Defensive remediation candidate neutralizing reported vulnerabilities with verifiable controls",
                            "dependencies": ["red_team"],
                            "priority": "high",
                            "risk_level": "high",
                            "required_tools": ["synthesize_defensive_patch"],
                            "approval_requirements": {"requires_approval": False, "reason": "Defensive patch verified before merge"},
                            "completion_criteria": "Neutralized reported vulnerabilities without introducing syntax or regression errors",
                            "parallel": False,
                            "status": "pending",
                        }
                        session.plan.append(blue_task)
                        session.assign_task(blue_task)
                        for t in session.plan:
                            if t["agent_key"] == "audit" and "blue_team" not in t.get("dependencies", []):
                                t.setdefault("dependencies", []).append("blue_team")
                                session.update_task(t["task_id"], dependencies=t["dependencies"])
                        has_blue_in_plan = True
                        session.emit_event(
                            "workflow_replanned",
                            agent="SupervisorAgent",
                            status="replanned",
                            reason="Discovered security vulnerabilities requiring defensive remediation",
                            plan=session.plan,
                        )
                        session.emit_event(
                            "plan_updated",
                            agent="SupervisorAgent",
                            status="updated",
                            plan=session.plan,
                            reason="Added REMEDY defensive remediation",
                        )

                    if findings and has_blue_in_plan:
                        session.send_message(
                            "red_team",
                            "blue_team",
                            f"SENTINEL published {len(findings)} vulnerability finding(s). Handing off structured evidence for defensive remediation.",
                            evidence_finding_ids=finding_ids,
                            structured_payload={
                                "finding_ids": finding_ids,
                                "evidence": [item.get("summary") or item.get("name") for item in findings],
                                "source_locations": locations,
                                "agent_identity": "SENTINEL",
                                "confidence": "high",
                                "proposed_actions": ["synthesize_defensive_patch"],
                                "validation_status": "unverified",
                            },
                        )

                if task["agent_key"] == "architect" and any(item["agent_key"] == "docstring" for item in session.plan):
                    architecture = session.get_findings("architect")
                    arch_ids = [item["finding_id"] for item in architecture if item.get("finding_id")]
                    fn_count = session.metadata.get("planning", {}).get("function_count", 0)
                    session.send_message(
                        "architect",
                        "docstring",
                        f"ATLAS reported {fn_count} function(s); use the published architecture evidence when preparing documentation.",
                        evidence_finding_ids=arch_ids,
                        structured_payload={
                            "finding_ids": arch_ids,
                            "evidence": architecture,
                            "source_locations": [],
                            "agent_identity": "ATLAS",
                            "confidence": "high",
                            "proposed_actions": ["explain_ast_semantics", "generate_docstrings"],
                            "validation_status": "unverified",
                        },
                    )

                # Route downstream dependency handoffs
                dependent_tasks = [
                    downstream
                    for downstream in session.plan
                    if task["task_id"] in downstream.get("dependencies", [])
                ]
                if dependent_tasks:
                    agent = self.swarm[task["agent_key"]]
                    findings = session.get_findings(task["agent_key"])
                    summary = result.get("summary") or "Task completed with no summary."
                    evidence_ids = [
                        item["finding_id"]
                        for item in findings
                        if item.get("finding_id")
                    ]
                    message = (
                        f"{agent.name} completed {task['name']}. {summary} "
                        f"Published {len(findings)} deliverable finding(s)."
                    )
                    for downstream in dependent_tasks:
                        session.send_message(
                            task["agent_key"],
                            downstream["agent_key"],
                            message,
                            evidence_finding_ids=evidence_ids,
                            structured_payload={
                                "finding_ids": evidence_ids,
                                "evidence": [item.get("summary") or item.get("name") for item in findings],
                                "source_locations": [item.get("line") for item in findings if item.get("line")],
                                "agent_identity": agent.name,
                                "confidence": "high",
                                "proposed_actions": ["execute_dependent_stage"],
                                "validation_status": "unverified",
                            },
                        )

        # 7. VERIFY
        session.set_status("completed")
        if session.final_audit is None:
            self._audit_from_observations(session, "audit")

        results = [
            {
                "task_id": task["task_id"],
                "agent_key": task["agent_key"],
                "status": session.tasks[task["task_id"]]["status"],
                "summary": session.tasks[task["task_id"]].get("summary", ""),
                "findings": session.get_findings(task["agent_key"]),
                "duration_ms": session.tasks[task["task_id"]].get(
                    "duration_ms", 0.0
                ),
                "execution_mode": session.tasks[task["task_id"]].get(
                    "execution_mode", "deterministic"
                ),
                "fallback_reason": session.tasks[task["task_id"]].get(
                    "fallback_reason"
                ),
                "candidate_status": session.tasks[task["task_id"]].get(
                    "candidate_status"
                ),
                "candidate_execution_mode": session.tasks[task["task_id"]].get(
                    "candidate_execution_mode"
                ),
                "candidate_proposed": session.tasks[task["task_id"]].get(
                    "candidate_proposed", False
                ),
                "error": session.tasks[task["task_id"]].get("error"),
            }
            for task in session.plan
        ]
        failed_tasks = [
            f"{task['agent_key']}: {session.tasks[task['task_id']].get('error', 'failed')}"
            for task in session.plan
            if session.tasks[task["task_id"]]["status"] == "failed"
        ]
        if failed_tasks:
            raise RuntimeError(
                "One or more specialist tasks failed: " + "; ".join(failed_tasks)
            )

        from backend.agentic.verification_contract import create_not_run_audit
        final_audit = session.final_audit or create_not_run_audit("No final audit record")
        _audit_task = session.tasks.get("audit", {})
        audit_status = final_audit.get("status", "not_run")
        audit_passed = final_audit.get("passed", False)

        # 8. REPORT
        diff = self._supervisor_tool(
            session,
            "compute_unified_diff",
            {
                "original_code": session.original_code,
                "candidate_code": session.current_code,
            },
            task_id="supervisor_final_diff",
        )
        if diff.get("status") != "success":
            raise RuntimeError(
                "Supervisor could not compute the final candidate diff: "
                + diff.get("error", "diff generation failed.")
            )
        modes = {item["execution_mode"] for item in results if item["status"] == "completed"}
        deterministic_candidates = any(
            item.get("candidate_proposed")
            and item.get("candidate_execution_mode")
            in {"deterministic", "deterministic_ast"}
            for item in results
        )
        execution_mode = (
            "model-assisted"
            if modes == {"model"} and not deterministic_candidates
            else "mixed"
            if "model" in modes or "mixed" in modes
            else "deterministic-fallback"
            if "deterministic_fallback" in modes
            else "deterministic"
        )
        model_ready = bool(
            AppConfig.AI_PROVIDER != "ast"
            and getattr(self.model_client, "chat", None)
            and provider_ready(self.model_client)
        )
        final_audit = session.final_audit or {}
        final_payload = {
            "status": "completed",
            "session_id": session.session_id,
            "original_code": session.original_code,
            "final_code": session.current_code,
            "code_changed": session.current_code.strip()
            != session.original_code.strip(),
            "diff": diff.get("result", {}).get("diff", ""),
            "plan": session.plan,
            "tasks": session.tasks,
            "findings": session.findings,
            "messages": session.messages,
            "tool_observations": session.tool_observations,
            "modification_history": session.modification_history,
            "candidate_outcomes": candidate_outcomes,
            "final_audit": final_audit,
            # 7 Honest Verification Status Keys
            "static_checks_passed": final_audit.get("static_checks_passed", False),
            "security_checks_passed": final_audit.get("security_checks_passed", False),
            "type_checks_passed": final_audit.get("type_checks_passed", False),
            "behavioral_tests_run": final_audit.get("behavioral_tests_run", False),
            "behavioral_tests_passed": final_audit.get("behavioral_tests_passed", False),
            "semantic_equivalence_verified": final_audit.get("semantic_equivalence_verified", False),
            "human_approval_received": final_audit.get("human_approval_received", session.is_approved),
            "complete_verification": final_audit.get("complete_verification", False),
            "verification_level": final_audit.get("verification_level", "static_only"),
            "acceptance_explanation": final_audit.get("acceptance_explanation"),
            "rejection_reasons": final_audit.get("rejection_reasons", []),
            "trajectory_steps": len(session.trajectory),
            "model_call_count": int(session.metadata.get("model_call_count", 0)),
            "checkpoints": len(session.checkpoints),
            "results": results,
            "audit_passed": audit_passed,
            "audit_status": audit_status,
            "execution_mode": execution_mode,
            "provider": AppConfig.AI_PROVIDER,
            "model_name": self.model_name,
            "model_execution_ready": model_ready,
        }
        session.emit_event(
            "workflow_completed",
            agent="SupervisorAgent",
            **final_payload,
        )
        return final_payload
