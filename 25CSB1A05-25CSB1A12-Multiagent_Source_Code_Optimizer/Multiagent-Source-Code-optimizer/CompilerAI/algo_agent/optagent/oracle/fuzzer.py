from __future__ import annotations
import random
import time
from collections import Counter
from dataclasses import dataclass, field

from ..config import Settings
from ..runtime.sandbox import RunOpts, Sandbox
from .golden import lines_of
from .mutators import MutCtx, mutate_args
from .schemas import Case, CaseResult


@dataclass
class FuzzResult:
    new_cases: list[Case] = field(default_factory=list)
    edges: set[str] = field(default_factory=set)
    rounds: int = 0
    stop_reason: str = ""

    @property
    def lines(self) -> set[int]:
        return lines_of(e for e in self.edges if ">" in e)


def _pseudo(r: CaseResult) -> set[str]:
    """Extra novelty signals: exception types and return types count as 'coverage' too."""
    s = set(r.edges)
    if r.status == "exception":
        s.add(f"X:{r.exc_type}")
    else:
        s.add(f"T:{r.return_type}")
        if r.return_type == "NoneType":
            s.add("N:none")
    return s


class CoverageFuzzer:
    """AFL-style loop: mutate inputs that reach rare edges, keep the ones that reach new ones."""

    def __init__(self, sb: Sandbox, s: Settings, src, entry: str, ctx: MutCtx,
                 rng: random.Random, props_path: str | None = None, log=print):
        self.sb, self.s, self.src, self.entry = sb, s, src, entry
        self.ctx, self.rng, self.props, self.log = ctx, rng, props_path, log

    def run(self, seeds: list[Case], budget_s: float) -> FuzzResult:
        s, rng = self.s, self.rng
        t0 = time.time()
        res = FuzzResult()
        seen = {c.id for c in seeds}
        out = self.sb.run(self.src, self.entry, seeds, RunOpts(cov=True, props_path=self.props))
        queue: list[tuple[Case, set[str]]] = []
        hits: Counter = Counter()
        for c, r in zip(seeds, out):
            if r.status in ("ok", "exception"):
                e = _pseudo(r)
                queue.append((c, e))
                hits.update(e)
                res.edges |= e
        stale = 0
        for rnd in range(s.fuzz_max_rounds):
            if time.time() - t0 > budget_s:
                res.stop_reason = "time budget"
                break
            if stale >= s.fuzz_patience:
                res.stop_reason = f"no new coverage for {stale} rounds"
                break
            if not queue:
                res.stop_reason = "empty queue"
                break
            weights = [sum(1.0 / hits[e] for e in es) + 0.1 for _, es in queue]
            parents = rng.choices(queue, weights=weights, k=s.fuzz_batch)
            others = [q[0].py() for q in rng.sample(queue, min(20, len(queue)))]
            kids: list[Case] = []
            for pc, _ in parents:
                a, k = pc.py()
                a2, k2 = mutate_args(a, k, rng, self.ctx, others=others)
                c = Case.make(a2, k2, "fuzz", "coverage_guided")
                if c.id in seen or c.size > 30000:
                    continue
                seen.add(c.id)
                kids.append(c)
            res.rounds = rnd + 1
            if not kids:
                stale += 1
                continue
            found = 0
            for c, r in zip(kids, self.sb.run(self.src, self.entry, kids,
                                               RunOpts(cov=True, props_path=self.props))):
                if r.status not in ("ok", "exception"):
                    continue
                e = _pseudo(r)
                hits.update(e)
                if e - res.edges:
                    res.edges |= e
                    queue.append((c, e))
                    res.new_cases.append(c)
                    found += 1
            stale = 0 if found else stale + 1
            self.log(f"  fuzz round {rnd + 1}: +{found} interesting, {len(res.edges)} edges total")
        res.stop_reason = res.stop_reason or "max rounds"
        return res