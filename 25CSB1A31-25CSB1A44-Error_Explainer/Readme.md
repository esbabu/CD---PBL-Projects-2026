# Compiler Error Explainer Using AST & NLP — Green Self-Healing Compiler

- **Roll Numbers:** `25CSB1A31`, `25CSB1A44`
- **Project Title:** Compiler Error Explainer Using AST & NLP (Green Self-Healing Compiler)
- **Course Repository:** `esbabu/CD---PBL-Projects-2026`
- **Source Project Repository:** `https://github.com/Ganesh-Revanth/toacd-pbl`

---

## Uploaded Files & Descriptions

### 1. Source Code (`src/`)
- `src/main.py` — CLI entry point for compilation, diagnostics, and auto-healing
- `src/gui.py` — Desktop GUI studio built with PyQt6
- `src/web/server.py` & `src/web/static/*` — Lightweight HTTP server and interactive web UI (`index.html`, `app.css`, `main.js`, `core.js`, `ast-graph.js`, `tree.js`, `pages-cpp.js`, `pages-evidence.js`, `pages-security.js`, `icons.js`, `fonts/*`)
- `src/agentic_compiler.py`, `src/agentic_worker.py`, `src/agent_tools.py` — Autonomous Gemini ReAct compiler repair loop and sandboxed tool wrappers
- `src/ai/llm_client.py` — Unified LLM provider wrapper with caching and guardrail enforcement
- `src/aai_guardrail.py` — Multi-layer Agentic AI (AAI) security guardrail (normalization, regex signatures, AST/token analysis, ML classifier, scope checks)
- `src/ast_extractor.py`, `src/cfg_extractor.py` — Clang AST JSON parser and LLVM IR Control Flow Graph (CFG) extractor
- `src/auto_healer.py`, `src/heal_loop.py`, `src/healing_suggester.py`, `src/diff_viewer.py` — Heuristic rule patcher, repair loop, diagnostic suggestions, and diff viewer
- `src/compiler_runner.py`, `src/error_parser.py`, `src/error_normalizer.py`, `src/error_classifier.py`, `src/error_explainer.py`, `src/common_errors.py`, `src/models.py`, `src/dataset_logger.py`, `src/prepare_training_data.py`, `src/build_dataset_from_tests.py` — Compiler execution, diagnostic normalization, ML error classifier, and plain-English explanations
- `src/energy_meter.py` — Process runtime, peak memory, and estimated energy/carbon meter
- `src/security_analyzer.py` — Static vulnerability scanner for C/C++
- `src/languages/` (`base.py`, `c.py`, `cpp.py`, `java.py`, `java_rules.py`, `python.py`, `python_rules.py`) — Multi-language compiler & safety adapters
- `src/evaluation/benchmark.py` — Evaluation runner helpers

### 2. Scripts & Generators (`scripts/`)
- `scripts/build_aai_corpus.py`, `scripts/simulate_aai_attacks.py` — AAI security corpus builder and ablation evaluation script
- `scripts/evaluate_complex_corpus.py`, `scripts/evaluate_large.py` — Complex (150–500 LOC) and large-program (2,000–5,000 LOC) guardrail evaluation suites
- `scripts/check_doc_numbers.py`, `scripts/demo_aai_attacks.py`, `scripts/demo_faculty_defense.py`, `scripts/demo_heal_worker.py` — Metric verification and demo scripts
- `scripts/generate_complex/*` & `scripts/generate_large/*` — Modular generators for benign, hard-negative, broken, and inert simulation corpora (`generate_all.py`, `make_attacks.py`, `utils.py`, etc.)

### 3. Tests & Benchmark Fixtures (`tests/`, `test_cases/`)
- `tests/` — Automated pytest suite (`test_aai_audit_log.py`, `test_aai_corpus.py`, `test_agentic_compiler_languages.py`, `test_agentic_compiler_security.py`, `test_ast_lines.py`, `test_benchmark.py`, `test_cfg.py`, `test_compiler_runner.py`, `test_doc_numbers.py`, `test_energy.py`, `test_guardrail_decisions.py`, `test_languages.py`, `test_large_attacks.py`, `test_large_corpus.py`, `test_llm_client.py`, `test_web_api.py`, `conftest.py`)
- `test_cases/` — Sample and benchmark source programs in C, C++, Python, and Java (`c/`, `cpp/`, `java/`, `python/`, `mini/`, `attacks/`, `complex/`, `large/`)

