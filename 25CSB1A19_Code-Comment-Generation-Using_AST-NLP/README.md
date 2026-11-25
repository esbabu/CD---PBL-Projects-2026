# Code Comment Generator with Agentic Security Analysis

A desktop application for generating source-code documentation and performing local static analysis.

## Supported languages

The Generator supports Python, C, C++, Java, JavaScript and TypeScript source files.

| Language | Comment generation | Analysis |
|---|---|---|
| Python | Rule-Based, T5-small AST + NLP, Neurosymbolic | Python AST, IR/CFG/DFA, quality patterns, security checks and malware-behaviour indicators |
| C / C++ | Tree-sitter structural Rule-Based comments | Cross-language static security patterns and malware-behaviour indicators |
| Java | Tree-sitter structural Rule-Based comments | Cross-language static security patterns and malware-behaviour indicators |
| JavaScript / TypeScript | Tree-sitter structural Rule-Based comments | Cross-language static security patterns and malware-behaviour indicators |

**Important model boundary:** The T5-small model and the existing Neurosymbolic generator are based on Python AST features. They are not applied to C/C++/Java/JavaScript/TypeScript. Those languages use structural Rule-Based comment generation.

## Install multi-language parsing support

From the project root, run:

```powershell
py -m pip install -r requirements-multilang.txt
```

Or double-click `install_multilang_support.bat`.

The parser package uses Tree-sitter grammars. A grammar that is not yet cached may be downloaded the first time it is used, so an internet connection may be needed for the initial parse. The application has a conservative declaration-scanner fallback if Tree-sitter or a grammar is unavailable; that fallback is less accurate and is identified in the generation report.

## Run the desktop application

```powershell
py run_gui.py
```

In the Generator workspace:

1. Pick a source file or paste source code.
2. Select the language in the Language selector (or use Auto Detect when a filename/clear syntax pattern is available).
3. For Python, select Rule-Based, ML-Based or Neurosymbolic generation.
4. For C, C++, Java, JavaScript and TypeScript, the application uses structural Rule-Based comments.
5. Click **Generate & Attach Comments**.
6. Open **Agentic Security**; the original source and language are transferred automatically.

## Python CLI

### Rule-Based generation

```bash
python -m src.main tests/inputs/complex_sample.py
```

### AST + NLP ML generation

```bash
python -m src.main tests/inputs/complex_sample.py --ml
```

`--ml` requires a trained model. Train it first from the ML Training workspace or run:

```bash
python -m src.main --train --epochs 1 --batch-size 2 --codesearchnet-max 20 --max-stdlib-files 10
```

## Comment-generation engines

- **Rule-Based:** Uses AST-derived facts and deterministic templates. It provides predictable output and does not require model inference.
- **ML-Based (Python):** Formats AST/context features and passes them to a trained `google-t5/t5-small` sequence-to-sequence model to generate a natural-language summary.
- **Neurosymbolic (Python):** Applies confidence-gated fusion between the ML summary and symbolic rules, then assembles structured Args/Returns/Raises content from AST facts.

## Local Agentic Security

The Agentic Security workspace receives the original source code and language from Generator without a second copy/paste. It coordinates local parsing, security checks, available quality checks, malware-behaviour indicator correlation, risk prioritization and report generation.

The local agent does not need an OpenAI API key. Python findings can receive selected deterministic secure rewrites. For non-Python languages, the current version provides issue locations and remediation guidance but does not automatically rewrite source code.

## Malware-behaviour assessment

The malware detector performs static source inspection and correlates combinations such as:

- encoded payload plus dynamic execution;
- downloaded content plus execution;
- sensitive-file access plus outbound transfer;
- startup/persistence changes;
- file traversal combined with encryption and destructive file operations;
- encoded hidden commands combined with process launch.

The Agentic Security screen displays a result box with the assessment, rule ID, affected line or line range, evidence and recommended action. The source code is never executed by this scanner. A result reading **NO MALWARE INDICATORS FOUND** means that the configured indicator combinations were not found; it is not a claim that no malware exists.

A clean result means only that the configured static indicators were not found. It does **not** prove that a program is malware-free. The current project does not include a dedicated malware-family classifier, dynamic sandbox, process monitor or threat-intelligence integration.

## Code quality and program analysis

The Python pipeline includes AST feature extraction, context analysis, an intermediate representation, CFG/DFA analysis, seven documented quality-pattern checks, and twelve documented security anti-pattern categories. The enhanced Insights dashboard classifies functions as Good (zero warning/error findings), Medium (one or two), or Poor (three or more). These categories summarize configured findings; they are not universal correctness or security scores.

## Tests

Run the cross-language and malware tests:

```powershell
py -m pytest test_multilang.py tests/test_malware_detector.py -q
```

Run the non-GUI regression suite:

```powershell
py -m pytest -q --ignore=tests/test_basic.py
```

Compile the source files:

```powershell
py -m compileall -q src run_gui.py
```

The GUI tests in `tests/test_basic.py` require PyQt6 installed in the active Python environment.

vedio 
https://drive.google.com/drive/folders/1bQZPMF7K6wKTTtgb4PeeNwaGJtVUGMVE?usp=drive_link

