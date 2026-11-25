# THEORY OF AUTOMATA AND COMPILER DESIGN
## SECURE OTA UPDATE COMPILER
### END-SEMESTER EVALUATION REPORT
**Complete project documentation • compiler, cryptography, device simulation and agentic security**

| Field | Details |
| :--- | :--- |
| **Submitted by** | Bokkasam Nitya Yasaswi Reddy, Muhammed Al Jamal |
| **Roll Number** | 25CSB1A01, 25CSB1A68 |
| **Programme / Section** | BTECH CSE-AIDS |
| **Submitted to** | Suresh Babu |
| **Academic Year** | 2026–2027 |
| **Department** | Department of Computer Science & Engineering |

---

### Abstract
This report presents the complete Secure OTA Update Compiler project, a compiler-assisted framework for improving the security of over-the-air firmware updates. On the server/build side, the OTA update handler part of the firmware update is analysed by a custom LLVM `TraversalPass` invoked through the `secure-clang` wrapper or the python AST analyser through `secure-python`. The pass checks control-flow dominance of signature, source-trust, image-hash and anti-rollback guards, and scans for unsafe APIs, sensitive logging, weak cryptography and embedded secrets. The packaging tool implements an encrypt-then-sign design using AES-256-GCM, SHA-256, payload-key wrapping and ECDSA P-256 signatures. On the device side, the project models OTA bundle parsing, signature and hash verification, payload decryption, version checks and installation-state updates. A browser-based demonstration exposes compilation results and an advisory Agentic Security Worker-Judge architecture. The AI workflow is bounded and advisory: it uses prompt-injection preprocessing, nonce-tagged untrusted data, read-only analysis tools, structured-output validation and local-only model communication.

---

### 1. Introduction
Connected devices increasingly depend on remote firmware updates to deliver security fixes and new features. OTA updates reduce maintenance effort, but they also create a high-value attack path. A compromised update server, tampered package, replayed firmware image, weak verification sequence or unsafe update routine can undermine the security of operations of that device. A conventional compiler checks language correctness but does not necessarily enforce the security ordering required by an OTA installation procedure.

The Secure OTA Update Compiler combines compiler design, static analysis, cryptographic packaging and a simulated device update path. It verifies that required security checks are made before installation is performed.

---

### 2. Problem Statement and Motivation
The project addresses the risk that firmware update handler routines may compile even when security checks are missing, bypassable or incorrectly ordered. It also addresses the need to protect the firmware payload during transfer, authenticate the package origin, detect tampering and prevent downgrade or replay attacks. Finally, it explores how a local AI advisory component can help developers interpret policy findings without granting the model unrestricted authority over files, commands or network destinations.

---

### 3. Objectives
1. Enforce OTA security invariants through an LLVM-based compile-time pass.
2. Prevent installation unless signature, source, image-integrity and anti-rollback checks are satisfied.
3. Detect selected unsafe memory APIs, sensitive logging, weak cryptography and hardcoded secrets.
4. Provide a `secure-clang` wrapper and browser-based compiler demonstration.
5. Package firmware using AES-256-GCM encryption, SHA-256 integrity metadata and ECDSA P-256 signing.
6. Simulate device-side package parsing, signature verification, decryption, version validation and installation-state updates.
7. Integrate a bounded advisory Worker/Judge AI workflow with prompt-injection and tool-safety controls.
8. Extend the system to OTA update handler routines written in Python including all security checks and AI analysis.

---

### 4. Overall System Architecture
The complete system is divided into a server/build pipeline and an IoT-device simulation pipeline. The server side analyses and packages firmware. The device side validates the received bundle and permits installation only after verification succeeds. The compiler and device checks are complementary: compile-time checks constrain the update logic, while runtime package checks validate the actual update data.

```
+-----------------------------------------------------------------------------------------+
| Tier 1: Frontend & Sandbox UI (web-demo/)                                               |
| - Diagnostics Console        - Control Rail Sidebar        - Monaco Multi-Tab Editor    |
+-----------------------------------------------------------------------------------------+
                                           |
+-----------------------------------------------------------------------------------------+
| Tier 2: Backend Orchestration Gateway (app.py)                                          |
| - POST /api/advisory-copilot    - Policy Manager           - POST /api/compile          |
+-----------------------------------------------------------------------------------------+
           |                                                      |
+-----------------------------------+     +-----------------------------------------------+
| Tier 3: Advisory Copilot Engine   |     | Tier 4: Dual Security Compiler Toolchains     |
| - Security Preprocessor (Nonces)  |     | - C Pipeline: secure-clang (LLVM TraversalPass)|
| - Auxiliary Read-Only Tools       |     | - Python Pipeline: secure-python (AST CFG)    |
| - Agentic Judge Engine            |     +-----------------------------------------------+
+-----------------------------------+                             |
                                                                  v
                                          +-----------------------------------------------+
                                          | Tier 5: Cryptographic Packaging (packager.py) |
                                          | - AES-256-GCM payload cipher + ECDSA P-256    |
                                          | - Canonical 328-Byte Binary Header            |
                                          +-----------------------------------------------+
                                                                  |
                                                                  v
                                          +-----------------------------------------------+
                                          | Tier 6: Embedded Target Hardware Execution    |
                                          | - updateFirmware() Invariant Pipeline         |
                                          | - Dual-Bank NVRAM Flash + Anti-rollback guard |
                                          +-----------------------------------------------+
```

