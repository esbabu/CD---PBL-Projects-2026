from __future__ import annotations
import json

from ..runtime.sandbox import RunOpts, Sandbox
from .schemas import Case, GoldenRecord

FIELDS = ("status", "ret", "exc_type", "stdout", "mut", "glob")


def lines_of(edges) -> set[int]:
    out = set()
    for e in edges:
        _, _, b = e.partition(">")
        if b.lstrip("-").isdigit() and int(b) > 0:
            out.add(int(b))
    return out


def make_golden(sb: Sandbox, src, entry: str, cases: list[Case], *, cov: bool = False,
                props_path: str | None = None):
    """Run the ORIGINAL under two hash seeds. Returns (golden, dropped, lines_per_case)."""
    r0 = sb.run(src, entry, cases, RunOpts(hashseed=0, cov=cov, props_path=props_path))
    keep = [i for i, r in enumerate(r0) if r.status in ("ok", "exception")]
    r1s = sb.run(src, entry, [cases[i] for i in keep], RunOpts(hashseed=1, props_path=props_path)) if keep else []
    alt = dict(zip(keep, r1s))
    golden: dict[str, GoldenRecord] = {}
    dropped: list[tuple[Case, str, str | None]] = []
    lines: dict[str, set[int]] = {}
    for i, (c, r) in enumerate(zip(cases, r0)):
        if i not in alt:
            dropped.append((c, r.status, r.exc_msg))
            continue
        a = alt[i]
        unstable = [f for f in FIELDS
                    if json.dumps(getattr(r, f), sort_keys=True) != json.dumps(getattr(a, f), sort_keys=True)]
        lines[c.id] = lines_of(r.edges)
        r.edges, a.edges = [], []
        golden[c.id] = GoldenRecord(case_id=c.id, result=r, unstable=unstable,
                                    alt=a if "ret" in unstable else None)
    return golden, dropped, lines