# Multi-language source support

The Generator now accepts these six language families:

- Python (`.py`, `.pyw`)
- C (`.c`, `.h`)
- C++ (`.cc`, `.cpp`, `.cxx`, `.hpp`, `.hh`, `.hxx`)
- Java (`.java`)
- JavaScript (`.js`, `.jsx`, `.mjs`, `.cjs`)
- TypeScript (`.ts`, `.tsx`, `.mts`, `.cts`)

## Install the structural parser

From the project root, run:

```powershell
py -m pip install -r requirements-multilang.txt
```

`tree-sitter-language-pack` supplies language parsers through `get_parser()`. The first use of a grammar may download that grammar to the local cache; an internet connection is needed for a grammar that is not already cached. Subsequent parsing uses the cache. If the parser package or grammar is unavailable, the application falls back to a conservative declaration scanner and labels that mode in its report. The fallback is less accurate than Tree-sitter.

## How generation works by language

- Python continues to use the original Python AST pipeline. Rule-Based, T5-small ML and Neurosymbolic generation remain Python-only.
- C, C++, Java, JavaScript and TypeScript use Tree-sitter structural parsing and Rule-Based documentation comments (`/** ... */`) for supported functions/methods/classes. This does not use the Python T5 model.
- Choose a language in the Generator selector when pasting code. Picking a source file selects the language from its extension.
- Generator hands the original source, language and filename to Agentic Security automatically.

## Security and malware analysis scope

The Agentic Security workspace runs local static checks for all six supported languages. The malware-behaviour scanner correlates multiple source indicators (for example encoded content plus dynamic execution) and reports rule IDs, line locations, evidence and remediation suggestions.

The scanner does not execute source code. A result stating that no configured indicators were found is not a guarantee that code is malware-free. Dynamic analysis, sandboxing and a validated malware benchmark are not included. Automatic safer-code rewrites are currently implemented for selected Python findings; non-Python findings provide evidence and remediation guidance without attempting an unsafe cross-language rewrite.

## Run

```powershell
py run_gui.py
```

## Tests

```powershell
py -m pytest test_multilang.py tests/test_malware_detector.py -q
py -m compileall -q src run_gui.py
```
