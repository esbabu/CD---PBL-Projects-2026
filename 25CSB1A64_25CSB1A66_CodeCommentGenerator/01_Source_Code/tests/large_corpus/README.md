# Large-file test corpus

50 generated Python files, each about 1,800–2,400 lines (101,057 lines in total), used by
`tests/test_large_corpus.py`.

| File | Role |
|---|---|
| `snippets.py` | For each of the 50 rules: one **vulnerable** snippet and one **safe twin** (the fix the rule's remediation recommends). The line the rule must report ends with `#!`. Written by hand. |
| `filler.py` | 24 templates of ordinary, secure application code: data classes, SQLite repositories with parameterised SQL, validation, statistics, CSV parsing, caches, state machines, reports, rate limiters, graph search, and Flask routes that convert or escape their input. |
| `generate.py` | Builds the files: a header + filler + 10 vulnerable snippets + 10 safe twins, shuffled with a fixed seed. File *i* plants rules `(10·(i−1)+k) mod 50` for k = 0..9, so **every rule is planted in exactly 10 files** (500 planted vulnerabilities) and appears 10 times as a safe twin. |
| `cases/` | The generated files (`case_01_inventory_service.py` … `case_50_city_permits.py`). |
| `manifest.json` | Ground truth: for every file, the expected `(rule, line)` pairs and the line ranges of the safe twins. |

## What the tests check

1. **Shape:** 50 files, each at least 1,500 lines; 500 planted vulnerabilities, 10 for each
   rule.
2. **Reproducibility:** each checked-in file and its manifest entry are byte-identical to
   what `generate.py` produces.
3. **Detection:** for each file, the analyzer's active findings must be **exactly** the
   planted pairs. Every planted vulnerability must be found at its line, and nothing else
   may be reported: no finding on a safe twin, and none on the roughly 1,900 lines of
   ordinary code.
4. **Comment generation:** on every 10th file, the full pipeline (`run_pipeline`) must give
   every function and class a docstring and report every planted vulnerability.

Current result: **500 / 500 found, 0 false positives, all 50 files**. Analysing one file
takes about 0.6 s, and the full pipeline with comments takes about 1.3 s per file.

## Where the ground truth comes from

The expected lines come from the `#!` markers in `snippets.py`, which were written by hand
from each rule's definition. They were **not** taken from analyzer output. When the
analyzer first disagreed with the corpus (the SEC023 safe twin `lang if lang.isalpha() else
"en"` was reported), the fix went into the analyzer: conditional expressions now apply the
validation in their condition. The ground truth was not changed.

## Limits

This is a **synthetic** regression corpus: the planted code follows the same patterns the
rules were designed for. It shows that the analyzer scales to large files and keeps its
precision when vulnerable code is surrounded by ordinary code. It is **not** an independent
accuracy benchmark; for that, see the OWASP and GHSA results in `SECURITY_ANALYSIS.md` §5.

Regenerate with `python -m tests.large_corpus.generate`. The output is deterministic.
