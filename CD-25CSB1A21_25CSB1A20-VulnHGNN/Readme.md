# CD-25CSB1A21_25CSB1A20 — VulnHGNN

**Project title:** VulnHGNN 2.0 — SecureCC  
**Team roll numbers:** 25CSB1A21, 25CSB1A20  

**Short description:** SecureCC is a local-first security workbench for C, C++, and Java. It uses LLVM IR, heterogeneous graph–based CWE detection (VulnHGNN), localization, explanation, and optional automated healing, with a Flask web workbench for analysis and live linting.

---

## Contents of this folder

This README lists the files and subfolders uploaded for the CD PBL submission, as required for the course GitHub workflow (fork → upload → pull request to [CD---PBL-Projects-2026](https://github.com/esbabu/CD---PBL-Projects-2026)).

### Demo

| File | Description |
|------|-------------|
| `Demo.mp4` | Demo video showing the VulnHGNN / SecureCC web workbench and analysis pipeline (compile, detect CWEs, visualization, and related features). |

### Source code — `sourceCode/`

| Path | Description |
|------|-------------|
| `sourceCode/README.md` | Main project README: installation, Docker, CLI commands, and web workbench usage. |
| `sourceCode/requirements.txt` | Python dependencies for running SecureCC. |
| `sourceCode/pyproject.toml` | Package metadata and editable install configuration for the `securecc` CLI. |
| `sourceCode/Dockerfile` | Container image build for UI and API on port 5050. |
| `sourceCode/CD_PROJECT_DOCUMENTATION.docx` | Consolidated CD project documentation (Word). |
| `sourceCode/src/` | Core implementation: V2 pipeline (compilation, detection, localization, explain, heal, SecureCC web app, HGNN/graph logic). |
| `sourceCode/docs/` | Additional docs: `INSTALL.md`, `CLI.md`, `MANUAL.md`, `SECURITY_MODEL.md`, `RELEASE_CHECKLIST.md`, and related materials. |
| `sourceCode/tests/` | Regression and release verification shell scripts. |
| `sourceCode/test_files/` | C/C++ sample programs and tests for specific CWEs and combo scenarios. |
| `sourceCode/configs/` | Configuration (e.g. `behavior.json`). |
| `sourceCode/scripts/` | Helper scripts for fixtures and tooling. |
| `sourceCode/data/` | Generated or sample IR/parsed artifacts used for analysis and tests. |

> **Note:** The `sourceCode/.pip_packages/` directory (if present locally) is a vendored dependency cache and is typically **not** uploaded to GitHub; use `pip install` per `sourceCode/README.md` instead.

### Documentation — `sourceCode/Documentation/`

| File | Description |
|------|-------------|
| `Project Report.pdf` | Formal project report for VulnHGNN / SecureCC. |
| `VulnHGNN.pdf` | Project documentation (PDF). |
| `VulnHGNN_2.0.pdf` | VulnHGNN 2.0 documentation (PDF). |
| `VulnHGNN.docx` | Project documentation (Word). |
| `VulnHGNN_2.0_Project_Documentation.docx` | VulnHGNN 2.0 project documentation (Word). |

---

## Large files (Google Drive)

If any upload exceeds GitHub file size limits, host the file on Google Drive and link it here. Share with **anyone with a NITW mail** can access, as per course instructions.

| File | Drive link |
|------|------------|
| `Demo.mp4` | *(Add link here if uploaded via Drive instead of GitHub)* |

---

## Submission checklist (from course instructions)

1. **Fork** the instructor repository: `https://github.com/esbabu/CD---PBL-Projects-2026.git`
2. **Upload** this folder (`CD-25CSB1A21_25CSB1A20-VulnHGNN/`) under your fork, including this `Readme.md` and all listed assets.
3. **Commit** changes after uploads complete.
4. **Open a pull request** with a title such as: `Added my project 25CSB1A21_25CSB1A20 VulnHGNN`

To fix mistakes: delete and recommit individual files on your fork. To remove an entire folder, delete all files inside it first (GitHub does not allow deleting an empty folder path in one step).

---

## Quick reference

- **Primary entry point for running the project:** see `sourceCode/README.md`
- **Typical run:** `securecc web` → open `http://127.0.0.1:5050`