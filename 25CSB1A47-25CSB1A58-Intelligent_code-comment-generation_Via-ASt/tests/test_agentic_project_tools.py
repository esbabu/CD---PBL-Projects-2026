"""Tests for safe multi-file project workspace tools and agent interactions."""

from __future__ import annotations

import pytest
from pathlib import Path

from backend.agentic.agents.specialists import (
    ArchitectAgent,
    AuditAgent,
    BlueTeamAgent,
    DocstringAgent,
    OptimizerAgent,
    RedTeamAgent,
)
from backend.agentic.runtime import AgentRuntime
from backend.agentic.session import AgentSession, InMemorySessionRepository, SessionManager
from backend.agentic.tools import create_standard_tool_registry
from backend.agentic.tools.project_tools import (
    MAX_PROJECT_BYTES_READ,
    MAX_PROJECT_TOOL_CALLS,
    find_symbol_handler,
    get_import_graph_handler,
    list_project_files_handler,
    propose_file_patch_handler,
    read_project_file_handler,
    search_project_code_handler,
)
from backend.project.change_management import ProjectChangeManager
from backend.project.routes import _ACTIVE_WORKSPACES
from backend.project.workspace import ProjectWorkspace


@pytest.fixture
def workspace_setup(tmp_path: Path):
    """Create a temporary project workspace populated with sample Python files."""
    base_dir = tmp_path / "workspaces"
    ws = ProjectWorkspace(workspace_id="test-ws-123", base_storage_dir=base_dir)
    ws.write_file("main.py", "import config\n\ndef run():\n    print(config.SECRET_TOKEN)\n")
    ws.write_file("config.py", "SECRET_TOKEN = 'sk-super-secret-token-abcdef12345'\nDEBUG = True\n")
    _ACTIVE_WORKSPACES[ws.workspace_id] = ws

    session = AgentSession(
        session_id="test-session-456",
        original_code=ws.read_file("main.py"),
        original_code_digest="digest-123",
        current_code=ws.read_file("main.py"),
        task="Audit the project for security vulnerabilities and review code.",
    )
    session.metadata["project_workspace_id"] = ws.workspace_id
    session.metadata["active_file"] = "main.py"

    yield ws, session

    ws.cleanup()
    _ACTIVE_WORKSPACES.pop(ws.workspace_id, None)


def test_allowed_tools_per_agent():
    """Verify tool permissions per agent specification:

    ATLAS gets 1-5; FORGE gets 1-4; SENTINEL gets 1-4;
    REMEDY gets 1-4 and 6; SCRIBE gets 1-4 and 6; VERITY gets 1-4.
    """
    registry = create_standard_tool_registry()

    atlas = ArchitectAgent(registry)
    forge = OptimizerAgent(registry)
    sentinel = RedTeamAgent(registry)
    remedy = BlueTeamAgent(registry)
    scribe = DocstringAgent(registry)
    verity = AuditAgent(registry)

    tools_1_4 = {"list_project_files", "read_project_file", "search_project_code", "find_symbol"}
    tools_1_5 = tools_1_4 | {"get_import_graph"}
    tools_1_4_6 = tools_1_4 | {"propose_file_patch"}

    assert tools_1_5.issubset(atlas.allowed_tools)
    assert "propose_file_patch" not in atlas.allowed_tools

    assert tools_1_4.issubset(forge.allowed_tools)
    assert "get_import_graph" not in forge.allowed_tools
    assert "propose_file_patch" not in forge.allowed_tools

    assert tools_1_4.issubset(sentinel.allowed_tools)
    assert "get_import_graph" not in sentinel.allowed_tools
    assert "propose_file_patch" not in sentinel.allowed_tools

    assert tools_1_4_6.issubset(remedy.allowed_tools)
    assert "get_import_graph" not in remedy.allowed_tools

    assert tools_1_4_6.issubset(scribe.allowed_tools)
    assert "get_import_graph" not in scribe.allowed_tools

    assert tools_1_4.issubset(verity.allowed_tools)
    assert "get_import_graph" not in verity.allowed_tools
    assert "propose_file_patch" not in verity.allowed_tools


