# OptAgent Component Taxonomy Map

Generated directly from `@component` registrations (`optagent/core/provenance.py`).

| Kind | Component | Module | Fallback Defined | Description |
|---|---|---|---|---|
| `HEURISTIC` | `inputs.annotation_inputs` | `optagent.analysis.inputs` | No | Derive seed inputs from parameter type annotations. |
| `HEURISTIC` | `inputs.heuristic_seed_inputs` | `optagent.analysis.inputs` | No | 7-step deterministic heuristic seed input ladder. |
| `HEURISTIC` | `inputs.infer_stdin_seeds` | `optagent.analysis.inputs` | No | Infer bounded stdin test inputs from script input() patterns. |
| `HEURISTIC` | `static_facts.analyze_source` | `optagent.analysis.static_facts` | No | Python AST fact, method, effect, and pattern extraction |
| `HEURISTIC` | `static_facts.rank_entries` | `optagent.analysis.static_facts` | No | Deterministic heuristic entry point ranker |
| `HEURISTIC` | `complexity.empirical` | `optagent.complexity.empirical` | No | Empirical scaling curve fitting & R^2 validation |
| `HEURISTIC` | `complexity.static_cost` | `optagent.complexity.static_cost` | No | Deterministic static loop/recursion cost analyzer |
| `HEURISTIC` | `triage.run_triage` | `optagent.core.triage` | No | Deterministic syntax, dependency, entry, and toolchain triage. |
| `HEURISTIC` | `contract.build_contract` | `optagent.intent.contract` | No | Deterministic preservation contract builder |
| `HEURISTIC` | `oracle.compare` | `optagent.oracle.compare` | No | Sole deterministic equivalence & safety verdict authority |
| `HEURISTIC` | `proposers.rule_engine` | `optagent.proposers.rule_engine` | No | Deterministic AST/KB rule rewrites |
| `HYBRID` | `proposers.ensemble` | `optagent.proposers.ensemble` | Yes | Merges heuristic rule engine + optional LLM candidates |
| `LLM` | `input_agent.generate` | `optagent.intent.input_agent` | Yes | Additive LLM seed input generation (falls back to heuristic seed ladder) |
| `LLM` | `spec_agent.draft` | `optagent.intent.spec_agent` | Yes | Advisory spec drafting (falls back to heuristic template spec) |
| `LLM` | `validator.validate` | `optagent.intent.validator` | Yes | Independent spec cross-check (skips on LLM failure) |
| `LLM` | `llm.gateway` | `optagent.llm.gateway` | No | Single Ollama HTTP gateway (/api/chat, /api/tags, /api/show, sqlite cache) |
| `LLM` | `oracle.adversary_agent` | `optagent.oracle.agents` | Yes | Red-team inputs (falls back to heuristic packs) |
| `LLM` | `oracle.property_agent` | `optagent.oracle.agents` | Yes | Property proposals validated against original (falls back to none) |
| `LLM` | `proposers.llm_proposer` | `optagent.proposers.llm_proposer` | Yes | LLM candidate synthesizer (falls back to rule engine only) |
| `LLM` | `verify.r8_llm_reviewer` | `optagent.verify.rungs` | Yes | Advisory-only LLM reviewer (never grants tier or decides correctness) |
| `TOOL` | `bench.runner` | `optagent.bench.runner` | No | Repeated benchmark timing & statistical significance gate |
| `TOOL` | `complexity.profiler` | `optagent.complexity.profiler` | No | Empirical line/cProfile/tracemalloc profiler |
| `TOOL` | `oracle.fuzzer` | `optagent.oracle.fuzzer` | No | Coverage-guided differential fuzzer |
| `TOOL` | `oracle.mutation` | `optagent.oracle.mutation` | No | Mutation testing and survivor hunting |
| `TOOL` | `sandbox.run` | `optagent.runtime.sandbox` | No | Isolated subprocess/Docker execution of original & candidate |
| `TOOL` | `verify.ladder` | `optagent.verify.ladder` | No | Deterministic verification rungs R1-R7 + tier assignment |
