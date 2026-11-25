# Code Comment Generation Using AST, NLP, and Intelligent Agent Security

- **Roll Numbers:** 25CSB1A55, 25CSB1A60
- **Course:** B.Tech 2nd Year — Compiler Design PBL (CD - PBL Projects 2026)

## Uploaded Files & Descriptions

### 1. Source Code (Upload)
- `agent_server.py` — Backend agent service implementing multi-pass code comment generation, code review, and edge-case/unit-test generation with untrusted-data isolation (`UNTRUSTED DATA`), complexity preservation, and error masking.
- `web/index.html` — Live Code Studio frontend UI featuring the code editor/viewer, diagnostics drawer, fix-preview gating, backend status checks, and the Edge Cases & Tests viewer.
- `tests/test_agent_server.py` — Unit test suite verifying prompt-injection isolation, complexity preservation, response schema handling, and error masking.
- `requirements-agent.txt` — Python dependencies required to run the agent backend and tests.
- `src/`, `tools/`, & `run_gui.py` — Core AST/NLP comment generation modules, utility scripts, and desktop GUI workspace launcher.

### 2. Documentation (Uploaded)
- `CD_MidSem_Project_Documentation_25CSB1A55-v2 (1).docx` — Mid-semester architecture and design documentation covering the AST/NLP pipeline and system overview.
- `CD_Project_Documentation_25CSB1A55 (1).docx` — Final project and security documentation detailing the multi-pass agent workflow, prompt-injection guardrails, and evaluation results.

### 3. Screen Recording (Uploaded)
- **End-to-End Demo Video:** Demonstrating live AST/NLP comment generation, security guardrails, and the Code Studio UI.

## How to Run Locally
> **Note:** `web/index.html` communicates with the FastAPI/Uvicorn backend (`agent_server.py`). Do not open `web/index.html` directly via `file://`, as it requires the backend server to render and handle API requests.

1. **Create and activate a virtual environment, then install dependencies:**
   ```bash
   python -m venv .venv
   # On Windows:
   .venv\Scripts\activate
   # On macOS/Linux:
   source .venv/bin/activate
   pip install -r requirements-agent.txt
