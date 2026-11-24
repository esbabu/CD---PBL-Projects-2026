"""Specialized sub-agent personas for the Agentic AI Layer."""

from __future__ import annotations

import ast
import re
from typing import Any, Dict, Optional, Set, Tuple

from backend.ast_analyzer import _safe_call_name, analyze_code
from backend.agentic.agents.base_agent import BaseAgent, extract_first_json_object
from backend.agentic.session import AgentSession
from backend.agentic.tools.registry import ToolRegistry
from backend.code_analysis import (
    _class_docstring,
    _fallback_comment_code,
    _function_docstring,
)
from backend.config import AppConfig
from backend import model_provider
from backend.validator import has_added_comments, validate_generated_code


def _clean_docstring(text: str) -> str:
    cleaned = text.strip()
    if cleaned.startswith('"""') and cleaned.endswith('"""') and len(cleaned) >= 6:
        cleaned = cleaned[3:-3].strip()
    elif cleaned.startswith("'''") and cleaned.endswith("'''") and len(cleaned) >= 6:
        cleaned = cleaned[3:-3].strip()
    return cleaned


def _extract_documented_params(docstring: str) -> Set[str]:
    params: Set[str] = set()
    lines = docstring.splitlines()
    in_params_section = False

    for i, line in enumerate(lines):
        stripped = line.strip()
        # Sphinx :param <type>? <name>: or :type <name>:
        for m in re.finditer(r":\s*(?:param|type)\s+(?:[\w\.\[\],\s]+\s+)?([a-zA-Z_]\w*)\s*:", line):
            params.add(m.group(1))

        # Section headers
        if re.match(r"^(?:Args|Arguments|Parameters)\s*:\s*$", stripped, re.IGNORECASE):
            in_params_section = True
            continue
        if (
            stripped in ("Parameters", "Other Parameters")
            and i + 1 < len(lines)
            and lines[i + 1].strip().startswith("---")
        ):
            in_params_section = True
            continue

        # Section endings
        if re.match(r"^(?:Returns|Raises|Yields|Examples|Notes|Attributes|See Also)\s*:\s*$", stripped, re.IGNORECASE):
            in_params_section = False
            continue
        if (
            in_params_section
            and stripped in ("Returns", "Yields", "Raises", "Notes", "Examples", "See Also")
            and i + 1 < len(lines)
            and lines[i + 1].strip().startswith("---")
        ):
            in_params_section = False
            continue

        if in_params_section:
            # Google style: param_name (type): description or param_name: description
            m = re.match(r"^\s*([a-zA-Z_]\w*)\s*(?:\([^)]*\))?\s*:", line)
            if m:
                p = m.group(1)
                if p.lower() not in (
                    "args",
                    "arguments",
                    "parameters",
                    "returns",
                    "raises",
                    "yields",
                    "note",
                    "notes",
                    "example",
                    "examples",
                ):
                    params.add(p)
            elif stripped and not stripped.startswith("-") and not stripped.startswith("#"):
                # NumPy style: param_name : type
                m_numpy = re.match(r"^\s*([a-zA-Z_]\w*)\s*(?::.*)?$", line)
                if m_numpy:
                    p = m_numpy.group(1)
                    if p.lower() not in ("returns", "yields", "raises", "notes", "example", "examples"):
                        params.add(p)
        else:
            # Standalone param declaration like 'param_name (type): ...'
            m = re.match(r"^\s*(?:-\s*)?([a-zA-Z_]\w*)\s*\([^)]+\)\s*:", line)
            if m:
                p = m.group(1)
                if p.lower() not in ("note", "warning", "returns", "raises", "see", "example", "yields"):
                    params.add(p)

    return params


