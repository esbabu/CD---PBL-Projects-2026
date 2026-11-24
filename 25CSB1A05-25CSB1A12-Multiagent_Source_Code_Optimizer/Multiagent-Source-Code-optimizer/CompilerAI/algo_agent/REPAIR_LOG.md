# OptAgent Repair Log

Chronological log of reproduced defects, root causes, fixes, verification tests, and edited files across Workstreams A–E (Defects D1–D4).

---

## Phase 0 — Reproduction Harness & Baseline

- **Doctor (`optagent/doctor.py`)**: Implemented `python -m optagent.doctor` emitting machine-readable `runs/doctor.json` and CLI readiness table. Verified Python 3.14.7 READY, Node.js v20.18.0 READY (including `~/.nodejs/...` auto-discovery on Windows), Tree-sitter 0.26.1 (`c`, `cpp`, `javascript` grammars loaded), `clang`/`clang++`/`gcc`/`g++`/`docker` absent on host, Ollama unreachable at `http://localhost:11434`.
- **Fixtures (`examples/repair/{python,js,c,cpp}/`)**: Created all 35 fixtures covering 14 Python patterns (plus `_right`/`_wrong` pairs), 4 JS fixtures (plus `_right`/`_wrong`), 4 C fixtures (plus `_right`/`_wrong`), and 3 C++ fixtures (plus `_right`/`_wrong`).
- **Conformance Suite (`tests/conformance/`)**: Created `spec.json`, `impl.py`, `impl.js`, `impl.c`, `impl.cpp`, and `test_conformance.py`. Baseline: 16 passed (Python + JS), 2 skipped (C/C++ compiler absent).
- **Baseline Matrix (`repair/baseline_matrix.md`)**: Captured unmodified baseline — only 4/25 fixtures reached L8 PASS (`simple_fn.py`, `no_annotations_complex.py`, `needs_numpy.py`, `multi_function_ambiguous.py`).
- **Baseline Existing Tests**: 97 passed, 1 pre-existing failure (`tests/test_step9.py::test_regression_suite_correctness_and_false_claims`).

---

## Workstream A — Typed Outcomes, Stage Isolation, Triage & Provenance

- **Bug A1: Silent denial / raw tracebacks on unsupported or failing inputs**
  - **Symptom**: Unsupported inputs, missing dependencies, or stage errors returned vague `status="error"` strings or crashed with raw exceptions; unverified paths risked being misread as verified optimizations.
  - **Root Cause**: No typed `OptimizeOutcome`, `SupportLevel`, `ReasonCode`, or stage isolation wrapper existed in `OptimizerAgent.run()`.
  - **Fix**: Created `optagent/core/outcome.py` (`SupportLevel`, `ReasonCode` [19 codes], `REASON_REMEDIATION`, `Reason`, `StageResult`, `OptimizeOutcome`), `optagent/core/stages.py` (`StageRunner` persisting stage tracebacks to `runs/<sha>/diagnostics.json`), `optagent/core/triage.py` (`run_triage` pre-flight check), and `optagent/core/provenance.py` (`@component`, `ProvenanceTracker`). Wired all of these into `optagent/agent.py` with explicit `ANALYSIS_ONLY` (`T0`, `unverified=True`) and `VERIFIED_WEAK` (`low_confidence=True`) paths.
  - **Tests**: `tests/test_repair_matrix.py::test_stage_exception_isolated_and_persisted_to_diagnostics_json`, `test_native_and_script_degraded_outcomes_never_crash`.
  - **Files**: `optagent/core/{__init__,outcome,stages,triage,provenance}.py`, `optagent/agent.py`, `README.md` (generated Troubleshooting section).

---

## Workstream B — Complex & Unusual Python Robustness (Defect D2)

- **Bug B1: `profiler.py` crashed on scalar/non-scaling Python functions (and broke `test_step9.py`)**
  - **Symptom**: `decorated_cached.py`, `deep_recursion.py`, `slow_heavy.py`, and `tests/test_step9.py::test_regression_suite_correctness_and_false_claims` crashed in `EmpiricalProfiler.profile()` with `AttributeError: 'str' object has no attribute 'size'`.
  - **Root Cause**: `oracle.cases` is a `dict[str, Case]`, not a `list[Case]`; `optagent/complexity/profiler.py` iterated `for c in oracle.cases` directly, yielding string keys.
  - **Fix**: Updated `optagent/complexity/profiler.py` to iterate `oracle.cases.values()` and guard non-Python / `__script__` runs cleanly.
  - **Tests**: `tests/test_step9.py` (now 17/17 passed), `tests/test_repair_matrix.py` (`decorated_cached.py`, `deep_recursion.py`, `slow_heavy.py`).
  - **Files**: `optagent/complexity/profiler.py`.

