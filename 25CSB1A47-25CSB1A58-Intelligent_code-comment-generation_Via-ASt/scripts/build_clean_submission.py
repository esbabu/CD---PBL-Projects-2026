import subprocess
import zipfile
from pathlib import Path
from typing import List, Set

FORBIDDEN_DIR_PARTS: Set[str] = {
    ".venv",
    ".pytest_cache",
    ".ruff_cache",
    "instance",
    "backups",
    "dist",
    "__pycache__",
    ".coverage",
}

FORBIDDEN_EXACT_NAMES: Set[str] = {
    ".env",
    ".gitignore",
    "README.md",
    "LICENSE",
    "requirements.txt",
}

FORBIDDEN_EXTENSIONS: Set[str] = {".db", ".pyc", ".sqlite", ".log"}


def get_git_tracked_files(root: Path) -> List[str]:
    try:
        result = subprocess.run(
            ["git", "ls-files"],
            cwd=str(root),
            capture_output=True,
            text=True,
            check=True,
        )
        return [path.strip() for path in result.stdout.splitlines() if path.strip()]
    except Exception:
        return []


def is_forbidden(path: str) -> bool:
    p = Path(path)
    for part in p.parts[:-1]:
        if part in FORBIDDEN_DIR_PARTS:
            return True
        if part.startswith(".venv"):
            return True
    if p.suffix.lower() in FORBIDDEN_EXTENSIONS:
        return True
    if p.name.startswith(".env") and p.name != ".env.example":
        return True
    return False


def build_clean_submission(output_zip: Path) -> Path:
    project_root = Path(__file__).resolve().parent.parent
    tracked = set(get_git_tracked_files(project_root))
    tracked_normalised = {p.replace("\\", "/") for p in tracked}

    output_zip.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(output_zip, "w", compression=zipfile.ZIP_DEFLATED) as zipf:
        for rel_path in tracked_normalised:
            if is_forbidden(rel_path):
                continue
            name = Path(rel_path).name
            if name in FORBIDDEN_EXACT_NAMES and name != ".env.example":
                continue
            file_path = project_root / rel_path
            if file_path.is_file():
                zipf.write(file_path, arcname=rel_path)
    return output_zip


__all__ = [
    "FORBIDDEN_DIR_PARTS",
    "FORBIDDEN_EXACT_NAMES",
    "FORBIDDEN_EXTENSIONS",
    "build_clean_submission",
    "get_git_tracked_files",
    "is_forbidden",
]