def _extract_node_spec(node: ast.AST) -> dict[str, Any]:
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        kind = "function"
        args_repr = ast.unparse(node.args)
        ret_repr = f" -> {ast.unparse(node.returns)}" if node.returns else ""
        prefix = "async def " if isinstance(node, ast.AsyncFunctionDef) else "def "
        sig = f"{prefix}{node.name}({args_repr}){ret_repr}:"

        params_info = []
        posonly = getattr(node.args, "posonlyargs", [])
        kwonly = getattr(node.args, "kwonlyargs", [])
        all_args = posonly + node.args.args + kwonly
        for arg in all_args:
            ann = ast.unparse(arg.annotation) if arg.annotation else "Any"
            params_info.append(f"{arg.arg}: {ann}")
        if node.args.vararg:
            ann = f": {ast.unparse(node.args.vararg.annotation)}" if node.args.vararg.annotation else ""
            params_info.append(f"*{node.args.vararg.arg}{ann}")
        if node.args.kwarg:
            ann = f": {ast.unparse(node.args.kwarg.annotation)}" if node.args.kwarg.annotation else ""
            params_info.append(f"**{node.args.kwarg.arg}{ann}")

        valid_params = {arg.arg for arg in all_args}
        if node.args.vararg:
            valid_params.add(node.args.vararg.arg)
        if node.args.kwarg:
            valid_params.add(node.args.kwarg.arg)

        decorators = [ast.unparse(d) for d in node.decorator_list]
        returns = [
            ast.unparse(r.value) if r.value else "None"
            for r in ast.walk(node)
            if isinstance(r, ast.Return)
        ]
        raises = [
            ast.unparse(r.exc) if r.exc else "Exception"
            for r in ast.walk(node)
            if isinstance(r, ast.Raise)
        ]
        called = list(dict.fromkeys(
            _safe_call_name(c.func)
            for c in ast.walk(node)
            if isinstance(c, ast.Call) and _safe_call_name(c.func)
        ))
        body = ast.unparse(node)
        return {
            "kind": kind,
            "signature": sig,
            "params_info": params_info,
            "valid_params": valid_params,
            "decorators": decorators,
            "returns": returns,
            "raises": raises,
            "called": called,
            "body": body,
        }
    elif isinstance(node, ast.ClassDef):
        kind = "class"
        bases_repr = ", ".join(ast.unparse(b) for b in node.bases)
        sig = f"class {node.name}({bases_repr}):" if bases_repr else f"class {node.name}:"
        init_node = next(
            (m for m in node.body if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef)) and m.name == "__init__"),
            None,
        )
        params_info = []
        valid_params = set()
        if init_node:
            init_all = (
                getattr(init_node.args, "posonlyargs", [])
                + init_node.args.args
                + getattr(init_node.args, "kwonlyargs", [])
            )
            for arg in init_all:
                ann = ast.unparse(arg.annotation) if arg.annotation else "Any"
                params_info.append(f"{arg.arg}: {ann}")
                valid_params.add(arg.arg)
            if init_node.args.vararg:
                valid_params.add(init_node.args.vararg.arg)
            if init_node.args.kwarg:
                valid_params.add(init_node.args.kwarg.arg)
        decorators = [ast.unparse(d) for d in node.decorator_list]
        return {
            "kind": kind,
            "signature": sig,
            "params_info": params_info,
            "valid_params": valid_params,
            "decorators": decorators,
            "returns": [],
            "raises": [],
            "called": [],
            "body": ast.unparse(node),
        }
    return {
        "kind": "unknown",
        "signature": "",
        "params_info": [],
        "valid_params": set(),
        "decorators": [],
        "returns": [],
        "raises": [],
        "called": [],
        "body": ast.unparse(node) if hasattr(node, "lineno") else "",
    }


def _deterministic_docstring_for_node(node: ast.AST, style: str) -> str:
    if isinstance(node, ast.ClassDef):
        return _class_docstring(node)
    return _function_docstring(node, style=style)


def _missing_callable_docstrings(source_code: str) -> list[dict[str, Any]]:
    try:
        tree = ast.parse(source_code)
    except Exception:
        return []
    missing = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if ast.get_docstring(node, clean=False) is None:
                missing.append({
                    "name": node.name,
                    "line": node.lineno,
                    "kind": "class" if isinstance(node, ast.ClassDef) else "function",
                    "node": node,
                })
    missing.sort(key=lambda item: item["line"])
    return missing


