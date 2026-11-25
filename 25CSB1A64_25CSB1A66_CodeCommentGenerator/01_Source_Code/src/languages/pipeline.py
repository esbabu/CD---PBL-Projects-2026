"""
Pipeline for Java, C and C++ files.

Runs parse → extract → analyze → generate → attach with the tree-sitter front
end and returns the same ``PipelineResult`` shape as the Python pipeline. The
Python-only stages (IR, pattern analysis, security) return empty results with a
note, so every caller (CLI, GUI, tests) can treat both paths alike.
"""
from __future__ import annotations

from typing import Dict, List, Optional

from ..analysis.pattern_detector import AnalysisReport
from ..comment_attacher import AttachResult
from ..comment_generator import CommentItem
from ..ir.ir_nodes import IRModule
from ..security_analyzer import SecurityReport
from . import language_name
from .doc_render import generate_foreign_comments
from .doc_render import STYLE_FOR
from .treesitter_extract import analyze_source

TREESITTER_LANGS = ("java", "c", "cpp")


def foreign_analysis(source_code: str, language: str, filepath: str = ""):
    """Comment features for a non-Python file (tree-sitter extractor or the multi-language IR)."""
    if language in TREESITTER_LANGS:
        return analyze_source(source_code, language, filepath)
    from .generic_extract import analyze_generic
    return analyze_generic(source_code, language, filepath)


def attach_foreign(source_code: str, comments: List[CommentItem], fixed_indent: Optional[str] = None) -> AttachResult:
    """Insert block comments above their declarations, copying each line's own indentation (tabs included).

    ``fixed_indent`` overrides that (COBOL: comment lines start in column 7)."""
    lines = source_code.splitlines()
    insertions: Dict[int, List[str]] = {}
    diff_log: List[str] = []
    for item in comments:
        idx = max(0, min(item.lineno - 1, len(lines)))
        target = lines[idx] if idx < len(lines) else ""
        indent = target[: len(target) - len(target.lstrip())] if fixed_indent is None else fixed_indent
        new_lines = [indent + text if text else indent.rstrip() for text in item.text.splitlines()]
        if idx not in insertions and idx > 0:
            prev = lines[idx - 1].strip()
            # Keep declarations visually separate: blank line unless the previous
            # line opens a block, is an access label, or is already blank.
            if prev and not prev.endswith(("{", ":")) and not prev.startswith("#"):
                new_lines.insert(0, "")
        insertions.setdefault(idx, []).extend(new_lines)
        diff_log.append(f"  + [{item.kind}] {item.node_type} '{item.target_name}' (before original line {idx + 1}):")
        diff_log.extend(f"      {nl}" for nl in new_lines)

    out: List[str] = []
    line_map: Dict[int, int] = {}
    for i, line in enumerate(lines):
        out.extend(insertions.get(i, []))
        out.append(line)
        line_map[len(out)] = i + 1
    out.extend(insertions.get(len(lines), []))
    text = "\n".join(out)
    if source_code.endswith("\n"):
        text += "\n"
    return AttachResult(annotated_source=text, diff_log=diff_log, comments_attached=len(comments),
                        line_map=line_map)


def run_foreign_pipeline(filepath: str, source_code: str, language: str, logger, engine: str = "rule_based"):
    from ..main import PipelineResult   # local import: main imports this module

    lang = language_name(language)
    logger.begin_stage("parse")
    analysis = foreign_analysis(source_code, language, filepath)
    logger.end_stage(summary={"total_lines": len(source_code.splitlines()), "file": filepath, "language": lang},
                     warnings=analysis.syntax_warnings)

    logger.begin_stage("validate")
    logger.end_stage(summary={"issues_found": len(analysis.syntax_warnings)}, warnings=analysis.syntax_warnings)

    mf, cg = analysis.module_features, analysis.context_graph
    logger.begin_stage("extract")
    logger.end_stage(summary={"functions": len(mf.functions), "classes": len(mf.classes), "imports": len(mf.imports)})

    logger.begin_stage("analyze")
    dist: Dict[str, int] = {}
    for fc in cg.function_contexts:
        dist[fc.complexity_label] = dist.get(fc.complexity_label, 0) + 1
    logger.end_stage(summary={"function_contexts": len(cg.function_contexts), "complexity_distribution": dist})

    logger.begin_stage("generate")
    warnings = []
    if engine != "rule_based":
        warnings.append(f"The ML model was trained on Python docstrings; {lang} comments use the rule-based engine.")
    comments = generate_foreign_comments(analysis)
    counts: Dict[str, int] = {}
    for c in comments:
        counts[c.kind] = counts.get(c.kind, 0) + 1
    logger.end_stage(summary={"total_comments": len(comments), "by_kind": counts, "engine": "rule_based",
                              "style": STYLE_FOR.get(language, "doxygen")}, warnings=warnings)
    logger.set_comments_generated(len(comments))

    logger.begin_stage("attach")
    attach_result = attach_foreign(source_code, comments, fixed_indent="      " if language == "cobol" else None)
    logger.end_stage(summary={"comments_attached": attach_result.comments_attached})

    # ── IR, CFG + data-flow patterns and security for every language (src/multilang) ──
    logger.begin_stage("build_ir")
    from ..analysis.cfg_builder import build_cfg
    from ..analysis.dfa_engine import run_dfa
    from ..analysis.pattern_detector import detect_patterns
    from ..multilang.analyzer import _lower
    try:
        lowered = _lower(source_code, language, filepath)
        ir_module = lowered.ir
        logger.end_stage(summary={"ir_functions": len(ir_module.functions),
                                  "total_blocks": sum(len(f.blocks) for f in ir_module.functions)})
    except Exception as exc:                      # report, never hide
        ir_module = IRModule(source_file=filepath)
        logger.end_stage(summary={"ir_functions": 0}, warnings=[f"IR lowering failed: {exc}"])
    logger.begin_stage("analysis")
    dfa_results = [run_dfa(build_cfg(f), f) for f in ir_module.functions]
    analysis_report = detect_patterns(ir_module, dfa_results) if ir_module.functions else AnalysisReport(source_file=filepath)
    logger.end_stage(summary={"findings": len(analysis_report.findings), "summary": analysis_report.summary})
    logger.begin_stage("security")
    from ..security_analyzer import run_security_analysis
    security_report = run_security_analysis(mf, cg, source_code, language=language)
    logger.end_stage(summary={"total_issues": security_report.total_issues,
                              "module_safe_pct": security_report.module_safe_pct})

    return PipelineResult(
        attach_result.annotated_source, comments, mf, cg, attach_result,
        ir_module, analysis_report, security_report, language,
    )
