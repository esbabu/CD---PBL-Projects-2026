"""Project Engineering Workbench API Routes.

Exposes REST endpoints for multi-file project workspaces:
- Safe archive upload and extraction
- Workspace file tree exploration and safe file I/O
- Architectural intelligence and dependency graph discovery
- Project-level AST analysis, dead code, and duplication detection
- Ground-truth documentation generation (README, Architecture, API catalog)
- Sandboxed developer tools execution (pytest, ruff, mypy, bandit)
- Consolidated project health reports
- Reversible change management, multi-file diffs, snapshots, and rollback
- Project ZIP export and report downloads
"""

from __future__ import annotations

import io
import logging
from pathlib import Path
from typing import Dict

from flask import Blueprint, jsonify, request, send_file

from backend.project.analyzer import ProjectAnalyzer
from backend.project.assistant_service import (
    ProjectAssistantError,
    chat_about_project,
    propose_project_changes as generate_project_change_proposal,
    stage_agentic_project_candidate,
)
from backend.project.change_management import ProjectChangeManager
from backend.project.code_intelligence import ProjectCodeIntelligence
from backend.project.documentation_generator import (
    ProjectDocumentationGenerator,
)
from backend.project.engineering_tools import EngineeringToolsRunner
from backend.project.health_report import ProjectHealthReporter
from backend.project.workspace import (
    DEFAULT_WORKSPACES_ROOT,
    ArchiveSecurityError,
    ProjectWorkspace,
)

logger = logging.getLogger(__name__)

project_routes = Blueprint("project_workbench", __name__, url_prefix="/api/project")

# In-memory registry of active workspaces (keyed by workspace_id)
_ACTIVE_WORKSPACES: Dict[str, ProjectWorkspace] = {}


def _get_workspace(workspace_id: str) -> ProjectWorkspace:
    """Retrieve or reconstruct a ProjectWorkspace by ID."""
    if workspace_id in _ACTIVE_WORKSPACES:
        return _ACTIVE_WORKSPACES[workspace_id]
    if (
        not workspace_id
        or workspace_id in {".", ".."}
        or "/" in workspace_id
        or "\\" in workspace_id
        or "\0" in workspace_id
    ):
        raise KeyError(f"Workspace '{workspace_id}' not found.")
    workspaces_root = Path(DEFAULT_WORKSPACES_ROOT).resolve()
    workspace_dir = (workspaces_root / workspace_id).resolve()
    if workspace_dir.parent != workspaces_root or not (workspace_dir / "project").is_dir():
        raise KeyError(f"Workspace '{workspace_id}' not found.")
    ws = ProjectWorkspace(workspace_id=workspace_id)
    _ACTIVE_WORKSPACES[workspace_id] = ws
    return ws


@project_routes.route("/upload", methods=["POST"])
def upload_project_archive():
    """Upload and safely extract a project ZIP archive into a new workspace."""
    if "archive" not in request.files:
        # Check raw body
        archive_bytes = request.get_data()
        if not archive_bytes:
            return jsonify({"error": "No archive file provided in request."}), 400
    else:
        file_obj = request.files["archive"]
        archive_bytes = file_obj.read()

    ws = ProjectWorkspace()
    try:
        extracted = ws.load_from_zip(archive_bytes)
        _ACTIVE_WORKSPACES[ws.workspace_id] = ws
        return jsonify({
            "status": "created",
            "workspace_id": ws.workspace_id,
            "total_files_extracted": len(extracted),
            "files": extracted[:20],
        }), 201
    except ArchiveSecurityError as exc:
        ws.cleanup()
        return jsonify({"error": f"Archive rejected: {exc}"}), 400
    except Exception as exc:
        ws.cleanup()
        logger.exception("Project archive upload failed")
        return jsonify({"error": f"Failed to extract project: {exc}"}), 500


@project_routes.route("/create", methods=["POST"])
def create_project_from_files():
    """Create a new project workspace from a dictionary of files."""
    data = request.get_json(silent=True) or {}
    files_map = data.get("files", {})
    if not isinstance(files_map, dict) or not files_map:
        return jsonify({"error": "Request body must contain non-empty 'files' dictionary."}), 400

    ws = ProjectWorkspace()
    try:
        created = ws.load_files_dict(files_map)
        _ACTIVE_WORKSPACES[ws.workspace_id] = ws
        return jsonify({
            "status": "created",
            "workspace_id": ws.workspace_id,
            "total_files_created": len(created),
            "files": created,
        }), 201
    except Exception as exc:
        ws.cleanup()
        return jsonify({"error": str(exc)}), 400