class ArchitectAgent(BaseAgent):
    """Specialist sub-agent for AST structural analysis, modular design, and complexity reduction."""

    def __init__(self, tools: ToolRegistry, model_client: Any = None) -> None:
        super().__init__(
            name="ATLAS",
            role_description=(
                "Architecture Intelligence Agent: analyzes project structure, imports, "
                "dependencies, complexity, and engineering task decomposition."
            ),
            system_prompt=(
                "Inspect the abstract syntax tree and dependency evidence, identify structural "
                "risks, and provide actionable architecture recommendations."
            ),
            tools=tools,
            model_client=model_client,
            allowed_tools=[
                "inspect_ast_structure",
                "infer_type_errors",
                "inspect_undefined_names",
                "list_project_files",
                "read_project_file",
                "search_project_code",
                "find_symbol",
                "get_import_graph",
            ],
        )

    def deterministic_turn(
        self, session: AgentSession, sub_task: str, task_id: str | None = None
    ) -> Dict[str, Any]:
        tool_res = self.execute_tool(
            session, "inspect_ast_structure", {}, task_id=task_id
        )
        type_res = self.execute_tool(
            session, "infer_type_errors", {}, task_id=task_id
        )
        undefined_res = self.execute_tool(
            session, "inspect_undefined_names", {}, task_id=task_id
        )
        self.require_tool_success(tool_res, "inspect_ast_structure")
        self.require_tool_success(type_res, "infer_type_errors")
        self.require_tool_success(undefined_res, "inspect_undefined_names")
        summary = (
            f"Analyzed AST structure: {tool_res.get('result', {}).get('function_count', 0)} function(s), "
            f"File CC={tool_res.get('result', {}).get('file_cyclomatic_complexity', 1)}. "
            f"Found {type_res.get('result', {}).get('error_count', 0)} definite type error(s)."
        )
        structure = tool_res.get("result", {})
        findings = [
            {
                "category": "architecture",
                "summary": "AST structure and module topology",
                "function_count": structure.get("function_count", 0),
                "class_count": structure.get("class_count", 0),
                "imports": structure.get("imports", []),
                "call_count": structure.get("call_count", 0),
                "cyclomatic_complexity": structure.get(
                    "file_cyclomatic_complexity", 1
                ),
                "functions": structure.get("functions", []),
                "classes": structure.get("classes", []),
            }
        ]
        type_result = type_res.get("result", {})
        findings.extend(type_result.get("definite_type_errors", []))
        findings.extend(undefined_res.get("result", {}).get("undefined_names", []))
        return {
            "agent": self.name,
            "status": "completed",
            "action": "finish",
            "summary": summary,
            "findings": findings,
        }


class OptimizerAgent(BaseAgent):
    """Specialist sub-agent for algorithmic complexity and performance speedups."""

    def __init__(self, tools: ToolRegistry, model_client: Any = None) -> None:
        super().__init__(
            name="FORGE",
            role_description=(
                "Code Engineering Agent: analyzes code quality, performance, "
                "algorithmic complexity, and maintainability."
            ),
            system_prompt=(
                "Analyze Python code for evidenced performance and maintainability "
                "opportunities, and prepare reviewable improvements."
            ),
            tools=tools,
            model_client=model_client,
            allowed_tools=[
                "detect_optimization_targets",
                "synthesize_optimization",
                "list_project_files",
                "read_project_file",
                "search_project_code",
                "find_symbol",
            ],
        )

    def deterministic_turn(
        self, session: AgentSession, sub_task: str, task_id: str | None = None
    ) -> Dict[str, Any]:
        detect_res = self.execute_tool(
            session, "detect_optimization_targets", {}, task_id=task_id
        )
        self.require_tool_success(detect_res, "detect_optimization_targets")
        opps = detect_res.get("result", {}).get("opportunities_count", 0)
        summary = f"Detected {opps} algorithmic optimization opportunity(ies)."
        candidate_code = None
        candidate_execution_mode = None
        fallback_reason = None

        if opps > 0:
            opt_res = self.execute_tool(
                session, "synthesize_optimization", {}, task_id=task_id
            )
            if not self.require_tool_success(opt_res, "synthesize_optimization"):
                return {
                    "agent": self.name,
                    "status": "pending_approval",
                    "tool": "synthesize_optimization",
                    "summary": "Optimization candidate requires approval.",
                    "findings": detect_res.get("result", {}).get(
                        "opportunities", []
                    ),
                }
            optimized = opt_res.get("result", {})
            fallback_reason = optimized.get("fallback_reason")
            if opt_res.get("status") == "success" and optimized.get("optimized"):
                candidate_code = optimized.get("optimized_code")
                candidate_execution_mode = optimized.get("execution_mode")
                summary += (
                    f" Proposed optimization: {optimized.get('complexity_before')} -> "
                    f"{optimized.get('complexity_after')}."
                )
        return {
            "agent": self.name,
            "status": "completed",
            "action": "finish",
            "summary": summary,
            "findings": detect_res.get("result", {}).get("opportunities", []),
            "candidate_code": candidate_code,
            "candidate_execution_mode": candidate_execution_mode,
            "fallback_reason": fallback_reason,
            "patches": opt_res.get("result", {}).get("patches", []) if candidate_code else [],
        }


