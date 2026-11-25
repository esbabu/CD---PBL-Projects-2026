TITLE:
SecCodeDiag IDE: A Zero-Open-Port Desktop IDE, Five-Layer Static Security Engine, and Multi-Agent AI Framework for C++ Syntax Error Classification and Verified Code Repair

FILE CONTENTS:

1. Source Code: SecCodeDiag_IDE_Source_Code.zip
Complete source code of SecCodeDiag IDE, an installable Electron + Monaco desktop IDE with a Python analysis engine. It communicates over stdio JSON-RPC 2.0,
so no network ports are opened. It contains:
- desktop/ : Electron + Monaco Editor front end (main process, RPC client in desktop/src/main/rpc_client.ts, Side-by-Side Diff view, command palette, DPAPI settings).
- engine/ : Python engine (rpc_main.py, service_layer.py, proposal_store.py), the 5-layer static security engine (sink_detector.py, cpp_tokenizer.py, scope_analyzer.py,
layer_b_analyzer.py, taint_tracker.py, cfg_analyzer.py, concurrency_analyzer.py, resource_table.json), and the compiler front end (lexer.py, cpp_parser.py, structural_validator.py, ast_features.py).
- Security and ML modules: assessment_engine.py, security_rules.py (107 rules, 81 CWEs), compiler_sandbox.py, and the Random Forest model files (model.pkl, scaler.pkl, label_encoder.pkl).
- Test and benchmark files: tests/ (1040 Python tests, 70 desktop unit tests, test_desktop_security.py), vulnerable_100.cpp, vuln_corpus.cpp, safe_samples.cpp.

2. Documentation: End_Project_Report.docx
Final technical report (Compiler Design PBL, end-project phase). It covers the problem statement, the contributions over the mid-project version,
the architecture, the 5-layer static security engine, the 3-layer cryptographic fix approval, the experimental results (detection on vulnerable_100.cpp improved
from 13.0% to 99.0%; all 13 syntax-error categories detected in one run; 114 security audit scenarios passed), the conclusion and references.
The appendix has annotated screenshots (Figs. A1-A12).

4. Screen Recording: Screen_Recording.mp4
Demonstration of SecCodeDiag IDE running as a desktop application. It shows the native menu bar and file operations,
Example Preset 1 (13 simultaneous syntax errors detected and fixed, 13 to 0), the Monaco Side-by-Side Diff with the approval gate,
Example Preset 2 (security vulnerabilities in vulnerable_100.cpp) with the live security scan and filters, the optimization example,
the command palette, the performance dashboard and the DPAPI settings modal.
