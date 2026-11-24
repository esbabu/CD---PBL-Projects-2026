# LLM Call-Site & Decision Audit (`repair/llm_audit.md`)

Generated before refactoring Workstreams D and E.

## 1. Complete Inventory of LLM Call Sites & Direct Dependencies

| File & Line | Symbol | Role | Defect Classification | Planned Fix |
|---|---|---|---|---|
| `optagent/llm/client.py:48,66` | `LLMClient.complete_json` | HTTP transport | Direct `litellm` dependency; no Ollama `/api/chat`, no health check, no model resolution, no context check, no cache, no concurrency semaphore | Reimplement `LLMClient` on top of `OllamaGateway` (`optagent/llm/{ollama,gateway,health,cache}.py`); remove `litellm` |
| `optagent/intent/pipeline.py:29-30,127` | `IntentExtractor.run` (`SpecAgent.draft`) | Spec drafting | **Missing fallback**: unhandled `LLMError` crashes entire run even when heuristic path can proceed | Wrap via `@component(kind=LLM)` + template spec fallback from static facts |
| `optagent/intent/pipeline.py:137-140` | `IntentExtractor.run` (`InputAgent.generate`) | Extra seed inputs | Has `try/except LLMError`, but heuristic seed ladder is too weak (annotations only) | Add 7-step heuristic seed ladder first; LLM seeds merged additively with provenance |
| `optagent/intent/pipeline.py:164-174` | `IntentExtractor.run` (`SpecValidator.validate` + `SpecAgent.refine`) | Spec cross-check | `SpecValidator.validate` lacks outer catch for gateway errors; no provenance recorded | Wrap with `@component(kind=LLM)`, degrade to `validation.status="skipped"` |
| `optagent/oracle/builder.py:67,181-194` | `OracleBuilder.build` (`PropertyProposer`, `RedTeamAgent`) | Properties & adversarial inputs | Only called when `use_llm=True`; needs `@component(kind=LLM)` + provenance tracking & fallback guarantee | Decorate with `@component`, keep heuristic packs independent |
| `optagent/proposers/ensemble.py:41` / `llm_proposer.py:63-160` | `LLMProposer.propose` | Candidate rewrites | Hard-codes Python `ast.parse(code)` at `llm_proposer.py:138` (rejects JS/C/C++ candidates); lacks provenance tags | Route syntax validation through language adapter; wrap with `@component(kind=LLM)`, rule engine always runs first |
| `optagent/verify/rungs.py` (`run_r8_llm_reviewer`) | `run_r8_llm_reviewer` | Advisory review | Must never decide correctness or grant evidence tier | Mark advisory-only with `@component(kind=LLM)`, omit gracefully when LLM unavailable |

## 2. Decision Sites Audit (Ensuring Deterministic Ownership)

| Decision | File | Current Owner | Required Owner | Status |
|---|---|---|---|---|
| Entry point selection | `analysis/static_facts.py`, `lang/*/adapter.py` | Heuristic | `HEURISTIC` | Fix ambiguous ranking (B2); never LLM-decided |
| Parameter types & seeds | `analysis/inputs.py`, `oracle/schema_infer.py` | Partial heuristic | `HEURISTIC` core + optional `LLM` additive | Add usage-based type inference + stdin grammar (B7) |
| Equivalence verdict | `oracle/compare.py`, `oracle/oracle.py` | Deterministic `Comparator` | `HEURISTIC` / `TOOL` only | Preserve invariant; enforce via tests |
| Complexity measurement | `complexity/{static_cost,empirical,reconcile}.py` | Deterministic | `HEURISTIC` / `TOOL` only | Fix `profiler.py` dict-keys bug; multi-lang fallback |
| Evidence tier & winner selection | `verify/ladder.py`, `search/controller.py` | Deterministic | `HEURISTIC` / `TOOL` only | Preserve invariant; add provenance summary |
| HTTP / LLM library imports | All files outside `optagent/llm/` | Only `llm/client.py` imported `litellm` | Strictly restricted to `optagent/llm/` | Enforce via AST test `tests/test_component_enforcement.py` |
