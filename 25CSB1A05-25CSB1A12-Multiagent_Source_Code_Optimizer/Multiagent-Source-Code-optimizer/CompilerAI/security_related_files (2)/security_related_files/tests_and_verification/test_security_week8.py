"""
test_security_week8.py — Week 8 Security Agent Tests

Covers:
  - SecurityAgent Layer 1: rule-based detection
  - SecurityAgent Layer 2: heuristic detection
  - SecurityPromptTemplate structure
  - New-vulnerability detection and rollback logic
  - Full 4-stage pipeline integration on real test cases
  - cppcheck integration (skipped if not installed)
"""

import os
import sys
import pytest
from unittest.mock import MagicMock, patch

# Ensure security package root is on path first
_this_dir = os.path.dirname(os.path.abspath(__file__))
_sec_dir = os.path.abspath(os.path.join(_this_dir, ".."))
_root_dir = os.path.abspath(os.path.join(_this_dir, "..", ".."))

for p in [_sec_dir, _root_dir]:
    if p in sys.path:
        sys.path.remove(p)
    sys.path.insert(0, p)

# Purge any conflicting cached agents module from other paths
for mod_name in list(sys.modules.keys()):
    if mod_name == "agents" or mod_name.startswith("agents."):
        mod_file = getattr(sys.modules[mod_name], "__file__", "") or ""
        if _sec_dir not in mod_file:
            del sys.modules[mod_name]

from agents.security_agent import SecurityAgent, ContextManager

try:
    from rules_and_scanners.prompt_templates import SecurityPromptTemplate
except ImportError:
    from src.llm.prompt_templates import SecurityPromptTemplate

# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def ctx():
    return ContextManager()


@pytest.fixture
def mock_llm():
    """LLM that returns a valid stub CoT JSON (no real Ollama needed)."""
    llm = MagicMock()
    llm._available = False
    llm.generate.return_value = (
        '```json\n'
        '{\n'
        '  "reasoning_steps": ["Analyzed code for vulnerabilities."],\n'
        '  "findings": [],\n'
        '  "overall_risk": "none",\n'
        '  "conclusion": "No new vulnerabilities found.",\n'
        '  "confidence": 0.7\n'
        '}\n'
        '```'
    )
    return llm


@pytest.fixture
def agent(ctx, mock_llm):
    return SecurityAgent("sec_test", ctx, llm_client=mock_llm)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _run(agent, original, optimized, file_path="test.cpp"):
    return agent.process({
        "original_code":  original,
        "optimized_code": optimized,
        "file_path":      file_path,
    })


# ═══════════════════════════════════════════════════════════════════════════════
# LAYER 1: Rule-based detection
# ═══════════════════════════════════════════════════════════════════════════════

