# Integrated Compiler Error Explainer & Self-Healing Pipeline
## Project Integration & Evaluator Guide

**Course:** Compiler Design (CS4XX)  
**Department:** Computer Science and Engineering  
**Institution:** NIT Warangal  
**Edition:** Integrated Unified Edition (VS Code IDE + Analytics Webview + 6-Gate Gauntlet)

---

## 1. System Architecture Overview

This project represents the complete unification of two specialized compiler tooling projects into a single, cohesive, production-grade development system.

```
+-----------------------------------------------------------------------------------+
|                           UNIFIED INTERFACE: VS CODE IDE                          |
|                                                                                   |
|  [ In-Editor Experience ]                                                         |
|  * Real-time compiler squigglies via vscode.languages.createDiagnosticCollection |
|  * Inline visual badges: ⚡ [Explainer: category] & 🛡️ [Security: CWE-xxx]        |
|  * Markdown Hover Cards: What Happened, Why It Happened, How To Fix, Suggestions |
|  * One-Click Quick-Fix Code Actions (Ctrl + .) with Cmd+Z Undo Support            |
|  * Standard Document Formatting Provider (Shift + Alt + F) via clang-format       |
|                                                                                   |
|  [ Embedded Webview Panel: Deep Analytics & Telemetry Dashboard ]                 |
|  * Interactive Clang AST Syntax Tree & Node Explorer                             |
|  * Control Flow Graph (CFG) & Function Call Graph Visualizers                     |
|  * Algorithmic Time & Space Big-O Complexity Analyzer                             |
|  * Real-Time CodeCarbon Power & CO₂ Emissions Telemetry Sparklines                |
|  * ML Classifier Confusion Matrix & Confidence Histograms                         |
|  * AI Second-Opinion Explainer & Healer (Google Gemini & Groq LLMs)               |
+-----------------------------------------+-----------------------------------------+
                                          |
                        (JSON Stdio / CLI & REST HTTP APIs)
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                                BRIDGE LAYER                                       |
|                                                                                   |
|  * tools/vscode_bridge.py: High-speed JSON bridge supporting:                     |
|      - Standard analysis: emit diagnostics, AST context, ML & AI predictions      |
|      - Auto-heal (--autoheal): multi-pass iterative repairs + unified diff         |
|      - Formatter (--format): clang-format + pure-Python AST beautifier            |
|  * src/web_server.py: Localhost REST API on port 8000 powering the Webview        |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                      INTELLIGENCE & ANALYSIS COGNITIVE ENGINE                     |
|                                                                                   |
|  * Diagnostic IR Normalizer & Regex Automaton Scanner                             |
|  * Supervised ML Classifier (Logistic Regression / SVM + TF-IDF)                  |
|  * Abstract Syntax Tree Extractor & Clang JSON Parser                             |
|  * Big-O Complexity Analyzer & Optimization Diff Generator                        |
|  * Live Energy & Carbon Telemetry (CodeCarbon + psutil)                           |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                        VERIFICATION GAUNTLET & DEFENSE                            |
|                                                                                   |
|  * Multi-Tier Auto-Healer: S0 (Compiler Fix-It), S1 (AST Rules), S2 (Heuristics)  |
|  * 20+ Specialized Bug Fixers: Buffer overflow, memory leak, UAF, types, etc.    |
|  * 6-Gate Sandboxed Verification Pipeline (src/verify_gates.py):                  |
|      - Gate 1: Recompilation success (g++ -std=c++17 returns exit code 0)         |
|      - Gate 2: Bounded AST diff size check                                        |
|      - Gate 3: Structural AST node invariant preservation                         |
|      - Gate 4: Zero CWE security regression check                                 |
|      - Gate 5: Differential execution runtime oracle                              |
|      - Gate 6: Patch AST security defense (anti-backdoor / anti-exfiltration)     |
|  * Agent Security Defense: Adversarial prompt injection & guard bypass defense    |
+-----------------------------------------------------------------------------------+
```

---

## 2. Quickstart: Running the Unified System

### 2.1 Installing Dependencies
```bash
# Python dependencies
pip install -r requirements.txt

# Compile TypeScript VS Code extension
cd vscode-extension
npm install
npm run compile
```

### 2.2 Using the VS Code Extension
1. Open VS Code in the integrated directory:
   ```bash
   code .
   ```
