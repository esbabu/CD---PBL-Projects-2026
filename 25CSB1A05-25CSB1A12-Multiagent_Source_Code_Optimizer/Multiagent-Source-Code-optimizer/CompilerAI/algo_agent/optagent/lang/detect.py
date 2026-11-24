"""Language detection from file extension, explicit request, or source heuristics."""
from __future__ import annotations

from pathlib import Path

EXT_MAP: dict[str, str] = {
    ".py": "python",
    ".pyw": "python",
    ".js": "javascript",
    ".mjs": "javascript",
    ".cjs": "javascript",
    ".c": "c",
    ".cc": "cpp",
    ".cpp": "cpp",
    ".cxx": "cpp",
    ".hpp": "cpp",
    ".hh": "cpp",
    ".hxx": "cpp",
}

ALIASES: dict[str, str] = {
    "py": "python",
    "python": "python",
    "python3": "python",
    "js": "javascript",
    "javascript": "javascript",
    "node": "javascript",
    "c": "c",
    "c11": "c",
    "c++": "cpp",
    "cpp": "cpp",
    "cxx": "cpp",
    "cc": "cpp",
}


def normalize_language(name: str) -> str:
    key = name.strip().lower()
    if key in ALIASES:
        return ALIASES[key]
    raise ValueError(f"Unsupported language '{name}'. Supported: python, javascript, c, cpp.")


def detect_language(
    path: str | Path | None = None,
    source: str | None = None,
    requested: str | None = None,
) -> str:
    """Detect language ID. Explicit `requested` always wins.

    Extension rules:
    - `.py` -> python
    - `.js`, `.mjs`, `.cjs` -> javascript
    - `.c` -> c
    - `.cc`, `.cpp`, `.cxx`, `.hpp` -> cpp
    - `.h` -> ambiguous; requires explicit `requested` language (raises ValueError otherwise).
    """
    if requested:
        return normalize_language(requested)

    if path is not None:
        ext = Path(str(path)).suffix.lower()
        if ext == ".h":
            raise ValueError(
                f"Header file '{path}' (.h) is ambiguous between C and C++. "
                "Please pass --lang c or --lang cpp explicitly."
            )
        if ext in EXT_MAP:
            return EXT_MAP[ext]

    if source:
        s = source.lstrip()
        # Simple fallback heuristics when no path or extension is provided
        if any(tok in s for tok in ("#include <vector>", "#include <string>", "#include <unordered_map>",
                                     "std::", "namespace ", "template<", "template <")):
            return "cpp"
        if "#include " in s and ("int " in s or "void " in s or "double " in s or "char*" in s or "char *" in s):
            return "c"
        if any(tok in s for tok in ("function ", "const ", "let ", "module.exports", "export function", "=> {")):
            if "def " not in s:
                return "javascript"

    return "python"