class TestRuleBasedDetection:

    def test_gets_flagged(self, agent):
        code = '#include <stdio.h>\nvoid f() { char buf[64]; gets(buf); }'
        result = _run(agent, code, code)
        types = [v["type"] for v in result["all_vulnerabilities"]]
        assert "unsafe_gets" in types

    def test_gets_severity_high(self, agent):
        code = 'void f() { char buf[64]; gets(buf); }'
        result = _run(agent, code, code)
        gets_finding = next(
            v for v in result["all_vulnerabilities"] if v["type"] == "unsafe_gets"
        )
        assert gets_finding["severity"] == "high"
        assert gets_finding["confidence"] == 0.9
        assert gets_finding["source"] == "rule"

    def test_strcpy_flagged(self, agent):
        code = 'void f(char* s) { char buf[64]; strcpy(buf, s); }'
        result = _run(agent, code, code)
        types = [v["type"] for v in result["all_vulnerabilities"]]
        assert "unsafe_strcpy" in types

    def test_sprintf_flagged(self, agent):
        code = 'void f(char* s) { char buf[64]; sprintf(buf, s); }'
        result = _run(agent, code, code)
        types = [v["type"] for v in result["all_vulnerabilities"]]
        assert "unsafe_sprintf" in types

    def test_format_string_bug_flagged(self, agent):
        code = 'void f(char* msg) { printf(msg); }'
        result = _run(agent, code, code)
        types = [v["type"] for v in result["all_vulnerabilities"]]
        assert "format_string_bug" in types

    def test_format_string_literal_not_flagged(self, agent):
        """printf("Hello %s", name) is safe — the format arg is a literal."""
        code = 'void f(char* name) { printf("Hello %s\\n", name); }'
        result = _run(agent, code, code)
        types = [v["type"] for v in result["all_vulnerabilities"]]
        assert "format_string_bug" not in types

    def test_use_after_free_flagged(self, agent):
        code = (
            '#include <stdlib.h>\n'
            'void f() {\n'
            '  int* p = (int*)malloc(4);\n'
            '  free(p);\n'
            '  *p = 42;\n'
            '}\n'
        )
        result = _run(agent, code, code)
        types = [v["type"] for v in result["all_vulnerabilities"]]
        assert "use_after_free" in types

    def test_safe_code_no_rule_findings(self, agent):
        safe_code = (
            '#include <stdio.h>\n'
            '#include <string.h>\n'
            'void f(const char* src) {\n'
            '    char buf[64];\n'
            '    strncpy(buf, src, sizeof(buf) - 1);\n'
            '    buf[63] = "\\0";\n'
            '    printf("%s\\n", buf);\n'
            '}\n'
        )
        result = _run(agent, safe_code, safe_code)
        rule_findings = [
            v for v in result["all_vulnerabilities"] if v.get("source") == "rule"
        ]
        assert len(rule_findings) == 0, f"Unexpected: {rule_findings}"


# ═══════════════════════════════════════════════════════════════════════════════
# LAYER 2: Heuristic detection
# ═══════════════════════════════════════════════════════════════════════════════

class TestHeuristicDetection:

    def test_taint_flow_detected(self, agent):
        """scanf → strcpy without size check triggers taint flow heuristic."""
        code = (
            '#include <stdio.h>\n'
            '#include <string.h>\n'
            'void f() {\n'
            '    char src[256], dst[64];\n'
            '    scanf("%s", src);\n'
            '    strcpy(dst, src);\n'
            '}\n'
        )
        result = _run(agent, code, code)
        types = [v["type"] for v in result["all_vulnerabilities"]]
        assert "taint_flow_risk" in types

    def test_unchecked_malloc_detected(self, agent):
        code = (
            '#include <stdlib.h>\n'
            'void f() {\n'
            '    int* p = (int*)malloc(100 * sizeof(int));\n'
            '    p[0] = 1;\n'
            '}\n'
        )
        result = _run(agent, code, code)
        types = [v["type"] for v in result["all_vulnerabilities"]]
        assert "unchecked_malloc" in types

    def test_unchecked_malloc_not_flagged_when_checked(self, agent):
        code = (
            '#include <stdlib.h>\n'
            '#include <assert.h>\n'
            'void f() {\n'
            '    int* p = (int*)malloc(100 * sizeof(int));\n'
            '    assert(p);\n'
            '    p[0] = 1;\n'
            '}\n'
        )
        result = _run(agent, code, code)
        h_types = [
            v["type"] for v in result["all_vulnerabilities"]
            if v.get("source") == "heuristic"
        ]
        assert "unchecked_malloc" not in h_types

    def test_int_overflow_malloc_detected(self, agent):
        code = (
            '#include <stdlib.h>\n'
            'void f(int a, int b) {\n'
            '    int* p = (int*)malloc(a * b);\n'
            '}\n'
        )
        result = _run(agent, code, code)
        types = [v["type"] for v in result["all_vulnerabilities"]]
        assert "integer_overflow_malloc" in types

    def test_buffer_loop_write_detected(self, agent):
        code = (
            'void f(int n) {\n'
            '    char buf[64];\n'
            '    for (int i = 0; i < n; i++) {\n'
            '        buf[i] = "A";\n'
            '    }\n'
            '}\n'
        )
        result = _run(agent, code, code)
        types = [v["type"] for v in result["all_vulnerabilities"]]
        assert "unbounded_loop_write" in types


# ═══════════════════════════════════════════════════════════════════════════════
# New vulnerability detection & rollback
# ═══════════════════════════════════════════════════════════════════════════════