2. Press `F5` in VS Code to launch the **Extension Development Host**.
3. In the new VS Code window, open any C++ file (e.g. `test_cases/syntax_error.cpp` or `all_test_cases/cases/case01_syntax_and_grammar_errors.cpp`).
4. **Features in action:**
   - **Squigglies & Badges:** Red squigglies appear on lines with compiler diagnostics, accompanied by inline badges: `⚡ [Explainer: syntax_error]`.
   - **Rich Hover Cards:** Hover your mouse over the underlined error to read the structured **What happened**, **Why it happened**, and **How to fix it** cards.
   - **1-Click Auto-Heal:** Click the Lightbulb (`Ctrl + .`) or run `Compiler Error Explainer: Auto-Heal Current File` to repair the error automatically.
   - **Deep Analytics Webview:** Click the status bar button `$(graph) Analytics Dashboard` or editor title icon to open the interactive AST tree, CFG/Call graphs, Big-O complexity tables, and CodeCarbon energy monitor right beside your code!

---

## 3. Command Line & Standalone Interfaces

You can also run the system via CLI or standalone web server:

```bash
# 1. Test backend bridge diagnostics
python tools/vscode_bridge.py test_cases/syntax_error.cpp

# 2. Test auto-heal via bridge
python tools/vscode_bridge.py --autoheal test_cases/syntax_error.cpp

# 3. Test code formatting via bridge
python tools/vscode_bridge.py --format test_cases/syntax_error.cpp

# 4. Launch localhost Web IDE & Analytics Server (port 8000)
python src/web_server.py

# 5. Launch PyQt6 Desktop Workbench
python src/gui.py
```

---

## 4. Multi-Tier Safety Classification

| Safety Level | Tier Name | Description | Example Error Types |
| :---: | :---: | :--- | :--- |
| **S0** | **Tier 1: Compiler Fix-It** | 100% deterministic, compiler-suggested fix-its via `-fdiagnostics-parseable-fixits`. | Missing includes, exact header injections. |
| **S1** | **Tier 2: AST Syntactic Rules** | Structured repairs using AST type inference, scoped symbol tables, and syntax invariants. | Missing semicolons, unmatched braces, stream operator (`>>`/`<<`), const assignment. |
| **S2** | **Tier 3: Heuristic & Security Fixes** | Semantic mitigations and security vulnerability patches verified through runtime gates. | Buffer overflows (`gets` -> `fgets`), memory leaks (`free`), null dereference, division guards. |

---

## 5. The 6-Gate Sandboxed Verification Gauntlet

Every patch synthesized by the Auto-Healer must pass a strict gauntlet before it is presented to the user:

1. **Gate 1 (Recompilation Check):** The patched source must recompile under `g++ -std=c++17` with exit code 0.
2. **Gate 2 (Minimal Diff Check):** The diff must not exceed bounded modification thresholds ($S0 \le 4$, $S1 \le 8$, $S2 \le 20$ lines).
3. **Gate 3 (AST Preservation):** High-level structural invariants (function declarations, main signature) must be preserved.
4. **Gate 4 (Zero Security Regressions):** Static analysis must confirm zero newly introduced CWE vulnerabilities.
5. **Gate 5 (Runtime Oracle Correctness):** If an executable test oracle exists, the binary must run and produce expected output.
6. **Gate 6 (Patch AST Security):** Confirms the patch itself contains no adversarial backdoors, socket connections, or environment exfiltration (`getenv`).

---

## 6. Verification & Automated Test Results

To run the complete automated test suite across all subsystems:

```bash
# Run new integration tests
python -m pytest tests/test_vscode_bridge.py tests/test_tiered_autohealer.py tests/test_agent_security.py tests/test_code_formatter.py -v

# Run VS Code TypeScript tests
cd vscode-extension && npm test
```

**Results:**
- `tests/test_vscode_bridge.py`: **5 / 5 Passed** (100%)
- `tests/test_tiered_autohealer.py`: **5 / 5 Passed** (100%)
- `tests/test_agent_security.py`: **4 / 4 Passed** (100%)
- `tests/test_code_formatter.py`: **12 / 12 Passed** (100%)
- `vscode-extension/test/mapping.test.ts`: **7 / 7 Passed** (100%)
