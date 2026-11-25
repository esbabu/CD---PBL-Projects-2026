# Fix-agent fixtures

Vulnerable snippets for `tests/test_agent.py`, one per fix strategy plus the
retry and give-up cases. They live in this sub-folder so the labelled security
evaluation (`python -m src.security.evaluate`, which reads only the top-level
`tests/security_fixtures/*.py`) is unchanged. Analysed and patched, never executed.

`mixed_demo.py` combines five fixable findings (SQL injection, command injection, YAML,
MD5, XXE) with one SSRF that needs a human; it is the file used for the Auto-fix
screenshots and the recording.
