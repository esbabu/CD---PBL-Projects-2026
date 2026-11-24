# Changelog

## Stabilization

- Gated C++ behavioral execution behind the runtime opt-in and refused it for High/Critical security findings, matching Python and Java.
- Corrected Java `--release` selection so it is used only when the runtime is older than `javac`.
- Added request-workspace cleanup, startup cleanup for stale workspaces, explicit missing-Java-tool responses, and a loopback-only one-command startup script.
- Completed dependency and ignore manifests and added setup, dashboard, support, and limitation documentation.

## Phase 5a — Foundation

- Added the `src/languages/` adapter boundary, C++ registry adapter, explicit Python/Java/C/JavaScript support-coming stubs, extension mapping, and startup toolchain detection using real version-command output.
- Made every stub-adapter operation return an explicit support-coming status rather than empty success-shaped results.
- Added language selection and extension-based selection in the dashboard, language-aware `/api/analyze` and `/api/fix` requests, structured support-coming responses for stubs, and per-language categorization-engine/tool-version provenance.
- Made the loaded C++ TF-IDF + Logistic Regression categorizer explicit in Diagnostics and Auto-Heal provenance.
- Preserved the existing C++ analyzer and auto-heal implementations behind the C++ adapter boundary.

## Phase 5b — Python Adapter

- Replaced the Python stub with real `py_compile` diagnostics, bounded runtime checks, exception-type explanations, Python AST/Graphviz rendering, and rule-based healing with rechecks and optional behavioral tests.
- Added Python AST security checks to the language-keyed security registry and integrated Python diagnostics, security health, runtime disclosure, categorizer/interpreter provenance, and Auto-Heal results into the dashboard APIs.

## Phase 5c — Java Adapter

- Added opt-in runtime checks for Python and Java; static analysis is the default, behavioral test specs run only after opt-in, and High/Critical security findings block execution.
- Replaced the Java AST approximation with tree-sitter-java parsing, bounded/expandable tree rendering, partial trees for broken source, and a labeled fallback; added the tree-sitter dependencies.
- Added javac diagnostic caret data and rule-based explanations, explicit javac/java paths and versions, Java target-release provenance, and a warning for compiler/runtime major-version differences.
- Added javac-rechecked Java repairs for missing semicolons/imports, numeric String/int literals, and missing closing braces.
- Expanded Java security findings to report exact lines for dynamic process arguments, SQL concatenation, hardcoded credentials, weak randomness, empty catch blocks, stack-trace disclosure, and unsafe deserialization.
- Audited and verified all Java adapter endpoints, opt-in execution constraints, and auto-heal strategies against the Phase 5c checklist under `.venv\Scripts\python.exe` with 71/71 pytest passes and 4/4 passing end-to-end healing tests.

## Phase 2

- Expanded the C/C++ security analyzer with line-specific static rules, language-keyed rule registration, and weighted HEALTHY/MODERATE/UNHEALTHY verdicts.
- Added verdict, score, flagged-line details, and source-line highlighting to the dashboard; added endpoint coverage for six representative programs.

## Phase 3

- Added leakage-safe, stratified classifier evaluation with macro/weighted metrics, per-class results, confusion matrices, hard-rule attribution, and saved charts.
- Added a dashboard Model Evaluation tab with asynchronous evaluation and report visualization.
- Combined compile status and security findings into a Code health verdict; clarified trained-class versus rule-only macro-F1 and dataset-label provenance, and mapped the unsupported unused-variable rule output to `other`.

## Phase 4

- Expanded the Clang AST extraction to include complex C++ declarations, statements, expressions, templates, namespaces, lambdas, exceptions, switch/range/do logic, and destructor/new/delete patterns while filtering implicit and system-header nodes.
- Added node/depth limits, rendering controls, a readable legend, and unique PNG output names; partial trees are preserved for compile-error cases without blank tabs or crashes.
- Verified the AST renderer through the real dashboard analyze endpoint for complex class, state-machine, exception, and error-heavy cases while preserving the existing nested-sample output behavior.
- Corrected range-for and throw-node extraction for offset-only Clang locations, added a 300+ node fixture with working full-tree expansion, and surfaced likely missing-semicolon fault lines beside compiler-reported lines in Overview and Security Audit.
