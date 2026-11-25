"""
Fix-and-verify agent
=====================
A small plan → act → observe → decide loop over the analyzer's findings:

  for each active finding (one at a time, re-analysing after every accepted patch):
    plan     pick the next fix strategy for the finding's rule
    act      produce a patched copy of the source (the input is never modified)
    observe  verify the patch with the analyzer (``verify.verify_patch``)
    decide   accept it, or try the next strategy; after ``max_attempts``
             strategies the finding is marked "needs manual fix"

Every step is recorded as an :class:`AgentStep`, so a run can be shown as a trace
(CLI, JSON or the GUI's Auto-fix panel).
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Callable, Dict, List, Optional, Sequence

from ..security.analyzer import analyze_source
from .strategies import STRATEGIES, FixContext, Patch, Strategy, strategies_for
from .verify import unified_diff, verify_patch

FIXED = "fixed"
MANUAL = "needs manual fix"


@dataclass
class AgentStep:
    phase: str                          # finding | plan | act | observe | decide | done
    message: str
    finding: int = 0                    # 1-based index of the finding being worked on
    data: Dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)

    def format(self) -> str:
        return f"[{self.phase:<7}] {self.message}"


@dataclass
class Attempt:
    strategy: str
    result: str                         # not applicable | rejected | accepted | error
    detail: str = ""
    checks: List[Dict] = field(default_factory=list)


@dataclass
class FindingOutcome:
    rule_id: str
    title: str
    function: str
    line: int                           # line in the original source the finding was reported on
    status: str                         # fixed | needs manual fix
    strategy: str = ""
    reason: str = ""
    attempts: List[Attempt] = field(default_factory=list)
    guidance: List[Dict] = field(default_factory=list)   # RAG passages for a manual fix

    @property
    def rejected(self) -> int:
        return sum(a.result == "rejected" for a in self.attempts)


@dataclass
class FixResult:
    filepath: str
    original: str
    patched: str
    outcomes: List[FindingOutcome] = field(default_factory=list)
    steps: List[AgentStep] = field(default_factory=list)
    findings_before: int = 0
    findings_after: int = 0
    parse_error: Optional[str] = None

    @property
    def changed(self) -> bool:
        return self.patched != self.original

    def diff(self) -> str:
        return unified_diff(self.original, self.patched, self.filepath)

    def counts(self) -> Dict[str, int]:
        return {"findings": len(self.outcomes),
                "fixed": sum(o.status == FIXED for o in self.outcomes),
                "needs_manual_fix": sum(o.status == MANUAL for o in self.outcomes),
                "rejected_patches": sum(o.rejected for o in self.outcomes)}

    def to_dict(self) -> dict:
        return {"file": self.filepath, "parse_error": self.parse_error,
                "findings_before": self.findings_before, "findings_after": self.findings_after,
                "summary": self.counts(),
                "outcomes": [asdict(o) for o in self.outcomes],
                "steps": [s.to_dict() for s in self.steps],
                "diff": self.diff()}


def _signature(finding, source: str) -> tuple:
    """Identifies a finding across patches (line numbers shift, the sink's code does not)."""
    lines = source.splitlines()
    code = lines[finding.line - 1].strip() if 0 < finding.line <= len(lines) else ""
    return finding.rule_id, finding.function, code


def _function_code(source: str, qualname: str, line: int) -> str:
    """Source of the function ``qualname`` (or a few lines around ``line`` at module level)."""
    import ast
    from .source import function_node
    lines = source.splitlines()
    try:
        node = function_node(ast.parse(source), qualname)
    except SyntaxError:
        node = None
    if node is not None:
        return "\n".join(lines[node.lineno - 1:node.end_lineno])
    lo, hi = max(0, line - 3), min(len(lines), line + 2)
    return "\n".join(lines[lo:hi])


def fix_source(source: str, filepath: str = "<string>", max_attempts: int = 3, use_llm: bool = False,
               strategies: Sequence[Strategy] = STRATEGIES,
               on_step: Optional[Callable[[AgentStep], None]] = None,
               learn: bool = False, memory_path: Optional[str] = None,
               guidance: bool = True) -> FixResult:
    """Run the agent on ``source`` and return the patched copy with the full trace.

    learn        store every verified fix in the RAG fix memory (``src.rag.memory``)
    guidance     attach retrieved guidance (``src.rag``) to findings left for a manual fix
    """
    result = FixResult(filepath, source, source)
    llm = None
    if use_llm:
        from .llm_strategy import LLM_STRATEGY
        llm = LLM_STRATEGY

    def log(phase: str, message: str, index: int = 0, **data):
        step = AgentStep(phase, message, index, data)
        result.steps.append(step)
        if on_step:
            on_step(step)

    report = analyze_source(source, filepath)
    if report.parse_error:
        result.parse_error = report.parse_error
        log("done", f"Cannot analyse the code: {report.parse_error}")
        return result
    result.findings_before = len(report.active())
    log("observe", f"Analyzer reports {result.findings_before} active finding(s)")

    # earlier patches shift lines; report every finding at its line in the original source
    original_line = {_signature(f, source): f.line for f in report.active()}
    current, done = source, set()
    for _ in range(4 * result.findings_before + 4):          # hard stop; each pass settles one finding
        pending = [f for f in sorted(report.active(), key=lambda f: (f.line, f.col))
                   if _signature(f, current) not in done]
        if not pending:
            break
        f = pending[0]
        sig = _signature(f, current)
        done.add(sig)
        line = original_line.get(sig, f.line)
        idx = len(result.outcomes) + 1
        outcome = FindingOutcome(f.rule_id, f.title, f.function, line, MANUAL)
        result.outcomes.append(outcome)
        log("finding", f"#{idx} {f.rule_id} {f.title} in {f.function}() at line {line} "
                       f"({f.status}, {f.confidence} confidence)", idx,
            rule_id=f.rule_id, function=f.function, line=line)

        plan = list(strategies_for(f.rule_id, strategies))
        if llm is not None and llm.available():               # no local model: skipped quietly
            plan.append(llm)
        if not plan:
            outcome.reason = f"no automatic fix for {f.rule_id}; {f.remediation}"
            log("decide", f"No strategy for {f.rule_id} → needs manual fix", idx)
            if guidance:
                _attach_guidance(outcome, f, current, memory_path, log, idx)
            continue

        tried = 0
        for strat in plan:
            if tried >= max_attempts:
                break
            tried += 1
            log("plan", f"Attempt {tried}/{max_attempts}: {strat.name} — {strat.description}", idx,
                strategy=strat.name)
            try:
                from .. import perf
                with perf.block("agent.strategy"):
                    patch = strat.apply(FixContext.build(current, f))
            except Exception as exc:                         # a strategy bug must not stop the run
                patch = Patch(None, f"error: {type(exc).__name__}: {exc}")
            if patch.patched is None:
                result_kind = "error" if patch.note.startswith("error:") else "not applicable"
                outcome.attempts.append(Attempt(strat.name, result_kind, patch.note))
                log("act", f"{strat.name} does not apply: {patch.note}", idx, strategy=strat.name)
                continue
            log("act", f"{strat.name} produced a patch ({patch.note})", idx, strategy=strat.name)
            from .. import perf
            with perf.block("agent.verify_patch"):
                check = verify_patch(current, patch.patched, f, report, filepath)
            checks = [asdict(c) for c in check.checks]
            log("observe", "Verification: " + check.summary() +
                "".join(f"; {c.detail}" for c in check.checks if not c.ok), idx,
                strategy=strat.name, checks=checks)
            if check.ok:
                outcome.attempts.append(Attempt(strat.name, "accepted", patch.note, checks))
                outcome.status, outcome.strategy, outcome.reason = FIXED, strat.name, patch.note
                if learn:
                    from ..rag import memory
                    if memory.remember(f.rule_id, strat.name, f.function,
                                       _function_code(current, f.function, f.line),
                                       _function_code(patch.patched, f.function, f.line), memory_path):
                        log("decide", "Verified fix stored in the RAG fix memory", idx)
                current, report = patch.patched, check.report
                log("decide", f"Accept {strat.name}; re-analysing the patched code", idx,
                    strategy=strat.name)
                break
            outcome.attempts.append(Attempt(strat.name, "rejected", patch.note, checks))
            log("decide", f"Reject {strat.name}; try the next strategy", idx, strategy=strat.name)

        if outcome.status != FIXED:
            notes = "; ".join(f"{a.strategy}: {a.detail}" for a in outcome.attempts)
            outcome.reason = notes or "no strategy could run"
            log("decide", f"Give up on #{idx} → needs manual fix", idx)
        if outcome.status != FIXED and guidance:
            _attach_guidance(outcome, f, current, memory_path, log, idx)

    result.patched = current
    result.findings_after = len(report.active())
    c = result.counts()
    log("done", f"{c['fixed']} of {c['findings']} finding(s) fixed and verified, "
                f"{c['needs_manual_fix']} need a manual fix; "
                f"active findings {result.findings_before} → {result.findings_after}")
    return result


def _attach_guidance(outcome: FindingOutcome, finding, source: str, memory_path, log, idx: int) -> None:
    """Retrieve passages that show how to fix this finding by hand (RAG)."""
    from .. import perf
    try:
        from ..rag import KnowledgeBase, guidance_for
        with perf.block("rag.retrieve"):
            g = guidance_for(finding, source, k=3, kb=KnowledgeBase.load(memory_path))
    except (OSError, ValueError, KeyError) as exc:          # guidance is advisory; never fatal
        log("observe", f"Guidance unavailable: {exc}", idx)
        return
    outcome.guidance = [{"kind": p.kind, "title": p.title, "source": p.source, "score": p.score,
                         "text": p.text} for p in g.passages]
    if g.passages:
        log("observe", "Retrieved guidance: " + "; ".join(f"[{p.kind}] {p.title}" for p in g.passages), idx)


def fix_source_profiled(source: str, filepath: str = "<string>", **kwargs) -> FixResult:
    """``fix_source`` inside a ``perf`` block (agent reasoning + remediation)."""
    from .. import perf
    with perf.block("agent.fix_and_verify", lines=source.count("\n") + 1):
        return fix_source(source, filepath, **kwargs)


def fix_file(path: str, **kwargs) -> FixResult:
    with open(path, encoding="utf-8") as fh:
        return fix_source(fh.read(), path, **kwargs)
