# OptAgent: Autonomous Algorithm Optimization Agent

OptAgent is an agentic system that takes Python code and returns the **most efficient equivalent algorithm** (lower time and/or space complexity) while **strictly preserving behavior**.

## Pipeline Architecture
`Source -> IntentBundle (Step 1) -> OracleBundle (Step 2) -> AnalysisBundle (Step 3) -> Candidate Ensemble (Step 4) -> Verification Ladder (Step 5) -> Benchmarking & Search (Step 6) -> Reporting & Memory (Step 7) -> Agent Facade & Service API (Step 8) -> Evaluation & Self-Improvement (Step 9)`

---

## Step 9: Evaluation Harness and Self-Improvement

Step 9 provides a comprehensive evaluation harness, benchmark adapters, ablation studies, and self-improvement preference data generation.

### Key Components in `optagent/eval/`
1. **Benchmark Adapters (`adapter.py`)**:
   - **PIE**: `load_pie_dataset(path)` converts Python Code Optimization tasks into `TaskSpec` models with test case overrides.
   - **EffiBench**: `load_effibench_dataset(path)` loads LLM code efficiency problems.
   - **Mercury**: `load_mercury_dataset(path)` imports competitive programming tasks with time/memory limits.
   - **ECCO**: `load_ecco_dataset(path)` loads empirical code complexity benchmarks.
   - **Auto-Detection**: `load_benchmark_dataset(path)` automatically detects benchmark schema.
2. **Metrics & Statistical Distributions (`metrics.py`, `schemas.py`)**:
   - Ground-truth correctness rate (100% required via Oracle and Ladder).
   - Speedup distribution percentiles (Min, P25, Median/P50, P75, P90, Max, Geometric Mean).
   - Memory ratio distribution percentiles.
   - Asymptotic complexity improvement tracking (e.g. $O(n^2) \rightarrow O(n \log n)$).
   - False-claim rate (optimizations claiming speedup/correctness that fail ground-truth tests).
   - Program optimization costs (exploration iterations, execution time, LLM calls, token usage).
3. **Ablation Studies (`ablation.py`)**:
   - **Proposer Ablations**: baseline vs. rules-only (deterministic CST) vs. no-memory.
   - **Verifier Rung Ablations**: baseline vs. no-diffcov (R5 disabled) vs. no-differential-fuzz (R4 disabled) vs. golden-only (R2 only).
   - Computes relative delta in correctness rate ($\Delta C$) and average speedup ($\Delta S$).
4. **Self-Improvement (`self_improve.py`)**:
   - `PreferenceHarvester` extracts pairwise trajectories $(x, y_{\text{chosen}}, y_{\text{rejected}})$ comparing verified winning candidates against failed or suboptimal candidates.
   - Grounded reward calculated from verification tier ($T_1 \dots T_4$) and speedup.
   - `export_dpo_jsonl` writes datasets ready for DPO / RLHF fine-tuning.
5. **Permanent Regression Suite**:
   - `EvalHarness.get_regression_suite()` runs `slow_two_sum.py` and `dedupe_rank.py` as permanent regressions, ensuring 100% correctness and 0% false claims.

---

## Installation & Setup

```bash
# Core dependencies
pip install pydantic rich hypothesis libcst numpy scipy sympy fastapi sse-starlette

# Optional dependencies
pip install litellm sentence-transformers faiss-cpu
```

---

## Running Step 9 Evaluation

### 1. Run Permanent Regression Suite
```bash
python -m optagent.cli eval --regression
```
Or via standalone entry point:
```bash
python -m optagent.cli_eval --regression
```

### 2. Run on Benchmarks (PIE, EffiBench, Mercury, ECCO)
```bash
python -m optagent.cli eval --dataset examples/benchmarks/pie_sample.json --benchmark pie
python -m optagent.cli eval --dataset examples/benchmarks/effibench_sample.json --benchmark effibench
python -m optagent.cli eval --dataset examples/benchmarks/mercury_sample.json --benchmark mercury
python -m optagent.cli eval --dataset examples/benchmarks/ecco_sample.json --benchmark ecco
```

### 3. Run Ablation Study
```bash
python -m optagent.cli eval --regression --ablate
```

### 4. Export DPO Preference Dataset
```bash
python -m optagent.cli eval --regression --export-dpo runs/eval/dpo_preferences.jsonl
```

### 5. Save Artifacts (JSON & Markdown)
```bash
python -m optagent.cli eval --regression --output runs/eval/eval_report.json --markdown runs/eval/eval_report.md
```

---

## Expected Output

