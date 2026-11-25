# Step-by-Step Implementation — Screenshots

All screenshots were captured from real runs of the project (A1–A9 on 10 November 2026; A10–A17 and
all GUI screens B1–B19 on 18 November 2026, after the GUI rework; A10 and A15–A17 and B19 after the
fix-and-verify agent and rules SEC016–SEC018 were added; A10, A18–A20 and B20–B21 on 20 November
2026, after the 50-rule extension, the large-file corpus and the RAG were added; B22–B23 on 22 November
2026 after the multi-language extension; A10, A21–A23 and B24–B29 on 22 November 2026 after the
security dataset, model evaluation and profiling were added), on Windows 11 with a Python 3.12 virtual
environment, on a white background. The Python steps use
[`screenshots/sample_input.py`](screenshots/sample_input.py): a small Flask module with a loop,
a raised exception, a SQL query built by string concatenation, and a class with an unused
local variable. The Java, C and C++ steps use the sample files in `tests/inputs/multilang/`
(`Inventory.java`, `shapes.cpp`, `matrix.c`).

## Part A — Command line

| Step | Screenshot | What it shows |
|---|---|---|
| A1 | ![](screenshots/cli_01_input_file.png) | The input file to be documented. |
| A2 | ![](screenshots/cli_02_rule_based_run.png) | Rule-based run: 6 functions and 1 class found, 8 comments generated, IR built for 6 functions, 1 analysis finding, 1 security finding. |
| A3 | ![](screenshots/cli_03_rule_based_output.png) | Annotated output (rule-based): block comment plus a Google-style docstring with Args / Returns / Raises taken from the AST. |
| A4 | ![](screenshots/cli_04_neurosymbolic_run.png) | Same file with the neuro-symbolic engine (T5 model + rules). |
| A5 | ![](screenshots/cli_05_neurosymbolic_output.png) | Neuro-symbolic output: ML summary *"Calculate the average of numbers."* used in *fused* mode (ML confidence 46 %), structured sections still from the AST. |
| A6 | ![](screenshots/cli_06_ir_dump.png) | Intermediate representation: three-address instructions in basic blocks (`entry`, `branch_0_true`, `loop_0_header`, …) with explicit successors. |
| A7 | ![](screenshots/cli_07_pattern_analysis.png) | Data-flow pattern analysis: P001 — `unused_discount` is assigned but never read. |
| A8 | ![](screenshots/cli_08_security_scan.png) | Security scan: SQL injection (SEC005, CWE-89) with the full source-to-sink trace across two functions and a fix suggestion. |
| A9 | ![](screenshots/cli_09_security_evaluation.png) | Security evaluation on the labelled fixtures: precision, recall, F1 and false-positive rate. |
| A10 | ![](screenshots/cli_10_test_suite.png) | Automated test suite: 680 tests passed, 0 failed (22 Nov 2026). |
| A11 | ![](screenshots/cli_11_java_run.png) | Java input (`tests/inputs/multilang/Inventory.java`): language detected from the extension, 7 methods and 3 classes found, 10 Javadoc comments generated. |
| A12 | ![](screenshots/cli_12_java_output.png) | Annotated Java: Javadoc with `@param`, `@return`, `@throws IOException`, generic types inside `{@code …}`, and a complexity note above the complex method. |
| A13 | ![](screenshots/cli_13_cpp_output.png) | Annotated C++ (`shapes.cpp`): Doxygen comments for a constructor that throws `std::invalid_argument`, a method, and a template function with a default argument. |
| A14 | ![](screenshots/cli_14_compile_check.png) | The annotated Java, C++ and C files still compile with `javac`, `g++` and `gcc`. |
| A15 | ![](screenshots/cli_15_agent_fix.png) | Fix-and-verify agent on `tests/security_fixtures/agent/mixed_demo.py`: SQL injection, command injection, unsafe YAML, MD5 and XXE fixed and verified by the analyzer; the SSRF finding is left for a human; unified diff of the patched copy (the input file is not modified). |
| A16 | ![](screenshots/cli_16_new_rules.png) | The three rules added last: SSRF (SEC016), open redirect (SEC017) and XXE (SEC018) on attack files 13–15 in `tests/inputs/attacks/`; only the vulnerable function of each file is reported, the version with a host check or defusedxml is not. |
| A17 | ![](screenshots/cli_17_agent_evaluation.png) | Agent evaluation (`python -m src.agent.evaluate`): per rule, findings, attempted, fixed and verified, left for a human, and rejected patches, on the labelled fixtures and all 1230 OWASP cases. |
| A18 | ![](screenshots/cli_18_rules50.png) | Rules from the 50-rule extension on `tests/inputs/demo_rules50.py`: LDAP injection (SEC019), XPath injection (SEC020), regex injection (SEC024), trust boundary (SEC028), cookie flags (SEC044), each with location, CWE, confidence reason and fix. The file reports exactly its 12 marked lines. |
| A19 | ![](screenshots/cli_19_large_corpus.png) | Large-file corpus: 106 tests passed over 50 files and 101,057 lines; every one of the 500 planted vulnerabilities found at its line, and nothing else reported. |
| A21 | ![](screenshots/cli_21_ml_pipeline.png) | `python -m src.vulnml evaluate`: for every language the train / validation / test counts, the hyperparameters chosen on validation, and the test precision, recall, F1, FPR, FNR and family accuracy (Rust and COBOL marked small-n). |
| A22 | ![](screenshots/cli_22_engine_comparison.png) | `make_tables.py comparison`: the rule-based, ML and neuro-symbolic engines on the same 7,006 test units — overall, by language, by source, Juliet recall inside / outside the rules' CWE scope, and exact (rule, line) results on the long test programs. |
| A23 | ![](screenshots/cli_23_block_profile.png) | `python -m src.perfbench --show`: end-to-end time, throughput, peak heap and bottleneck per language, and the share of measured time per block (data flow & taint is the overall bottleneck). |
| A20 | ![](screenshots/cli_20_rag.png) | RAG: knowledge-base contents (50 rule cards + 50 examples), a free-text query ranking the JWT rule first, and the retrieval evaluation on OWASP labels (recall@1 0.49, recall@5 0.81, chance 0.02). |

