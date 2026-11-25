# THEORY OF AUTOMATA AND COMPILER DESIGN
## Project Title: Secure OTA Update Compiler
### Submission Folder: `25CSB1A01_25CSB1A68_SECURE_OTA_UPDATE_COMPILER`

---

## 👥 Student & Course Details
* **Student Name(s)**: Bokkasam Nitya Yasaswi Reddy, Muhammed Al Jamal
* **Roll Number(s)**: `25CSB1A01`, `25CSB1A68`
* **Programme / Section**: B.Tech CSE (Artificial Intelligence & Data Science)
* **Course**: Theory of Automata and Compiler Design (CS-PBL)
* **Faculty Guide**: Suresh Babu
* **Academic Year**: 2026–2027
* **Institution**: National Institute of Technology, Warangal (NITW)

---

## 📌 Project Overview & Abstract
The **Secure OTA Update Compiler** is a compiler-assisted security verification framework that enforces over-the-air (OTA) firmware security invariants before code generation. Modern IoT devices are highly vulnerable to malicious firmware injection, version rollback (downgrade) replay attacks, tampered ciphertexts, and insecure flashing routines.

This project introduces a **dual-language static analysis compiler pipeline** (C via LLVM `secure-clang` and Python via AST `secure-python`) coupled with an **Encrypt-then-Sign cryptographic packaging pipeline** (AES-256-GCM + ECDSA P-256) and an **Agentic AI Security Advisory Judge (Worker-Judge architecture)** with zero cloud telemetry.

### Core Security Invariants Enforced:
1. **Digital Signature Verification Dominance**: `verifySignature()` must strictly dominate the `install()` path.
2. **Trusted Source Validation Dominance**: `sourceTrusted()` must strictly dominate `install()`.
3. **Monotonic Anti-Rollback Guard**: `incoming_version > current_version` strictly enforced; downgrade and same-version replay attacks are blocked.
4. **Cryptographic Image Hash Dominance**: SHA-256 integrity hash verification must dominate `install()`.
5. **Memory Safety**: Strict ban on unbounded memory functions (`strcpy`, `strcat`, `sprintf`, `gets`, `system`).
6. **Sensitive Logging Ban**: Ban on side-channel logging APIs (`printf`, `puts`, `fprintf`, `perror`) inside flashing handlers.
7. **Weak Cryptography Ban**: Rejection of insecure primitives (`MD5`, `SHA1`, and `rand()` PRNG).
8. **Hardcoded Secrets Detection**: Automated entropy scanning to intercept private keys and API tokens.

---

## 📁 Repository File Manifest & Component Descriptions

Below is the complete list of files and components submitted within this directory:

