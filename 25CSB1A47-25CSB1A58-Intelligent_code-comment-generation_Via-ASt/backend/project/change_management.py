"""Reversible Project Change Management, Multi-File Diffs, and Rollback Engine.

Manages all code modifications with complete reversibility:
- Point-in-time workspace snapshots
- Multi-file before-and-after unified diffs
- Staging of candidate changes requiring human approval
- Rollback to any prior snapshot
- Change history auditing
- ZIP export and downloadable reports
"""

from __future__ import annotations

import difflib
import hashlib
import json
import os
import shutil
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List

from backend.patch_safety import validate_patch_structural_safety
from backend.project.workspace import ProjectWorkspace


class ProjectChangeManager:
    """Provides snapshot versioning, reversible rollbacks, staging, and approval."""

    def __init__(self, workspace: ProjectWorkspace) -> None:
        self.workspace = workspace
        self.manifest_path = self.workspace.base_dir / "change_manifest.json"
        self._init_manifest()

    def _init_manifest(self) -> None:
        if not self.manifest_path.exists():
            self._save_manifest({
                "snapshots": [],
                "pending_proposals": {},
                "history": [],
            })

    def _load_manifest(self) -> Dict[str, Any]:
        try:
            return json.loads(self.manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {"snapshots": [], "pending_proposals": {}, "history": []}

    def _save_manifest(self, data: Dict[str, Any]) -> None:
        self.manifest_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def _compute_dir_hash(self, directory: Path) -> str:
        hasher = hashlib.sha256()
        for root, dirs, files in os.walk(directory):
            for f in sorted(files):
                file_p = Path(root) / f
                hasher.update(file_p.relative_to(directory).as_posix().encode())
                try:
                    hasher.update(file_p.read_bytes())
                except OSError:
                    pass
        return hasher.hexdigest()

    def create_snapshot(self, label: str, description: str = "") -> str:
        """Create a point-in-time snapshot of the current workspace project tree."""
        snapshot_id = f"snap_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        snap_dir = self.workspace.snapshots_dir / snapshot_id
        snap_dir.mkdir(parents=True, exist_ok=True)

        # Copy current project directory into snapshot directory
        for root, dirs, files in os.walk(self.workspace.project_dir):
            rel_dir = Path(root).relative_to(self.workspace.project_dir)
            target_sub = snap_dir / rel_dir
            target_sub.mkdir(parents=True, exist_ok=True)
            for f in files:
                src_file = Path(root) / f
                dst_file = target_sub / f
                shutil.copy2(src_file, dst_file)

        manifest = self._load_manifest()
        record = {
            "snapshot_id": snapshot_id,
            "label": label,
            "description": description,
            "timestamp": time.time(),
            "formatted_time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "digest": self._compute_dir_hash(snap_dir),
            "files_count": len(self.workspace.list_files()),
        }
        manifest["snapshots"].append(record)
        manifest["history"].append({
            "action": "snapshot_created",
            "snapshot_id": snapshot_id,
            "label": label,
            "timestamp": time.time(),
        })
        self._save_manifest(manifest)
        return snapshot_id

    def list_snapshots(self) -> List[Dict[str, Any]]:
        """List all available project snapshots."""
        return self._load_manifest().get("snapshots", [])

    def compute_file_diff(self, old_content: str, new_content: str, file_path: str = "file.py") -> Dict[str, Any]:
        """Compute unified diff between old and new file content."""
        old_lines = old_content.splitlines(keepends=True)
        new_lines = new_content.splitlines(keepends=True)
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile=f"a/{file_path}",
            tofile=f"b/{file_path}",
            n=3,
        ))
        diff_text = "".join(diff)
        added = sum(1 for line in diff if line.startswith("+") and not line.startswith("+++"))
        removed = sum(1 for line in diff if line.startswith("-") and not line.startswith("---"))
        return {
            "has_changes": bool(diff_text.strip()),
            "diff": diff_text,
            "added_lines": added,
            "removed_lines": removed,
        }

    def propose_multi_file_changes(
        self,
        changes: Dict[str, str],
        author: str = "AI Assistant",
        reason: str = "Automated optimization/remediation",
    ) -> Dict[str, Any]:
        """Stage proposed multi-file changes and compute diffs without applying them yet."""
        proposal_id = f"prop_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        file_diffs: Dict[str, Dict[str, Any]] = {}
        safety_checks: Dict[str, Dict[str, Any]] = {}
        total_added = 0
        total_removed = 0
        all_safe = True

        for rel_path, new_content in changes.items():
            try:
                old_content = self.workspace.read_file(rel_path)
            except FileNotFoundError:
                old_content = ""

            diff_data = self.compute_file_diff(old_content, new_content, file_path=rel_path)
            file_diffs[rel_path] = diff_data
            total_added += diff_data["added_lines"]
            total_removed += diff_data["removed_lines"]

            # Run AST structural safety check if file is python
            if rel_path.endswith(".py") and old_content:
                s_check = validate_patch_structural_safety(old_content, new_content)
                safety_checks[rel_path] = s_check
                if not s_check["is_safe"]:
                    all_safe = False

        manifest = self._load_manifest()
        manifest["pending_proposals"][proposal_id] = {
            "proposal_id": proposal_id,
            "author": author,
            "reason": reason,
            "timestamp": time.time(),
            "changes": changes,
            "all_safe": all_safe,
            "status": "pending_approval",
        }
        self._save_manifest(manifest)

        return {
            "proposal_id": proposal_id,
            "status": "pending_approval",
            "requires_approval": True,
            "all_safety_checks_passed": all_safe,
            "total_files_changed": len(changes),
            "total_added_lines": total_added,
            "total_removed_lines": total_removed,
            "diffs_by_file": file_diffs,
            "safety_checks_by_file": safety_checks,
        }

    def approve_and_commit_changes(self, proposal_id: str) -> Dict[str, Any]:
        """Approve and apply staged changes to the workspace, creating a recovery snapshot first."""
        manifest = self._load_manifest()
        proposal = manifest.get("pending_proposals", {}).get(proposal_id)
        if not proposal or proposal.get("status") != "pending_approval":
            raise ValueError(f"Proposal '{proposal_id}' does not exist or was already processed.")

        # Create pre-apply rollback checkpoint snapshot
        pre_snap_id = self.create_snapshot(
            label=f"Pre-apply checkpoint for proposal {proposal_id}",
            description=f"Auto-generated before applying proposal by {proposal.get('author')}",
        )

        manifest = self._load_manifest()
        proposal = manifest.get("pending_proposals", {}).get(proposal_id)
        if not proposal or proposal.get("status") != "pending_approval":
            raise ValueError(f"Proposal '{proposal_id}' does not exist or was already processed.")
        changes = proposal["changes"]
        for rel_path, new_content in changes.items():
            self.workspace.write_file(rel_path, new_content)

        proposal["status"] = "committed"
        proposal["committed_at"] = time.time()
        proposal["rollback_snapshot_id"] = pre_snap_id

        manifest["history"].append({
            "action": "proposal_committed",
            "proposal_id": proposal_id,
            "files_modified": list(changes.keys()),
            "pre_snapshot_id": pre_snap_id,
            "timestamp": time.time(),
        })
        self._save_manifest(manifest)

        return {
            "status": "committed",
            "proposal_id": proposal_id,
            "files_committed": list(changes.keys()),
            "rollback_snapshot_id": pre_snap_id,
        }

    def reject_proposal(self, proposal_id: str) -> Dict[str, Any]:
        """Mark a pending proposal rejected so it can no longer be approved."""
        manifest = self._load_manifest()
        proposal = manifest.get("pending_proposals", {}).get(proposal_id)
        if not proposal or proposal.get("status") != "pending_approval":
            raise ValueError(f"Proposal '{proposal_id}' does not exist or was already processed.")

        proposal["status"] = "rejected"
        proposal["rejected_at"] = time.time()
        manifest["history"].append({
            "action": "proposal_rejected",
            "proposal_id": proposal_id,
            "timestamp": time.time(),
        })
        self._save_manifest(manifest)
        return {"status": "rejected", "proposal_id": proposal_id}

    def rollback_to_snapshot(self, snapshot_id: str) -> Dict[str, Any]:
        """Revert the entire workspace project directory to the state captured in snapshot_id."""
        snap_dir = self.workspace.snapshots_dir / snapshot_id
        if not snap_dir.exists() or not snap_dir.is_dir():
            raise ValueError(f"Snapshot '{snapshot_id}' does not exist.")

        # Wipe current project directory and restore snapshot
        shutil.rmtree(self.workspace.project_dir)
        self.workspace.project_dir.mkdir(parents=True, exist_ok=True)

        for root, dirs, files in os.walk(snap_dir):
            rel_dir = Path(root).relative_to(snap_dir)
            target_sub = self.workspace.project_dir / rel_dir
            target_sub.mkdir(parents=True, exist_ok=True)
            for f in files:
                src_file = Path(root) / f
                dst_file = target_sub / f
                shutil.copy2(src_file, dst_file)

        manifest = self._load_manifest()
        manifest["history"].append({
            "action": "rolled_back_to_snapshot",
            "snapshot_id": snapshot_id,
            "timestamp": time.time(),
        })
        self._save_manifest(manifest)

        return {
            "status": "rolled_back",
            "restored_snapshot_id": snapshot_id,
            "files_count": len(self.workspace.list_files()),
        }
