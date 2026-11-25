# Security Dataset, Model Evaluation and Block-wise Profiling

This document covers the second phase of the multi-language security work:

1. a versioned security dataset for all seven languages (§1);
2. a reproducible ML training pipeline with a 70 / 15 / 15 split (§2);
3. the rule-based, ML and neuro-symbolic engines scored on the **same** held-out test units (§3);
4. block-wise performance profiling of the whole tool (§4).

Every table between `BEGIN` / `END` markers is generated from the result files by
`python docs/figures/make_tables.py --inject docs/SECURITY_DATASET_AND_EVALUATION.md`;
no number in them is typed by hand. The GUI's **Performance** page reads the same files.

| Step | Command | Output |
|---|---|---|
| Build the dataset | `python -m src.dataset.build` | `datasets/security_dataset/v1/` |
| Train, tune, test the ML models | `python -m src.vulnml.pipeline train` | `outputs/vulnml/<lang>.joblib`, `_config.json`, `_metrics.json` |
| Compare the three engines | `python -m src.vulnml.pipeline evaluate` | `outputs/eval/model_comparison.json` |
| Block-wise benchmark | `python -m src.perfbench` | `outputs/perf/benchmark.json` |
| Figures / tables | `python docs/figures/make_figures.py`, `python docs/figures/make_tables.py` | `docs/figures/*.png` |

---

## 1. Dataset (`datasets/security_dataset/v1/`)

### 1.1 Sources

| Source | Languages | What is taken | Labels |
|---|---|---|---|
| NIST SARD Juliet Test Suite 1.3 (public domain) | Java, C, C++, C# | up to 100 functional variants per CWE, 2 files each; every `bad` function (vulnerable) and `good*` function (safe) | CWE of the test case; flaw lines from Juliet's own `FLAW` / `POTENTIAL FLAW` comments |
| OWASP BenchmarkPython (GPL-3.0, pinned commit) | Python | all 1,230 test cases | real / false positive and CWE from the benchmark's expected results |
| Custom function templates | Java, C#, C, C++, Rust | every function of the multi-language fixtures and its `…Safe` twin, with the hand-written `expect:` markers | rule and line next to the code |
| Custom Python snippet pairs | Python | the vulnerable / safe pairs of the large-file corpus | rule and line next to the code |
| Custom COBOL paragraph templates | COBOL | 11 vulnerable / safe paragraph pairs (`src/dataset/cobol_templates.py`) | rule and line marked `#!` |
| Coverage snippets | all | the one-vulnerability programs of `tests/test_multilang_coverage.py` | rule |
| **Long programs** | all seven | 13 per language (8 train, 2 validation, 3 test), 1,000–2,000 lines each, composed from that split's templates plus ordinary code (`src/dataset/fillers.py`) | every planted vulnerability's rule and exact line |

Labels never come from the analyzer. Custom labels are written next to the code by hand; Juliet
and OWASP labels come from the suites themselves. One template group was excluded: SEC007
(mutable default argument) is a code-quality rule without a CWE.

### 1.2 Splits without leakage

The split unit is a **group**, never a single sample:

- Juliet: a functional variant (test-case name without its flow-variant number), so the
  near-identical `_01` … `_84` versions of one source / sink pair never cross splits;
- OWASP: a template family (`owasp_group_key`);
- custom: a template together with its safe twin and all renamed variants.

Groups are assigned 70 / 15 / 15 by a hash of the group key (rank-based for the small custom
pools, so every split has templates). Long programs of a split are built only from that split's
templates. Tests check that no group crosses splits and that no custom or OWASP code appears
verbatim in both train and test (`tests/test_dataset_pipeline_perf.py`).

### 1.3 Validation

Every custom file must parse without syntax errors (tree-sitter, `ast`, or the COBOL parser);
vulnerable samples must carry at least one location label and safe samples none. Rejected
samples are listed in `manifest.json` — there were none in v1.