def test_tools_hidden_and_rejected_without_workspace(workspace_setup):
    """Tools must not be offered or executed when no workspace is attached."""
    _, session = workspace_setup
    registry = create_standard_tool_registry()
    sentinel = RedTeamAgent(registry)

    # With workspace: project tools are present
    msgs_with_ws = sentinel.format_messages(session, "Audit project")
    prompt_with_ws = msgs_with_ws[0]["content"]
    assert "read_project_file" in prompt_with_ws

    # Without workspace: project tools are hidden
    no_ws_session = AgentSession(
        session_id="no-ws-sess",
        original_code="x = 1",
        original_code_digest="d",
        current_code="x = 1",
        task="Test",
    )
    msgs_without_ws = sentinel.format_messages(no_ws_session, "Audit project")
    prompt_without_ws = msgs_without_ws[0]["content"]
    assert "read_project_file" not in prompt_without_ws
    assert "list_project_files" not in prompt_without_ws

    # Direct execution without workspace raises PermissionError or ValueError
    with pytest.raises(PermissionError):
        sentinel.execute_tool(no_ws_session, "read_project_file", {"path": "main.py"})


def test_path_traversal_rejected(workspace_setup):
    """Path traversal attempts via .. or drive letters are rejected."""
    _, session = workspace_setup

    with pytest.raises(ValueError, match="Path traversal attempt rejected"):
        read_project_file_handler({"path": "../../etc/passwd"}, session)

    with pytest.raises(ValueError, match="Path traversal attempt rejected"):
        read_project_file_handler({"path": "../outside.py"}, session)

    with pytest.raises(ValueError, match="Path traversal attempt rejected"):
        propose_file_patch_handler({"path": "../outside.py", "new_content": "x = 1"}, session)

    with pytest.raises(ValueError, match="Invalid glob pattern"):
        list_project_files_handler({"glob": "../../../*.py"}, session)


def test_reading_outside_workspace_rejected(workspace_setup, tmp_path: Path):
    """Reading files outside the workspace directory sandbox is rejected."""
    _, session = workspace_setup

    outside_file = tmp_path / "secret.txt"
    outside_file.write_text("super_secret_data")

    # Trying to escape sandbox
    with pytest.raises(ValueError):
        read_project_file_handler({"path": f"../{outside_file.name}"}, session)

    # Trying to read a non-existent file inside workspace raises FileNotFoundError
    with pytest.raises(FileNotFoundError):
        read_project_file_handler({"path": "non_existent_file.py"}, session)


def test_quota_enforced(workspace_setup):
    """Enforce both per-session tool call quota and total bytes read limit."""
    _, session = workspace_setup

    # 1. Enforce call quota
    session.metadata["project_tool_calls_count"] = MAX_PROJECT_TOOL_CALLS
    with pytest.raises(ValueError, match="Project tool call quota exceeded"):
        list_project_files_handler({"glob": "**/*.py"}, session)

    # Reset call count
    session.metadata["project_tool_calls_count"] = 0

    # 2. Enforce byte read quota
    session.metadata["project_tool_bytes_read"] = MAX_PROJECT_BYTES_READ
    with pytest.raises(ValueError, match="Project bytes read quota exceeded"):
        read_project_file_handler({"path": "main.py"}, session)


def test_propose_file_patch_stages_without_modifying(workspace_setup):
    """propose_file_patch validates syntax and stages diff without modifying files."""
    ws, session = workspace_setup
    registry = create_standard_tool_registry()

    tool = registry.get("propose_file_patch")
    assert tool is not None
    assert tool.requires_approval is True
    assert tool.is_read_only is False

    original_main = ws.read_file("main.py")

    # Invalid syntax patch rejected
    with pytest.raises(ValueError, match="Syntax validation failed"):
        propose_file_patch_handler(
            {"path": "main.py", "new_content": "def broken(:\n    pass\n"},
            session,
        )

    # Valid syntax patch staged
    res = propose_file_patch_handler(
        {"path": "main.py", "new_content": "import config\n\ndef run():\n    print('updated')\n"},
        session,
    )

    assert res["status"] == "pending_approval"
    assert res["requires_approval"] is True
    assert res["modified_files"] is False
    assert "proposal_id" in res
    assert res["proposal_id"].startswith("prop_")
    assert "+    print('updated')" in res["diff"]

    # File on disk must remain unchanged!
    assert ws.read_file("main.py") == original_main


def test_approval_commits_and_creates_snapshot(workspace_setup):
    """Approving a staged proposal commits file changes and generates a recovery snapshot."""
    ws, session = workspace_setup
    cm = ProjectChangeManager(ws)

    new_code = "import config\n\ndef run():\n    print('approved modification')\n"
    res = propose_file_patch_handler(
        {"path": "main.py", "new_content": new_code, "rationale": "Add approval feature"},
        session,
    )
    proposal_id = res["proposal_id"]

    # Commit proposal
    commit_res = cm.approve_and_commit_changes(proposal_id)
    assert commit_res["status"] == "committed"
    assert "main.py" in commit_res["files_committed"]
    assert "rollback_snapshot_id" in commit_res

    # File must now be updated on disk
    assert ws.read_file("main.py") == new_code

    # Recovery snapshot must be recorded in manifest
    snapshots = cm.list_snapshots()
    assert len(snapshots) >= 1
    assert any(s["snapshot_id"] == commit_res["rollback_snapshot_id"] for s in snapshots)


