from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

class RunEvent(BaseModel):
    run_id: str
    seq: int
    type: str  # run_started, agent_started, agent_progress, agent_log, agent_artifact, agent_completed, agent_failed, agent_cancelled, warning, error, run_completed, run_partially_completed, run_cancelled
    agent: Optional[str] = None  # "optimization" | "security" | None
    stage: Optional[str] = None  # "optimization" | "security" | None
    status: Optional[str] = None
    timestamp: str
    message: str
    data: Dict[str, Any] = Field(default_factory=dict)
