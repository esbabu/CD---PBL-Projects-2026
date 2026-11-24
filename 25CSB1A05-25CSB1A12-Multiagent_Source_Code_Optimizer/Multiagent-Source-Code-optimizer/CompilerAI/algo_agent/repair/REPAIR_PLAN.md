# OptAgent Repair Plan (Repository-First Investigation)

## 1. Actual Repository Architecture & Request-to-Result Flow

```
OptimizeRequest (CLI / FastAPI / CompilerAI Adapter)
  └─► OptimizerAgent.run() [optagent/agent.py]
        ├─► Step 1: IntentExtractor.run() [optagent/intent/pipeline.py]
        │     ├─ Language detection & adapter [optagent/lang/registry.py]
        │     ├─ Static facts [analysis/static_facts.py | adapter.analyze()]
        │     ├─ Entry selection [select_entry | adapter.select_entry()]
        │     ├─ Seed inputs [analysis/inputs.py | adapter.seed_inputs() | InputAgent]
        │     ├─ Golden seed exec [runtime/executor.py | Sandbox]
        │     └─ Contract reconciliation [intent/contract.py + adapter.contract_rules()]
        ├─► Step 2: OracleBuilder.build() -> Oracle [optagent/oracle/{builder,oracle}.py]
        │     ├─ Schema inference, family/hypothesis/fuzz/scaling generation
        │     ├─ Golden stability runs & coverage [oracle/golden.py]
        │     └─ Mutation testing [oracle/mutation.py]
        ├─► Step 3: Analyzer.analyze() [optagent/complexity/{analyzer,static_cost,profiler,empirical}.py]
        ├─► Step 4: ProposerEnsemble [optagent/proposers/{ensemble,rule_engine,llm_proposer}.py]
        ├─► Step 5-6: SearchController + Ladder + BenchmarkRunner [optagent/{search,verify,bench}/]
        └─► Step 7: ReportBuilder + MemoryStore [optagent/{report,memory}/]
```

## 2. Diagnosed Root Causes for D1–D4 (with Evidence)

### D1: C, C++, JavaScript End-to-End Failure
- **Symptom**: Running `OptimizerAgent.run()` on `examples/js/two_sum.js` crashes at Step 2 (`L6`) with `SyntaxError: invalid syntax (<unknown>, line 1)`. C/C++ crash at `L2` with raw `Build failed: Compiler not found` instead of typed `TOOLCHAIN_MISSING` / `ANALYSIS_ONLY`.
- **Root Causes**:
  1. `optagent/agent.py:118-156` does not pass `adapter` into `OracleBuilder`, `Oracle`, `Analyzer`, `ProposerEnsemble`, `Ladder`, or `BenchmarkRunner`.
  2. `optagent/oracle/mutators.py:50` (`build_pool`) calls Python `ast.parse(source)` directly on JS/C/C++ source.
  3. `optagent/oracle/builder.py:37`, `optagent/oracle/oracle.py:120` (`_static`), `optagent/complexity/static_cost.py:100`, `optagent/complexity/profiler.py:39,56`, `optagent/proposers/llm_proposer.py:138`, `optagent/proposers/rule_engine.py:120`, `optagent/verify/diffcov.py:25` all hard-code Python `ast.parse` or `target.py`/`profile_harness.py`.
  4. `optagent/lang/js/adapter.py` + `Sandbox` needed Node.js lookup fallback when Node lives in user-local path and ESM/async/stdin handling.
  5. When native C/C++ compilers (`clang`/`gcc`/Docker) are absent on host, the pipeline raises an unhandled `IntentError` instead of degrading to `ANALYSIS_ONLY` with `TOOLCHAIN_MISSING`.

### D2: Complex / Unusual Python Denials & Crashes
- **Symptom**: Baseline ladder shows only 4/25 fixtures reach L8 PASS.
- **Root Causes**:
  1. **Class methods** (`leetcode_class.py`, `static_and_classmethods.py`): `analysis/static_facts.py:114` skips `ast.ClassDef` with `continue`; harness cannot instantiate classes or track `self.__dict__`.
  2. **Script mode** (`stdin_script.py`): `static_facts.py` + `select_entry` raise `AmbiguousEntry([])` when no top-level function exists.
  3. **Async entry** (`async_entry.py`): `intent/pipeline.py:110` explicitly raises `IntentError("async entry points are not supported yet")`.
  4. **Missing seeds** (`dataclass_args.py`, `no_annotations_complex.py`): `analysis/inputs.py` only inspects type annotations; no usage-based type inference, default values, doctests, call-site extraction, or stdin grammar inference.
  5. **Profiler crash** (`decorated_cached.py`, `deep_recursion.py`, `slow_heavy.py`): `complexity/profiler.py:114` iterates `for c in oracle.cases` (dict keys = `str`) instead of `oracle.cases.values()`, crashing with `AttributeError: 'str' object has no attribute 'kind'`.
  6. **No typed outcomes / stage isolation**: Exceptions (`IntentError`, `OracleError`, `AmbiguousEntry`, `AttributeError`) abort runs with bare errors/tracebacks instead of returning `OptimizeOutcome(support_level, reasons, stages, provenance)`.
  7. **Arbitrary objects & caches**: `runtime/canon.py` + `batch_harness.py` lack structural dataclass/object reconstruction, `lru_cache` clearing per case, adaptive timeouts, and `numpy.ndarray` tag.

