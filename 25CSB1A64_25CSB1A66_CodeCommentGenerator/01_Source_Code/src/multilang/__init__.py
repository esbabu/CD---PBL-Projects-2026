"""
Multi-language compiler back end and security analysis
=======================================================
Java, C, C++, C#, Rust and COBOL source is lowered into the same three-address
IR the Python pipeline uses (``src/ir/ir_nodes.py``), so the existing CFG
builder, data-flow analyses (reaching definitions, live variables) and
pattern detector (P001–P007) run unchanged on every language.

  lower.py      tree-sitter syntax tree → IRModule (Java, C, C++, C#, Rust)
  cobol.py      COBOL parser (fixed and free format) → IRModule
  specs.py      per-language taint sources, sinks, sanitizers, propagation
  taint.py      language-neutral taint analysis over the IR + CFG
  memory.py     flow-sensitive memory-safety checks (use after free, double free,
                unchecked allocation) for C / C++
  patterns.py   syntax-level rules (dangerous APIs, crypto, TLS, XXE configuration,
                hard-coded credentials, unsafe Rust, races, authorization)
  analyzer.py   entry point: ``analyze_source(source, path, language)`` →
                ``SecurityFindings`` (the same type the Python analyzer returns)

Python keeps its own, richer front end (``src/security``); see ``CAPABILITIES``
in ``analyzer.py`` for what is fully, partially or not supported per language.
"""
from .analyzer import CAPABILITIES, SUPPORTED, analyze_file, analyze_source

__all__ = ["CAPABILITIES", "SUPPORTED", "analyze_file", "analyze_source"]
