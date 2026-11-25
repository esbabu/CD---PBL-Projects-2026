"""
Multi-language security analysis — entry point
================================================
``analyze_source(source, filepath, language)`` returns the same
``SecurityFindings`` object the Python analyzer returns, so the CLI, the GUI,
the fix agent's reports and the RAG guidance work for every language.

Pipeline per file: parse → lower to IR (``lower.py`` / ``cobol.py``) → CFG and
data-flow (``analysis.cfg_builder`` / ``dfa_engine``) → taint (``taint.py``) +
memory safety (``memory.py``) + syntax rules (``patterns.py``) → findings.

Suppression: a comment ``nosec SEC005: <reason>`` on the line (``//``, ``/* */``,
``#``, or ``*>`` in COBOL) suppresses that rule there; without a reason it is
ignored, like in the Python analyzer.
"""
from __future__ import annotations

import os
import re
import time
from typing import Dict, List, Optional

from ..languages import detect_language
from ..security.findings import Finding, SecurityFindings, lower_severity, min_level
from ..security.rules import RULES
from .specs import SPECS

SUPPORTED = ("java", "c", "cpp", "csharp", "rust", "cobol")

def _ml_caption(lang: str) -> str:
    """ML detector status from the saved test metrics (python -m src.vulnml.pipeline train)."""
    import json
    path = os.path.join(os.path.dirname(__file__), "..", "..", "outputs", "vulnml", f"{lang}_metrics.json")
    cfg_path = path.replace("_metrics.json", "_config.json")
    try:
        m = json.load(open(path, encoding="utf-8"))
        cfg = json.load(open(cfg_path, encoding="utf-8"))
    except (OSError, ValueError):
        return "none (no trained model; run python -m src.vulnml.pipeline train)"
    if "test_binary" not in m:
        return "none (metrics in an old format; rerun python -m src.vulnml.pipeline train)"
    f1 = m["test_binary"].get("f1")
    parts = [f"test F1 {f1}" if f1 is not None else "test F1 undefined (no true positives)"]
    for src, label in (("juliet", "Juliet"), ("owasp", "OWASP"), ("custom", "hand-written")):
        b = m.get("test_by_source", {}).get(src)
        if b and b.get("positives"):
            parts.append(f"{label} recall {b['recall']}")
    if cfg.get("small_n"):
        return (f"partial (small-n: {cfg['counts']['train']} training samples; " + "; ".join(parts)
                + "; not used by the neuro-symbolic engine)")
    return "partial (" + "; ".join(parts) + ")"


# What each language gets. full = modelled like Python (taint across functions, sources/sinks/sanitizers,
# CFG + data-flow); partial = works with the limits named in the note; none = not available.
CAPABILITIES: Dict[str, Dict[str, str]] = {
    "python": {"parsing": "full", "ir_cfg_dataflow": "full", "taint": "full", "rules": "full (50 rules)",
               "memory_safety": "n/a", "ml_detector": _ml_caption("python"), "neuro_symbolic": "full (fusion of rules, ML and KB conditions; ML signal limited, see ml_detector)",
               "fix_agent": "full (12 rules)", "rag": "full", "comments": "full (3 engines)"},
    "java": {"parsing": "full (tree-sitter)", "ir_cfg_dataflow": "full", "taint": "full (intra-file summaries)",
             "rules": "partial (injection, crypto, TLS, XXE, deserialization, races, auth)", "memory_safety": "n/a",
             "ml_detector": _ml_caption("java"), "neuro_symbolic": "full (fusion of rules, ML and KB conditions; ML signal limited, see ml_detector)", "fix_agent": "none", "rag": "full",
             "comments": "full (Javadoc)"},
    "csharp": {"parsing": "full (tree-sitter)", "ir_cfg_dataflow": "full", "taint": "full (intra-file summaries)",
               "rules": "partial (injection, crypto, TLS, XXE, deserialization, races, auth)", "memory_safety":
               "partial (unsafe blocks)", "ml_detector": _ml_caption("csharp"), "neuro_symbolic": "full (fusion of rules, ML and KB conditions; ML signal limited, see ml_detector)",
               "fix_agent": "none", "rag": "full", "comments": "full (XML doc comments)"},
    "cpp": {"parsing": "full (tree-sitter)", "ir_cfg_dataflow": "full", "taint": "full (intra-file summaries)",
            "rules": "partial (injection, buffers, format strings, crypto, TLS, races)",
            "memory_safety": "partial (UAF / double free / unchecked malloc; no alias analysis)",
            "ml_detector": _ml_caption("cpp"), "neuro_symbolic": "full (fusion of rules, ML and KB conditions; ML signal limited, see ml_detector)", "fix_agent": "none", "rag": "full",
            "comments": "full (Doxygen)"},
    "c": {"parsing": "full (tree-sitter)", "ir_cfg_dataflow": "full", "taint": "full (intra-file summaries)",
          "rules": "partial (injection, buffers, format strings, crypto, TLS, races)",
          "memory_safety": "partial (UAF / double free / unchecked malloc; no alias analysis)",
          "ml_detector": _ml_caption("c"), "neuro_symbolic": "full (fusion of rules, ML and KB conditions; ML signal limited, see ml_detector)", "fix_agent": "none", "rag": "full",
          "comments": "full (Doxygen)"},
    "rust": {"parsing": "full (tree-sitter)", "ir_cfg_dataflow": "full", "taint": "full (intra-file summaries)",
             "rules": "partial (command, SQL, path, SSRF, TLS, unsafe code, panics, static mut)",
             "memory_safety": "partial (unsafe operations flagged, not proven)",
             "ml_detector": _ml_caption("rust"), "neuro_symbolic": "partial (rules + knowledge base; small-n ML model not used)", "fix_agent": "none", "rag": "full", "comments": "full (rustdoc)"},
    "cobol": {"parsing": "partial (own parser: DATA + PROCEDURE DIVISION statements; no COPY expansion)",
              "ir_cfg_dataflow": "full (paragraphs, IF, EVALUATE, PERFORM)", "taint": "partial (one program per file)",
              "rules": "partial (dynamic SQL, CALL, file names, reference modification, STRING overflow, secrets)",
              "memory_safety": "partial (STRING overflow, reference modification)",
              "ml_detector": _ml_caption("cobol"),
              "neuro_symbolic": "partial (rules + knowledge base; small-n ML model not used)", "fix_agent": "none", "rag": "full",
              "comments": "full (*> comment blocks)"},
}

