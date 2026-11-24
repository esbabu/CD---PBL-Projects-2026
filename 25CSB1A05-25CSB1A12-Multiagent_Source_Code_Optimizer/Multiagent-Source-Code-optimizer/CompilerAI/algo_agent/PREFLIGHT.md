# OptAgent Multi-Language Preflight Report

## 1. Existing Pipeline Status (Steps 1–9)

All Steps 1 through 9 are implemented and verified (67/67 tests passing under `OPT_SANDBOX=local`).

| Step | Status | Primary Module(s) | Key Symbols / Hook Points |
|---|---|---|---|
| **Step 1: Intent Extraction** | Implemented | `optagent/intent/pipeline.py`, `optagent/analysis/static_facts.py`, `optagent/analysis/inputs.py`, `optagent/intent/contract.py`, `optagent/llm/prompts.py` | `IntentExtractor` (`run`), `analyze_source`, `select_entry`, `annotation_inputs`, `build_contract`, `reconcile_spec`, `IntentBundle`, `ModuleFacts`, `FunctionFacts`, `Aspect`, `PreservationItem`, `Constraints`, `ExecRecord` |
| **Step 2: Oracle & Sandbox** | Implemented | `optagent/runtime/sandbox.py`, `optagent/runtime/canon.py`, `optagent/oracle/builder.py`, `optagent/oracle/oracle.py`, `optagent/oracle/compare.py`, `optagent/oracle/golden.py`, `optagent/oracle/mutation.py`, `optagent/oracle/schemas.py` | `Sandbox` (`run`, `run_batch`, `_spawn`, `_watch`), `RunOpts`, `OracleBuilder` (`build`), `Oracle` (`load`, `check`, `check_scale`, `_static`, `_path_for`, `_run`, `_judge`, `_fresh_cases`, `_shrink`), `source_sha`, `Comparator` (`compare`, `compare_scale`), `make_golden`, `MutationTester`, `SurvivorHunter`, `Case`, `CaseResult`, `GoldenRecord`, `OracleBundle` |
| **Step 3: Complexity Analyzer** | Implemented | `optagent/complexity/analyzer.py`, `optagent/complexity/static_cost.py`, `optagent/complexity/empirical.py`, `optagent/complexity/profiler.py`, `optagent/complexity/reconcile.py` | `Analyzer` (`analyze`), `StaticCostAnalyzer` (`CALL_COSTS`, `analyze_function`), `Profiler` (`profile`), `ProfileSandbox` (`run_profile_batch`), `fit_scaling_data`, `reconcile_complexity` |
| **Step 4: Candidate Proposers** | Implemented | `optagent/proposers/ensemble.py`, `optagent/proposers/rule_engine.py`, `optagent/proposers/llm_proposer.py`, `optagent/proposers/retrieval.py`, `optagent/proposers/kb/catalog.py` | `ProposerEnsemble` (`propose_candidates`), `RuleEngine` (`propose`), `RuleCatalog` (`load`, `filter_applicable`), `RuleRetriever`, `LLMProposer`, `Candidate` |
| **Step 5: Verification Ladder** | Implemented | `optagent/verify/ladder.py`, `optagent/verify/rungs.py`, `optagent/verify/diffcov.py`, `optagent/verify/schemas.py` | `Ladder` (`verify`), `run_r1_compile_lint`, `run_r2_golden_holdout`, `run_r3_properties`, `run_r4_differential_fuzz`, `run_r5_diffcov`, `run_r6_symbolic`, `run_r7_formal`, `run_r8_llm_reviewer`, `Evidence`, `RungResult` |
| **Step 6: Benchmarking & Search** | Implemented | `optagent/bench/runner.py`, `optagent/bench/stats.py`, `optagent/search/controller.py` | `BenchmarkRunner` (`run`), `SearchController` (`run`), `SearchBudget`, `SearchResult`, `BenchmarkResult` |
| **Step 7: Reporting & Memory** | Implemented | `optagent/report/builder.py`, `optagent/report/render.py`, `optagent/report/schemas.py`, `optagent/memory/store.py` | `ReportBuilder` (`build`), `render_markdown`, `render_json`, `Report`, `MemoryStore` |
| **Step 8: Facade & Service API** | Implemented | `optagent/agent.py`, `optagent/service/app.py`, `optagent/cli.py`, `optagent/cli_oracle.py`, `optagent/cli_complexity.py`, `optagent/cli_proposers.py`, `optagent/cli_verify.py`, `optagent/cli_search.py`, `optagent/cli_eval.py` | `OptimizerAgent` (`run`), `OptimizeRequest`, `OptimizeResult`, FastAPI `app` (`/optimize`, `/runs/{sha}`, `/runs/{sha}/events`, `/runs/{sha}/override`) |
| **Step 9: Evaluation & Self-Improve** | Implemented | `optagent/eval/harness.py`, `optagent/eval/ablation.py`, `optagent/eval/self_improve.py` | `EvalHarness`, `PreferenceHarvester` |

## 2. Exact Hook Points & Compatibility Patches (P1–P7)

