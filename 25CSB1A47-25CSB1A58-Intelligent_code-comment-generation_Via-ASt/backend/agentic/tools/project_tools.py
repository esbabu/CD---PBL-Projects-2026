"""Project workspace exploration, inspection, and staging tools for NEXUS agents.

Provides safe multi-file tools routed strictly through ProjectWorkspace:
1. list_project_files(glob="**/*.py") -> paths, line counts.
2. read_project_file(path, start_line=1, end_line=200) -> numbered lines (cap 300 lines per call).
3. search_project_code(pattern, max_results=20) -> file, line, snippet (no shell execution).
4. find_symbol(name) -> definitions (file, line, kind) and call sites using AST.
5. get_import_graph() -> module import dependency graph via ProjectAnalyzer.
6. propose_file_patch(path, new_content, rationale) -> stages unified diff without writing.
"""

from __future__ import annotations

import ast
import fnmatch
import logging
import re
from pathlib import Path, PurePosixPath
from typing import Any, Dict, Set

from backend.project.analyzer import ProjectAnalyzer
from backend.project.change_management import ProjectChangeManager
from backend.project.workspace import ProjectWorkspace
from backend.validator import validate_code

logger = logging.getLogger(__name__)

# Quota configurations
MAX_PROJECT_TOOL_CALLS: int = 40
MAX_PROJECT_BYTES_READ: int = 1_000_000  # 1 MB total bytes read per session
MAX_LINES_PER_READ: int = 300
MAX_SEARCH_RESULTS: int = 20

PROJECT_TOOL_NAMES: Set[str] = {
    "list_project_files",
    "read_project_file",
    "search_project_code",
    "find_symbol",
    "get_import_graph",
    "propose_file_patch",
}


def _get_workspace_and_enforce_call_quota(context: Any) -> ProjectWorkspace:
    """Retrieve ProjectWorkspace for the active session, checking call quota."""
    if context is None or not hasattr(context, "metadata"):
        raise ValueError("No session context provided for project workspace operation.")

    workspace_id = context.metadata.get("project_workspace_id")
    if not workspace_id:
        raise ValueError("No project workspace attached to session.")

    current_calls = context.metadata.setdefault("project_tool_calls_count", 0)
    if current_calls >= MAX_PROJECT_TOOL_CALLS:
        raise ValueError(
            f"Project tool call quota exceeded: maximum of {MAX_PROJECT_TOOL_CALLS} "
            "project tool calls per session reached."
        )
    context.metadata["project_tool_calls_count"] = current_calls + 1

    from backend.project.routes import _get_workspace

    try:
        return _get_workspace(workspace_id)
    except KeyError:
        ws = ProjectWorkspace(workspace_id=workspace_id)
        if not ws.project_dir.exists():
            raise ValueError(f"Project workspace '{workspace_id}' was not found.")
        return ws


def _record_bytes_read(context: Any, bytes_count: int) -> None:
    """Track total bytes read by project tools in this session, enforcing limits."""
    if context is None or not hasattr(context, "metadata"):
        return
    current_bytes = context.metadata.setdefault("project_tool_bytes_read", 0)
    if current_bytes + bytes_count > MAX_PROJECT_BYTES_READ:
        raise ValueError(
            f"Project bytes read quota exceeded: total bytes read limit ({MAX_PROJECT_BYTES_READ} bytes) exceeded."
        )
    context.metadata["project_tool_bytes_read"] = current_bytes + bytes_count


def _matches_glob(rel_path: str, pattern: str) -> bool:
    """Check if relative path matches glob, handling recursive wildcard prefix correctly."""
    if PurePosixPath(rel_path).match(pattern) or fnmatch.fnmatch(rel_path, pattern):
        return True
    if pattern.startswith("**/"):
        sub_pat = pattern[3:]
        if PurePosixPath(rel_path).match(sub_pat) or fnmatch.fnmatch(rel_path, sub_pat):
            return True
    return False


