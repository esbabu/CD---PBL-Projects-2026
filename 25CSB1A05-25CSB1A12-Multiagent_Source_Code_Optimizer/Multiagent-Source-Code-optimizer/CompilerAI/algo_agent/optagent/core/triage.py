"""Triage stage: first stage in the pipeline, deciding strategy and typed reasons."""
from __future__ import annotations

import ast
import hashlib
import importlib.util
import shutil
import sys
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from ..config import Settings
from ..lang.detect import detect_language, normalize_language
from ..lang.registry import get_adapter, list_adapters
from .outcome import Reason, ReasonCode, SupportLevel
from .provenance import ComponentKind, component


class ExecutionStrategy(str, Enum):
    FUNCTION = "function"
    METHOD = "method"
    SCRIPT = "script"
    ANALYSIS_ONLY = "analysis_only"
    REFUSED = "refused"


class TriageResult(BaseModel):
    language: str = "python"
    strategy: ExecutionStrategy = ExecutionStrategy.FUNCTION
    support_level: SupportLevel = SupportLevel.FULL
    entry_point: str | None = None
    entry_candidates: list[str] = Field(default_factory=list)
    entry_ranking: list[dict[str, Any]] = Field(default_factory=list)
    reasons: list[Reason] = Field(default_factory=list)
    missing_dependencies: list[str] = Field(default_factory=list)
    has_import_side_effects: bool = False
    detected_class: str | None = None
    method_kind: str | None = None  # instance | static | classmethod | None
    source_sha: str = ""
    toolchain_ok: bool = True


MAX_SOURCE_BYTES = 512 * 1024  # 512 KB sanity cap


def _find_node_exe() -> str | None:
    exe = shutil.which("node")
    if exe:
        return exe
    cand = Path.home() / ".nodejs" / "node-v20.18.0-win-x64" / "node.exe"
    return str(cand) if cand.exists() else None


def _check_toolchain(lang: str, settings: Settings) -> tuple[bool, str]:
    """Return (available, diagnostic_message) for executing `lang`."""
    if lang == "python":
        return True, ""
    if lang == "javascript":
        if settings.sandbox_backend == "docker" and shutil.which("docker"):
            return True, ""
        if _find_node_exe():
            return True, ""
        if shutil.which("docker"):
            return True, ""
        return False, "Neither Node.js nor Docker (docker/sandbox-js.Dockerfile) is available on this host."
    if lang in ("c", "cpp"):
        compilers = ("clang", "gcc") if lang == "c" else ("clang++", "g++")
        has_docker = bool(shutil.which("docker"))
        if has_docker and settings.sandbox_backend != "local":
            return True, ""
        found = next((c for c in compilers if shutil.which(c)), None)
        if found:
            if not settings.allow_local_native and not has_docker:
                return False, f"Found {found} locally, but OPT_ALLOW_LOCAL_NATIVE=1 is not set and Docker is unavailable."
            return True, ""
        return (
            False,
            f"Native compiler ({'/'.join(compilers)}) and Docker (docker/sandbox-native.Dockerfile) are unavailable on this host.",
        )
    return False, f"Unsupported language '{lang}'."


def _scan_python_imports(tree: ast.Module) -> list[str]:
    """Return top-level module names imported by the Python AST that are unavailable in this runtime."""
    stdlib = getattr(sys, "stdlib_module_names", set())
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0 and node.module:
                imported.add(node.module.split(".")[0])
    missing: list[str] = []
    for mod in sorted(imported):
        if mod in stdlib or mod in ("__future__", "builtins"):
            continue
        if importlib.util.find_spec(mod) is None:
            missing.append(mod)
    return missing


