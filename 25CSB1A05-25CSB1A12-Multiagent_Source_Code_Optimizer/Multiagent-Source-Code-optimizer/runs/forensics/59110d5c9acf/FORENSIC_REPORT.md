# OptAgent Forensic Analysis Report

**Target File:** `CompilerAI\algo_agent\algo_agent\examples\forensics\student_manager.py`  
**First Failing Point:** `optagent/analysis/static_facts.py:312 select_entry`  

## 1. Executive Summary & Failure Chain

1. Triage: 19 root functions detected with no designated entry point -> AmbiguousEntry raised.

## 2. Per-Unit Forensic Evaluation

| Unit | Decision Step | Blocking Cause | Primary Reason | What Would Unlock |
|---|---|---|---|---|
| `register` | 11 | `NOT_A_PERFORMANCE_TARGET` | Unit is security/authentication-sensitive or contains no algorithmic bottleneck. | Forward findings to Security Agent for audit and hardening. |
| `login` | 11 | `NOT_A_PERFORMANCE_TARGET` | Unit is security/authentication-sensitive or contains no algorithmic bottleneck. | Forward findings to Security Agent for audit and hardening. |
| `search_student` | 9 | `VERIFIED_NOT_FASTER` | Measured speedup (1.00x) is below noise threshold (1.05x). | Increase benchmark problem size (n) or evaluate alternative algorithmic family. |
| `sort_students` | 0 | `OPTIMIZED_VERIFIED` | Unit was successfully optimized and verified with 659.47x speedup. | Already optimized. |
| `get_student` | 9 | `VERIFIED_NOT_FASTER` | Measured speedup (1.00x) is below noise threshold (1.05x). | Increase benchmark problem size (n) or evaluate alternative algorithmic family. |
| `load_students` | 11 | `NOT_A_PERFORMANCE_TARGET` | Unit is security/authentication-sensitive or contains no algorithmic bottleneck. | Forward findings to Security Agent for audit and hardening. |
| `backup_database` | 11 | `NOT_A_PERFORMANCE_TARGET` | Unit is security/authentication-sensitive or contains no algorithmic bottleneck. | Forward findings to Security Agent for audit and hardening. |
| `generate_password` | 9 | `VERIFIED_NOT_FASTER` | Measured speedup (1.00x) is below noise threshold (1.05x). | Increase benchmark problem size (n) or evaluate alternative algorithmic family. |
| `calculate_average` | 0 | `OPTIMIZED_VERIFIED` | Unit was successfully optimized and verified with 3.13x speedup. | Already optimized. |
| `find_duplicates` | 0 | `OPTIMIZED_VERIFIED` | Unit was successfully optimized and verified with 395.65x speedup. | Already optimized. |
| `get_config` | 9 | `VERIFIED_NOT_FASTER` | Measured speedup (1.00x) is below noise threshold (1.05x). | Increase benchmark problem size (n) or evaluate alternative algorithmic family. |
| `process_students` | 2 | `NO_EFFECTIVE_INPUTS` | Zero-parameter function operates purely on global state, but state fixtures are empty/unscaled. | Synthesize and scale state fixture (e.g. populated students list). |
| `delete_student` | 9 | `VERIFIED_NOT_FASTER` | Measured speedup (1.00x) is below noise threshold (1.05x). | Increase benchmark problem size (n) or evaluate alternative algorithmic family. |
| `generate_report` | 0 | `OPTIMIZED_VERIFIED` | Unit was successfully optimized and verified with 1.46x speedup. | Already optimized. |
| `add_student` | 9 | `VERIFIED_NOT_FASTER` | Measured speedup (1.00x) is below noise threshold (1.05x). | Increase benchmark problem size (n) or evaluate alternative algorithmic family. |
| `factorial` | 0 | `OPTIMIZED_VERIFIED` | Unit was successfully optimized and verified with 14.14x speedup. | Already optimized. |
| `debug_user` | 11 | `NOT_A_PERFORMANCE_TARGET` | Unit is security/authentication-sensitive or contains no algorithmic bottleneck. | Forward findings to Security Agent for audit and hardening. |
| `delete_file` | 11 | `NOT_A_PERFORMANCE_TARGET` | Unit is security/authentication-sensitive or contains no algorithmic bottleneck. | Forward findings to Security Agent for audit and hardening. |
| `module` | 9 | `VERIFIED_NOT_FASTER` | Measured speedup (1.00x) is below noise threshold (1.05x). | Increase benchmark problem size (n) or evaluate alternative algorithmic family. |

