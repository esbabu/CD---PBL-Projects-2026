# IntelliFix: Formal Automata-Grounded Python Error Diagnosis & Auto-Repair Engine

> **Academic Submission — Theory of Computation & Formal Languages (SEM 3, NIT Warangal)**  
> **Course:** CS / Automata Theory & Compiler Principles  
> **Project Title:** IntelliFix — Multi-Tier Python Error Diagnostic, AST Optimization & Autonomous Program Repair Engine  

---

## 📋 Executive Summary

**IntelliFix** is an academic compiler and program-analysis engine that bridges the foundations of **Theory of Computation (TOC)** with automated developer tooling. It implements deterministic formal language models (Finite Automata, Pushdown Automata, Context-Free Grammars, Control Flow Graphs) combined with static AST analysis, intermediate code optimization, and a 4-tier resilient error repair pipeline.

The system diagnoses, explains, and safely repairs 25+ Python built-in and standard-library exception types while enforcing strict execution boundaries through a multi-gate cryptographic security shield.

---

## 🚀 Quick Evaluation Guide (For Evaluator & Professor)

To evaluate the system quickly, run any of the following self-contained commands from the extracted project root:

| What to Run | Command | Description / Expected Output |
| :--- | :--- | :--- |
| **1-Click Master Verification** | `python verify_all_features.py` | Automated verification of all 9 core subsystems (DFAs, PDAs, CFG, Merkle Ledger, Shield, Dual-Key, etc.). Returns `ALL 9 SYSTEMS FULLY OPERATIONAL AND VERIFIED!`. |
| **Deep Compiler Analysis Verification** | `python reverify_compiler_features.py` | Exhaustive check of Symbol Tables, TAC/SSA IR, Kildall Taint Dataflow, 5-Pass IR Optimizer, and SMT-style Translation Validation. |
| **Launch Web IDE Studio** | `powershell -ExecutionPolicy Bypass -File .\start_app.ps1`<br>*(or `python app.py`)* | Launches the full-featured interactive web workbench at **`http://127.0.0.1:5000`** with real-time automata animations, AST tree views, and live editor. |
| **Standalone Desktop Executable** | Run `dist\TOC_Studio_Standalone.exe`<br>*(or `python desktop_app.py`)* | Zero-install single-file desktop GUI executable for Windows (or run via Python). |
| **Command-Line Interface (CLI)** | `python intellifix.py T_errors1.py` | Analyzes a Python file, diagnoses errors across AST passes, and displays unified diffs and fix status. |
| **Automated Unit Test Suites** | `python -m unittest tests_offline tests_rules tests_autofix tests_dfa tests_pda tests_shield_policy` | Executes offline unit tests covering formal automata, deterministic repair rules, and security policies (580+ tests passing). |

---

## 🧩 Formal Theory of Computation (TOC) Foundations

IntelliFix directly implements core mathematical models from formal language theory:

### 1. Deterministic Finite Automata (DFA) & Lexical Analysis (`dfa.py`, `tokenizer.py`, `automaton_engine.py`)
- **Mathematical 5-Tuple Formulation:** $M = (Q, \Sigma, \delta, q_0, F)$
- **Lexical Construction:** Handcrafted deterministic state machines for Python identifiers ($[a\text{-}zA\text{-}Z\_][a\text{-}zA\text{-}Z0\text{-}9\_]*$), decimal numbers, and underscore-separated integer literals.
- **Automata Algorithms:** 
  - Regular Expression $\to$ Thompson NFA $\to$ Subset Construction DFA $\to$ **Hopcroft $O(n \log n)$ State Minimization**.
  - Interactive Mermaid-generated state transition diagrams and live state-stepping.
  - Verified with 0 token mismatches against Python's standard library `tokenize` module across 66,000+ token permutations.