```
                   Evaluation Suite: Tasks Breakdown                    
┏━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━┓
┃ Task Name     ┃ Benchmark  ┃ Verified ┃ Tier ┃ Speedup ┃ Mem Ratio ┃ Asymptotic ┃ Time (s) ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━┩
│ slow_two_sum  │ regression │ YES      │ T2   │   3.73x │     1.00x │ YES        │     8.85 │
│ dedupe_rank   │ regression │ YES      │ T2   │   2.27x │     1.00x │ NO         │    14.93 │
└───────────────┴────────────┴──────────┴──────┴─────────┴───────────┴────────────┴──────────┘
             Speedup & Resource Distribution             
┏━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━┳━━━━━━━┳━━━━━━━━━━━┓
┃ Metric      ┃   Min ┃   P25 ┃ Median(P50) ┃   P75 ┃   P90 ┃   Max ┃ Geom Mean ┃
┡━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━╇━━━━━━━╇━━━━━━━━━━━┩
│ Speedup (x) │ 2.27x │ 2.64x │       3.00x │ 3.37x │ 3.59x │ 3.73x │     2.91x │
│ Mem Ratio   │ 1.00x │ 1.00x │       1.00x │ 1.00x │ 1.00x │ 1.00x │     1.00x │
└─────────────┴───────┴───────┴─────────────┴───────┴───────┴───────┴───────────┘
╭────────────────────────────── Step 9 Evaluation Summary ──────────────────────────────╮
│ Total Tasks: 2                                                                        │
│ Correctness Rate: 100.0% (Ground-truth gate: 100%)                                    │
│ Average Speedup: 2.91x                                                                │
│ Asymptotic Improvement Rate: 50.0%                                                    │
│ False-Claim Rate: 0.0% (Target: 0.0%)                                                 │
│ Total Elapsed Time: 23.86s                                                            │
╰───────────────────────────────────────────────────────────────────────────────────────╯
```

---

## Running Tests
Run the entire suite without LLM and using the local sandbox:
```bash
OPT_SANDBOX=local pytest -q
```
All 67 tests across Steps 1 to 9 pass cleanly.

---

## Troubleshooting (Reason Codes & Remediation)

Generated from `optagent.core.outcome.REASON_REMEDIATION`.

| Reason Code | Remediation |
|---|---|
| `SYNTAX_ERROR` | Fix syntax errors in the source code before running optimization. |
| `NO_ENTRY_FOUND` | Define a callable function/method or provide a runnable stdin/stdout script. |
| `ENTRY_AUTO_SELECTED` | Pass `--entry <name>` or `entry` in the request to choose a different entry point. |
| `UNSUPPORTED_ENTRY_KIND` | Wrap core logic in a callable function or provide `hints` (e.g., `hints.instantiate` for templates). |
| `MISSING_DEPENDENCY` | Install the missing package in the configured sandbox image or configure `OPT_PY_IMAGES`. |
| `IMPORT_SIDE_EFFECT` | Move top-level I/O or heavy initialization inside `if __name__ == '__main__':`. |
| `NO_SEED_INPUTS` | Add type annotations, default arguments, a docstring example, or pass explicit `inputs` in overrides. |
| `ORIGINAL_TIMEOUT` | Supply smaller seed inputs or increase `case_timeout_s` so baseline cases finish cleanly. |
| `ORIGINAL_CRASH` | Ensure the original implementation succeeds on at least one valid input without crashing. |
| `UNSERIALIZABLE_ARGS` | Use JSON/primitive/dataclass/namedtuple arguments or supply `hints.ctor_args`. |
| `SANDBOX_UNAVAILABLE` | Start Docker or set `OPT_SANDBOX=local` (for Python/JS) to enable sandbox execution. |
| `TOOLCHAIN_MISSING` | Install the required compiler/runtime (node, clang/gcc) or build the corresponding image under `docker/`. |
| `BUILD_FAILED` | Check the compiler diagnostic log in `diagnostics.json` and fix missing headers or flags. |
| `LLM_UNAVAILABLE` | Start Ollama at the configured `OPT_API_BASE` URL and verify installed models with `python -m optagent.doctor`, or run with `OPT_LLM_MODE=off`. |
| `LLM_INVALID_OUTPUT` | The model returned malformed JSON or schema-invalid output; deterministic heuristic fallbacks were used. |
| `ORACLE_WEAK` | Add richer seed inputs or pass `accept_low_confidence=True` to accept candidates verified on a weak oracle (Tier C/D). |
| `LANGUAGE_UNSUPPORTED` | Use one of the supported languages: python, javascript, c, cpp. |
| `STAGE_ERROR` | Inspect `runs/<sha>/diagnostics.json` for the full stage exception trace. |
| `INPUT_TOO_LARGE` | Reduce source size below the configured limit or split the target function into a smaller module. |