### 1.4 Statistics

<!-- BEGIN:dataset -->
### Dataset summary

| Item | Value |
|---|---|
| Samples | 23,131 |
| Lines of code | 774,960 |
| Split groups | 3,895 |
| Distinct CWEs | 132 |
| Vulnerable / safe | 6,931 / 16,200 |
| Train / val / test | 16,216 / 3,815 / 3,100 |
| Long programs | 91 (1,099–1,912 lines; 137,144 lines; 4,984 planted vulnerabilities) |
| Files with more than one vulnerability class | 98 |
| Rejected by validation | 0 |

### Samples per language

| Language | Samples | Vulnerable | Safe | Train/val/test | Lines |
|---|---|---|---|---|---|
| Python | 1,537 | 612 | 925 | 957/411/169 | 115,587 |
| Java | 3,755 | 960 | 2,795 | 2,699/525/531 | 161,402 |
| C# | 3,844 | 957 | 2,887 | 2,581/719/544 | 121,055 |
| C | 8,490 | 2,174 | 6,316 | 6,020/1,326/1,144 | 211,179 |
| C++ | 5,358 | 2,126 | 3,232 | 3,871/807/680 | 124,332 |
| Rust | 67 | 55 | 12 | 38/12/17 | 21,064 |
| COBOL | 80 | 47 | 33 | 50/15/15 | 20,341 |

### Samples per source

| Source | Samples |
|---|---|
| custom | 756 |
| custom-long | 91 |
| juliet | 21,054 |
| owasp | 1,230 |

### Vulnerable samples by family (top 15)

| Family | Vulnerable samples |
|---|---|
| integer-overflow | 1,284 |
| buffer-overflow | 919 |
| memory-management | 575 |
| input-validation | 431 |
| resource-exhaustion | 349 |
| command-injection | 344 |
| path-traversal | 324 |
| format-string | 319 |
| error-handling | 284 |
| null-dereference | 211 |
| xss | 187 |
| weak-crypto | 183 |
| long programs (labelled per location) | 181 |
| ldap-injection | 159 |
| cleartext | 146 |
<!-- END:dataset -->

`DATASHEET.md` next to the data has the full distributions (per rule, per CWE, per split) and the
record format.

**Imbalances to keep in mind.** Juliet dominates C, C++, Java and C#. Rust (67 samples) and
COBOL (80) have only custom data — no public labelled corpus exists for them — so their ML
results are small-sample and flagged as such everywhere.

---

## 2. ML pipeline (`src/vulnml/pipeline.py`)

- **Units:** function-level samples (Juliet functions, OWASP request handlers, custom template
  functions and coverage snippets). Long programs are not used for training.
- **Preprocessing:** `dataset.normalise` — comments removed, strings → `STR`, numbers → `NUM`,
  identifiers that leak labels (`good`, `bad`, `cwe…`, `flaw`, `fix`, `g2b`, `b2g`) and access
  modifiers masked.
- **Features and model:** TF-IDF (max 40,000 features, sublinear tf) and logistic regression,
  one model per language, over the vulnerability families plus `safe`.
- **Hyperparameters:** grid C ∈ {1, 4, 16} × n-grams ∈ {(1,1), (1,2)}, chosen by
  vulnerable-vs-safe F1 on the **validation** split; the chosen setting is refit on train +
  validation and scored **once** on test. Seed 7.
- **Artifacts:** `outputs/vulnml/<lang>.joblib` (model), `<lang>_config.json` (data, grid,
  choice, counts), `<lang>_metrics.json` (test metrics, family confusion matrix, per-source
  metrics, tuning table), `training_report.json`.
- Rust and COBOL models are trained and reported but marked **small-n** and are not used by the
  neuro-symbolic engine (`detector.SMALL_N`).

<!-- BEGIN:training -->
### ML detector: tuning on validation, one score on test