@project_routes.route("/<workspace_id>/tree", methods=["GET"])
def get_workspace_tree(workspace_id: str):
    """Retrieve the hierarchical file tree of the workspace."""
    try:
        ws = _get_workspace(workspace_id)
        tree = ws.get_file_tree()
        return jsonify({
            "workspace_id": workspace_id,
            "tree": tree,
            "python_files": ws.list_python_files(),
        })
    except KeyError as exc:
        return jsonify({"error": str(exc)}), 404


@project_routes.route("/<workspace_id>/file", methods=["GET"])
def read_workspace_file(workspace_id: str):
    """Read a specific file from the workspace."""
    rel_path = request.args.get("path", "").strip()
    if not rel_path:
        return jsonify({"error": "Query parameter 'path' is required."}), 400
    try:
        ws = _get_workspace(workspace_id)
        content = ws.read_file(rel_path)
        return jsonify({
            "workspace_id": workspace_id,
            "path": rel_path,
            "content": content,
            "lines_count": len(content.splitlines()),
        })
    except KeyError as exc:
        return jsonify({"error": str(exc)}), 404
    except FileNotFoundError as exc:
        return jsonify({"error": str(exc)}), 404
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


@project_routes.route("/<workspace_id>/file", methods=["POST"])
def write_workspace_file(workspace_id: str):
    """Write or update a file in the workspace."""
    data = request.get_json(silent=True) or {}
    rel_path = data.get("path", "").strip()
    content = data.get("content")
    if not rel_path or content is None:
        return jsonify({"error": "'path' and 'content' are required in request body."}), 400
    try:
        ws = _get_workspace(workspace_id)
        ws.write_file(rel_path, content)
        return jsonify({"status": "saved", "path": rel_path})
    except KeyError as exc:
        return jsonify({"error": str(exc)}), 404
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


@project_routes.route("/<workspace_id>/assistant/chat", methods=["POST"])
def chat_about_workspace(workspace_id: str):
    """Answer a question using bounded context read from the project workspace."""
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "A JSON request body is required."}), 400
    include_context = data.get("include_project_context", True)
    if not isinstance(include_context, bool):
        return jsonify({"error": "include_project_context must be a boolean."}), 400
    response_mode = data.get("response_mode", "answer")
    if not isinstance(response_mode, str) or response_mode not in {"answer", "explain", "debug"}:
        return jsonify({"error": "response_mode must be answer, explain, or debug."}), 400
    try:
        workspace = _get_workspace(workspace_id)
        result = chat_about_project(
            workspace,
            prompt=data.get("prompt"),
            active_file=data.get("active_file"),
            history=data.get("history", []),
            include_project_context=include_context,
            response_mode=response_mode,
        )
        return jsonify(result)
    except KeyError as exc:
        return jsonify({"error": str(exc)}), 404
    except ProjectAssistantError as exc:
        return jsonify({"error": str(exc)}), exc.status_code


@project_routes.route(
    "/<workspace_id>/assistant/propose-changes", methods=["POST"]
)
def propose_workspace_changes(workspace_id: str):
    """Generate, validate, and stage a project change proposal without applying it."""
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "A JSON request body is required."}), 400
    try:
        workspace = _get_workspace(workspace_id)
        result = generate_project_change_proposal(
            workspace,
            prompt=data.get("prompt"),
            active_file=data.get("active_file"),
            history=data.get("history", []),
        )
        return jsonify(result)
    except KeyError as exc:
        return jsonify({"error": str(exc)}), 404
    except ProjectAssistantError as exc:
        return jsonify({"error": str(exc)}), exc.status_code


@project_routes.route("/<workspace_id>/architecture", methods=["GET"])
def get_project_architecture(workspace_id: str):
    """Analyze and return project architecture, packages, and dependency graph."""
    try:
        ws = _get_workspace(workspace_id)
        analyzer = ProjectAnalyzer(ws)
        report = analyzer.generate_project_architecture_report()
        return jsonify(report)
    except KeyError as exc:
        return jsonify({"error": str(exc)}), 404
    except Exception as exc:
        logger.exception("Architecture analysis failed")
        return jsonify({"error": str(exc)}), 500