### 4. Data, Trained Models & Results (`data/`, `models/`, `results/`)
- `data/error_classifier.joblib`, `data/training_data.json` — Trained diagnostic error classifier and training data
- `data/aai/attacks.jsonl`, `data/aai/benign.jsonl` — Academic AAI security corpus
- `data/large/manifest_benign.jsonl`, `data/large/manifest_broken.jsonl`, `data/large/manifest_attacks.jsonl` — Large-program evaluation manifests
- `models/aai_injection.joblib` — Trained AAI prompt/patch injection classifier
- `results/` — Benchmark CSVs, Markdown evaluation reports (`benchmark_summary.md`, `complex_benchmark.md`, `aai_metrics.md`, `large_benchmark.md`, `large_misses.md`), and charts (`aai_roc.png`, `aai_pr.png`, `results/large/*.png`)

### 5. Documentation (`Project Documentation (Reports)/` & Root Docs)
- `Project Documentation (Reports)/Mid Evaluation Report.docx` — Mid evaluation project report
- `Project Documentation (Reports)/Final End Evaluation Report, Documentation.docx` — Final end evaluation report and full documentation
- `Green Self-Healing Compiler A Simple Guide.pdf` — Illustrated user guide
- `PBL_Report.md` — Project-Based Learning report
- `DOCUMENTATION.md` — Full system documentation
- `ARCHITECTURE_GUIDE.md` — Architectural reference
- `project_explanation.md` — Detailed design walkthrough

### 6. Screen Recordings (`Screen Recordings/`)
- `Screen Recordings/Mid.mp4` (`91.91 MB`) — Mid evaluation demo screen recording (uploaded in repository)
- **End Evaluation Screen Recording (`End.mp4`, `222.36 MB`):** Exceeds GitHub's `100 MB` single-file limit — Google Drive Link (NITW access): `[<ADD_GOOGLE_DRIVE_LINK_FOR_END_MP4_HERE>](https://drive.google.com/file/d/1PyuFA0qMSkKPOBW38A2d6_lBozMmcZ1P/view?usp=sharing)`

### 7. Configuration & Assets
- `requirements.txt`, `pytest.ini`, `.env.example`, `.gitattributes`, `.gitignore`, `.vscode/settings.json`, `assets/`, `end_eval_assets/`

---

# Green Self-Healing Compiler

## What It Is

The Green Self-Healing Compiler is an educational tool that explains and fixes programming errors.
A compiler is a program that translates human-written code into runnable machine instructions.
This project wraps standard compilers with automatic repair tools, energy meters, and security checks.

## What It Can Do

A diagnostic is a message emitted by a compiler about code problems.
The tool translates raw compiler messages into plain English explanations and repair tips.

A heuristic is a fast, practical rule for solving specific problems.
For common syntax errors, deterministic rules repair code in milliseconds without internet access.

A Large Language Model (LLM) is an artificial intelligence model trained on code.
The autonomous Gemini agent analyzes tricky multi-line bugs and tests candidate fixes iteratively.

A diff is a visual comparison displaying additions and deletions between two files.
The editor shows every proposed patch side-by-side so you can accept or reject it.

Energy telemetry means measuring processor run time and estimated electricity use during execution.
The system reports CPU seconds, peak memory, estimated Joules, and carbon footprint.

A Control Flow Graph (CFG) shows execution paths and branch directions through a function.
The web app renders interactive diagrams of basic blocks, branch conditions, loops, and syntax trees.

A guardrail is a safety filter that inspects prompts and code.
The built-in shield blocks prompt injections, hidden agenda patches, and system tampering.

## How It Works

1. You write or load code in the editor and click Compile or Run.
2. The backend runs the real compiler and collects any output error text.
3. An error classifier categorizes each problem into a known type.
4. The system attaches a plain explanation and fix suggestion to each error.
5. When healing is chosen, rules or the AI agent build a candidate patch.
6. The security guardrail inspects the patch to confirm it is safe to test.
7. The compiler verifies the patch, and you choose whether to accept the diff.

## Worked Example from a Real Run

Here is a real repair of `tc01_missing_semicolon.cpp`:

```cpp
#include <iostream>
int main() {
    std::cout << "Hello, World!" << std::endl
    return 0;
}
```

The compiler reports an expected semicolon before the return statement:

```text
main.cpp:4:5: error: expected ';' before 'return'
```

The system classifies this issue as a `missing_semicolon`.
The rule healer inserts `;` at line 3.
The compiler re-runs and finishes with code 0 in 1 attempt.

