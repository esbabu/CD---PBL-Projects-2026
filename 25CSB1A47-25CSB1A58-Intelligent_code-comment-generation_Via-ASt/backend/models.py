"""Response structures and serialization."""

from typing import TypedDict


class Warning(TypedDict):
    rule_id: str
    severity: str
    message: str
    line: int
