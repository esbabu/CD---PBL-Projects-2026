import asyncio
import json
from fastapi import APIRouter, HTTPException
from sse_starlette.sse import EventSourceResponse
from app.services.event_bus import event_bus
from app.services.result_store import result_store

router = APIRouter(tags=["Events"])

TERMINAL_STATUSES = {"completed", "partially_completed", "failed", "cancelled"}

@router.get("/runs/{run_id}/events")
async def stream_run_events(run_id: str):
    record = result_store.get_run(run_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found")

    async def event_generator():
        queue = await event_bus.subscribe(run_id)
        try:
            while True:
                # Wait for next event with a periodic heartbeat
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=15.0)
                    yield {
                        "event": "message",
                        "data": event.model_dump_json(),
                    }

                    # If this is a terminal run event, close the stream cleanly
                    if event.type in {"run_completed", "run_partially_completed", "run_cancelled"}:
                        break

                except asyncio.TimeoutError:
                    # Send keep-alive heartbeat comment to keep SSE connection alive
                    yield {
                        "event": "heartbeat",
                        "data": json.dumps({"type": "heartbeat", "run_id": run_id}),
                    }
                    # Also check if run already finished
                    curr_record = result_store.get_run(run_id)
                    if curr_record and curr_record.status in TERMINAL_STATUSES:
                        break

        finally:
            await event_bus.unsubscribe(run_id, queue)

    return EventSourceResponse(event_generator())
