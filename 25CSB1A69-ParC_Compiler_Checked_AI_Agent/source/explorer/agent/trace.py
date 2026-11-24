"""A readable, ordered timeline of one explain/fix request.

This adds no new agent logic and runs no new check: it only re-reads what
agent.explain()/agent.fix() already computed and already tests (the
"security" events, "shown_code", and for a fix every candidate's verdict)
and lays them out as a sequence of steps, each naming which reviewer
produced it and what that reviewer was allowed to see. The point is to make
least privilege visible: a reviewer's step shows only the data that
reviewer actually had, nothing from later in the pipeline.
"""


def _step(actor, label, detail, tone="neutral", code=None):
    return {"actor": actor, "label": label, "detail": detail, "tone": tone, "code": code}


def _input_steps(events):
    """The input-stage events, split by which reviewer produced them: the claim checker's
    event is always "contradicted-claim"; everything else at this stage is the rules."""
    input_events = [e for e in events if e["stage"] == "input"]
    if not input_events:
        return [_step("Rules reviewer", "nothing matched", "No wording in the comments, strings or names looked "
                      "like an instruction to the model.", "good")]
    steps = []
    for e in input_events:
        actor = "Claim checker" if e["attack"] == "contradicted-claim" else "Rules reviewer"
        tone = "risk" if e["action"] in ("blocked", "sanitized") else "warn"
        steps.append(_step(actor, e["attack"], e["detail"], tone))
    return steps


def _numbered(label, counts):
    """label, or "label (2nd time)" if this exact label has been seen before — the model's
    retries often trip the same check more than once, and that is worth showing, not hiding."""
    counts[label] = counts.get(label, 0) + 1
    n = counts[label]
    return label if n == 1 else f"{label} ({n}{'nd' if n == 2 else 'rd' if n == 3 else 'th'} time)"


def _model_step(result):
    code = result.get("shown_code")
    if code is None:
        return _step("Model", "not used", "No model answered this request: either none is set up, or an input-"
                     "stage reviewer refused to use one. A template answered instead; see the input steps above "
                     "for why.", "warn")
    asked = result.get("model") if result.get("model") not in (None, "none") else result.get("source")
    return _step("Model", f"asked ({asked or 'a model'})",
                "Shown exactly this — the flagged function, with comments already removed if a reviewer above "
                "required it, and the compiler's facts about the finding. Never the token or tree JSON.",
                "neutral", code=code)


def _blind_step():
    return _step("Blind mode", "every comment removed", "By design, not by detection: the model is never shown "
                 "a comment, whatever its wording or language, so a comment injection has nowhere to go.", "good")


def explain_trace(source, build, finding, result, blind=False):
    """The timeline for one agent.explain() result. `finding` is the finding dict (from
    build["findings"]["findings"]); `result` is exactly what agent.explain() returned.
    `blind` says whether blind mode was on for the request (security.blind())."""
    steps = [_step("Compiler", finding.get("id", ""),
                   f"{finding.get('kind', '')} at line {finding.get('line', '?')}: {finding.get('message', '')}",
                   "neutral")]
    if result.get("hint"):
        steps.append(_step("User sees", "a guiding question, not an explanation", result.get("explanation", ""),
                           "neutral"))
        return steps
    steps += _input_steps(result.get("security", []))
    if blind:
        steps.append(_blind_step())
    steps.append(_model_step(result))
    output_events = [e for e in result.get("security", []) if e["stage"] == "explanation"]
    for e in output_events:
        actor = "Fact check" if e["attack"] == "fact-mismatch" else "Explanation rules"
        steps.append(_step(actor, e["attack"], e["detail"], "risk" if e["action"] == "blocked" else "warn"))
    source_label = "the compiler's own template" if result.get("source") == "template" else result.get("source", "")
    steps.append(_step("User sees", source_label, result.get("explanation", ""),
                       "neutral" if result.get("source") == "template" else "good"))
    return steps


def fix_trace(source, build, finding, result, blind=False):
    """The timeline for one agent.fix() result."""
    steps = [_step("Compiler", finding.get("id", ""),
                   f"{finding.get('kind', '')} at line {finding.get('line', '?')}: {finding.get('message', '')}",
                   "neutral")]
    steps += _input_steps(result.get("security", []))
    if blind:
        steps.append(_blind_step())
    steps.append(_model_step(result))
    rewrite_events = [e for e in result.get("security", []) if e["stage"] in ("rewrite", "tool")]
    seen = {}
    for e in rewrite_events:
        actor = "Tool check" if e["stage"] == "tool" else "Rewrite check"
        steps.append(_step(actor, _numbered(e["attack"], seen), e["detail"], "risk" if e["action"] == "blocked" else "warn"))
    for c in result.get("candidates", []):
        if c["passed"]:
            detail = f"compiles, fixes {finding.get('id', '')}, no new warning, same behaviour"
            tone = "good"
        elif c["failed_at"] == "security":
            # c["reason"] already starts "refused by the security check: ..."; don't say it twice.
            detail = c["reason"][0].upper() + c["reason"][1:]
            tone = "risk"
        else:
            detail = f"refused at the “{c['failed_at']}” check: {c['reason']}"
            tone = "warn"
        steps.append(_step("Compiler gate", c["description"], detail, tone))
    if result.get("fixed"):
        steps.append(_step("User sees", f"the fix ({result.get('origin', '')})", result.get("description", ""), "good"))
    else:
        steps.append(_step("User sees", "no fix", result.get("reason", ""), "neutral"))
    return steps


def trace(ask, source, build, finding, result, blind=False):
    """explain_trace() or fix_trace(), by `ask` ("explain" or "fix")."""
    if ask == "fix":
        return fix_trace(source, build, finding, result, blind)
    return explain_trace(source, build, finding, result, blind)