class TestNewVulnerabilityDetection:

    def test_new_vuln_detected_when_not_in_original(self, agent):
        original  = 'void f() { char buf[64]; strncpy(buf, "hi", 63); }'
        optimized = 'void f() { char buf[64]; gets(buf); }'
        result = _run(agent, original, optimized)
        new_types = [v["type"] for v in result["new_vulnerabilities"]]
        assert "unsafe_gets" in new_types

    def test_preexisting_vuln_not_in_new_vulns(self, agent):
        """gets() in both original and optimized → not a new vulnerability."""
        code = 'void f() { char buf[64]; gets(buf); }'
        result = _run(agent, code, code)
        new_types = [v["type"] for v in result["new_vulnerabilities"]]
        assert "unsafe_gets" not in new_types

    def test_rollback_triggered_on_new_high_severity(self, ctx, mock_llm):
        """A new HIGH rule-based finding must trigger rollback."""
        agent = SecurityAgent("sec_rb", ctx, llm_client=mock_llm)
        # Put something in context so rollback has state to revert
        ctx.set("original_code", "void f() {}")
        ctx.set("optimized_code", "void f() { gets(buf); }")

        original  = 'void f() {}'
        optimized = 'void f() { char buf[64]; gets(buf); }'
        result = _run(agent, original, optimized)
        assert result["status"] == "ROLLBACK"
        assert len(result["rollback_triggers"]) > 0

    def test_no_rollback_when_no_new_high_severity(self, ctx, mock_llm):
        """Pre-existing gets() should NOT trigger rollback."""
        agent = SecurityAgent("sec_no_rb", ctx, llm_client=mock_llm)
        code = 'void f() { char buf[64]; gets(buf); }'
        result = _run(agent, code, code)
        assert result["status"] == "PASS"
        assert len(result["rollback_triggers"]) == 0

    def test_llm_only_finding_does_not_trigger_rollback(self, ctx):
        """LLM findings alone must not trigger rollback, only rules/heuristics can."""
        llm = MagicMock()
        llm._available = True
        # LLM reports a high-severity finding
        llm.generate.return_value = (
            '```json\n'
            '{\n'
            '  "reasoning_steps": ["Found a SQL injection risk."],\n'
            '  "findings": [{"type": "sql_injection", "severity": "high", '
            '    "line": 5, "description": "SQL risk", "cwe_id": "CWE-89", '
            '    "recommendation": "Use prepared statements"}],\n'
            '  "overall_risk": "high",\n'
            '  "conclusion": "SQL injection risk detected.",\n'
            '  "confidence": 0.9\n'
            '}\n'
            '```'
        )
        agent = SecurityAgent("sec_llm", ctx, llm_client=llm)
        safe_code = 'void f() { int x = 1; }'
        result = _run(agent, safe_code, safe_code)
        # sql_injection is only from LLM → should NOT rollback
        assert result["status"] == "PASS"


# ═══════════════════════════════════════════════════════════════════════════════
# SecurityPromptTemplate
# ═══════════════════════════════════════════════════════════════════════════════

class TestSecurityPromptTemplate:

    def test_build_contains_required_schema_keys(self):
        prompt = SecurityPromptTemplate.build("void f() {}")
        for key in ["reasoning_steps", "findings", "overall_risk",
                    "conclusion", "confidence"]:
            assert key in prompt, f"Missing key: {key}"

    def test_build_includes_code(self):
        code = "void secret_function() { return 42; }"
        prompt = SecurityPromptTemplate.build(code)
        assert "secret_function" in prompt

    def test_build_with_baseline_types_includes_note(self):
        prompt = SecurityPromptTemplate.build(
            optimized_code="void f() {}",
            original_code="void f() { gets(buf); }",
            baseline_types=["unsafe_gets"],
        )
        assert "unsafe_gets" in prompt
        assert "ALREADY present" in prompt

    def test_system_prompt_not_empty(self):
        assert len(SecurityPromptTemplate.SYSTEM) > 10


