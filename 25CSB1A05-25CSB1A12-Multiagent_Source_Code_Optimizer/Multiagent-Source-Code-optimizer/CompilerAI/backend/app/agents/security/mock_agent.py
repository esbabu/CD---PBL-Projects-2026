import asyncio
import datetime
from typing import Callable, Awaitable, List
from app.contracts.security import SecurityRequest, SecurityResult, SecurityFinding
from app.contracts.common import SourceKind
from app.contracts.events import RunEvent

class MockSecurityAgent:
    """
    Deterministic mock implementation of the Security Agent.
    Assesses source code and generates CWE-aligned security findings.
    Faithfully reports whether evaluation was performed on original or optimized source.
    """

    async def execute(
        self,
        request: SecurityRequest,
        emit: Callable[[RunEvent], Awaitable[None]],
    ) -> SecurityResult:
        start_time = datetime.datetime.now(datetime.timezone.utc)
        seq = 1

        async def send_event(event_type: str, status: str, message: str, data: dict = None):
            nonlocal seq
            event = RunEvent(
                run_id=request.run_id,
                seq=seq,
                type=event_type,
                agent="security",
                stage="security",
                status=status,
                timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                message=message,
                data=data or {},
            )
            seq += 1
            await emit(event)

        # 1. Agent started
        source_label = "Optimized Code" if request.source_kind == SourceKind.OPTIMIZED else "Original Source"
        await send_event(
            "agent_started",
            "running",
            f"Security Agent started vulnerability scanning on {source_label}",
            {
                "inference_mode": request.inference_mode.value,
                "source_kind": request.source_kind.value,
                "language": request.language,
            },
        )
        await asyncio.sleep(0.15)

        # Scripted failure testing support
        if request.options.get("mock_security_failure") or "FAIL_SECURITY" in request.source_code:
            await send_event(
                "agent_log",
                "running",
                "Security scanner crash: Static analysis engine failure (Scripted failure)",
            )
            await send_event(
                "agent_failed",
                "failed",
                "Security Agent encountered an unrecoverable analysis error",
                {"error": "Simulated security scanner failure"},
            )
            return SecurityResult(
                run_id=request.run_id,
                status="failed",
                source_kind=request.source_kind,
                findings=[],
                raw_result={"error": "Simulated security scan failure"},
                diagnostics=["Security analysis scanner terminated with error code 1."],
                duration_ms=150,
                is_demo=True,
            )

        # 2. Progress & Logs
        await send_event("agent_progress", "running", "Performing static taint analysis & buffer safety audit...", {"progress": 35})
        await asyncio.sleep(0.15)

        if request.source_kind == SourceKind.ORIGINAL:
            await send_event(
                "agent_log",
                "running",
                "Found CWE-193: Off-by-one boundary check (i <= n) in loop accessing array pointer",
            )
            await send_event(
                "agent_log",
                "running",
                "Found CWE-457: Use of Uninitialized Variable 'sum' without prior assignment",
            )
        else:
            await send_event(
                "agent_log",
                "running",
                "Verified boundary fix: Loop boundary condition strictly checked (i < n)",
            )
            await send_event(
                "agent_log",
                "running",
                "Verified variable initialization: 'sum' is explicitly zero-initialized",
            )

        await asyncio.sleep(0.15)
        await send_event("agent_progress", "running", "Evaluating memory safety and invariant integrity...", {"progress": 75})
        await asyncio.sleep(0.15)

        # Generate findings according to assessed source kind
        findings: List[SecurityFinding] = []
        if request.source_kind == SourceKind.ORIGINAL:
            findings = [
                SecurityFinding(
                    id="SEC-001",
                    title="Off-by-one Buffer Read Vulnerability",
                    severity="high",
                    description="Loop condition 'i <= n' permits accessing array index out-of-bounds when i equals n.",
                    line_number=10,
                    rule_or_cwe="CWE-193: Off-by-one Error",
                    remediation="Change loop guard condition to 'i < n' to avoid reading past allocated buffer boundary.",
                ),
                SecurityFinding(
                    id="SEC-002",
                    title="Uninitialized Local Variable Usage",
                    severity="medium",
                    description="Variable 'sum' is read during accumulation without an initial assignment.",
                    line_number=9,
                    rule_or_cwe="CWE-457: Use of Uninitialized Variable",
                    remediation="Explicitly initialize local variable: 'int sum = 0;'.",
                ),
                SecurityFinding(
                    id="SEC-003",
                    title="Unbounded Pointer Arithmetic Potential",
                    severity="low",
                    description="Pointer 'arr' is not checked for null before dereference in 'sumArray'.",
                    line_number=11,
                    rule_or_cwe="CWE-476: NULL Pointer Dereference",
                    remediation="Add null check guard at start of function: 'if (!arr) return 0;'.",
                ),
            ]
        else:
            # Evaluated against optimized code: show that previous critical issues were resolved,
            # only remaining informational/low finding persists.
            findings = [
                SecurityFinding(
                    id="SEC-OPT-001",
                    title="Unbounded Pointer Parameter Validation",
                    severity="info",
                    description="Pointer 'arr' has __restrict__ qualifier for performance; caller must guarantee non-null.",
                    line_number=7,
                    rule_or_cwe="CWE-476: NULL Pointer Dereference",
                    remediation="Consider adding an assertion or defensive guard: 'if (!arr) return 0;'.",
                )
            ]

        end_time = datetime.datetime.now(datetime.timezone.utc)
        duration_ms = int((end_time - start_time).total_seconds() * 1000)

        # Emit artifact event
        await send_event(
            "agent_artifact",
            "running",
            f"Security findings report generated ({len(findings)} findings)",
            {"findings_count": len(findings), "source_kind": request.source_kind.value},
        )
        await asyncio.sleep(0.1)

        # Completed
        await send_event(
            "agent_completed",
            "completed",
            f"Security Agent completed audit on {source_label} (Mock Demo)",
            {"duration_ms": duration_ms, "findings_count": len(findings)},
        )

        return SecurityResult(
            run_id=request.run_id,
            status="completed",
            source_kind=request.source_kind,
            findings=findings,
            raw_result={
                "agent": "MockSecurityAgent",
                "demo": True,
                "assessed_source_kind": request.source_kind.value,
                "findings": [f.model_dump() for f in findings],
            },
            diagnostics=[
                f"[DEMO RESULT] This security audit was generated by MockSecurityAgent.",
                f"Assessed Source Kind: {request.source_kind.value.upper()}.",
                "Results are for UI demonstration and test verification.",
            ],
            duration_ms=duration_ms,
            is_demo=True,
        )
