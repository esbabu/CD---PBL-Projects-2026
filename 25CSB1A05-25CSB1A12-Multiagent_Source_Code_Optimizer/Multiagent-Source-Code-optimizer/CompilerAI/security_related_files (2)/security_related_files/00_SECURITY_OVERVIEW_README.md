# Security Subsystem: Complete Architecture & File Directory

This directory brings together **all core components, scanners, patchers, schemas, benchmark datasets, and verification test suites** powering the security aspect of this project.

---

## Directory Structure

```
securty related files/
│
├── 00_SECURITY_OVERVIEW_README.md               <-- You are here: Executive Guide & File Index
│
├── agents/
│   └── security_agent.py                        <-- Independent Security Audit Agent (Phase 4)
│
├── rules_and_scanners/
│   ├── security_rules.py                        <-- Static Security Rules Engine (6 CWE Domains)
│   └── prompt_templates.py                     <-- Neuro-Symbolic & CoT Prompt Templates
│
├── remediation_and_patching/
│   └── security_patcher.py                      <-- Deterministic Line-Level Security Patcher
│
├── analysis_and_detection/
│   ├── finding_schema.py                        <-- Canonical Defect Taxonomy & Deduplication
│   └── tool_runner.py                           <-- Multi-Engine SAST Runner (Clang-Tidy, Cppcheck)
│
├── benchmarks_and_evaluation/
│   ├── vulnerable_100.cpp                       <-- Ground-Truth 100-Vulnerability Benchmark
│   ├── vulnerable_100_evaluation_report.json    <-- Empirical Benchmark Evaluation Metrics
│   └── vulnerable_demo_eval.json                <-- Per-Sample Diagnostic Overlap & Detections
│
└── tests_and_verification/
    ├── test_security_week8.py                   <-- Security Agent Unit & Integration Test Suite
    ├── test_security_fix_in_optimization.py     <-- Line-Level Remediation in Optimization Tests
    └── test_vulnerable_100_regression.py         <-- Benchmark Automated Regression Test Runner
```

---

## Detailed File Descriptions & Security Roles

### 1. `agents/security_agent.py`
- **Role:** Independent Security Audit Agent operating at Phase 4 of the compiler pipeline, and usable standalone.
- **Key Capabilities:**
  - **Multi-Language Support:** First-class security auditing across **C/C++, Java, and Python** source code.
  - **Rich Terminal Reporting:** Direct CLI and terminal reporting with ANSI color coding, risk badges, detailed defect listings with line numbers, CWE IDs, and remediation instructions.
  - **Multi-Layered Audit:** Runs rule-based scanning, heuristic taint/allocation detection, conventional SAST tools, and semantic LLM reasoning.
  - **New Vulnerability Detection:** Compares candidate findings against baseline original findings to identify any newly created flaws.
  - **Transactional Rollback:** Immediately discards candidate code and restores pristine original code if high-severity flaws or regressions are detected.
  - **Security Scoring (0–100):** Computes qualitative risk posture (Critical/High/Medium/Low/None) and score change delta ($\Delta$).

### 2. `rules_and_scanners/security_rules.py`
- **Role:** Deep AST/Regex Static Security Rules Engine covering **6 Vulnerability Domains** across **C/C++, Java, and Python**:
  1. *Section A: Memory Safety & Resource Management* (CWE-120, CWE-121, CWE-122, CWE-125, CWE-193, CWE-242, CWE-401, CWE-415, CWE-416, CWE-476, CWE-762, CWE-775 unclosed streams).
  2. *Section B: Injection & Output Handling* (CWE-78 OS Command Injection in C/C++/Java/Python, CWE-89 SQLi across JDBC & Python cursor, CWE-94/95 Code Injection/eval/exec, CWE-502 Insecure Deserialization via pickle/ObjectInputStream, CWE-611 XXE in Java/Python, CWE-134 Format Strings).
  3. *Section C: Cryptography & Authentication* (CWE-208 Timing Discrepancy, CWE-327 Broken Crypto / DES / ECB, CWE-328 Weak Hash MD5/SHA-1 in hashlib/MessageDigest, CWE-338 Insecure PRNG random/Random, CWE-798 Hardcoded Credentials).
  4. *Section D: Concurrency & File System* (CWE-362 Race Conditions, CWE-367 TOCTOU, CWE-377 Insecure Temp Files mktemp, CWE-732 Permissive chmod, CWE-775 Resource Leaks).
  5. *Section E: Network Safety* (CWE-130 Header Length, CWE-295 Disabled TLS Verification verify=False / TrustManager, CWE-601 Open Redirect).
  6. *Section F: Undefined Behavior & Logic* (CWE-190 Integer Overflow, CWE-369 Division by Zero, CWE-489 Debug Mode Enabled, CWE-617 Assert Security Gates, CWE-562 Return Stack Address).

