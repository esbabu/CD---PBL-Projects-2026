# Progress Against the Proposed Architecture

Status as of 20 November 2026. "Proposed architecture" = the design in
[architecture.png](architecture.png) and the project presentation (`CodeCommentGenerator.pptx`).
Every status below was checked by running the code (CLI, GUI and the 658-test suite), not
taken from earlier notes.

**Overall:** all 11 components of the proposed architecture are built, connected and
working end to end. The one remaining gap is quality, not building: the ML model's output
quality. Measured by components, roughly **90 %** of the
proposed system is complete. Three parts go beyond the original proposal: the security
analyzer, support for Java, C and C++ input in addition to Python (item 12), and a
fix-and-verify agent that patches security findings and checks each patch with the analyzer
(item 13).

| # | Component (proposed) | Status | Evidence | Remaining work |
|---|---|---|---|---|
| 1 | Input: CLI and GUI entry points | ✅ Done | Screenshots A1–A2, B1–B2 | — |
| 2 | Parse + semantic validation | ✅ Done | Tests; syntax errors reported with line/column | — |
| 3 | AST feature extraction | ✅ Done | B4 (AST Features), B5 (AST Graph) | — |
| 4 | Context analysis (complexity, call graph, variables) | ✅ Done | B6, B7 | — |
| 5 | Rule-based NLP engine | ✅ Done | A3 | — |
| 6 | ML engine (T5-small on AST features) | ⚠️ Working, quality low | Trained on 13,480 pairs; BLEU-4 0.060, ROUGE-L 0.262, exact match 1 % (B10, B12) | Train on the full default corpus (20,000 CodeSearchNet functions, 4 epochs) or a code-specific model; add a small human evaluation of comment quality |
| 7 | Neuro-symbolic fusion (confidence-gated) | ✅ Done | A5: ML summary used in *fused* mode at 46 % confidence | Depends on item 6 for better summaries |
| 8 | Comment attachment | ✅ Done | A3, A5; output always compiles; multi-line signatures fixed; line map kept | — |
| 9 | IR + CFG + data-flow + 7 patterns | ✅ Done (rebuilt) | A6, A7, B8, B9; IR now lowered from the real AST (branches, loops, try/finally, match) | — |
| 10 | Security analysis | ✅ Done, beyond proposal | Proposal: 12 pattern rules with a score. Now: **50 rules** (SEC001–SEC050), taint analysis with source→sink traces, cross-file analysis, benchmarks (A8, A9, B11); SSRF, open redirect and XXE added last (A16; OWASP redirect + XXE held-out F1 0.933, original 8 categories unchanged); 32 rules added on 20 Nov (LDAP, XPath, NoSQL, log, header, regex, reflection, format string, setattr, session, plus 22 settings/crypto/transport rules) — OWASP LDAP/XPath/trust-boundary/secure-cookie F1 0.862 (held-out 0.860) | Recognise validation done in helper functions; model more sink APIs (see SECURITY_ANALYSIS.md §6) |
| 11 | Outputs: annotated file, JSON reports, GUI views | ✅ Done | A2, B3, B13 | — |
| 12 | Other input languages: Java, C, C++ (not in the proposal) | ✅ Done, beyond proposal | tree-sitter front end feeding the same AST features and context analysis; Javadoc / Doxygen comments; annotated files compile with javac / gcc / g++ (A11–A14, B14–B18) | Security analysis, IR and the ML engines are still Python-only; more languages (C#, Go, JavaScript) could reuse the same front end |
| 13 | Fix-and-verify agent (not in the proposal) | ✅ Done, beyond proposal | Plan → act → verify → accept/retry loop. Every patch is re-checked by the analyzer (parses; finding gone; nothing new; only the reported function changed). AST strategies for SEC005, SEC002, SEC010, SEC004, SEC001, SEC018, SEC024, SEC029, SEC030, SEC042, SEC043 and SEC044; offline RAG guidance and a verified-fix memory (`src/rag/`, docs/SECURE_AGENTIC_AI_AND_RAG.md); optional local LLM, off by default; CLI, `--fix` and GUI Auto-fix (A15, A17, B19). Measured: fixtures 25 of 43 attempted findings fixed, OWASP 130 of 164, 0 patches rejected (`outputs/benchmarks/final/agent_fix_eval.json`) | Strategies for XSS (SEC014) and path traversal (SEC013), the most common unfixed findings; run the project's tests on patched code, not only the analyzer |
| — | Evaluation (BLEU-4, ROUGE-L, exact match; security P/R/F1/FPR) | ✅ Done | B10, A9; OWASP held-out F1 0.90–0.92, real-world held-out F1 0.69 | Larger, independently reviewed real-world security benchmark |
| — | Automated tests | ✅ Done | 523 passed, including Java/C/C++ extraction, idempotence and compile checks, agent and RAG tests, a vulnerable + safe snippet for each of SEC019–SEC050, and the large-file corpus: 50 files of ~2,000 lines (101,057 lines), 500 planted vulnerabilities all found, 0 false positives (tests/large_corpus/) | — |
| — | Documentation | ✅ Done | README, docs/DOCUMENTATION.md, SECURITY_ANALYSIS.md, METHODOLOGY.md, existing and proposed architecture diagrams, these screenshots | — |

## Issues found while taking the screenshots — fixed on 10 November 2026

1. **GUI safety score was misleading.** A file with one high-severity SQL injection showed
   "100.0 % safe", because one high finding cost only 15 points and a function counted as
   unsafe only below 80. Weights are now critical 40, high 25, medium 5, low 1, so any high or
   critical finding makes the function unsafe; the sample now shows 83.3 % safe (B11).
   Regression test: `test_single_high_finding_makes_function_unsafe`.
2. **AST graph did not fit the window.** It now zooms and centres itself when data is loaded
   or the window is resized; double-click resets the view (B5).
3. **`matplotlib` was missing from `requirements.txt`** although the GUI charts need it. Added.

4. **Presentation was out of date.** `CodeCommentGenerator.pptx` has been corrected: 15 rules
   with taint analysis (slides 2, 4, 9), the new score weights (slide 4), the new severity
   groups including SEC013–SEC015 (slide 4), and P007 renamed to *Unused parameter* (slide 6).

## Changes on 20 November 2026

1. **50 security rules.** SEC019–SEC050 were added (see SECURITY_ANALYSIS.md §4). The OWASP
   numbers of the earlier categories did not change.
2. **Large-file test corpus.** 50 generated files of about 2,000 lines each, with ground truth
   written by hand (`tests/large_corpus/`). It exposed one analyzer gap: validation inside a
   conditional expression was ignored. That is now fixed.
3. **RAG guidance and fix memory** for the agent (`src/rag/`).
4. **GUI:** the language drop-down could show dark text on a dark list when Windows is in dark
   mode. The app now always uses its light palette (Fusion style plus an explicit palette),
   and the drop-down list has explicit colours. Regression test:
   `test_language_dropdown_is_readable`.

## Changes on 22 November 2026 — compiler expansion and security intelligence

1. **Six languages in the compiler back end.** Java, C#, C, C++ and Rust are lowered from
   tree-sitter, and COBOL from a new parser, into the same IR. CFG, data flow, P001–P007 and
   taint analysis now run on all of them. C#, Rust and COBOL also get doc comments: XML doc,
   rustdoc and `*>` blocks.
2. **64 rules.** SEC051–SEC064 add buffer and integer overflow, untrusted length and index,
   use after free, double free, unchecked allocation, TOCTOU, unsafe Rust/C#, missing
   authorization, panicking parse, shared mutable state and neuro-symbolic findings. The
   existing rules now run in every language where they apply.
3. **Knowledge base of 1,512 entries** from MITRE CWE 5.0, CAPEC and NIST SARD Juliet, wired
   into the RAG (`explain_finding`). Documented and implemented coverage are kept apart.
4. **ML detector** trained on Juliet and OWASP with leakage controls (held-out F1 0.60–0.91).
   On hand-written code it finds far fewer vulnerable functions; this domain shift is
   measured and documented.
5. **Neuro-symbolic engine** fusing rules, ML and knowledge-base sink conditions (`--engine
   neurosymbolic`).
6. **Dashboard:** a 9-class chart (8 original + Others), a class column, and a coverage
   caption per language.
7. **Python results unchanged:** OWASP F1 0.904 / 0.955 / 0.862. Tests: 658 passing.

## Changes on 22 November 2026 — security dataset, model evaluation and profiling

1. **Security dataset v1** (`python -m src.dataset.build`, `datasets/security_dataset/v1/`):
   23,131 samples and 774,960 lines in seven languages, 132 CWEs. Juliet 1.3 functions, OWASP
   BenchmarkPython, hand-labelled templates, and 91 long programs of 1,099–1,912 lines with 4,984
   planted vulnerabilities. Split 70/15/15 by group; no custom sample failed validation.
2. **Reproducible ML pipeline** (`python -m src.vulnml.pipeline`): hyperparameters chosen on
   validation, one test score per language, configs and metrics saved with each model. These
   models replace the Juliet-only models of the previous entry (item 4); its fixture evaluation
   is archived in `outputs/vulnml/archive_juliet_only_models/`. Rust and COBOL models are small-n
   and are not used by the neuro-symbolic engine.
3. **Three engines on the same 7,006 test units:** F1 rule-based 0.759, ML 0.554,
   neuro-symbolic 0.772 (`outputs/eval/model_comparison.json`). Juliet in-scope and
   out-of-scope recall are reported separately; rule results on custom data are documented as
   not independent of rule development.
4. **Block-wise profiling** (`src/perf.py`, `python -m src.perfbench`) of every stage, with a
   timing pass and a tracemalloc / psutil memory pass, and a **Performance** page in the GUI
   (Comparison, Rule-Based, ML Model, Neuro-Symbolic and Pipeline tabs, live profile).
5. **Two slowdowns found by profiling and fixed with identical results:** COBOL taint analysis
   (about 100 s → 1 s per 1,300-line program) and ML evidence tokens (prediction 3.3× faster).
6. `python -m src.vulnml train/evaluate` now use the pipeline; the capability captions read the
   saved metrics instead of hard-coded numbers. SEC007 (no CWE) is excluded from the dataset.
7. Documentation: [SECURITY_DATASET_AND_EVALUATION.md](SECURITY_DATASET_AND_EVALUATION.md), an
   updated architecture diagram, the final report, and the screenshots B24–B29 and A21–A23.
   Tests: 680 passing.