---

### 5. Compiler-Side Security Enforcement

#### 5.1 C Pipeline (secure-clang & LLVM TraversalPass)
* **LLVM TraversalPass (`llvm-pass/TraversalPass.cpp`)**: Analyses LLVM IR for `updateFirmware()`. Uses dominator-tree control flow analysis to verify that signature verification, source trust, image hash, and strict monotonic anti-rollback strictly dominate `install()`.
* **Security Invariants**:
  1. *Digital Signature Verification Dominance*: `install()` cannot execute unless signature verification succeeds.
  2. *Trusted Source Validation Dominance*: Update repository domain prefix must be verified.
  3. *Monotonic Anti-Rollback Guard*: `incoming_version > current_version` strictly enforced (rejects downgrade & same-version replay).
  4. *Cryptographic Image Hash Dominance*: Integrity hash must dominate installation.
  5. *Memory Safety*: Bans `strcpy`, `strcat`, `sprintf`, `gets`, and `system`.
  6. *Sensitive Logging Ban*: Bans `printf`, `puts`, `fprintf`, `perror` inside update handlers.
  7. *Weak Cryptography Ban*: Rejects `MD5`, `SHA1`, and weak PRNGs (`rand`, `srand`).
  8. *Hardcoded Secrets Detection*: Scans for private keys, tokens, and high-entropy literals.

#### 5.2 Python Pipeline (secure-python & AST Analyzer)
* **AST Security Analyzer (`tools/secure_python.py`)**: Analyses Python AST and builds basic-block CFGs. Enforces identical 8 security invariants, detects dynamic execution (`eval`, `exec`, `os.system`, `pickle`), and produces verified Python bytecode (`.pyc`).

---

### 6. Firmware Packaging and Cryptographic Protection
* **Encrypt-then-sign**: Payload encrypted with ephemeral AES-256-GCM key (96-bit IV). Ephemeral key is wrapped with 256-bit Master Key. SHA-256 hash computed over metadata, ciphertext, and GCM tag; signed with ECDSA P-256.
* **Canonical 328-Byte Binary Header**: Magic `0x3141544F`, packed SemVer, domain URL, IV, wrapped key, ciphertext length, hash, signature, and GCM tag.

---

### 7. Device-Side OTA Simulation
Models device update behavior: `load_ota_package()`, `verify_cryptographic_signature()`, `sourceTrusted()`, `verify_image_hash()`, and `decrypt_payload_aes_gcm()`. Coordinated via `updateFirmware()` with dual-bank staging and monotonic hardware version NVRAM updates.

---

### 8. Web Demonstration Interface
Flask application on port 5050 with dark/light theme, CodeCarbon sustainability tracking, C/Python multi-tab editor, live diagnostics console, and AI Advisory Copilot drawer.

---

### 9. Agentic AI Security Advisory & Defenses
* **Multi-Pass Worker-Judge Architecture**: Bounded 3-pass review separating recommendation drafting from validation.
* **Prompt Injection Defenses**: Preprocessor neutralizes embedded jailbreaks, escapes control tokens, and wraps untrusted inputs in cryptographic nonces.
* **Zero Cloud Telemetry**: Restricted strictly to loopback addresses (`127.0.0.1`), preserving firmware source privacy.

---

### 10. Quantitative Results & Evaluation Benchmarks

#### 10.1 Multi-Class Confusion Matrix (100 Test Samples per Class)
Evaluation of AST/CFG flaw classification across 5 defect classes:
* **Syntax Errors**: 96% Precision
* **Declaration Errors**: 92% Precision
* **Type Mismatches**: 95% Precision
* **Memory Bounds Defects**: 93% Precision
* **Scope / Control Flow Violations**: 96% Precision

#### 10.2 BLEU & ROUGE Code Quality Scores
| Error Category | BLEU Score | ROUGE-L Score |
| :--- | :---: | :---: |
| Indentation Error (Python) | 1.00 | 1.00 |
| NameError / Typo Correction | 1.00 | 1.00 |
| Undefined Variable (C) | 0.91 | 0.85 |
| Undefined Variable (Python) | 1.00 | 1.00 |
| Type Mismatch | 0.94 | 0.89 |
| Missing Semicolon | 0.93 | 0.63 |
| Attribute Error | 1.00 | 1.00 |
| Syntax Errors | 0.84 | 0.74 |
| Other Defects | 0.84 | 0.76 |

#### 10.3 Pipeline Latency Benchmarks (in milliseconds)
| Component | Min Time (ms) | Avg Time (ms) | Max Time (ms) |
| :--- | :---: | :---: | :---: |
| Prompt Injection Preprocessor | 0.14 | 1.33 | 36.53 |
| Syntax & Delimiter Validator | 0.14 | 1.68 | 66.73 |
| CFG Dominance & Invariant Verifier | 0.16 | 1.51 | 43.37 |
| Secret & Entropy Scanner | 0.03 | 0.41 | 6.66 |
| Code Compilation & Artifact Generation | 0.01 | 9.19 | 59.97 |

---

### 11. Conclusion
The Secure OTA Update Compiler successfully demonstrates a layered approach to firmware update security:
* Deterministic compile-time compiler pass enforcement (C and Python).
* Encrypted and signed packaging (AES-256-GCM + ECDSA P-256).
* Monotonic version protection against downgrade and replay attacks.
* Safe, bounded AI advisory assistance with zero cloud telemetry.
