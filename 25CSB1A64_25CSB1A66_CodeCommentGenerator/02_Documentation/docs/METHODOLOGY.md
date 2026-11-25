# Code Comment Generator using AST and NLP — Step-by-Step Methodology

This document describes, step by step, how the system turns a source file (Python, Java,
C or C++) into commented code, a code-quality report and a security report, and how the machine-learning
model behind it was built and evaluated. The overall flow is shown in
[architecture.png](architecture.png).

---

## Overview of the Method

```
Python source ──► 1 Input ──► 2 Parse ──► 3 Validate ──► 4 Extract AST features ──► 5 Analyse context
                                                                                         │
                     ┌───────────────────────────────┬───────────────────────────────────┤
                     ▼                               ▼                                   ▼
          6 Generate comments              8 Build IR                       10 Security analysis
            (rule / ML / hybrid)           9 CFG + data flow                   (taint + AST rules)
          7 Attach comments                  + pattern detection
                     │                               │                                   │
                     └───────────────────────────────┴──────────► 11 Outputs & reports ◄─┘
```

The key idea is that **the program is understood through its Abstract Syntax Tree (AST),
not as plain text**. Structural facts (parameters, types, loops, branches, calls,
exceptions) are extracted from the AST first; natural-language techniques (NLP) and a
neural model then turn those facts into readable English. Facts that must be exact —
argument names, types, raised exceptions — always come from the AST, so the generated
documentation cannot contradict the code.

