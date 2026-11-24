import datetime
import asyncio
from typing import Callable, Awaitable, Optional
from app.contracts.requests import CreateRunRequest, RunMode, InferenceMode
from app.contracts.common import SourceKind
from app.contracts.events import RunEvent
from app.contracts.optimization import OptimizationRequest, OptimizationResult
from app.contracts.security import SecurityRequest, SecurityResult
from app.agents.base import OptimizationAgentPort, SecurityAgentPort
from app.agents.optimization.adapter import OptimizationAdapter
from app.agents.security.adapter import SecurityAdapter
from app.services.event_bus import event_bus
from app.services.result_store import result_store
from app.orchestration.cancellation import CancellationToken
from app.core.config import settings

SUPPORTED_LANGUAGES = {"c", "cpp", "c++", "python", "javascript", "js"}

class PipelineOrchestrator:
    """
    Coordinates Optimization and Security agents across the 3 execution modes.
    Enforces strictly sequential ordering in Full Pipeline mode.
    """

    def __init__(
        self,
        optimization_adapter: Optional[OptimizationAgentPort] = None,
        security_adapter: Optional[SecurityAgentPort] = None,
    ):
        self.optimization_adapter = optimization_adapter or OptimizationAdapter()
        self.security_adapter = security_adapter or SecurityAdapter()

    async def execute_run(
        self,
        run_id: str,
        request: CreateRunRequest,
        cancellation_token: CancellationToken,
    ) -> None:
        seq = 0

        async def emit(event: RunEvent) -> None:
            await event_bus.publish(event)

        async def send_lifecycle_event(
            event_type: str,
            status: str,
            message: str,
            stage: Optional[str] = None,
            agent: Optional[str] = None,
            data: dict = None,
        ) -> None:
            nonlocal seq
            seq += 1
            evt = RunEvent(
                run_id=run_id,
                seq=seq,
                type=event_type,
                agent=agent,
                stage=stage,
                status=status,
                timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                message=message,
                data=data or {},
            )
            await emit(evt)

        # Ensure run record exists in store
        if not result_store.get_run(run_id):
            result_store.create_run(
                run_id=run_id,
                request=request,
                created_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            )

        # 1. Validate source code and language
        if not request.source_code or not request.source_code.strip():
            result_store.set_status(run_id, "failed", "Empty source code submitted")
            await send_lifecycle_event(
                "error", "failed", "Execution rejected: Source code cannot be empty"
            )
            await send_lifecycle_event(
                "run_completed", "failed", "Run aborted: empty source code"
            )
            return

        lang_normalized = request.language.lower().strip()
        if lang_normalized not in SUPPORTED_LANGUAGES:
            result_store.set_status(run_id, "failed", f"Unsupported language: {request.language}")
            await send_lifecycle_event(
                "error",
                "failed",
                f"Execution rejected: Language '{request.language}' is not supported. Supported: {', '.join(sorted(SUPPORTED_LANGUAGES))}",
            )
            await send_lifecycle_event(
                "run_completed", "failed", "Run aborted: unsupported language"
            )
            return

        # 2. Run started
        result_store.set_status(run_id, "running")
        await send_lifecycle_event(
            "run_started",
            "running",
            f"Run started in '{request.mode.value}' mode ({lang_normalized})",
            data={"mode": request.mode.value, "inference_mode": request.inference_mode.value},
        )

        # If Security agent in LLM mode requires local Ollama, verify availability
        if request.mode in (RunMode.SECURITY, RunMode.PIPELINE) and request.inference_mode == InferenceMode.LLM:
            from app.api.routes_health import get_live_ollama_status

            ollama_info = get_live_ollama_status()
            if not (ollama_info.get("reachable") and ollama_info.get("models")):
                mode_note = (
                    "Backend is operating in Mock Demo mode."
                    if settings.optimization_adapter_mode == "mock" and settings.security_adapter_mode == "mock"
                    else f"Ollama is unavailable ({ollama_info.get('remediation') or 'not reachable'}); security analysis will rely on deterministic rules."
                )
                await send_lifecycle_event(
                    "warning",
                    "running",
                    f"Notice: 'LLM' inference mode selected for security. {mode_note}",
                )

        try:
            # 3. Branch by mode
            if request.mode == RunMode.OPTIMIZE:
                await self._execute_optimize_mode(run_id, request, cancellation_token, emit, send_lifecycle_event)

            elif request.mode == RunMode.SECURITY:
                await self._execute_security_mode(run_id, request, cancellation_token, emit, send_lifecycle_event)

            elif request.mode == RunMode.PIPELINE:
                await self._execute_full_pipeline_mode(run_id, request, cancellation_token, emit, send_lifecycle_event)

        except asyncio.CancelledError:
            result_store.set_status(run_id, "cancelled")
            await send_lifecycle_event("run_cancelled", "cancelled", "Run cancelled by user request")
        except Exception as ex:
            result_store.set_status(run_id, "failed", str(ex))
            await send_lifecycle_event("error", "failed", f"Unexpected execution error: {str(ex)}")
            await send_lifecycle_event("run_completed", "failed", f"Run failed: {str(ex)}")

    async def _execute_optimize_mode(
        self,
        run_id: str,
        request: CreateRunRequest,
        token: CancellationToken,
        emit: Callable[[RunEvent], Awaitable[None]],
        send_lifecycle: Callable[..., Awaitable[None]],
    ) -> None:
        if token.is_cancelled:
            result_store.set_status(run_id, "cancelled")
            await send_lifecycle("run_cancelled", "cancelled", "Run cancelled before starting optimization")
            return

        opt_req = OptimizationRequest(
            run_id=run_id,
            source_code=request.source_code,
            language=request.language,
            inference_mode=request.inference_mode,
            options={**request.options, "mode": "optimize"},
        )

        opt_result = await self.optimization_adapter.run(opt_req, emit)
        result_store.set_optimization_result(run_id, opt_result)

        if token.is_cancelled:
            result_store.set_status(run_id, "cancelled")
            await send_lifecycle("run_cancelled", "cancelled", "Run cancelled during optimization")
            return

        if opt_result.status == "completed":
            result_store.set_status(run_id, "completed")
            await send_lifecycle(
                "run_completed",
                "completed",
                "Optimize run completed successfully",
                data={"transformations": len(opt_result.transformations)},
            )
        else:
            result_store.set_status(run_id, "failed", "Optimization stage failed")
            await send_lifecycle(
                "run_completed",
                "failed",
                "Optimize run failed",
                data={"diagnostics": opt_result.diagnostics},
            )

    async def _execute_security_mode(
        self,
        run_id: str,
        request: CreateRunRequest,
        token: CancellationToken,
        emit: Callable[[RunEvent], Awaitable[None]],
        send_lifecycle: Callable[..., Awaitable[None]],
    ) -> None:
        if token.is_cancelled:
            result_store.set_status(run_id, "cancelled")
            await send_lifecycle("run_cancelled", "cancelled", "Run cancelled before starting security analysis")
            return

        sec_req = SecurityRequest(
            run_id=run_id,
            source_code=request.source_code,
            language=request.language,
            source_kind=SourceKind.ORIGINAL,
            inference_mode=request.inference_mode,
            options=request.options,
        )

        sec_result = await self.security_adapter.run(sec_req, emit)
        result_store.set_security_result(run_id, sec_result)

        if token.is_cancelled:
            result_store.set_status(run_id, "cancelled")
            await send_lifecycle("run_cancelled", "cancelled", "Run cancelled during security audit")
            return

        if sec_result.status == "completed":
            result_store.set_status(run_id, "completed")
            await send_lifecycle(
                "run_completed",
                "completed",
                "Security audit completed successfully",
                data={"findings_count": len(sec_result.findings)},
            )
        else:
            result_store.set_status(run_id, "failed", "Security analysis failed")
            await send_lifecycle(
                "run_completed",
                "failed",
                "Security run failed",
                data={"diagnostics": sec_result.diagnostics},
            )

    async def _execute_full_pipeline_mode(
        self,
        run_id: str,
        request: CreateRunRequest,
        token: CancellationToken,
        emit: Callable[[RunEvent], Awaitable[None]],
        send_lifecycle: Callable[..., Awaitable[None]],
    ) -> None:
        # STRICT SEQUENTIAL RULE: Stage 1 = Optimization, Stage 2 = Security
        # Security MUST NOT start until Optimization produces usable code.

        if token.is_cancelled:
            result_store.set_status(run_id, "cancelled")
            await send_lifecycle("run_cancelled", "cancelled", "Run cancelled before pipeline start")
            return

        # Stage 1: Optimization
        opt_req = OptimizationRequest(
            run_id=run_id,
            source_code=request.source_code,
            language=request.language,
            inference_mode=request.inference_mode,
            options={**request.options, "mode": "pipeline"},
        )

        opt_result = await self.optimization_adapter.run(opt_req, emit)
        result_store.set_optimization_result(run_id, opt_result)

        if token.is_cancelled:
            result_store.set_status(run_id, "cancelled")
            await send_lifecycle("run_cancelled", "cancelled", "Run cancelled after optimization stage")
            return

        # Gate check: did Optimization succeed?
        if opt_result.status != "completed":
            result_store.set_status(run_id, "failed", "Pipeline failed at Optimization stage")
            await send_lifecycle(
                "error",
                "failed",
                "Pipeline halted: Optimization Agent failed. Security Agent will NOT be invoked.",
                stage="optimization",
            )
            await send_lifecycle(
                "run_completed",
                "failed",
                "Full Pipeline failed because Optimization Agent failed",
            )
            return

        # Gate check: was usable optimized code generated?
        if not opt_result.optimized_code or not opt_result.optimized_code.strip():
            result_store.set_status(
                run_id,
                "partially_completed",
                "Missing optimized code artifact. Security stage skipped.",
            )
            await send_lifecycle(
                "warning",
                "partially_completed",
                "Optimization completed without code output. Skipping Security stage to prevent evaluation on guessed content.",
            )
            await send_lifecycle(
                "run_partially_completed",
                "partially_completed",
                "Pipeline ended partially completed: Missing optimized code artifact",
            )
            return

        # Stage 2: Security Assessment
        await send_lifecycle(
            "pipeline_stage_changed",
            "running",
            "Optimization stage completed. Proceeding sequentially to Security stage with optimized code artifact.",
            stage="security",
        )

        sec_req = SecurityRequest(
            run_id=run_id,
            source_code=opt_result.optimized_code,
            language=request.language,
            source_kind=SourceKind.OPTIMIZED,
            inference_mode=request.inference_mode,
            options=request.options,
        )

        sec_result = await self.security_adapter.run(sec_req, emit)
        result_store.set_security_result(run_id, sec_result)

        if token.is_cancelled:
            result_store.set_status(run_id, "cancelled")
            await send_lifecycle("run_cancelled", "cancelled", "Run cancelled during security stage")
            return

        if sec_result.status == "completed":
            result_store.set_status(run_id, "completed")
            await send_lifecycle(
                "run_completed",
                "completed",
                "Full Pipeline completed successfully (Optimization → Security)",
                data={
                    "transformations": len(opt_result.transformations),
                    "findings_count": len(sec_result.findings),
                },
            )
        else:
            result_store.set_status(
                run_id,
                "partially_completed",
                "Optimization succeeded, but Security audit failed",
            )
            await send_lifecycle(
                "run_partially_completed",
                "partially_completed",
                "Full Pipeline partially completed: Optimization artifact preserved, Security audit failed",
                data={"diagnostics": sec_result.diagnostics},
            )