### 1. 📖 Documentation & Evaluation Reports (`/Documentation`)
* `Documentation/End_Semester_Evaluation_Report.md`: Full comprehensive end-semester report covering system architecture, compiler theory, cryptographic specifications, evaluation benchmarks, and result discussions.
* `Documentation/Mid_Semester_Evaluation_Report.md`: Mid-semester evaluation report documenting compiler-side static enforcement and initial pass design.
* `Documentation/Secure_OTA_Compiler_Demo.mp4`: Local copy of the complete recorded video walkthrough demonstrating live compilation, security policy blocking, diagnostics, and AI advisory remediation.
* **Google Drive Video Link**: [NITW Drive Access Link](https://drive.google.com/file/d/your-drive-link-here/view?usp=sharing) *(Accessible via `@nitw.ac.in` domain).*

### 2. ⚙️ Compiler Passes & Toolchain Drivers
* `llvm-pass/TraversalPass.cpp`: Custom LLVM C++ pass analyzing LLVM IR basic-block dominator trees for CFG dominance, banned functions, and monotonic version checks.
* `llvm-pass/build/libTraversalPass.so`: Compiled shared object LLVM pass plugin for Clang integration.
* `secure-clang`: Executable compiler wrapper that intercepts C compilation, emits LLVM IR, runs `TraversalPass`, enforces policy JSON rules, and tracks energy consumption via CodeCarbon.
* `secure-python`: Executable compiler wrapper for Python firmware routines.
* `tools/secure_python.py`: Python AST & CFG dominance analyzer, enforcing identical 8 security invariants before emitting compiled bytecode (`.pyc`).
* `tools/package_firmware.py`: Encrypt-then-sign cryptographic packaging tool generating canonical 328-byte binary OTA bundles.

### 3. 💻 Firmware Runtime Implementation (`/src` & `/src_py`)
* `src/update_handler.c` & `include/update_handler.h`: C runtime implementation for parsing canonical 328-byte headers, verifying signatures, validating hashes, and safe flashing.
* `src/crypto.c` & `include/crypto.h`: Cryptographic primitives for AES-256-GCM authenticated decryption, SHA-256 digests, and ECDSA P-256 verification.
* `src/version.c` & `include/version.h`: Monotonic SemVer parsing, comparison, and persistent NVRAM version storage simulation.
* `src_py/update_handler.py`: Complete Python equivalent runtime for parsing, verifying, and applying encrypted OTA packages.

### 4. 🌐 Web Demonstration Interface & Agentic AI Copilot (`/web-demo`)
* `web-demo/app.py`: Flask application providing an interactive compiler sandbox, multi-tab code editor, live telemetry, and REST endpoints.
* `web-demo/advisory_copilot.py`: Bounded advisory engine utilizing a Multi-Pass Worker-Judge architecture to explain compiler violations and generate compliant in-place remediations.
* `web-demo/read_only_tools.py`: Deterministic read-only security tools auditing AST CFG dominance, banned APIs, external libraries, and entropy.
* `web-demo/security_preprocessor.py`: Prompt-injection firewall intercepting jailbreaks and framing untrusted input with cryptographic boundary nonces.
* `web-demo/templates/index.html` & `web-demo/static/`: Interactive UI with dark/light mode toggle, live diagnostics console, CodeCarbon emissions tracker, and Monaco-style editor.
* `launch_web_demo.bat`: One-click startup script initializing the web demo on `http://localhost:5050`.

### 5. 🧪 Test Suites & Security Fixtures (`/tests`)
* `tests/*.c` (38 C testcases): Exhaustive positive/negative unit tests for all invariants (missing signature, rollback violation, weak crypto, logging leaks, hardcoded secrets, prompt injections).
* `tests/python/*.py` (9 Python testcases): Complete Python security test suite verified with `secure-python`.
* `tests/test_pipeline_e2e.py`: Automated end-to-end integration test runner validating packaging, encryption, tampering rejection, and compilation for C.
* `tests/test_python_pipeline_e2e.py`: Automated end-to-end integration test runner for the Python pipeline.
* `web-demo/test_all_syntax_and_typos.py`: Regression verification suite testing 41 distinct syntax and typo remediation patterns.
* `web-demo/test_endpoints.py`: Automated API verification harness testing all web-demo REST endpoints.

### 6. 🔒 Security Policies (`/policies`)
* `policies/original_protocol.json`: Strict policy enforcing all 8 security invariants.
* `policies/rules_python.json`: Specialized policy configuration for Python AST verification.
* `policies/signature_and_source_only.json`: Constrained device policy omitting rollback and logging checks.

### 7. 🔑 Cryptographic Keys (`/keys`)
* `keys/private_key.pem` & `keys/public_key.pem`: Sample ECDSA P-256 keypair for signing and verification.
* `keys/master_key.bin`: Provisioned 256-bit AES master key used for payload key unwrapping.

---

## 📊 Summary of Evaluation Results

### 1. Classification Performance (Confusion Matrix)
* **Syntax Errors**: 96% Precision
* **Declaration Errors**: 92% Precision
* **Type Mismatches**: 95% Precision
* **Memory Bounds Defects**: 93% Precision
* **Scope / Control Flow Violations**: 96% Precision

### 2. Code Quality Scores (BLEU & ROUGE)
* **Indentation / NameError**: BLEU 1.00 / ROUGE-L 1.00
* **Undefined Variables**: BLEU 0.91 / ROUGE-L 0.85
* **Type Mismatches**: BLEU 0.94 / ROUGE-L 0.89
* **Syntax & Semicolons**: BLEU 0.84 / ROUGE-L 0.74

### 3. Pipeline Latency Benchmarks
* Prompt Preprocessor: **0.14 ms** (avg 1.33 ms)
* CFG Dominance Verifier: **0.16 ms** (avg 1.51 ms)
* Secret Scanner: **0.03 ms** (avg 0.41 ms)
* Total End-to-End Build & Gate Enforcement: **~10 ms**

---

## 🚀 How to Run the Demonstration

1. Double-click `launch_web_demo.bat` (or run `python3 web-demo/app.py` inside WSL/Linux).
2. Open your browser and navigate to **`http://localhost:5050`**.
3. Select any sample from the **Demo Mode** panel (e.g., *Weak Crypto*, *Hardcoded Secret*, *Rollback Violation*).
4. Click **Run secure-clang** to inspect compile-time policy diagnostics.
5. Click **Replace in Editor** to apply the verified in-place remediation, and re-run compilation to verify a clean **PASSED** build.
