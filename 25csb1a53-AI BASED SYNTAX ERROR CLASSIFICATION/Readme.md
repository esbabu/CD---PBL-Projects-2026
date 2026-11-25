# AI Based Syntax Error Classification

**Roll Number:** `25CSB1A53` (`25csb1a53`)  
**Project Title:** AI Based Syntax Error Classification  
**Student:** Sanjay Cherukupelli (GitHub: `Sanjaycherukupelli`)  
**Faculty Guide:** Dr. E. Suresh Babu  
**Course:** Compiler Design — Project-Based Learning (CD PBL 2026), NIT Warangal  

---

## Project Overview

An AI-driven C++ syntax error classification, semantic inspection, CWE security auditing, and automated code repair studio with an interactive browser UI and Python backend.

---

## Uploaded Files & Descriptions

### 1. Documentation Reports
| File Name | Description |
| --- | --- |
| `mid part report.docx` | Mid-term evaluation report covering initial compiler front-end design, AST feature extraction, and Random Forest syntax error classification. |
| `end part report.docx` | End-term evaluation report covering complete system architecture, experiments, and final metrics. |
| `updated report.docx` | Final updates and new features report covering Random Forest + CodeBERT hybrid comparison, expanded 30+ CWE security scanner with line numbers, and live performance dashboard. |

### 2. Source Code & Web Application (`04_Web_Application/`)
| File Name | Description |
| --- | --- |
| `04_Web_Application/START_WEBSITE.bat` | Windows 1-click launcher that opens `http://localhost:8000` and starts the local Python server. |
| `04_Web_Application/server.py` | Python HTTP backend serving the IDE pages and analysis/telemetry endpoints. |
| `04_Web_Application/index.html` | Main web IDE interface for C++ code editing, syntax/semantic diagnostics, and CWE security scanning. |
| `04_Web_Application/stage_results.html` | Random Forest vs. CodeBERT vs. Hybrid stage comparison page. |
| `04_Web_Application/performance.html` | Performance and evaluation metrics dashboard. |
| `04_Web_Application/presentation.html` | Interactive HTML project presentation deck. |
| `04_Web_Application/lexer.py` | Lexical analyzer / C++ tokenizer. |
| `04_Web_Application/cpp_parser.py` | Error-tolerant recursive-descent C++ AST parser. |
| `04_Web_Application/ast_features.py` | Syntactic feature extraction module operating on AST representations. |
| `04_Web_Application/semantic_analyzer.py` | Symbol table and semantic/scope validation module. |
| `04_Web_Application/security_autoheal.py` | CWE vulnerability detector and automated repair helper. |
| `04_Web_Application/agentic_engine.py` | Reflection loop, eco/complexity profiler, and code optimization engine. |
| `04_Web_Application/predict.py` | ML prediction and syntax error classification inference script. |
| `04_Web_Application/train.py` | Training pipeline for the Random Forest model. |
| `04_Web_Application/model.pkl` | Trained Random Forest classifier model artifact. |
| `04_Web_Application/scaler.pkl` | Feature standardization scaler artifact. |
| `04_Web_Application/label_encoder.pkl` | Error category label encoder artifact. |
| `04_Web_Application/performance_data.json` | Recorded benchmark and evaluation metrics dataset. |
| `04_Web_Application/test_cases_70/` | 75 C++ test programs (`tc01`–`tc75`) covering syntax errors, semantic errors, CWE security vulnerabilities, and performance/complexity cases. |

### 3. Screenshots, Architecture Diagrams & Comparison Graphs (`03_Screenshots_and_Comparison_Graphs/`)
38 PNG/JPG visual assets, including:
- **UI Feature Screenshots:** `Fig_01_Editor_Interface_and_Buttons.png` through `Fig_13_Export_PDF_and_Toolbar_Actions.png`
- **Compiler Stage Visualizations (Tokens, AST, DAG, TAC):** `Fig_01_Page16_User_Interface.jpg` through `Fig_13_Page22_Simple_Program_TAC.jpg`
- **Architecture Diagrams:** `MID_PART_ARCHITECTURE_DIAGRAM.png`, `FINAL_PART_ARCHITECTURE_DIAGRAM.png`, `a4_architecture_diagram.png`, `architecture_diagram_v2.png`
- **ML Evaluation & Benchmark Graphs:** `MID_FIGURE_2_PERFORMANCE.png`, `MID_FIGURE_3_PERFORMANCE.png`, `FIGURE_2_PERFORMANCE_GRAPHS.png`, `FIGURE_3_TRAINING_AND_ROC_GRAPHS.png`, `confusion_matrix.png`, `feature_importance.png`, `codebert_benchmark_comparison.png`, `codebert_confusion_matrix.png`

### 4. Screen Recordings (Google Drive Link)
Because both demo screen recordings exceed GitHub's file size limit (>100 MB), they are hosted on Google Drive (accessible with NITW mail) per submission guidelines:

- **Before-update screen recording:** `Agentic AI — C++ Code Analysis Platform v2 - Google Chrome 2026-11-18 23-55-03.mp4` (214.04 MB)
- **After-update screen recording:** `after update scrren record.mp4` (150.92 MB)
- **Google Drive Link:** https://drive.google.com/drive/folders/1LakeVGXlYBNPjQEXVxwKN-BZ4PO0y3hB?usp=drive_link

---

## How to Run Locally

1. Open the `04_Web_Application` folder.
2. Double-click `START_WEBSITE.bat` (Windows), or run in a terminal:
   ```bash
   python server.py
   ```
3. Open `http://localhost:8000` in your browser:
   - Main Studio & CWE Security Scanner: `http://localhost:8000`
   - Random Forest vs. CodeBERT vs. Hybrid Comparison: `http://localhost:8000/stage_results.html`
   - Performance Dashboard: `http://localhost:8000/performance`
   - Presentation Slides: `http://localhost:8000/presentation`
