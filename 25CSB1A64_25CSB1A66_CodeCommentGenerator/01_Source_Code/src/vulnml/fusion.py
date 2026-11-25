"""
Neuro-symbolic security engine
===============================
Combines the three sources of evidence for every function:

  neural     the ML detector's family and P(vulnerable), with the tokens behind it
  symbolic   the rule engines' findings (taint, memory safety, syntax rules)
  semantic   detection conditions from the knowledge base: does the function call
             a sink API of the predicted family (the same sink tables the taint
             engine uses), with data that is not a constant?

Reasoning (each step is written into the finding's ``confidence_reasons``):

  1. rule finding + ML agrees on the family (P ≥ 0.6)
       → kept; "ML detector agrees" is recorded; a *potential* finding whose only
         doubts are a method-name sink match or an unresolved call is upgraded to
         *confirmed* when P ≥ 0.8.
  2. rule finding + ML says safe (P(vulnerable) < 0.2)
       → kept unchanged (symbolic evidence wins); the disagreement is recorded.
  3. no rule finding, ML predicts a family with P ≥ 0.7, and the semantic check
     holds (a sink API of that family is called with non-constant data)
       → a new finding SEC064 "Possible <family> (neuro-symbolic)", status
         *potential*, with the ML evidence tokens and the sink call as its trace.
  4. ML alone with no semantic evidence → not reported (recorded in
     ``ml_unconfirmed`` on the result for transparency).

For Rust and COBOL (small-n models, see detector.SMALL_N) the engine has no neural
signal and returns the rule findings unchanged.
"""
from __future__ import annotations

import ast
import re
from typing import Dict, List, Optional

from ..security.findings import Finding
from ..security.rules import RULES
from .detector import MLPrediction, predict_lowered, predict_python
from .families import family_cwe, family_label, family_of_rule

AGREE_P, UPGRADE_P, NEW_P, DISAGREE_P = 0.6, 0.8, 0.7, 0.2


def _family_sink_patterns(lang: str, fam: str) -> List[tuple]:
    """(patterns, args) of every sink whose rule belongs to the family (multi-language specs)."""
    from ..multilang.specs import SPECS
    spec = SPECS.get(lang)
    if spec is None:
        return []
    return [(s.patterns, s.args) for s in spec.sinks if family_of_rule(s.rule_id) == fam]


def _semantic_evidence_lowered(info, lang: str, fam: str) -> Optional[str]:
    from ..ir.ir_nodes import IROpcode
    from ..multilang.taint import match_call
    sinks = _family_sink_patterns(lang, fam)
    consts = {i.result for i in info.fn.all_instructions() if i.op == IROpcode.ASSIGN and "const" in i.meta}
    for ins in info.fn.all_instructions():
        if ins.op != IROpcode.CALL or ins.call is None:
            continue
        for patterns, args in sinks:
            if match_call(patterns, ins) is None:
                continue
            positions = range(len(ins.call.args)) if args == "*" else args
            data = [ins.call.args[k] for k in positions if k < len(ins.call.args)]
            if any(a not in consts for a in data):
                return f"L{ins.lineno}: calls {ins.call.raw_callee}() — a {family_label(fam).lower()} sink — with non-constant data"
    return None


_PY_SINKS = None


def _python_sinks() -> Dict[str, List[str]]:
    global _PY_SINKS
    if _PY_SINKS is None:
        from ..security.rules import SINKS
        _PY_SINKS = {}
        for s in SINKS:
            fam = family_of_rule(s.rule_id)
            if fam:
                _PY_SINKS.setdefault(fam, []).extend(list(s.callees) + [f".{m}" for m in s.methods])
    return _PY_SINKS


def _semantic_evidence_python(fn_node, fam: str, imports: Dict[str, str]) -> Optional[str]:
    names = _python_sinks().get(fam, [])
    for n in ast.walk(fn_node):
        if not isinstance(n, ast.Call):
            continue
        func = n.func
        dotted = ast.unparse(func)
        root = dotted.split(".")[0]
        canon = imports.get(root, root) + dotted[len(root):]
        hit = any(canon == s or (s.startswith(".") and dotted.endswith(s)) for s in names)
        if hit and any(not isinstance(a, ast.Constant) for a in n.args):
            return f"L{n.lineno}: calls {dotted}() — a {family_label(fam).lower()} sink — with non-constant data"
    return None


