"""Pre-configured standard tool catalog for the Agentic AI Layer."""

from __future__ import annotations

from backend.agentic.tools.ast_tools import (
    explain_ast_semantics_handler,
    infer_type_errors_handler,
    inspect_ast_structure_handler,
    inspect_undefined_names_handler,
)
from backend.agentic.tools.optimization_tools import (
    detect_optimization_targets_handler,
    synthesize_optimization_handler,
)
from backend.agentic.tools.project_tools import (
    find_symbol_handler,
    get_import_graph_handler,
    list_project_files_handler,
    propose_file_patch_handler,
    read_project_file_handler,
    search_project_code_handler,
)
from backend.agentic.tools.registry import ToolDefinition, ToolRegistry
from backend.agentic.tools.security_tools import (
    evaluate_attack_guardrail_handler,
    probe_security_vulnerabilities_handler,
    synthesize_defensive_patch_handler,
)
from backend.agentic.tools.verification_tools import (
    compute_unified_diff_handler,
    evaluate_quality_handler,
    run_isolated_behavioral_tests_handler,
    verify_code_integrity_handler,
)


def create_standard_tool_registry() -> ToolRegistry:
    """Build and return a ToolRegistry populated with all allowlisted AST tools."""
    registry = ToolRegistry()

    # 1. Structure & AST Inspection
    registry.register(
        ToolDefinition(
            name="inspect_ast_structure",
            description="Inspect AST structural breakdown: functions, classes, imports, call count, and cyclomatic complexity.",
            parameters_schema={
                "type": "object",
                "properties": {
                    "source_code": {
                        "type": "string",
                        "description": "Optional Python code override. If omitted, uses active code from context.",
                    }
                },
                "required": [],
            },
            handler=inspect_ast_structure_handler,
            is_read_only=True,
        )
    )

    # 2. Definite Type Inference
    registry.register(
        ToolDefinition(
            name="infer_type_errors",
            description="Statically detect definite type collisions (e.g. incompatible operations) without running code.",
            parameters_schema={
                "type": "object",
                "properties": {
                    "source_code": {
                        "type": "string",
                        "description": "Optional Python code override.",
                    },
                },
                "required": [],
            },
            handler=infer_type_errors_handler,
            is_read_only=True,
        )
    )

    # 3. AST Semantic Explanations
    registry.register(
        ToolDefinition(
            name="explain_ast_semantics",
            description="Generate deterministic, AST-grounded explanations of control flow, recursion, and key logic steps.",
            parameters_schema={
                "type": "object",
                "properties": {
                    "source_code": {
                        "type": "string",
                        "description": "Optional Python code override.",
                    },
                },
                "required": [],
            },
            handler=explain_ast_semantics_handler,
            is_read_only=True,
        )
    )

    # 4. Undefined Names
    registry.register(
        ToolDefinition(
            name="inspect_undefined_names",
            description="Check for undefined variables, missing imports, or unresolved function identifiers.",
            parameters_schema={
                "type": "object",
                "properties": {
                    "source_code": {
                        "type": "string",
                        "description": "Optional Python code override.",
                    }
                },
                "required": [],
            },
            handler=inspect_undefined_names_handler,
            is_read_only=True,
        )
    )

    # 5. Security Vulnerability Analysis
    registry.register(
        ToolDefinition(
            name="probe_security_vulnerabilities",
            description="Audit source code statically for 7 CWE vulnerability classes (SQLi, command injection, path traversal, insecure deserialization, SSRF, XXE, ReDoS) without code execution.",
            parameters_schema={
                "type": "object",
                "properties": {
                    "source_code": {
                        "type": "string",
                        "description": "Optional Python code override.",
                    }
                },
                "required": [],
            },
            handler=probe_security_vulnerabilities_handler,
            is_read_only=True,
        )
    )

    # 6. Security Remediation
    registry.register(
        ToolDefinition(
            name="synthesize_defensive_patch",
            description="Synthesize defensive patches for reported security findings (e.g. parameterized queries, safe regex bounds). Requires approval before applying.",
            parameters_schema={
                "type": "object",
                "properties": {
                    "source_code": {
                        "type": "string",
                        "description": "Optional Python code override.",
                    },
                    "findings": {
                        "type": "array",
                        "description": "Structured findings published by SENTINEL.",
                        "items": {"type": "object"},
                    },
                },
                "required": [],
            },
            handler=synthesize_defensive_patch_handler,
            is_read_only=True,
            requires_approval=False,
            allowed_agents={"blue_team", "remedy"},
        )
    )

    # 7. Attack Guardrail Evaluation
    registry.register(
        ToolDefinition(
            name="evaluate_attack_guardrail",
            description="Evaluate prompt or source code against deterministic adversarial prompt-injection and data exfiltration guards.",
            parameters_schema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Prompt text or source code to evaluate.",
                    },
                    "content_type": {
                        "type": "string",
                        "description": "Either 'prompt' or 'code'.",
                    },
                },
                "required": [],
            },
            handler=evaluate_attack_guardrail_handler,
            is_read_only=True,
        )
    )

    # 8. Optimization Bottlenecks Detection
    registry.register(
        ToolDefinition(
            name="detect_optimization_targets",
            description="Detect algorithmic and memory optimization opportunities (quadratic loops, redundant dictionary lookups, eager comprehensions).",
            parameters_schema={
                "type": "object",
                "properties": {
                    "source_code": {
                        "type": "string",
                        "description": "Optional Python code override.",
                    }
                },
                "required": [],
            },
            handler=detect_optimization_targets_handler,
            is_read_only=True,
        )
    )

    # 9. Synthesize Optimizations
    registry.register(
        ToolDefinition(
            name="synthesize_optimization",
            description="Propose algorithmic complexity and speedup optimizations. Requires approval before applying.",
            parameters_schema={
                "type": "object",
                "properties": {
                    "source_code": {
                        "type": "string",
                        "description": "Optional Python code override.",
                    }
                },
                "required": [],
            },
            handler=synthesize_optimization_handler,
            is_read_only=True,
            requires_approval=False,
            allowed_agents={"optimizer", "forge"},
        )
    )

    # 10. Code Integrity Verification
    registry.register(
        ToolDefinition(
            name="verify_code_integrity",
            description="Verify Python AST validity, syntax correctness, and function/class definition preservation.",
            parameters_schema={
                "type": "object",
                "properties": {
                    "original_code": {
                        "type": "string",
                        "description": "Original Python source code.",
                    },
                    "candidate_code": {
                        "type": "string",
                        "description": "Modified candidate Python source code.",
                    },
                    "allow_executable_changes": {
                        "type": "boolean",
                        "description": "True only when verifying an intentional code transformation.",
                    },
                },
                "required": [],
            },
            handler=verify_code_integrity_handler,
            is_read_only=True,
        )
    )

    # 11. Compute Unified Diff
    registry.register(
        ToolDefinition(
            name="compute_unified_diff",
            description="Compute unified diff between original code and candidate code.",
            parameters_schema={
                "type": "object",
                "properties": {
                    "original_code": {
                        "type": "string",
                        "description": "Original Python code.",
                    },
                    "candidate_code": {
                        "type": "string",
                        "description": "Modified Python code.",
                    },
                },
                "required": [],
            },
            handler=compute_unified_diff_handler,
            is_read_only=True,
        )
    )

    registry.register(
        ToolDefinition(
            name="evaluate_quality",
            description="Evaluate the current Python candidate with deterministic quality rules.",
            parameters_schema={
                "type": "object",
                "properties": {
                    "source_code": {
                        "type": "string",
                        "description": "Optional Python code override.",
                    }
                },
                "required": [],
            },
            handler=evaluate_quality_handler,
            is_read_only=True,
        )
    )

    # 13. Isolated Behavioral Test Verification
    registry.register(
        ToolDefinition(
            name="run_isolated_behavioral_tests",
            description="Execute behavioral unit tests against candidate code in an isolated disposable sandbox.",
            parameters_schema={
                "type": "object",
                "properties": {
                    "candidate_code": {
                        "type": "string",
                        "description": "Candidate Python source code.",
                    },
                    "test_code": {
                        "type": "string",
                        "description": "Test harness script or unit tests.",
                    },
                    "timeout_seconds": {
                        "type": "number",
                        "description": "Execution timeout limit (default: 5.0 seconds).",
                    },
                    "enabled": {
                        "type": "boolean",
                        "description": "Whether behavioral testing is enabled.",
                    },
                },
                "required": [],
            },
            handler=run_isolated_behavioral_tests_handler,
            is_read_only=True,
            allowed_agents={"audit", "verity"},
        )
    )

    # 14. Project Workspace: List Files
    registry.register(
        ToolDefinition(
            name="list_project_files",
            description="List all files in the project workspace matching a glob pattern, with line counts.",
            parameters_schema={
                "type": "object",
                "properties": {
                    "glob": {
                        "type": "string",
                        "description": "Optional glob pattern to filter files (default: '**/*.py').",
                    }
                },
                "required": [],
            },
            handler=list_project_files_handler,
            is_read_only=True,
            allowed_agents={
                "architect", "atlas", "ATLAS",
                "optimizer", "forge", "FORGE",
                "red_team", "sentinel", "SENTINEL",
                "blue_team", "remedy", "REMEDY",
                "docstring", "scribe", "SCRIBE",
                "audit", "verity", "VERITY",
            },
        )
    )

    # 15. Project Workspace: Read File
    registry.register(
        ToolDefinition(
            name="read_project_file",
            description="Read numbered lines from a file in the project workspace (up to 300 lines per call).",
            parameters_schema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative POSIX path of the file to read within the workspace.",
                    },
                    "start_line": {
                        "type": "integer",
                        "description": "1-based line number to start reading from (default: 1).",
                    },
                    "end_line": {
                        "type": "integer",
                        "description": "1-based line number to end reading at (default: 200, max 300 lines per read).",
                    },
                },
                "required": ["path"],
            },
            handler=read_project_file_handler,
            is_read_only=True,
            allowed_agents={
                "architect", "atlas", "ATLAS",
                "optimizer", "forge", "FORGE",
                "red_team", "sentinel", "SENTINEL",
                "blue_team", "remedy", "REMEDY",
                "docstring", "scribe", "SCRIBE",
                "audit", "verity", "VERITY",
            },
        )
    )

    # 16. Project Workspace: Search Code
    registry.register(
        ToolDefinition(
            name="search_project_code",
            description="Search for a text pattern or regex across Python files in the workspace (no shell execution).",
            parameters_schema={
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "Search pattern or regular expression to look for.",
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of matching lines to return (default: 20, max: 100).",
                    },
                },
                "required": ["pattern"],
            },
            handler=search_project_code_handler,
            is_read_only=True,
            allowed_agents={
                "architect", "atlas", "ATLAS",
                "optimizer", "forge", "FORGE",
                "red_team", "sentinel", "SENTINEL",
                "blue_team", "remedy", "REMEDY",
                "docstring", "scribe", "SCRIBE",
                "audit", "verity", "VERITY",
            },
        )
    )

    # 17. Project Workspace: Find Symbol
    registry.register(
        ToolDefinition(
            name="find_symbol",
            description="Locate symbol definitions (functions, classes, assignments) and call sites across the project via AST.",
            parameters_schema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Identifier name of the symbol to locate.",
                    }
                },
                "required": ["name"],
            },
            handler=find_symbol_handler,
            is_read_only=True,
            allowed_agents={
                "architect", "atlas", "ATLAS",
                "optimizer", "forge", "FORGE",
                "red_team", "sentinel", "SENTINEL",
                "blue_team", "remedy", "REMEDY",
                "docstring", "scribe", "SCRIBE",
                "audit", "verity", "VERITY",
            },
        )
    )

    # 18. Project Workspace: Import Graph
    registry.register(
        ToolDefinition(
            name="get_import_graph",
            description="Extract full module import dependency graph, circular imports, and third-party dependencies.",
            parameters_schema={
                "type": "object",
                "properties": {},
                "required": [],
            },
            handler=get_import_graph_handler,
            is_read_only=True,
            allowed_agents={"architect", "atlas", "ATLAS"},
        )
    )

    # 19. Project Workspace: Propose File Patch
    registry.register(
        ToolDefinition(
            name="propose_file_patch",
            description="Stage a proposed modification to a file in the project workspace without writing to disk. Validates AST syntax.",
            parameters_schema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative file path within the project workspace to modify.",
                    },
                    "new_content": {
                        "type": "string",
                        "description": "Complete new content for the file.",
                    },
                    "rationale": {
                        "type": "string",
                        "description": "Explanation or justification for the proposed patch.",
                    },
                },
                "required": ["path", "new_content"],
            },
            handler=propose_file_patch_handler,
            is_read_only=False,
            requires_approval=True,
            allowed_agents={"remedy", "blue_team", "REMEDY", "scribe", "docstring", "SCRIBE"},
        )
    )

    return registry


default_tool_registry = create_standard_tool_registry()

__all__ = [
    "ToolDefinition",
    "ToolRegistry",
    "create_standard_tool_registry",
    "default_tool_registry",
]
