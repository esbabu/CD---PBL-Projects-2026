"""Exception locator: maps tracebacks to decision frames, origin frames, and defect classes."""
from __future__ import annotations

import os
import traceback
from typing import Any
from pydantic import BaseModel


class LocatedException(BaseModel):
    decision_frame: str
    origin_frame: str
    defect_class: str
    evidence: str
    exc_type: str
    exc_message: str


KNOWN_DEFECT_CLASSES = [
    ("AmbiguousEntry", "ENTRY_SELECTION"),
    ("no seed inputs", "SEEDS"),
    ("ZeroDivisionError", "ORIGINAL_NEEDS_STATE"),
    ("no such table", "DEGENERATE_GOLDEN"),
    ("OperationalError", "DEGENERATE_GOLDEN"),
    ("load_error", "IMPORT_FAILURE"),
    ("FileNotFoundError", "MISSING_FIXTURE_RESOURCE"),
    ("SyntaxError", "SYNTAX_ERROR"),
    ("IndentationError", "SYNTAX_ERROR"),
    ("TabError", "SYNTAX_ERROR"),
    ("PermissionError", "EFFECT_POLICY_VIOLATION"),
    ("TimeoutError", "EXEC_TIMEOUT"),
]


class ExceptionLocator:
    """Pinpoints where an error originated and which component gave up."""

    @classmethod
    def locate(cls, exc: BaseException, tb: Any = None) -> LocatedException:
        if tb is None:
            tb = exc.__traceback__

        extracted = traceback.extract_tb(tb)
        exc_type = type(exc).__name__
        exc_msg = str(exc)

        if not extracted:
            return LocatedException(
                decision_frame="unknown:0 <unknown>",
                origin_frame="unknown:0 <unknown>",
                defect_class="UNKNOWN",
                evidence=f"{exc_type}: {exc_msg}",
                exc_type=exc_type,
                exc_message=exc_msg,
            )

        # origin_frame: innermost frame
        origin = extracted[-1]
        origin_frame = f"{os.path.basename(origin.filename)}:{origin.lineno} {origin.name}"

        # decision_frame: outermost frame inside optagent
        decision = extracted[0]
        for f in extracted:
            if "optagent" in f.filename.replace("\\", "/"):
                decision = f
                break
        decision_frame = f"{os.path.basename(decision.filename)}:{decision.lineno} {decision.name}"

        # Classify defect
        full_text = f"{exc_type} {exc_msg} {origin_frame} {decision_frame}"
        defect_class = "PIPELINE_ERROR"
        for pattern, d_class in KNOWN_DEFECT_CLASSES:
            if pattern.lower() in full_text.lower():
                defect_class = d_class
                break

        evidence = f"{exc_type} at {origin_frame} (handled/stopped at {decision_frame}): {exc_msg}"
        return LocatedException(
            decision_frame=decision_frame,
            origin_frame=origin_frame,
            defect_class=defect_class,
            evidence=evidence,
            exc_type=exc_type,
            exc_message=exc_msg,
        )
