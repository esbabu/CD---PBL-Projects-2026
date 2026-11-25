"""RAG guidance: tokenizer, BM25 ranking, knowledge base, verified-fix memory (including its
safety rules) and the agent integration."""
import json
import os
import tempfile
import textwrap

import pytest

from src.agent.fixer import FIXED, MANUAL, fix_source
from src.rag import KnowledgeBase, guidance_for, retrieve
from src.rag import memory
from src.rag.retriever import BM25, tokenize
from src.security.analyzer import analyze_source
from tests.test_security_rules50 import CASES


@pytest.fixture
def mem_path():
    d = tempfile.mkdtemp()
    return os.path.join(d, "fix_memory.jsonl")


def test_tokenizer_splits_identifiers_and_keeps_ids():
    toks = tokenize("render_template_string setFeature CWE-89 SEC005")
    for t in ("render", "template", "string", "set", "feature", "setfeature", "cwe89", "sec005"):
        assert t in toks


def test_bm25_ranks_the_matching_document_first():
    docs = [tokenize("sql query cursor execute parameter"), tokenize("html escape template"),
            tokenize("shell command subprocess")]
    assert BM25(docs).top(tokenize("cursor execute with a query"), 1)[0][0] == 0


def test_knowledge_base_covers_every_rule_and_the_security_kb():
    from src.security.rules import RULES
    kb = KnowledgeBase.load(include_memory=False)
    assert {d.rule_id for d in kb.documents if d.kind == "rule"} == set(RULES)
    assert {f"SEC{n:03d}" for n in range(1, 51)} <= {d.rule_id for d in kb.documents if d.kind == "example"}
    kinds = {d.kind for d in kb.documents}
    assert {"rule", "example", "cwe", "capec"} <= kinds
    assert sum(d.kind in ("cwe", "capec") for d in kb.documents) >= 1000


@pytest.mark.parametrize("text,rule", [
    ("user input concatenated into an LDAP search filter", "SEC019"),
    ("xpath expression built from request parameter", "SEC020"),
    ("jwt decode without verifying the signature", "SEC047"),
    ("requests get with verify False certificate", "SEC030"),
    ("tarfile extractall path traversal members", "SEC042"),
])
def test_free_text_retrieval(text, rule):
    assert retrieve(text, k=1)[0].rule_id == rule


def test_guidance_is_restricted_to_the_finding_rule():
    src = textwrap.dedent(CASES["SEC019"][0])
    f = next(x for x in analyze_source(src, "c.py").active() if x.rule_id == "SEC019")
    g = guidance_for(f, src, kb=KnowledgeBase.load(include_memory=False))
    assert g.passages and all(p.rule_id == "SEC019" for p in g.passages)
    assert any(p.kind == "rule" for p in g.passages)


def test_memory_stores_only_valid_code_and_masks_credentials(mem_path):
    assert memory.remember("SEC024", "s", "f", "def f(:", "def f(): pass", mem_path) is False
    assert memory.remember("SEC024", "s", "f", "def f(): pass", "def f(): pass", mem_path) is False
    before = 'def f():\n    password = "hunter2hunter2"\n    return re.findall(p, t)'
    after = 'def f():\n    password = "hunter2hunter2"\n    return re.findall(re.escape(p), t)'
    assert memory.remember("SEC024", "regex-escape", "f", before, after, mem_path) is True
    assert memory.remember("SEC024", "regex-escape", "f", before, after, mem_path) is False  # duplicate
    recs = memory.load(mem_path)
    assert len(recs) == 1 and "hunter2" not in recs[0]["before"] and "****" in recs[0]["after"]


def test_tampered_memory_records_are_ignored(mem_path):
    memory.remember("SEC024", "regex-escape", "f", "def f():\n    return 1",
                    "def f():\n    return 2", mem_path)
    rec = json.loads(open(mem_path, encoding="utf-8").readline())
    rec["after"] = "def f():\n    import os; os.system('rm -rf /')"    # edited by hand
    with open(mem_path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec) + "\n")
        fh.write("not json\n")
    assert len(memory.load(mem_path)) == 1
    assert "os.system" not in KnowledgeBase.load(mem_path).documents[-1].text


def test_agent_learns_verified_fixes_and_retrieves_them(mem_path):
    src = textwrap.dedent(CASES["SEC024"][0])
    result = fix_source(src, "c.py", learn=True, memory_path=mem_path)
    assert any(o.rule_id == "SEC024" and o.status == FIXED for o in result.outcomes)
    recs = memory.load(mem_path)
    assert len(recs) == 1 and recs[0]["strategy"] == "regex-escape" and "re.escape" in recs[0]["after"]
    kb = KnowledgeBase.load(mem_path)
    assert any(d.kind == "memory" for d in kb.documents)
    f = next(x for x in analyze_source(src, "c.py").active() if x.rule_id == "SEC024")
    assert guidance_for(f, src, kb=kb).passages[0].kind == "memory"


def test_rejected_or_unlearned_runs_write_nothing(mem_path):
    fix_source(textwrap.dedent(CASES["SEC024"][0]), "c.py", memory_path=mem_path)   # learn=False
    assert not os.path.exists(mem_path)


def test_manual_findings_carry_guidance(mem_path):
    result = fix_source(textwrap.dedent(CASES["SEC019"][0]), "c.py", memory_path=mem_path)
    o = next(o for o in result.outcomes if o.rule_id == "SEC019")
    assert o.status == MANUAL and o.guidance
    assert all(g["source"] for g in o.guidance)
