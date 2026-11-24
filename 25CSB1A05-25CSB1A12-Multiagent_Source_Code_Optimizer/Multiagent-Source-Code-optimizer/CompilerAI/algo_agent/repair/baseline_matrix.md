# OptAgent Repair Matrix

| Language | Fixture | L0 | L1 | L2 | L3 | L4 | L5 | L6 | L7 | L8 | First Failure Detail |
|---|---|---|---|---|---|---|---|---|---|---|---|
| python | `async_entry.py` | PASS | PASS | PASS | PASS | PASS | FAIL | - | - | - | `L5`: IntentError: async entry points are not supported yet |
| python | `dataclass_args.py` | PASS | PASS | PASS | FAIL | - | - | - | - | - | `L3`: No smoke cases could be constructed |
| python | `decorated_cached.py` | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | FAIL | `L8`: AttributeError: 'str' object has no attribute 'kind' |
| python | `deep_recursion.py` | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | FAIL | `L8`: AttributeError: 'str' object has no attribute 'kind' |
| python | `generator_entry.py` | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |  |
| python | `import_side_effects.py` | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |  |
| python | `leetcode_class.py` | PASS | FAIL | - | - | - | - | - | - | - | `L1`: AmbiguousEntry: Several candidate entry points: []. Pass --entry. |
| python | `multi_function_ambiguous.py` | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |  |
| python | `needs_numpy.py` | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |  |
| python | `no_annotations_complex.py` | PASS | PASS | PASS | FAIL | - | - | - | - | - | `L3`: No smoke cases could be constructed |
| python | `simple_fn.py` | PASS | PASS | PASS | PASS | PASS | PASS | PASS | FAIL | - | `L7`: AttributeError: 'Verdict' object has no attribute 'counterexample' |
| python | `slow_heavy.py` | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | FAIL | `L8`: AttributeError: 'str' object has no attribute 'kind' |
| python | `static_and_classmethods.py` | PASS | FAIL | - | - | - | - | - | - | - | `L1`: AmbiguousEntry: Several candidate entry points: []. Pass --entry. |
| python | `stdin_script.py` | PASS | FAIL | - | - | - | - | - | - | - | `L1`: AmbiguousEntry: Several candidate entry points: []. Pass --entry. |
| javascript | `async_fn.js` | PASS | PASS | PASS | PASS | PASS | PASS | FAIL | - | - | `L6`: SyntaxError: invalid syntax (<unknown>, line 1) |
| javascript | `esm_export.mjs` | PASS | PASS | PASS | PASS | PASS | PASS | FAIL | - | - | `L6`: SyntaxError: invalid syntax (<unknown>, line 1) |
| javascript | `stdin_script.js` | PASS | FAIL | - | - | - | - | - | - | - | `L1`: AmbiguousEntry: Several candidate entry points: []. Pass --entry. |
| javascript | `two_sum.js` | PASS | PASS | PASS | PASS | PASS | PASS | FAIL | - | - | `L6`: SyntaxError: invalid syntax (<unknown>, line 1) |
| c | `main_only.c` | PASS | FAIL | - | - | - | - | - | - | - | `L1`: AmbiguousEntry: Several candidate entry points: ['main']. Pass --entry. |
| c | `static_fn.c` | PASS | PASS | FAIL | - | - | - | - | - | - | `L2`: Build failed: Compiler not found (gcc): [WinError 2] The system cannot find the file specified |
| c | `sum_overflow.c` | PASS | PASS | FAIL | - | - | - | - | - | - | `L2`: Build failed: Compiler not found (gcc): [WinError 2] The system cannot find the file specified |
| c | `two_sum.c` | PASS | PASS | FAIL | - | - | - | - | - | - | `L2`: Build failed: Compiler not found (gcc): [WinError 2] The system cannot find the file specified |
| cpp | `class_method.cpp` | PASS | PASS | FAIL | - | - | - | - | - | - | `L2`: Build failed: Compiler not found (g++): [WinError 2] The system cannot find the file specified |
| cpp | `dedupe_rank.cpp` | PASS | PASS | FAIL | - | - | - | - | - | - | `L2`: Build failed: Compiler not found (g++): [WinError 2] The system cannot find the file specified |
| cpp | `template_fn.cpp` | PASS | PASS | FAIL | - | - | - | - | - | - | `L2`: Build failed: Compiler not found (g++): [WinError 2] The system cannot find the file specified |

**Summary**: 4/25 fixtures reached L8 PASS.
