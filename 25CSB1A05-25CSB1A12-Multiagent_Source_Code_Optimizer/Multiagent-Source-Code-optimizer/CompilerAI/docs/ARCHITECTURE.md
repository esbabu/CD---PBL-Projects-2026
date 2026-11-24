# CompilerAI — Architecture Specification (Milestone 1)

## Overview

CompilerAI is a high-performance developer studio designed for automated code optimization and security auditing. It is architected around **exactly two primary agent boundaries**:

1. **Optimization Agent**
2. **Security Agent**

The orchestrator coordinates these two independent subsystems without performing domain-specific optimizations or vulnerability scans itself.

---

## Architectural Topology

```
                         COMPILERAI FRONTEND
  ┌─────────────────────────────────────────────────────────────┐
  │ Header: Mode | Inference | Status | Theme | Run             │
  │                                                             │
  │ ┌────────────────────────┐  ┌─────────────────────────────┐ │
  │ │ SOURCE CODE            │  │ LIVE PIPELINE               │ │
  │ │ Monaco Code Editor     │  │ Real-time stage graph & SSE │ │
  │ └────────────────────────┘  └─────────────────────────────┘ │
  │                                                             │
  │ Output | Optimized Code | Security | Messages                │
  └──────────────────────────────┬──────────────────────────────┘
                                 │ REST + SSE
                                 ▼
                       BACKEND RUN SERVICE
  ┌─────────────────────────────────────────────────────────────┐
  │ Request Validation                                          │
  │ Run Manager / Run Context / Cancellation                    │
  │ Two-Agent Orchestrator                                      │
  │ Event Publisher (SSE)                                       │
  │ Result Store (Strict Run ID Isolation)                      │
  └───────────────────┬─────────────────────┬───────────────────┘
                      │                     │
                      ▼                     ▼
            OPTIMIZATION ADAPTER      SECURITY ADAPTER
                      │                     │
                      ▼                     ▼
             MOCK OPTIMIZER          MOCK SECURITY AGENT
             (Milestone 1)           (Milestone 1)
```

---

## System Responsibilities

### Frontend
- **State Management**: Managed via an immutable reducer pattern (`runReducer`).
- **Live Event Ingestion**: Subscribes to Server-Sent Events (`/api/runs/{run_id}/events`) and updates the stage graph, status badges, and message log in real-time.
- **Result Presentation**:
  - `Output`: Runtime execution logs or concise run-level summary.
  - `Optimized Code`: Transformed code with metrics, rationale, and "Apply to Source" capability.
  - `Security`: Vulnerability findings (CWE-aligned) with severity, description, line number, remediation, and assessed source kind badge (`original` vs `optimized`).
  - `Messages`: Chronological execution, integration, and diagnostics feed.

### Backend Run Service
- **FastAPI Core**: Validates requests via Pydantic v2 schemas and enforces language and syntax boundaries.
- **Pipeline Orchestrator**: Executes selected agent workflows with strictly enforced sequential ordering in Full Pipeline mode.
- **Run Manager & Cancellation**: Manages asynchronous tasks and provides graceful, responsive cancellation via tokens.
- **Event Bus**: In-memory event distribution with replay support for reconnecting clients.
- **Result Store**: Complete run-isolation ensuring no state or artifacts are leaked across runs.

### Adapters & Ports
- **Optimization Port (`OptimizationAgentPort`)**: Contract for receiving code and returning structured transformation data.
- **Security Port (`SecurityAgentPort`)**: Contract for auditing code and returning CWE-aligned vulnerability findings.
- **Mock Implementations**: Deterministic mock agents provide realistic progress telemetry and artifacts for testing before real agent folders are connected.
