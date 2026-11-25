# 25CSB1A51 — Agentic AI Multi-Language Compiler & Debugger

**Student:** Arpit Ratnakar  
**Roll Number:** 25CSB1A51  
**Project Title:** Agentic AI Multi-Language Compiler & Debugger (v3.0)

## Project Description

An Automated Program Repair (APR) teaching assistant and developer tool designed to securely diagnose and fix compilation errors, syntax errors, and runtime bugs across multiple programming languages (**C++, Python, Java, C, and JavaScript**) using localized agentic AI (Google Gemini API and local Ollama / Llama 3).

## Key Features
- **Multi-Language Support:** C++, C, Python, Java, and JavaScript via modular adapters (`languages/`)
- **Dual AI Engine:** Google Gemini API + 100% offline local Ollama (Llama 3)
- **Dual Sandbox Execution:** Hardened Docker container sandbox and local subprocess sandbox
- **ReAct Agentic Reasoning:** Step-by-step tool turns, error classification, and verified fix diffs
- **Security Guardrails:** Security pre-scan, DLP service, prompt injection detection, access control, execution guard, supply chain audit, and Human-in-the-Loop (HITL) gateway
- **Carbon & Green Telemetry:** Energy consumed & carbon emissions tracking via CodeCarbon (`emissions.csv`)
- **Configurable Test Suite Evaluator:** Automated stdin/expected output diffing

## Quick Start
```bash
./run.sh
# or
./.venv/bin/streamlit run app.py
```
Run automated tests:
```bash
./.venv/bin/python3 -m unittest discover -s tests
```

## Files Submitted

### Source Code
| File | Description |
|------|-------------|
| `app.py` | Main Streamlit web application (IDE UI + orchestration) |
| `agent_core.py` | Multi-language ReAct agentic reasoning orchestrator |
| `llm_client.py` | Dual LLM client (Google Gemini API + local Ollama) |
| `compiler_service.py` | Multi-language compilation and test suite service |
| `error_classifier.py` | Language-aware rule-based error classification engine |
| `fix_engine.py` | AI-powered fix extraction & sandboxed verification |
| `sandbox_runner.py` | Dual execution engine (Docker container & local subprocess) |
| `security_analyzer.py` | Security vulnerability analyzer |
| `access_control.py` | Role-based access control |
| `agent_memory.py` | Agent memory and context management |
| `audit_logger.py` | Security audit logging |
| `dlp_service.py` | Data loss prevention (DLP) service |
| `execution_guard.py` | Execution safety guard |
| `hitl_gateway.py` | Human-in-the-loop gateway |
| `injection_detector.py` | Prompt/code injection detection |
| `output_sanitizer.py` | Output sanitization |
| `policy_gateway.py` | Policy enforcement gateway |
| `secure_scan.py` | Multi-language security pre-scan guardrail |
| `security_config.py` | Security configuration |
| `security_logger.py` | Security event logger |
| `supply_chain.py` | Supply chain dependency security |
| `tool_validator.py` | Tool validation module |
| `github_scraper.py` | GitHub security keyword miner (sanitized) |
| `lldb_engine.py` | LLDB debugger integration |
| `error_logger.py` | Error logging module |
| `build_documents.py` | Documentation builder script |
| `render_architecture_diagrams.py` | Architecture diagram renderer |
| `test_runner.py` | Configurable test case evaluation & diff engine |
| `debug_target.cpp`, `final_tests.cpp`, `temp_source.cpp`, `test1.cpp` | Sample C++ test targets |

### Subdirectories
| Folder | Description |
|--------|-------------|
| `languages/` | Modular language adapters (`base.py`, `c_adapter.py`, `cpp_adapter.py`, `java_adapter.py`, `javascript_adapter.py`, `python_adapter.py`, `__init__.py`) |
| `tests/` | Automated multi-language, agent orchestration, and `tests/security/` unit/red-team test suites |
| `images/` | Architecture diagrams and UI figures |
| `scripts/` | Setup and dependency audit scripts (`setup.sh`, `audit_dependencies.py`) |
| `.streamlit/` | Streamlit theme and app configuration (`config.toml`) |

### Configuration & Deployment
| File | Description |
|------|-------------|
| `requirements.txt`, `requirements.lock` | Python dependencies and locked versions |
| `Dockerfile`, `Dockerfile.app` | Docker container images |
| `docker-compose.yml`, `docker-compose.prod.yml` | Docker Compose definitions |
| `nginx.conf` | Nginx reverse proxy configuration |
| `Makefile`, `run.sh` | Build automation and one-click launcher |
| `.dockerignore`, `.env.example` | Docker ignore rules and environment variable template |

### Documentation
| File | Description |
|------|-------------|
| `TOA_END_DOC.docx` | End-semester project submission document |
| `Multi_Language_Compiler_Debugger_Documentation.pdf` | Complete project documentation (PDF) |
| `Multi_Language_Compiler_Debugger_Documentation.docx` | Complete project documentation (Word) |
| `PROJECT_DOCUMENTATION_PAPER.md` | Full project documentation paper |
| `DEPLOYMENT.md` | Deployment guide |
| `SECURITY.md`, `SECURITY_AUDIT.md` | Security policy and audit report |
| `METHODOLOGY_REPORT.txt` | Methodology report |

### Data & Telemetry Logs
| File | Description |
|------|-------------|
| `compiler_errors.csv` | Compiler error dataset |
| `emissions.csv` | Carbon emissions telemetry data |
| `security_audit.jsonl` | Security audit log |
| `system_interactions.json` | System interaction logs |
| `inventory.json` | Tool & component inventory |
| `powermetrics_log.txt` | Power metrics telemetry log |

### Large Files (Google Drive — NITW Mail Access)
> Files exceeding GitHub's file size limit (`toa_project.zip` and `END_RECORDING.mov` demo recording) are hosted in Google Drive (accessible with NITW mail):
- **Screen Recording (Demo Video):** https://drive.google.com/file/d/1Wu3aF2IQeqH5sggshep8f94nliFuVjVR/view?usp=drive_link
- **Full Project Archive (`toa_project.zip`):** https://drive.google.com/file/d/17Emv4hLqGuey3kc4sr_ogxwaF9hbeGUS/view?usp=drive_link
- **Google Drive Folder:** https://drive.google.com/drive/folders/1szEW7pJ7j7cuxAp3Y8SE4atMmo8VRF5v
