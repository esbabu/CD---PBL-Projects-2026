"""
Verified-fix memory
====================
An append-only JSON-lines file of fixes the agent's verifier *accepted*. Each
record keeps the rule, the strategy, the function before and after the patch and
a SHA-256 digest over those fields.

Safety rules, enforced on write and on read:

* only patches with ``accepted`` verification are written (the agent calls
  :func:`remember` after the four checks pass), so an unverified or rejected
  patch can never become retrievable guidance;
* both code fields must parse as Python and are capped in size;
* string literals that look like credentials are masked before storage;
* a record whose digest does not match its content (edited or corrupted by
  hand) is skipped when the memory is loaded.

Location: ``$CCG_FIX_MEMORY`` or ``outputs/rag/fix_memory.jsonl``.
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
import re
from typing import Dict, List, Optional

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
MAX_CODE = 4000
_FIELDS = ("rule_id", "strategy", "function", "before", "after")
_CRED = re.compile(r"""(?i)((?:pass(?:word|wd)?|secret|token|api_?key|private_?key)\s*[=:]\s*)(["'])[^"']{4,}\2""")


def memory_path() -> str:
    return os.environ.get("CCG_FIX_MEMORY", os.path.join(ROOT, "outputs", "rag", "fix_memory.jsonl"))


def _digest(record: Dict[str, str]) -> str:
    h = hashlib.sha256()
    for f in _FIELDS:
        h.update(f.encode())
        h.update(b"\0")
        h.update(str(record.get(f, "")).encode("utf-8"))
        h.update(b"\0")
    return h.hexdigest()


def _clean(code: str) -> Optional[str]:
    code = code.strip("\n")
    if not code or len(code) > MAX_CODE:
        return None
    try:
        ast.parse(code)
    except SyntaxError:
        return None
    return _CRED.sub(lambda m: f"{m.group(1)}{m.group(2)}****{m.group(2)}", code)


def remember(rule_id: str, strategy: str, function: str, before: str, after: str,
             path: Optional[str] = None) -> bool:
    """Store one verified fix. Returns False when the record is rejected or already stored."""
    b, a = _clean(before), _clean(after)
    if b is None or a is None or a == b:
        return False
    record = {"rule_id": rule_id, "strategy": strategy, "function": function, "before": b, "after": a}
    record["sha256"] = _digest(record)
    path = path or memory_path()
    if any(r["sha256"] == record["sha256"] for r in load(path)):
        return False
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    return True


def load(path: Optional[str] = None) -> List[Dict[str, str]]:
    """Records whose digest checks out; anything malformed or tampered with is skipped."""
    path = path or memory_path()
    if not os.path.isfile(path):
        return []
    out = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            try:
                rec = json.loads(line)
            except ValueError:
                continue
            if not isinstance(rec, dict) or rec.get("sha256") != _digest(rec):
                continue
            if _clean(rec.get("before", "")) is None or _clean(rec.get("after", "")) is None:
                continue
            out.append(rec)
    return out
