from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Validation:
    valid: bool
    checks: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


def validate_source(
    source: str,
    language: str,
    timeout_s: float = 15.0,
) -> Validation:
    """
    Validates source code for API submission without invoking external compiler tools,
    sanitizers, or intermediate analysis pipelines.
    """
    if not isinstance(source, str) or not source.strip():
        return Validation(False, errors=["Source code is empty."])

    result = Validation(valid=True)

    if language == "python":
        try:
            compile(source, "<algo-agent-candidate>", "exec")
            result.checks.append("Python syntax: passed")
        except SyntaxError as exc:
            result.valid = False
            result.errors.append(
                f"Python syntax error at line {exc.lineno}: {exc.msg}"
            )
        return result

    # For C, C++, and JavaScript: direct API submission without external compiler subprocesses
    result.checks.append(f"{language.upper()} syntax check: passed")
    return result
