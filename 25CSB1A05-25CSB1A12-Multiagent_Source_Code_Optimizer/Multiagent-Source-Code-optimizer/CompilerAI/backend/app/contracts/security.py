from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from app.contracts.common import InferenceMode, SourceKind

class SecurityFinding(BaseModel):
    id: str
    title: str
    severity: str  # "critical" | "high" | "medium" | "low" | "info"
    description: str
    line_number: Optional[int] = None
    rule_or_cwe: Optional[str] = None
    remediation: Optional[str] = None

class SecurityRequest(BaseModel):
    run_id: str
    source_code: str
    language: str
    source_kind: SourceKind  # "original" | "optimized"
    inference_mode: InferenceMode
    options: Dict[str, Any] = Field(default_factory=dict)

class SecurityResult(BaseModel):
    run_id: str
    status: str  # "completed" | "failed"
    source_kind: SourceKind
    findings: List[SecurityFinding] = Field(default_factory=list)
    raw_result: Dict[str, Any] = Field(default_factory=dict)
    diagnostics: List[str] = Field(default_factory=list)
    duration_ms: int = 0
    is_demo: bool = True
