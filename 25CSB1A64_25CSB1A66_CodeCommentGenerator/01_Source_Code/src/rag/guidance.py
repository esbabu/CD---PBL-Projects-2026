"""
Guidance for a finding
=======================
Builds a retrieval query from a finding (its message, the sink and source code,
the function's own code) and returns ranked passages from the knowledge base.

Two retrieval modes:

* ``guidance_for(finding)`` — the analyzer already knows the rule, so passages
  are restricted to that rule and ranked by how closely they match the code
  (a verified fix of a similar function ranks above the generic example);
* ``retrieve(text)`` — free-text search over everything (the CLI ``query``
  command and the evaluation in ``evaluate.py``).
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import List, Optional

from .knowledge import KnowledgeBase


@dataclass
class Passage:
    doc_id: str
    kind: str
    rule_id: str
    title: str
    source: str
    score: float
    text: str


@dataclass
class Guidance:
    rule_id: str
    query: str
    passages: List[Passage] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

    def format(self, max_chars: int = 600) -> str:
        lines = [f"Retrieved guidance for {self.rule_id}:"]
        for p in self.passages:
            text = p.text if len(p.text) <= max_chars else p.text[:max_chars].rstrip() + " ..."
            lines.append(f"  [{p.kind}] {p.title}  (score {p.score}; source: {p.source})")
            lines.extend("      " + t for t in text.splitlines())
        return "\n".join(lines)


def finding_query(finding, source: Optional[str] = None) -> str:
    """Query text for a finding: message, sink/source code and the enclosing function."""
    parts = [finding.title, finding.message]
    sink = getattr(finding, "sink", None) or {}
    src = getattr(finding, "source", None) or {}
    parts += [sink.get("code", ""), sink.get("operation", ""), src.get("code", ""),
              src.get("description", "")]
    if source and getattr(finding, "line", 0):
        lines = source.splitlines()
        lo, hi = max(0, finding.line - 6), min(len(lines), finding.line + 3)
        parts.append("\n".join(lines[lo:hi]))
    return "\n".join(p for p in parts if p)


def _passages(hits) -> List[Passage]:
    return [Passage(d.doc_id, d.kind, d.rule_id, d.title, d.source, s, d.text) for d, s in hits]


def guidance_for(finding, source: Optional[str] = None, k: int = 3,
                 kb: Optional[KnowledgeBase] = None) -> Guidance:
    """Ranked passages for one finding (restricted to its rule)."""
    kb = kb or KnowledgeBase.load()
    query = finding_query(finding, source)
    hits = kb.search(query, k=k, rule_id=finding.rule_id)
    if not any(d.kind == "rule" for d, _ in hits):            # always include the rule card
        card = next((d for d in kb.documents if d.doc_id == f"rule:{finding.rule_id}"), None)
        if card is not None:
            hits = hits[:k - 1] + [(card, 0.0)]
    return Guidance(finding.rule_id, query, _passages(hits))


_LANG_NAMES = {"python": "Python", "java": "Java", "csharp": "C#", "c": "C", "cpp": "C++", "rust": "Rust",
               "cobol": "COBOL"}


def explain_finding(finding, source: Optional[str] = None, language: str = "python") -> dict:
    """An explanation of one finding for people and for the agent, grounded in retrieved knowledge.

    Returns the source-code evidence (the trace lines), the CWE description and consequences,
    mitigations, the closest vulnerable / fixed example (preferring the finding's language), related
    attack patterns and references — each part with its source.
    """
    from .. import perf
    from .knowledge import kb_entry
    from ..security.rules import RULES
    with perf.block("rag.retrieve"):
        return _explain(finding, source, language, kb_entry, RULES)


def _explain(finding, source, language, kb_entry, RULES) -> dict:
    rule = RULES.get(finding.rule_id)
    cwe = finding.cwe or (rule.cwe if rule else None)
    entry = kb_entry(cwe) if cwe else None
    evidence = [{"line": s["line"], "kind": s["kind"], "text": s["text"]} for s in finding.trace]
    if not evidence and source:
        lines = source.splitlines()
        if 0 < finding.line <= len(lines):
            evidence = [{"line": finding.line, "kind": "code", "text": lines[finding.line - 1].strip()}]
    out = {"rule": finding.rule_id, "title": finding.title, "cwe": cwe, "severity": finding.severity,
           "confidence": finding.confidence, "location": f"{finding.file}:{finding.line}",
           "evidence": evidence, "finding": finding.message, "fix": finding.remediation, "knowledge": None}
    if entry is not None:
        want = _LANG_NAMES.get(language, language)
        examples = entry.get("examples", [])
        same = [x for x in examples if x.get("language") == want and x.get("code")]
        pick = same or [x for x in examples if x.get("code")]
        bad = next((x for x in pick if x["nature"] == "bad"), None)
        good = next((x for x in pick if x["nature"] == "good"), None)
        out["knowledge"] = {
            "id": entry["id"], "name": entry["name"], "source": entry["source"], "url": entry["url"],
            "description": entry.get("description", ""),
            "consequences": entry.get("consequences", [])[:3],
            "mitigations": [m.get("description", "") for m in entry.get("mitigations", [])[:3]],
            "example_vulnerable": bad, "example_fixed": good,
            "observed_cves": [o["cve"] for o in entry.get("observed_examples", [])[:4]],
            "attack_patterns": entry.get("related_attack_patterns", [])[:5],
            "references": entry.get("references", [])[:4],
            "detected_in_languages": entry.get("detection", {}).get("languages", []),
        }
    return out


def format_explanation(ex: dict, max_code: int = 900) -> str:
    lines = [f"{ex['rule']} {ex['title']} ({ex['cwe']}) — {ex['severity']} severity, {ex['confidence']} confidence",
             f"  at {ex['location']}", f"  {ex['finding']}"]
    if ex["evidence"]:
        lines.append("  evidence from the code:")
        lines += [f"    L{e['line']:<4} [{e['kind']}] {e['text']}" for e in ex["evidence"][:12]]
    lines.append(f"  fix: {ex['fix']}")
    k = ex.get("knowledge")
    if k:
        lines.append(f"  knowledge: {k['id']} {k['name']}  ({k['source']}, {k['url']})")
        lines.append("    " + k["description"][:400])
        for m in k["mitigations"][:2]:
            lines.append("    mitigation: " + m[:300])
        for label, x in (("vulnerable example", k["example_vulnerable"]), ("fixed example", k["example_fixed"])):
            if x:
                lines.append(f"    {label} ({x.get('language') or 'any language'}; {x['source']}):")
                lines += ["      " + l for l in x["code"][:max_code].splitlines()[:18]]
        if k["observed_cves"]:
            lines.append("    seen in: " + ", ".join(k["observed_cves"]))
    return "\n".join(lines)


def retrieve(text: str, k: int = 5, kb: Optional[KnowledgeBase] = None,
             kinds: Optional[tuple] = None) -> List[Passage]:
    """Free-text retrieval over the whole knowledge base."""
    kb = kb or KnowledgeBase.load()
    return _passages(kb.search(text, k=k, kinds=kinds))