def _apply(findings: List[Finding], preds: List[MLPrediction], filepath: str, evidence_for) -> List[Finding]:
    out = list(findings)
    unconfirmed = []
    for p in preds:
        in_fn = [f for f in findings if p.line <= f.line <= p.end_line and f.status != "suppressed"]
        ml_txt = (f"ML detector: {family_label(p.family)} with P(vulnerable) = {p.p_vulnerable:.2f}"
                  + (f" (driven by tokens: {', '.join(t for t, _ in p.evidence[:5])})" if p.evidence else ""))
        if in_fn:
            for f in in_fn:
                fam = family_of_rule(f.rule_id)
                if p.p_vulnerable >= AGREE_P and fam == p.family:
                    f.confidence_reasons.append("neuro-symbolic: " + ml_txt + " — agrees with the rule finding")
                    doubts = [r for r in f.confidence_reasons if r.startswith(("sink '", "value passes through"))]
                    others = [r for r in f.confidence_reasons if not r.startswith(("sink '", "value passes through",
                                                                                   "neuro-symbolic"))
                              and "local" not in r and "resolved sink" not in r and "structural" not in r]
                    if f.status == "potential" and p.p_vulnerable >= UPGRADE_P and doubts and not others \
                            and f.analysis == "taint":
                        f.status, f.confidence = "confirmed", "high"
                        f.confidence_reasons.append("neuro-symbolic: upgraded to confirmed — the only doubts were "
                                                    "resolution heuristics and the ML detector independently agrees")
                elif p.p_vulnerable < DISAGREE_P:
                    f.confidence_reasons.append("neuro-symbolic: " + ml_txt + " — ML considers the function safe; "
                                                "kept because the symbolic evidence is explicit")
            continue
        if p.p_vulnerable < NEW_P:
            continue
        sem = evidence_for(p)
        if sem is None:
            unconfirmed.append({"function": p.function, "family": p.family, "p_vulnerable": p.p_vulnerable})
            continue
        line = int(re.match(r"L(\d+)", sem).group(1))
        rule = RULES["SEC064"]
        f = Finding(rule_id="SEC064", title=f"Possible {family_label(p.family).lower()} (neuro-symbolic)",
                    category=rule.category, cwe=family_cwe(p.family), severity="medium", confidence="low",
                    status="potential", file=filepath, function=p.function, line=line, col=0,
                    message=(f"The ML detector predicts {family_label(p.family).lower()} in {p.function}() "
                             f"(P = {p.p_vulnerable:.2f}) and the function calls a sink of that family with "
                             "non-constant data, but no rule traced an untrusted source to it."),
                    remediation=rule.remediation, analysis="neuro-symbolic",
                    severity_reason="medium: statistical prediction confirmed by a semantic condition, no traced flow",
                    confidence_reasons=["neural: " + ml_txt, "semantic: " + sem,
                                        "symbolic: no rule finding in this function (no recognised source)"],
                    trace=[{"line": p.line, "col": 0, "kind": "ml", "text": ml_txt, "function": p.function},
                           {"line": line, "col": 0, "kind": "sink", "text": sem, "function": p.function}])
        f.compute_fingerprint()
        out.append(f)
    out.sort(key=lambda f: (f.line, f.rule_id))
    _LAST["unconfirmed"] = unconfirmed
    _LAST["predictions"] = preds
    return out


_LAST: Dict[str, object] = {}


def fuse(findings: List[Finding], mod, lang: str, filepath: str) -> List[Finding]:
    from .. import perf
    with perf.block("ml.predict", lines=mod.source.count("\n") + 1):
        preds = predict_lowered(mod, lang)
    if not preds:
        _LAST["predictions"], _LAST["unconfirmed"] = [], []
        return findings
    infos = mod.functions
    with perf.block("neurosymbolic.fuse"):
        return _apply(findings, preds, filepath,
                      lambda p: _semantic_evidence_lowered(infos[p.function], lang, p.family) if p.function in infos else None)


def fuse_python(findings: List[Finding], source: str, filepath: str) -> List[Finding]:
    from .. import perf
    with perf.block("ml.predict", lines=source.count("\n") + 1):
        preds = predict_python(source)
    if not preds:
        _LAST["predictions"], _LAST["unconfirmed"] = [], []
        return findings
    tree = ast.parse(source)
    from ..ir.lowering import collect_module_imports
    imports = collect_module_imports(tree)
    nodes = {(n.name, n.lineno): n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    with perf.block("neurosymbolic.fuse"):
        return _apply(findings, preds, filepath,
                      lambda p: _semantic_evidence_python(nodes[(p.function, p.line)], p.family, imports)
                      if (p.function, p.line) in nodes else None)


def last_run() -> Dict[str, object]:
    """Predictions and unconfirmed ML signals of the most recent fusion (for reports and the GUI)."""
    return dict(_LAST)