_NOSEC = re.compile(r"nosec\s+(SEC\d{3})(?:\s*:\s*(\S.*?))?\s*(\*/|$)")


def _language_of(filepath: str, source: str, language: Optional[str]) -> str:
    if language:
        return language
    ext = os.path.splitext(filepath or "")[1].lower()
    if ext in (".cob", ".cbl", ".cpy", ".cobol"):
        return "cobol"
    if ext in (".cs",):
        return "csharp"
    if ext in (".rs",):
        return "rust"
    return detect_language(filepath, source)


def _lower(source: str, lang: str, filepath: str):
    if lang == "cobol":
        from .cobol import lower_cobol
        return lower_cobol(source, filepath)
    from .lower import lower_source
    return lower_source(source, lang, filepath)


def analyze_source(source: str, filepath: str = "<string>", language: Optional[str] = None,
                   engines: str = "rules") -> SecurityFindings:
    """Analyse Java / C / C++ / C# / Rust / COBOL source.

    engines: ``"rules"`` (taint + memory + syntax rules), or ``"neurosymbolic"`` to also run the ML
    detector and fuse it with the rule results (``src/vulnml``).
    """
    t0 = time.perf_counter()
    lang = _language_of(filepath, source, language)
    result = SecurityFindings(file=filepath)
    if lang not in SUPPORTED:
        result.parse_error = f"language {lang!r} is not handled by the multi-language analyzer"
        return result
    from .. import perf
    nlines = source.count("\n") + 1
    try:
        with perf.block("security.parse_and_ir_lowering", lines=nlines):
            mod = _lower(source, lang, filepath)
    except Exception as exc:                      # a parser failure is reported, never hidden
        result.parse_error = f"{type(exc).__name__}: {exc}"
        return result
    from .memory import analyze_memory
    from .patterns import run_patterns
    from .taint import TaintEngine

    with perf.block("security.cfg_dataflow_taint", lines=nlines):
        engine = TaintEngine(mod, SPECS[lang], RULES)
        hits = engine.run()
    findings: List[Finding] = [_from_hit(h, filepath, mod) for h in hits]
    with perf.block("security.rules_and_findings", lines=nlines):
        raw = run_patterns(mod) if lang != "cobol" else []
        if lang == "cobol":
            from .cobol import cobol_patterns
            raw += cobol_patterns(mod)
    with perf.block("security.memory_safety", lines=nlines):
        raw += analyze_memory(mod)
    findings += [_from_raw(r, filepath, mod) for r in raw]
    findings = _dedupe(findings)
    _suppress(findings, mod.source)
    result.findings = sorted(findings, key=lambda f: (f.line, f.rule_id))
    result.functions_analysed = len(mod.functions)
    result.unmodelled = {q: list(i.fn.unsupported) for q, i in mod.functions.items() if i.fn.unsupported}
    result.converged = engine.converged
    if mod.syntax_error:
        result.unmodelled["<file>"] = [f"parser recovered from a {mod.syntax_error}; results there may be incomplete"]
    if engines == "neurosymbolic":
        from ..vulnml.fusion import fuse
        result.findings = fuse(result.findings, mod, lang, filepath)
    result.runtime_ms = (time.perf_counter() - t0) * 1000
    return result


def analyze_file(path: str, language: Optional[str] = None, engines: str = "rules") -> SecurityFindings:
    with open(path, encoding="utf-8", errors="replace") as fh:
        return analyze_source(fh.read(), path, language, engines)


