# Security dataset v1

Built by `python -m src.dataset.build` (101.5 s). Every number below is computed from
`samples.jsonl.gz` by the builder.

| | |
|---|---|
| Samples | 23,131 |
| Total lines of code | 774,960 |
| Groups (split unit) | 3,895 |
| Distinct CWEs | 132 |
| Long programs (1,000-2,000 lines) | 91 programs, 137,144 lines, 4984 planted vulnerabilities |
| Files with more than one vulnerability class | 98 |

## Splits (70/15/15 by group (Juliet functional variant, OWASP template family, custom template with its safe twin and renamed variants); long programs use only their split's templates)

| Split | Samples |
|---|---|
| test | 3100 |
| train | 16216 |
| val | 3815 |

## Languages

| Language | Samples | Lines of code |
|---|---|---|
| python | 1,537 | 115,587 |
| java | 3,755 | 161,402 |
| csharp | 3,844 | 121,055 |
| c | 8,490 | 211,179 |
| cpp | 5,358 | 124,332 |
| rust | 67 | 21,064 |
| cobol | 80 | 20,341 |

## Sources

| Source | Samples |
|---|---|
| custom | 756 |
| custom-long | 91 |
| juliet | 21054 |
| owasp | 1230 |

## Labels per language

| Language / label | Samples |
|---|---|
| c/safe | 6316 |
| c/vulnerable | 2174 |
| cobol/safe | 33 |
| cobol/vulnerable | 47 |
| cpp/safe | 3232 |
| cpp/vulnerable | 2126 |
| csharp/safe | 2887 |
| csharp/vulnerable | 957 |
| java/safe | 2795 |
| java/vulnerable | 960 |
| python/safe | 925 |
| python/vulnerable | 612 |
| rust/safe | 12 |
| rust/vulnerable | 55 |

## Vulnerable samples by family

| Family | Samples |
|---|---|
| (per-location rules) | 181 |
| authorization | 47 |
| buffer-overflow | 919 |
| cleartext | 146 |
| code-injection | 47 |
| command-injection | 344 |
| deserialization | 32 |
| error-handling | 284 |
| format-string | 319 |
| hardcoded-credentials | 67 |
| header-injection | 89 |
| index-validation | 104 |
| information-exposure | 79 |
| input-validation | 431 |
| integer-overflow | 1284 |
| ldap-injection | 159 |
| log-injection | 24 |
| memory-management | 575 |
| null-dereference | 211 |
| open-redirect | 59 |
| path-traversal | 324 |
| race-condition | 48 |
| resource-exhaustion | 349 |
| sql-injection | 98 |
| ssrf | 12 |
| trust-boundary | 85 |
| weak-crypto | 183 |
| weak-randomness | 123 |
| xpath-injection | 102 |
| xss | 187 |
| xxe | 19 |

## Location labels by rule (custom samples and long programs)

| Rule | Locations |
|---|---|
| SEC001 | 6 |
| SEC002 | 348 |
| SEC003 | 239 |
| SEC004 | 253 |
| SEC005 | 375 |
| SEC006 | 6 |
| SEC008 | 12 |
| SEC009 | 97 |
| SEC010 | 7 |
| SEC011 | 76 |
| SEC012 | 5 |
| SEC013 | 501 |
| SEC014 | 100 |
| SEC015 | 15 |
| SEC016 | 170 |
| SEC017 | 102 |
| SEC018 | 134 |
| SEC019 | 41 |
| SEC020 | 71 |
| SEC021 | 7 |
| SEC022 | 103 |
| SEC023 | 44 |
| SEC024 | 108 |
| SEC025 | 142 |
| SEC026 | 172 |
| SEC027 | 8 |
| SEC028 | 73 |
| SEC029 | 15 |
| SEC030 | 121 |
| SEC031 | 159 |
| SEC032 | 12 |
| SEC033 | 122 |
| SEC034 | 56 |
| SEC035 | 16 |
| SEC036 | 10 |
| SEC037 | 10 |
| SEC038 | 11 |
| SEC039 | 10 |
| SEC040 | 10 |
| SEC041 | 8 |
| SEC042 | 8 |
| SEC043 | 13 |
| SEC044 | 66 |
| SEC045 | 56 |
| SEC046 | 34 |
| SEC047 | 35 |
| SEC048 | 8 |
| SEC049 | 33 |
| SEC050 | 134 |
| SEC051 | 41 |
| SEC052 | 117 |
| SEC053 | 51 |
| SEC054 | 253 |
| SEC055 | 92 |
| SEC056 | 164 |
| SEC057 | 40 |
| SEC058 | 38 |
| SEC059 | 64 |
| SEC060 | 81 |
| SEC061 | 96 |
| SEC062 | 87 |
| SEC063 | 199 |

## Record format (`samples.jsonl.gz`, one JSON object per line)

`id, language, source (juliet | owasp | custom | custom-long), kind (function | file), split, group,
label (vulnerable | safe), family, cwe, severity, severity_source, locations [{line, rule, cwe, severity}],
lines, code, path (files), origin, template / variant (custom)`

Juliet locations come from Juliet's own `FLAW` comments; OWASP cases carry a file-level label only
(no line); custom locations are the hand-written markers. Severity comes from the project's rule for
that rule or CWE family (CWE itself has no severity field).

## Validation

0 custom samples were rejected (custom files must parse without syntax errors; vulnerable samples carry >= 1 location label, safe samples none).

## Licences

NIST SARD Juliet Test Suite 1.3 for Java, C/C++, C# (public domain); OWASP BenchmarkPython (GPL-3.0, pinned commit in src/security/benchmarks.py); hand-labelled templates in tests/ and src/dataset/ (labels written next to the code).