- **Bug B2: Class methods (`Class.method`), `@staticmethod`, `@classmethod`, `@property` denied or crashed**
  - **Symptom**: `leetcode_class.py` and `static_and_classmethods.py` failed at L1/L3 (`no entry function found`, or harness could not bind `self`/`cls`).
  - **Root Cause**: `static_facts.py` only extracted top-level functions; `batch_harness.py` and `harness.py` only looked up `getattr(mod, entry)` and never instantiated classes; `oracle.py`, `builder.py`, `rungs.py`, `static_cost.py`, and `llm_proposer.py` did not recognize `Class.method` syntax.
  - **Fix**: Extended `optagent/analysis/static_facts.py` to extract class methods (`Class.method`) with `is_method`, `is_staticmethod`, `is_classmethod`, `is_property`, and `class_fields`; added `Aspect.SELF_STATE` to `optagent/schemas.py`; updated `batch_harness.py` & `harness.py` to construct a fresh class instance per test case and record `mut["self"]`; updated `oracle.py`, `builder.py`, `rungs.py`, `static_cost.py`, `llm_proposer.py`, and `intent/pipeline.py` (with `applicable=True` on `PreservationItem`).
  - **Tests**: `tests/test_repair_matrix.py::test_python_class_methods_right_passes_wrong_fails[leetcode_class|static_and_classmethods]`.
  - **Files**: `optagent/schemas.py`, `optagent/analysis/static_facts.py`, `optagent/runtime/{batch_harness,harness}.py`, `optagent/oracle/{oracle,builder}.py`, `optagent/verify/rungs.py`, `optagent/complexity/static_cost.py`, `optagent/proposers/llm_proposer.py`, `optagent/intent/pipeline.py`.

- **Bug B3: Top-level / stdin scripts (`stdin_script.py`) denied as having no function**
  - **Symptom**: `stdin_script.py` failed with `no function found` and crashed in `IntentExtractor` / `OracleBuilder`.
  - **Root Cause**: No `__script__` execution mode existed; `IntentExtractor` rejected modules without functions; `OracleBuilder` tried to run `Gen`/`Hypothesis`/`mutate_args` on script inputs; `PythonAdapter.program_mode` was `False`.
  - **Fix**: Enabled `program_mode=True` in `optagent/lang/python_adapter.py`; added `__script__` execution mode (stdin/argv/stdout/`SystemExit` capture) in `batch_harness.py` & `harness.py`; implemented `infer_stdin_seeds()` in `optagent/analysis/inputs.py`; handled `__script__` (`params=[]`) in `intent/pipeline.py`, `oracle/oracle.py`, `oracle/builder.py`, `verify/rungs.py`, and `bench/runner.py`.
  - **Tests**: `tests/test_repair_matrix.py::test_python_stdin_script_mode`.
  - **Files**: `optagent/lang/python_adapter.py`, `optagent/analysis/inputs.py`, `optagent/runtime/{batch_harness,harness}.py`, `optagent/intent/pipeline.py`, `optagent/oracle/{oracle,builder}.py`, `optagent/verify/rungs.py`, `optagent/bench/runner.py`.