@component(kind=ComponentKind.HEURISTIC, name="triage.run_triage", description="Deterministic syntax, dependency, entry, and toolchain triage.")
def run_triage(
    source: str,
    language: str | None = None,
    source_name: str = "input.py",
    entry: str | None = None,
    overrides: dict[str, Any] | None = None,
    settings: Settings | None = None,
) -> TriageResult:
    s = settings or Settings()
    overrides = overrides or {}
    reasons: list[Reason] = []

    # 1. Empty / size limit checks -> REFUSED
    if not source or not source.strip():
        return TriageResult(
            language=normalize_language(language or "python"),
            strategy=ExecutionStrategy.REFUSED,
            support_level=SupportLevel.REFUSED,
            reasons=[Reason(code=ReasonCode.SYNTAX_ERROR, message="Source code is empty.", stage="triage")],
        )
    if len(source.encode("utf-8")) > getattr(s, "max_source_bytes", MAX_SOURCE_BYTES):
        return TriageResult(
            language=normalize_language(language or "python"),
            strategy=ExecutionStrategy.REFUSED,
            support_level=SupportLevel.REFUSED,
            reasons=[Reason(code=ReasonCode.INPUT_TOO_LARGE, message=f"Source exceeds size limit ({len(source)} chars).", stage="triage")],
        )

    # 2. Language resolution: explicit request language always wins over heuristics
    req_lang = language or overrides.get("language")
    if req_lang:
        lang_id = normalize_language(req_lang)
    else:
        fname = source_name if source_name and source_name != "input.py" else None
        lang_id = detect_language(fname, source, None)

    available_langs = list_adapters()
    if lang_id not in available_langs:
        return TriageResult(
            language=lang_id,
            strategy=ExecutionStrategy.REFUSED,
            support_level=SupportLevel.REFUSED,
            reasons=[
                Reason(
                    code=ReasonCode.LANGUAGE_UNSUPPORTED,
                    message=f"Language '{lang_id}' is not supported. Registered adapters: {available_langs}.",
                    stage="triage",
                )
            ],
        )

    sha = (
        hashlib.sha256(source.encode("utf-8")).hexdigest()[:12]
        if lang_id == "python"
        else hashlib.sha256(f"{lang_id}\0{source}".encode("utf-8")).hexdigest()[:12]
    )

    adapter = get_adapter(lang_id)
    hints = dict(overrides.get("hints") or {})

    # 3. Language-appropriate syntax check & fact extraction
    try:
        mod = adapter.analyze(source, hints)
    except SyntaxError as e:
        return TriageResult(
            language=lang_id,
            strategy=ExecutionStrategy.REFUSED,
            support_level=SupportLevel.REFUSED,
            source_sha=sha,
            reasons=[Reason(code=ReasonCode.SYNTAX_ERROR, message=f"Syntax error ({lang_id}): {e}", stage="triage")],
        )
    except Exception as e:
        return TriageResult(
            language=lang_id,
            strategy=ExecutionStrategy.REFUSED,
            support_level=SupportLevel.REFUSED,
            source_sha=sha,
            reasons=[Reason(code=ReasonCode.SYNTAX_ERROR, message=f"Failed to parse {lang_id} source: {e}", stage="triage")],
        )

    # 4. Python-specific import & side-effect checks
    missing_deps: list[str] = []
    has_side_effects = bool(mod.module_side_effects)
    if lang_id == "python":
        tree = ast.parse(source)
        missing_deps = _scan_python_imports(tree)
        if missing_deps:
            reasons.append(
                Reason(
                    code=ReasonCode.MISSING_DEPENDENCY,
                    message=f"Missing third-party Python package(s) in current runtime: {', '.join(missing_deps)}.",
                    remediation=f"Install {', '.join(missing_deps)} or configure an image containing them via OPT_PY_IMAGES.",
                    stage="triage",
                    detail={"missing": missing_deps},
                )
            )
        if has_side_effects:
            reasons.append(
                Reason(
                    code=ReasonCode.IMPORT_SIDE_EFFECT,
                    message=f"Top-level statements execute at import time ({len(mod.module_side_effects)} statement(s)).",
                    stage="triage",
                    detail={"statements": mod.module_side_effects[:5]},
                )
            )

    # 5. Entry detection & strategy selection
    req_entry = entry or overrides.get("entry_point")
    strategy = ExecutionStrategy.FUNCTION
    selected_entry: str | None = None
    candidates = list(mod.functions.keys())
    ranking: list[dict[str, Any]] = []
    detected_class: str | None = None
    method_kind: str | None = None

    if lang_id == "python":
        from ..analysis.static_facts import rank_entries

        if req_entry and req_entry in mod.functions:
            selected_entry = req_entry
        elif mod.functions:
            ranked = rank_entries(mod, source)
            ranking = ranked
            selected_entry = ranked[0]["name"]
            if len(mod.root_functions) > 1 or (len(mod.functions) > 1 and not req_entry):
                if len(ranked) > 1 and ranked[0]["name"] != req_entry:
                    reasons.append(
                        Reason(
                            code=ReasonCode.ENTRY_AUTO_SELECTED,
                            message=f"Auto-selected entry '{selected_entry}' from candidates {[r['name'] for r in ranked[:5]]}.",
                            stage="triage",
                            detail={"ranking": ranked[:5]},
                        )
                    )
        else:
            # No functions or methods: check if runnable stdin/stdout script
            strategy = ExecutionStrategy.SCRIPT
            selected_entry = "__script__"

        if selected_entry and "." in selected_entry and selected_entry in mod.functions:
            strategy = ExecutionStrategy.METHOD
            fn = mod.functions[selected_entry]
            detected_class = fn.extra.get("class_name") or selected_entry.split(".")[0]
            method_kind = fn.extra.get("method_kind", "instance")
    else:
        # JS / C / C++
        if req_entry and req_entry in mod.functions:
            selected_entry = req_entry
        elif mod.functions:
            try:
                selected_entry = adapter.select_entry(mod, req_entry)
            except Exception:
                # Non-main preferred, otherwise check main-only
                non_main = [k for k in mod.functions if k != "main"]
                if non_main:
                    selected_entry = non_main[0]
                    reasons.append(
                        Reason(
                            code=ReasonCode.ENTRY_AUTO_SELECTED,
                            message=f"Auto-selected entry '{selected_entry}' from {non_main}.",
                            stage="triage",
                        )
                    )
                elif "main" in mod.functions:
                    selected_entry = "main"
                    strategy = ExecutionStrategy.ANALYSIS_ONLY
                    reasons.append(
                        Reason(
                            code=ReasonCode.UNSUPPORTED_ENTRY_KIND,
                            message=f"{lang_id.upper()} file contains only `main()`; program-mode execution is not yet enabled for {lang_id}.",
                            remediation="Wrap the core algorithm in a callable function or provide hints.",
                            stage="triage",
                        )
                    )
        else:
            strategy = ExecutionStrategy.ANALYSIS_ONLY
            reasons.append(
                Reason(
                    code=ReasonCode.UNSUPPORTED_ENTRY_KIND,
                    message=f"No callable function found in {lang_id} source (script/program mode not yet enabled for {lang_id}).",
                    remediation="Wrap the core logic in a named function (e.g. `function solve(...)`).",
                    stage="triage",
                )
            )

        # C++ template without instantiation hint -> ANALYSIS_ONLY
        if lang_id == "cpp" and selected_entry and selected_entry in mod.functions:
            fn = mod.functions[selected_entry]
            if (fn.extra.get("is_template") or fn.extra.get("template_params")) and not hints.get("instantiate"):
                strategy = ExecutionStrategy.ANALYSIS_ONLY
                reasons.append(
                    Reason(
                        code=ReasonCode.UNSUPPORTED_ENTRY_KIND,
                        message=f"C++ function '{selected_entry}' is a template without `hints.instantiate`.",
                        remediation="Provide `hints: {instantiate: ['int']}` in overrides to benchmark a concrete instantiation.",
                        stage="triage",
                    )
                )

    # 6. Toolchain availability check
    toolchain_ok, tc_msg = _check_toolchain(lang_id, s)
    if not toolchain_ok:
        reasons.append(
            Reason(
                code=ReasonCode.TOOLCHAIN_MISSING,
                message=tc_msg,
                stage="triage",
                detail={"language": lang_id},
            )
        )

    # 7. Determine final triage support level
    if missing_deps or not toolchain_ok or strategy == ExecutionStrategy.ANALYSIS_ONLY:
        strategy = ExecutionStrategy.ANALYSIS_ONLY
        support_level = SupportLevel.ANALYSIS_ONLY
    else:
        support_level = SupportLevel.FULL

    return TriageResult(
        language=lang_id,
        strategy=strategy,
        support_level=support_level,
        entry_point=selected_entry,
        entry_candidates=candidates,
        entry_ranking=ranking,
        reasons=reasons,
        missing_dependencies=missing_deps,
        has_import_side_effects=has_side_effects,
        detected_class=detected_class,
        method_kind=method_kind,
        source_sha=sha,
        toolchain_ok=toolchain_ok,
    )
