"""
Unit and regression tests verifying that Security Vulnerabilities
are directly remediated and surfaced as line-level fixes in the Optimization tab.
"""
import os
import sys
import pytest
from unittest.mock import MagicMock

_this_dir = os.path.dirname(os.path.abspath(__file__))
_sec_dir = os.path.abspath(os.path.join(_this_dir, ".."))
_root_dir = os.path.abspath(os.path.join(_this_dir, "..", ".."))

for p in [_sec_dir, _root_dir]:
    if p not in sys.path:
        sys.path.insert(0, p)

for cand in [
    os.path.join(os.path.expanduser("~"), "Desktop", "modified-main (2)", "modified-main"),
    r"C:\Users\user\Desktop\modified-main (2)\modified-main",
]:
    if os.path.isdir(cand) and cand not in sys.path:
        sys.path.append(cand)

try:
    from agent_framework.context_manager import ContextManager
except ImportError:
    from agents.security_agent import ContextManager

try:
    from remediation_and_patching.security_patcher import SecurityPatcher
except ImportError:
    from src.optimization.security_patcher import SecurityPatcher

try:
    from src.agents.optimization_agent import OptimizationAgent
except ImportError:
    OptimizationAgent = None


class TestSecurityPatcher:
    """Tests for deterministic security patching."""

    def test_remediate_strcpy(self):
        code = (
            "#include <string.h>\n"
            "void test(const char* src) {\n"
            "    char buf[32];\n"
            "    strcpy(buf, src);\n"
            "}\n"
        )
        patched, transforms, diff = SecurityPatcher.patch_code(code, "test.c")
        assert "strncpy" in patched
        assert "sizeof(buf) - 1" in patched
        assert any(t.get("cwe_id") in ("CWE-120", "CWE-121") for t in transforms)
        assert len(diff) > 0

    def test_remediate_sprintf(self):
        code = (
            "#include <stdio.h>\n"
            "void test(const char* name) {\n"
            "    char buf[64];\n"
            "    sprintf(buf, \"User: %s\", name);\n"
            "}\n"
        )
        patched, transforms, diff = SecurityPatcher.patch_code(code, "test.c")
        assert "snprintf" in patched
        assert "sizeof(buf)" in patched
        assert any(t.get("cwe_id") in ("CWE-134", "CWE-121") for t in transforms)

    def test_remediate_gets(self):
        code = (
            "#include <stdio.h>\n"
            "void read_input() {\n"
            "    char buf[128];\n"
            "    gets(buf);\n"
            "}\n"
        )
        patched, transforms, diff = SecurityPatcher.patch_code(code, "test.c")
        assert "fgets(buf, sizeof(buf), stdin)" in patched
        assert " gets(" not in patched
        assert any(t.get("cwe_id") == "CWE-242" for t in transforms)

    def test_remediate_format_string(self):
        code = (
            "#include <stdio.h>\n"
            "void log_msg(const char* msg) {\n"
            "    printf(msg);\n"
            "}\n"
        )
        patched, transforms, diff = SecurityPatcher.patch_code(code, "test.c")
        assert 'printf("%s", msg);' in patched
        assert any(t.get("cwe_id") == "CWE-134" for t in transforms)


class TestOptimizationAgentSecurityRemediation:
    """Tests that OptimizationAgent produces security fixes when findings exist."""

    def test_optimization_agent_generates_security_fixes_offline(self):
        if OptimizationAgent is None:
            pytest.skip("OptimizationAgent not available in standalone security package")
        ctx = ContextManager()
        # Mock LLM as unavailable/offline
        mock_llm = MagicMock()
        mock_llm.generate.return_value = {"text": "", "meta": {"model": "offline"}}

        agent = OptimizationAgent("optimization_1", ctx, mock_llm)
        code = (
            "#include <string.h>\n"
            "#include <stdio.h>\n"
            "void process(const char* input) {\n"
            "    char buf[32];\n"
            "    strcpy(buf, input);\n"
            "    printf(buf);\n"
            "}\n"
        )
        result = agent.process({
            "source_code": code,
            "file_path": "vuln.c",
            "security_report": {
                "all_vulnerabilities": [
                    {
                        "type": "buffer_overflow",
                        "cwe_id": "CWE-120",
                        "line": 5,
                        "description": "Unbounded strcpy into buffer",
                    },
                    {
                        "type": "format_string",
                        "cwe_id": "CWE-134",
                        "line": 6,
                        "description": "printf called with dynamic format string",
                    },
                ]
            }
        })

        assert result.get("optimization_status") in ("optimization_generated", "SECURITY_REMEDIATION_APPLIED")
        assert len(result.get("transformations", [])) >= 2
        assert "strncpy" in result.get("optimized_code", "")
        assert 'printf("%s", buf)' in result.get("optimized_code", "")
        # Check that transformation cards contain line numbers and CWE tags
        transforms = result.get("transformations", [])
        assert any(t.get("cwe_id") == "CWE-120" and t.get("line") == 5 for t in transforms)
        assert any(t.get("cwe_id") == "CWE-134" and t.get("line") == 6 for t in transforms)
