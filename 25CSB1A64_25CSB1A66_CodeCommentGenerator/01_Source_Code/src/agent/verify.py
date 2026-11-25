"""
Patch verification
===================
A proposed patch is accepted only if the compiler's own analysis agrees:

  a) parses         the patched source is valid Python (``ast.parse``)
  b) finding gone   re-running ``analyze_source`` reports fewer findings of the
                    same rule in the same function (rule + function, not line
                    numbers, because a patch shifts lines)
  c) nothing new    no (rule, function) pair is reported more often than before
  d) in scope       every changed line lies inside the reported function; the
                    only change allowed elsewhere is a new top-level import
"""
from __future__ import annotations

import ast
import difflib
from collections import Counter
from dataclasses import dataclass, field
from typing import List, Optional

from ..security.analyzer import analyze_source
from .source import allowed_lines


@dataclass
class Check:
    name: str
    ok: bool
    detail: str = ""


@dataclass
class Verification:
    ok: bool
    checks: List[Check] = field(default_factory=list)
    report: object = None              # SecurityFindings of the patched source

    def summary(self) -> str:
        return ", ".join(f"{c.name} {'✓' if c.ok else '✗'}" for c in self.checks)


def finding_counts(report) -> Counter:  # noqa: D401 (unchanged)
    return Counter((f.rule_id, f.function) for f in report.active())


def _is_import(line: str) -> bool:
    try:
        body = ast.parse(line.strip()).body
    except SyntaxError:
        return False
    return len(body) == 1 and isinstance(body[0], (ast.Import, ast.ImportFrom))


def changed_outside(original: str, patched: str, allowed: set) -> List[int]:
    """Original line numbers changed outside ``allowed`` (new import lines are fine)."""
    a, b = original.splitlines(), patched.splitlines()
    bad = []
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if tag == "equal":
            continue
        if tag == "insert":
            # lines inserted after original line i1: inside if they sit between two lines of
            # the function, or directly after its last line and indented (still its body)
            indented = all(not l.strip() or l[:1].isspace() for l in b[j1:j2])
            inside = i1 in allowed and (i1 + 1 in allowed or indented)
            if not inside and not all(_is_import(l) for l in b[j1:j2]):
                bad.append(i1 + 1)
            continue
        bad.extend(n for n in range(i1 + 1, i2 + 1) if n not in allowed)
    return bad


def verify_patch(original: str, patched: Optional[str], finding, before_report,
                 filepath: str = "<string>") -> Verification:
    checks: List[Check] = []
    try:
        ast.parse(patched)
        checks.append(Check("parses", True))
    except SyntaxError as exc:
        checks.append(Check("parses", False, f"SyntaxError: {exc.msg} (line {exc.lineno})"))
        return Verification(False, checks)

    after = analyze_source(patched, filepath)
    before_n, after_n = finding_counts(before_report), finding_counts(after)
    key = (finding.rule_id, finding.function)
    gone = after_n[key] < before_n[key]
    checks.append(Check("finding gone", gone,
                        "" if gone else f"{finding.rule_id} still reported in {finding.function}()"))

    new = sorted(k for k in after_n if after_n[k] > before_n[k])
    checks.append(Check("no new findings", not new,
                        "" if not new else "new: " + ", ".join(f"{r} in {fn}()" for r, fn in new)))

    original_tree = ast.parse(original)
    allowed = allowed_lines(original_tree, finding.function, len(original.splitlines()))
    outside = changed_outside(original, patched, allowed)
    checks.append(Check("only the reported function changed", not outside,
                        "" if not outside else f"lines changed outside: {outside[:5]}"))
    return Verification(all(c.ok for c in checks), checks, after)


def unified_diff(original: str, patched: str, name: str = "code") -> str:
    return "".join(difflib.unified_diff(original.splitlines(keepends=True),
                                        patched.splitlines(keepends=True),
                                        fromfile=f"{name} (original)", tofile=f"{name} (patched)"))
