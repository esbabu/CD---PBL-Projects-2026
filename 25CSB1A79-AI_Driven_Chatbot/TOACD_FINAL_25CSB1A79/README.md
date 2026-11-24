# Samphel Secure Coding Assistant

**Project Title:** Samphel Secure Coding Assistant — An Intelligent Agentic AI-Driven Self-Healing C++ Compiler, Debugger, and Security Analysis Platform

**Student Name:** Ugyen Jigme Samphel
**Roll Number:** 25CSB1A79
**Course:** Theory of Automata and Compiler Design (TOACD)
**Academic Year:** 2025–2026

---

## 1. Project Overview

The Samphel Secure Coding Assistant is a full-stack, browser-based educational and security analysis platform built with Python and Streamlit. It integrates a GCC-based C++ compiler, an LLDB-inspired agentic debug loop, a local AI engine (Ollama Llama 3), a six-stage automated self-healing code repair pipeline, and a persistent security incident database (Attack Vault).

The platform is designed for students and developers who write C++ programs and need an intelligent, explainable, and security-aware assistant to identify compile-time errors, classify them, generate AI-assisted fixes, verify those fixes through multi-stage gates, and log all security incidents for analyst review.

The project is entirely local — no cloud APIs are required. The AI inference runs on a locally hosted Ollama model. If Ollama is unavailable, the system gracefully falls back to deterministic repair rules.

---

## 2. Objectives

- Provide an interactive browser-based C++ compilation and debugging interface.
- Automatically classify GCC compiler errors into semantic categories.
- Generate AI-assisted, human-readable explanations and fix suggestions using a local Llama 3 model.
- Implement an agentic LLDB-style debug loop that iteratively analyses and repairs code errors.
- Provide a six-stage verification pipeline that validates every AI-generated repair before it is applied.
- Detect and block prompt injection attacks, policy bypasses, and banned API usage.
- Log all security incidents into a persistent, queryable SQLite Attack Vault.
- Support analyst triage, review, and export of security incidents.
- Measure and report environmental impact (energy and carbon emissions) using CodeCarbon.
- Display real-time error analytics and system health status.

---

## 3. Main Features

| Feature | Description |
|---|---|
| C++ Compiler Interface | Compile and run user-submitted C++ code using GCC with structured error output |
| Error Classification | Classify GCC errors (Type Mismatch, Syntax Error, Linker Error, etc.) using `error_classifier.py` |
| AI Explanation | Generate pedagogical explanations and fix suggestions using local Ollama Llama 3 |
| Agentic Debug Loop | LLDB-style iterative repair loop (`lldb_engine.py`) that attempts up to N fix iterations |
| Self-Healing Engine | Six-stage verification pipeline: Pre-Scan → Security Gate → GCC Compilation → Sandbox Execution → Regression Test → Latency Benchmark |
| Security Guardrails | Ban list of 15+ dangerous C++ APIs (`gets`, `strcpy`, `system`, `popen`, `exec*`, etc.) |
| Prompt Injection Detection | Regex-based detection of LLM prompt injections and policy bypass attempts |
| Risk Scoring | Multi-vector risk scoring (0.0–1.0) across input payload, AI prompt, and fix output |
| Attack Vault | Persistent SQLite database recording all detected security incidents with SHA-256 deduplication |
| Analyst Triage | Classify incidents as Confirmed Attack / False Positive / Needs Review |
| Import / Export | Import baseline attack datasets (JSON); export confirmed incidents as CSV or JSON |
| Security Audit Dashboard | Real-time threat metrics, event timelines, and posture summaries |
| Error Analytics | Pandas-driven compiler error frequency and trend charts |
| Green Computing | CodeCarbon-based energy and carbon footprint measurement per session |
| System Status | Live diagnostics for Ollama availability, GCC path, SQLite, and sandboxing environment |

---

## 4. System Architecture and Workflow

```
User Browser (Streamlit UI)
        │
        ▼
  Navigation Router (app.py)
        │
   ┌────┴─────────────────────────────────┐
   │                                      │
   ▼                                      ▼
Compiler & Debugger               Self-Healing Lab
   │                                      │
   ├── Input Sanitizer                    ├── Pre-Scan Gate (secure_scan.py)
   ├── Security Check (agent_security.py) ├── Security Gate
   ├── GCC Compiler (compiler_service.py) ├── GCC Compilation Gate
   ├── Error Classifier (error_classifier)├── Sandbox Execution Gate
   ├── LLDB Debug Loop (lldb_engine.py)   ├── Regression Test Gate
   └── AI Explanation (Ollama Llama 3)    └── Latency Benchmark Gate
        │                                         │
        ▼                                         ▼
  Audit Logger (audit_logger.py)   ◄──── Fix Validation (fix_engine.py)
        │
        ▼
  Attack Vault (SQLite, attack_vault.py)
        │
        ▼
  Security Audit Dashboard (security_audit_ui.py)
        │
   ┌────┴───────────────────┐
   ▼                        ▼
Error Analytics        Green Metrics
(dashboard.py)         (CodeCarbon)
```

