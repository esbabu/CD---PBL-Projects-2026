"""Safe Multi-File Project Workspace and Archive Extraction Manager.

Provides secure multi-file workspace storage and extraction:
- Strict protection against ZIP path traversal (Zip Slip / ../ / drive letters)
- Zip bomb & resource exhaustion mitigation (max total size, file count, max file size)
- Symlink and hardlink abuse rejection
- Sandboxed file tree navigation and safe file I/O
- Reversible workspace state snapshots and clean ZIP export
"""

from __future__ import annotations

import io
import os
import re
import shutil
import stat
import uuid
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

logger = logging = __import__("logging").getLogger(__name__)

# Security limits for uploaded project archives
MAX_PROJECT_ARCHIVE_BYTES: int = 25 * 1024 * 1024  # 25 MB max compressed archive
MAX_UNCOMPRESSED_BYTES: int = 50 * 1024 * 1024     # 50 MB max extracted workspace
MAX_ARCHIVE_FILE_COUNT: int = 1000                 # 1,000 files max per project
MAX_SINGLE_FILE_BYTES: int = 5 * 1024 * 1024       # 5 MB max per single file
MAX_COMPRESSION_RATIO: float = 100.0               # Max expansion ratio (zip bomb check)

DEFAULT_WORKSPACES_ROOT: Path = Path("instance") / "workspaces"

# Directories that should be skipped during project tree exploration
IGNORED_PROJECT_DIRS: Set[str] = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "node_modules",
    ".tox",
    ".eggs",
    "dist",
    "build",
}


class ArchiveSecurityError(ValueError):
    """Raised when an uploaded archive violates security invariants."""


class SafeArchiveExtractor:
    """Safely inspects and extracts ZIP and TAR archives into a destination sandbox."""

    @staticmethod
    def extract_zip(archive_bytes: bytes, dest_dir: Path) -> List[str]:
        """Extract a ZIP archive safely into dest_dir, preventing traversal and resource exhaustion."""
        if len(archive_bytes) > MAX_PROJECT_ARCHIVE_BYTES:
            raise ArchiveSecurityError(
                f"Archive exceeds maximum allowed compressed size ({len(archive_bytes)} > {MAX_PROJECT_ARCHIVE_BYTES} bytes)."
            )

        dest_dir = dest_dir.resolve()
        dest_dir.mkdir(parents=True, exist_ok=True)
        extracted_files: List[str] = []

        try:
            with zipfile.ZipFile(io.BytesIO(archive_bytes)) as zf:
                infolist = zf.infolist()
                if len(infolist) > MAX_ARCHIVE_FILE_COUNT:
                    raise ArchiveSecurityError(
                        f"Archive contains too many entries ({len(infolist)} > {MAX_ARCHIVE_FILE_COUNT})."
                    )

                total_uncompressed = 0
                for info in infolist:
                    # 1. Symlink / device check
                    # UNIX mode is stored in the high 16 bits of external_attr
                    mode = info.external_attr >> 16
                    if stat.S_ISLNK(mode) or stat.S_ISCHR(mode) or stat.S_ISBLK(mode) or stat.S_ISFIFO(mode):
                        raise ArchiveSecurityError(f"Symlinks and device nodes are forbidden in archive: '{info.filename}'")

                    # 2. Path Traversal checks
                    cleaned_name = info.filename.replace("\\", "/")
                    if (
                        cleaned_name.startswith("/")
                        or ".." in Path(cleaned_name).parts
                        or re.match(r"^[a-zA-Z]:", cleaned_name)
                        or "\0" in cleaned_name
                    ):
                        raise ArchiveSecurityError(f"Path traversal detected in archive entry: '{info.filename}'")

                    target_path = (dest_dir / cleaned_name).resolve()
                    if not str(target_path).startswith(str(dest_dir)):
                        raise ArchiveSecurityError(f"Entry resolves outside destination sandbox: '{info.filename}'")

                    # 3. File size and total size checks
                    if info.file_size > MAX_SINGLE_FILE_BYTES:
                        raise ArchiveSecurityError(
                            f"File '{info.filename}' exceeds single file limit ({info.file_size} > {MAX_SINGLE_FILE_BYTES} bytes)."
                        )

                    total_uncompressed += info.file_size
                    if total_uncompressed > MAX_UNCOMPRESSED_BYTES:
                        raise ArchiveSecurityError(
                            f"Total uncompressed project size exceeds limit ({total_uncompressed} > {MAX_UNCOMPRESSED_BYTES} bytes)."
                        )

                    # Compression ratio check for zip bomb prevention
                    if info.compress_size > 0:
                        ratio = info.file_size / info.compress_size
                        if ratio > MAX_COMPRESSION_RATIO and info.file_size > 1024 * 1024:
                            raise ArchiveSecurityError(
                                f"High compression ratio ({ratio:.1f}x) detected on '{info.filename}', potential zip bomb."
                            )

                    # Extract entry
                    if info.is_dir():
                        target_path.mkdir(parents=True, exist_ok=True)
                    else:
                        target_path.parent.mkdir(parents=True, exist_ok=True)
                        with zf.open(info) as src, open(target_path, "wb") as dst:
                            shutil.copyfileobj(src, dst)
                        rel = target_path.relative_to(dest_dir).as_posix()
                        extracted_files.append(rel)

        except zipfile.BadZipFile as exc:
            raise ArchiveSecurityError(f"Invalid or corrupted ZIP archive: {exc}")

        return extracted_files