def test_rollback_restores(workspace_setup):
    """Rolling back to the pre-apply snapshot restores the exact prior workspace state."""
    ws, session = workspace_setup
    cm = ProjectChangeManager(ws)

    original_code = ws.read_file("main.py")

    res = propose_file_patch_handler(
        {"path": "main.py", "new_content": "def run(): pass\n", "rationale": "test rollback"},
        session,
    )
    commit_res = cm.approve_and_commit_changes(res["proposal_id"])
    assert ws.read_file("main.py") == "def run(): pass\n"

    # Roll back using the snapshot ID
    rollback_res = cm.rollback_to_snapshot(commit_res["rollback_snapshot_id"])
    assert rollback_res["status"] == "rolled_back"
    assert ws.read_file("main.py") == original_code


def test_find_symbol_across_workspace(workspace_setup):
    """find_symbol locates definitions and call sites using AST across workspace files."""
    ws, session = workspace_setup
    ws.write_file("helpers.py", "def helper_util(val):\n    return val * 2\n")
    ws.write_file("consumer.py", "from helpers import helper_util\nres = helper_util(21)\n")

    res = find_symbol_handler({"name": "helper_util"}, session)

    assert res["symbol"] == "helper_util"
    assert res["total_definitions"] >= 1
    assert any(d["file"] == "helpers.py" and d["kind"] == "function" for d in res["definitions"])

    assert res["total_call_sites"] >= 1
    assert any(c["file"] == "consumer.py" for c in res["call_sites"])


def test_search_and_import_graph(workspace_setup):
    """search_project_code and get_import_graph operate correctly across project files."""
    _, session = workspace_setup

    # Search code
    search_res = search_project_code_handler({"pattern": "SECRET_TOKEN"}, session)
    assert search_res["total_matches"] >= 2
    matched_files = {m["file"] for m in search_res["matches"]}
    assert "main.py" in matched_files
    assert "config.py" in matched_files

    # Import graph
    graph = get_import_graph_handler({}, session)
    assert "internal_dependency_graph" in graph
    assert "config" in graph.get("internal_dependency_graph", {}).get("main", [])


def test_agentic_run_sentinel_reads_config_and_cites_file_and_line(workspace_setup):
    """Acceptance test: SENTINEL executes a project run, discovers the 2nd file (config.py),

    calls read_project_file, and outputs a finding that cites config.py and line number.
    """
    ws, session = workspace_setup
    registry = create_standard_tool_registry()

    # Track emitted events to verify tool_started/completed with path
    emitted_events = []

    def event_collector(event_name: str, payload: dict):
        emitted_events.append((event_name, payload))

    session.event_callback = event_collector

    _ = AgentRuntime(
        tools=registry,
        session_manager=SessionManager(repository=InMemorySessionRepository()),
    )
    sentinel = RedTeamAgent(registry)

    # Execute SENTINEL deterministic turn
    result = sentinel.deterministic_turn(session, "Audit project workspace for secrets")

    assert result["status"] == "completed"
    findings = result["findings"]

    # Verify config.py was discovered and cited
    config_findings = [f for f in findings if f.get("file") == "config.py"]
    assert len(config_findings) >= 1, f"Expected findings in config.py, got: {findings}"

    secret_finding = config_findings[0]
    assert secret_finding["file"] == "config.py"
    target_line = secret_finding.get("target_line") or secret_finding.get("ast_sink_line")
    assert target_line == 1
    assert "[config.py:1]" in secret_finding["summary"]

    # Verify tool events were emitted with path
    started_tools = [p for e, p in emitted_events if e == "tool_started"]
    completed_tools = [p for e, p in emitted_events if e == "tool_completed"]

    read_calls = [p for p in started_tools if p.get("tool") == "read_project_file"]
    assert len(read_calls) >= 1
    assert read_calls[0].get("path") == "config.py"

    completed_read_calls = [p for p in completed_tools if p.get("tool") == "read_project_file"]
    assert len(completed_read_calls) >= 1
    assert completed_read_calls[0].get("path") == "config.py"
