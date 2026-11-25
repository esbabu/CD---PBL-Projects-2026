**Title:** Secure Agentic AI Compiler — 25CSB1A71

---

**SOURCE CODE:**

| File Name | Description |
|---|---|
| `api/server.py` | Multi-threaded REST API server with `/api/compile`, `/api/results`, `/api/status`, `/api/audit`, `/api/safe_stop` endpoints |
| `core/orchestrator/orchestrator.py` | 22-state zero-trust LLVM IR optimization orchestrator (main pipeline engine) |
| `core/orchestrator/state_machine.py` | State machine definition with 22 compiler pipeline states |
| `core/orchestrator/decision_engine.py` | Decision logic for optimization pass selection |
| `core/frontend/ingestion.py` | Untrusted C/C++ source ingestion and quarantine module |
| `core/frontend/clang_frontend.py` | Clang compiler frontend integration |
| `core/ir/validator.py` | Deterministic LLVM IR validator |
| `core/ir/profiler.py` | Static IR profiler for HOT/COLD function classification |
| `core/security/security_gate.py` | Zero-trust security gate |
| `core/security/signing_service.py` | Cryptographic artifact signing service |
| `core/verification/correctness_gate.py` | Correctness verification gate |
| `core/verification/canary.py` | Canary drift detection module |
| `core/verification/differential.py` | Differential IR verification engine |
| `core/optimizer/pass_pipeline.py` | LLVM optimization pass pipeline manager |
| `core/optimizer/candidate.py` | Candidate IR management |
| `core/optimizer/cost_benefit.py` | Cost-benefit analysis for optimization candidates |
| `core/benchmark/benchmark_engine.py` | Statistical benchmarking engine |
| `core/experience/experience_store.py` | Agent learning and experience database (SQLite-backed) |
| `core/observability/audit_log.py` | Hash-chained append-only audit log |
| `core/provenance/provenance_generator.py` | Cryptographic provenance certificate generator |
| `core/provenance/replay_engine.py` | Deterministic replay verification engine |
| `core/agents/ir_tuner.py` | AI advisor agent for IR-level tuning |
| `core/agents/hw_tuner.py` | AI advisor agent for hardware-level tuning |
| `core/agents/security_analyzer.py` | AI advisor agent for security analysis |
| `core/agents/test_generator.py` | AI advisor agent for test case generation |
| `policy/policy_loader.py` | Policy enforcement loader |
| `policy/policy_schema_validator.py` | Policy schema validator |
| `policy/policy_config.json` | Signed policy configuration file |
| `sandbox/process_sandbox.py` | Process-level sandboxing |
| `run_demo.py` | End-to-end pipeline demo script |
| `run_secure_compiler.py` | CLI compiler entry point with argument parsing |
| `src/pipeline.py` | Pipeline smoke test runner |
| `src/web_ui/app.py` | Standalone results dashboard server (port 5050) |
| `src/agents/boss_agent.py` | Boss agent orchestrating sub-agents |
| `src/agents/ir_tuner_agent.py` | IR tuner agent (original implementation) |
| `src/agents/fixer_agent.py` | Fixer agent for IR correction |
| `src/agents/hw_tuner_agent.py` | Hardware tuner agent (original implementation) |
| `web/index.html` | HFT Compiler interactive Web UI dashboard (HTML) |
| `web/app.js` | Dashboard JavaScript — polls `/api/results` every 5 seconds |
| `web/style.css` | Dashboard CSS styling |
| `examples/hft_strategy.cpp` | High-frequency trading strategy C++ benchmark source |
| `examples/enterprise_hft_engine.cpp` | Enterprise HFT engine C++ example |
| `examples/market_maker.cpp` | Market maker C++ example |
| `examples/order_book_engine.cpp` | Order book engine C++ example |
| `cpp/ir_scanner/ir_scanner.cpp` | Native C++ LLVM IR scanner tool |
| `cpp/profiler/profiler.cpp` | Native C++ profiler tool |
| `cpp/benchmark/benchmark_harness.cpp` | Native C++ benchmark harness |
| `tests/test_phase1_scaffolding.py` | Phase 1 test: project scaffolding |
| `tests/test_phase2_core_pipeline.py` | Phase 2 test: core pipeline |
| `tests/test_phase3_ai_agents.py` | Phase 3 test: AI agents |
| `tests/test_phase4_security.py` | Phase 4 test: security gate |
| `tests/test_phase5_benchmarking.py` | Phase 5 test: benchmarking engine |
| `tests/test_phase6_verification.py` | Phase 6 test: verification |
| `tests/test_phase7_provenance.py` | Phase 7 test: provenance & replay |
| `tests/test_phase8_web_api.py` | Phase 8 test: web API endpoints |
| `tests/test_phase9_adversarial_security.py` | Phase 9 test: adversarial/security stress tests |
| `Makefile` | Build and test automation |

---

**DOCUMENTATION:**

| File Name | Description |
|---|---|
| `ARCHITECTURE/Architecture_25CSB1A71.docx` | Full system architecture document |
| `Reports/25CSB1A71_End_Report.docx` | End-term project report |
| `Reports/25CSB1A71_Mid_Report.docx` | Mid-term project report |
| `web/SecAICodeTutor_Final_Submission.docx` | Final submission document |
| `docs/state_machine.md` | 22-state machine specification |
| `docs/threat_model.md` | Zero-trust threat model |
| `docs/anti_patterns.md` | HFT latency anti-patterns catalog |

---

**SCREEN RECORDINGS:**

| File Name | Description |
|---|---|
| `Reports/build_summary.json - Agentic-AI-Compiler-main-backup - Visual Studio Code 2026-11-19 18-21-55.mp4` | Live demo of the full Agentic AI Compiler pipeline running end-to-end in VS Code (~73 MB) |
