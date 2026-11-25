"""
Retrieval-augmented guidance (RAG) for security findings
=========================================================
A small, offline retrieval system that the fix-and-verify agent, the CLI and the
GUI use to attach *evidence-based* remediation guidance to a finding.

  knowledge.py  builds the knowledge base: one card per rule (SEC001-SEC050), the
                bundled vulnerable → fixed example pairs, and the agent's memory of
                fixes that the verifier accepted
  retriever.py  BM25 ranking over code-aware tokens (pure Python, no network)
  memory.py     append-only, integrity-checked store of verified fixes
  guidance.py   turns a finding into a query and returns the top passages

Nothing here executes retrieved text. Retrieved passages are shown to people or
passed to the optional local LLM as *reference data*; any patch the LLM writes
still has to pass the agent's four verification checks.
"""
from .guidance import Guidance, explain_finding, format_explanation, guidance_for, retrieve
from .knowledge import KnowledgeBase, Document

__all__ = ["Guidance", "guidance_for", "retrieve", "explain_finding", "format_explanation", "KnowledgeBase",
           "Document"]