### D3: Heuristic vs LLM Mixing & Missing Provenance
- **Root Causes**:
  1. No `@component(kind=..., llm_fallback=...)` registry or provenance tracking.
  2. `intent/pipeline.py:127` calls `SpecAgent.draft()` with no `try/except`, so any LLM error aborts the entire heuristic pipeline.
  3. `oracle/builder.py` and `proposers/ensemble.py` lack structured provenance summaries distinguishing `HEURISTIC`, `TOOL`, `LLM`, and `HYBRID` outputs.
  4. No architectural test preventing HTTP/LLM imports outside `optagent/llm/`.

### D4: Unreliable LLM Access
- **Root Causes**:
  1. `optagent/llm/client.py:48` depends on `litellm` (not installed, opaque provider errors), with no native Ollama `/api/chat` client.
  2. No health check (`/api/version`, `/api/tags`), no installed-model role resolution, no `OPT_LLM_MODE` (`off` | `assist` | `required`), no context window / truncation detection (`prompt_eval_count`, `done_reason == "length"`), no concurrency semaphore, and no SQLite response cache.

## 3. Existing Baseline Test Status
- `tests/conformance/test_conformance.py`: 16 passed (Python + JS), 2 skipped (C/C++ compiler absent).
- Existing `tests/test_step*.py` + `tests/test_lang_*.py`: 97 passed, 1 pre-existing failure (`test_step9.py::test_regression_suite_correctness_and_false_claims`: `correctness_rate == 0.5`).
- Baseline repair ladder (`repair/baseline_matrix.md`): 4/25 fixtures reached L8 PASS.

## 4. Environment Prerequisites & Safe Degradation
- **Python 3.14.7**: READY (`tree-sitter`, `numpy`, `hypothesis`, `httpx`, `pytest`).
- **JavaScript**: READY via local Node v20.18.0 (`C:\Users\user\.nodejs\node-v20.18.0-win-x64\node.exe`) + `tree-sitter-javascript`.
- **C / C++**: Tree-sitter parsing & static analysis READY; local `gcc`/`clang`/`docker` are absent on this Windows host. All C/C++ unit/codegen/mock-toolchain tests will be verified, and live execution will honestly return `ANALYSIS_ONLY` + `TOOLCHAIN_MISSING` (never silent failure or fake execution).
- **Ollama**: Currently unreachable at `http://localhost:11434`. All Ollama gateway behaviors will be rigorously tested against a local fake HTTP Ollama server (`tests/test_llm_gateway.py`), with live `@pytest.mark.ollama` tests guarded cleanly.

## 5. Phased Repair Sequence
1. **Typed Outcomes, Stage Runner & Triage** (`optagent/core/{outcome,stages,triage}.py`) + `agent.py` integration.
2. **Ollama Core (Workstream E)** (`optagent/llm/{ollama,gateway,health,cache}.py`, `client.py`, `config.py`, `tests/test_llm_gateway.py`).
3. **Heuristic/LLM Separation & Provenance (Workstream D)** (`optagent/core/provenance.py`, `docs/COMPONENT_MAP.md`, `tests/test_component_enforcement.py`).
4. **Python Robustness (Workstream B: B1–B13)** (`static_facts.py`, `inputs.py`, `canon.py`, `batch_harness.py`, `executor.py`, `profiler.py`, `pipeline.py`, `builder.py`).
5. **Multi-Language End-to-End Repair (Workstream C: JS, C, C++)** (`agent.py`, `mutators.py`, `oracle.py`, `static_cost.py`, `profiler.py`, `rungs.py`, `diffcov.py`, `rule_engine.py`, `llm_proposer.py`, `lang/js/`, `lang/native/`).
6. **Final Matrix, Acceptance Suite & Docs** (`tests/test_repair_matrix.py`, `repair/final_matrix.md`, `REPAIR_LOG.md`, `README.md` Troubleshooting).
