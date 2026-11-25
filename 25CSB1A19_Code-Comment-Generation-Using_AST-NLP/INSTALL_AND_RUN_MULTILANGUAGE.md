# Install and run the updated multi-language project

## 1. Extract and open the project

1. Extract the ZIP file.
2. In VS Code, open the inner `TOC.PRO` folder — the folder that contains `run_gui.py`.
3. Open Terminal from that folder.

## 2. Install the Tree-sitter language pack

Run:

```powershell
py -m pip install -r requirements-multilang.txt
```

Alternatively, double-click `install_multilang_support.bat`.

The first time a language parser is used, Tree-sitter may need to download its grammar and cache it locally. Connect to the internet for this first use. Once cached, the grammar can be reused locally.

## 3. Start the application

```powershell
py run_gui.py
```

The current project already depends on PyQt6 and the ML libraries for its existing Python workflows. Use the same Python environment in which the existing Comment Gen Pro application was running.

## 4. Generate comments for each language

1. Open **Generator**.
2. Select a language from the Language dropdown or choose a file using **Pick File**.
3. Paste or load the source code.
4. For Python, select Rule-Based, ML-Based or Neurosymbolic.
5. For C, C++, Java, JavaScript and TypeScript, the Generator uses structural Rule-Based comments.
6. Click **Generate & Attach Comments**.
7. Open **Agentic Security**. The original source and language are handed over automatically.

## 5. Read the malware result box

The result box is at the top of Agentic Security:

- **NO MALWARE INDICATORS FOUND** — no configured static behaviour combinations matched.
- **SUSPICIOUS BEHAVIOUR DETECTED** — at least one configured persistence-related indicator needs review.
- **POTENTIALLY MALICIOUS BEHAVIOUR DETECTED** — one or more high-risk behaviour combinations matched.
- **MALWARE ASSESSMENT INCONCLUSIVE** — no usable source was provided or the scan could not complete.

For a finding, the box shows the rule, severity, source file, line or line range, function where it could be inferred, evidence, explanation and recommendation.

The scanner never executes the submitted program. A clean result does not prove malware-free status. The current version is static analysis; it is not a full malware lab, sandbox, malware-family classifier, or dynamic runtime monitor.

## 6. Scope by language

Python retains the project's original AST/IR/CFG/DFA pipeline and the three comment engines. C, C++, Java, JavaScript and TypeScript receive syntax-tree-based rule comments and the cross-language static security/malware indicator checks. The T5-small model, Python CFG/DFA quality analysis and automatic secure-code rewriting are not generalized to every language in this build. Non-Python findings include location and remediation guidance for manual changes.

## 7. Run checks

```powershell
py -m compileall -q src run_gui.py
py -m pytest test_multilang.py tests/test_malware_detector.py tests/test_multilang_agent.py -q
py -m pytest -q --ignore=tests/test_basic.py
```

`tests/test_basic.py` also needs PyQt6 to be installed in the selected Python environment.