[Step 13](#step-13--fix-and-verify-agent) adds an agent that patches security findings and
accepts a patch only after the analyzer re-checks it.

Steps 1–11 describe the Python pipeline. Java, C and C++ files go through the same stages up
to comment attachment, using a tree-sitter parser instead of Python's `ast` module — see
[Step 12](#step-12--other-languages-java-c-and-c).

---

## Step 1 — Input Acquisition

**Goal:** accept the code to be documented and choose how to process it.

1. The user supplies a single `.py` file (or, for security analysis, a whole project folder).
2. Three entry points are available:
   - Command line: `python -m src.main <file.py>` with options for the engine
     (`--ml`, `--neurosymbolic`) and for security output (`--security`, `--security-json`).
   - Security-only command line: `python -m src.security <file or folder> [--project]`.
   - Desktop GUI: `python run_gui.py` (PyQt), with workspaces for generation, training,
     insights, security and logs.
3. The selected generation engine is recorded: **rule-based** (default, no model needed),
   **ML (AST + NLP)**, or **neuro-symbolic** (ML combined with rules).

## Step 2 — Parsing the Source into an AST

**Goal:** obtain a faithful tree representation of the program.

1. The file is read with encoding detection (`parser_module.read_file`).
2. Python's built-in `ast.parse` converts the text into an Abstract Syntax Tree. Every node
   keeps its line and column numbers, which are used later to place comments and to report
   findings at exact locations.
3. If the file has a syntax error, processing stops with a clear message giving the line and
   column (`error_handler`), instead of producing broken output.

## Step 3 — Semantic Validation

**Goal:** detect problems that are legal Python but worth reporting.

1. A `SemanticValidator` (an `ast.NodeVisitor`) walks the tree.
2. It checks conventions such as snake_case function names and other style/semantic rules.
3. Violations are collected as warnings and logged; they do not stop the pipeline.

## Step 4 — AST Feature Extraction

**Goal:** convert the tree into structured facts about every function and class.

A `FeatureExtractor` visits each definition and records:

| For functions | For classes |
|---|---|
| name, parameters, type annotations, default values | name, base classes |
| return annotation (or inferred return types) | class attributes (public / private) |
| decorators (`@property`, `@staticmethod`, …), `async` | methods |
| number of loops and conditionals, body size | existing docstring |
| internal and external calls | line numbers |
| exceptions raised, existing docstring, line numbers | |

These facts are stored in `FunctionFeature`, `ClassFeature` and `ModuleFeatures` objects
(`ast_extractor.py`, `ast_body_extractor.py`). Everything later in the pipeline reads these
objects rather than the raw text.

## Step 5 — Context Analysis

**Goal:** add meaning that needs a view of the whole function or module.

1. **Cyclomatic complexity** is computed for each function by counting decision points
   (`if`, loops, `except`, boolean operators, comprehensions).
2. Each function receives a complexity label:

   | Cyclomatic complexity | Label |
   |---|---|
   | ≤ 2 | simple |
   | 3 – 5 | moderate |
   | 6 – 10 | complex |
   | > 10 | very complex |

3. A **call graph** records which functions call which.
4. A **variable tracker** records where variables are assigned and used, with simple type
   inference from literals.
5. Security messages from the security analyzer (Step 10) can be attached to each function's
   context so that they appear in the generated comments.

The result is a `ContextGraph` with one `FunctionContext` per function (`context_analyzer.py`).

## Step 6 — Comment Generation

**Goal:** produce a docstring for each undocumented function and class, plus block comments
for non-trivial functions. One of three engines is used.

### 6a. Rule-based NLP engine (`comment_generator.py`)

1. **Identifier splitting:** names such as `calculateTotalPrice` or `load_user_data` are split
   into words (`calculate total price`, `load user data`).
2. **Stop-word removal** keeps only meaningful tokens.
3. **Verb mapping:** the first meaningful word is mapped to a descriptive verb using a table of
   150+ entries (e.g. `get → Retrieves`, `calc → Calculates`, `is → Checks whether`).
4. **Summary sentence:** `<Verb> <noun phrase>.` — for example, `calculate_total(items)` →
   *"Calculates total."*; async functions are prefixed with *"Asynchronously …"*.
5. **Body description** from the AST facts: loops, branches, complexity label (with a
   refactoring hint for complex functions), delegated calls, decorators, raised exceptions.
6. **Structured sections** — `Args`, `Returns`, `Raises` — are filled directly from the AST
   (names, annotations, defaults, exception types).
7. Classes receive *"Represents a …"* plus inheritance, attributes and methods sections.

### 6b. ML engine — AST + NLP model (`src/ml/`)

1. **Feature serialisation:** the function's AST facts are written as structured text
   (`ast_feature_formatter.py`). The model never sees the raw source code. Example:

   ```
   Generate docstring: process_items
   async: no | method: no
   params: items:list, threshold:int=5
   returns: dict
   loops: 1 | conditionals: 2 | body_size: 8
   complexity: moderate (cyclomatic=4)
   calls_internal: validate_input, store_result
   calls_external: os.path.join
   raises: ValueError, IOError
   ```

2. **Generation:** a fine-tuned **T5-small** sequence-to-sequence model (60M parameters)
   generates a one-sentence summary using beam search (6 beams, up to 72 tokens).
3. **Confidence score:** the probability of the chosen beam is turned into a confidence value
   between 0 and 1.
4. **Docstring assembly:** the ML summary is combined with the AST-derived `Args`, `Returns`
   and `Raises` sections (`build_full_docstring`), so only the English summary depends on the
   model.
5. If no trained model exists, the system falls back to the rule-based engine (unless strict
   ML mode is requested).

### 6c. Neuro-symbolic engine (`src/neurosymbolic/`)

Combines the neural model with symbolic rules, gated by confidence:

1. The ML model produces a summary and its confidence (as in 6b).
2. A **symbolic reasoner** matches 13 rules against the AST facts (e.g. SYM006 *dangerous
   eval*, SYM010 *generator pattern*, SYM012 *recursion*, SYM013 *high complexity*).
3. A **consistency check** compares the ML sentence with AST facts (e.g. the summary of a
   function with loops should mention iteration; a declared return type should be reflected)
   and records any mismatches.
4. **Fusion by confidence:**

   | ML confidence | Decision |
   |---|---|
   | ≥ 0.7 | use the ML summary directly ("neural") |
   | 0.4 – 0.7 | use the ML summary, add symbolic notes and warnings ("fused") |
   | < 0.4 | discard the ML summary, use the rule-based summary ("symbolic") |

### Common safeguards (all engines)

- Generated text is **sanitised**: triple quotes and string prefixes that would break Python
  syntax are removed, so the output file always compiles.
- Functions that already have a docstring are left alone.

## Step 7 — Comment Attachment

**Goal:** insert the comments into the source without breaking it or changing its behaviour.

1. The source is parsed again to find each function/class body's **first statement**.
2. Docstrings are inserted **immediately before that first statement**, using its indentation —
   this stays correct for signatures spread over several lines. Block comments go just above
   the `def`/`class` line.
3. One-line bodies (`def f(): return 1`) are left unchanged and noted in the change log.
4. A **line map** from original to new line numbers is recorded, so findings computed on the
   original file can still be shown at the right place in the commented file.
5. The annotated source is written to the output folder.

## Step 8 — Intermediate Representation (IR)

**Goal:** a simpler, uniform form of each function for program analysis.

1. Each function's AST is **lowered** to three-address instructions (assignments, calls,
   attribute and subscript access, branches, returns) grouped into **basic blocks**
   (`src/ir/lowering.py`).
2. Control structures — `if`/`else`, `for`/`while` with `break`/`continue`,
   `try`/`except`/`finally`, `match`, early `return`, and calls that never return — become
   explicit jumps between blocks.
3. Every instruction keeps its source line and column.

## Step 9 — Control-Flow Graph, Data-Flow Analysis and Pattern Detection

**Goal:** find code-quality problems that need knowledge of execution paths.

1. A **control-flow graph (CFG)** is built from the basic blocks (`cfg_builder.py`).
2. Two classic data-flow analyses run with a worklist algorithm until they converge
   (`dfa_engine.py`):
   - **Reaching definitions** (forward): which assignments can reach each point.
   - **Live variables** (backward): which variables are still needed at each point.
3. The **pattern detector** uses these results to report seven patterns (`pattern_detector.py`):

   | Code | Pattern |
   |---|---|
   | P001 | variable assigned but never read |
   | P002 | cyclomatic complexity above 10 |
   | P003 | dead block (unreachable from the entry block) |
   | P004 | function annotated to return a value can return `None` |
   | P005 | loops nested three or more levels deep |
   | P006 | more than 10 distinct functions called |
   | P007 | parameter never read |
4. Results are collected into a code-quality report.

## Step 10 — Security Analysis

**Goal:** detect vulnerabilities with evidence of how attacker data reaches a dangerous
operation.

1. **Lowering:** the module is lowered to IR + CFG (as in Step 8), or a whole folder of modules
   in project mode, with imports resolved across files.
2. **Taint analysis** (`src/security/taint.py`, `rules.py`):
   - **Sources** — where untrusted data enters (e.g. Flask/Django request data such as
     `request.args`, `input()`, standard input, environment variables).
   - **Propagation** — taint follows assignments, string operations, containers, object fields,
     function calls and returns, including across functions and files (function summaries
     computed to a fixed point).
   - **Sanitisers** — context-specific: e.g. `shlex.quote` makes data safe for a shell command
     but not for SQL; allow-list and path-prefix checks on a branch make data safe only on that
     branch.
   - **Sinks** — dangerous operations: SQL execution, shell commands, `eval`/`exec`, file paths,
     HTML output, unsafe deserialisation (`pickle`, `yaml.load`), outbound HTTP requests (SSRF),
     redirects (open redirect), XML parsers with external entities enabled (XXE), and others.
     A URL whose scheme and host are fixed literals is not reported, and a host checked
     against an allow-list (`urlparse(u).netloc in ALLOWED`) is safe on that branch.
   - Constant propagation removes branches that can never execute, avoiding false alarms.
3. **AST rules** (`ast_rules.py`) detect issues that are properties of the code itself:
   hard-coded secrets, weak hashes (MD5/SHA-1), bare `except`, mutable default arguments,
   `assert` used for validation, insecure randomness, hard-coded network addresses.
   `config_rules.py` adds 22 rules for insecure *settings*: debug mode, disabled TLS
   verification, old TLS versions, weak ciphers, ECB, short keys, static IVs, `mktemp`,
   world-writable files, binding to all interfaces, FTP/Telnet, plain HTTP, tar extraction,
   template auto-escaping, cookie flags, CSRF, CORS, JWT verification, SSH host keys,
   swallowed exceptions and secrets in logs (SEC029–SEC050).
   The taint engine has ten more sink families (SEC019–SEC028): LDAP filters, XPath, MongoDB
   queries, log messages, HTTP headers, regular expressions, dynamic imports, `str.format`
   templates, `setattr` and the session. Each has its own context and sanitizers
   (`escape_filter_chars`, `re.escape`, …).
4. **Findings:** every issue is reported with rule ID (SEC001–SEC050), CWE number, severity,
   confidence, status (*confirmed* / *potential*), exact location and the step-by-step data-flow
   trace from source to sink. A finding can be suppressed only with a written justification
   (`# nosec SEC005: reason`).

## Step 11 — Outputs and Reporting

**Goal:** present the results to the user.

1. **Commented `.py` file** — the original code with the generated docstrings and comments.
2. **Reports** in `outputs/` — JSON for AST features, context graph, IR, analysis findings and
   security findings, plus a stage-by-stage pipeline log with timings.
3. **GUI views** — AST graph, context graph, CFG, security findings table and graph, training
   charts and logs.
4. In security-only mode the command line exits with code 1 when active security findings
   exist, so the tool can be used in automated checks.

## Step 12 — Other Languages: Java, C and C++

**Goal:** give the same AST-driven comments to the most widely used compiled languages, not
only to Python.

1. **Language detection** (`src/languages/__init__.py`). The language is taken from the file
   extension: `.java` → Java; `.c`/`.h` → C; `.cpp`, `.cc`, `.cxx`, `.hpp` → C++. A `.h` file
   that uses C++ syntax (`class`, `namespace`, `template<…>`, `std::`) is treated as C++. In the
   GUI the *Language* box follows the opened file and can be set by hand for pasted code.
2. **Parsing with tree-sitter** (`src/languages/treesitter_extract.py`). Python's `ast`
   module cannot read other languages, so these files are parsed with tree-sitter, an
   incremental parser with maintained grammars for Java, C and C++. If the parser had to
   recover from a syntax error, the line is reported as a warning instead of stopping the run.
3. **Feature extraction into the same data model.** The tree-sitter tree is walked to fill the
   *same* `FunctionFeature`, `ClassFeature` and `ModuleFeatures` objects as Step 4:
   - functions, methods, constructors, destructors, template functions and header prototypes
     (a prototype is skipped when the same file also defines the function);
   - parameters with types and C++ default values, return types (including `*` and `&`),
     Java annotations and C/C++ specifiers (`static`, `virtual`, `template`);
   - classes, interfaces, enums, records, structs (including `typedef struct {…} Name;`) and
     unions, with base classes, fields and methods;
   - calls, loops, branches and thrown exceptions (`throw new X(…)` in Java, declared
     `throws` clauses, `throw std::x(…)` in C++).
4. **Context analysis.** Cyclomatic complexity is counted the same way as Step 5: one plus
   every `if`, loop, `case`, `catch`, ternary and `&&`/`||`. Local variables are tracked with
   their declared types, and calls are split into internal (to functions in the same file) and
   external, giving the same `ContextGraph` and complexity labels.
5. **Comment generation in the language's own style** (`src/languages/doc_render.py`). The
   summary and body sentences come from the same rule-based NLP helpers as Step 6a
   (identifier splitting, verb selection, body description); only the comment syntax changes:
   - **Java → Javadoc:** `/** … */` with `@param`, `@return`, `@throws`, `{@code …}`; `<`, `>`
     and `&` are escaped because Javadoc is HTML. The output passes `javadoc -Xdoclint`.
   - **C / C++ → Doxygen:** `/** @brief … */` with `@param`, `@param[out]` for output pointers,
     `@return` (including "or NULL on failure" when the function allocates), `@throws`.
   - Special cases: constructors ("Creates a new X instance"), destructors, `main`, `toString`,
     boolean `is…`/`has…` methods and noun-only names (`area()` → "Returns the area").
   - Functions that are not simple also get a short `// Complexity: …` note above the comment.
6. **Comment attachment** (`src/languages/pipeline.py`). Each comment is inserted directly
   above the declaration (above `template<…>` and Java annotations), copying that line's own
   indentation, tabs included. A declaration that already has a comment directly above it
   (for Java, a `/** */` comment) is left alone, so a second run adds nothing.
7. **What stays Python-only.** The ML and neuro-symbolic *comment* engines (the T5 model was
   trained on Python docstrings) and the fix-and-verify agent. IR, pattern analysis (P001–P007)
   and security analysis were extended to every language in Step 14.

---

## Step 13 — Fix-and-Verify Agent

**Goal:** go from *detecting* a vulnerability to *fixing* it, without trusting any fix that
the compiler's own analysis has not checked.

The agent (`src/agent/`) is a small plan → act → observe → decide loop around the analyzer
of Step 10:

```
analyze_source ──► next finding ──► PLAN: pick next strategy for its rule
      ▲                                   │
      │                                   ▼
      │                            ACT: patched copy of the source (input never modified)
      │                                   │
      │                                   ▼
      │                OBSERVE: (a) ast.parse  (b) finding gone  (c) nothing new
      │                         (d) only the reported function changed
      │                                   │
      └──── accept ◄── DECIDE ──► reject: next strategy (max 3), then "needs manual fix"
```

1. **One finding at a time.** Findings are taken in line order. After every accepted patch the
   code is analysed again, so later fixes always start from verified code. A finding is
   identified across patches by rule, function and the sink's line of code, because line
   numbers shift.
2. **Strategies** (`src/agent/strategies.py`) are deterministic rewrites that use node
   positions from Python's `ast`. Edits are exact span replacements; no regular expressions
   are applied to the source. A needed import is added after the existing imports.

   | Rule | Strategy | Rewrite |
   |---|---|---|
   | SEC005 SQL injection | `sql-param-qmark`, then `sql-param-format` | concatenation, f-string, `%` or `.format()` → `"... = ?"` (or `%s`) plus a parameter tuple. It follows `query = …; final = query` inside the function. `'%{x}%'` around `LIKE` moves into the parameter. `?` is skipped for Django/psycopg2/MySQL code, and `%s` is skipped for sqlite3. |
   | SEC002 command injection | `cmd-argv-list`, then `cmd-shlex-quote` | `os.system(cmd)` / `shell=True` → `subprocess.run([...], shell=False, check=True)` when the literal text has no shell syntax. Otherwise each untrusted part is wrapped in `shlex.quote()`. |
   | SEC010 unsafe YAML | `yaml-safe-load` | `yaml.load(...)` → `yaml.safe_load(...)` |
   | SEC004 weak hash | `hash-sha256` | `hashlib.md5/sha1` → `hashlib.sha256` (skipped when `usedforsecurity=` is set) |
   | SEC001 eval | `eval-literal-eval` | `eval(x)` → `ast.literal_eval(x)`, adding `import ast` |
   | SEC018 XXE | `xxe-disable-entities` | `setFeature(feature_external_ges, True)` / `XMLParser(resolve_entities=True)` inside the function → `False` |
   | SEC024 regex injection | `regex-escape` | `re.findall(p, …)` → `re.findall(re.escape(p), …)` |
   | SEC029 debug mode | `debug-off` | `app.run(debug=True)` → `debug=False` |
   | SEC030 TLS verification | `tls-verify-on` | `verify=False` → `verify=True` |
   | SEC042 tar extraction | `tar-data-filter` | `tar.extractall(d)` → `tar.extractall(d, filter="data")` |
   | SEC043 auto-escaping | `jinja-autoescape` | `jinja2.Environment(...)` → `autoescape=True` |
   | SEC044 cookie flags | `cookie-secure` | `set_cookie(...)` → `secure=True, httponly=True` |

   A strategy declines, giving the reason, when a mechanical fix would be wrong:
   - the value is spliced in as SQL syntax (`ORDER BY col`, `WHERE <clause>`), where a placeholder cannot go and an allow-list is needed;
   - the string is a parameter, so it is built by the caller;
   - the variable is assigned in a loop or in several branches;
   - the untrusted value chooses the program to run;
   - the call is `exec`.
3. **Verification** (`src/agent/verify.py`) re-runs `analyze_source` on the patched code. It
   compares (rule, function) counts, not line numbers: the patched function must have fewer
   findings of that rule, and no (rule, function) pair may appear more often than before. A
   line diff (`difflib`) checks that only lines of the reported function changed; the only
   change allowed elsewhere is a new top-level import.
4. **Optional LLM strategy** (`src/agent/llm_strategy.py`, off by default). With `--llm` and a
   local Ollama server at `localhost:11434`, it is tried after the templates. It sends the
   function, the finding message, the evidence trace and the remediation text, and asks for the
   rewritten function only. The reply goes through the same four checks. Without a model it is
   skipped quietly; everything else works offline. The prompt also carries the top passages
   retrieved by the RAG system (below), fenced and marked as reference data.
5. **Retrieval-augmented guidance** (`src/rag/`). The knowledge base holds:
   - a card for each of the 50 rules;
   - a hand-written vulnerable → fixed example for each rule;
   - with `--learn`, the fixes the verifier accepted (an integrity-checked JSONL memory).

   A BM25 retriever ranks passages, restricted to the finding's rule. Findings the agent
   cannot fix get the top passages as guidance. Full design and safety measures:
   [SECURE_AGENTIC_AI_AND_RAG.md](SECURE_AGENTIC_AI_AND_RAG.md).
6. **Interfaces.**
   - `python -m src.agent file.py [--out patched.py] [--llm] [--json] [--max-attempts N] [--trace] [--learn]`
   - `python -m src.rag query|explain|stats|evaluate`
   - `python -m src.security file.py --fix`
   - The GUI's **Auto-fix** button (Security workspace) streams the trace and shows a side-by-side
     diff with **Accept patch** / **Discard**.

**Measured results** (`python -m src.agent.evaluate`, saved to
`outputs/benchmarks/final/agent_fix_eval.json`, no LLM, at most 3 attempts per finding).
*Attempted* means at least one strategy exists for the finding's rule and was tried.

| Dataset | Findings | Attempted | Fixed and verified | Needs manual fix | Patches rejected |
|---|---|---|---|---|---|
| Labelled fixtures (7 files) | 74 | 43 | 25 | 49 | 0 |
| OWASP BenchmarkPython (1230 cases, 16.5 s) | 2033 | 164 | 130 | 1903 | 0 |

Per rule on OWASP (findings attempted → fixed):

| Rule | Attempted → fixed |
|---|---|
| SEC004 weak hash | 71 → 71 |
| SEC005 SQL injection | 5 → 5 |
| SEC010 unsafe YAML | 5 → 5 |
| SEC001 eval/exec | 35 → 16 (the other 19 are `exec`) |
| SEC018 XXE | 9 → 9 |
| SEC044 cookie without Secure | 24 → 24 |
| SEC002 command injection | 15 → 0 |

The OWASP command-injection cases build `sh -c "echo {bar}"` across `if`/`else` branches or
append it to a list. An argument list would still pass the value to a shell, so the agent
leaves them for a person.

Most findings have no strategy at all: 1104 of the OWASP findings are XSS (SEC014), 351 are
bare `except` (SEC006), 95 are path traversal (SEC013) and 14 are open redirects (SEC017).
SSRF and open redirect need a decision about which hosts are allowed, so the agent reports them
with the remediation text instead of guessing an allow-list.

On real-vulnerability OWASP cases, every reported finding of the case's own category was fixed in:
- all 71 weak-hash cases;
- all 5 SQL-injection cases;
- 10 of 20 code-injection cases;
- 5 of 18 deserialization cases;
- all 8 XXE cases.

No patch was rejected by verification, because the strategies decline instead of guessing.
The verifier's rejection path is covered by tests with a deliberately bad strategy and with
a stubbed LLM reply that keeps the bug.

**Limits.** "Verified" means the analyzer no longer reports the finding and the code parses;
the patched programs were not executed. Some fixes change behaviour on purpose:
- `check=True` raises an exception when the command fails;
- `sha256` changes stored digests, and passwords really need a KDF;
- `literal_eval` rejects expressions.

The diff is therefore shown for review instead of being written over the file.

---

## Step 14 — Multi-Language Security Intelligence

1. **One IR for every language.** Java, C#, C, C++ and Rust are lowered from tree-sitter
   syntax trees (`src/multilang/lower.py`), and COBOL from a new parser (`src/multilang/cobol.py`),
   into the three-address IR of Step 8. The CFG builder, data-flow analyses and P001–P007 of
   Step 9 then run unchanged.
2. **Rule-based engine.** A language-neutral taint engine uses per-language source, sink
   and sanitizer tables. It adds memory-safety analysis for C/C++ (use after free, double
   free, unchecked allocation) and syntax rules (crypto, TLS, XXE, deserialization,
   credentials, races, authorization, unsafe code). There are 64 rules in total.
3. **ML engine.** TF-IDF and logistic regression per language, trained on NIST SARD Juliet
   (Java, C, C++, C#) and OWASP BenchmarkPython. Label-leaking names, comments and
   modifiers are removed, and the data is split by functional variant.
4. **Neuro-symbolic engine.** Rule findings, ML predictions and knowledge-base sink
   conditions are fused: agreement raises confidence, and an ML-only signal is reported only
   with semantic evidence.
5. **Knowledge base and RAG.** 1,512 entries (MITRE CWE + CAPEC, Juliet examples) are
   retrieved to explain each finding with its code evidence.
6. **Dashboard.** 9 classes: the 8 original OWASP classes plus Others.

Measured results and the support matrix: [MULTILANG_SECURITY.md](MULTILANG_SECURITY.md).

---

## Step 15 — Security Dataset, Model Evaluation and Profiling

1. **Dataset** (`python -m src.dataset.build`). Juliet 1.3 functions (Java, C, C++, C#), OWASP
   BenchmarkPython cases, hand-labelled templates for all seven languages, and long programs of
   1,000–2,000 lines composed from the templates of one split plus ordinary code. Labels come
   from the suites or from markers written next to the code, never from the analyzer. Every
   custom file must parse and carry consistent labels.
2. **Split** 70 / 15 / 15 by group (Juliet functional variant, OWASP template family, custom
   template with its safe twin and variants), so no related code crosses splits.
3. **ML pipeline** (`python -m src.vulnml.pipeline train`). Normalised tokens → TF-IDF → logistic
   regression per language; C and the n-gram range are chosen on validation, the chosen model is
   refit on train + validation and scored once on test. Configs and metrics are saved with the
   model.
4. **Three-engine comparison** (`python -m src.vulnml.pipeline evaluate`). Rule-based, ML and
   neuro-symbolic engines are scored on the same test units: accuracy, precision, recall, F1,
   false-positive and false-negative rates, confusion matrices, per language, per source and per
   family, exact (rule, line) matches on the long programs, and latency.
5. **Block-wise profiling** (`src/perf.py`, `python -m src.perfbench`). Blocks in the code measure
   every stage; a timing pass and a separate tracemalloc / psutil memory pass run over the test
   programs of every language. The results and a live profile of the editor's code are in the
   GUI's Performance page.

Method and results: [SECURITY_DATASET_AND_EVALUATION.md](SECURITY_DATASET_AND_EVALUATION.md).

---

## Model Training Methodology

The ML and neuro-symbolic engines rely on a model trained once, offline
(`python -m src.main --train`).

### T1 — Data collection
1. **CodeSearchNet (Python)** — downloaded from Hugging Face; real open-source functions with
   human-written docstrings (primary source).
2. **Python standard library** — crawled locally as an offline supplement.

### T2 — Building training pairs
For every function that has a docstring:
1. Parse it with `ast` and run the same feature extraction and context analysis as Steps 4–5.
2. Serialise the features into the structured text of Step 6b → **input**.
3. Clean the docstring down to its first sentence → **target**.
4. Remove duplicates (hash of the normalised input and target).

### T3 — Data split
90 % training / 10 % test; a further part of the training set is held out for validation
during training (fixed random seed 42 for reproducibility).

### T4 — Fine-tuning
| Setting | Value used |
|---|---|
| Base model | `google-t5/t5-small` (60M parameters) |
| Input / output length | 256 / 64 tokens |
| Epochs | 3 |
| Batch size | 8 |
| Learning rate | 2 × 10⁻⁴ |
| Precision / device | bfloat16 mixed precision on a CUDA GPU |
| Model selection | checkpoint with the lowest validation loss |

### T5 — Training run recorded in `outputs/training_report.json`
- 13,480 training pairs (8,000 CodeSearchNet functions requested, 600 stdlib files):
  10,918 train, 1,214 validation, 1,348 test.
- Training loss 3.66 → 3.19 → 3.03; validation loss 3.11 → 2.97 → **2.93** (best at epoch 3).

### T6 — Evaluation (`outputs/eval_report.json`, 200 test functions)
| Metric | Result |
|---|---|
| BLEU-4 (mean) | 0.060 |
| ROUGE-L (mean) | 0.262 |
| Exact match | 1 % |

These scores are typical for one-sentence docstring generation from a small model: the
generated sentences usually capture the intent (e.g. reference *"Convert WordSet into raw
dictionary data."* → generated *"Converts a term to a dictionary."*) without matching the
reference wording. This is why the neuro-symbolic engine gates ML output by confidence and why
`Args`/`Returns`/`Raises` are always taken from the AST.

---

## Testing and Evaluation Methodology

1. **Automated tests** — 680 tests (`python -m pytest`) covering parsing, IR semantics, data-flow
   analysis, comment placement (output must still compile and keep line integrity), the ML
   path, the GUI, the security analyzer and the fix-and-verify agent. The agent tests cover:
   - every strategy fixes its fixture, and the analyzer confirms it;
   - retry after a declined or rejected patch;
   - giving up;
   - no change outside the reported function;
   - safe files left unchanged;
   - a stubbed LLM. For Java, C and C++ the tests check extraction,
   comment content, that a second run adds nothing, that every original line is kept in order,
   and that the annotated files still compile with `javac`, `gcc` and `g++`.
2. **Security evaluation** on three separate datasets, using precision, recall, F1 and
   false-positive rate (undefined values reported as *undefined*, never as perfect):
   - **Synthetic fixtures** written with the analyzer — regression tests only.
   - **OWASP BenchmarkPython** — independently labelled test cases, split into development and
     held-out sets. Held-out F1 (confirmed + potential findings): 0.901 single-file, 0.916
     project mode. The redirect and XXE categories, covered by the rules added last, are
     scored separately: held-out F1 0.933 single-file, 1.000 project mode (18 cases). The
     LDAP, XPath, trust-boundary and secure-cookie categories (rules SEC019, SEC020, SEC028,
     SEC044) are a third block: held-out F1 0.860, dev 0.862.
   - **Large-file corpus** — 50 generated files of ~2,000 lines (101,057 lines). Each has 10
     planted vulnerabilities and 10 safe twins, so every rule is planted 10 times. The
     expected lines are written by hand. Result: 500 of 500 found, 0 false positives. This is
     a regression and scale test, not an independent benchmark.
   - **Real-world GitHub security advisories** — vulnerable and patched versions of real
     projects, labelled manually from the advisory and fix. Held-out F1: 0.690 (14 cases;
     indicative only).
3. **Multi-language and dataset evaluation.** The seven multi-language fixtures carry 83
   hand-marked vulnerabilities (all found, no false positives; regression tests). The security
   dataset's test split scores the rule-based, ML and neuro-symbolic engines on the same 7,006
   units, with Juliet and OWASP as the independent slices
   ([SECURITY_DATASET_AND_EVALUATION.md](SECURITY_DATASET_AND_EVALUATION.md)).
4. **RAG retrieval evaluation** (`python -m src.rag evaluate`). The query is the vulnerable
   code of each OWASP true-positive case, and the truth is OWASP's category label. Over 452
   cases: recall@1 0.49, recall@3 0.66, recall@5 0.81, where chance is 0.02.

   Details and limitations: [SECURITY_ANALYSIS.md](../SECURITY_ANALYSIS.md) §5–6 and
   [benchmarks/README.md](../benchmarks/README.md).

---

## Tools and Technologies

| Purpose | Technology |
|---|---|
| Language | Python 3.11 / 3.12 |
| Input languages | Python, Java, C#, C, C++, Rust, COBOL |
| Parsing and analysis | Python `ast` module, tree-sitter (Java, C#, C, C++, Rust), own COBOL parser, custom IR, CFG, data-flow and taint engine |
| NLP / ML | Hugging Face Transformers, PyTorch, T5-small; scikit-learn (TF-IDF + logistic regression vulnerability detector) |
| Dataset | CodeSearchNet (Hugging Face `datasets`), Python standard library; NIST SARD Juliet 1.3, OWASP BenchmarkPython, MITRE CWE 5.0 / CAPEC; security dataset v1 |
| Evaluation metrics | BLEU-4, ROUGE-L, exact match; accuracy / precision / recall / F1 / FPR / FNR, confusion matrices |
| Profiling | `time.perf_counter`, `tracemalloc`, `psutil` (`src/perf.py`) |
| Fix-and-verify agent | Python `ast` (exact span edits), `difflib`; optional local LLM via Ollama |
| GUI | PyQt6 |
| Testing | pytest / unittest |