## Results

### Standard Multi-Language Benchmark (40 files total)

| Language | Fixtures | Clean Files | Broken Files | Rule Healed | AI Agent Healed |
|:---|:---|:---|:---|:---|:---|
| C++ | 10 | 2/10 (20.0%) | 8/10 (80.0%) | 50.0% (4/8) | 87.5% (7/8) |
| C | 10 | 2/10 (20.0%) | 8/10 (80.0%) | 100.0% (8/8) | 100.0% (8/8) |
| Python | 10 | 2/10 (20.0%) | 8/10 (80.0%) | N/A (Agent only) | 100.0% (8/8) |
| Java | 10 | 2/10 (20.0%) | 8/10 (80.0%) | N/A (Agent only) | 100.0% (8/8) |
| **Total** | **40** | **8/40 (20.0%)** | **32/40 (80.0%)** | **75.0% (12/16)** | **96.9% (31/32)** |

### Complex Multi-Fault Benchmark (134 files total)

| Evaluation Metric | Total Fixtures | Passed | Success Rate |
|:---|:---:|:---:|:---:|
| Clean Program Compiles | 58 | 58 | 100.0% (58/58) |
| Baseline Fault Check | 50 | 50 | 100.0% (50/50) |
| Rule-Based Repair (C++ & C) | 30 | 0 | 0.0% (0/30) |
| Agentic Gemini Repair | 50 | 30 | 60.0% (30/50) |
| Adversarial Attack Interception | 26 | 18 | 69.2% (18/26) |

### Security Shield Test Split (308 samples: 154 attacks, 154 benign)

| Metric | Samples | Result |
|:---|:---:|:---:|
| True Positives (Blocked Attacks) | 154 | 100 |
| False Positives (Clean Flagged) | 154 | 9 |
| True Negatives (Clean Allowed) | 154 | 145 |
| False Negatives (Missed Attacks) | 154 | 54 |
| Accuracy | 308 | 79.55% (245/308) |
| Precision | 109 | 91.74% (100/109) |
| Recall | 154 | 64.94% (100/154) |
| False Positive Rate | 154 | 5.84% (9/154) |
| Attack Success Rate (Shield ON) | 154 | 35.06% (54/154) |
| Attack Success Rate (Shield OFF) | 154 | 100.00% (154/154) |

## Limitations

1. "Fixed" means only that the code compiles, not that the logic is correct.
2. Energy values are estimates based on CPU runtime and default processor wattages.
3. The security shield is not perfect and missed 54 of 154 test attacks.
4. Heuristic rules cannot repair complex multi-fault programs, scoring 0.0% (0/30).
5. Autonomous AI healing requires internet access and a valid Gemini API key.
6. Control flow graphs are available only for C and C++ programs through Clang.

## Install and Run Commands

Clone the repository and install the dependencies:

```bash
git clone https://github.com/Ganesh-Revanth/toacd-pbl.git
cd toacd-pbl
pip install -r requirements.txt
```

Launch the web studio interface:

```bash
python src/web/server.py
```

Run the automated test suite:

```bash
python -m pytest tests -q
```

## Glossary

- **Compiler**: A program that translates source code into machine instructions.
- **Diagnostic**: An error or warning message emitted during compilation.
- **Abstract Syntax Tree (AST)**: A tree diagram showing the grammatical structure of code.
- **Control Flow Graph (CFG)**: A graph showing all paths code can take during execution.
- **Heuristic**: A fast practical rule used to solve common errors.
- **Large Language Model (LLM)**: An AI system trained on code to suggest fixes.
- **Guardrail**: A security filter that blocks unsafe commands or text.

## File Map

```text
src/agentic_compiler.py : Gemini agent repair loop
src/ast_extractor.py    : Clang AST JSON parser
src/auto_healer.py      : Rule-based C/C++ patcher
src/cfg_extractor.py    : Clang LLVM IR flow parser
src/energy_meter.py     : CPU time and energy model
src/error_classifier.py : ML diagnostic categorizer
src/error_explainer.py  : Plain-language diagnostic advice
src/security_analyzer.py: C/C++ static vulnerability scanner
src/aai_guardrail.py    : Multi-layer threat guardrail
src/languages/          : Language plugins (C++, C, Py, Java)
src/web/                : Lightweight HTTP API and web UI
test_cases/             : Benchmark fixtures and samples
tests/                  : Pytest automated test suite
results/                : Benchmark output logs and metrics
scripts/                : Evaluation and validation tools
```
