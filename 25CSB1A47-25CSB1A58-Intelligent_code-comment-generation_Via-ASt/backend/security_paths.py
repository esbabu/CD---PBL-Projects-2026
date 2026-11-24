"""Safe path resolution and workspace sandbox enforcement for AST Studio.

Prevents path traversal, symlink escapes, and unauthorized access to
sensitive configuration files (.env, .git, .venv, system files).
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional, Set

# File and directory basenames strictly forbidden from agent reading/writing
FORBIDDEN_BASENAMES: Set[str] = {
    ".env",
    ".env.local",
    ".env.production",
    ".env.staging",
    ".env.test",
    ".git",
    ".gitignore",
    ".venv",
    "venv",
    "id_rsa",
    "id_ed25519",
}

# System directories that must never be accessed
SYSTEM_PATHS_PREFIXES = (
    "/etc",
    "/proc",
    "/sys",
    "/root",
    "c:\\windows",
    "c:\\program files",
)


class PathTraversalError(PermissionError):
    """Raised when a path attempts to escape the designated workspace boundary."""


class SensitiveFileAccessError(PermissionError):
    """Raised when an operation attempts to access a protected or sensitive file."""


def safe_resolve_workspace_path(
    target_path: str | Path,
    base_dir: Optional[str | Path] = None,
) -> Path:
    """Resolve and validate that target_path resides strictly within the workspace sandbox.

    Blocks path traversal (../), absolute root escapes, and access to forbidden files.
    """
    if not target_path:
        raise ValueError("Target path must not be empty.")

    root = Path(base_dir or os.getcwd()).resolve()
    candidate = Path(target_path)

    # If relative, resolve relative to root
    if not candidate.is_absolute():
        resolved = (root / candidate).resolve()
    else:
        resolved = candidate.resolve()

    # Verify containment within base directory
    try:
        resolved.relative_to(root)
    except ValueError:
        raise PathTraversalError(
            f"Access denied: path '{target_path}' escapes the workspace boundary '{root}'."
        )

    # Check for forbidden basenames
    for part in resolved.parts:
        if part.lower() in FORBIDDEN_BASENAMES:
            raise SensitiveFileAccessError(
                f"Access denied: access to sensitive entity '{part}' is prohibited."
            )

    # Check against system directories
    resolved_str = str(resolved).lower()
    for prefix in SYSTEM_PATHS_PREFIXES:
        if resolved_str.startswith(prefix):
            raise SensitiveFileAccessError(
                f"Access denied: access to system location '{resolved}' is prohibited."
            )

    return resolved
