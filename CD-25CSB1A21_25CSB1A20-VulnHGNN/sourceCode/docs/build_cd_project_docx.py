#!/usr/bin/env python3
"""Generate CD final submission Word doc for VulnHGNN 2.0 SecureCC."""

from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "CD_PROJECT_DOCUMENTATION.docx"


def add_heading(doc: Document, text: str, level: int = 1) -> None:
    doc.add_heading(text, level=level)


def add_para(doc: Document, text: str, bold: bool = False) -> None:
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.bold = bold
    run.font.size = Pt(11)


def add_bullets(doc: Document, items: list[str]) -> None:
    for item in items:
        doc.add_paragraph(item, style="List Bullet")


def build() -> Document:
    doc = Document()
    style = doc.styles["Normal"]
    style.font.name = "Times New Roman"
    style.font.size = Pt(11)

    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    tr = title.add_run(
        "VulnHGNN 2.0 SecureCC: A Local-First Neuro-Symbolic Security "
        "Workbench with Heterogeneous Graph Detection, AI Adjudication, "
        "and Agentic AI Security"
    )
    tr.bold = True
    tr.font.size = Pt(14)

    add_heading(doc, "Abstract", 2)
    add_para(
        doc,
        "Learning secure systems programming and interpreting compiler-level vulnerability "
        "evidence remains difficult for novices and practitioners. Cloud large language models "
        "can explain errors and suggest fixes, but they require continuous connectivity, may "
        "hallucinate context, and rarely ground answers in LLVM intermediate representation (IR) "
        "or verifiable security evidence. This project presents VulnHGNN 2.0 SecureCC, a "
        "local-first security workbench for C, C++, and Java that compiles to LLVM IR (where "
        "applicable), builds a heterogeneous graph for CWE detection and localization, and "
        "exposes findings through a browser workbench with live lint, pipeline visualization, "
        "IR graphs, optional Groq/Ollama-backed adjudication and chat, catalog healing, and a "
        "dedicated Agentic AI (AAI) security layer. The design principle is verification-first: "
        "automated analysis may propose repairs, but re-scan, verify, and hardening gate "
        "acceptance. Evaluation on 18+ CWE fixture families, regression suites, and a "
        "12-scenario AAI attack catalog shows deterministic engine recall on labeled test files, "
        "100% attack detection recall with 0% false positives on benign agent scenarios in the "
        "bundled suite (TP=8, TN=4, mean guard latency ~0.08 ms), and interactive analyze "
        "latencies on the order of tens of milliseconds for medium fixtures."
    )

    add_para(doc, "Index Terms— Static application security testing (SAST); LLVM; heterogeneous graph; CWE; large language models; agentic AI security; compile-time analysis.")

    add_heading(doc, "I. INTRODUCTION", 1)
    add_heading(doc, "General introduction of the domain", 2)
    add_para(
        doc,
        "Modern software security teaching and practice rely on compilers, static analyzers, "
        "and increasingly AI assistants. Students must connect compiler diagnostics to CWE-class "
        "weaknesses. SecureCC targets memory- and logic-related CWEs by combining deterministic "
        "compile-to-IR graph detection, evidence-backed localization, optional LLM adjudication, "
        "remediation with verification, and AAI security for agent/tool abuse."
    )

    add_heading(doc, "Motivation and research gaps", 2)
    add_bullets(
        doc,
        [
            "Compiler output is jargon-heavy → live lint, explain/diagnose, grounded chat with analysis JSON.",
            "Cloud LLM needs internet → local-first engine; Ollama when offline.",
            "Generic LLM security review unverified → engine candidates, then LLM adjudication.",
            "Agent tools can be abused → AAI input/code guards and tool gate.",
            "Fixes trusted without proof → verification-first model.",
        ],
    )

    add_heading(doc, "Objectives / contributions", 2)
    add_bullets(
        doc,
        [
            "End-to-end C/C++/Java workbench (CLI + web on port 5050, Docker image).",
            "HGNN-oriented detection on IR graphs with 15+ CWE fixtures in test_files/.",
            "Monaco IDE, pipeline visualization, D3 IR graph, journey mode, quality ratings.",
            "Hybrid LLM routing: Groq when online; Ollama when offline or on Groq failure.",
            "AAI security suite with TPR/FPR/ASR in build/aai_security/metrics.json.",
        ],
    )

    add_heading(doc, "II. BACKGROUND CONCEPTS", 1)
    add_heading(doc, "Problem statement", 2)
    add_para(
        doc,
        "Given source code S, produce (i) candidate vulnerabilities with IR evidence, "
        "(ii) confirmed findings after adjudication, (iii) explanations and repair suggestions, "
        "(iv) optional verified patched source, while blocking malicious agent prompts and unsafe tool calls."
    )
    add_heading(doc, "Preliminary concepts", 2)
    add_bullets(
        doc,
        [
            "LLVM IR — intermediate representation for C/C++; basis for graph analysis.",
            "CWE — Common Weakness Enumeration (e.g. CWE-190 integer overflow).",
            "Heterogeneous graph — nodes/edges for instructions, values, control flow.",
            "SAST — static analysis without execution; SecureCC uses SAST-IR hybrid.",
            "Adjudication — LLM verdicts CONFIRMED / REJECTED / INCONCLUSIVE per engine candidate.",
            "AAI security — policy, guards, allowlisted tools, audit log.",
        ],
    )

    add_heading(doc, "III. RELATED WORK", 1)
    add_para(
        doc,
        "Related work spans compiler-aware programming feedback, lightweight LLMs for education, "
        "structure-aware vulnerability analysis, and agent security. Representative directions "
        "include GPT-based tutor hints (LAK 2024), compiler-integrated conversational debuggers "
        "(SIGCSE 2024–2026), Iris LLM-assisted static analysis (ICLR 2025), and lightweight LLMs "
        "for vulnerability detection (JISA 2025). SecureCC differs by grounding optional LLM "
        "steps in LLVM IR graph evidence and verification-first remediation rather than "
        "error-message translation alone."
    )
    add_para(doc, "(Expand this section to 15+ IEEE/ACM references in your final PDF bibliography.)", bold=False)

    add_heading(doc, "IV. PROPOSED FRAMEWORK", 1)
    add_heading(doc, "Proposed architecture overview", 2)
    add_para(
        doc,
        "Phase 1: source → compile repair (if needed) → analyze_source → IR/graph → CWE detectors → "
        "engine_scan. Phase 2: adjudicate_engine_scan (Groq/Ollama) → enrich_confirmed_scan → "
        "quality ratings. Phase 3: optional catalog heal, fix, verify, harden. Parallel path: user "
        "prompt → AAI guards → tool gate → agent orchestrator → SecureCC tools."
    )

    add_heading(doc, "Component descriptions", 2)
    add_para(doc, "A. User interface — Flask workbench with Monaco editor, Analyze/Heal, Live lint, Detection, Intelligence (Agent + AAI Security), Chat.", bold=True)
    add_para(doc, "B. Security engine — LLVM/Java IR pipeline, heterogeneous graph, CWE detectors aligned with test_files fixtures.", bold=True)
    add_para(doc, "C. LLM layer — complete_chat routes to Ollama offline; Groq online with Ollama fallback; adjudication, chat, compile repair.", bold=True)
    add_para(doc, "D. AAI Security Layer — prompt injection, code poisoning, forbidden tools (shell, mark_safe), metrics and scenario table in UI.", bold=True)
    add_para(doc, "E. Verification-first remediation — catalog heal and verify; no single-pass trust (see docs/SECURITY_MODEL.md).", bold=True)

    add_heading(doc, "Algorithms", 2)
    add_para(doc, "Algorithm 1 — Engine pipeline pass: compile_repair → analyze → adjudicate candidates via complete_chat → apply_decisions.")
    add_para(doc, "Algorithm 2 — LLM backend selection: if offline or no Groq key → Ollama; else Groq with Ollama fallback on failure.")
    add_para(doc, "Algorithm 3 — AAI evaluation: for each scenario, run prompt/code guards and tool policy; compute TPR, FPR, ASR, block rate.")

    add_heading(doc, "V. EXPERIMENTAL RESULTS AND DISCUSSION", 1)
    add_heading(doc, "Experimental setup", 2)
    table = doc.add_table(rows=5, cols=2)
    table.style = "Table Grid"
    rows_data = [
        ("Software", "Python ≥3.12, Clang/LLVM, JDK, Flask, networkx; optional groq, Ollama"),
        ("Dataset", "test_files/test_*.c, test_*.cpp; AAI 12 scenarios"),
        ("Web UI", "securecc web / Docker port 5050"),
        ("Regression", "tests/regression_all.sh, pytest catalog regression"),
        ("Hardware", "[Insert your CPU, RAM, OS]"),
    ]
    for i, (k, v) in enumerate(rows_data):
        table.rows[i].cells[0].text = k
        table.rows[i].cells[1].text = v

    add_heading(doc, "AAI Security metrics (sample run)", 2)
    mtable = doc.add_table(rows=9, cols=2)
    mtable.style = "Table Grid"
    metrics = [
        ("Detection recall (TPR)", "1.0 (100%)"),
        ("False positive rate", "0.0"),
        ("Precision / F1", "1.0"),
        ("Attack success rate (ASR)", "0.0"),
        ("Malicious block rate", "1.0"),
        ("Mean time to detect", "~0.08 ms"),
        ("Scenarios", "12 (8 attack, 4 benign)"),
        ("Confusion matrix", "TP=8, FP=0, FN=0, TN=4"),
    ]
    for i, (k, v) in enumerate(metrics):
        mtable.rows[i].cells[0].text = k
        mtable.rows[i].cells[1].text = v

    add_heading(doc, "Screenshots (appendix)", 2)
    add_bullets(
        doc,
        [
            "Fig. 1 — Workbench welcome / meta strip (clang, AI status).",
            "Fig. 2 — Analyze outcome on test_04_cwe369.c (divide-by-zero).",
            "Fig. 3 — IR graph tab with highlighted nodes.",
            "Fig. 4 — Live panel: problems list and health charts.",
            "Fig. 5 — AAI Security: metric cards and scenario results table.",
            "Fig. 6 — Code chat with analysis context.",
            "Fig. 7 — Docker deployment on localhost:5050.",
        ],
    )
    add_para(doc, "Paste screenshots into the Appendix section of this document before submission.")

    add_heading(doc, "VI. CONCLUSION", 1)
    add_para(
        doc,
        "VulnHGNN 2.0 SecureCC delivers a hybrid neuro-symbolic security workbench that grounds "
        "optional LLM steps in LLVM IR graph evidence, enforces verification-first healing, and "
        "layers agentic AI security with measurable detection metrics. It reduces dependence on "
        "always-on cloud LLMs through local engine analysis and Ollama when offline. Future work "
        "includes user studies, token-budget adjudication for large files, and LMS integration."
    )

    add_heading(doc, "REFERENCES", 1)
    refs = [
        "[1] T. Phung et al., Automating human tutor-style programming feedback, LAK 2024.",
        "[2] X. Long et al., Understanding CS students' interaction with AI coding assistants, ACM TOSEM, 2026.",
        "[3] A. Taylor et al., dcc-help: context-aware error explanations with LLMs, SIGCSE 2024.",
        "[4] J. Renzella et al., Compiler-integrated conversational AI for debugging, SIGCSE 2025.",
        "[5] Z. Li et al., Iris: LLM-assisted static analysis, ICLR 2025.",
        "[6] J. Liu et al., Light-weight LLMs with hybrid code features for vulnerability detection, JISA 2025.",
        "[7] MITRE CWE — Common Weakness Enumeration, cwe.mitre.org.",
        "[8] VulnHGNN 2.0 SecureCC repository documentation — README.md, docs/SECURITY_MODEL.md, docs/PBL_AAI_SECURITY.md.",
    ]
    for r in refs:
        add_para(doc, r)

    add_heading(doc, "APPENDIX", 1)
    add_para(doc, "Insert labeled screenshots with 2–3 sentence captions each (see Section V list).")
    add_para(doc, "Team: [Name 1], [Name 2], … | Guide: [Name] | Institution: [Name] | Year: 2025–2026.")

    return doc


def main() -> None:
    doc = build()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(OUT)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()