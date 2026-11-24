from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.contracts.requests import CreateRunRequest, RunResponse
from app.orchestration.run_manager import run_manager
from app.services.result_store import result_store

router = APIRouter(tags=["Runs"])

@router.post("/runs", response_model=RunResponse, status_code=202)
async def create_run(request: CreateRunRequest, background_tasks: BackgroundTasks):
    return run_manager.start_run(request, background_tasks)

@router.get("/runs/{run_id}")
async def get_run_status(run_id: str):
    record = result_store.get_run(run_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found")
    return {
        "run_id": record.run_id,
        "status": record.status,
        "mode": record.request.mode.value,
        "failure_reason": record.failure_reason,
        "created_at": record.created_at,
    }

@router.get("/runs/{run_id}/results")
async def get_run_results(run_id: str):
    record = result_store.get_run(run_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found")
    return result_store.get_results(run_id)

@router.post("/runs/{run_id}/cancel")
async def cancel_run(run_id: str):
    success = run_manager.cancel_run(run_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found or already terminated")
    return {"run_id": run_id, "status": "cancelled", "message": "Run cancelled"}