| Language | Train/val/test | Chosen | Val F1 | Acc | P | R | F1 | FPR | FNR | Family acc | Train s |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Python | 913/403/163 | C=16.0, n-grams (1, 1) | 0.691 | 0.865 | 1.000 | 0.681 | 0.810 | 0.000 | 0.319 | 0.841 | 9.3 |
| Java | 2,684/519/528 | C=16.0, n-grams (1, 2) | 0.804 | 0.941 | 0.974 | 0.797 | 0.876 | 0.008 | 0.203 | 0.926 | 19.9 |
| C# | 2,562/716/539 | C=16.0, n-grams (1, 2) | 0.916 | 0.922 | 0.951 | 0.722 | 0.821 | 0.012 | 0.278 | 0.915 | 19.1 |
| C | 6,011/1,321/1,138 | C=16.0, n-grams (1, 2) | 0.804 | 0.916 | 0.900 | 0.763 | 0.826 | 0.030 | 0.236 | 0.915 | 41.8 |
| C++ | 3,862/805/674 | C=16.0, n-grams (1, 2) | 0.576 | 0.730 | 0.721 | 0.583 | 0.644 | 0.164 | 0.417 | 0.700 | 27.2 |
| Rust (small-n) | 25/9/11 | C=16.0, n-grams (1, 2) | 1.000 | 0.455 | 0.400 | 0.400 | 0.400 | 0.500 | 0.600 | 0.273 | 0.2 |
| COBOL (small-n) | 42/13/12 | C=4.0, n-grams (1, 2) | 0.250 | 0.500 | — | 0.000 | — | 0.000 | 1.000 | 0.500 | 0.2 |
<!-- END:training -->

---

## 3. The three engines on the same test units

`python -m src.vulnml.pipeline evaluate` scores every engine on the test split:

