"""FastAPI service wrapper for OptAgent."""
from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any, AsyncGenerator

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from ..agent import OptimizerAgent, OptimizeRequest, OptimizeResult
from ..config import Settings
from ..oracle.oracle import source_sha
from ..report.schemas import Report

app = FastAPI(
    title="OptAgent Algorithm Optimization Service",
    description="REST and SSE API for optimizing Python algorithms with formal/differential verification.",
    version="1.0.0",
)

# In-memory progress event queues keyed by run SHA
_EVENT_QUEUES: dict[str, list[dict[str, Any]]] = {}


class OverrideRequest(BaseModel):
    overrides: dict[str, Any]


@app.get("/languages")
def list_languages_endpoint() -> dict[str, Any]:
    """Return supported languages, capabilities, contract aspects, and security profiles for UI integration."""
    from ..lang.pipeline_hooks import list_language_metadata
    return {"languages": list_language_metadata()}


@app.post("/optimize", response_model=OptimizeResult)
def optimize_endpoint(req: OptimizeRequest) -> OptimizeResult:
    """Run full optimization pipeline on provided source code."""
    sha = source_sha(req.source, req.language or "python")
    _EVENT_QUEUES[sha] = []

    def on_progress(stage: str, msg: str, pct: float):
        event_data = {"stage": stage, "message": msg, "progress": pct}
        if sha in _EVENT_QUEUES:
            _EVENT_QUEUES[sha].append(event_data)

    agent = OptimizerAgent(Settings())
    return agent.run(req, progress_callback=on_progress)


@app.get("/runs/{sha}")
def get_run_report(sha: str) -> dict[str, Any]:
    """Retrieve the generated Report and artifact paths for a given source SHA."""
    settings = Settings()
    run_dir = Path(settings.runs_dir) / sha
    report_file = run_dir / "report.json"
    if not report_file.exists():
        raise HTTPException(status_code=404, detail=f"No report found for SHA {sha}")

    report_data = json.loads(report_file.read_text(encoding="utf-8"))
    return {
        "source_sha": sha,
        "report": report_data,
        "report_markdown": (run_dir / "report.md").read_text(encoding="utf-8") if (run_dir / "report.md").exists() else "",
    }


@app.get("/runs/{sha}/events")
async def get_run_events(sha: str, request: Request) -> EventSourceResponse:
    """Stream SSE progress events for an optimization run."""
    async def event_generator() -> AsyncGenerator[dict[str, Any], None]:
        sent = 0
        while True:
            if await request.is_disconnected():
                break

            events = _EVENT_QUEUES.get(sha, [])
            while sent < len(events):
                yield {"event": "progress", "data": json.dumps(events[sent])}
                sent += 1

            if events and events[-1].get("stage") == "complete":
                yield {"event": "done", "data": json.dumps({"status": "complete"})}
                break

            await asyncio.sleep(0.5)

    return EventSourceResponse(event_generator())


@app.post("/runs/{sha}/override", response_model=OptimizeResult)
def override_contract_endpoint(sha: str, req: OverrideRequest) -> OptimizeResult:
    """Rebuild and re-optimize a function with modified contract or inputs."""
    settings = Settings()
    run_dir = Path(settings.runs_dir) / sha
    intent_file = run_dir / "intent.json"
    if not intent_file.exists():
        raise HTTPException(status_code=404, detail=f"No run found for SHA {sha}")

    intent_data = json.loads(intent_file.read_text(encoding="utf-8"))
    source = intent_data["source"]
    entry = intent_data.get("entry_point")

    # Combine existing overrides with new overrides
    opt_req = OptimizeRequest(
        source=source,
        entry=entry,
        overrides=req.overrides,
        use_llm=False,
    )

    agent = OptimizerAgent(settings)
    return agent.run(opt_req)