def list_project_files_handler(args: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """List files in the project workspace matching glob pattern, with line counts."""
    ws = _get_workspace_and_enforce_call_quota(context)
    pattern = args.get("glob") or "**/*.py"

    if ".." in Path(pattern).parts or pattern.startswith("/") or pattern.startswith("\\"):
        raise ValueError(f"Invalid glob pattern (path traversal rejected): '{pattern}'")

    all_files = ws.list_files()
    matched_files = []
    total_bytes = 0

    for rel_path in all_files:
        if _matches_glob(rel_path, pattern):
            try:
                content = ws.read_file(rel_path)
                file_bytes = len(content.encode("utf-8"))
                total_bytes += file_bytes
                line_count = len(content.splitlines())
                matched_files.append({
                    "path": rel_path,
                    "line_count": line_count,
                    "size_bytes": file_bytes,
                })
            except Exception as exc:
                logger.debug("Could not read file '%s' for listing: %s", rel_path, exc)

    _record_bytes_read(context, total_bytes)
    return {
        "glob": pattern,
        "total_files": len(matched_files),
        "files": matched_files,
    }


def read_project_file_handler(args: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Read numbered lines from a file in the workspace within specified line bounds (cap 300 lines)."""
    ws = _get_workspace_and_enforce_call_quota(context)
    path = args.get("path")
    if not path or not isinstance(path, str):
        raise ValueError("A valid file 'path' string is required.")

    start_line = int(args.get("start_line", 1) or 1)
    end_line = int(args.get("end_line", 200) or 200)

    if start_line < 1:
        start_line = 1
    if end_line < start_line:
        raise ValueError(f"end_line ({end_line}) cannot be less than start_line ({start_line}).")

    # Enforce line cap: maximum 300 lines per call
    if (end_line - start_line + 1) > MAX_LINES_PER_READ:
        end_line = start_line + MAX_LINES_PER_READ - 1

    # Safe read through ws.read_file (which enforces safe path resolution and prevents traversal)
    content = ws.read_file(path)
    file_bytes = len(content.encode("utf-8"))
    _record_bytes_read(context, file_bytes)

    lines = content.splitlines()
    total_lines = len(lines)

    actual_start = min(start_line, max(1, total_lines))
    actual_end = min(end_line, total_lines)

    if total_lines == 0 or actual_start > total_lines:
        numbered = []
        raw_slice = []
    else:
        raw_slice = lines[actual_start - 1 : actual_end]
        numbered = [f"{i}: {lines[i - 1]}" for i in range(actual_start, actual_end + 1)]

    return {
        "path": path,
        "start_line": actual_start,
        "end_line": actual_end,
        "total_lines": total_lines,
        "line_count": len(numbered),
        "lines": numbered,
        "raw_lines": raw_slice,
        "content": "\n".join(numbered),
    }


def search_project_code_handler(args: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Search for pattern across project files using plain substring or regex (no shell)."""
    ws = _get_workspace_and_enforce_call_quota(context)
    pattern = args.get("pattern")
    if not pattern or not isinstance(pattern, str):
        raise ValueError("A non-empty 'pattern' string is required.")
    if len(pattern) > 200:
        raise ValueError("Search pattern exceeds maximum length of 200 characters.")

    max_results = int(args.get("max_results", MAX_SEARCH_RESULTS) or MAX_SEARCH_RESULTS)
    max_results = max(1, min(max_results, 100))

    use_regex = True
    try:
        compiled_re = re.compile(pattern)
    except re.error:
        use_regex = False
        compiled_re = None

    matches = []
    total_bytes = 0

    for rel_path in ws.list_python_files():
        try:
            content = ws.read_file(rel_path)
            total_bytes += len(content.encode("utf-8"))
            lines = content.splitlines()
            for line_no, line_text in enumerate(lines, 1):
                is_match = False
                if use_regex and compiled_re:
                    is_match = bool(compiled_re.search(line_text))
                else:
                    is_match = pattern in line_text

                if is_match:
                    matches.append({
                        "file": rel_path,
                        "line": line_no,
                        "snippet": line_text.strip(),
                    })
                    if len(matches) >= max_results:
                        break
        except Exception:
            continue
        if len(matches) >= max_results:
            break

    _record_bytes_read(context, total_bytes)
    return {
        "pattern": pattern,
        "is_regex": use_regex,
        "total_matches": len(matches),
        "matches": matches,
    }


def find_symbol_handler(args: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Find symbol definitions (file, line, kind) and call sites across the workspace using AST."""
    ws = _get_workspace_and_enforce_call_quota(context)
    name = args.get("name")
    if not name or not isinstance(name, str):
        raise ValueError("A valid symbol 'name' string is required.")
    name = name.strip()
    if not name.isidentifier():
        raise ValueError(f"Symbol name '{name}' must be a valid Python identifier.")

    definitions = []
    call_sites = []
    total_bytes = 0

    for rel_path in ws.list_python_files():
        try:
            content = ws.read_file(rel_path)
            total_bytes += len(content.encode("utf-8"))
            tree = ast.parse(content)
        except Exception:
            continue

        for node in ast.walk(tree):
            # Definitions
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
                definitions.append({
                    "file": rel_path,
                    "line": node.lineno,
                    "kind": "function",
                })
            elif isinstance(node, ast.ClassDef) and node.name == name:
                definitions.append({
                    "file": rel_path,
                    "line": node.lineno,
                    "kind": "class",
                })
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == name:
                        definitions.append({
                            "file": rel_path,
                            "line": getattr(node, "lineno", 1),
                            "kind": "variable",
                        })
            elif isinstance(node, ast.AnnAssign):
                if isinstance(node.target, ast.Name) and node.target.id == name:
                    definitions.append({
                        "file": rel_path,
                        "line": getattr(node, "lineno", 1),
                        "kind": "variable",
                    })

            # Call sites
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == name:
                    call_sites.append({
                        "file": rel_path,
                        "line": getattr(node, "lineno", 1),
                        "kind": "direct_call",
                    })
                elif isinstance(node.func, ast.Attribute) and node.func.attr == name:
                    call_sites.append({
                        "file": rel_path,
                        "line": getattr(node, "lineno", 1),
                        "kind": "attribute_call",
                    })

    _record_bytes_read(context, total_bytes)
    return {
        "symbol": name,
        "definitions": definitions,
        "call_sites": call_sites,
        "total_definitions": len(definitions),
        "total_call_sites": len(call_sites),
    }


def get_import_graph_handler(args: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Extract full import dependency graph using ProjectAnalyzer."""
    ws = _get_workspace_and_enforce_call_quota(context)
    analyzer = ProjectAnalyzer(ws)
    graph = analyzer.build_dependency_graph()
    return graph


def propose_file_patch_handler(args: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Validate syntax and stage a proposed patch via ProjectChangeManager without modifying files."""
    ws = _get_workspace_and_enforce_call_quota(context)
    path = args.get("path")
    new_content = args.get("new_content")
    rationale = args.get("rationale") or "Proposed patch"

    if not path or not isinstance(path, str):
        raise ValueError("A valid file 'path' string is required.")
    if new_content is None or not isinstance(new_content, str):
        raise ValueError("A 'new_content' string is required.")

    # 1. Path safety check (raises ValueError if path traversal detected)
    ws.resolve_safe_path(path)

    # 2. Syntax validation if Python file
    if path.endswith(".py"):
        syntax_ok = validate_code(new_content)
        if syntax_ok is not True:
            raise ValueError(f"Syntax validation failed for proposed patch to '{path}': {syntax_ok}")

    # 3. Stage through ProjectChangeManager (does NOT write to files!)
    cm = ProjectChangeManager(ws)
    proposal = cm.propose_multi_file_changes(
        {path: new_content},
        author="NEXUS Agent",
        reason=rationale,
    )
    proposal_id = proposal["proposal_id"]

    # 4. Attach pending proposal to session context if available
    if context is not None and hasattr(context, "pending_approval"):
        context.pending_approval = {
            "agent": getattr(context, "agent_key", "NEXUS"),
            "tool": "propose_file_patch",
            "proposal_id": proposal_id,
            "path": path,
            "arguments": args,
            "requires_approval": True,
        }
        if hasattr(context, "approval_status"):
            context.approval_status = "required"

    diff_info = proposal.get("diffs_by_file", {}).get(path, {})
    return {
        "status": "pending_approval",
        "proposal_id": proposal_id,
        "path": path,
        "diff": diff_info.get("diff", ""),
        "added_lines": proposal.get("total_added_lines", 0),
        "removed_lines": proposal.get("total_removed_lines", 0),
        "all_safety_checks_passed": proposal.get("all_safety_checks_passed", True),
        "rationale": rationale,
        "requires_approval": True,
        "modified_files": False,
    }