- **function units:** every test Juliet function (wrapped in a minimal class for Java and C#),
  every OWASP test case (findings counted inside its request handler), every custom test
  program, and every function of the test long programs (vulnerable when it contains a planted
  vulnerability);
- **decision:** rule-based and neuro-symbolic — any active finding in the unit; ML —
  P(vulnerable) ≥ 0.5;
- **location level:** on the long test programs, exact (rule, line) matches against the planted
  labels (the ML engine predicts per function and has no line output);
- **latency:** wall time per unit, per engine and language.

<!-- BEGIN:comparison -->
### Three engines on the same test units (all languages)

| Engine | n | Acc | P | R | F1 | FPR | FNR | TP | FP | FN | TN |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Rule-based | 7,006 | 0.882 | 0.936 | 0.637 | 0.759 | 0.018 | 0.362 | 1,296 | 88 | 737 | 4,885 |
| ML | 7,006 | 0.743 | 0.559 | 0.548 | 0.553 | 0.177 | 0.452 | 1,115 | 881 | 918 | 4,092 |
| Neuro-symbolic | 7,006 | 0.888 | 0.938 | 0.657 | 0.772 | 0.018 | 0.343 | 1,335 | 89 | 698 | 4,884 |

### By language (F1, with precision / recall)

| Language | Units | Rule-based | ML | Neuro-symbolic |
|---|---|---|---|---|
| Python | 738 | 0.880 (0.79 / 1.00) | 0.595 (0.70 / 0.52) | 0.880 (0.79 / 1.00) |
| Java | 1,156 | 0.833 (0.92 / 0.76) | 0.781 (0.97 / 0.66) | 0.851 (0.92 / 0.79) |
| C# | 996 | 0.700 (1.00 / 0.54) | 0.477 (0.60 / 0.40) | 0.725 (1.00 / 0.57) |
| C | 1,697 | 0.583 (0.92 / 0.43) | 0.647 (0.89 / 0.51) | 0.615 (0.92 / 0.46) |
| C++ | 1,250 | 0.655 (0.98 / 0.49) | 0.476 (0.71 / 0.36) | 0.663 (0.98 / 0.50) |
| Rust | 691 | 1.000 (1.00 / 1.00) | 0.372 (0.23 / 1.00) | 1.000 (1.00 / 1.00) |
| COBOL | 478 | 1.000 (1.00 / 1.00) | 0.643 (0.47 / 1.00) | 1.000 (1.00 / 1.00) |

### By source (F1 / recall / FPR)

| Source | Units | Rule-based | ML | Neuro-symbolic |
|---|---|---|---|---|
| custom | 117 | 1.000 / 1.000 / 0.000 | 0.682 / 0.600 / 0.286 | 1.000 / 1.000 / 0.000 |
| custom-long | 3,927 | 1.000 / 1.000 / 0.000 | 0.360 / 0.370 / 0.264 | 1.000 / 1.000 / 0.000 |
| juliet | 2,838 | 0.171 / 0.099 / 0.023 | 0.800 / 0.764 / 0.059 | 0.243 / 0.147 / 0.024 |
| owasp | 124 | 0.713 / 1.000 / 0.562 | 0.903 / 0.824 / 0.000 | 0.713 / 1.000 / 0.562 |

### Juliet recall inside / outside the rules' CWE scope

| Language | In scope | Out of scope | Rule-based | ML | Neuro-symbolic |
|---|---|---|---|---|---|
| Java | 64 | 61 | 0.625 / 0.000 | 0.906 / 0.869 | 0.781 / 0.000 |
| C# | 51 | 76 | 0.118 / 0.000 | 0.745 / 0.842 | 0.275 / 0.000 |
| C | 236 | 52 | 0.093 / 0.038 | 0.792 / 0.808 | 0.161 / 0.038 |
| C++ | 241 | 37 | 0.046 / 0.000 | 0.685 / 0.486 | 0.066 / 0.000 |

### Long test programs: exact (rule, line) matches

| Language | Programs | Lines | TP | FP | FN | P | R | Neuro-symbolic TP/FP/FN |
|---|---|---|---|---|---|---|---|---|
| Python | 3 | 4,842 | 79 | 0 | 0 | 1.000 | 1.000 | 79/0/0 |
| Java | 3 | 5,187 | 219 | 0 | 0 | 1.000 | 1.000 | 219/0/0 |
| C# | 3 | 4,420 | 192 | 0 | 0 | 1.000 | 1.000 | 192/0/0 |
| C | 3 | 4,969 | 162 | 0 | 0 | 1.000 | 1.000 | 162/0/0 |
| C++ | 3 | 4,435 | 239 | 0 | 0 | 1.000 | 1.000 | 239/0/0 |
| Rust | 3 | 4,797 | 150 | 0 | 0 | 1.000 | 1.000 | 150/0/0 |
| COBOL | 3 | 3,834 | 113 | 0 | 0 | 1.000 | 1.000 | 113/0/0 |

### Mean latency per unit (ms)

| Language | Rule-based (small / long file) | ML (small / long) | Neuro-symbolic (small / long) |
|---|---|---|---|
| Python | 10.1 / 701 | 1.5 / 27 | 37.9 / 902 |
| Java | 8.4 / 729 | 1.7 / 24 | 12.6 / 947 |
| C# | 4.5 / 381 | 1.3 / 32 | 7.7 / 580 |
| C | 4.8 / 498 | 1.4 / 23 | 8.0 / 628 |
| C++ | 5.2 / 397 | 1.7 / 30 | 9.0 / 568 |
| Rust | 2.9 / 619 | 2.4 / 24 | 2.6 / 567 |
| COBOL | 2.5 / 974 | 3.2 / 14 | 1.4 / 962 |
<!-- END:comparison -->

### 3.1 Reading the results

- **Neuro-symbolic vs rule-based.** Fusion adds recall at unchanged precision. It flags 40 test
  units the rules miss — 39 of them truly vulnerable, all Juliet functions (16 C, 10 Java, 8 C#,
  5 C++) — and never drops a rule finding. The additions are SEC064 findings: the ML model predicts
  a family *and* the function calls a sink of that family with non-constant data. Its
  false-positive rate stays at the rule engine's level because ML alone never reports.
- **ML alone** has the best recall on Juliet but a much higher false-positive rate on the
  hand-written code and long programs, which come from a different distribution than its
  mostly-Juliet training data (domain shift).
- **Rule-based scores of 1.000 on custom samples and long programs are not independent
  evidence.** Those templates come from the fixtures the rules were developed against. They show
  that the labels, the composition and the location reporting are consistent at 1,000-2,000
  lines in every language; independent accuracy is what the Juliet and OWASP slices measure.
- **Juliet.** Most Juliet CWEs in C and C++ (integer overflow, buffer overflows with constant
  sizes, null dereference, resource exhaustion) have no rule at all; the in-scope / out-of-scope
  table separates these. Even in scope, Juliet's flows often go through `badSink` helpers in
  other files and sources such as sockets that per-file taint does not follow — a real limitation,
  not tuned away: the analyzer was not adjusted on this test split.
- **OWASP slice vs the OWASP benchmark.** The benchmark scores only findings of the test case's
  own category (F1 0.904 on 877 cases). Here any active finding counts; 38 of the 41 safe test
  cases flagged by the rules have an XSS finding (the handler echoes request data into the
  response) while OWASP labels the file with another weakness. Recall is 1.000 under both rules.

---

## 4. Block-wise profiling (`src/perf.py`, `src/perfbench.py`)

`src/perf.py` provides `profile()` and `block(name)`. Blocks are placed in the code itself and
cost one context-variable lookup when no profile is active:

| Group | Blocks |
|---|---|
| Parsing & AST | `pipeline.parse`, `pipeline.validate` |
| Features & preprocessing | `pipeline.extract`, `pipeline.analyze` |
| Comment generation | `pipeline.generate`, `pipeline.attach` |
| IR & CFG | `pipeline.build_ir`, `pipeline.analysis`, `security.parse`, `security.ir_lowering`, `security.parse_and_ir_lowering` |
| Data flow & taint | `security.cfg_dataflow_taint` |
| Vulnerability detection (rules) | `security.rules_and_findings`, `security.memory_safety` |
| ML model | `ml.predict` |
| Neuro-symbolic fusion | `neurosymbolic.fuse` |
| RAG retrieval | `rag.retrieve` |
| Agentic remediation | `agent.fix_and_verify` (with `agent.strategy`, `agent.verify_patch`); Python only |

`python -m src.perfbench` runs the whole tool (comment pipeline with IR and analysis, the
neuro-symbolic security scan, RAG explanations of up to five findings, and for Python the
fix-and-verify agent) on the long and small test programs of every language. It makes two passes:

- a **timing pass** without tracing;
- a **memory pass** with `tracemalloc` (peak Python heap inside each block; nested blocks
  propagate their peaks to the parent) and `psutil` resident-memory deltas — tracemalloc slows
  Python down several times, so time is never measured in this pass.

A warm-up file per language loads parsers, models and the knowledge base first; that cold start
is recorded separately in the JSON. Each file is analysed for security twice — once by the
comment pipeline's security stage and once by the neuro-symbolic scan — as when a GUI user
generates comments and then scans; the taint and rule blocks include both.

<!-- BEGIN:perf -->
### Block-wise profile (Intel64 Family 6 Model 151 Stepping 2, GenuineIntel, 12 logical CPUs, Python 3.12.6)

| Block (mean ms per file) | Python | Java | C# | C | C++ | Rust | COBOL | Share |
|---|---|---|---|---|---|---|---|---|
| Parsing & AST | 13.0 | 23.0 | 29.2 | 16.6 | 38.5 | 50.2 | 39.5 | 2.3% |
| Features & preprocessing | 148.6 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1.7% |
| Comment generation | 99.4 | 15.9 | 5.2 | 9.7 | 10.7 | 12.2 | 4.0 | 1.8% |
| IR & CFG | 412.6 | 150.0 | 66.1 | 136.0 | 123.6 | 179.8 | 381.3 | 16.2% |
| Data flow & taint | 1241.5 | 459.8 | 88.5 | 189.8 | 261.4 | 307.7 | 1012.4 | 39.7% |
| Vulnerability detection (rules) | 467.0 | 92.9 | 36.6 | 62.5 | 65.0 | 113.8 | 0.9 | 9.3% |
| ML model | 79.5 | 99.2 | 36.4 | 110.3 | 97.0 | 0.0 | 0.0 | 4.7% |
| Neuro-symbolic fusion | 0.6 | 0.6 | 0.3 | 0.5 | 0.9 | 0.0 | 0.0 | 0.0% |
| RAG retrieval | 107.8 | 0.3 | 0.2 | 0.3 | 0.4 | 0.5 | 0.3 | 1.2% |
| Agentic remediation | 2069.1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 23.1% |

### End to end

| Language | Files | Lines | Mean ms/file | p95 ms/file | Lines/s | Peak heap MB | Bottleneck |
|---|---|---|---|---|---|---|---|
| Python | 10 | 3,382 | 2786 | 16176 | 121 | 22.0 | Agentic remediation |
| Java | 10 | 3,785 | 864 | 4467 | 438 | 17.4 | Data flow & taint |
| C# | 10 | 2,887 | 271 | 1568 | 1064 | 11.4 | Data flow & taint |
| C | 10 | 3,420 | 539 | 3025 | 634 | 13.3 | Data flow & taint |
| C++ | 10 | 3,137 | 618 | 3320 | 508 | 16.4 | Data flow & taint |
| Rust | 10 | 3,137 | 679 | 4159 | 462 | 17.7 | Data flow & taint |
| COBOL | 10 | 2,795 | 1458 | 9210 | 192 | 150.1 | Data flow & taint |

Overall bottleneck: **Data flow & taint**. Process RSS 34.2 → 227.7 MB.
<!-- END:perf -->

**Two bottlenecks found and fixed by this profiling.**

1. *COBOL taint analysis.* The first evaluation run took about 100 s for each 1,300-line COBOL
   program. A COBOL program is lowered as one function, so the taint engine merged the state of
   every data item at every block, rebuilding entries that did not change (80 million `join`
   calls). Skipping no-op merges, sharing unchanged values, and visiting blocks in program order
   (a priority worklist instead of FIFO) reduced it to about 1 s per program; the findings on all
   fixtures and long test programs are identical before and after.
2. *ML evidence tokens.* The first benchmark (kept as `outputs/perf/benchmark_before_ml_cache.json`)
   named the **ML model** block the bottleneck for C#, C and C++ (14.8 % of all measured time).
   The cause was not the model: for every function, the explanation step rebuilt the vectoriser's
   list of 40,000 feature names and re-transformed the text. Caching the names per model and
   reusing the file's transformed matrix made prediction 3.3× faster (21.5 s → 6.5 s over 2,303
   predictions) with identical families, probabilities and evidence tokens. The table above is
   the benchmark after the fix.

The memory pass shows COBOL with the largest peak heap: its whole program is one function, so
the taint state of every data item is held at every block.

---

## 5. Limitations

- The ML models are trained mostly on synthetic Juliet code and transfer poorly to hand-written
  code (see the per-source rows). Rust and COBOL have only a few dozen samples.
- Rule-based results on custom data are not independent of rule development (§3.1).
- Juliet location labels exist only where Juliet has `FLAW` comments; OWASP has file-level
  labels only.
- Severity labels are the project's rule severities (CWE itself has no severity field).
- Timings depend on the machine; the benchmark JSON records Python version, processor and CPU
  count, and every run regenerates the numbers.
