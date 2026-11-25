"""
Knowledge base
===============
Three kinds of documents, all local:

  rule      one card per rule: title, CWE, category, severity, why it matters,
            remediation (from ``security.rules.RULES`` + ``data/knowledge.json``)
  example   a hand-written vulnerable → fixed pair per rule (``data/knowledge.json``)
  memory    fixes the agent made and the verifier accepted (``memory.py``)

Each document records its source, so guidance always says where a passage came
from. The bundled file is read-only data shipped with the code.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Dict, List, Optional

from ..security.rules import RULES
from . import memory
from .retriever import BM25, tokenize

DATA = os.path.join(os.path.dirname(__file__), "data", "knowledge.json")
KB_PATH = os.path.join(os.path.dirname(__file__), "data", "security_kb.json.gz")


@dataclass
class Document:
    doc_id: str
    kind: str                     # rule | example | memory
    rule_id: str
    title: str
    text: str                     # what is shown / passed on
    source: str                   # where the passage came from
    code_before: str = ""
    code_after: str = ""
    cwe: str = ""                 # CWE / CAPEC id the passage is about
    languages: tuple = ()
    tokens: List[str] = field(default_factory=list, repr=False)


def _bundled() -> Dict[str, Dict[str, str]]:
    with open(DATA, encoding="utf-8") as fh:
        return json.load(fh)["rules"]


def rule_documents() -> List[Document]:
    extra = _bundled()
    docs = []
    for rid, r in sorted(RULES.items()):
        why = extra.get(rid, {}).get("why", "")
        text = (f"{rid} {r.title} ({r.cwe or 'no CWE'}, {r.category}, severity {r.severity}). "
                f"Why it matters: {why} How to fix: {r.remediation}")
        docs.append(Document(f"rule:{rid}", "rule", rid, r.title, text,
                             f"rule catalogue (src/security/rules.py) — {r.cwe or rid}"))
        ex = extra.get(rid)
        if ex:
            docs.append(Document(f"example:{rid}", "example", rid, f"{r.title}: vulnerable vs fixed",
                                 f"Vulnerable:\n{ex['vulnerable']}\nFixed:\n{ex['fixed']}",
                                 "bundled example (src/rag/data/knowledge.json)",
                                 ex["vulnerable"], ex["fixed"]))
    return docs


@lru_cache(maxsize=1)
def security_kb() -> dict:
    """The structured knowledge base (MITRE CWE + CAPEC + NIST Juliet examples), or an empty one."""
    import gzip
    if not os.path.isfile(KB_PATH):
        return {"meta": {}, "entries": []}
    with gzip.open(KB_PATH, "rt", encoding="utf-8") as fh:
        return json.load(fh)


def kb_entry(entry_id: str) -> Optional[dict]:
    for e in security_kb()["entries"]:
        if e["id"] == entry_id:
            return e
    return None


def _kb_text(e: dict) -> str:
    parts = [f"{e['id']} {e['name']}.", e.get("description", ""), e.get("extended_description", "")[:600]]
    for m in e.get("mitigations", [])[:3]:
        parts.append("Mitigation: " + m.get("description", "")[:400])
    for d in e.get("detection_methods", [])[:2]:
        parts.append(f"Detection ({d.get('method')}): " + d.get("description", "")[:300])
    for x in e.get("examples", [])[:3]:
        if x.get("code"):
            parts.append(f"{x['nature']} {x.get('language', '')} example:\n{x['code'][:600]}")
    return "\n".join(p for p in parts if p)


def kb_documents() -> List[Document]:
    docs = []
    rule_by_cwe: Dict[str, str] = {}
    for rid, r in RULES.items():
        if r.cwe:
            rule_by_cwe.setdefault(r.cwe, rid)
    for e in security_kb()["entries"]:
        rid = rule_by_cwe.get(e["id"], "")
        docs.append(Document(f"kb:{e['id']}", "cwe" if e["kind"] == "weakness" else "capec", rid,
                             f"{e['id']}: {e['name']}", _kb_text(e), f"{e['source']} — {e['url']}",
                             cwe=e["id"], languages=tuple(e.get("languages", []))))
    return docs


def memory_documents(path: Optional[str] = None) -> List[Document]:
    docs = []
    for i, rec in enumerate(memory.load(path)):
        rid = rec["rule_id"]
        title = RULES[rid].title if rid in RULES else rid
        docs.append(Document(f"memory:{rec['sha256'][:12]}", "memory", rid,
                             f"{title}: verified fix by {rec['strategy']}",
                             f"Before:\n{rec['before']}\nAfter:\n{rec['after']}",
                             f"verified-fix memory (fix #{i + 1}, strategy {rec['strategy']})",
                             rec["before"], rec["after"]))
    return docs


class KnowledgeBase:
    """The indexed documents. Build once with :meth:`load` (cached) and query with :meth:`search`."""

    def __init__(self, documents: List[Document]):
        self.documents = documents
        for d in documents:
            # rule metadata words are part of what a passage is about, so they are indexed too
            meta = RULES.get(d.rule_id)
            head = f"{d.title} {meta.category} {meta.cwe or ''}" if meta else d.title
            d.tokens = tokenize(f"{head}\n{d.text}")
        self.index = BM25([d.tokens for d in documents])

    @classmethod
    def load(cls, memory_path: Optional[str] = None, include_memory: bool = True) -> "KnowledgeBase":
        key = (memory_path or memory.memory_path(), include_memory,
               _mtime(memory_path or memory.memory_path()))
        return _cached(*key)

    def search(self, query: str, k: int = 3, kinds: Optional[tuple] = None,
               rule_id: Optional[str] = None) -> List[tuple]:
        """Top ``k`` (document, score) pairs; optional filters on kind and rule."""
        scored = self.index.top(tokenize(query), len(self.documents))
        out = []
        for i, s in scored:
            d = self.documents[i]
            if kinds and d.kind not in kinds:
                continue
            if rule_id and d.rule_id != rule_id:
                continue
            out.append((d, round(s, 3)))
            if len(out) == k:
                break
        return out


def _mtime(path: str) -> float:
    try:
        return os.path.getmtime(path)
    except OSError:
        return 0.0


@lru_cache(maxsize=4)
def _cached(memory_path: str, include_memory: bool, _mtime_key: float) -> KnowledgeBase:
    docs = rule_documents() + kb_documents()
    if include_memory:
        docs += memory_documents(memory_path)
    return KnowledgeBase(docs)
