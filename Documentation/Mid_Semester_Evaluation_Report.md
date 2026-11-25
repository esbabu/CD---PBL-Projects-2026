# THEORY OF AUTOMATA AND COMPILER DESIGN
## SECURE OTA UPDATE COMPILER
### MID-SEMESTER EVALUATION REPORT
**Initial implementation scope • compiler-side security enforcement**

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
This report documents the initial implementation of the Secure OTA Update Compiler project. The work focuses on the compiler-side foundation: a custom LLVM pass that checks firmware-update routines for security invariants, together with a `secure-clang` wrapper that places those checks before normal Clang compilation. The central idea is to move selected firmware security requirements from informal coding guidelines into deterministic compile-time checks written into read-only memory of the IoT device at the time of manufacturing. The pass examines the control-flow structure around the installation operation and scans for unsafe functions, sensitive logging, weak cryptographic APIs and embedded secrets. The current milestone also includes the ability to change the security protocol according to manufacturer’s needs, an Encrypt-then-Sign architecture where the device expects the update to be encrypted and signed by the server, which is used to ensure the validity and integrity of the update, and a browser-based demonstration interface for submitting source code and viewing policy findings.

---

### 1. Introduction
Over-the-air (OTA) firmware updates allow connected devices to receive software updates without physical access. This convenience creates a security-sensitive path: an attacker may attempt to install an unauthenticated image, redirect a device to an untrusted source, replay an older release, or exploit unsafe code in the update routine. Traditional compilation checks syntax and type correctness, but it does not automatically prove that all required update-security checks occur before the firmware installation call.

The project addresses this gap by extending the LLVM/Clang compilation pipeline. The C source is compiled to LLVM Intermediate Representation (IR), a custom pass traverses the IR and checks the update function, and the wrapper permits normal compilation only when the policy checks succeed.

---

### 2. Problem Statement
OTA firmware updates are sent out as monolithic packages with the actual firmware update and the new update handler packed together. A firmware handler routine can compile successfully while still containing security weaknesses. In particular, an installation call may be reachable without successful signature verification, trusted-source validation, an anti-rollback condition or image-integrity validation. Unsafe memory APIs, sensitive logging, weak cryptographic functions and hardcoded secrets can also increase the risk of attacks. The project therefore requires a compiler-integrated mechanism that detects these conditions and blocks compilation when configured invariants are violated.

---

### 3. Objectives
1. Design an LLVM pass that performs static security checks on OTA firmware update handler routines.
2. Verify that signature and trusted-source checks dominate the install path.
3. Check the monotonic version condition so older or equal firmware versions cannot be installed.
4. Require image-hash verification to dominate installation.
5. Detect selected memory-unsafe functions, sensitive logging APIs, weak cryptography and hardcoded secrets.
6. Integrate the pass into a compiler wrapper so a failed policy check prevents normal compilation.
7. Prepare secure and insecure test programs and a demonstration interface.

---

### 4. Scope of the Mid-Semester Milestone
This milestone covers the compiler-side enforcement layer and its demonstration path:
* LLVM `TraversalPass` and IR-based policy checks.
* `secure-clang` wrapper and compile gates.
* Static checks for control-flow dominance and unsafe APIs.
* Secure/insecure C fixtures and policy configuration.
* Web demo for source input and displaying compile-time findings.

---

### 5. Background Concepts
* **5.1 Compiler pipeline and LLVM IR**: A compiler transforms source code through intermediate representations before producing machine code. LLVM IR is a compiler-independent representation that exposes instructions, basic blocks, branches and function calls. Analysing IR allows a pass to reason about program structure rather than relying only on text matching.
* **5.2 Control-flow graph and dominance**: A control-flow graph (CFG) represents basic blocks as nodes and possible control transfers as directed edges. A node A dominates node B when every path from the function entry to B passes through A. The project uses this property to enforce that security checks occur before `install()`.
* **5.3 Static analysis and policy enforcement**: Static analysis inspects code without executing the firmware. The project combines structural checks on control flow with scans for prohibited functions and sensitive string constants.
* **5.4 Policy modularity**: A manufacturer can change the policy configuration to fit their needs; this allows the pass to enable or disable selected categories of checks.

---

### 6. Proposed Architecture
The mid-semester architecture consists of four main stages:
1. **Source firmware input**: C source file containing the `updateFirmware()` routine.
2. **`secure-clang` wrapper**: Creates LLVM IR and invokes the `TraversalPass`.
3. **LLVM `TraversalPass`**: CFG dominance, monotonic version guard, image hash, banned APIs, and secret scanning.
4. **Compile decision**: Pass invokes Clang; Fail stops compilation and outputs policy diagnostics.

---

### 7. Methodology and Implementation

#### 7.1 LLVM TraversalPass
`TraversalPass.cpp` implements the custom LLVM pass:

| Security Check | Purpose / Expected Behaviour |
| :--- | :--- |
| **Signature verification dominance** | `install()` must not be reachable unless signature verification succeeds. |
| **Trusted-source dominance** | The update source must be validated before installation. |
| **Anti-rollback guard** | The incoming version must be strictly greater than the current version; equal or lower versions are rejected. |
| **Image-hash dominance** | Image integrity verification must dominate `install()` on the successful branch. |
| **Banned function scan** | Reject selected unsafe functions such as `strcpy`, `strcat`, `sprintf`, `gets` and `system`. |
| **Logging / weak crypto scan** | Reject sensitive logging calls (`printf`, `puts`, `perror`) and weak APIs such as `MD5`, `SHA-1` and `rand`. |
| **Secret detection** | Scan string constants for private-key markers, credential tokens and high-entropy data. |

#### 7.2 secure-clang wrapper
Acts as a security wrapper around Clang. It identifies C source files, creates temporary LLVM IR, invokes `opt` with the `TraversalPass` plugin, and checks the pass result. Only after successful policy validation does it invoke Clang.

#### 7.3 Policy configuration
JSON policies include:
* `original_protocol.json` (Full Security): Enables all 8 invariants.
* `signature_and_source_only.json`: Reduced configuration for constrained devices.

#### 7.4 Test fixtures and demonstration interface
The `tests/` directory provides test suites verifying each rule independently. The `web-demo/` application provides a graphical interface with live code editor, policy selector, diagnostics console, CodeCarbon emissions tracker, and compile history.

---

### 8. Initial Testing Plan
The repository provides secure and insecure source test cases and test harnesses intended to compile each test to LLVM IR, execute the policy pass and compare the observed outcome with the expected secure/insecure classification.

---

### 9. Current Progress and Limitations
* Core compiler-side design and `secure-clang` orchestration verified.
* Comprehensive policy checks for dominance, unsafe APIs, and secret scanning.
* Web demo exposes interactive audit and diagnostic breakdown.
* Runtime device operations, cross-language compilation, and AI-assisted remediation reserved for the End-Semester scope.

---

### 10. Conclusion and Next Steps
The mid-semester milestone establishes the compiler-enforcement foundation for a secure OTA update workflow. By placing policy checks in an LLVM pass and invoking that pass through `secure-clang`, the project moves critical update-security rules into the build process.
