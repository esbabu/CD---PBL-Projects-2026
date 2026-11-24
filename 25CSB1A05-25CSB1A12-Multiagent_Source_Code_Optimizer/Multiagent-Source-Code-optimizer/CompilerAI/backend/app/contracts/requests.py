from pydantic import BaseModel, Field
from typing import Dict, Any
from app.contracts.common import RunMode, InferenceMode

class CreateRunRequest(BaseModel):
    mode: RunMode = Field(..., description="Execution mode: pipeline, optimize, or security")
    language: str = Field(default="cpp", description="Source code language (e.g. cpp, c, rust, python)")
    source_code: str = Field(..., min_length=1, description="Source code to process")
    inference_mode: InferenceMode = Field(default=InferenceMode.LLM, description="Selected inference strategy")
    options: Dict[str, Any] = Field(default_factory=dict, description="Execution options (e.g. mock_failure for testing)")

class RunResponse(BaseModel):
    run_id: str
    status: str
    mode: RunMode
    created_at: str
    message: str
