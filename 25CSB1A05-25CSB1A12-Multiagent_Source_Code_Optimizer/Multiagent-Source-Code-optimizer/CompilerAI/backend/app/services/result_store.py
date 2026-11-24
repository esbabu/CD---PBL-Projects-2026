import datetime
from typing import Dict, Optional, Any
from app.contracts.optimization import OptimizationResult
from app.contracts.security import SecurityResult
from app.contracts.requests import CreateRunRequest

TERMINAL_STATUSES = {"completed", "partially_completed", "failed", "cancelled"}

class RunRecord:
    def __init__(self, run_id: str, request: CreateRunRequest, status: str = "queued"):
        self.run_id = run_id
        self.request = request
        self.status = status  # queued, running, completed, partially_completed, failed, cancelled
        self.optimization_result: Optional[OptimizationResult] = None
        self.security_result: Optional[SecurityResult] = None
        self.failure_reason: Optional[str] = None
        self.created_at: str = ""
        self.completed_at: Optional[str] = None

class ResultStore:
    """
    Maintains isolated per-run storage.
    Guarantees runs never overwrite or leak results across run IDs.
    """

    def __init__(self):
        self._runs: Dict[str, RunRecord] = {}

    def create_run(self, run_id: str, request: CreateRunRequest, created_at: str) -> RunRecord:
        record = RunRecord(run_id=run_id, request=request, status="queued")
        record.created_at = created_at
        self._runs[run_id] = record
        return record

    def get_run(self, run_id: str) -> Optional[RunRecord]:
        return self._runs.get(run_id)

    def set_status(self, run_id: str, status: str, failure_reason: Optional[str] = None) -> None:
        if run_id in self._runs:
            self._runs[run_id].status = status
            if failure_reason:
                self._runs[run_id].failure_reason = failure_reason
            if status in TERMINAL_STATUSES:
                self._runs[run_id].completed_at = datetime.datetime.now(datetime.timezone.utc).isoformat()

    def set_optimization_result(self, run_id: str, result: OptimizationResult) -> None:
        if run_id in self._runs:
            self._runs[run_id].optimization_result = result

    def set_security_result(self, run_id: str, result: SecurityResult) -> None:
        if run_id in self._runs:
            self._runs[run_id].security_result = result

    def get_results(self, run_id: str) -> Dict[str, Any]:
        record = self.get_run(run_id)
        if not record:
            return {}
        return {
            "run_id": record.run_id,
            "status": record.status,
            "mode": record.request.mode.value,
            "optimization_result": record.optimization_result.model_dump() if record.optimization_result else None,
            "security_result": record.security_result.model_dump() if record.security_result else None,
            "failure_reason": record.failure_reason,
            "created_at": record.created_at,
            "completed_at": record.completed_at,
        }

result_store = ResultStore()