class RedTeamAgent(BaseAgent):
    """Specialist sub-agent for static security vulnerability probing."""

    def __init__(self, tools: ToolRegistry, model_client: Any = None) -> None:
        super().__init__(
            name="SENTINEL",
            role_description=(
                "Security Intelligence Agent: performs static security analysis, "
                "identifies vulnerabilities, and evaluates risk."
            ),
            system_prompt=(
                "Inspect Python source with static tools only. Report supported vulnerability "
                "evidence, source locations, sinks, and risk without claiming unproven origins."
            ),
            tools=tools,
            model_client=model_client,
            allowed_tools=[
                "probe_security_vulnerabilities",
                "list_project_files",
                "read_project_file",
                "search_project_code",
                "find_symbol",
            ],
        )

    def deterministic_turn(
        self, session: AgentSession, sub_task: str, task_id: str | None = None
    ) -> Dict[str, Any]:
        has_workspace = bool(session.metadata.get("project_workspace_id"))
        all_scenarios = []
        vuln_count = 0
        min_resilience = 100

        probe_res = self.execute_tool(
            session,
            "probe_security_vulnerabilities",
            {"source_code": session.original_code},
            task_id=task_id,
        )
        self.require_tool_success(probe_res, "probe_security_vulnerabilities")
        res_data = probe_res.get("result", {})
        active_scenarios = res_data.get("scenarios", [])
        active_file = session.metadata.get("active_file", "main.py")
        for sc in active_scenarios:
            sc["file"] = active_file
            if not sc.get("summary"):
                sc_line = sc.get("target_line") or sc.get("ast_sink_line") or 1
                sc["summary"] = f"[{active_file}:{sc_line}] {sc.get('name')}"
        all_scenarios.extend(active_scenarios)
        vuln_count += res_data.get("vulnerabilities_detected", 0)
        min_resilience = min(min_resilience, res_data.get("resilience_score", 100))

        if has_workspace:
            files_res = self.execute_tool(
                session, "list_project_files", {"glob": "**/*.py"}, task_id=task_id
            )
            if files_res.get("status") == "success":
                file_list = files_res.get("result", {}).get("files", [])
                for f_info in file_list:
                    rel_path = f_info.get("path")
                    if not rel_path or rel_path == active_file:
                        continue
                    read_res = self.execute_tool(
                        session,
                        "read_project_file",
                        {"path": rel_path, "start_line": 1, "end_line": 300},
                        task_id=task_id,
                    )
                    if read_res.get("status") != "success":
                        continue
                    raw_lines = read_res.get("result", {}).get("raw_lines")
                    if raw_lines is not None:
                        file_code = "\n".join(raw_lines)
                    else:
                        file_code = read_res.get("result", {}).get("content", "")
                    file_probe = self.execute_tool(
                        session,
                        "probe_security_vulnerabilities",
                        {"source_code": file_code},
                        task_id=task_id,
                    )
                    if file_probe.get("status") == "success":
                        f_res_data = file_probe.get("result", {})
                        scenarios = f_res_data.get("scenarios", [])
                        for sc in scenarios:
                            sc["file"] = rel_path
                            line_no = sc.get("target_line") or sc.get("ast_sink_line") or 1
                            sc["summary"] = f"[{rel_path}:{line_no}] {sc.get('name')}"
                        all_scenarios.extend(scenarios)
                        vuln_count += f_res_data.get("vulnerabilities_detected", 0)
                        min_resilience = min(min_resilience, f_res_data.get("resilience_score", 100))

        summary = (
            f"SENTINEL static assessment completed. Found {vuln_count} vulnerability finding(s). "
            f"Static resilience score: {min_resilience}/100."
        )
        return {
            "agent": self.name,
            "status": "completed",
            "action": "finish",
            "summary": summary,
            "vulnerabilities": all_scenarios,
            "findings": all_scenarios,
        }


class BlueTeamAgent(BaseAgent):
    """Specialist sub-agent for defensive remediation and security patching."""

    def __init__(self, tools: ToolRegistry, model_client: Any = None) -> None:
        super().__init__(
            name="REMEDY",
            role_description=(
                "Code Remediation Agent: prepares secure code improvements, "
                "vulnerability remediations, and defensive recommendations."
            ),
            system_prompt=(
                "Use only published upstream evidence to prepare a reviewable defensive "
                "candidate and explain which controls it applies."
            ),
            tools=tools,
            model_client=model_client,
            allowed_tools=[
                "synthesize_defensive_patch",
                "list_project_files",
                "read_project_file",
                "search_project_code",
                "find_symbol",
                "propose_file_patch",
            ],
        )

    def deterministic_turn(
        self, session: AgentSession, sub_task: str, task_id: str | None = None
    ) -> Dict[str, Any]:
        shared_context = session.context_for(self.agent_key, task_id)
        red_findings = [
            item
            for item in shared_context["dependency_findings"]
            if item.get("source_agent") == "red_team"
        ]
        session.send_message(
            self.agent_key,
            "SupervisorAgent",
            f"Received {len(red_findings)} finding(s) from upstream analysis.",
            evidence_finding_ids=[
                item["finding_id"]
                for item in red_findings
                if item.get("finding_id")
            ],
        )
        patch_res = self.execute_tool(
            session,
            "synthesize_defensive_patch",
            {"findings": red_findings},
            task_id=task_id,
        )
        if not self.require_tool_success(
            patch_res, "synthesize_defensive_patch"
        ):
            return {
                "agent": self.name,
                "status": "pending_approval",
                "tool": "synthesize_defensive_patch",
                "summary": "Defensive candidate requires approval.",
                "findings": [],
            }
        res_data = patch_res.get("result", {})

        if res_data.get("fixed"):
            summary = (
                f"Prepared a candidate addressing {res_data.get('neutralized_count', 0)} "
                "vulnerability finding(s). "
                f"Defensive controls: {', '.join(res_data.get('defensive_controls', []))}."
            )
        else:
            summary = "No unmitigated vulnerabilities required defensive patching."

        return {
            "agent": self.name,
            "status": "completed",
            "action": "finish",
            "summary": summary,
            "findings": [
                {
                    "category": "remediation",
                    "summary": item,
                    "reported_finding_ids": [
                        finding.get("finding_id") for finding in red_findings
                    ],
                }
                for item in res_data.get("defensive_controls", [])
            ],
            "candidate_code": (
                res_data.get("fixed_code") if res_data.get("fixed") else None
            ),
            "candidate_execution_mode": (
                res_data.get("execution_mode") if res_data.get("fixed") else None
            ),
            "fallback_reason": res_data.get("fallback_reason"),
            "patches": res_data.get("patches", []) if res_data.get("fixed") else [],
        }