- **Bug B4: Async functions, generators, dataclasses, numpy arrays, `@lru_cache`, deep recursion, import side effects, slow functions, ambiguous entries, missing deps**
  - **Symptom**: `async_entry.py` was explicitly refused in `intent/pipeline.py`; `dataclass_args.py` failed canonical serialization/reconstruction; `decorated_cached.py` leaked `@lru_cache` state across cases; `import_side_effects.py` hung or leaked stdout on import; `slow_heavy.py` hit rigid 1s timeouts; `needs_nonexistent_pkg.py` crashed instead of returning `MISSING_DEPENDENCY`.
  - **Root Cause**: Missing runtime & canonicalization support across `canon.py`, `batch_harness.py`, `inputs.py`, `builder.py`, `triage.py`, and `static_facts.py`.
  - **Fix**:
    - `optagent/runtime/canon.py`: Added structural `__obj__` (dataclasses/namedtuples/custom objects with namespace re-instantiation), `__ndarray__` support, and memory-address normalization (`0x...`).
    - `optagent/runtime/{batch_harness,harness}.py`: Added `asyncio.run` for coroutines, `cache_clear()` for `@lru_cache`, `sys.setrecursionlimit`, import-time `input()` blocking, and `canon.decode(..., mod.__dict__)`.
    - `optagent/analysis/inputs.py`: Implemented 7-step deterministic `heuristic_seed_inputs()` (type annotations incl. dataclasses, defaults, doctests, call sites, usage-based AST inference, stdin grammar inference, boundary pack).
    - `optagent/oracle/builder.py`: Added adaptive timeout calibration based on seed execution times (up to 60s).
    - `optagent/analysis/static_facts.py`: Added `rank_entries()` heuristic scoring for ambiguous multi-function files.
    - `optagent/core/triage.py`: Pre-flight import probe returning `ANALYSIS_ONLY` + `MISSING_DEPENDENCY` with exact remediation when an imported package is absent.
  - **Tests**: All 15 Python tests in `tests/test_repair_matrix.py`.
  - **Files**: `optagent/runtime/{canon,batch_harness,harness}.py`, `optagent/analysis/{inputs,static_facts}.py`, `optagent/oracle/builder.py`, `optagent/intent/pipeline.py`, `optagent/core/triage.py`.

---

## Workstream C — Multi-Language End-to-End Execution: C, C++, JavaScript (Defect D1)

- **Bug C1: JavaScript/C/C++ failed across Oracle, Mutation, Profiler, Benchmarker, and Proposer**
  - **Symptom**: `two_sum.js`, `esm_export.mjs`, `async_fn.js` crashed at L6/L7/L8 with `SyntaxError` in `mutators.py`, `FileNotFoundError` for `mutant_1.js`, Python `ProfileSandbox` errors, and `ast.parse` failures in `llm_proposer.py`. C/C++ crashed when compilers were missing instead of degrading cleanly.
  - **Root Cause**:
    1. `OptimizerAgent.run()` never passed `adapter` into `OracleBuilder` / `Oracle`.
    2. `optagent/oracle/mutators.py:build_pool()` called Python `ast.parse(source)` directly on JS/C/C++ source.
    3. `optagent/oracle/mutation.py` hardcoded `mutant_{m['id']}.py` while `optagent/oracle/builder.py` looked for `.py` (and later `mut_ext`).
    4. `optagent/bench/runner.py` invoked Python `ProfileSandbox` for non-Python languages.
    5. `optagent/proposers/llm_proposer.py` validated candidate syntax with Python `ast.parse`.
    6. `optagent/lang/js/adapter.py` failed to locate Node.js when installed under `~/.nodejs/...` outside global `PATH`.
    7. `optagent/core/triage.py` checked `is_template` instead of `template_params` from `adapter_cpp.py`.
  - **Fix**: Propagated `adapter` through every stage of `agent.py`; added regex literal fallback in `mutators.py`; respected `self._ext` in both `mutation.py` and `builder.py`; guarded Python-only profiler/benchmarker/static_cost logic for foreign languages; updated `llm_proposer.py` to validate via language adapter; added Windows `~/.nodejs` discovery in `js/adapter.py`, `doctor.py`, and `triage.py`; fixed `template_params` check in `triage.py`; ensured missing C/C++ toolchains and unsupported entry kinds (`main_only.c`, `template_fn.cpp`, `stdin_script.js`) return `ANALYSIS_ONLY` (`T0`, `unverified=True`) with exact reason codes (`TOOLCHAIN_MISSING` / `UNSUPPORTED_ENTRY_KIND`).
  - **Tests**: `tests/conformance/test_conformance.py` (16 passed, 2 skipped), `tests/test_repair_matrix.py` (all 4 JS tests + all 8 C/C++/JS degraded outcome tests).
  - **Files**: `optagent/agent.py`, `optagent/oracle/{mutators,mutation,builder,oracle}.py`, `optagent/bench/runner.py`, `optagent/complexity/{profiler,static_cost}.py`, `optagent/proposers/llm_proposer.py`, `optagent/lang/js/adapter.py`, `optagent/core/triage.py`.

