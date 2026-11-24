# CompilerAI — Milestone 1 Decisions, Assumptions & Deferred Scope

## 1. Key Architectural Decisions

1. **Two-Agent Model Exclusivity**:
   - The application supports strictly **Optimization Agent** and **Security Agent**.
   - Legacy concepts of "Analyze" and "Verify" from old references are eliminated from UI, routing, contracts, and backend.

2. **Sequential Full Pipeline Invariant**:
   - In Full Pipeline mode, the Security Agent is executed strictly downstream of Optimization.
   - Concurrency (`asyncio.gather`) is prohibited for the stages.
   - If Optimization fails or returns no code artifact, Security is not invoked on guessed content.

3. **Adapter Boundary Decoupling**:
   - The orchestrator and frontend interact only with `OptimizationAgentPort` and `SecurityAgentPort`.
   - The mock agents are isolated behind these adapters and clearly label all outputs with `is_demo: true` and visible UI demo tags.

4. **Honest Capabilities and Health Reporting**:
   - `/api/health` honestly reports that adapters are in `mock` mode and LLM connection is `not_configured`.
   - The UI displays an honest service badge rather than claiming a live model is connected.

5. **Run Isolation & Result Freshness**:
   - Each execution produces an independent `run_id`.
   - All results and events are scoped strictly to their `run_id`. Starting a new run immediately clears previous results or marks them stale, preventing cross-run contamination.

---

## 2. Assumptions Requiring Future User Confirmation

1. **Agent Execution Environments**:
   - Real agent folders will be supplied in Milestone 2.
   - Assumptions: each agent folder will contain its own runnable entrypoint (e.g. Python CLI, binary, or bash/powershell script) that accepts source code via file path or stdin and writes a JSON output artifact.

2. **Schema Mapping**:
   - The real agent folders may have different JSON schemas from the mock implementation. The adapters in `app/agents/optimization/adapter.py` and `app/agents/security/adapter.py` will inspect and map those fields without altering the frontend API contracts.

3. **Fallback Policy in Production**:
   - When real agents are connected, should a failure in Optimization offer an optional user prompt to run Security against the original source code? (Currently rejected to avoid implicit fallbacks; requires explicit user authorization).

---

## 3. Deliberately Deferred Scope (Not in Milestone 1)

- Connecting to live LLM APIs (Ollama, OpenAI, Gemini, etc.).
- Heavy database or broker dependencies (PostgreSQL, Redis, RabbitMQ).
- Multi-user authentication and authorization.
- Real compiler toolchain execution (GCC, Clang, rustc).
