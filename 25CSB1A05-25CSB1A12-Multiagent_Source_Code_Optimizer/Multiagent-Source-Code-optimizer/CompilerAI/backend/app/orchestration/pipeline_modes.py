from enum import Enum
from typing import List

class PipelineMode(str, Enum):
    PIPELINE = "pipeline"
    OPTIMIZE = "optimize"
    SECURITY = "security"

def get_stages_for_mode(mode: str) -> List[str]:
    if mode == PipelineMode.PIPELINE or mode == "pipeline":
        return ["optimization", "security"]
    elif mode == PipelineMode.OPTIMIZE or mode == "optimize":
        return ["optimization"]
    elif mode == PipelineMode.SECURITY or mode == "security":
        return ["security"]
    else:
        raise ValueError(f"Unknown pipeline mode: {mode}")