### 3. `remediation_and_patching/security_patcher.py`
- **Role:** Deterministic, High-Precision Security Remediation Engine.
- **Key Capabilities:**
  - Converts detected vulnerabilities directly into line-level fixes without stochastic hallucination.
  - C/C++ fixes: buffer overflows (`strcpy` $\rightarrow$ `strncpy`), unsafe input (`gets` $\rightarrow$ `fgets`), format strings (`printf(var)` $\rightarrow$ `printf("%s", var)`), timing attacks (`strcmp` $\rightarrow$ constant-time loop).
  - Python fixes: `eval(...)` $\rightarrow$ `ast.literal_eval(...)`, `hashlib.md5(...)` $\rightarrow$ `hashlib.sha256(...)`, `tempfile.mktemp()` $\rightarrow$ `tempfile.NamedTemporaryFile()`, `verify=False` $\rightarrow$ `verify=True`, `debug=True` $\rightarrow$ `debug=False`.
  - Java fixes: `MessageDigest.getInstance("MD5")` $\rightarrow$ `MessageDigest.getInstance("SHA-256")`, `new Random()` $\rightarrow$ `new java.security.SecureRandom()`, `Cipher.getInstance("DES")` $\rightarrow$ `Cipher.getInstance("AES/GCM/NoPadding")`.
  - Produces unified diffs and populates `[CWE-XXX FIX]` transformation cards for the Optimization Tab.

### 4. `analysis_and_detection/finding_schema.py`
- **Role:** Standardized Finding Schema and Cross-Tool Deduplication Engine.
- **Key Capabilities:**
  - Defines the unified `Finding` dataclass (severity, confidence, line, column, CWE, detection engine).
  - Groups disparate compiler diagnostics into **Canonical Defect Families** (e.g., merging Clang-Tidy `format-security`, Cppcheck `formatString`, and compiler warnings on identical lines).
  - Merges duplicate cards into multi-engine corroborated findings while preserving unique line numbers and jump-to-line navigation.

### 5. `analysis_and_detection/tool_runner.py`
- **Role:** Parallel Conventional SAST Tool Runner with Language Awareness.
- **Key Capabilities:**
  - Concurrently executes Clang-Tidy, Cppcheck, Flawfinder, Semgrep, and Address/Undefined-Behavior Sanitizers (ASan/UBSan) for C/C++.
  - Executes Python syntax compilation checks and AST verification for Python source.
  - Executes javac compilation and error diagnostics when Java source is provided.
  - Normalizes diverse tool outputs into the standard `Finding` schema with automated CWE tagging.

### 6. `benchmarks_and_evaluation/`
- **`vulnerable_100.cpp`:** Benchmark C/C++ suite featuring 100 ground-truth vulnerabilities across all 6 CWE categories.
- **`vulnerable_100_evaluation_report.json`:** Comprehensive empirical evaluation report documenting 100% recall and precision, multi-engine corroboration, and 35.4% duplicate card reduction.
- **`vulnerable_demo_eval.json`:** Detailed per-defect audit and engine overlap analysis.

### 7. `tests_and_verification/`
- **`test_security_week8.py`:** 49 targeted tests validating C/C++, Java, and Python rule-based detection, AST validation, taint heuristics, use-after-free, new vulnerability flagging, rollback triggering, terminal report formatting, and score comparison.
- **`test_security_fix_in_optimization.py`:** Tests verifying that deterministic security fixes appear in the Optimization tab with CWE badges, line numbers, and diffs.
- **`test_vulnerable_100_regression.py`:** Automated evaluation runner that runs the analyzer against `vulnerable_100.cpp` and validates ground-truth detection.

---

## How to Run Security Agent & Verification Tests

### 1. Running Security Agent directly on the terminal
```powershell
# Scan any C/C++, Java, or Python source file and display results directly on the terminal:
python agents/security_agent.py path/to/file.py
python agents/security_agent.py path/to/file.java
python agents/security_agent.py path/to/file.cpp

# Or through run_agent.py CLI:
python run_agent.py security path/to/file.py
python run_agent.py security path/to/file.java
python run_agent.py security path/to/file.cpp
```

### 2. Running Security Verification Tests
From the project directory, run:

```powershell
# Run the complete multi-language security test suite
python -m pytest "security_related_files/tests_and_verification/test_security_week8.py" -v

# Run the security patcher and optimization remediation tests
python -m pytest "security_related_files/tests_and_verification/test_security_fix_in_optimization.py" -v

# Run the 100-vulnerability benchmark evaluation runner
python -m pytest "security_related_files/tests_and_verification/test_vulnerable_100_regression.py" -v
```
