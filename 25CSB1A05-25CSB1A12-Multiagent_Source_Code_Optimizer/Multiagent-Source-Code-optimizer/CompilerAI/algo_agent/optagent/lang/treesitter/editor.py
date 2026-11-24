"""Byte-range source editor backed by tree-sitter byte offsets."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ByteEdit:
    start_byte: int
    end_byte: int
    replacement: bytes


class SourceEditor:
    """Applies non-overlapping byte-range replacements cleanly to UTF-8 source."""

    def __init__(self, source: str):
        self.source = source
        self.src_bytes = source.encode("utf-8")
        self._edits: list[ByteEdit] = []

    def replace(self, start_byte: int, end_byte: int, text: str) -> "SourceEditor":
        if start_byte < 0 or end_byte < start_byte or end_byte > len(self.src_bytes):
            raise ValueError(f"Invalid byte range [{start_byte}, {end_byte}] for buffer of len {len(self.src_bytes)}")
        self._edits.append(ByteEdit(start_byte, end_byte, text.encode("utf-8")))
        return self

    def insert(self, offset: int, text: str) -> "SourceEditor":
        return self.replace(offset, offset, text)

    def delete(self, start_byte: int, end_byte: int) -> "SourceEditor":
        return self.replace(start_byte, end_byte, "")

    def apply(self) -> str:
        if not self._edits:
            return self.source
        ordered = sorted(self._edits, key=lambda e: (e.start_byte, e.end_byte))
        # Validate no overlapping ranges
        for prev, cur in zip(ordered, ordered[1:]):
            if cur.start_byte < prev.end_byte:
                raise ValueError(
                    f"Overlapping edits: [{prev.start_byte}, {prev.end_byte}) vs [{cur.start_byte}, {cur.end_byte})"
                )
        buf = bytearray(self.src_bytes)
        for edit in reversed(ordered):
            buf[edit.start_byte:edit.end_byte] = edit.replacement
        return buf.decode("utf-8")