# ═══════════════════════════════════════════════════════════════════════════════
# cppcheck integration (skip if not available)
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.skipif(
    not SecurityAgent._check_cppcheck(),
    reason="cppcheck not installed",
)
class TestCppcheckIntegration:

    def test_cppcheck_runs_without_crash(self, agent):
        code = '#include <stdio.h>\nvoid f() { char buf[4]; gets(buf); }'
        findings = agent._cppcheck_scan(code, "test.cpp")
        # Just verify it returned a list (may be empty on some cppcheck versions)
        assert isinstance(findings, list)

    def test_cppcheck_source_label(self, agent):
        code = 'void f() { int* p = 0; *p = 1; }'
        findings = agent._cppcheck_scan(code, "test.cpp")
        for f in findings:
            assert f["source"] == "cppcheck"
            assert "cppcheck_" in f["type"]


# ═══════════════════════════════════════════════════════════════════════════════
# Overall risk computation
# ═══════════════════════════════════════════════════════════════════════════════

class TestRiskComputation:

    def test_no_findings_is_none_risk(self, agent):
        assert agent._compute_risk([]) == "none"

    def test_single_high_is_high_risk(self, agent):
        findings = [{"severity": "high"}]
        assert agent._compute_risk(findings) == "high"

    def test_three_high_is_critical(self, agent):
        findings = [{"severity": "high"}] * 3
        assert agent._compute_risk(findings) == "critical"

    def test_medium_only_is_medium(self, agent):
        findings = [{"severity": "medium"}, {"severity": "low"}]
        assert agent._compute_risk(findings) == "medium"

    def test_low_only_is_low(self, agent):
        findings = [{"severity": "low"}]
        assert agent._compute_risk(findings) == "low"


# ═══════════════════════════════════════════════════════════════════════════════
# Full 4-stage pipeline integration tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestPipelineIntegration:
    """Run the full 4-stage pipeline on real test case files (--no-llm mode)."""

    @pytest.fixture(autouse=True)
    def setup_pipeline(self):
        from src.pipeline.pipeline import CompilerOptimizationPipeline
        from src.llm.llm_client import LLMClient
        llm = LLMClient()
        llm._available = False  # offline mode — rules only
        self.pipeline = CompilerOptimizationPipeline(llm_client=llm)

    def _tc_path(self, name):
        return os.path.join(
            os.path.dirname(__file__), "..",
            "MicroBenchmarks", "Testcases", name,
        )

    def test_pipeline_has_security_report_field(self):
        tc = self._tc_path("TC01_uninit_arithmetic.cpp")
        if not os.path.isfile(tc):
            pytest.skip("TC01 not found")
        result = self.pipeline.run(tc)
        assert hasattr(result, "security_report"), \
            "PipelineResult missing security_report field"
        assert isinstance(result.security_report, dict)

    def test_pipeline_tc11_buffer_overflow(self):
        tc = self._tc_path("TC11_buffer_overflow_loop.cpp")
        if not os.path.isfile(tc):
            pytest.skip("TC11 not found")
        result = self.pipeline.run(tc)
        assert result.status in ("success", "partial", "rollback", "failed", "no_optimization")
        # Security report must exist
        assert result.security_report.get("status") in ("PASS", "ROLLBACK")

    def test_pipeline_tc14_memory_leak(self):
        tc = self._tc_path("TC14_memory_leak.cpp")
        if not os.path.isfile(tc):
            pytest.skip("TC14 not found")
        result = self.pipeline.run(tc)
        assert result.status in ("success", "partial", "rollback", "failed", "no_optimization")
        assert isinstance(result.security_report.get("all_vulnerabilities"), list)

    def test_pipeline_tc16_use_after_free(self):
        tc = self._tc_path("TC16_use_after_free.cpp")
        if not os.path.isfile(tc):
            pytest.skip("TC16 not found")
        result = self.pipeline.run(tc)
        assert result.status in ("success", "partial", "rollback", "failed", "no_optimization")
        sec = result.security_report
        # TC16 contains use_after_free — security agent should detect it
        all_types = [v["type"] for v in sec.get("all_vulnerabilities", [])]
        assert "use_after_free" in all_types, \
            f"Expected use_after_free in {all_types}"

    def test_pipeline_tc19_heap_overflow(self):
        tc = self._tc_path("TC19_heap_overflow.cpp")
        if not os.path.isfile(tc):
            pytest.skip("TC19 not found")
        result = self.pipeline.run(tc)
        assert result.status in ("success", "partial", "rollback", "failed", "no_optimization")
        assert "overall_risk" in result.security_report

    def test_pipeline_summary_includes_security_section(self):
        tc = self._tc_path("TC01_uninit_arithmetic.cpp")
        if not os.path.isfile(tc):
            pytest.skip("TC01 not found")
        result = self.pipeline.run(tc)
        summary = result.summary()
        assert "[Security]" in summary, \
            "PipelineResult.summary() missing [Security] section"

    def test_pipeline_result_status_is_valid(self):
        tc = self._tc_path("TC01_uninit_arithmetic.cpp")
        if not os.path.isfile(tc):
            pytest.skip("TC01 not found")
        result = self.pipeline.run(tc)
        assert result.status in ("success", "partial", "rollback", "failed", "no_optimization")