### 2. Pushdown Automata (PDA) for Dyck Languages (`pda_engine.py`, `bracket_checker.py`)
- **Mathematical 7-Tuple Formulation:** $P = (Q, \Sigma, \Gamma, \delta, q_0, Z_0, F)$
- **Language Recognition:** Recognizes the Dyck-3 language $L_{\text{Dyck}} = \{ w \in \{ (, ), [, ], \{, \} \}^* \mid \text{properly nested} \}$ over stack alphabet $\Gamma = \{ Z_0, (, [, \{ \}$.
- **Tape & Stack Step Animator:** Tracks stack push/pop transitions step-by-step with stack-bottom symbol $Z_0$ and surgical syntax error recovery.
- **Mutant Testing:** Validated against 350+ deterministic AST mutants with 91.4% diagnostic agreement with native Python compiler syntax errors.

### 3. Context-Free Grammars & Control Flow Graphs (CFG) (`cfg_engine.py`)
- **Control Flow Graph Generation:** Partitions Python AST into basic blocks $B_i$ connected by directed control transfer edges $(B_i, B_j)$.
- **McCabe Cyclomatic Complexity:** Computes $M = E - V + 2P$ to identify high-risk execution branches and recursive cycles.
- **Complexity Heatmaps:** Renders function-level complexity scores and visual block graphs in real time.

### 4. Advanced Compiler Passes & Semantic Symbol Table (`semantic_analyzer.py`, `ir_generator.py`, `ir_optimizer.py`)
- **Semantic Analysis & Scope Resolution:** Builds hierarchical symbol tables across Global, Enclosing, Local, and Built-in (LEGB) scopes; provides symbol-grounded fixes for `UnboundLocalError` and `NameError`.
- **Three-Address Code (TAC) & Static Single Assignment (SSA):** Lowers Python AST into linearized 3-address instructions and inserts $\phi$-nodes at confluence basic blocks.
- **5 Formal Optimization Passes:**
  1. *Constant Folding & Propagation:* Statically evaluates compile-time arithmetic.
  2. *Strength Reduction:* Converts costly operators into cheaper equivalents (e.g., $x \times 2 \to x + x$).
  3. *Common Subexpression Elimination (CSE):* Reuses previously computed values within basic blocks.
  4. *Loop-Invariant Code Motion (LICM):* Hoists loop-independent computations into loop pre-headers.
  5. *Security-Aware Dead Code Elimination (DCE):* Safely prunes unused statements while strictly preserving cryptographic zeroing and memory scrubbing instructions.

### 5. Algorithmic Optimization Engine (`code_quality.py`)
- **Cubic-to-Quadratic Transformation ($O(N^3) \to O(N^2)$):** Statically inspects nested loop patterns, identifies hashable lookups, and automatically rewrites nested iteration into hash-set membership ($O(1)$ lookups).
- **Halstead Complexity & Maintainability Metrics:** Tracks volume, difficulty, effort, and code-smell indicators.

### 6. Translation Validation & Equivalence Prover (`translation_validator.py`)
- Statically and differentially validates that an automated repair preserves input-output semantics:
  - Generates fuzzing inputs across valid domains.
  - Compares original and patched outputs; flags semantic regressions with concrete counterexamples.

---

## 🏗️ Multi-Tier Architecture & Fallback Hierarchy

When a user program triggers an unhandled exception or static defect, IntelliFix resolves it through a resilient 4-tier pipeline:

```
                  User Code / Exception Traceback
                                │
                                ▼
        ┌──────────────────────────────────────────────┐
        │ 1. Deterministic Rule Engine (25+ Types)     │ ──(Match)──► Sub-millisecond, zero-hallucination fix
        └──────────────────────┬───────────────────────┘
                               │ (Unrecognized pattern)
                               ▼
        ┌──────────────────────────────────────────────┐
        │ 2. Grounded AI Tier (Gemini / Groq)          │ ──(Key Valid)──► LLM repair with format validation
        └──────────────────────┬───────────────────────┘
                               │ (Offline / Rate limit / Quota / Reject)
                               ▼
        ┌──────────────────────────────────────────────┐
        │ 3. Deterministic Offline Guide (25+ Types)   │ ──(Slot Fill)──► Deterministic slot-filled explanation
        └──────────────────────┬───────────────────────┘
                               │ (Fail-safe safety net)
                               ▼
        ┌──────────────────────────────────────────────┐
        │ 4. Universal Base Fail-Safe                  │ ──► Structured base diagnostic guidance
        └──────────────────────────────────────────────┘
```

### 5-Round Iterative Sandboxed Repair Loop
1. **Isolated Subprocess Sandbox:** All proposed code repairs are executed inside `sandbox_runner.py` with memory, execution time (5s limit), and syscall constraints.
2. **Progress-Based Acceptance Invariants:** A candidate repair is accepted only if:
   - Program reaches exit code 0, **OR**
   - The first failing line advances forward without deleting functions, reducing statements beyond limits, or modifying unaffected code.
3. **Whole-Program Multi-Error Detection:** Analyzes sequential chained errors without downstream secondary error poisoning.

---

## 🛡️ Four-Gate AAI Security Shield Subsystem

To protect educational environments and multi-user deployments, IntelliFix incorporates an armed defense-in-depth security subsystem (`security/`):

1. **Gate 1: Input Guard (`security/input_guard.py`)**  
   Scans incoming instructions and code for prompt injection, jailbreaks, hidden control characters, homoglyphs, and base64 payloads. Achieves 95.6% recall and 0% false positives on benign code.
2. **Gate 2: Code Guard (`security/code_guard.py`)**  
   Performs AST-level static security whitelisting; blocks arbitrary system execution (`os.system`, `subprocess`, raw network sockets, ctypes memory manipulation).
3. **Gate 3: Output Guard (`security/output_guard.py`)**  
   Prevents data exfiltration and masks sensitive environment tokens, cryptographic keys, and system paths.
4. **Gate 4: Tool Guard (`security/tool_guard.py`)**  
   Monitors execution boundaries and prevents unauthorized file access or subprocess spawning.
5. **Cryptographic Merkle Audit Ledger (`security/audit_log.py`)**  
   Every security event is recorded in a hash-chained, tamper-evident Merkle ledger (`results/security_log.jsonl`).
6. **Banking Four-Eyes Dual-Key Vault (`security/dual_key.py`)**  
   High-risk actions require mutual authorization with cryptographic HMAC-SHA256 signatures from both an Auditor and an Operator.

---

## 💻 Installation & Setup

### System Prerequisites
- **Python:** 3.10, 3.11, 3.12, or 3.13
- **Operating System:** Windows, macOS, or Linux

### 1. Installation

#### Option A: Lightweight Core Installation (Recommended & Fast, < 50 MB)
Installs Flask, AST tooling, and core dependencies without heavy neural libraries:
```bash
pip install -r requirements-base.txt
```

#### Option B: Full Installation (Includes Optional Online AI Support)
```bash
pip install -r requirements.txt
```

### 2. Environment Configuration
The system operates **100% offline out-of-the-box** using the deterministic rule engine and offline guide.  
To enable online LLM explanation (Tier 2), configure API keys:

**Windows PowerShell:**
```powershell
$env:GEMINI_API_KEY = "your-api-key"
# Optional Groq fallback:
$env:GROQ_API_KEY = "your-groq-key"
```

**Linux / macOS Bash:**
```bash
export GEMINI_API_KEY="your-api-key"
export GROQ_API_KEY="your-groq-key"
```

*(Alternatively, copy `.env.example` to `.env` and fill in your keys).*

---

## 🏃 Running the Application

### 1. Launching the Web Studio Workbench
**Option A (PowerShell Managed Launch - Recommended on Windows):**
```powershell
powershell -ExecutionPolicy Bypass -File .\start_app.ps1
```
**Option B (Direct Python Launch):**
```bash
python app.py
```
Open **`http://127.0.0.1:5000`** in any modern web browser.

**Web Studio Features:**
- **Code Editor:** Monaco-style interactive editor with syntax highlighting and file tree.
- **Diagnostic Inspector:** Instant multi-error detection, error classification, and side-by-side diff view.
- **Automata Visualizer:** Interactive NFA/DFA transition graphs, Hopcroft minimization, and input string tracer.
- **PDA Stack Animator:** Step-by-step push/pop tape animation for bracket nesting.
- **CFG Complexity Heatmap:** McCabe cyclomatic complexity graph and block inspection.
- **Compiler Passes Modal:** Real-time symbol tables, 3-Address Code, SSA $\phi$-nodes, and 5-pass optimization viewer.
- **Security Dashboard:** Live Merkle audit log inspector, risk scoring, and dual-key authorization console.

### 2. Running via Command-Line Interface (CLI)
Diagnose and repair Python scripts directly from your terminal using `intellifix.py`:

```bash
# Basic diagnosis and repair
python intellifix.py test_cases/T_errors1.py

# Display unified colorized diff
python intellifix.py test_cases/T_errors1.py --diff

# Output structured JSON for IDE integration
python intellifix.py test_cases/T_errors1.py --json

# Save repaired code to a new file
python intellifix.py test_cases/T_errors1.py --write

# Verify version and release hash
python intellifix.py --version
```

### 3. Running the Standalone Desktop GUI
**Option A (Pre-compiled Standalone Executable):**
Double-click or run from terminal:
```powershell
.\dist\TOC_Studio_Standalone.exe
```
*(Zero-install, self-contained single-file desktop application).*

**Option B (Direct Python Launch):**
```bash
python desktop_app.py
```

### 4. Running the Verification & Test Suites
```bash
# 1-Click Master Subsystem Verification
python verify_all_features.py

# Deep Compiler & Program Analysis Verification
python reverify_compiler_features.py

# Offline Core Unit Tests
python -m unittest tests_offline tests_rules tests_autofix tests_dfa tests_pda tests_shield_policy

# Full Integration Test Matrix
python -m unittest tests_server.py tests_contract.py tests_metrics.py tests_cli.py tests_week6_integration.py
```

---

## 📁 Clean Submission Project Structure

```
.
├── README.md                      # Comprehensive project documentation (this file)
├── IntelliFix_Report.pdf          # Final 35-page formal academic technical report
├── requirements.txt               # Full dependencies
├── requirements-base.txt          # Lightweight core dependencies (< 50MB)
├── requirements-ai.txt            # Optional AI client dependencies
├── .env.example                   # Template for optional API configuration
├── start_app.ps1                  # PowerShell automated launcher script
├── app.py                         # Flask Web Studio server & API routing
├── desktop_app.py                 # Standalone Desktop GUI launcher
├── intellifix.py                  # Command-Line Interface (CLI) tool
├── verify_all_features.py         # 1-Click Master Subsystem Verification
├── reverify_compiler_features.py  # Deep Compiler Analysis Verification
├── main.py                        # Quick execution runner
│
├── automaton_engine.py            # Formal Thompson NFA -> Subset DFA -> Hopcroft Minimizer
├── dfa.py                         # Formal 5-tuple Handcrafted Deterministic Finite Automata
├── pda_engine.py                  # Pushdown Automaton tape & stack animation engine
├── bracket_checker.py             # PDA bracket validator for Dyck languages
├── tokenizer.py                   # Regex-based deterministic lexical analyzer
├── cfg_engine.py                  # Control Flow Graph & McCabe Cyclomatic Complexity
├── code_quality.py                # AST code smells, quality metrics, O(N^3)->O(N^2) optimizer
├── dataflow_engine.py             # Kildall fixed-point dataflow & taint analysis
├── semantic_analyzer.py           # Symbol table & hierarchical scope analysis
├── ir_generator.py                # Intermediate Representation (TAC & SSA) generator
├── ir_optimizer.py                # 5-pass formal compiler IR optimizer
├── translation_validator.py       # Translation validation & equivalence prover
├── error_extractor.py             # Traceback and exception metadata parser
├── offline_guide.py               # Deterministic rule knowledge base (25+ exception types)
├── nlp_explainer.py               # Educational error explanation engine
├── multi_error.py                 # Whole-program multi-error detection & multi-round fixer
├── llm_explainer.py               # AI explanation coordinator
├── llm_calls.py                   # Resilient Gemini & Groq client with circuit breaker
├── llm_config.py                  # Provider priority & timeout configuration
├── sandbox_runner.py              # Isolated subprocess sandbox runner
├── sandbox_child.py               # Sandboxed worker process
│
├── agent.py                       # Autonomous repair agent
├── agent_memory.py                # Agent state & action history
├── agent_proposals.py             # LLM code repair patch generator
├── agent_tools.py                 # Agent tool execution interface
│
├── security_analyzer.py           # Static AST security scanner
├── run_benchmark.py               # 24-program offline utility benchmark runner
│
├── templates/                     # Clean Web IDE Studio templates
│   ├── index.html                 # Main IDE workbench (editor, visualizers, modals)
│   └── analytics.html             # Security & complexity analytics dashboard
│
├── security/                      # 4-Gate AAI Security Shield Subsystem
│   ├── shield.py                  # Master Shield coordinator
│   ├── input_guard.py             # Gate 1: Prompt injection & Trojan detector
│   ├── code_guard.py              # Gate 2: AST whitelisting & safety filter
│   ├── output_guard.py            # Gate 3: Exfiltration blocker & secret masker
│   ├── tool_guard.py              # Gate 4: Subprocess sandbox boundary enforcement
│   ├── risk_engine.py             # Multi-signal composite risk score calculator
│   ├── blast_radius.py            # Code mutation impact & blast radius estimator
│   ├── canary.py                  # Canary tokens & honeypot files
│   ├── dual_key.py                # Four-Eyes dual-key HMAC cryptographic vault
│   ├── audit_log.py               # Cryptographic Merkle tree audit ledger
│   ├── metrics.py                 # Statistical evaluation & confusion matrix metrics
│   ├── policy_engine.py           # Rule-based policy evaluation
│   ├── policy_loader.py           # Policy integrity loader with SHA256 verification
│   ├── threat_catalog.py          # Threat taxonomy catalog
│   ├── policy.json                # Armed security policy definition
│   ├── policy.sha256              # Policy SHA256 integrity checksum
│   └── shield_manifest.json       # Component cryptographic manifest
│
├── test_cases/                    # Demonstration and benchmark Python scripts
│   ├── T1.py                      # Multi-algorithm demonstration test case 1
│   ├── T2.py                      # Multi-algorithm demonstration test case 2
│   ├── T3.py                      # Multi-algorithm demonstration test case 3
│   ├── T-optimising.py            # O(N^3) -> O(N^2) loop optimization test case
│   ├── T_errors1.py               # Multi-exception error file (8 distinct errors)
│   ├── T_errors2.py               # Multi-exception error file (chained errors)
│   ├── T_holes.py                 # Unicode, edge-case syntax, and hole test file
│   ├── T_token_verification.py    # Lexical tokenizer verification test suite
│   ├── T_Brackets.py              # Pushdown automaton bracket matching test suite
│   ├── T_few_Injections.py        # Security prompt injection vectors
│   ├── test_case_large.py         # Large-scale multi-function stress program
│   └── test_case_large_fixed.py   # Ground-truth verified clean version
│
├── tests/                         # Comprehensive unit & integration test suites
│   ├── tests_offline.py           # Offline rule-based explanation tests
│   ├── tests_rules.py             # Deterministic rule engine tests
│   ├── tests_autofix.py           # 5-round auto-repair loop unit tests
│   ├── tests_automaton.py         # NFA/DFA conversion & Hopcroft minimization tests
│   ├── tests_dfa.py               # 5-tuple DFA equivalence vs regex tests
│   ├── tests_pda.py               # Pushdown Automaton Dyck language tests
│   ├── tests_bracket.py           # 350+ bracket mutant test cases
│   ├── tests_cfg.py               # Control Flow Graph & complexity tests
│   ├── tests_tokenizer.py         # Lexical analyzer tests against standard tokenize
│   ├── tests_compiler_upgrades.py # Compiler optimization & quality tests
│   ├── tests_optimizer_universal.py # Algorithmic loop optimizer tests
│   ├── tests_quality_metrics.py   # AST metrics & code smell tests
│   ├── tests_shield_policy.py     # Policy engine tests
│   ├── tests_input_guard.py       # Input guard prompt injection tests
│   ├── tests_canary_ledger.py     # Canary honeypots & Merkle ledger tests
│   ├── tests_dual_key.py          # Four-eyes dual-key vault tests
│   ├── tests_agent.py             # Repair agent core tests
│   ├── tests_cli.py               # IntelliFix CLI unit tests
│   ├── tests_contract.py          # API contract verification tests
│   ├── tests_ui.py                # UI route & rendering tests
│   └── tests_week6_integration.py # End-to-end integration test suite
│
├── benchmark_programs/            # 24 standard benchmark programs (prog_01 to prog_24)
├── dataset/                       # Curated error dataset (data.jsonl)
├── docs/                          # Detailed Theory & Architecture Documentation
│   ├── ARCHITECTURE.md            # System architecture specification
│   ├── DFA.md                     # Formal 5-tuple DFA definitions & proofs
│   ├── PDA.md                     # Pushdown Automaton Dyck-language specification
│   ├── TOKENIZER.md               # Lexical tokenizer grammar & regex definitions
│   ├── INPUT_GUARD.md             # Multi-signal prompt injection detector specification
│   ├── SANDBOX.md                 # Execution sandbox security & isolation model
│   ├── MULTI_ERROR.md             # Multi-error detection & cascade prevention theory
│   ├── THREAT_MODEL.md            # Threat taxonomy & mitigation matrix
│   ├── VIVA_NOTES.md              # Quick viva & oral examination cheat sheet
│   ├── FINAL_VIVA.md              # In-depth viva defense questions & answers
│   ├── PROJECT_MAP.md             # Complete module-by-module reference
│   ├── architecture.png           # Architecture overview diagram
│   └── architecture.svg           # High-resolution vector diagram
│
└── screenshots/                   # Visual proof of Web UI & automata animations
```

---

## 📊 Summary of Test Results & Quality Metrics

- **Unit & Integration Tests:** 582 automated tests passing (`100% pass rate`, 0 failures).
- **Automata Equivalence:** 100% agreement across 66,000+ strings between hand-written DFAs and Python regex engines.
- **Bracket PDA Accuracy:** 91.4% diagnostic agreement against Python `compile()` on 350+ deterministic mutants.
- **Security Shield Attack Containment:** 0.0% Attack Success Rate (ASR) with Shield Armed vs 100% ASR with Shield Disabled.
- **Auto-Repair Success Rate:** High precision across 25+ Python built-in exception types with surgical position invariance and AST safety invariants.

---

## 📜 Submission & Academic Integrity Notice

This project was developed for the **Theory of Computation** course curriculum at **National Institute of Technology, Warangal (NITW)**. All formal automata models, lexers, pushdown stack engines, control flow graphs, compiler passes, and security mechanisms are implemented from fundamental principles in pure Python.