@project_routes.route("/<workspace_id>/intelligence", methods=["GET"])
def get_project_code_intelligence(workspace_id: str):
    """Run project-scale code intelligence: dead code, duplicates, and maintainability."""
    try:
        ws = _get_workspace(workspace_id)
        intel = ProjectCodeIntelligence(ws)
        all_files = intel.analyze_all_files()
        dead_code = intel.detect_dead_code()
        duplicates = intel.detect_cross_file_duplicates()
        metrics = intel.calculate_project_metrics()
        return jsonify({
            "quality": all_files,
            "dead_code": dead_code,
            "duplicates": duplicates,
            "metrics": metrics,
        })
    except KeyError as exc:
        return jsonify({"error": str(exc)}), 404
    except Exception as exc:
        logger.exception("Project intelligence analysis failed")
        return jsonify({"error": str(exc)}), 500


@project_routes.route("/<workspace_id>/documentation", methods=["POST"])
def generate_project_docs(workspace_id: str):
    """Generate ground-truth documentation (readme, architecture, or api)."""
    data = request.get_json(silent=True) or {}
    doc_type = data.get("type", "readme").lower()

    try:
        ws = _get_workspace(workspace_id)
        doc_gen = ProjectDocumentationGenerator(ws)
        if doc_type == "readme":
            content = doc_gen.generate_readme_draft()
        elif doc_type == "architecture":
            content = doc_gen.generate_architecture_documentation()
        elif doc_type == "api":
            content = doc_gen.generate_api_documentation()
        elif doc_type == "dependencies":
            content = doc_gen.generate_dependency_documentation()
        else:
            return jsonify({"error": f"Unknown documentation type '{doc_type}'. Permitted: readme, architecture, api, dependencies."}), 400

        return jsonify({
            "type": doc_type,
            "content": content,
            "format": "markdown",
        })
    except KeyError as exc:
        return jsonify({"error": str(exc)}), 404
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@project_routes.route("/<workspace_id>/tools/run", methods=["POST"])
def run_project_tools(workspace_id: str):
    """Run the requested tool or report why it cannot safely run."""
    data = request.get_json(silent=True) or {}
    tool_name = data.get("tool", "all").lower()

    try:
        ws = _get_workspace(workspace_id)
        runner = EngineeringToolsRunner(ws)
        if tool_name == "pytest":
            res = runner.run_pytest()
        elif tool_name == "ruff":
            res = runner.run_ruff()
        elif tool_name == "mypy":
            res = runner.run_mypy()
        elif tool_name == "bandit":
            res = runner.run_bandit()
        elif tool_name == "all":
            res = runner.run_all_available_tools()
        else:
            return jsonify({"error": f"Unknown tool '{tool_name}'. Permitted: pytest, ruff, mypy, bandit, all."}), 400

        return jsonify(res)
    except KeyError as exc:
        return jsonify({"error": str(exc)}), 404
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@project_routes.route("/<workspace_id>/health", methods=["GET"])
def get_project_health(workspace_id: str):
    """Generate consolidated 8-dimension project health report."""
    run_tests = request.args.get("run_tests", "false").lower() == "true"
    try:
        ws = _get_workspace(workspace_id)
        reporter = ProjectHealthReporter(ws)
        report = reporter.generate_health_report(run_tests=run_tests)
        return jsonify(report)
    except KeyError as exc:
        return jsonify({"error": str(exc)}), 404
    except Exception as exc:
        logger.exception("Health report generation failed")
        return jsonify({"error": str(exc)}), 500


@project_routes.route("/<workspace_id>/changes/propose", methods=["POST"])
def propose_project_changes(workspace_id: str):
    """Stage multi-file changes and compute diffs requiring approval."""
    data = request.get_json(silent=True) or {}
    changes = data.get("changes", {})
    author = data.get("author", "AI Assistant")
    reason = data.get("reason", "Project refactor")

    if not isinstance(changes, dict) or not changes:
        return jsonify({"error": "'changes' dictionary required."}), 400

    try:
        ws = _get_workspace(workspace_id)
        cm = ProjectChangeManager(ws)
        res = cm.propose_multi_file_changes(changes, author=author, reason=reason)
        return jsonify(res)
    except KeyError as exc:
        return jsonify({"error": str(exc)}), 404
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@project_routes.route(
    "/<workspace_id>/changes/propose-agentic-candidate", methods=["POST"]
)
def propose_agentic_project_candidate(workspace_id: str):
    """Stage a reviewed specialist candidate for project-level approval."""
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "A JSON request body is required."}), 400
    try:
        workspace = _get_workspace(workspace_id)
        result = stage_agentic_project_candidate(
            workspace,
            active_file=data.get("active_file"),
            candidate_code=data.get("candidate_code"),
        )
        return jsonify(result)
    except KeyError as exc:
        return jsonify({"error": str(exc)}), 404
    except ProjectAssistantError as exc:
        return jsonify({"error": str(exc)}), exc.status_code