All language-specific logic will live under `optagent/lang/`, `optagent/runtime/js/`, `optagent/runtime/native/`, and `docker/`. Existing files receive only the additive, backward-compatible patches P1–P7:

- **P1 (`optagent/schemas.py`):** Add `IntentBundle.language: str = "python"`, `FunctionFacts.extra: dict[str, Any] = {}`, and new `Aspect` enum members (`MEMORY_SAFETY`, `UNDEFINED_BEHAVIOR`, `INTEGER_SEMANTICS`, `ABI_SIGNATURE`, `RESOURCE_OWNERSHIP`, `ERRNO_STATE`, `THREAD_SAFETY`, `ASYNC_SEMANTICS`, `KEY_ENUMERATION_ORDER`, `PROTOTYPE_STATE`).
- **P2 (`optagent/oracle/schemas.py`):** Add `OracleBundle.language: str = "python"` and `CaseResult` optional fields `sanitizer: str | None = None`, `signal: str | None = None`, `build_log: str | None = None`.
- **P3 (`optagent/runtime/sandbox.py`):** Introduce `SandboxProfile` dataclass and `PYTHON_PROFILE` constant; extend `Sandbox(s, backend=None, profile=PYTHON_PROFILE)` with an optional build phase before the case loop, Docker enforcement for native profiles (`allow_local_native`), and `load_error` synthesis on build failure.
- **P4 (`optagent/oracle/compare.py`):** Handle `CaseResult.sanitizer` and `CaseResult.signal` plus new language aspects (`memory_safety`, `undefined_behavior`, `integer_semantics`, `async_semantics`, `key_enumeration_order`, `prototype_state`, `errno_state`, `thread_safety`, `abi_signature`, `resource_ownership`) when MUST; unchanged when fields are `None`.
- **P5 (`optagent/config.py`):** Append multi-language settings (`js_docker_image`, `native_docker_image`, `compile_timeout_s`, `c_flags`, `cpp_flags`, `allow_local_native`, `cbmc_unwind`, `enable_cbmc`, `enable_sanitizers`).
- **P6 (`optagent/intent/pipeline.py`, `optagent/oracle/builder.py`, `optagent/oracle/oracle.py`):** Accept optional `adapter=None` constructor argument (default path remains byte-for-byte Python behavior). Inject adapter hooks for: `analyze`, `select_entry`, `seed_inputs`, sandbox-based golden seeds for foreign languages, `prompt_pack`, `contract_rules`, `param_schema`, `executable_lines`, `mutation_ops`, `normalize_result`, and `sandbox_profile`.
- **P7 (`optagent/oracle/oracle.py`):** Update `source_sha(source: str, language: str = "python") -> str`: Python uses `sha256(source)[:12]` unchanged; other languages use `sha256(f"{language}\0{source}")[:12]`.

## 3. Host Environment Check

- **Python 3.14 (`py -3.14`):** Prebuilt binary wheels available for `tree-sitter`, `tree-sitter-c`, `tree-sitter-cpp`, `tree-sitter-javascript`, `jinja2`, `pyyaml`, and all OptAgent dependencies.
- **Python 3.15 (`python`):** All core OptAgent deps installed (67/67 existing tests pass).
- **External toolchains on host PATH:** `node`, `clang`, `gcc`, `docker`, `cbmc` are not pre-installed on this host PATH. Dockerfiles (`docker/sandbox-js.Dockerfile`, `docker/sandbox-native.Dockerfile`) are provided for containerized execution, and local fallback paths are guarded properly (`OPT_ALLOW_LOCAL_NATIVE=1` required for local native runs).

## 4. Phased Build Order

1. **Phase 0:** `optagent/lang/` abstraction (`base.py`, `registry.py`, `detect.py`, `python_adapter.py`), patches P1–P7, `--lang` CLI flag, `tests/test_lang_registry.py`, `tests/test_lang_compat.py`.
2. **Phase 1:** Tree-sitter engine (`optagent/lang/treesitter/`), JavaScript adapter (`optagent/lang/js/`), JS runtime harness (`optagent/runtime/js/`), `docker/sandbox-js.Dockerfile`, `examples/js/`, `tests/test_lang_js.py`.
3. **Phase 2:** C adapter & shared native infrastructure (`optagent/lang/native/`, `optagent/runtime/native/harness_common.h`, vendored cJSON, `docker/sandbox-native.Dockerfile`, `examples/c/`, `tests/test_lang_c.py`).
4. **Phase 3:** C++ adapter (`adapter_cpp.py`, `driver.cpp.j2`, STL marshalling, exceptions, overloads/templates, normalization, vendored nlohmann/json, `examples/cpp/`, `tests/test_lang_cpp.py`).
5. **Phase 4:** Steps 3–7 integration per language (cost tables, rule packs, prompt packs, verification rungs incl. sanitizers & CBMC, bench profiles, report fields, agent facade multi-lang support).
6. **Phase 5:** Security profiles, FastAPI service/UI language metadata & language-specific contract aspects.