---

## 5. Technologies Used

| Category | Technology | Version / Notes |
|---|---|---|
| Language | Python | 3.10+ required |
| Web Framework | Streamlit | 1.28+ |
| AI / LLM | Ollama (Llama 3) | Local inference, http://localhost:11434 |
| Compiler | GCC / G++ | Available in system PATH |
| Data Processing | Pandas | 2.0+ |
| Database | SQLite3 | Built into Python standard library |
| Security Scanning | Regex (re module) | Built into Python standard library |
| Carbon Tracking | CodeCarbon | 2.3+ |
| HTTP Client | Requests | 2.31+ |
| Testing | Python unittest | Built into Python standard library |
| Serialization | JSON, CSV | Built into Python standard library |

---

## 6. Software Requirements

### Minimum Requirements

- **Operating System:** Windows 10/11, Ubuntu 20.04+, or macOS 12+
- **Python:** 3.10 or higher
- **GCC / G++:** Installed and available in the system PATH
  - Windows: Install [MinGW-w64](https://www.mingw-w64.org/) or [MSYS2](https://www.msys2.org/) and add `bin/` to PATH
  - Linux: `sudo apt install build-essential`
  - macOS: `xcode-select --install`
- **RAM:** Minimum 4 GB (8 GB recommended when running Ollama)
- **Disk:** Minimum 2 GB free (more if storing Ollama models)

### Optional (Recommended for AI features)

- **Ollama:** Installed with model `llama3` pulled
  - Download from: https://ollama.com
  - GPU support: NVIDIA GPU recommended for faster inference

---

## 7. Installation Instructions

### Step 1: Clone or Extract the Project

Extract `25CSB1A79_Samphel_Source_Code.zip` into a directory of your choice.

```bash
cd 25CSB1A79_Samphel_Source_Code
```

### Step 2: Create a Virtual Environment (Recommended)

```bash
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on Linux / macOS
source venv/bin/activate
```

### Step 3: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Verify GCC is Available

```bash
g++ --version
```

If the command is not found, install GCC for your operating system (see Section 6).

---

## 8. Ollama Setup and Model Configuration

Ollama provides the local AI inference engine. If it is not installed, the application will function in a reduced mode — compiler output will still work but AI explanations and self-healing will use deterministic rule-based fallbacks.

### Install Ollama

Download and install from: https://ollama.com

### Pull the Required Model

```bash
ollama pull llama3
```

### Start Ollama (if not set to start automatically)

```bash
ollama serve
```

Ollama listens on `http://localhost:11434` by default. This is the address used by the application.

### Configure a Different Ollama Host or Model (Optional)

Set environment variables before running the application:

```bash
# Windows
set OLLAMA_HOST=http://localhost:11434
set OLLAMA_MODEL=llama3

# Linux / macOS
export OLLAMA_HOST=http://localhost:11434
export OLLAMA_MODEL=llama3
```

---

## 9. Instructions to Run the Application

### Initialize the Attack Vault Database

The database is initialized automatically on first run. You may also initialize it manually:

```python
python -c "from attack_vault import init_vault, import_attack_dataset; init_vault(); import_attack_dataset('attack_dataset.json')"
```

### Start the Streamlit Application

```bash
python -m streamlit run app.py
```

The application will open automatically in your default browser at:

```
http://localhost:8501
```

### Stopping the Application

Press `Ctrl+C` in the terminal to stop the server.

---

## 10. Explanation of All Six Modules

### Module 1 — Compiler & Debugger (app.py, compiler_service.py, error_classifier.py, lldb_engine.py)

The main interface for C++ code submission. Users type or paste C++ source code into the editor, then click Compile & Debug.

The module:
1. Sanitizes the input using `secure_scan.py` and `agent_security.py` to block banned APIs and prompt injection attempts.
2. Passes clean code to `compiler_service.py`, which invokes GCC as a subprocess with timeout enforcement.
3. Parses GCC's structured error output using `error_classifier.py` to categorize errors (Type Mismatch, Syntax Error, Linker Error, etc.).
4. Constructs a pedagogical prompt and sends it to the local Ollama Llama 3 model.
5. Runs the LLDB-inspired agentic debug loop (`lldb_engine.py`) which iterates over error analysis and fix attempts.
6. Displays compiler output, error classification, AI explanation, and fix suggestions in the UI.
7. Logs all interactions to the audit logger.

---

### Module 2 — Self-Healing Lab (self_healing_engine.py, self_healing_ui.py, fix_engine.py, semantic_analyzer.py)

An automated program repair (APR) pipeline that attempts to autonomously detect, repair, and verify C++ code errors.

**Six-Stage Verification Gate:**

| Stage | Name | Description |
|---|---|---|
| 1 | Pre-Scan | Scans original code for banned functions and prompt injections |
| 2 | Security Gate | Scans proposed AI fix for banned API calls and jailbreak constructs |
| 3 | GCC Compilation Gate | Compiles the fix in a temporary sandbox using GCC with debug flags |
| 4 | Sandbox Execution Gate | Executes the compiled binary under a 5-second timeout with resource limits |
| 5 | Regression & Test Gate | Validates output against user-specified expected substrings |
| 6 | Latency Benchmark | Records execution latency before and after repair |

A repair is only applied if it passes all six gates. The original source is preserved and a unified diff is displayed.

---

### Module 3 — Attack Vault (attack_vault.py, attack_vault_ui.py, attack_dataset.json)

A persistent SQLite-based security incident management system.

**Stored threat types:**
- Prompt injection and system prompt extraction attempts
- Policy bypass attempts (`system("rm -rf /")`, `popen`, `exec`)
- Banned C++ memory and buffer overflow vulnerabilities
- Malicious or poisoned AI-generated fixes
- Failed security verifications

**Features:**
- SHA-256 deduplication prevents duplicate entries
- Session correlation via unique `correlation_id` per session
- Analyst triage: classify incidents as Confirmed Attack / False Positive / Needs Review
- Import baseline datasets; export confirmed incidents as CSV or JSON

---

### Module 4 — Error Analytics Dashboard (dashboard.py)

A Pandas-powered analytics dashboard that reads `compiler_errors.csv` and displays:
- Error type frequency distribution
- Error trend over time
- Most common error categories

---

### Module 5 — Security Audit & Metrics (security_audit_ui.py, security_metrics.py, agent_security.py)

Real-time security posture monitoring:
- Reads from `security_audit_logs.json`
- Displays threat event counts, risk score distributions, and category breakdowns
- Shows live threat posture score and detection metrics
- `agent_security.py` performs multi-vector risk scoring (prompt injection risk, policy bypass risk, payload risk)

---

### Module 6 — System & Ollama Status (system_status_ui.py)

A diagnostic panel that checks and reports:
- Ollama server availability and model availability
- GCC compiler path and version
- SQLite availability and Attack Vault database status
- Sandboxing environment (temp directory access, subprocess permissions)
- Python version and codecarbon version

---

## 11. Security Features

| Feature | File | Description |
|---|---|---|
| Banned API Guardrail | `secure_scan.py` | Blocks 15+ dangerous C++ functions: `gets`, `strcpy`, `strcat`, `sprintf`, `system`, `popen`, `exec*`, `mktemp`, `auto_ptr` |
| Prompt Injection Detection | `agent_security.py` | Regex-based detection of LLM prompt injection and jailbreak patterns |
| Policy Bypass Detection | `agent_security.py` | Detects shell command injection via `system()`, `popen()`, `exec()` |
| Risk Scoring | `agent_security.py` | Multi-vector risk score (0.0–1.0): input payload, AI prompt, fix output |
| AI Fix Validation | `fix_engine.py` | JSON parsing and safety validation of every AI-generated fix |
| Six-Stage Gate | `self_healing_engine.py` | Full verification pipeline before any repair is applied |
| SQL Injection Prevention | `attack_vault.py` | Parameterized SQLite queries throughout |
| Deduplication | `attack_vault.py` | SHA-256 hash deduplication prevents duplicate attack records |
| Audit Logging | `audit_logger.py` | All security events are logged to `security_audit_logs.json` and mirrored to Attack Vault |
| Compiler Sandboxing | `compiler_service.py` | Subprocess execution with 10-second compile timeout and 5-second run timeout |

---

## 12. Testing Instructions

### Run All 25 Automated Tests

```bash
python test_system.py
```

Expected output:
```
.........................
----------------------------------------------------------------------
Ran 25 tests in ~34s

OK
```

### Run Individual Test Suites

```bash
# Self-Healing Engine tests (8 tests)
python -m unittest test_self_healing

# Attack Vault tests (9 tests)
python -m unittest test_attack_vault
```

### Test Coverage Summary

**Self-Healing Tests (8):**
1. Valid C++ code remains unchanged when no repair is needed
2. Missing semicolon errors are identified and repaired
3. Proposed repairs must compile before being verified
4. Non-compiling repairs are rejected
5. Repairs introducing dangerous system calls are rejected
6. Repairs breaking regression tests are rejected
7. Original code is preserved after a failed repair
8. Ollama unavailability produces clear error without crashing

**Attack Vault Tests (9):**
1. Attack events are stored with correct fields and schema
2. Records persist after reopening the database
3. Filtering by severity and category works correctly
4. SQL injection in stored payloads is handled safely
5. Stored attack inputs are never executed
6. Duplicate dataset imports are handled via SHA-256 deduplication
7. Review decisions and analyst notes persist
8. CSV and JSON exports contain expected fields
9. Database errors are handled gracefully

---

## 13. Project Folder Structure

```
25CSB1A79_Samphel_Source_Code/
│
├── app.py                      # Main Streamlit application and navigation router
├── self_healing_ui.py          # UI for the Self-Healing Lab (Module 2)
├── self_healing_engine.py      # Core APR orchestration, 6-stage gate verification
├── attack_vault.py             # SQLite database manager for the Attack Vault
├── attack_vault_ui.py          # UI for Attack Vault triage and inspection (Module 3)
├── attack_dataset.json         # Baseline dataset of known attack signatures
├── security_metrics.py         # Real-time threat posture and metrics calculation
├── semantic_analyzer.py        # Static semantic analyser (div-by-zero, loops, null ptrs)
├── compiler_service.py         # Subprocess GCC wrapper with timeout enforcement
├── agent_security.py           # Prompt injection and policy bypass detection
├── secure_scan.py              # C++ banned API guardrail
├── fix_engine.py               # AI repair JSON parser and safety validator
├── error_classifier.py         # GCC error parser and pedagogical prompt builder
├── audit_logger.py             # Dual logger: JSON audit log + Attack Vault mirror
├── dashboard.py                # Error analytics dashboard (Module 4)
├── security_audit_ui.py        # Security audit log view and threat metrics (Module 5)
├── system_status_ui.py         # System and Ollama diagnostic panel (Module 6)
├── lldb_engine.py              # Agentic LLDB-style iterative debug loop
├── error_logger.py             # CSV-based compiler error logger
├── github_scraper.py           # GitHub Search API utility for keyword frequency
│
├── test_system.py              # Master test suite (runs 25 automated unit tests)
├── test_self_healing.py        # Self-Healing Engine tests (8 tests)
├── test_attack_vault.py        # Attack Vault tests (9 tests)
│
├── final_tests.cpp             # Sample C++ test file for demonstration
├── test1.cpp                   # Sample C++ file with intentional errors
│
├── compiler_errors.csv         # Recorded compiler error log (from live usage)
├── emissions.csv               # Carbon and energy telemetry (CodeCarbon output)
├── security_audit_logs.json    # Recorded security audit events (from live usage)
├── github_link.txt             # GitHub repository reference
│
├── requirements.txt            # Python dependency list
├── README.md                   # This file
├── .gitignore                  # Git ignore rules
│
└── data/
    └── attack_vault.db         # SQLite Attack Vault database (auto-created on first run)
```

---

## Known Limitations

1. **Compilation Sandboxing:** GCC is invoked as a host subprocess with timeout limits. For untrusted multi-tenant environments, additional OS-level isolation (Docker, Linux seccomp, WebAssembly/WASI) is recommended.
2. **Obfuscation Bypass:** Static banned-API checks block known patterns. Dynamically loaded dangerous functions (e.g. via `dlopen`) are not currently detected.
3. **AI Fix Quality:** Fix quality and speed depend on the Ollama model and host hardware. On systems without a GPU, inference may be slow. Rule-based fallbacks are always available.
4. **Attack Vault Encryption:** The SQLite database is not encrypted at rest. In a production environment, database-level encryption should be added.

---

## GitHub Repository

https://github.com/samphel-workhard/ToACD25CSB1A79

---

*Submission prepared for Theory of Automata and Compiler Design — Academic Year 2025–2026.*
