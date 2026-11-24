from enum import Enum

class RunMode(str, Enum):
    PIPELINE = "pipeline"
    OPTIMIZE = "optimize"
    SECURITY = "security"

class InferenceMode(str, Enum):
    LLM = "llm"
    HEURISTICS = "heuristics"

class StageStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"

class RunStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    PARTIALLY_COMPLETED = "partially_completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class SourceKind(str, Enum):
    ORIGINAL = "original"
    OPTIMIZED = "optimized"