## Part B — Desktop GUI (`python run_gui.py`)

| Step | Screenshot | What it shows |
|---|---|---|
| B1 | ![](screenshots/gui_01_start_screen.png) | Start screen: Generator, Insights, ML Training, Security and Logs workspaces; engine choice, Language box and output folder at the top. |
| B2 | ![](screenshots/gui_02_file_loaded_neurosymbolic.png) | `sample_input.py` opened (Language: Python), neuro-symbolic engine selected. |
| B3 | ![](screenshots/gui_03_comments_generated.png) | After *Generate Comments*: annotated output beside the input with added lines highlighted (8 comments, 85 lines added); the badge shows 16.7 % unsafe, 1 issue. |
| B4 | ![](screenshots/gui_04_insights_ast_features.png) | Insights → AST Features: functions, parameters, types and complexity as a tree. |
| B5 | ![](screenshots/gui_05_insights_ast_graph.png) | Insights → AST Graph: module, imports, classes, functions and parameters (the graph fits itself to the window). |
| B6 | ![](screenshots/gui_06_insights_context_graph.png) | Insights → Context Graph: complexity and variables per function. |
| B7 | ![](screenshots/gui_07_insights_call_graph.png) | Insights → Call Graph: `user_page` calls `find_user`; nodes coloured by complexity, red border marks the security issue. |
| B8 | ![](screenshots/gui_08_insights_ir_dump.png) | Insights → IR Dump. |
| B9 | ![](screenshots/gui_09_insights_analysis_report.png) | Insights → Analysis Report (P001–P007 findings). |
| B10 | ![](screenshots/gui_10_insights_evaluation.png) | Insights → Evaluation: training-loss curve, BLEU-4 / ROUGE-L / exact-match bars, confidence-vs-quality scatter. |
| B11 | ![](screenshots/gui_11_security_workspace.png) | Security workspace: `find_user` scores 75 because of the SQL injection, so the module is 83.3 % safe / 16.7 % unsafe; charts and the findings table. |
| B12 | ![](screenshots/gui_12_ml_training_report.png) | ML Training workspace: presets and options, Start / Cancel, and the model card of the recorded training run (13,480 pairs, 3 epochs; BLEU-4 0.060, ROUGE-L 0.262, exact match 1 %). |
| B13 | ![](screenshots/gui_13_logs_workspace.png) | Logs workspace: output files and a JSON report viewer. |
| B14 | ![](screenshots/gui_14_java_generated.png) | A Java file opened: the *Language* box switches to Java, the ML comment engines are disabled (the T5 model is Python-only), and Javadoc is generated. |
| B15 | ![](screenshots/gui_15_cpp_generated.png) | A C++ file: Doxygen comments for the class, destructor and methods, with C++ syntax highlighting. |
| B16 | ![](screenshots/gui_16_cpp_ast_graph.png) | Insights → AST Graph for the C++ file: includes, classes, methods, functions and parameters. |
| B17 | ![](screenshots/gui_17_java_call_graph.png) | Insights → Call Graph for the Java file, coloured by cyclomatic complexity (`findLowStock` is complex). |
| B18 | ![](screenshots/gui_18_cpp_security_python_only.png) | *Historical (18 Nov 2026, before Step 14):* the Security workspace for a C++ file marked "Not scanned (Python only)". C++ is now scanned like every other language (see B22, B23). |
| B19 | ![](screenshots/gui_19_security_autofix.png) | Security workspace → *Auto-fix* on `mixed_demo.py`: the agent's live trace (plan / act / observe / decide with the four verification checks), "5 of 6 fixed and verified", and the original and patched code side by side with changed lines tinted; *Accept patch* puts the patched code in the editor and re-scans it (6 → 1 finding). |
| B20 | ![](screenshots/gui_20_security_rules50.png) | Security workspace on `demo_rules50.py`: 12 findings from the new rules (JWT, LDAP, XPath, TLS verification, DES, 1024-bit RSA, tar extraction, debug mode, regex, session, cookie, password logged); *Issue Types* now uses horizontal bars so rule IDs stay readable. |
| B22 | ![](screenshots/gui_22_security_java_9classes.png) | Security scan of a Java servlet: 18 findings with a *Class* column, the 9-class chart (8 original classes + Others), and the caption "Java: 33 rules detect 31 CWEs \| knowledge base documents 956 CWEs + 556 attack patterns". |
| B23 | ![](screenshots/gui_23_security_csharp_neurosymbolic.png) | The same view for an ASP.NET controller with the **Neuro-symbolic (rules + ML)** engine selected: 16 findings, each traced from the model-bound request parameter to its sink. |
| B24 | ![](screenshots/gui_24_performance_comparison.png) | **Performance** page, Comparison tab: the three engines on the same held-out units (accuracy, precision, recall, F1, FPR, FNR, unit count, mean latency), grouped bars, F1 by language and latency. |
| B25 | ![](screenshots/gui_25_performance_rules.png) | Rule-Based tab: per-language metrics, exact (rule, line) results on the long programs, confusion matrix, recall by vulnerability family and latency per language. |
| B26 | ![](screenshots/gui_26_performance_ml.png) | ML Model tab: the same views for the ML detector, plus each language's hyperparameters chosen on the validation split. |
| B27 | ![](screenshots/gui_27_performance_neurosymbolic.png) | Neuro-Symbolic tab: the fusion engine's metrics, confusion matrix and latency. |
| B28 | ![](screenshots/gui_28_performance_pipeline.png) | Pipeline tab: files, lines, mean and p95 time per file, lines per second, peak heap and bottleneck per language; stacked time per block; share of time per block. |
| B29 | ![](screenshots/gui_29_performance_live_profile.png) | *Profile editor code* on a Java servlet pasted in the Generator: every block with its calls, time and peak heap (149 lines, 18 findings, 22 comments). |
| B21 | ![](screenshots/gui_21_language_dropdown.png) | The language drop-down after the fix: a light list with dark text and a highlighted selection, also when Windows is in dark mode (before, the list could show dark text on a dark background). |

Notes on how the screenshots were taken:
- Console screenshots: the commands were run in a Windows console set to a white background;
  the console's light-grey background was converted to pure white afterwards.
- GUI screenshots: the real application window was driven by a script (file loaded, engine
  selected, button pressed, tabs opened) and each screen saved with Qt's own window capture.
  B12 shows the model card the workspace reads from the recorded training run
  (`outputs/training_report.json`, `outputs/eval_report.json`); training was not re-run for
  the screenshot.