---

## Workstream D — Heuristic vs LLM Separation & Enforcement (Defect D3)

- **Bug D1: Heuristic and LLM responsibilities were entangled; LLM failures crashed deterministic stages**
  - **Symptom**: Missing/unreachable LLM crashed `IntentExtractor` and `OracleBuilder`; no provenance recorded which components used heuristics vs LLM vs tools; no guardrail prevented HTTP/LLM calls outside `optagent/llm/`.
  - **Root Cause**: `intent/pipeline.py`, `oracle/builder.py`, and `llm/client.py` lacked `@component` classification, provenance tracking, and deterministic template fallbacks.
  - **Fix**: Created `@component(kind=HEURISTIC|TOOL|LLM|HYBRID, llm_fallback=...)` and `ProvenanceTracker` in `optagent/core/provenance.py`; decorated pipeline components; added deterministic template spec fallback in `intent/pipeline.py`; guarded LLM calls in `oracle/builder.py`; generated `docs/COMPONENT_MAP.md`; enforced zero HTTP/LLM imports outside `optagent/llm/` and zero network calls under `LLM_MODE=off` via AST & monkeypatched-socket tests.
  - **Tests**: `tests/test_component_enforcement.py` (4/4 passed).
  - **Files**: `optagent/core/provenance.py`, `optagent/intent/pipeline.py`, `optagent/oracle/builder.py`, `optagent/agent.py`, `docs/COMPONENT_MAP.md`, `tests/test_component_enforcement.py`.

---

## Workstream E — Native Ollama Gateway & Reliability (Defect D4)

- **Bug E1: Unreliable LLM access via `litellm` with no health check, role resolution, schema inlining, truncation detection, or caching**
  - **Symptom**: `litellm` caused opaque errors against Ollama, sent un-inlined `$defs` JSON schemas causing HTTP 400s, had no health cache, no concurrency control, no context truncation check, and no offline cache.
  - **Root Cause**: `optagent/llm/client.py` depended directly on `litellm` and made raw uncached calls.
  - **Fix**: Removed `litellm` completely; built native `httpx` Ollama layer:
    - `optagent/llm/ollama.py`: Native `/api/tags`, `/api/show`, `/api/chat` client with `$defs` inlining, HTTP 400 fallback to `format="json"`, `done_reason=="length"` truncation detection, and context window inspection.
    - `optagent/llm/health.py`: Cached health probe (`~30s` TTL) + role-to-model resolution (`proposer`/`judge` -> `coder`/`general` families) against locally installed models only (never installs/pulls/starts Ollama).
    - `optagent/llm/cache.py`: Persistent SQLite response cache (`runs/.llm_cache.db`).
    - `optagent/llm/gateway.py`: Single `OllamaGateway` enforcing `off`/`assist`/`required` modes, semaphore concurrency control, retries, and provenance/token recording.
    - `optagent/llm/client.py`: Thin compatibility wrapper delegating all calls to `OllamaGateway`.
  - **Tests**: `tests/test_llm_gateway.py` (10 passed against fake local HTTP Ollama server, 1 `@pytest.mark.ollama` live test skipped because Ollama is not running on host).
  - **Files**: `optagent/config.py`, `optagent/llm/{ollama,health,cache,gateway,client}.py`, `repair/llm_audit.md`, `tests/test_llm_gateway.py`.

---

## CompilerAI Backend Integration Alignment

- **Fix**: Updated `backend/app/agents/optimization/adapter.py` to normalize `javascript`/`js`/`c++` extensions, map `InferenceMode` to `llm_mode` (`"assist"` vs `"off"`), and propagate `OptimizeOutcome` (`support_level`, `unverified`, `reasons`, `provenance`, `strategy`) into `OptimizationResult` (`metrics`, `raw_result`, `diagnostics`), ensuring `ANALYSIS_ONLY` outputs are reported truthfully as unverified static analysis. Added `"javascript"`/`"js"` to `backend/app/orchestration/orchestrator.py` and `backend/app/api/routes_health.py`.
- **Files**: `backend/app/agents/optimization/adapter.py`, `backend/app/orchestration/orchestrator.py`, `backend/app/api/routes_health.py`.
