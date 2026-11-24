# Compiler Error Explainer Using AST & NLP
### Compiler Design — Project-Based Learning (PBL) 2026

**Roll Number:** 25CSB1A30  
**Student Name:** Jaisingh Saini  
**Course:** Compiler Design (CS4XX)  
**Department:** Department of Computer Science and Engineering  
**Institution:** National Institute of Technology Warangal (NITW)  

---

## 🔗 Project Media & Google Drive Archive (Exceeding File Size Limit)

> **Important Note as per Guidelines:**  
> High-definition screen recording videos exceed GitHub's maximum file size limit (100 MB). All screen recordings and full project archives have been uploaded to Google Drive with access enabled for NITW emails and link holders:
> 
> **Google Drive Link:** [https://drive.google.com/drive/folders/1GwzyWYIhGYWxmBAybFoJDnLqv8NrE0vO?usp=share_link](https://drive.google.com/drive/folders/1GwzyWYIhGYWxmBAybFoJDnLqv8NrE0vO?usp=share_link)

### Included in Google Drive Folder:
1. **`Screen Recording.mov` (489 MB):** Comprehensive demonstration of the PyQt6 GUI, AST visualizer, 9-phase meta-compiler pipeline, automated healing loop, static security analysis pass, and CodeCarbon energy telemetry.
2. **`VSCode Extension Integrated Project Screen Recording.mp4` (100 MB):** End-to-end demonstration of the integrated VS Code Extension, real-time in-editor diagnostics, one-click quick fixes, interactive syntax tree explorer, and Deep Analytics Webview dashboard.
3. **Full Project Archive:** Complete project files, reports, and original datasets.

---

## 📁 Repository Structure and Uploaded Files Description

| File / Directory | Description |
| :--- | :--- |
| **`Readme.md`** | Project submission document detailing student credentials, file descriptions, Google Drive links, and setup instructions. |
| **`Compiler Error Explainer Integrated Report.pdf`** | Comprehensive integrated final lab report (25 MB) detailing theoretical background, compiler pipeline mapping, ML models, security gates, and ablation benchmarks. |
| **`Compiler Error Explainer with NLP.pdf` / `.pages`** | Project documentation reports in PDF and Apple Pages formats. |
| **`PBL_Report.md`** | Academic lab report in Markdown format structured for PBL evaluation. |
| **`DOCUMENTATION.md`** | Technical system documentation covering module APIs, classes, and architectural specifications. |
| **`project_explanation.md`** | High-level architectural walkthrough of core compiler concepts, IR design, and ML pipeline. |
| **`src/`** | **Core Source Code**: Lexical scanner, AST parser, ML error classifier, 6-gate safety verifier, iterative auto-healer, PyQt6 GUI, and energy telemetry. |
| **`vscode-extension/`** | **VS Code Extension**: Production-ready extension with TypeScript source code, package manifests, and pre-compiled `.vsix` installer (`compiler-error-explainer-0.1.0.vsix`). |
| **`data/`** | Pre-trained Machine Learning model weights (`model.pkl`, `vectorizer.pkl`), training datasets, and diagnostic mappings. |
| **`benchmark/`** | Verification suites, ablation studies (`ABLATION_GATES.csv`, `BENCHMARK_RESULTS.csv`), adversarial attack benchmarks, and automated benchmarking scripts. |
| **`tests/`** | Automated unit tests, integration tests, and verification suites covering compiler diagnostic parsing, security checks, and healing gates. |
| **`test_cases/` & `all_test_cases/`** | Curated C++ test files spanning syntax errors, type system violations, semantic faults, memory corruption, and security vulnerabilities. |
| **`tools/`** | Utility and evaluation scripts for dataset preparation, model training, metric evaluation, and security testing. |
| **`config.yaml`** | System configuration parameters, compiler flags, ML thresholds, and security rules. |
| **`requirements.txt` & `requirements-dev.txt`** | Python dependencies required to run the application, GUI, ML models, and development tools. |
| **`run.sh`** | Quick-start shell script to launch the application. |

---

## 🚀 Overview & Key Features

Traditional compiler diagnostics often provide technical, terse messages without explaining the root cause of a programming error or how to remediate it. This project designs and implements an intelligent post-compilation pipeline layered atop the standard `g++`/`clang++` toolchain.

### Key Capabilities:
1. **Compiler Diagnostic Normalization & Lexing:** Intercepts raw GCC/Clang diagnostic streams, tokenizes errors using a finite automaton regex scanner, and normalizes them into structured Intermediate Representation (IR).
2. **Machine Learning Error Classification:** Uses a trained Logistic Regression classifier with TF-IDF n-gram feature extraction across 10 semantic error categories with fallback mechanisms.
3. **Iterative Bounded Auto-Healing:** Applies source-to-source peephole rewrite rules in a bounded iterative convergence loop (up to 10 iterations) with fixed-point tracking.
4. **Abstract Syntax Tree (AST) & Call Graph Exploration:** Integrates Clang LibTooling AST extraction, interactive AST tree navigation, and control-flow/call-graph visualization.
5. **6-Gate Sandboxed Safety Verification:** Multi-tier pre- and post-compilation gates protecting against memory corruptions (buffer overflows, format string vulnerabilities, command injection) and malicious patch smuggling.
6. **Energy & Carbon Telemetry:** Tracks execution-time kilowatt-hour energy usage and CO₂ emission metrics per compilation attempt powered by CodeCarbon.
7. **Dual Interface:** Full desktop GUI (PyQt6) and industrial Visual Studio Code Extension with an embedded analytics Webview dashboard.

---

## 🛠️ Technology Stack

* **Programming Languages:** Python 3.10+, C++17, TypeScript / JavaScript
* **GUI & Visualization:** PyQt6, QCustomPlot / Matplotlib, Graphviz
* **Machine Learning & NLP:** scikit-learn, TF-IDF Vectorizer, NumPy, Google Gemini & Groq LLM bridges
* **Static Analysis & Compilers:** GCC (`g++`), Clang / LLVM (`clang++`), `clang-format`
* **Telemetry & Testing:** CodeCarbon, psutil, pytest

---

## 💻 Setup & Installation Instructions

### Prerequisites
* GCC / G++ supporting C++17
* Clang / LLVM (optional, for AST dumping and formatting)
* Python 3.10 or higher

### Installation
```bash
# 1. Create and activate a Python virtual environment
python3 -m venv .venv
source .venv/bin/activate    # On Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Running the Desktop GUI
```bash
python -m src.main
# or using the quick-launch script:
chmod +x run.sh && ./run.sh
```

### Running Automated Test Suites
```bash
pytest tests/
python benchmark/run_benchmark.py
```

### Installing the VS Code Extension
Open Visual Studio Code, navigate to Extensions (`Ctrl+Shift+X` / `Cmd+Shift+X`), select **"Install from VSIX..."** from the top right menu (`...`), and select:
`vscode-extension/compiler-error-explainer-0.1.0.vsix`