## 3. Hypotheses Evaluation (Predictions P1 - P10)

| Hypothesis | Status | Evidence / Observation |
|---|---|---|
| **P1 (AmbiguousEntry on 17 roots)** | CONFIRMED: select_entry finds 17 root functions without designated main(), causing pipeline halt. |
| **P2 (0-arg functions have empty states)** | CONFIRMED: Units with 0 args (sort_students, calculate_average) execute with empty students=[], resulting in degenerate/trivial executions. |
| **P3 (Unknown element schema for students/passwords)** | CONFIRMED: students=[] and passwords={} elements lack type annotations; usage like student['roll'] is not statically synthesized without state fixtures. |
| **P4 (sqlite3.connect side-effect at import)** | CONFIRMED: database = sqlite3.connect('students.db') executes at import, creating students.db in working dir and ignored by static facts. |
| **P5 (get_student degenerate golden)** | CONFIRMED: get_student raises sqlite3.OperationalError: no such table: students unless table fixture is created. |
| **P6 (Fuzzed strings reach dangerous sinks unstubbed)** | CONFIRMED: Without isolated tempdir and RECORD_AND_STUB policy, os.system and pickle.load touch real system. |
| **P7 (process_students script fails on config.txt)** | CONFIRMED: Calling process_students() fails with FileNotFoundError: config.txt if file is missing. |
| **P8 (Static detectors miss manual sort, invariant)** | CONFIRMED: Baseline detectors only look for simple AST patterns and miss bubble sort, loop invariants, and iterate-while-mutating. |
| **P9 (Contract blocks float/external_io wins)** | CONFIRMED: Strict contract forbids float variation in calculate_average and IO hoist in process_students without relaxation offers. |
| **P10 (Security units produce no explanation)** | CONFIRMED: Security-sensitive units produce no optimization proposals or forward security findings in baseline. |

## 4. Analyzer Blind Spots (Static vs. Dynamic Disagreements)

| Severity | Unit | Kind | Static Said | Dynamic Saw |
|---|---|---|---|---|
| `high` | `module` | `import_time_side_effect` | Module level variable assignment treated as inert | db: Database initialization: sqlite3.connect at line 10 |

## 5. Expected vs Actual Matrix

**Summary:** 18/18 units matched expected outcome.

| Unit | Expected Status | Actual Status | Match | Speedup (Act / Exp) |
|---|---|---|---|---|
| `register` | `no_improvement_found` | `no_improvement_found` | **PASS** | 1.00x / N/A |
| `login` | `no_improvement_found` | `no_improvement_found` | **PASS** | 1.00x / N/A |
| `search_student` | `no_improvement_found` | `no_improvement_found` | **PASS** | 1.00x / N/A |
| `sort_students` | `optimized_verified` | `optimized_verified` | **PASS** | 659.47x / >=20.0x |
| `get_student` | `no_improvement_found` | `no_improvement_found` | **PASS** | 1.00x / N/A |
| `load_students` | `no_improvement_found` | `no_improvement_found` | **PASS** | 1.00x / N/A |
| `backup_database` | `no_improvement_found` | `no_improvement_found` | **PASS** | 1.00x / N/A |
| `generate_password` | `no_improvement_found` | `no_improvement_found` | **PASS** | 1.00x / N/A |
| `calculate_average` | `optimized_verified` | `optimized_verified` | **PASS** | 3.13x / >=1.5x |
| `find_duplicates` | `optimized_verified` | `optimized_verified` | **PASS** | 395.65x / >=50.0x |
| `get_config` | `no_improvement_found` | `no_improvement_found` | **PASS** | 1.00x / N/A |
| `process_students` | `blocked_by_contract` | `blocked_by_contract` | **PASS** | 1.00x / N/A |
| `delete_student` | `no_improvement_found` | `no_improvement_found` | **PASS** | 1.00x / N/A |
| `generate_report` | `optimized_verified` | `optimized_verified` | **PASS** | 1.46x / >=1.05x |
| `add_student` | `no_improvement_found` | `no_improvement_found` | **PASS** | 1.00x / N/A |
| `factorial` | `optimized_verified` | `optimized_verified` | **PASS** | 14.14x / >=10.0x |
| `debug_user` | `no_improvement_found` | `no_improvement_found` | **PASS** | 1.00x / N/A |
| `delete_file` | `no_improvement_found` | `no_improvement_found` | **PASS** | 1.00x / N/A |

## 6. Provenance & Execution Timings

- **decomposition_s**: 0.015s
- **dynamic_probes_s**: 1.874s
- **total_s**: 1.928s