class DocstringAgent(BaseAgent):
    """Specialist sub-agent for AST docstrings and semantic specifications."""

    def __init__(self, tools: ToolRegistry, model_client: Any = None) -> None:
        super().__init__(
            name="SCRIBE",
            role_description=(
                "Documentation Intelligence Agent: produces technical documentation, "
                "architecture notes, code explanations, and engineering reports."
            ),
            system_prompt=(
                "Your objective is to produce substantive function docstrings detailing parameters, "
                "returns, exceptions, and intermediate operational logic grounded in AST facts."
            ),
            tools=tools,
            model_client=model_client,
            allowed_tools=[
                "inspect_ast_structure",
                "explain_ast_semantics",
                "list_project_files",
                "read_project_file",
                "search_project_code",
                "find_symbol",
                "propose_file_patch",
            ],
        )

    def _generate_docstring_for_node(
        self,
        session: AgentSession,
        node: ast.AST,
        style: str,
        model_client: Any,
        task_id: Optional[str] = None,
    ) -> Tuple[str, str]:
        spec = _extract_node_spec(node)
        valid_params = spec["valid_params"]
        kind = spec["kind"]

        prompt = (
            f"Generate an AST-grounded Python docstring in {style.upper()} format for the following {kind}:\n\n"
            f"Signature: {spec['signature']}\n"
            f"Parameters: {', '.join(spec['params_info']) if spec['params_info'] else 'None'}\n"
            f"Decorators: {', '.join(spec['decorators']) if spec['decorators'] else 'None'}\n"
            f"Return expressions: {', '.join(spec['returns']) if spec['returns'] else 'None'}\n"
            f"Raised exceptions: {', '.join(spec['raises']) if spec['raises'] else 'None'}\n"
            f"Called functions: {', '.join(spec['called']) if spec['called'] else 'None'}\n"
            f"Source Code:\n{spec['body']}\n\n"
            f"CRITICAL INSTRUCTIONS:\n"
            f"1. Chosen style: {style}. Continuation lines must be properly indented.\n"
            f"2. Only document parameters that exist in the signature: {sorted(valid_params)}. Do NOT document parameters that do not exist.\n"
            f"3. Return ONLY a single valid JSON object in the exact format:\n"
            f'{{"docstring": "..."}}\n'
            f"Do not include any extra text outside the JSON object."
        )

        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt},
        ]
        extra_body = model_provider.provider_extra_body()

        try:
            response = model_client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.1,
                max_tokens=self.max_tokens,
                extra_body=extra_body,
            )
            raw_text = response.choices[0].message.content or ""
            data = extract_first_json_object(raw_text)

            if not isinstance(data, dict) or not isinstance(data.get("docstring"), str):
                retry_messages = list(messages)
                retry_messages.append({"role": "assistant", "content": raw_text})
                retry_messages.append({
                    "role": "user",
                    "content": 'Your response was not valid JSON. Return ONLY a single JSON object: {"docstring": "..."}',
                })
                retry_resp = model_client.chat.completions.create(
                    model=self.model_name,
                    messages=retry_messages,
                    temperature=0.1,
                    max_tokens=self.max_tokens,
                    extra_body=extra_body,
                )
                retry_raw = retry_resp.choices[0].message.content or ""
                data = extract_first_json_object(retry_raw)
                if not isinstance(data, dict) or not isinstance(data.get("docstring"), str):
                    return _deterministic_docstring_for_node(node, style), "deterministic"

            docstring = data["docstring"].strip()
            documented = _extract_documented_params(docstring)
            hallucinated = documented - valid_params
            hallucinated.discard("self")
            hallucinated.discard("cls")

            if hallucinated:
                retry_messages = list(messages)
                retry_messages.append({"role": "assistant", "content": raw_text})
                retry_messages.append({
                    "role": "user",
                    "content": (
                        f"Reject: the docstring mentions parameter(s) {sorted(hallucinated)} which are not in the signature "
                        f"{sorted(valid_params)}. Return ONLY valid JSON with no extra parameters: {{\"docstring\": \"...\"}}"
                    ),
                })
                retry_resp = model_client.chat.completions.create(
                    model=self.model_name,
                    messages=retry_messages,
                    temperature=0.1,
                    max_tokens=self.max_tokens,
                    extra_body=extra_body,
                )
                retry_raw = retry_resp.choices[0].message.content or ""
                data2 = extract_first_json_object(retry_raw)
                if isinstance(data2, dict) and isinstance(data2.get("docstring"), str):
                    doc2 = data2["docstring"].strip()
                    doc2_params = _extract_documented_params(doc2) - valid_params
                    doc2_params.discard("self")
                    doc2_params.discard("cls")
                    if not doc2_params:
                        return _clean_docstring(doc2), "model"

                return _deterministic_docstring_for_node(node, style), "deterministic"

            return _clean_docstring(docstring), "model"
        except Exception:
            return _deterministic_docstring_for_node(node, style), "deterministic"

    def finish_from_observations(
        self,
        session: AgentSession,
        task_id: str | None = None,
        *,
        execution_mode: str = "deterministic",
        model_output: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        result = super().finish_from_observations(
            session, task_id, execution_mode=execution_mode, model_output=model_output, **kwargs
        )
        current_code = session.current_code
        analysis = analyze_code(current_code)
        missing_docstrings = _missing_callable_docstrings(current_code)
        style = (
            session.metadata.get("docstring_style")
            or getattr(AppConfig, "DOCSTRING_STYLE", "google")
            or "google"
        )
        model_client = session.model_client or self.model_client

        findings_source: Dict[str, str] = {}
        custom_docstrings: Dict[Any, str] = {}

        if (
            execution_mode == "model"
            and model_client
            and getattr(model_client, "chat", None)
            and missing_docstrings
        ):
            for item in missing_docstrings:
                node = item.get("node")
                if node:
                    doc, src = self._generate_docstring_for_node(
                        session, node, style, model_client, task_id=task_id
                    )
                    findings_source[item["name"]] = src
                    custom_docstrings[item["name"]] = doc
                    custom_docstrings[(item["name"], item["line"])] = doc
                else:
                    findings_source[item["name"]] = "deterministic"
            candidate = _fallback_comment_code(
                current_code,
                analysis=analysis,
                docstring_style=style,
                custom_docstrings=custom_docstrings,
            )
            validation = validate_generated_code(current_code, candidate)
            if not validation.get("is_valid"):
                candidate = _fallback_comment_code(
                    current_code, analysis=analysis, docstring_style=style
                )
                validation = validate_generated_code(current_code, candidate)
                for item in missing_docstrings:
                    findings_source[item["name"]] = "deterministic"
        else:
            for item in missing_docstrings:
                findings_source[item["name"]] = "deterministic"
            candidate = _fallback_comment_code(
                current_code, analysis=analysis, docstring_style=style
            )
            validation = validate_generated_code(current_code, candidate)

        added_documentation = has_added_comments(current_code, candidate)
        if (
            validation.get("is_valid")
            and added_documentation
            and candidate != current_code
        ):
            has_model_source = any(src == "model" for src in findings_source.values())
            result["candidate_code"] = candidate
            result["candidate_execution_mode"] = (
                "model" if has_model_source else "deterministic_ast"
            )
            result["findings"].extend(
                {
                    "function": item["name"],
                    "line": item["line"],
                    "status": "candidate_generated",
                    "ast_context_available": True,
                    "source": findings_source.get(item["name"], "deterministic"),
                }
                for item in missing_docstrings
            )
            if not missing_docstrings:
                result["findings"].append(
                    {
                        "category": "documentation",
                        "summary": "Added AST-anchored inline comments.",
                        "status": "candidate_generated",
                        "source": "deterministic",
                    }
                )
            result["summary"] += (
                f" Generated and validated AST-grounded documentation with "
                f"{len(missing_docstrings)} missing function or method docstring(s) "
                "and inline comments."
            )
        return result

    def deterministic_turn(
        self, session: AgentSession, sub_task: str, task_id: str | None = None
    ) -> Dict[str, Any]:
        original_code = session.current_code
        structure_result = self.execute_tool(
            session, "inspect_ast_structure", {}, task_id=task_id
        )
        self.require_tool_success(structure_result, "inspect_ast_structure")
        explanations = self.execute_tool(
            session, "explain_ast_semantics", {}, task_id=task_id
        )
        self.require_tool_success(explanations, "explain_ast_semantics")
        ast_context = session.context_for(self.agent_key, task_id)
        analysis = analyze_code(original_code)
        missing_docstrings = _missing_callable_docstrings(original_code)
        style = (
            session.metadata.get("docstring_style")
            or getattr(AppConfig, "DOCSTRING_STYLE", "google")
            or "google"
        )
        candidate = _fallback_comment_code(original_code, analysis=analysis, docstring_style=style)
        validation = validate_generated_code(original_code, candidate)
        validation_issues = validation.get("issues", [])
        added_documentation = has_added_comments(original_code, candidate)
        candidate_generated = (
            validation.get("is_valid")
            and added_documentation
            and candidate != original_code
        )

        summary = (
            f"{'Generated and validated' if candidate_generated else 'No new'} "
            f"AST documentation candidate; {len(missing_docstrings)} function or "
            "method(s) were missing docstrings."
        )
        if validation_issues:
            summary += " Candidate rejected: " + "; ".join(validation_issues)

        findings = [
            {
                "function": item["name"],
                "line": item["line"],
                "status": "candidate_generated" if candidate_generated else "missing",
                "ast_context_available": bool(ast_context["dependency_findings"]),
                "source": "deterministic",
            }
            for item in missing_docstrings
        ]
        if candidate_generated and has_added_comments(original_code, candidate):
            findings.append(
                {
                    "category": "documentation",
                    "summary": "Added AST-anchored inline comments and/or docstrings.",
                    "status": "candidate_generated",
                    "source": "deterministic",
                }
            )

        return {
            "agent": self.name,
            "status": "completed",
            "action": "finish",
            "summary": summary,
            "findings": findings,
            "candidate_code": candidate if candidate_generated else None,
            "candidate_execution_mode": (
                "deterministic_ast" if candidate_generated else None
            ),
            "ast_explanations": explanations.get("result", {}).get(
                "explanations", []
            ),
        }


class AuditAgent(BaseAgent):
    """Specialist sub-agent for AST non-regression audit and score delta calculation."""

    def __init__(self, tools: ToolRegistry, model_client: Any = None) -> None:
        super().__init__(
            name="VERITY",
            role_description=(
                "Quality & Verification Agent: independently checks code integrity, "
                "security regressions, test evidence, and final quality."
            ),
            system_prompt=(
                "Your objective is to perform the final non-regression audit. Verify that syntax is valid, "
                "all definitions are preserved, and calculate the overall health improvements."
            ),
            tools=tools,
            model_client=model_client,
            allowed_tools=[
                "verify_code_integrity",
                "compute_unified_diff",
                "probe_security_vulnerabilities",
                "evaluate_quality",
                "infer_type_errors",
                "run_isolated_behavioral_tests",
                "list_project_files",
                "read_project_file",
                "search_project_code",
                "find_symbol",
            ],
        )

    def deterministic_turn(
        self, session: AgentSession, sub_task: str, task_id: str | None = None
    ) -> Dict[str, Any]:
        val_res = self.execute_tool(
            session,
            "verify_code_integrity",
            {
                "original_code": session.original_code,
                "candidate_code": session.current_code,
                "allow_executable_changes": True,
            },
            task_id=task_id,
        )
        diff_res = self.execute_tool(
            session,
            "compute_unified_diff",
            {
                "original_code": session.original_code,
                "candidate_code": session.current_code,
            },
            task_id=task_id,
        )
        security_res = self.execute_tool(
            session,
            "probe_security_vulnerabilities",
            {},
            task_id=task_id,
        )
        type_res = self.execute_tool(
            session,
            "infer_type_errors",
            {"source_code": session.current_code},
            task_id=task_id,
        )
        quality_res = self.execute_tool(
            session,
            "evaluate_quality",
            {},
            task_id=task_id,
        )
        self.require_tool_success(val_res, "verify_code_integrity")
        self.require_tool_success(diff_res, "compute_unified_diff")
        self.require_tool_success(
            security_res, "probe_security_vulnerabilities"
        )
        self.require_tool_success(quality_res, "evaluate_quality")

        # Optional behavioral verification in isolated disposable sandbox
        behavioral_test_code = session.metadata.get("behavioral_test_code")
        run_behavioral = bool(
            session.metadata.get("run_behavioral_tests") or behavioral_test_code
        )
        behavioral_res: Dict[str, Any] = {}
        if run_behavioral and behavioral_test_code:
            b_tool = self.execute_tool(
                session,
                "run_isolated_behavioral_tests",
                {
                    "candidate_code": session.current_code,
                    "test_code": behavioral_test_code,
                    "enabled": True,
                },
                task_id=task_id,
            )
            behavioral_res = b_tool.get("result", {})

        integrity_result = val_res.get("result", {})
        _structural_safety = integrity_result.get("structural_safety", {})
        static_checks_passed = bool(integrity_result.get("all_passed", False))

        # Security evaluation
        security_result = security_res.get("result", {})
        current_findings = security_result.get("scenarios", [])
        initial_findings = session.get_findings("red_team")
        initial_keys = {
            (item.get("cwe"), item.get("category"), item.get("name"))
            for item in initial_findings
        }
        _current_keys = {
            (item.get("cwe"), item.get("category"), item.get("name"))
            for item in current_findings
        }
        introduced_findings = [
            item
            for item in current_findings
            if (item.get("cwe"), item.get("category"), item.get("name"))
            not in initial_keys
        ]
        security_regressions = bool(introduced_findings)
        security_findings = current_findings
        security_checks_passed = not security_regressions and not security_findings

        # Type evaluation
        type_result = type_res.get("result", {}) if type_res.get("status") == "success" else {}
        type_errors = type_result.get("definite_type_errors", [])
        type_checks_passed = len(type_errors) == 0

        # Behavioral testing evaluation
        behavioral_tests_run = bool(behavioral_res.get("behavioral_tests_run", False))
        behavioral_tests_passed = bool(behavioral_res.get("behavioral_tests_passed", False))

        # Semantic equivalence
        _semantic_equivalence_verified = bool(
            integrity_result.get("executable_code_preserved", False)
        )
        from backend.agentic.verification_contract import (
            approval_record_for_current_code,
        )

        approval_record = approval_record_for_current_code(session)
        human_approval_received = approval_record is not None

        # Honest complete verification rule:
        # Never report complete verification when behavioral testing was not performed.
        complete_verification = (
            behavioral_tests_run
            and behavioral_tests_passed
            and static_checks_passed
            and security_checks_passed
            and type_checks_passed
        )
        _verification_level = (
            "fully_verified_with_behavioral_sandbox"
            if complete_verification
            else "static_only"
        )

        _overall_passed = (
            static_checks_passed
            and security_checks_passed
            and type_checks_passed
            and (behavioral_tests_passed if behavioral_tests_run else True)
        )

        diff_data = diff_res.get("result", {})
        quality_result = quality_res.get("result", {})
        findings = list(security_findings)
        findings.extend(quality_result.get("findings", []))

        behaviour_change = integrity_result.get("behaviour_change", False)
        behaviour_warnings = integrity_result.get("behaviour_warnings", [])
        behaviour_preservation = integrity_result.get("behaviour_preservation", {})
        if behaviour_change:
            for bf in behaviour_preservation.get("findings", []):
                findings.append({
                    "category": "behaviour_change",
                    "summary": bf.get("summary", "Remediation changes execution or return contract."),
                    "details": bf.get("details", ""),
                    "behaviour_change": True,
                })

        from backend.agentic.verification_contract import build_unified_audit

        audit = build_unified_audit(
            integrity_result=integrity_result,
            security_findings=security_findings,
            security_regressions=introduced_findings,
            type_errors=type_errors,
            behavioral_results=behavioral_res if run_behavioral else None,
            is_approved=human_approval_received,
            code_changed=session.current_code.strip() != session.original_code.strip(),
            quality_result=quality_result,
            diff_data=diff_data,
            approval_record=approval_record,
            security_checked=True,
            types_checked=True,
            behaviour_change=behaviour_change,
            behaviour_warnings=behaviour_warnings,
            behaviour_preservation=behaviour_preservation,
        )
        session.final_audit = audit
        session.emit_event(
            "verification_completed",
            agent=self.agent_key,
            status=audit["status"],
            verification_level=audit["verification_level"],
            audit=audit,
        )
        return {
            "agent": self.name,
            "status": "completed",
            "action": "finish",
            "summary": audit["summary"],
            "passed": audit["passed"],
            "diff": diff_data.get("diff", ""),
            "findings": findings,
            "audit": audit,
            "report": audit.get("report", ""),
        }


# Enterprise specialist aliases matching workforce nomenclature
AtlasSpecialist = ArchitectAgent
ForgeSpecialist = OptimizerAgent
SentinelSpecialist = RedTeamAgent
RemedySpecialist = BlueTeamAgent
ScribeSpecialist = DocstringAgent
VeritySpecialist = AuditAgent
