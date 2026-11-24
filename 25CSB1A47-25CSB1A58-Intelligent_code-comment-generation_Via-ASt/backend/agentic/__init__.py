"""Agentic AI Layer for Intelligent Code Comment Generation via AST.

Provides stateful execution loops, extensible tool registries, sub-agent swarms,
and deterministic AST verification gates.
"""

from backend.agentic.tools.registry import ToolDefinition, ToolRegistry

__all__ = [
    "ToolDefinition",
    "ToolRegistry",
]
