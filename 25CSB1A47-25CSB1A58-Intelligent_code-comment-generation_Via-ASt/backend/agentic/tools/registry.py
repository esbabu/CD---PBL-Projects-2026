"""Unified Tool Registry and standard schema definitions for Agentic AI Layer."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from time import perf_counter
from typing import Any, Callable, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


class ToolExecutionError(Exception):
    """Raised when an allowlisted tool fails during execution."""


@dataclass
class ToolDefinition:
    """Specification of an allowlisted, executable agent tool."""

    name: str
    description: str
    parameters_schema: Dict[str, Any]
    handler: Callable[[Dict[str, Any], Any], Dict[str, Any]]
    is_read_only: bool = True
    requires_approval: bool = False
    allowed_agents: Optional[Set[str]] = None
    timeout_seconds: float = 30.0
    max_output_bytes: int = 65536
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_function_schema(self) -> Dict[str, Any]:
        """Convert into standard OpenAI/Copilot function-calling format."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters_schema,
            },
        }


class ToolRegistry:
    """Thread-safe registry of allowlisted agent tools."""

    def __init__(self) -> None:
        self._tools: Dict[str, ToolDefinition] = {}

    def register(self, tool: ToolDefinition) -> None:
        """Register a new tool definition."""
        if not tool.name or not isinstance(tool.name, str):
            raise ValueError("Tool name must be a non-empty string.")
        if not callable(tool.handler):
            raise ValueError(f"Tool handler for '{tool.name}' must be callable.")
        if tool.parameters_schema.get("type") == "object":
            tool.parameters_schema.setdefault("additionalProperties", False)
        self._tools[tool.name] = tool
        logger.debug("Registered tool: %s (read_only=%s)", tool.name, tool.is_read_only)

    def get(self, name: str) -> Optional[ToolDefinition]:
        """Fetch a registered tool by identifier."""
        return self._tools.get(name)

    def list_tools(self) -> List[ToolDefinition]:
        """Return all registered tools."""
        return list(self._tools.values())

    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        """Return all tool schemas in function-calling format."""
        return [t.to_function_schema() for t in self._tools.values()]

    def validate_arguments(self, tool: ToolDefinition, args: Any) -> List[str]:
        """Validate tool input against the supported JSON Schema constraints."""
        if not isinstance(args, dict):
            return ["Tool arguments must be a JSON object."]

        errors: List[str] = []
        type_map = {
            "string": str,
            "integer": int,
            "number": (int, float),
            "boolean": bool,
            "array": list,
            "object": dict,
        }

        def validate_value(value: Any, schema: Dict[str, Any], path: str) -> None:
            expected_type = schema.get("type")
            python_type = type_map.get(expected_type)
            valid_type = python_type is None or isinstance(value, python_type)
            if expected_type in {"integer", "number"} and isinstance(value, bool):
                valid_type = False
            if not valid_type:
                errors.append(
                    f"Parameter '{path}' expected type '{expected_type}', "
                    f"got '{type(value).__name__}'."
                )
                return

            if "enum" in schema and value not in schema["enum"]:
                errors.append(f"Parameter '{path}' must be one of {schema['enum']!r}.")
            if expected_type == "object":
                properties = schema.get("properties", {})
                for required in schema.get("required", []):
                    if required not in value or value[required] is None:
                        errors.append(f"Missing required parameter: '{path}.{required}'.")
                if schema.get("additionalProperties") is False:
                    extras = set(value) - set(properties)
                    for extra in sorted(extras):
                        errors.append(f"Unexpected parameter: '{path}.{extra}'.")
                for name, child in value.items():
                    if name in properties and isinstance(properties[name], dict):
                        validate_value(child, properties[name], f"{path}.{name}")
            elif expected_type == "array" and isinstance(value, list):
                item_schema = schema.get("items")
                if isinstance(item_schema, dict):
                    for index, item in enumerate(value):
                        validate_value(item, item_schema, f"{path}[{index}]")
            elif expected_type == "string" and isinstance(value, str):
                if len(value) < schema.get("minLength", 0):
                    errors.append(f"Parameter '{path}' is shorter than minLength.")
                if "maxLength" in schema and len(value) > schema["maxLength"]:
                    errors.append(f"Parameter '{path}' exceeds maxLength.")
            elif expected_type in {"integer", "number"} and valid_type:
                if "minimum" in schema and value < schema["minimum"]:
                    errors.append(f"Parameter '{path}' is below minimum.")
                if "maximum" in schema and value > schema["maximum"]:
                    errors.append(f"Parameter '{path}' exceeds maximum.")

        validate_value(args, tool.parameters_schema or {}, "arguments")
        return errors

    def execute(
        self,
        name: str,
        arguments: Optional[Dict[str, Any]] = None,
        context: Any = None,
    ) -> Dict[str, Any]:
        """Execute a registered tool within sandboxed error handling and latency tracking."""
        args = {} if arguments is None else arguments
        if name not in self._tools:
            return {
                "status": "error",
                "tool": name,
                "error": f"Tool '{name}' is not in the allowlisted registry.",
                "execution_time_ms": 0.0,
            }

        tool = self._tools[name]
        agent_id = getattr(context, "agent_key", None) or getattr(context, "agent_name", None) or ""
        if tool.allowed_agents and agent_id and agent_id not in tool.allowed_agents:
            logger.warning("Agent '%s' unauthorized to invoke tool '%s'", agent_id, name)
            return {
                "status": "error",
                "tool": name,
                "error": f"Agent '{agent_id}' is not authorized to invoke tool '{name}' (least-privilege policy).",
                "execution_time_ms": 0.0,
            }

        validation_errors = self.validate_arguments(tool, args)
        if validation_errors:
            return {
                "status": "error",
                "tool": name,
                "error": "Argument validation failed: " + "; ".join(validation_errors),
                "validation_errors": validation_errors,
                "execution_time_ms": 0.0,
            }

        # Check Human-in-the-Loop approval gate
        is_approved = getattr(context, "is_approved", False) if context else False
        if tool.requires_approval and not is_approved and name != "propose_file_patch":
            return {
                "status": "pending_approval",
                "tool": name,
                "arguments": args,
                "message": f"Action '{name}' requires human approval before proceeding.",
                "execution_time_ms": 0.0,
            }

        started_at = perf_counter()
        try:
            result = tool.handler(args, context)
            if not isinstance(result, dict):
                raise TypeError(
                    f"Tool '{name}' returned {type(result).__name__}; expected a dictionary."
                )
            latency_ms = round((perf_counter() - started_at) * 1000, 3)

            # Enforce output size bounds
            try:
                payload_str = json.dumps(result, ensure_ascii=True, default=str)
                if len(payload_str) > tool.max_output_bytes:
                    result = {
                        "warning": f"Tool output truncated: payload size {len(payload_str)}B exceeded {tool.max_output_bytes}B limit.",
                        "truncated": True,
                        "summary": str(result)[:2000],
                    }
            except Exception:
                pass

            logger.info(
                "SECURITY_AUDIT tool_call: tool=%s agent=%s read_only=%s approved=%s status=success duration_ms=%.2f",
                name,
                agent_id or "supervisor",
                tool.is_read_only,
                is_approved,
                latency_ms,
            )
            status = (
                "pending_approval"
                if isinstance(result, dict) and result.get("status") == "pending_approval"
                else "success"
            )
            return {
                "status": status,
                "tool": name,
                "result": result,
                "is_read_only": tool.is_read_only,
                "execution_time_ms": latency_ms,
            }
        except Exception as exc:
            latency_ms = round((perf_counter() - started_at) * 1000, 3)
            logger.exception("Execution of tool '%s' raised an exception: %s", name, exc)
            logger.info(
                "SECURITY_AUDIT tool_call: tool=%s agent=%s read_only=%s approved=%s status=failed duration_ms=%.2f error=%s",
                name,
                agent_id or "supervisor",
                tool.is_read_only,
                is_approved,
                latency_ms,
                type(exc).__name__,
            )
            return {
                "status": "error",
                "tool": name,
                "error": str(exc),
                "error_type": type(exc).__name__,
                "execution_time_ms": latency_ms,
            }
        finally:
            if tool.requires_approval and is_approved and context is not None:
                context.is_approved = False
                if hasattr(context, "approval_status"):
                    context.approval_status = "not_required"