# ═══════════════════════════════════════════════════════════════════════════════
# MULTI-LANGUAGE EXTENSION: Python & Java Security Auditing
# ═══════════════════════════════════════════════════════════════════════════════

class TestPythonSecurityDetection:

    def test_python_command_injection(self, agent):
        code = "import os\ndef ping(host):\n    os.system('ping ' + host)"
        result = _run(agent, code, code, file_path="network_tool.py")
        types = [v["type"] for v in result["all_vulnerabilities"]]
        assert any("command_injection" in t for t in types)
        finding = next(v for v in result["all_vulnerabilities"] if "command_injection" in v["type"])
        assert finding["cwe_id"] == "CWE-78"
        assert finding["severity"] == "critical"

    def test_python_eval_code_injection(self, agent):
        code = "def calculate(expr):\n    return eval(expr)"
        result = _run(agent, code, code, file_path="calc.py")
        types = [v["type"] for v in result["all_vulnerabilities"]]
        assert any("eval" in t for t in types)
        finding = next(v for v in result["all_vulnerabilities"] if "eval" in v["type"])
        assert finding["cwe_id"] == "CWE-94"
        assert finding["severity"] == "critical"

    def test_python_insecure_pickle_deserialization(self, agent):
        code = "import pickle\ndef load_data(raw):\n    return pickle.loads(raw)"
        result = _run(agent, code, code, file_path="parser.py")
        types = [v["type"] for v in result["all_vulnerabilities"]]
        assert any("pickle" in t for t in types)
        finding = next(v for v in result["all_vulnerabilities"] if "pickle" in v["type"])
        assert finding["cwe_id"] == "CWE-502"
        assert finding["severity"] == "critical"

    def test_python_sql_injection(self, agent):
        code = "def get_user(cursor, username):\n    cursor.execute(f'SELECT * FROM users WHERE name = {username}')"
        result = _run(agent, code, code, file_path="db.py")
        types = [v["type"] for v in result["all_vulnerabilities"]]
        assert any("sqli" in t for t in types)
        finding = next(v for v in result["all_vulnerabilities"] if "sqli" in v["type"])
        assert finding["cwe_id"] == "CWE-89"

    def test_python_insecure_hash_md5(self, agent):
        code = "import hashlib\ndef hash_pw(pw):\n    return hashlib.md5(pw.encode()).hexdigest()"
        result = _run(agent, code, code, file_path="auth.py")
        types = [v["type"] for v in result["all_vulnerabilities"]]
        assert any("md5" in t for t in types)
        finding = next(v for v in result["all_vulnerabilities"] if "md5" in v["type"])
        assert finding["cwe_id"] == "CWE-328"

    def test_python_tls_verification_disabled(self, agent):
        code = "import requests\ndef fetch(url):\n    return requests.get(url, verify=False)"
        result = _run(agent, code, code, file_path="client.py")
        types = [v["type"] for v in result["all_vulnerabilities"]]
        assert any("tls" in t for t in types)
        finding = next(v for v in result["all_vulnerabilities"] if "tls" in v["type"])
        assert finding["cwe_id"] == "CWE-295"


