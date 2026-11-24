# CD - PBL Project 2026: Compiler Error Explainer Using AST & NLP

**Course:** Compiler Design (CS4XX) — Project-Based Learning (PBL) 2026  
**Department:** Computer Science and Engineering  
**Institution:** National Institute of Technology Warangal (NITW)  
**Project Title:** Compiler Error Explainer Using AST & NLP (Green Self-Healing Compiler & Security Supervisor)  
**Group Members / Roll Numbers:**
- **25CSB1A23**
- **25CSB1A30**

---

## 📌 Submission & External Links

> [!IMPORTANT]
> **Google Drive Link (Demonstration Video & Project Files Archive):**  
> 🔗 [https://drive.google.com/drive/folders/1DvAUUXB0LUg7cYFccQ_y1XEqUwsoDByz?usp=sharing](https://drive.google.com/drive/folders/1DvAUUXB0LUg7cYFccQ_y1XEqUwsoDByz?usp=sharing)  
> *(As per PDF Guideline Note 1: Video file `Compiler explainer using AST and NLP.mp4` exceeds GitHub's 100 MB limit (106.5 MB), and is hosted on Google Drive with access granted to anyone with an NITW mail address).*

---

## 📂 File & Directory Manifest (Uploaded Contents & Descriptions)

In accordance with Step 2 of the submission guidelines, below is the detailed list and description of all files, source code, documentation, and resources uploaded in this folder:

| File / Folder Name | Category | Description |
| :--- | :--- | :--- |
| **`Readme.md`** | Overview & Manifest | Submission metadata, roll numbers, Google Drive links, file manifest, and full project usage documentation. |
| **`Compiler Error Explainer Using AST & NLP Report.docx`** | Documentation | Complete academic project report in Microsoft Word format. |
| **`PBL_Report.md`** | Documentation | Formal Markdown PBL project report detailing research, methodology, and theoretical background. |
| **`DOCUMENTATION.md`** | Documentation | In-depth engineering specification and component references. |
| **`STRUCTURE.md`** | Documentation | Complete architectural design, directory hierarchy, 9 engineering phases, and safety invariants. |
| **`project_explanation.md`** | Documentation | Conceptual breakdown of the self-healing compiler pipeline and NLP mapping. |
| **`docs/`** | Documentation & Schematics | Architectural schematics, flowcharts, evaluation charts, and visual figures. |
| **`src/`** | Source Code (Core Engine) | Core Python meta-compiler backend: lexical tokenization, AST parser, TF-IDF classifier, auto-healing engine, static security analyzer, and GUI. |
| **`tools/`** | Tools & Bridges | VS Code bridge interface (`vscode_bridge.py`), verification scripts, dataset processing, and benchmark harnesses. |
| **`vscode-extension/`** | IDE Integration | TypeScript VS Code extension source, package manifests, and compiled `.vsix` installer (`compiler-error-explainer-0.1.0.vsix`). |
| **`test_cases/`** | Test Suites | C++ test files spanning syntax errors, type errors, memory leaks, and CWE security scenarios. |
| **`all_test_cases/`** | Stress & Regression Tests | Scaled DSA stress test files (500, 2,000, 5,000, 10,000 lines), and 12-case end-to-end evaluation harness. |
| **`tests/`** | Unit Tests | Automated Pytest test suite covering guards, auto-healer, VS Code bridge, and AST verification. |
| **`benchmark/`** | Benchmarks | 242-file scientific benchmark suite, ablation study harnesses, and CSV benchmark logs. |
| **`security_bench/`** | Security Benchmarks | Adversarial attack cases and security evaluation datasets. |
| **`data/`** | Datasets & Models | Pre-trained dual-vectorizer Logistic Regression classifier (`model.joblib`), training datasets, and CWE knowledge bases. |
| **`assets/`** | Assets | Icons, favicons, and graphic assets for the desktop GUI and extension. |
| **`healed/`** | Samples | Auto-healed code outputs demonstrating multi-pass verification. |
| **`config.yaml`** | Configuration | Runtime configurations, timeouts, and compiler settings. |
| **`requirements.txt`** | Dependencies | Minimal production Python dependencies. |
| **`requirements-dev.txt`** | Dependencies | Developer, testing, and benchmarking dependencies. |
| **`my_test.cpp`** | Verification Demo | Multi-issue demo file containing syntax errors, CWEs, and quadratic Bubble Sort. |
| **`example.cpp`** | Sample Code | Sample C++ program for quick compiler testing. |
| **`Compiler explainer using AST and NLP.mp4`** | Screen Recording / Video | High-definition video demonstration of all features (~106.5 MB; hosted on Google Drive per Note 1). |

---

# Green Self-Healing Compiler & Security Supervisor
### Intelligent Compiler Error Explanation, AST-Driven Auto-Repair, Static Security Auditing & Algorithmic Optimization

[![C++ Standard](https://img.shields.io/badge/C%2B%2B-17-blue.svg)](https://en.cppreference.com/w/cpp/17)
[![Python Version](https://img.shields.io/badge/Python-3.10%2B-green.svg)](https://www.python.org/)
[![VS Code](https://img.shields.io/badge/VS%20Code-Extension%20Ready-purple.svg)](https://code.visualstudio.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An end-to-end, fully offline **meta-compiler intelligence platform** layered directly over standard GCC/Clang (`g++ -std=c++17`) toolchains. The system transforms cryptic compiler diagnostics into structured natural language explanations, audits source code against over 20 CWE security rules, automatically heals syntax and security vulnerabilities through a verified 5-gate loop, and optimizes algorithmic bottlenecks from $\mathcal{O}(n^2)$ down to $\mathcal{O}(n \log n)$.

> **Note on Architecture:** For the deep architectural design, directory tree, component engineering phases, and safety invariants, please refer to [STRUCTURE.md](STRUCTURE.md).

---

## Table of Contents
1. [Key Features](#key-features)
2. [Prerequisites & System Requirements](#prerequisites--system-requirements)
3. [Installation & Setup](#installation--setup)
4. [How to Run the Application](#how-to-run-the-application)
   - [Mode 1: Visual Studio Code Extension (Recommended)](#mode-1-visual-studio-code-extension-recommended)
   - [Mode 2: Standalone Desktop GUI (PyQt6)](#mode-2-standalone-desktop-gui-pyqt6)
   - [Mode 3: Command Line Interface (CLI)](#mode-3-command-line-interface-cli)
5. [How to Test Everything (Step-by-Step Verification)](#how-to-test-everything-step-by-step-verification)
   - [Verification Demo 1: Full-Feature Test Harness](#verification-demo-1-full-feature-test-harness)
   - [Verification Demo 2: Automated Unit & Regression Tests](#verification-demo-2-automated-unit--regression-tests)
   - [Verification Demo 3: 242-File Scientific Benchmark Corpus](#verification-demo-3-242-file-scientific-benchmark-corpus)
6. [Supported Compiler Errors & Security Rules](#supported-compiler-errors--security-rules)
7. [Repository File Organization](#repository-file-organization)

---

## Key Features

1. **Natural Language Compiler Diagnostics:**
   - Intercepts raw GCC/Clang errors and normalizes them into structured JSON Intermediate Representations.
   - Categorizes faults across 10 semantic classes using a trained dual-vectorizer (character + word n-grams) Logistic Regression classifier (**95.92% accuracy**).
   - Generates 4-part pedagogical feedback: *What Happened*, *Why It Happened*, *Suggestions*, and *Concrete Fix*.

2. **Static Application Security Testing (SAST):**
   - Scans code and AST for 20+ CWE and CERT C++ rules (e.g., CWE-369 division by zero, CWE-190 integer overflow, CWE-120/676 buffer overflows, CWE-134 format strings).
   - Simulates 89 adversarial attack vectors via an integrated Red-vs-Blue consensus defense engine.

3. **Multi-Tier Automated Program Repair (Auto-Heal All):**
   - **Tier 1:** Deterministic AST rules (missing semicolons, unbalanced braces, stream operators `<<` / `>>`).
   - **Tier 2:** Symbol table resolution (auto-inserting missing headers like `<iostream>`, Levenshtein-based typo corrections).
   - **Tier 3:** Security mitigations (ternary guards, bounded string copies via `strncpy`, integer bounds widening).
   - **5-Gate Safety Verification:** Guarantees that code is only saved if compiler errors decrease and zero new vulnerabilities are introduced.

4. **Algorithmic Big-O Static Analysis & Optimization:**
   - Traverses loop nesting depth and recursive trees to calculate asymptotic time and space complexities.
   - Detects quadratic bottlenecks ($\mathcal{O}(n^2)$ Bubble Sort) and automatically transforms them into optimal $\mathcal{O}(n \log n)$ implementations (`std::sort`), delivering **10x to 100x speedups**.

5. **Green Telemetry & Environmental Carbon Tracking:**
   - Real-time empirical hardware monitoring via `CodeCarbon`.
   - Computes execution energy consumption in Joules and greenhouse gas emissions in $\mathrm{gCO}_2\mathrm{eq}$.

6. **Deep Analytics & Code Quality Dashboard:**
   - Aggregates program metrics into a 0–100 **Code Health Score** and letter grade (Grade A through F).
   - Interactive AST visualizer and Second Opinion consensus panel.

---

## Prerequisites & System Requirements

Before running the application, ensure your workstation has the following installed:

| Requirement | Supported Version | Notes |
| :--- | :--- | :--- |
| **Operating System** | Windows 10/11, Ubuntu 20.04+, macOS | Tested across Windows and Linux |
| **C++ Compiler** | GCC / MinGW-w64 (`g++`) $\ge$ 9.0 | Must support `-std=c++17` |
| **Python** | Python $\ge$ 3.10 | Core engine runtime |
| **Node.js** *(Optional)* | Node.js $\ge$ 18.0 | Only required if modifying the VS Code extension source |
| **Visual Studio Code** | VS Code $\ge$ 1.80 | Required for the extension interface |

Verify compiler availability by running:
```bash
g++ --version
```

---

## Installation & Setup

### 1. Open the Project Folder
You can open the project in your terminal or directly inside VS Code:

* **VS Code UI Method:**
  1. Open Visual Studio Code.
  2. Click **File** > **Open Folder...** (or press `Ctrl+K Ctrl+O` on Windows, `Cmd+O` on macOS).
  3. Select the project directory (`compiler error explainer using AST and NLP integrated`).

* **PowerShell / Terminal Method:**
  ```powershell
  # Navigate into the project directory
  cd "path\to\compiler error explainer using AST and NLP integrated"
  ```

---

### 2. Configure Python Virtual Environment & Dependencies

It is recommended to use an isolated Python virtual environment:

#### Option A: Windows PowerShell
```powershell
# 1. Create virtual environment
python -m venv venv

# 2. Activate virtual environment
.\venv\Scripts\Activate.ps1

# (Note: If PowerShell displays a script execution policy error, run once:)
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 3. Upgrade pip and install all required runtime dependencies
pip install --upgrade pip
pip install -r requirements.txt

# (Optional: Install developer and benchmarking packages)
pip install -r requirements-dev.txt
```

#### Option B: Linux / macOS (Bash / Zsh)
```bash
# 1. Create virtual environment
python3 -m venv venv

# 2. Activate virtual environment
source venv/bin/activate

# 3. Upgrade pip and install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

---

## How to Run the Application

The system can be used through **three flexible modes**:
1. **Mode 1: Visual Studio Code Extension** (Interactive, 1-Click Buttons & Graphical Panels)
2. **Mode 2: Standalone Desktop GUI (PyQt6)** (Standalone Window with Code Editor, AST Visualizer, and Telemetry)
3. **Mode 3: Command Line Interface (CLI / PowerShell)** (Terminal-driven automation and scripting)

---

### Mode 1: Visual Studio Code Extension (Recommended)

The easiest, most interactive way to experience the tool is directly inside VS Code.

#### Step 1: Install the Extension (`.vsix`)
Choose either method below:

* **Method A: Direct in VS Code GUI (No Terminal Required)**
  1. In VS Code, click the **Extensions** icon on the left Activity Bar (or press `Ctrl+Shift+X` / `Cmd+Shift+X`).
  2. Click the **`...` (Views and More Actions)** three-dot menu at the top of the Extensions pane.
  3. Select **Install from VSIX...**.
  4. In the file picker, open the `vscode-extension/` folder inside this repository and select `compiler-error-explainer-0.1.0.vsix`.
  5. Click **Install**.
  *(Alternative shortcut: In VS Code's File Explorer pane on the left, right-click `vscode-extension/compiler-error-explainer-0.1.0.vsix` and select **Install Extension VSIX**).*

* **Method B: PowerShell / Terminal Command**
  ```powershell
  code --install-extension vscode-extension/compiler-error-explainer-0.1.0.vsix
  ```

---

#### Step 2: Open a Test File
Open `my_test.cpp` or `all_test_cases/master_test_all_features.cpp` in the editor.

---

#### Step 3: Use the Top-Right Editor Toolbar Buttons
Whenever an active C++ (`.cpp` or `.c`) file is open, look at the **top-right corner of the editor title bar** (next to the split editor icon). You will see dedicated action buttons:

| Button Icon | Action | What It Does |
| :---: | :--- | :--- |
| **▶** | **Run File** (`cee.run`) | Compiles the active file with `g++ -std=c++17` and executes the binary inside the VS Code integrated terminal. |
| **⚒** | **Compile Check** (`cee.compile`) | Compiles the file, parses diagnostics, extracts the Clang AST, and displays red error squiggles and rich hover cards. |
| **⚡** | **Auto-Heal All** (`cee.autoheal`) | Automatically repairs syntax errors (missing semicolons, unbalanced braces, stream operators) and patches security vulnerabilities across the file in a single click using the verified 5-Gate loop. |
| **🚀** | **Optimize Code** (`cee.optimize`) | Runs static Big-O asymptotic analysis, detects quadratic/cubic bottlenecks ($\mathcal{O}(n^2)$ Bubble Sort), and refactors them into optimal $\mathcal{O}(n \log n)$ algorithms (`std::sort`), providing 10x–100x speedups. |
| **📊** | **Analytics Dashboard** (`cee.openDashboard`) | Opens the rich **Compiler Deep Analytics & Code Quality** panel beside your code with real-time complexity evolution and telemetry. |
| **🛡️** | **Scan Security** (`cee.scanSecurity`) | Audits the file against 20+ CWE / CERT rules and runs the 89-vector red-vs-blue adversarial defense check. |
| **🎨** | **Format Code** (`cee.format`) | Cleans and formats C++ code with AST-aware indentation. |

---

#### Step 4: Use the Analytics Dashboard Webview
When you click **📊 Analytics Dashboard**, an interactive webview opens side-by-side with your editor.

1. **Dashboard Top Header Buttons:**
   At the very top of the dashboard, you have quick-action buttons:
   * `[▶ Run File]`
   * `[⚒ Compile Check]`
   * `[⚡ Auto-Heal All]`
   * `[🚀 Optimize Code]`
   * `[🔄 Refresh]`

2. **Dashboard Interactive Tabs:**
   * **Code Quality & Distribution:** Overall health score (Grade A through F), active compiler error counts, and CWE vulnerability statistics.
   * **Big-O & Complexity:** Before-and-after complexity comparison (e.g., $\mathcal{O}(n^2) \to \mathcal{O}(n \log n)$), loop nesting depth analyzer, and redundant memory copy warnings.
   * **AST Visualizer:** Interactive tree hierarchy of Clang Abstract Syntax Tree nodes.
   * **Second Opinion:** Model-generated top-2 cause hypotheses and confidence percentages.
   * **Green Telemetry:** Real-time CodeCarbon hardware energy consumption in Joules, kWh, and environmental carbon emissions in $\mathrm{gCO}_2\mathrm{eq}$.

---

#### Step 5: Bottom Status Bar & Command Palette
You can also trigger all operations without the mouse:
* **Status Bar (Bottom):** Look at the bottom blue status bar for one-click shortcuts: `Run`, `Compile`, `Auto-Heal`, `Optimize`, `Analytics Dashboard`.
* **Command Palette (Keyboard Shortcut):**
  Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on macOS) and type:
  * `Compiler Error Explainer: Compile & Check Errors`
  * `Compiler Error Explainer: Auto-Heal All Errors & Security`
  * `Compiler Error Explainer: Optimize C++ Code (Big-O)`
  * `Compiler Error Explainer: Open Deep Analytics & AST Dashboard`
  * `Compiler Error Explainer: Compile & Run C++ File`

---

### Mode 2: Standalone Desktop GUI (PyQt6)

If you prefer running a standalone desktop window outside of VS Code:

* **PowerShell / Terminal:**
  ```powershell
  python src/main.py
  ```
* **Desktop GUI Capabilities:**
  * Dual-pane syntax-highlighted code editor with line numbers.
  * Direct Compile, Auto-Heal, and Run action buttons.
  * Interactive Clang AST tree visualization widget.
  * Function call graph renderer.
  * Real-time CodeCarbon energy graphs.

---

### Mode 3: Command Line Interface (CLI / PowerShell)

Every capability of the platform can be executed directly from PowerShell or Bash via `tools/vscode_bridge.py`:

```powershell
# 1. Run diagnostics, error explanations, and security scan:
python tools/vscode_bridge.py my_test.cpp

# 2. Run multi-pass automated healing (Auto-Heal):
python tools/vscode_bridge.py --autoheal my_test.cpp

# 3. Run algorithmic Big-O optimization:
python tools/vscode_bridge.py --optimize my_test.cpp

# 4. Generate JSON analytics dashboard data:
python tools/vscode_bridge.py --dashboard my_test.cpp

# 5. Format C++ source code cleanly:
python tools/vscode_bridge.py --format my_test.cpp
```

---

## How to Test Everything (Step-by-Step Verification)

To demonstrate the full capabilities of the platform to professors, examiners, or reviewers, follow these verification procedures:

### Verification Demo 1: Full-Feature Test Harness (Errors + CWEs + Big-O)

We provide a comprehensive test suite in `my_test.cpp` (and `all_test_cases/master_test_all_features.cpp`) containing deliberate syntax errors, security vulnerabilities, and an algorithmic bottleneck:

```
Test Component             Issue Injected                       Expected Resolution
-------------------------------------------------------------------------------------------------------------------
Compiler Error 1           Missing semicolon (int checkVal = 100) Auto-Heal inserts delimiter ';' cleanly.
Compiler Error 2           Inverted stream operator (cout >> ...) Auto-Heal corrects operator to 'cout << ...'.
Security Vulnerability 1   CWE-369 Division by Zero             Auto-Heal applies ternary guard (divisor != 0 ? ... : 0).
Security Vulnerability 2   CWE-190 Integer Overflow             Auto-Heal promotes calculation to 64-bit bounds.
Security Vulnerability 3   CWE-120/676 Unsafe strcpy            Auto-Heal replaces with bounded strncpy + null terminator.
Security Vulnerability 4   CWE-134 Format String (printf(msg))  Auto-Heal sanitizes to printf("%s", msg).
Algorithmic Bottleneck     O(n²) Quadratic Bubble Sort          Optimizer replaces with O(n log n) std::sort.
```

#### Verification Steps in VS Code:
1. Open `my_test.cpp` in VS Code.
2. In the top-right toolbar, click **⚒ Compile Check**:
   - The compiler flags the missing semicolon and stream operator.
   - Hover over the highlighted red squiggles to see natural language explanations (*What Happened*, *Why It Happened*, *How to Fix*).
3. In the top-right toolbar, click **📊 Analytics Dashboard**:
   - The dashboard opens showing **Code Health Score: Grade D/F**.
   - Red vulnerability badges show CWE-369, CWE-190, CWE-120/676, CWE-134.
   - The **Big-O & Complexity** tab flags **$\mathcal{O}(n^2)$ for quadraticBubbleSort**.
4. In the top-right toolbar (or inside the Dashboard), click **⚡ Auto-Heal All**:
   - Both compiler errors and all 4 security vulnerabilities are instantly repaired in-place!
   - Active compiler errors and security findings drop to **0**.
5. In the top-right toolbar (or inside the Dashboard), click **🚀 Optimize Code**:
   - The nested loop Bubble Sort is refactored into `std::sort`.
   - The Big-O panel updates with:
     $$\mathcal{O}(n^2) \xrightarrow{\quad\text{OPTIMIZED}\quad} \mathcal{O}(n \log n)$$
   - Confirms an estimated **10x to 100x speedup**!
   - Code Health Score upgrades to **Grade A**!
6. Click **▶ Run File**:
   - The healed and optimized code compiles and executes in the VS Code terminal with exit code `0`.

#### Equivalent Verification via PowerShell:
```powershell
# 1. Check initial diagnostics and CWEs:
python tools/vscode_bridge.py my_test.cpp

# 2. Automatically heal all syntax errors and security vulnerabilities:
python tools/vscode_bridge.py --autoheal my_test.cpp

# 3. Optimize quadratic bottleneck to O(n log n):
python tools/vscode_bridge.py --optimize my_test.cpp

# 4. Compile and run verified binary:
g++ -std=c++17 my_test.cpp -o my_test_run.exe
.\my_test_run.exe
```

---

### Verification Demo 2: Automated Unit & Regression Tests

Run the automated test suite across all parser, classifier, security, and healing modules:

* **In PowerShell / Terminal:**
  ```powershell
  # 1. Run core unit tests (all 22 tests pass):
  pytest tests/test_vscode_bridge.py tests/test_tiered_autohealer.py tests/test_code_formatter.py -v

  # 2. Run the 12-case comprehensive security and syntax suites:
  python all_test_cases/cases/run_all_cases.py
  ```

Expected output:
```text
All 12 test cases executed: 12 PASSED, 0 FAILED.
```

---

### Verification Demo 3: 242-File Scientific Benchmark Corpus

To replicate the empirical evaluation reported in academic papers:

* **In PowerShell / Terminal:**
  ```powershell
  python benchmark/run_benchmark.py
  ```
* **Evaluation Corpus:** 242 standardized C++ benchmark files across 10 error categories and NIST Juliet security cases.
* **Metrics Recorded:** Classification Accuracy (95.92%), Healing Success Rate (79.2%), Security Detection Recall (94.4%), and Mean Healing Latency (<150 ms).

---

## Supported Compiler Errors & Security Rules

### Compiler Error Categories
1. `syntax_error`: Missing semicolons, malformed control structures, mismatched parentheses.
2. `undeclared_variable`: Identifier not found in scope (enhanced with Levenshtein typo matching).
3. `type_error`: Incompatible assignments, pointer-to-integer conversions.
4. `stream_operator`: Inverted stream insertion/extraction (`<<` vs `>>`).
5. `missing_header`: Missing declarations for standard library symbols (`cout`, `vector`, `string`).
6. `missing_return`: Non-void functions without return statements.
7. `missing_brace`: Unbalanced curly braces or premature EOF.
8. `array_bounds`: Constant out-of-bounds array access.
9. `null_dereference`: Direct dereferencing of null pointers.
10. `visibility_error`: Accessing private/protected class members.

### Security Vulnerabilities (SAST & Adversarial Defense)
* `CWE-120 / CWE-121 / CWE-676`: Classic Buffer Overflow (`strcpy`, `strcat`, `sprintf`, `gets`).
* `CWE-134`: Uncontrolled Format String (`printf(buffer)` without format specifier).
* `CWE-190`: Integer Overflow and arithmetic wraparound in memory allocations.
* `CWE-369`: Divide by Zero in arithmetic computations.
* `CWE-416`: Use After Free.
* `CWE-476`: NULL Pointer Dereference.
* `CWE-78`: OS Command Injection via `system()` or `popen()`.

---

## Repository File Organization

| Path | Purpose |
| :--- | :--- |
| `src/` | Core Python meta-compiler backend (parsing, NLP, AST, SAST, healing, optimization, telemetry). |
| `tools/vscode_bridge.py` | JSON IPC interface connecting VS Code to the Python analytics backend. |
| `vscode-extension/` | TypeScript extension package, Language Server client, and Webview dashboard. |
| `all_test_cases/` | Extensive benchmarks including 500, 2,000, 5,000, and 10,000-line DSA stress tests. |
| `benchmark/` | Scientific evaluation scripts, ablation study harnesses, and CSV benchmark logs. |
| `data/` | Pre-trained classification model (`model.joblib`) and CWE signature databases. |
| `docs/` | High-resolution architectural schematics and evaluation charts. |
| `STRUCTURE.md` | Comprehensive architectural guide, engineering phases, and design choices. |

---