@project_routes.route("/<workspace_id>/changes/approve", methods=["POST"])
def approve_project_changes(workspace_id: str):
    """Approve and apply staged changes to the workspace."""
    data = request.get_json(silent=True) or {}
    proposal_id = data.get("proposal_id", "").strip()
    if not proposal_id:
        return jsonify({"error": "'proposal_id' is required."}), 400

    try:
        ws = _get_workspace(workspace_id)
        cm = ProjectChangeManager(ws)
        res = cm.approve_and_commit_changes(proposal_id)
        return jsonify(res)
    except KeyError as exc:
        return jsonify({"error": str(exc)}), 404
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


@project_routes.route("/<workspace_id>/changes/reject", methods=["POST"])
def reject_project_changes(workspace_id: str):
    """Reject a pending proposal without changing workspace files."""
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "A JSON request body is required."}), 400
    proposal_id = data.get("proposal_id", "")
    if not isinstance(proposal_id, str):
        return jsonify({"error": "'proposal_id' must be a string."}), 400
    proposal_id = proposal_id.strip()
    if not proposal_id:
        return jsonify({"error": "'proposal_id' is required."}), 400
    try:
        ws = _get_workspace(workspace_id)
        cm = ProjectChangeManager(ws)
        return jsonify(cm.reject_proposal(proposal_id))
    except KeyError as exc:
        return jsonify({"error": str(exc)}), 404
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


@project_routes.route("/<workspace_id>/changes/rollback", methods=["POST"])
def rollback_project(workspace_id: str):
    """Revert project workspace to a specified snapshot."""
    data = request.get_json(silent=True) or {}
    snapshot_id = data.get("snapshot_id", "").strip()
    if not snapshot_id:
        return jsonify({"error": "'snapshot_id' is required."}), 400

    try:
        ws = _get_workspace(workspace_id)
        cm = ProjectChangeManager(ws)
        res = cm.rollback_to_snapshot(snapshot_id)
        return jsonify(res)
    except KeyError as exc:
        return jsonify({"error": str(exc)}), 404
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


@project_routes.route("/<workspace_id>/snapshots", methods=["GET"])
def list_project_snapshots(workspace_id: str):
    """List all available project snapshots."""
    try:
        ws = _get_workspace(workspace_id)
        cm = ProjectChangeManager(ws)
        return jsonify({"snapshots": cm.list_snapshots()})
    except KeyError as exc:
        return jsonify({"error": str(exc)}), 404


@project_routes.route("/<workspace_id>/export", methods=["GET"])
def export_project_zip(workspace_id: str):
    """Download the current project workspace as a ZIP archive."""
    try:
        ws = _get_workspace(workspace_id)
        zip_bytes = ws.export_as_zip()
        return send_file(
            io.BytesIO(zip_bytes),
            mimetype="application/zip",
            as_attachment=True,
            download_name=f"project_{workspace_id[:8]}.zip",
        )
    except KeyError as exc:
        return jsonify({"error": str(exc)}), 404


@project_routes.route("/<workspace_id>/report/download", methods=["GET"])
def download_project_report(workspace_id: str):
    """Download Markdown health report or architecture report."""
    report_type = request.args.get("type", "health").lower()
    try:
        ws = _get_workspace(workspace_id)
        if report_type == "architecture":
            doc_gen = ProjectDocumentationGenerator(ws)
            md_content = doc_gen.generate_architecture_documentation()
            filename = f"architecture_report_{workspace_id[:8]}.md"
        else:
            reporter = ProjectHealthReporter(ws)
            md_content = reporter.generate_markdown_report()
            filename = f"health_report_{workspace_id[:8]}.md"

        return send_file(
            io.BytesIO(md_content.encode("utf-8")),
            mimetype="text/markdown",
            as_attachment=True,
            download_name=filename,
        )
    except KeyError as exc:
        return jsonify({"error": str(exc)}), 404