class TestJavaSecurityDetection:

    def test_java_command_injection(self, agent):
        code = (
            "public class Shell {\n"
            "    public void run(String cmd) throws Exception {\n"
            "        Runtime.getRuntime().exec(cmd);\n"
            "    }\n"
            "}\n"
        )
        result = _run(agent, code, code, file_path="Shell.java")
        types = [v["type"] for v in result["all_vulnerabilities"]]
        assert any("command_injection" in t for t in types)
        finding = next(v for v in result["all_vulnerabilities"] if "command_injection" in v["type"])
        assert finding["cwe_id"] == "CWE-78"
        assert finding["severity"] == "critical"

    def test_java_sql_injection(self, agent):
        code = (
            "import java.sql.*;\n"
            "public class UserDao {\n"
            "    public void query(Statement stmt, String user) throws Exception {\n"
            "        stmt.executeQuery(\"SELECT * FROM users WHERE name = '\" + user + \"'\");\n"
            "    }\n"
            "}\n"
        )
        result = _run(agent, code, code, file_path="UserDao.java")
        types = [v["type"] for v in result["all_vulnerabilities"]]
        assert any("sql" in t for t in types)
        finding = next(v for v in result["all_vulnerabilities"] if "sql" in v["type"])
        assert finding["cwe_id"] == "CWE-89"

    def test_java_object_deserialization(self, agent):
        code = (
            "import java.io.*;\n"
            "public class Deser {\n"
            "    public Object read(InputStream in) throws Exception {\n"
            "        ObjectInputStream ois = new ObjectInputStream(in);\n"
            "        return ois.readObject();\n"
            "    }\n"
            "}\n"
        )
        result = _run(agent, code, code, file_path="Deser.java")
        types = [v["type"] for v in result["all_vulnerabilities"]]
        assert any("object_input_stream" in t for t in types)
        finding = next(v for v in result["all_vulnerabilities"] if "object_input_stream" in v["type"])
        assert finding["cwe_id"] == "CWE-502"

    def test_java_insecure_md5(self, agent):
        code = (
            "import java.security.MessageDigest;\n"
            "public class Hasher {\n"
            "    public MessageDigest get() throws Exception {\n"
            "        return MessageDigest.getInstance(\"MD5\");\n"
            "    }\n"
            "}\n"
        )
        result = _run(agent, code, code, file_path="Hasher.java")
        types = [v["type"] for v in result["all_vulnerabilities"]]
        assert any("message_digest" in t for t in types)
        finding = next(v for v in result["all_vulnerabilities"] if "message_digest" in v["type"])
        assert finding["cwe_id"] == "CWE-328"


# ═══════════════════════════════════════════════════════════════════════════════
# TERMINAL OUTPUT VERIFICATION
# ═══════════════════════════════════════════════════════════════════════════════

class TestSecurityTerminalOutput:

    def test_format_terminal_report_structure(self, agent):
        code = "import os\ndef f(x):\n    os.system('sh ' + x)"
        result = _run(agent, code, code, file_path="script.py")
        report_text = SecurityAgent.format_terminal_report(result, use_color=False)

        assert "SECURITY AGENT AUDIT REPORT" in report_text
        assert "Target File" in report_text
        assert "script.py" in report_text
        assert "PYTHON" in report_text
        assert "Audit Status" in report_text
        assert "Overall Risk" in report_text
        assert "DETECTED VULNERABILITIES" in report_text
        assert "CWE-78" in report_text
        assert "Remediation" in report_text

    def test_print_terminal_report_writes_to_stream(self, agent):
        import io
        code = 'void f() { char b[32]; gets(b); }'
        result = _run(agent, code, code, file_path="vuln.cpp")
        buf = io.StringIO()
        SecurityAgent.print_terminal_report(result, stream=buf)
        output = buf.getvalue()

        assert "SECURITY AGENT AUDIT REPORT" in output
        assert "vuln.cpp" in output
        assert "CWE-242" in output
        assert "unsafe_gets" in output

    def test_process_triggers_terminal_output_by_default(self, agent):
        import io
        code = 'void f() { char b[32]; gets(b); }'
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            agent.process({
                "original_code": code,
                "optimized_code": code,
                "file_path": "test_output.cpp",
                "terminal_output": True,
            })
            val = fake_out.getvalue()
            assert "SECURITY AGENT AUDIT REPORT" in val
            assert "test_output.cpp" in val

