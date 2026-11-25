# Code Comment Generator — AST + NLP

This project generates comments and docstrings from the syntax tree of the code.
It supports **Python, Java, C#, C, C++, Rust and COBOL** (see [Other languages](#other-languages-java-c-c),
[docs/MULTILANG_SECURITY.md](docs/MULTILANG_SECURITY.md) and, for the dataset, model comparison and profiling,
[docs/SECURITY_DATASET_AND_EVALUATION.md](docs/SECURITY_DATASET_AND_EVALUATION.md)).
For Python there are three engines:

- `Rule-Based` (deterministic AST analysis)
- `AST+NLP ML` (model trained on structured AST features -> natural-language docstrings)
- `Neurosymbolic` (the ML summary, used only when its confidence is high enough, plus rule-based sections)

It also contains a static **security analyzer** with **64 rules** for all seven languages: taint
analysis over a real IR/CFG, memory-safety analysis for C/C++, and syntax rules. There are three
detection engines (rule-based, ML, neuro-symbolic) and a 1,512-entry security knowledge base
(MITRE CWE + CAPEC + NIST SARD Juliet examples) behind the RAG guidance. The analyzer runs
independently of comment generation,
a **fix-and-verify agent** that patches findings and re-checks every patch, and a small offline
**RAG** system that retrieves fix guidance — see [Security analysis](#security-analysis),
[SECURITY_ANALYSIS.md](SECURITY_ANALYSIS.md) and
[docs/SECURE_AGENTIC_AI_AND_RAG.md](docs/SECURE_AGENTIC_AI_AND_RAG.md).

| At a glance | |
|---|---|
| Languages analysed (IR, CFG, data flow, taint, rules) | Python, Java, C#, C, C++, Rust, COBOL |
| Security rules | 64 (Python 50, Java 33, C# 35, C 27, C++ 29, Rust 22, COBOL 8) |
| Detection engines | rule-based; ML (test F1 Java 0.88, C# 0.82, C 0.83, C++ 0.64, Python 0.81; Rust and COBOL small-n); neuro-symbolic fusion |
| Security dataset v1 | 23,131 samples, 774,960 lines, 7 languages, 132 CWEs; 91 long programs (1,099–1,912 lines) with 4,984 planted vulnerabilities; 70/15/15 split by group |
| Engines on the same 7,006 test units | F1 rule-based 0.759, ML 0.554, neuro-symbolic 0.772 ([details](docs/SECURITY_DATASET_AND_EVALUATION.md)) |
| Block-wise profiling | every stage timed and memory-profiled; `python -m src.perfbench`; GUI Performance page |
| Security knowledge base | 1,512 entries (956 CWE + 556 CAPEC), 566 with code examples; 53 CWEs detected |
| Multi-language fixtures | 7 realistic programs, 83 hand-marked vulnerabilities: all found, 0 false positives |
| Automated tests | 680, all passing (`python -m pytest`) |
| Large-file corpus | 50 files of ~1,800–2,400 lines (101,057 lines), 500 planted vulnerabilities + 500 safe twins: all 500 found, 0 false positives |
| OWASP BenchmarkPython | F1 0.904 on the 8 original categories (unchanged); 0.955 on redirect/XXE; 0.862 on LDAP/XPath/trust-boundary/secure-cookie |
| Agent on OWASP | 130 of 164 attempted findings fixed and verified, 0 patches rejected |

## Setup

> **The trained model is not in this repository.** `outputs/model/` is listed in
> `.gitignore` (checkpoints are hundreds of MB), so **every fresh clone must train
> once** before `--ml` or `--neurosymbolic` will work. See
> [Troubleshooting](#troubleshooting) if you hit the "No trained AST+NLP model found" error.

### 1. Use Python 3.11 or 3.12 — not 3.14

PyTorch publishes no wheels for Python 3.14, so `pip install torch` fails outright
there. Check what you have:

```bash
py -0p
```

Create the virtual environment with a supported interpreter:

```bash
py -3.12 -m venv .venv
```

### 2. Install dependencies

With an NVIDIA GPU (install the CUDA build of torch *first*, then the rest):

```bash
.venv/Scripts/python.exe -m pip install torch --index-url https://download.pytorch.org/whl/cu121
.venv/Scripts/python.exe -m pip install -r requirements.txt
```

CPU-only (slower training, everything still works):

```bash
.venv/Scripts/python.exe -m pip install -r requirements.txt
```

### 3. Train once

```bash
# Smoke test — a few minutes, proves the pipeline end to end.
.venv/Scripts/python.exe -m src.main --train --quick

# Real run.
.venv/Scripts/python.exe -m src.main --train \
  --codesearchnet-max 8000 --max-stdlib-files 600 --epochs 3 --batch-size 8
```

The checkpoint lands in `outputs/model/ast_model/`. The CLI and the GUI both read
from that one location.

---

### Optional: install as a package

```bash
pip install -e .            # rule-based engine + security analyzer (standard library only)
pip install -e .[gui]       # + desktop app
pip install -e .[all]       # + ML training/inference and pytest
```

This adds the commands `code-comment-gen`, `code-comment-security` and
`code-comment-gen-gui`. On Windows the examples below work the same with
`.venv/Scripts/python.exe` in place of `python`.

---

## Desktop app

```bash
python run_gui.py
```

Six pages: **Generator** (open or drop a file, pick an engine, view the annotated output
with added lines highlighted, copy or save it), **Security** (scan the editor code or a
whole folder without generating anything, read the source-to-sink evidence, double-click a
finding to jump to its line), **ML Training** (presets, progress, cancel), **Insights**
(AST, call graph, IR, pattern report, evaluation charts), **Performance** (dashboards for the
rule-based, ML and neuro-symbolic engines; block-wise time, memory and throughput; live
profile of the editor code) and **Logs**. Full guide:
[docs/GUI.md](docs/GUI.md).

---

## Current ML Architecture

The active ML pipeline is centered on `src/ml/`:

- `ast_feature_formatter.py` — serializes extracted AST/context features into model input text
- `ast_dataset_builder.py` — builds `(input_text, target_text)` training pairs from:
  - CodeSearchNet Python
  - Python stdlib fallback
- `ast_comment_model.py` — T5-based generator used for AST+NLP comment generation
- `trainer.py` — end-to-end training/evaluation/report saving
- `evaluator.py` — BLEU-4 / ROUGE-L / exact-match metrics

## CLI Usage

### 1) Train AST+NLP model

```bash
python -m src.main --train
```

Useful tuning flags:

```bash
python -m src.main --train \
  --epochs 1 \
  --batch-size 2 \
  --codesearchnet-max 20 \
  --max-stdlib-files 10
```

### 2) Rule-based generation

```bash
python -m src.main tests/inputs/complex_sample.py
```

### Other languages (Java, C, C++)

The same command works for Java, C and C++ files; the language is chosen from the file
extension (`.java`, `.c`/`.h`, `.cpp`/`.cc`/`.cxx`/`.hpp`; a `.h` file that uses C++ syntax is
treated as C++). In the desktop app, the **Language** box next to *Open File* switches
automatically and can be set by hand for pasted code.

```bash
python -m src.main tests/inputs/multilang/Inventory.java     # Javadoc
python -m src.main tests/inputs/multilang/matrix.c           # Doxygen
python -m src.main tests/inputs/multilang/shapes.cpp -o out/shapes_annotated.cpp
```

| | Python | Java | C / C++ |
|---|---|---|---|
| Comment style | Google docstrings | Javadoc (`@param`, `@return`, `@throws`) | Doxygen (`@brief`, `@param`, `@param[out]`, `@return`, `@throws`) |
| Parser | Python `ast` | tree-sitter | tree-sitter |
| Comments for | functions, methods, classes | methods, constructors, classes, interfaces, enums, records | functions, prototypes in headers, methods, constructors, destructors, templates, classes, structs, unions, enums |
| Complexity, call graph, AST views | yes | yes | yes |
| ML / neurosymbolic engines | yes | rule-based only (the model was trained on Python) | rule-based only |
| IR, pattern analysis, security scan | yes | no | no |

Existing documentation is respected: a Java declaration with a `/** */` comment, or a C/C++
declaration with any comment directly above it, is left alone, so running the tool twice adds
nothing new. Indentation (tabs included) is copied from the declaration. Install the parsers
with `pip install tree-sitter tree-sitter-java tree-sitter-c tree-sitter-cpp` (already in
`requirements.txt`). The front end lives in `src/languages/`.

### 3) AST+NLP ML generation

```bash
python -m src.main tests/inputs/complex_sample.py --ml
```

`--ml` is strict AST+NLP mode. If no trained model exists, execution fails with a clear train-first message.

Recommended medium-quality run for RTX 4050:

```bash
python -m src.main --train \
  --codesearchnet-max 8000 \
  --max-stdlib-files 600 \
  --epochs 3 \
  --batch-size 8 \
  --grad-accum-steps 1
```

## Output Artifacts

After training, artifacts are written in `outputs/`:

- `outputs/model/ast_model/` — trained AST+NLP model
- `outputs/ast_train_dataset.json` — saved AST/NLP dataset
- `outputs/ast_train_dataset.csv` — dataset in CSV format
- `outputs/training_report.json` — training metadata
- `outputs/eval_report.json` — evaluation metrics

`training_report.json` includes:

- `data_profile.input_mode = "AST structured features"`
- `data_profile.target_mode = "NLP docstring sentence"`
- `data_profile.ast_nlp_pairs`

## Docstring Quality & Safety

Both generation engines apply automatic docstring sanitization to ensure generated code is syntactically valid:

- **Triple-quote escaping**: Prevents malformed docstrings when generated text contains quote characters
- **Raw string sanitization**: Removes invalid raw string prefixes (r""", u""", etc.) that could break syntax
- **Content validation**: All dynamic content (parameters, types, exceptions) is validated before insertion
- This guarantees output Python files are always compilable and valid

Docstrings are inserted before the first statement of the body, so functions
with multi-line signatures stay valid; one-line bodies (`def f(): return 1`)
are left untouched. The input file is never modified — use `--output`.

## Security analysis

**Seven languages.** Python uses the analyzer described below. Java, C#, C, C++, Rust and COBOL
are lowered into the same IR by `src/multilang`. `python -m src.security <file>` and the GUI's
*Scan Editor Code* work for every language. `--engine neurosymbolic` (or the GUI option) adds
the ML detector and fuses it with the rules. The dashboard groups findings into **9 classes**:
the 8 original OWASP classes plus *Others*. Details, the full rule × language matrix and
measured results are in [docs/MULTILANG_SECURITY.md](docs/MULTILANG_SECURITY.md).

The analyzer tracks untrusted data (HTTP request data, `input()`, environment,
`sys.argv`, files, network responses) through assignments, string building,
containers, branches, loops, fields, closures and calls between functions, to
SQL execution, shell/process execution, file-system access, HTML responses,
template compilation, `eval`/`exec`, unsafe deserializers, outbound HTTP requests
(SSRF), redirects (open redirect), XML parsers with external entities enabled (XXE),
LDAP filters, XPath expressions, MongoDB queries, log messages, HTTP headers, regular
expressions, dynamic imports, `str.format` templates, `setattr` and the session. Sanitizers are
context-specific (HTML escaping does not make data safe for SQL). It also runs
AST rules for hardcoded secrets, weak hashes, bare `except`, mutable defaults,
`assert`, insecure randomness, hardcoded IPs, and insecure settings: debug mode, disabled TLS
verification, old TLS versions, weak ciphers, ECB, short keys, static IVs, `mktemp`,
world-writable files, binding to `0.0.0.0`, FTP/Telnet, plain HTTP, tar extraction,
template auto-escaping, cookie flags, CSRF, CORS, JWT verification, SSH host keys,
swallowed exceptions and secrets written to logs. The full list of 50 rules is in
[SECURITY_ANALYSIS.md §4](SECURITY_ANALYSIS.md#4-rules).

Every finding has a rule ID, CWE, severity, **confidence** (high/medium/low with
the reasons), **status** (`confirmed` / `potential` / `suppressed`), the
original file location and a source-to-sink evidence trace:

```text
[CONFIRMED] SEC005 SQL injection — high severity, high confidence (CWE-89)
  at demo.py:13:5 in run_query()
  Data from Flask request data (flask.request.args.get) reaches SQL execution (cur.execute) as argument 1 without sql-context sanitisation.
  evidence:
    L17   [source] untrusted Flask request data: name = request.args.get("name")
    L17   [assign] name = request.args.get("name")
    L18   [call] calls build(): run_query(build(name))
    L7    [param] enters build() as parameter 'name'
    L8    [return] returned: return "SELECT * FROM users WHERE name = '" + name + "'"
    L18   [return] value returned from build()
    L18   [call] calls run_query(): run_query(build(name))
    L10   [param] enters run_query() as parameter 'q'
    L13   [sink] reaches SQL execution cur.execute() as argument 1
  confidence: resolved sink reached by a recognised untrusted source on a feasible path
```

```bash
# security only (no comment generation, no ML model)
python -m src.security path/to/file_or_dir [--json] [--fail-on confirmed]
python -m src.main path/to/file.py --security [--security-json out.json]

# full pipeline, also printing the findings
python -m src.main path/to/file.py --security-report --output out.py

# evaluation on the labelled fixtures (precision / recall / F1 / FPR)
python -m src.security.evaluate [--confirmed-only] [--granularity function]
```

Suppress a reviewed finding with a justification on the same line:
`cur.execute(q)  # nosec SEC005: read-only replica, input is an enum`
(a `# nosec` without a reason is ignored).

Design, full source/sink/sanitizer tables, evaluation results and known
limitations: [SECURITY_ANALYSIS.md](SECURITY_ANALYSIS.md).

## Fix-and-verify agent

The analyzer can also **fix** what it finds. `src/agent/` runs a small agent loop for
each finding, one at a time, re-analysing after every accepted patch:

1. **plan:** pick the next fix strategy for the finding's rule;
2. **act:** make a patched copy of the source; the file itself is never changed;
3. **verify** with the compiler's own analysis:
   - (a) the code parses;
   - (b) `analyze_source` no longer reports that rule in that function;
   - (c) no new finding appears;
   - (d) only the reported function changed, apart from a new import;
4. **accept** the patch, or retry with the next strategy (at most 3), then mark the finding
   *needs manual fix*.

```bash
python -m src.agent path/to/file.py [--out patched.py] [--trace] [--json] [--max-attempts N] [--llm] [--learn]
python -m src.security path/to/file.py --fix      # analysis report, then the agent's report and diff
python -m src.agent.evaluate                      # fixtures + OWASP, saved to outputs/benchmarks/final/
```

| Rule | Strategies (tried in order) |
|---|---|
| SEC005 SQL injection | parameterised query with `?`, then with `%s` (driver-aware) |
| SEC002 command injection | `subprocess.run([...], shell=False, check=True)`, then `shlex.quote()` |
| SEC010 unsafe YAML | `yaml.safe_load` |
| SEC004 weak hash | `hashlib.sha256` |
| SEC001 eval | `ast.literal_eval` |
| SEC018 XXE | external entities switched back off (`False`) |
| SEC024 regex injection | `re.escape()` around the user-supplied pattern |
| SEC029 debug mode | `debug=False` |
| SEC030 TLS verification off | `verify=True` |
| SEC042 tar extraction | `extractall(..., filter="data")` |
| SEC043 auto-escaping off | `autoescape=True` |
| SEC044 cookie flags | `secure=True, httponly=True` |

Findings the agent cannot fix get **retrieved guidance** instead: the rule card and the
closest vulnerable → fixed example, or a fix the agent made earlier (RAG, below).

Strategies are AST-based exact edits. When a mechanical fix would be wrong they decline and
give the reason, for example `ORDER BY` + a column name (an allow-list is needed), a query
passed in by the caller, or `exec`. `--llm` adds a last attempt by a local Ollama model, if
one is running. Its reply must pass the same four checks, and without a model it is skipped
quietly. In the desktop app, **Security → Auto-fix** shows the agent's trace step by step and
a side-by-side diff with **Accept patch** / **Discard**.

**Measured** (no LLM, `outputs/benchmarks/final/agent_fix_eval.json`):
- **Labelled fixtures:** 25 of the 43 findings that have a strategy were fixed and verified (74 findings in total).
- **OWASP BenchmarkPython (1230 cases):** 130 of 164 attempted findings were fixed:

  | Rule | Fixed / attempted |
  |---|---|
  | weak hash | 71 / 71 |
  | SQL injection | 5 / 5 |
  | YAML | 5 / 5 |
  | `eval` | 16 / 35 (the rest are `exec`) |
  | XXE | 9 / 9 |
  | cookie without Secure (SEC044) | 24 / 24 |
  | command injection | 0 / 15 (`sh -c` built across branches) |

No patch was rejected by verification, because the strategies decline instead of guessing.
"Verified" means re-analysed and parsed, not executed. Review the diff before accepting it:
`check=True`, SHA-256 and `literal_eval` change behaviour on purpose. Details:
[docs/METHODOLOGY.md, Step 13](docs/METHODOLOGY.md#step-13--fix-and-verify-agent).

## Retrieval-augmented guidance (RAG)

`src/rag/` is a small offline retrieval system (no network, no new dependencies). Its
knowledge base holds a card for each of the 50 rules (CWE, why it matters, how to fix), a
hand-written vulnerable → fixed example per rule, and a **memory of fixes the agent made
and the verifier accepted** (`--learn`). A BM25 retriever ranks passages for a finding.
The passages are used three ways:
- the agent attaches them to findings it leaves for a manual fix;
- the optional local LLM gets them as fenced reference data, and its patch must still pass
  the four checks;
- `python -m src.rag` searches the knowledge base directly.

```bash
python -m src.rag query "user input in an LDAP search filter"
python -m src.rag explain path/to/file.py      # every finding + retrieved guidance
python -m src.rag stats
python -m src.rag evaluate                      # retrieval accuracy on OWASP labels
```

Retrieval from raw vulnerable code alone, scored against OWASP's own labels (452 cases,
50 rules): recall@1 0.49, recall@3 0.66, recall@5 0.81, where chance is 0.02. Inside the
agent the analyzer already knows the rule, so retrieval only ranks passages for that rule.
How the agent and the RAG are kept safe:
[docs/SECURE_AGENTIC_AI_AND_RAG.md](docs/SECURE_AGENTIC_AI_AND_RAG.md).

---

## Security dataset, model evaluation and profiling

```bash
python -m src.dataset.build              # dataset → datasets/security_dataset/v1/ (manifest, DATASHEET.md)
python -m src.vulnml.pipeline all        # train + tune on validation + test; compare the three engines
python -m src.perfbench                  # block-wise time / memory / throughput → outputs/perf/benchmark.json
python docs/figures/make_figures.py      # figures; make_tables.py prints every results table
```

- **Dataset v1:** 23,131 samples and 774,960 lines in seven languages: NIST SARD Juliet 1.3
  functions (Java, C, C++, C#), OWASP BenchmarkPython, hand-labelled templates and 91 long
  programs of 1,000–2,000 lines with every planted vulnerability's rule and line. Split 70/15/15
  by group, so related code never crosses splits; labels never come from the analyzer.
- **Engines on the same 7,006 test units:** F1 rule-based 0.759, ML 0.554, neuro-symbolic 0.772;
  per language, per source, per family, confusion matrices and latency in
  [docs/SECURITY_DATASET_AND_EVALUATION.md](docs/SECURITY_DATASET_AND_EVALUATION.md).
- **Profiling:** `src/perf.py` blocks cover parsing, features, comment generation, IR/CFG,
  taint, rules, memory safety, ML, fusion, RAG and the agent; the GUI's **Performance** page shows
  the dashboards and profiles the editor's code.

## Tests

```bash
python -m pytest                             # 680 tests
python -m pytest -q tests/test_large_corpus.py   # only the large-file corpus
python -m tests.large_corpus.generate        # regenerate the corpus (deterministic)
```

The suite includes:
- **headless GUI smoke tests** (`tests/test_gui_smoke.py`), which need PyQt6 but no trained
  model;
- **a vulnerable and a safe snippet for every new rule** (`tests/test_security_rules50.py`);
- **the RAG tests** (`tests/test_rag.py`);
- **the multi-language tests** (`tests/test_multilang_*.py`, `tests/test_security_intelligence.py`);
- **the dataset, ML pipeline, profiler and Performance page tests** (`tests/test_dataset_pipeline_perf.py`);
- **the large-file corpus** ([tests/large_corpus/README.md](tests/large_corpus/README.md)):
  50 files of about 2,000 lines each, with 10 planted vulnerabilities and 10 safe twins per
  file. The analyzer must report exactly the planted (rule, line) pairs, and the comment
  pipeline must document every function in a sample of the files. A GitHub Actions workflow (`.github/workflows/tests.yml`) runs the suite on
Python 3.11 and 3.12.

## More documentation

- [docs/GUI.md](docs/GUI.md) — desktop app guide
- [docs/GUIDE.md](docs/GUIDE.md) — feature guide and CLI reference
- [docs/WALKTHROUGH.md](docs/WALKTHROUGH.md) — architecture walkthrough
- [docs/DOCUMENTATION.md](docs/DOCUMENTATION.md) — full technical documentation
- [docs/METHODOLOGY.md](docs/METHODOLOGY.md), [docs/PROGRESS.md](docs/PROGRESS.md)
- [SECURITY_ANALYSIS.md](SECURITY_ANALYSIS.md), [benchmarks/README.md](benchmarks/README.md)
- [docs/SECURE_AGENTIC_AI_AND_RAG.md](docs/SECURE_AGENTIC_AI_AND_RAG.md) — the agent and the RAG system, and how they are kept safe
- [docs/MULTILANG_SECURITY.md](docs/MULTILANG_SECURITY.md) — multi-language back end, knowledge base, ML and neuro-symbolic engines, support matrix
- [docs/SECURITY_DATASET_AND_EVALUATION.md](docs/SECURITY_DATASET_AND_EVALUATION.md) — security dataset, ML pipeline, three-engine comparison, block-wise profiling

---

## Troubleshooting

### "No trained AST+NLP model found" / exit code 2

`--ml` and `--neurosymbolic` require a fine-tuned checkpoint at
`outputs/model/ast_model/`. That directory is gitignored, so it is absent in a
fresh clone. Run `python -m src.main --train --quick` once.

Confirm it worked:

```bash
ls outputs/model/ast_model/      # config.json, model.safetensors, tokenizer files
```

### `pip install torch` fails / "no matching distribution"

You are almost certainly on Python 3.14, which PyTorch does not support yet.
Build the venv with 3.11 or 3.12 — see [Setup](#setup).

### Training is unbearably slow

The defaults (`--epochs 4 --codesearchnet-max 20000 --max-stdlib-files 1500`) are
a multi-hour job. Use `--quick` while you are checking that things work, and
`--dataset-json outputs/ast_train_dataset.json` to skip rebuilding the corpus on
every re-run.

### CUDA out of memory

Halve the batch and compensate with accumulation:

```bash
python -m src.main --train --batch-size 4 --grad-accum-steps 2
```

Mixed precision (fp16) is enabled automatically on CUDA, which is what makes
`--batch-size 8` fit on a 4 GB card.

### "All CodeSearchNet sources failed"

The HuggingFace download was unreachable, or `datasets>=3.0` rejected the legacy
loading-script dataset. Training still proceeds on the Python standard library
crawl — a smaller and narrower corpus, so expect weaker metrics. Check your
network/proxy, or pass `--no-codesearchnet` to make the stdlib-only path explicit.

### GUI: ML-Based and Neurosymbolic are greyed out

No checkpoint was found in `outputs/model/ast_model/`. Train one from the ML Training
page (start with the *Quick check* preset). An older GUI version wrote to `outputs/gui_models` while the generator
tab read from `outputs`. Both now resolve through `src/config.py`. If you
previously trained from the GUI, the stale checkpoint is in
`outputs/gui_models/model/ast_model/` — move it to `outputs/model/ast_model/` or
just retrain.
