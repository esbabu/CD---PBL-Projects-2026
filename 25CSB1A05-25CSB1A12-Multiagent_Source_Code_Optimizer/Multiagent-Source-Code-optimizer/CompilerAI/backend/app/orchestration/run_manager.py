import uuid
import datetime
import asyncio
from typing import Dict, Optional
from app.contracts.requests import CreateRunRequest, RunResponse
from app.services.result_store import result_store
from app.orchestration.orchestrator import PipelineOrchestrator
from app.orchestration.cancellation import cancellation_manager

class RunManager:
    """
    Manages the lifecycle, background tasks, and isolation of all runs.
    """

    def __init__(self, orchestrator: Optional[PipelineOrchestrator] = None):
        self.orchestrator = orchestrator or PipelineOrchestrator()
        self._tasks: Dict[str, asyncio.Task] = {}

    def start_run(self, request: CreateRunRequest, background_tasks=None) -> RunResponse:
        run_id = f"run-{uuid.uuid4().hex[:8]}"
        created_at = datetime.datetime.now(datetime.timezone.utc).isoformat()

        # Initialize isolated run record
        result_store.create_run(run_id=run_id, request=request, created_at=created_at)

        # Get cancellation token
        token = cancellation_manager.get_token(run_id)

        # Launch background execution
        if background_tasks:
            background_tasks.add_task(self.orchestrator.execute_run, run_id, request, token)
        else:
            task = asyncio.create_task(
                self.orchestrator.execute_run(run_id, request, token)
            )
            self._tasks[run_id] = task

        return RunResponse(
            run_id=run_id,
            status="queued",
            mode=request.mode,
            created_at=created_at,
            message="Run queued and orchestrator initiated",
        )

    def cancel_run(self, run_id: str) -> bool:
        record = result_store.get_run(run_id)
        if not record:
            return False

        cancellation_manager.cancel(run_id)
        task = self._tasks.get(run_id)
        if task and not task.done():
            task.cancel()

        result_store.set_status(run_id, "cancelled")
        return True

run_manager = RunManager()
