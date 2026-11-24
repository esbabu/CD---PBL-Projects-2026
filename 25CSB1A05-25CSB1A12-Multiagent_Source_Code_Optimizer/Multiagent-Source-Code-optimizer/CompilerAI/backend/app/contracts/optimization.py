from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from app.contracts.common import InferenceMode

class OptimizationRequest(BaseModel):
    run_id: str
    source_code: str
    language: str
    inference_mode: InferenceMode
    options: Dict[str, Any] = Field(default_factory=dict)

class OptimizationResult(BaseModel):
    run_id: str
    status: str  # "completed" | "failed" | "not_performed"
    optimized_code: Optional[str] = None
    transformations: List[str] = Field(default_factory=list)
    metrics: Dict[str, Any] = Field(default_factory=dict)
    raw_result: Dict[str, Any] = Field(default_factory=dict)
    diagnostics: List[str] = Field(default_factory=list)
    duration_ms: int = 0
    is_demo: bool = True
