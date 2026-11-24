# CompilerAI — Agent Integration Contract & Folder Integration Model

This document defines the stable contracts between the CompilerAI application and the agent adapters, and describes the lifecycle for plugging in real agent folders in future milestones.

---

## 1. Stable Port Protocols (Python)

```python
from typing import Protocol, Callable, Awaitable
from app.contracts.optimization import OptimizationRequest, OptimizationResult
from app.contracts.security import SecurityRequest, SecurityResult
from app.contracts.events import RunEvent

class OptimizationAgentPort(Protocol):
    async def run(
        self,
        request: OptimizationRequest,
        emit: Callable[[RunEvent], Awaitable[None]],
    ) -> OptimizationResult:
        """Execute optimization and stream progress events."""
        ...

class SecurityAgentPort(Protocol):
    async def run(
        self,
        request: SecurityRequest,
        emit: Callable[[RunEvent], Awaitable[None]],
    ) -> SecurityResult:
        """Execute security audit and stream progress events."""
        ...
```

---

## 2. Request & Result Schemas

### Optimization Request & Result

```python
class OptimizationRequest(BaseModel):
    run_id: str
    source_code: str
    language: str
    inference_mode: InferenceMode  # "llm" | "heuristics"
    options: Dict[str, Any]

class OptimizationResult(BaseModel):
    run_id: str
    status: str                    # "completed" | "failed" | "not_performed"
    optimized_code: Optional[str]
    transformations: List[str]
    metrics: Dict[str, Any]
    raw_result: Dict[str, Any]
    diagnostics: List[str]
    duration_ms: int
    is_demo: bool = True
```

### Security Request & Result

```python
class SecurityRequest(BaseModel):
    run_id: str
    source_code: str
    language: str
    source_kind: SourceKind        # "original" | "optimized"
    inference_mode: InferenceMode  # "llm" | "heuristics"
    options: Dict[str, Any]

class SecurityFinding(BaseModel):
    id: str
    title: str
    severity: str                  # "critical" | "high" | "medium" | "low" | "info"
    description: str
    line_number: Optional[int]
    rule_or_cwe: Optional[str]
    remediation: Optional[str]

class SecurityResult(BaseModel):
    run_id: str
    status: str                    # "completed" | "failed"
    source_kind: SourceKind
    findings: List[SecurityFinding]
    raw_result: Dict[str, Any]
    diagnostics: List[str]
    duration_ms: int
    is_demo: bool = True
```

---

## 3. Real Agent Integrations (Milestone 2)

Both agent folders are connected and operational:

### 3.1 Optimization Agent (`algo_agent`)
- **Directory**: `c:\Users\user\Desktop\algo_agent\algo_agent`
- **Class**: `optagent.agent.OptimizerAgent`
- **Execution**:
  - Request: `OptimizeRequest(source=..., language=..., budget=SearchBudget(max_candidates=3, max_time_s=15.0))`
  - Asynchronous Execution: Runs in background thread via `asyncio.to_thread` to maintain responsive SSE streaming.
  - Telemetry: Binds `progress_callback(stage, msg, pct)` to real-time `agent_progress` SSE events.
  - Output Normalization:
    - `optimized_code`: `res.report.optimized_source`
    - `metrics`: `{"overall_speedup": res.report.overall_speedup, "evidence_tier": res.report.evidence_tier}`
    - `transformations`: derived from `res.report.complexity.bottlenecks_resolved`

### 3.2 Security Agent (`security_related_files`)
- **Directory**: `c:\Users\user\Desktop\security_related_files (2)\security_related_files`
- **Class**: `agents.security_agent.SecurityAgent`
- **Execution**:
  - `agent.audit_code(source_code=..., file_path=...)`
  - Scans across 6 CWE vulnerability domains (Buffer Overflow, Use-After-Free, Command Injection, Insecure Deserialization, Broken Cryptography, TLS Disabled).
  - Output Normalization:
    - Maps `all_vulnerabilities` into strongly-typed `SecurityFinding` objects with line numbers, CWE-IDs, descriptions, and remediations.
    - Honors `source_kind: original | optimized` for upstream/downstream auditing.