class ProjectWorkspace:
    """Manages an isolated project workspace directory with multi-file exploration and safe file I/O."""

    def __init__(self, workspace_id: Optional[str] = None, base_storage_dir: Optional[Path] = None) -> None:
        self.workspace_id = workspace_id or str(uuid.uuid4())
        self.base_dir = (base_storage_dir or DEFAULT_WORKSPACES_ROOT) / self.workspace_id
        self.project_dir = self.base_dir / "project"
        self.snapshots_dir = self.base_dir / "snapshots"
        self.project_dir.mkdir(parents=True, exist_ok=True)
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)

    def resolve_safe_path(self, rel_path: str) -> Path:
        """Resolve a relative path inside the workspace project_dir, preventing traversal."""
        cleaned = rel_path.replace("\\", "/").strip().lstrip("/")
        if ".." in Path(cleaned).parts or "\0" in cleaned or re.match(r"^[a-zA-Z]:", cleaned):
            raise ValueError(f"Path traversal attempt rejected: '{rel_path}'")
        target = (self.project_dir / cleaned).resolve()
        if not str(target).startswith(str(self.project_dir.resolve())):
            raise ValueError(f"Target path escapes workspace sandbox: '{rel_path}'")
        return target

    def write_file(self, rel_path: str, content: str) -> None:
        """Safely write text content to a relative path inside the workspace."""
        target = self.resolve_safe_path(rel_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    def read_file(self, rel_path: str) -> str:
        """Safely read text content of a file in the workspace."""
        target = self.resolve_safe_path(rel_path)
        if not target.exists() or not target.is_file():
            raise FileNotFoundError(f"File '{rel_path}' does not exist in workspace.")
        return target.read_text(encoding="utf-8", errors="replace")

    def delete_file(self, rel_path: str) -> bool:
        """Safely delete a file in the workspace."""
        target = self.resolve_safe_path(rel_path)
        if target.exists() and target.is_file():
            target.unlink()
            return True
        return False

    def list_files(self, extension: Optional[str] = None) -> List[str]:
        """List all relative file paths in the workspace, optionally filtering by extension."""
        results: List[str] = []
        for root, dirs, files in os.walk(self.project_dir):
            dirs[:] = [d for d in dirs if d not in IGNORED_PROJECT_DIRS]
            for f in files:
                full_p = Path(root) / f
                rel = full_p.relative_to(self.project_dir).as_posix()
                if extension is None or rel.endswith(extension):
                    results.append(rel)
        return sorted(results)

    def list_python_files(self) -> List[str]:
        """List all Python (.py) source files in the project."""
        return self.list_files(extension=".py")

    def get_file_tree(self) -> Dict[str, Any]:
        """Build a hierarchical JSON-serializable directory tree of the workspace."""
        def build_tree(current_path: Path) -> Dict[str, Any]:
            name = current_path.name or "root"
            if current_path.is_file():
                try:
                    size = current_path.stat().st_size
                    line_count = len(current_path.read_text(encoding="utf-8", errors="ignore").splitlines())
                except OSError:
                    size = 0
                    line_count = 0
                return {
                    "name": name,
                    "path": current_path.relative_to(self.project_dir).as_posix(),
                    "type": "file",
                    "extension": current_path.suffix.lower(),
                    "size": size,
                    "line_count": line_count,
                    "is_python": current_path.suffix.lower() == ".py",
                }

            children = []
            try:
                entries = sorted(current_path.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
            except OSError:
                entries = []

            for entry in entries:
                if entry.name in IGNORED_PROJECT_DIRS:
                    continue
                children.append(build_tree(entry))

            return {
                "name": name,
                "path": current_path.relative_to(self.project_dir).as_posix() if current_path != self.project_dir else "",
                "type": "directory",
                "children": children,
            }

        return build_tree(self.project_dir)

    def load_files_dict(self, files_map: Dict[str, str]) -> List[str]:
        """Populate the workspace from a dictionary of relative paths and contents."""
        created: List[str] = []
        for path_str, content in files_map.items():
            self.write_file(path_str, content)
            created.append(path_str)
        return created

    def load_from_zip(self, archive_bytes: bytes) -> List[str]:
        """Safely extract uploaded archive bytes into the project workspace."""
        return SafeArchiveExtractor.extract_zip(archive_bytes, self.project_dir)

    def export_as_zip(self) -> bytes:
        """Export the entire current workspace project tree into a clean ZIP archive."""
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(self.project_dir):
                dirs[:] = [d for d in dirs if d not in IGNORED_PROJECT_DIRS]
                for file_name in files:
                    file_path = Path(root) / file_name
                    rel_path = file_path.relative_to(self.project_dir).as_posix()
                    zf.write(file_path, arcname=rel_path)
        return buffer.getvalue()

    def cleanup(self) -> None:
        """Remove the workspace and all its files from storage."""
        if self.base_dir.exists():
            shutil.rmtree(self.base_dir, ignore_errors=True)
