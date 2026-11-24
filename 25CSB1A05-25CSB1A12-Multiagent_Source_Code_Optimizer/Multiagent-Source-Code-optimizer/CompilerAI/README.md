# CompilerAI — Optimization Studio (Milestone 1)

CompilerAI is a developer-focused IDE studio designed for code optimization and security auditing. It coordinates two independent agent boundaries:
1. **Optimization Agent**
2. **Security Agent**

In Milestone 1, the full application architecture, UI shell matching the visual design, API contracts, deterministic mock agents, and sequential orchestrator pipelines are established and verified before real agent folders are integrated in subsequent milestones.

---

## Architecture Overview

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
  │ Run Contexts & Cancellation                                 │
  │ Two-Agent Orchestrator (Full Pipeline / Optimize / Security)│
  │ Event Stream Publisher (SSE)                                │
  │ Run & Artifact Store (Isolated by Run ID)                   │
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

## Supported Execution Modes

1. **Full Pipeline (`pipeline`)**: Strictly sequential execution (`Optimization Agent` → `Security Agent`). Security only assesses the verified optimized code returned by Optimization.
2. **Optimize (`optimize`)**: Executes only the Optimization Agent. Security is never called.
3. **Security (`security`)**: Executes only the Security Agent against the original source code. Optimization is never called.

---

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+ & npm

### Development Quickstart

#### 1. Backend Service
```powershell
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

#### 2. Frontend Application
```powershell
cd frontend
npm install
npm run dev
```

The frontend will run on `http://127.0.0.1:5173`, proxying `/api` requests to `http://127.0.0.1:8000`.

### Running Tests
```powershell
cd backend
python -m pytest
```

---

## Milestone 2 Status: Real Agent Folders Connected
- **Status**: Milestone 2 Complete. Real agent folders (`algo_agent` and `security_related_files`) are connected and active behind the stable adapter boundaries.
- **Backend Health**: `http://127.0.0.1:8000/api/health` reports `adapters: {"optimization": "real", "security": "real"}`.
- **Optimization Agent**: `algo_agent` (`optagent.agent.OptimizerAgent`) performs AST intent extraction, oracle generation, empirical complexity profiling, and transformation search.
- **Security Agent**: `security_related_files` (`agents.security_agent.SecurityAgent`) executes deep static AST scans and taint heuristics across 6 CWE vulnerability domains.
