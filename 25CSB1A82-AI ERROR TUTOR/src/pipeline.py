"""
Main Pipeline - End-to-end error explanation system (Agentic Version)
"""

from typing import Optional
from dataclasses import dataclass
from .orchestrator import Orchestrator

@dataclass
class ExplanationResult:
    success: bool
    error_type: Optional[str]
    raw_error: Optional[str]
    friendly_explanation: Optional[str]
    suggested_fix: Optional[str]
    code_context: Optional[str]
    line_number: Optional[int]
    similar_names: list
    security_warnings: list


class AIErrorTutor:
    def __init__(self, model_path: Optional[str] = "./models/error_tutor_model", use_ai: bool = True):
        self.use_ai = use_ai
        self.model = None
        
        # We are using the fallback, so skip AI model loading
        if use_ai:
            try:
                # Uncomment these lines if you install torch later:
                # from .model import ErrorExplainerModel
                # self.model = ErrorExplainerModel(model_path=model_path)
                self.use_ai = False # Force fallback for now
            except Exception as e:
                print(f"⚠️ AI model not available: {e}")
                self.use_ai = False

        self.orchestrator = Orchestrator(ai_model=self.model if self.use_ai else None)

    def analyze_code(self, code: str) -> ExplanationResult:
        result_dict = self.orchestrator.run(code)
        
        return ExplanationResult(
            success=result_dict.get("success", False),
            error_type=result_dict.get("error_type"),
            raw_error=result_dict.get("raw_error"),
            friendly_explanation=result_dict.get("friendly_explanation"),
            suggested_fix=result_dict.get("suggested_fix"),
            code_context=result_dict.get("code_context"),
            line_number=result_dict.get("line_number"),
            similar_names=result_dict.get("similar_names", []),
            security_warnings=result_dict.get("security_warnings", [])
        )
