# Multi-Language Compiler Back End and Security Intelligence

This phase extended the Code Comment Generator from Python-only security analysis to **six
languages: Python, Java, C#, C++, COBOL and Rust**, plus C, which was already a comment
language. It adds:
- **Rules:** 14 rules (64 in total).
- **Knowledge base:** 1,512 entries, built from MITRE CWE, MITRE CAPEC and NIST SARD.
- **Three detection engines:** rule-based, ML and neuro-symbolic.
- **Dashboard:** 9 vulnerability classes.

Every number below was measured with the commands in [§10](#10-reproducing).

| | |
|---|---|
| Languages with IR, CFG, data flow and taint analysis | Python, Java, C#, C, C++, Rust, COBOL |
| Rules | 64 (SEC001–SEC064) |
| Knowledge base | 1,512 unique entries: 956 CWE weaknesses + 556 CAPEC attack patterns; 566 with code examples |
| ML detector | 7 models trained on the security dataset (Rust and COBOL small-n); test F1 Java 0.88, C# 0.82, C 0.83, C++ 0.64, Python 0.81 — see [SECURITY_DATASET_AND_EVALUATION.md](SECURITY_DATASET_AND_EVALUATION.md) |
| Security dataset | 23,131 samples, 774,960 lines, 7 languages, 91 long programs of 1,000–2,000 lines |
| Realistic fixtures | 7 programs, 83 hand-marked vulnerabilities, all found, 0 false positives |
| Tests | 680 passing |
| Python OWASP results | unchanged (F1 0.904 / 0.955 / 0.862) |

---

## 1. Architecture

```
source ─┬─ Python ─────────── ast ─────────────── ir.lowering ──────┐
        ├─ Java, C#, C, C++, Rust ─ tree-sitter ── multilang.lower ─┤   same 3-address IR
        └─ COBOL ──────────── multilang.cobol (own parser) ─────────┘   (ir/ir_nodes.py)
                                                                       │
              analysis.cfg_builder → analysis.dfa_engine (reaching definitions, live variables)
                                   → analysis.pattern_detector (P001–P007) — unchanged, every language
                                                                       │
   ┌───────────────────────────┬──────────────────────────────┬────────┴────────────────────┐
   │ rule-based engine          │ ML engine                     │ neuro-symbolic engine         │
   │ multilang.taint (per-lang  │ vulnml: TF-IDF + logistic     │ vulnml.fusion: rules + ML +   │
   │ specs) + memory + patterns │ regression per language       │ knowledge-base sink conditions│
   └───────────────────────────┴──────────────────────────────┴───────────────────────────────┘
                                                                       │
          security.findings.Finding  →  CLI · GUI (9-class dashboard) · agent · RAG explanations
```

Each part is in its own module:

| Part | Module |
|---|---|
| tree-sitter → IR (Java, C#, C, C++, Rust) | `src/multilang/lower.py` |
| COBOL parser → IR | `src/multilang/cobol.py` |
| sources, sinks and sanitizers per language | `src/multilang/specs.py` |
| language-neutral taint engine | `src/multilang/taint.py` |
| use after free, double free, unchecked malloc | `src/multilang/memory.py` |
| syntax rules (crypto, TLS, XXE, credentials, races, auth, unsafe code) | `src/multilang/patterns.py` |
| entry point, capability table | `src/multilang/analyzer.py` |
| 9 classes | `src/security/categories.py` |
| rule × language coverage | `src/security/coverage.py` |
| knowledge base builder | `src/rag/build_kb.py` → `src/rag/data/security_kb.json.gz` |
| ML detector and fusion | `src/vulnml/` |
| comment features for C#, Rust and COBOL | `src/languages/generic_extract.py` |

The Python analyzer (`src/security`) is unchanged. It keeps its richer front end:
cross-file analysis, constant propagation and the fix agent.

---

## 2. Front ends

**Java, C#, C, C++, Rust (tree-sitter).** Every function, method and constructor is lowered
to basic blocks of three-address code.
- **Statements:** declarations, assignments (including field, element and pointer stores),
  `if`/`else`, all loop forms, `switch`/`match`, `try`/`catch`/`finally`, `return`, `throw`,
  `break`, `continue`, Rust `unsafe` blocks, and C# `using`/`lock`.
- **Calls:** each call keeps its receiver, method, argument operands, literal arguments,
  and the receiver's declared type when it is known. Examples: `Statement.executeQuery` and
  `Data<Connection>` → `Connection`.
- **Language details:**
  - C# object initialisers become named arguments;
  - Rust macro arguments (`format!(…)`) are re-parsed and lowered as real expressions;
  - `std::cin >> x` and `std::ifstream f(path)` are modelled, including C++'s "most vexing
    parse".
- **Fallback:** constructs that are not modelled are lowered conservatively, so data still
  flows through them, and each one is listed in `IRFunction.unsupported`.

**COBOL (own parser).** It handles:
- fixed and free source formats;
- DATA DIVISION items: level, PIC, VALUE, OCCURS and the group hierarchy;
- LINKAGE parameters;
- `SELECT … ASSIGN TO DYNAMIC`;
- PROCEDURE DIVISION statements: ACCEPT, DISPLAY, MOVE, COMPUTE/ADD/…, STRING, UNSTRING,
  CALL (static, dynamic, SYSTEM), EXEC SQL (EXECUTE IMMEDIATE, PREPARE, static SQL with host
  variables), EXEC CICS (RECEIVE, WEB READ, LINK, XCTL, SEND), IF/ELSE, EVALUATE, PERFORM
  (inline, UNTIL), OPEN/READ/WRITE;
- subscripts and reference modification.

Paragraphs are blocks inside a loop, because PERFORM can run them in any order. Data flow is
therefore flow-sensitive within a paragraph and flow-insensitive across paragraphs.

**Comments** for the new languages:
- C# gets XML documentation comments (`/// <summary>`, `<param>`, `<returns>`, `<exception>`);
- Rust gets rustdoc (`/// # Arguments`, `# Returns`, `# Errors`, `# Panics`);
- COBOL gets `*>` blocks above each paragraph and the program, starting in column 7 (valid in
  both formats).

Running the pipeline again on its own output adds nothing.

---

## 3. Support by language

`full` means modelled like Python. `partial` means it works within the limits named.
`none` means not available.

| Capability | Python | Java | C# | C | C++ | Rust | COBOL |
|---|---|---|---|---|---|---|---|
| Parsing | full | full | full | full | full | full | partial (no COPY expansion) |
| IR + CFG + data flow + P001–P007 | full | full | full | full | full | full | full (flow-insensitive across paragraphs) |
| Taint analysis | full (cross-file) | full (one file) | full (one file) | full (one file) | full (one file) | full (one file) | partial (one program) |
| Rules implemented | 50 | 33 | 35 | 27 | 29 | 22 | 8 |
| CWEs detected | 41 | 31 | 33 | 24 | 26 | 21 | 8 |
| Memory safety | n/a | n/a | partial (unsafe blocks) | partial (UAF, double free, unchecked malloc; no aliases) | partial (same + delete) | partial (unsafe operations flagged) | partial (subscript / ref-mod) |
| ML detector | partial | partial | partial | partial | partial | partial (small-n, custom data only) | partial (small-n, custom data only) |
| Neuro-symbolic engine | full | full | full | full | full | partial (small-n model not used) | partial (small-n model not used) |
| RAG explanations | full | full | full | full | full | full | full |
| Fix-and-verify agent | full (12 rules) | none | none | none | none | none | none |
| Comment generation | full (3 engines) | full | full | full | full | full | full |

ML detector notes:
- All models are trained on the security dataset (§7): test F1 Python 0.81, Java 0.88, C# 0.82,
  C 0.83, C++ 0.64; Rust and COBOL have a few dozen custom samples only (small-n).
- All are weak on hand-written code (§7).

The same table is available in code as `src/multilang/analyzer.py: CAPABILITIES`.

---

## 4. Vulnerability coverage

The 8 original classes still use their original rules. Every other rule is grouped under
**Others**, and each finding keeps its detailed rule ID, family and CWE.

The families added in this phase, and where they are implemented:

| Family | Rules | Languages |
|---|---|---|
| Command injection | SEC002 | all 7 |
| SSRF | SEC016 | Python, Java, C#, Rust |
| XXE | SEC018 | Python, Java, C#, C, C++ |
| Path traversal | SEC013, SEC042 | all 7 |
| Insecure deserialization | SEC009, SEC010 | Python, Java, C#, C++, Rust |
| Authentication / authorization | SEC045, SEC047, SEC061 | Python, Java, C#, Rust (JWT) |
| Hard-coded credentials | SEC003 | all 7 |
| Insecure cryptography | SEC004, SEC030–SEC036 | Python, Java, C#, C, C++, Rust |
| Buffer overflow | SEC051, SEC052, SEC053 | C, C++ |
| Integer overflow | SEC055 | C, C++ |
| Use after free / double free | SEC056, SEC057 | C, C++ |
| Race conditions | SEC059 (TOCTOU), SEC063 (shared mutable state) | Java, C#, C, C++, Rust |
| Format strings | SEC026 | Python, C, C++ |
| Memory safety | SEC054, SEC058, SEC060 | C, C++, C#, Rust, COBOL |
| Improper input validation | SEC054, SEC062 | C, C++, COBOL, Rust |
| Language-specific | Rust `unsafe` / `static mut` / panicking parse; C# `BinaryFormatter`, `TypeNameHandling`, `[AllowAnonymous]`; Java servlet fields, `@PermitAll`, XML factories; COBOL dynamic CALL / EXEC SQL / ref-mod | as listed |

### Every rule and where it is implemented

Every ✓ is exercised by a test: either a language fixture or a snippet in
`tests/test_multilang_coverage.py`. The test `test_every_claimed_pair_is_exercised` enforces
this.

| Rule | Title | CWE | Class | Py | Java | C# | C | C++ | Rust | COBOL |
|---|---|---|---|---|---|---|---|---|---|---|
| SEC001 | Code injection via dynamic evaluation | CWE-95 | Code Injection | ✓ | ✓ |  |  |  |  |  |
| SEC002 | OS command injection | CWE-78 | Command Injection | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| SEC003 | Hardcoded secret | CWE-798 | Others | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| SEC004 | Weak cryptographic hash | CWE-328 | Weak Hashing | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  |
| SEC005 | SQL injection | CWE-89 | SQL Injection | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| SEC006 | Bare except clause | CWE-396 | Others | ✓ |  |  |  |  |  |  |
| SEC007 | Mutable default argument |  | Others | ✓ |  |  |  |  |  |  |
| SEC008 | assert used for runtime checks | CWE-703 | Others | ✓ |  |  |  |  |  |  |
| SEC009 | Unsafe deserialization | CWE-502 | Insecure Deserialization | ✓ | ✓ | ✓ |  | ✓ | ✓ |  |
| SEC010 | Unsafe YAML load | CWE-502 | Insecure Deserialization | ✓ |  |  |  |  |  |  |
| SEC011 | Insecure randomness in a security context | CWE-338 | Weak Randomness | ✓ | ✓ | ✓ | ✓ | ✓ |  |  |
| SEC012 | Hardcoded network address | CWE-1051 | Others | ✓ |  |  |  |  |  |  |
| SEC013 | Path traversal | CWE-22 | Path Traversal | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| SEC014 | Cross-site scripting (XSS) | CWE-79 | Cross-Site Scripting | ✓ | ✓ | ✓ |  |  | ✓ | ✓ |
| SEC015 | Server-side template injection | CWE-1336 | Code Injection | ✓ |  |  |  |  |  |  |
| SEC016 | Server-side request forgery (SSRF) | CWE-918 | Others | ✓ | ✓ | ✓ |  |  | ✓ |  |
| SEC017 | Open redirect | CWE-601 | Others | ✓ | ✓ | ✓ |  |  | ✓ |  |
| SEC018 | XML external entity (XXE) processing | CWE-611 | Others | ✓ | ✓ | ✓ | ✓ | ✓ |  |  |
| SEC019 | LDAP injection | CWE-90 | Others | ✓ | ✓ | ✓ | ✓ | ✓ |  |  |
| SEC020 | XPath injection | CWE-643 | Others | ✓ | ✓ | ✓ |  |  |  |  |
| SEC021 | NoSQL injection | CWE-943 | Others | ✓ |  |  |  |  |  |  |
| SEC022 | Log injection | CWE-117 | Others | ✓ | ✓ | ✓ |  |  | ✓ |  |
| SEC023 | HTTP header injection | CWE-113 | Others | ✓ | ✓ | ✓ |  |  |  |  |
| SEC024 | Regular-expression injection (ReDoS) | CWE-1333 | Others | ✓ | ✓ | ✓ |  |  | ✓ |  |
| SEC025 | Unsafe reflection: module chosen by user input | CWE-470 | Others | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ |
| SEC026 | Format-string injection | CWE-134 | Others | ✓ |  |  | ✓ | ✓ |  |  |
| SEC027 | Mass assignment via setattr | CWE-915 | Others | ✓ |  |  |  |  |  |  |
| SEC028 | Trust boundary violation (untrusted data in session) | CWE-501 | Others | ✓ | ✓ | ✓ |  |  |  |  |
| SEC029 | Debug mode enabled | CWE-489 | Others | ✓ |  | ✓ |  |  |  |  |
| SEC030 | TLS certificate verification disabled | CWE-295 | Others | ✓ |  |  | ✓ | ✓ | ✓ |  |
| SEC031 | Unverified SSL context | CWE-295 | Others | ✓ |  | ✓ | ✓ | ✓ |  |  |
| SEC032 | Insecure SSL/TLS protocol version | CWE-327 | Others | ✓ | ✓ | ✓ | ✓ | ✓ |  |  |
| SEC033 | Broken or weak cipher | CWE-327 | Others | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  |
| SEC034 | ECB block-cipher mode | CWE-327 | Others | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  |
| SEC035 | Insufficient cryptographic key size | CWE-326 | Others | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  |
| SEC036 | Static initialisation vector or nonce | CWE-329 | Others | ✓ | ✓ | ✓ |  |  |  |  |
| SEC037 | Insecure temporary file (tempfile.mktemp) | CWE-377 | Others | ✓ |  |  | ✓ | ✓ |  |  |
| SEC038 | Overly permissive file permissions | CWE-732 | Others | ✓ |  |  |  |  |  |  |
| SEC039 | Service bound to all network interfaces | CWE-1327 | Others | ✓ |  |  |  |  |  |  |
| SEC040 | Cleartext network protocol | CWE-319 | Others | ✓ |  |  |  |  |  |  |
| SEC041 | Cleartext HTTP request | CWE-319 | Others | ✓ |  |  |  |  |  |  |
| SEC042 | Unsafe archive extraction (tar slip) | CWE-22 | Path Traversal | ✓ |  |  |  |  |  |  |
| SEC043 | Template auto-escaping disabled | CWE-79 | Cross-Site Scripting | ✓ |  |  |  |  |  |  |
| SEC044 | Cookie without Secure / HttpOnly flag | CWE-614 | Others | ✓ | ✓ | ✓ |  |  |  |  |
| SEC045 | CSRF protection disabled | CWE-352 | Others | ✓ | ✓ | ✓ |  |  |  |  |
| SEC046 | Permissive CORS policy (any origin) | CWE-942 | Others | ✓ | ✓ | ✓ |  |  | ✓ |  |
| SEC047 | JWT signature not verified | CWE-347 | Others | ✓ | ✓ | ✓ |  |  | ✓ |  |
| SEC048 | SSH host key not verified | CWE-295 | Others | ✓ |  |  |  |  |  |  |
| SEC049 | Exception silently swallowed | CWE-390 | Others | ✓ | ✓ | ✓ |  | ✓ |  |  |
| SEC050 | Sensitive data written to a log | CWE-532 | Others | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| SEC051 | Use of an inherently dangerous function | CWE-242 | Others |  |  |  | ✓ | ✓ |  |  |
| SEC052 | Buffer overflow: unbounded copy into a fixed-size buffer | CWE-120 | Others |  |  |  | ✓ | ✓ |  |  |
| SEC053 | Buffer copy with an untrusted length | CWE-805 | Others |  |  |  | ✓ | ✓ |  |  |
| SEC054 | Array index from untrusted input | CWE-129 | Others |  |  |  | ✓ | ✓ |  | ✓ |
| SEC055 | Integer overflow in an allocation size | CWE-190 | Others |  |  |  | ✓ | ✓ |  |  |
| SEC056 | Use after free | CWE-416 | Others |  |  |  | ✓ | ✓ |  |  |
| SEC057 | Double free | CWE-415 | Others |  |  |  | ✓ | ✓ |  |  |
| SEC058 | Unchecked allocation result (NULL dereference) | CWE-690 | Others |  |  |  | ✓ | ✓ |  |  |
| SEC059 | Time-of-check to time-of-use race (TOCTOU) | CWE-367 | Others |  | ✓ | ✓ | ✓ | ✓ | ✓ |  |
| SEC060 | Unsafe memory operation (Rust / C# unsafe code) | CWE-119 | Others |  |  | ✓ |  |  | ✓ |  |
| SEC061 | Missing authorization on a state-changing endpoint | CWE-862 | Others |  | ✓ | ✓ |  |  |  |  |
| SEC062 | Unchecked parsing of untrusted input (panic / crash) | CWE-20 | Others |  |  |  |  |  | ✓ |  |
| SEC063 | Shared mutable state without synchronization | CWE-362 | Others |  | ✓ | ✓ |  |  | ✓ |  |
| SEC064 | Possible vulnerability (neuro-symbolic: ML prediction + semantic evidence) |  | Others |  |  |  |  |  |  |  |

---

## 5. Security knowledge base (1,512 entries)

`python -m src.rag.build_kb` builds `src/rag/data/security_kb.json.gz` (1.1 MB) from local
copies of authoritative sources:

| Source | Entries | What each entry holds |
|---|---|---|
| MITRE CWE 5.0 | 956 weaknesses (all that are not deprecated) | description, extended description, likelihood of exploit, consequences, applicable languages, detection methods, mitigations, demonstrative examples marked Bad/Good, observed CVEs (linked to cve.org / NVD), related weaknesses and attack patterns, taxonomy mappings (OWASP Top Ten, CERT…), references |
| MITRE CAPEC 3.9 | 556 attack patterns (all that are not deprecated or obsolete) | description, likelihood, typical severity, prerequisites, execution flow, mitigations, example instances, related CWEs |
| NIST SARD Juliet 1.3 | examples added to 170 CWE entries (Java examples for 107 CWEs, C 104, C++ 29, C# 103) | a flawed (`bad`) and a fixed (`good`) function from a real test case |

Integrity checks (in `tests/test_security_intelligence.py`):
- IDs are unique;
- descriptions are at least 98 % distinct;
- every entry has a source and URL;
- descriptions are at least 30 characters long.

**Documented vs. implemented.** Every CWE entry has a `detection` field naming the rules
and languages that detect it. 53 of the 956 CWEs are detected by this project; the rest are
documented only. (The rules name 54 distinct CWEs: SEC037, `tempfile.mktemp`, keeps CWE-377 as
Bandit does, but MITRE marked CWE-377 *Deprecated* in CWE 5.0 for its ambiguous name, so the
knowledge base has no entry for it.) The GUI says this for each scan, for example "Java: 33 rules detect 31 CWEs
| knowledge base documents 956 CWEs + 556 attack patterns".

**Severity.** CAPEC entries carry MITRE's own Typical_Severity. CWE has no severity field,
so a CWE entry carries the severity of the project rule that detects it (labelled as such),
or none. No severity was invented.

**RAG integration.** All entries are BM25 documents alongside the rule cards and examples
(1,625 documents). `explain_finding()` combines:
- the finding's own source-code evidence (the trace);
- the CWE description, consequences and mitigations;
- the closest vulnerable and fixed example, preferring the finding's language (a Java finding
  gets a Juliet Java example);
- observed CVEs and attack patterns.

`python -m src.rag explain <file>` prints this for every finding in any of the seven
languages. The agent attaches the same guidance to findings it leaves for a manual fix.

---

## 6. Rule-based engine

**Taint analysis** (`multilang/taint.py`) is a forward may-analysis over each function's CFG.
- **Sources:** HTTP request APIs, framework-bound parameters (`@RequestParam`,
  `[FromQuery]`, public ASP.NET controller actions, Rust extractor types), `argv`, `stdin`,
  `recv`, `getenv`, COBOL ACCEPT, CICS RECEIVE and LINKAGE items.
- **Contexts:** each rule has its own security context. Sanitizers clear only their own
  contexts. For example, `Integer.parseInt` removes every injection context but keeps
  `size`/`index`, because a parsed number can still overflow a buffer.
- **Refinement on branch edges:**
  - bounds checks (`n < sizeof buf`, `strlen(s) < N`, combined with `&&` / `||`);
  - string allow-lists (`x.equals("lit")`);
  - regex validation (`x.matches("[a-z]+")`, COBOL `IS NUMERIC`).
- **Calls within a file:** summarised (parameter → return, parameter → sink) and iterated to
  a fixed point.

**Memory safety** (`multilang/memory.py`, C/C++) tracks pointers freed on *some* path and on
*every* path:
- use after free: high confidence when the free happens on every path;
- double free;
- allocation results used before a NULL check.

**Syntax rules** (`multilang/patterns.py`) cover:
- weak hashes and ciphers, ECB, short keys and static IVs;
- disabled TLS checks and old TLS versions;
- XXE-prone XML factories without hardening;
- dangerous deserializers;
- hard-coded credentials;
- cookie flags, CSRF, CORS and JWT verification;
- `gets`, unbounded `scanf("%s")`, non-literal format strings;
- TOCTOU races;
- servlet/controller shared state;
- Rust/C# unsafe operations;
- missing authorization.

**Fixtures.** Seven realistic programs:
- a Java servlet and a Spring controller;
- an ASP.NET controller;
- a C network daemon;
- a C++ service;
- Rust actix handlers;
- a COBOL CICS transaction.

83 vulnerabilities are marked by hand, each with a safe twin. All 83 are found, and nothing
else is reported (`tests/test_multilang_security.py`).

---

## 7. ML engine

The ML detectors are trained by the reproducible pipeline of the second phase on the security
dataset (Juliet, OWASP and hand-labelled samples; 70 / 15 / 15 split by group, hyperparameters
chosen on validation, one score on test). The method, the dataset and the side-by-side comparison
with the other engines are in [SECURITY_DATASET_AND_EVALUATION.md](SECURITY_DATASET_AND_EVALUATION.md).

**Model:** TF-IDF over normalised code tokens with logistic regression, one model per language,
over the vulnerability families plus safe.

**Leakage controls.** Juliet gives away its labels in names and comments, so these are removed:
comments (`/* FLAW */`, `/* FIX */`); every identifier containing a CWE number, `good` or `bad`;
access modifiers (the first models scored a suspicious precision of 1.0 because `bad()` is
`public` and the `good` helpers are `private`). Related samples never cross splits (§1.2 of the
dataset document).

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

**Domain shift.** Juliet is synthetic. The per-source rows of the comparison show the models
recall far fewer vulnerable functions in hand-written code than in Juliet, and raise more false
alarms there. That is why the ML model is a supporting signal, not a detector on its own (§8).
Rust and COBOL models are trained on a few dozen custom samples only; they are reported but not
used by the neuro-symbolic engine.

---

## 8. Neuro-symbolic engine

`vulnml/fusion.py` combines three kinds of evidence for every function:
- **neural:** the ML family, P(vulnerable), and the tokens behind it;
- **symbolic:** the rule findings;
- **semantic:** a detection condition from the knowledge base and sink tables: does the
  function call a sink API of the predicted family with non-constant data?

| Situation | What happens |
|---|---|
| rule finding + ML agrees (P ≥ 0.6, same family) | kept; "ML detector agrees" recorded; a *potential* taint finding whose only doubts are resolution heuristics is upgraded to *confirmed* when P ≥ 0.8 |
| rule finding + ML says safe (P < 0.2) | kept: explicit symbolic evidence wins; the disagreement is recorded |
| no rule finding, ML P ≥ 0.7, and the semantic condition holds | new **SEC064** "Possible \<family\> (neuro-symbolic)", status *potential*, with the ML tokens and the sink call as its trace |
| ML alone, no semantic evidence | not reported (kept in the run's `unconfirmed` list) |

On the seven fixtures (dataset-trained models), the engine:
- recorded 44 agreements (C 11, Java 18, C# 9, C++ 6);
- upgraded 3 potential taint findings to confirmed (2 Java, 1 C#);
- recorded 5 disagreements, where the model calls a function safe that a rule flags — the
  domain shift of §7; the rule findings are kept;
- added no SEC064 findings, so the safe twins stay clean.
Rust and COBOL findings are unchanged (no model in fusion). On the dataset's test split the
engine flags 40 test units the rules miss, 39 of them correctly (see SECURITY_DATASET_AND_EVALUATION.md §3.1).

Select it with `--engine neurosymbolic` (CLI) or the **Neuro-symbolic (rules + ML)** option
next to *Scan Editor Code* (GUI).

---

## 9. Dashboard

- **Vulnerability classes chart:** always shows all nine classes, zeros included, with
  "Others" in grey (screenshots B22 and B23).
- **Findings table:** has a *Class* column next to the rule and CWE.
- **Report JSON:** contains `by_class` and a `class` per issue.
- **Status line:** separates implemented detection from documented knowledge for the
  scanned language.

---

## 10. Reproducing

```bash
# data (git-ignored .benchmarks/): MITRE CWE + CAPEC XML, NIST SARD Juliet 1.3 (Java, C/C++, C#)
#   https://cwe.mitre.org/data/xml/cwec_latest.xml.zip  https://capec.mitre.org/data/xml/capec_latest.xml
#   https://samate.nist.gov/SARD/downloads/test-suites/…juliet-test-suite-for-{java,c-cplusplus,csharp}-v1-3.zip
python -m src.rag.build_kb                       # knowledge base (1,512 entries)
python -m src.dataset.build                      # security dataset → datasets/security_dataset/v1/
python -m src.vulnml.pipeline train              # ML detectors (tuned on validation) → outputs/vulnml/
python -m src.vulnml.pipeline evaluate           # rule-based vs ML vs neuro-symbolic → outputs/eval/
python -m src.perfbench                          # block-wise profile → outputs/perf/benchmark.json
python -m src.security tests/multilang_fixtures/java/AccountServlet.java   # any language
python -m src.security path/to/file.cs --engine neurosymbolic
python -m src.rag explain tests/multilang_fixtures/c/netconf.c             # findings + knowledge
python -m src.main tests/multilang_fixtures/rust/handlers.rs --security-report --analysis
python -m pytest                                 # 680 tests
```

## 11. Limitations

- Taint analysis for the new languages works on one file at a time. Only Python has
  cross-file analysis.
- C/C++ memory safety has no alias analysis: after `q = p; free(p)`, a use of `q` is missed.
  Uses after a free on only some paths are reported at medium confidence.
- Method-name sinks on objects of unknown type need a receiver-name hint (`conn`, `log`, …)
  and are reported at medium confidence.
- COBOL:
  - COPY books are not expanded;
  - data flow across paragraphs is flow-insensitive;
  - nested programs and declaratives are not modelled.
- The ML models generalise poorly from Juliet to hand-written code (§7). Rust and COBOL have
  small-n models only.
- The fix-and-verify agent only patches Python. Other languages get RAG guidance instead.
- The knowledge base documents far more weaknesses (956) than the project detects (53 CWEs),
  and the GUI and the `detection` field say so.
