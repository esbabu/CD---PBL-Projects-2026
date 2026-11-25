# Compiler Error Explainer

Compiler Error Explainer is an educational C++/Python/Java source analyzer with a Flask dashboard. It combines compiler or interpreter diagnostics, plain-language explanations, static security checks, language-specific syntax healing, and visual views such as DFA traces and AST diagrams.

## Install

On Windows, create the project virtual environment and install the dependencies:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

The project also uses local compiler/toolchain executables. `start_app.ps1` checks for them at startup and warns when an optional tool is missing.

## Run

From the project directory, run:

```powershell
.\start_app.ps1
```

Open [http://localhost:5000](http://localhost:5000). The server binds to `127.0.0.1` with Flask debug mode disabled.

## Dashboard tabs

| Tab | Purpose |
|---|---|
| Overview & Metrics | Health summary and diagnostic counts |
| Diagnostics & NLP | Compiler/interpreter messages and explanations |
| Model Evaluation | Evaluation metrics and classifier charts |
| Agentic Auto-Heal | Rule-based repair attempts and diffs |
| Security Audit | Static security findings and flagged source lines |
| DFA Trace | Character-by-character lexer trace |
| AST Diagram | Source syntax tree visualization |
| Grammar Check | C++ toy-grammar result |
| Source Code | Uploaded source with finding highlights |

## Supported languages

| Language | Analysis and healing |
|---|---|
| C++ | Compiler diagnostics, rule-based healing, static security analysis, and optional behavioral tests |
| Python | Syntax/runtime diagnostics, rule-based healing, AST view, and static security analysis |
| Java | `javac` diagnostics, rule-based healing, tree-sitter AST view, and static security analysis |

## Limitations

- Auto-Heal uses rules; it is not a general-purpose or semantics-aware repair system.
- The ML classifier is trained on C++ GCC messages only. Python and Java use language-specific rule-based categorization.
- Runtime checks and behavioral tests are opt-in. High/Critical security findings block execution.
- Taint tracking is not built yet.
- The classifier feedback loop is not built yet.
