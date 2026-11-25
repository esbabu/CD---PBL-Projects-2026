# COMMENT GEN PRO – expanded CWE-mapped security signatures

The scanner contains **647 distinct project rule IDs**: the original 47 curated signatures plus 600 additional source/sink-pair signatures. The 600 additions are distributed as 75 signatures in each of eight requested areas: injection; authentication/access control; cryptography/sensitive data; file handling/path traversal; C/C++ memory safety; web security; deserialization/input validation; and network/configuration/other weaknesses.

## What the count means

- The count is **detection signatures**, not 647 unique CWE identifiers. Multiple signatures map to a smaller set of CWE weakness classes.
- The 600 additions are distinct source/sink pair expressions. They are useful static review indicators, but many require both tokens on the same source line. They do not constitute full taint analysis and may miss flows across variables, functions or files.
- A match is not proof of exploitability; absence of a match is not proof of safety. Some categories such as authentication, authorization, memory lifetime, race conditions and dependency vulnerabilities require control-flow, data-flow, framework or deployment context.
- Language coverage depends on syntax and API recognition. Python also retains the existing AST-based checks. C, C++, Java, JavaScript and TypeScript receive source-signature scanning through the existing Local Agentic Security workflow.
- The scanner is local and never executes submitted source code.

Every finding includes a stable project rule ID, CWE mapping, category, severity, line, evidence, language and remediation guidance. Project rule IDs are not MITRE identifiers. Review CWE mappings and false-positive rates before presenting the scanner as production-grade.

Official reference: https://cwe.mitre.org/