def _code(mod, line: int) -> str:
    lines = mod.source.splitlines()
    return lines[line - 1].strip()[:200] if 0 < line <= len(lines) else ""


def _from_hit(h, filepath: str, mod) -> Finding:
    rule = RULES[h.rule_id]
    info = h.info
    factors = []
    if h.resolution == "method-name":
        factors.append(("medium", f"sink '{h.sink_name}' matched by method name; the receiver's type was not resolved"))
    if info.trust == "local":
        factors.append(("medium", f"source is {info.description} (local / operator-controlled)"))
    for u in sorted(info.unc):
        factors.append(("medium", u))
    confidence = min_level([lvl for lvl, _ in factors])
    severity = rule.severity
    sev_reason = f"base severity of {rule.rule_id} ({rule.category})"
    if info.trust == "local":
        severity = lower_severity(severity)
        sev_reason += "; lowered one level because the source is local/operator-controlled"
    trace = [{"line": s[0], "col": 0, "kind": s[1], "text": s[2], "function": s[3]} for s in info.trace]
    f = Finding(
        rule_id=rule.rule_id, title=rule.title, category=rule.category, cwe=rule.cwe, severity=severity,
        confidence=confidence, status="confirmed" if confidence == "high" else "potential", file=filepath,
        function=h.function, line=h.line, col=h.col,
        message=(f"Data from {info.description} reaches {h.operation} ({h.sink_name}) as {h.role} without "
                 f"{h.context}-context sanitisation."),
        remediation=rule.remediation, analysis="taint", severity_reason=sev_reason,
        confidence_reasons=[t for _, t in factors] or ["resolved sink reached by a recognised untrusted source"],
        sink={"name": h.sink_name, "operation": h.operation, "role": h.role, "line": h.line, "col": h.col,
              "code": _code(mod, h.line)},
        source={"description": info.description, "kind": "source", "trust": info.trust, "line": info.origin_line,
                "col": 0, "function": info.origin_function, "file": filepath, "code": _code(mod, info.origin_line)},
        trace=trace, sanitizers=[s["text"] for s in trace if s["kind"] == "sanitizer"],
        missing_protections=[f"no sanitizer valid for the '{h.context}' context on this path"],
    )
    f.compute_fingerprint()
    return f


def _from_raw(r: dict, filepath: str, mod) -> Finding:
    rule = RULES[r["rule_id"]]
    conf = r.get("confidence", "high")
    f = Finding(
        rule_id=rule.rule_id, title=rule.title, category=rule.category, cwe=rule.cwe,
        severity=lower_severity(rule.severity) if r.get("analysis") == "api-use" else rule.severity,
        confidence=conf, status="confirmed" if conf == "high" else "potential", file=filepath,
        function=r.get("function", "<module>"), line=int(r["line"]), col=int(r.get("col", 0)),
        message=str(r["message"]), remediation=rule.remediation, analysis=str(r.get("analysis", "ast-pattern")),
        severity_reason=f"base severity of {rule.rule_id} ({rule.category})",
        confidence_reasons=list(r.get("confidence_reasons") or []) or ["structural pattern matched exactly"],
        sink={"name": "", "operation": "", "role": "", "line": int(r["line"]), "col": int(r.get("col", 0)),
              "code": _code(mod, int(r["line"]))},
        trace=[{"line": int(r["line"]), "col": 0, "kind": "pattern", "text": _code(mod, int(r["line"])),
                "function": r.get("function", "")}],
    )
    f.compute_fingerprint()
    return f


def _dedupe(findings: List[Finding]) -> List[Finding]:
    """One finding per (rule, line, origin); a taint finding supersedes a pattern finding of the same rule."""
    by_key: Dict[tuple, Finding] = {}
    taint_lines = {(f.rule_id, f.line) for f in findings if f.analysis == "taint"}
    taint_funcs = {(f.rule_id, f.function) for f in findings if f.analysis == "taint"}
    for f in findings:
        if f.analysis != "taint" and (f.rule_id, f.line) in taint_lines:
            continue
        if f.analysis == "api-use" and (f.rule_id, f.function) in taint_funcs:
            continue                    # the traced flow already reports this dangerous API
        k = (f.rule_id, f.line, (f.source or {}).get("description", ""))
        if k not in by_key:
            by_key[k] = f
    return list(by_key.values())


def _suppress(findings: List[Finding], source: str) -> None:
    lines = source.splitlines()
    for f in findings:
        for ln in (f.line, f.line - 1):
            if not 0 < ln <= len(lines):
                continue
            m = _NOSEC.search(lines[ln - 1])
            if m and m.group(1) == f.rule_id:
                if m.group(2):
                    f.status = "suppressed"
                    f.suppression_reason = m.group(2).strip()
                else:
                    f.confidence_reasons.append("'# nosec' without a reason is ignored")
                break
