# OptAgent Repair Matrix

| Language | Fixture | L0 | L1 | L2 | L3 | L4 | L5 | L6 | L7 | L8 | First Failure Detail |
|---|---|---|---|---|---|---|---|---|---|---|---|
| python | `async_entry.py` | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |  |
| python | `dataclass_args.py` | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |  |
| python | `decorated_cached.py` | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |  |
| python | `deep_recursion.py` | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |  |
| python | `generator_entry.py` | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |  |
| python | `import_side_effects.py` | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |  |
| python | `leetcode_class.py` | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |  |
| python | `multi_function_ambiguous.py` | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |  |
| python | `needs_numpy.py` | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |  |
| python | `no_annotations_complex.py` | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |  |
| python | `simple_fn.py` | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |  |
| python | `slow_heavy.py` | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |  |
| python | `static_and_classmethods.py` | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |  |
| python | `stdin_script.py` | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |  |
| javascript | `async_fn.js` | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |  |
| javascript | `esm_export.mjs` | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |  |
| javascript | `stdin_script.js` | PASS | FAIL | - | - | - | - | - | - | - | `L1`: AmbiguousEntry: Several candidate entry points: []. Pass --entry. |
| javascript | `two_sum.js` | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |  |
| c | `main_only.c` | PASS | FAIL | - | - | - | - | - | - | - | `L1`: AmbiguousEntry: Several candidate entry points: ['main']. Pass --entry. |
| c | `static_fn.c` | PASS | PASS | FAIL | - | - | - | - | - | - | `L2`: Build failed: Compiler not found (gcc): [WinError 2] The system cannot find the file specified |
| c | `sum_overflow.c` | PASS | PASS | FAIL | - | - | - | - | - | - | `L2`: Build failed: Compiler not found (gcc): [WinError 2] The system cannot find the file specified |
| c | `two_sum.c` | PASS | PASS | FAIL | - | - | - | - | - | - | `L2`: Build failed: Compiler not found (gcc): [WinError 2] The system cannot find the file specified |
| cpp | `class_method.cpp` | PASS | PASS | FAIL | - | - | - | - | - | - | `L2`: Build failed: Compiler not found (g++): [WinError 2] The system cannot find the file specified |
| cpp | `dedupe_rank.cpp` | PASS | PASS | FAIL | - | - | - | - | - | - | `L2`: Build failed: Compiler not found (g++): [WinError 2] The system cannot find the file specified |
| cpp | `template_fn.cpp` | PASS | PASS | FAIL | - | - | - | - | - | - | `L2`: Build failed: Compiler not found (g++): [WinError 2] The system cannot find the file specified |

**Summary**: 17/25 fixtures reached L8 PASS.
