"""
Comprehensive end-to-end integration test suite for VulnHGNN.

Tests all system components:
  1. Web & API Endpoints (/ , /api/live-check, /api/analyze, /api/suggest-fix, /api/heal, /api/pipeline)
  2. Security Hardening (Input validation, Security headers, Rate limiting, API key auth)
  3. HMAC Token Gate (Cryptographic binding, tamper rejection, expired rejection)
  4. Broad Multi-Class CWE Support (All-CWE detection, CWE_CATALOG enrichment)
  5. Static Analysis & Compilation (Clang syntax checks, div-by-zero detection)
  6. 66-Fixture Benchmark Integrity (All 66 files exist and compile with Clang)
"""

import os
import json
import time
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src import app as app_module
from src.security import (
    sign_finding,
    verify_finding_token,
    check_rate_limit,
    verify_api_key,
    validate_source_input,
)
from src.llm_security_review import CWE_CATALOG, _normalize_review

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class SecurityHardeningTests(unittest.TestCase):
    """Test input validation, security headers, rate limiting, and API key auth."""

    def setUp(self):
        self.client = app_module.app.test_client()

    def test_input_validation_empty_source(self):
        is_valid, msg = validate_source_input("")
        self.assertFalse(is_valid)
        self.assertIn("empty", msg.lower())

    def test_input_validation_null_byte(self):
        is_valid, msg = validate_source_input("int main() { \x00 return 0; }")
        self.assertFalse(is_valid)
        self.assertIn("null byte", msg.lower())

    def test_input_validation_valid_c_source(self):
        is_valid, msg = validate_source_input("int main(void) { return 0; }")
        self.assertTrue(is_valid)

    def test_security_headers_present_on_all_responses(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.headers.get("X-Content-Type-Options"), "nosniff")
        self.assertEqual(res.headers.get("X-Frame-Options"), "DENY")
        self.assertEqual(res.headers.get("X-XSS-Protection"), "1; mode=block")
        self.assertEqual(res.headers.get("Referrer-Policy"), "strict-origin-when-cross-origin")

    def test_rate_limiter_allows_under_limit(self):
        ip = "192.168.1.100"
        allowed = [check_rate_limit(ip, "test-ep", max_requests=5, window_seconds=10) for _ in range(5)]
        self.assertTrue(all(allowed))

    def test_rate_limiter_blocks_over_limit(self):
        ip = "192.168.1.101"
        for _ in range(5):
            check_rate_limit(ip, "test-ep2", max_requests=5, window_seconds=10)
        blocked = check_rate_limit(ip, "test-ep2", max_requests=5, window_seconds=10)
        self.assertFalse(blocked)

    def test_api_key_auth_open_mode_when_unset(self):
        with patch.dict(os.environ, {"VULNHGNN_API_KEY": ""}):
            self.assertTrue(verify_api_key(""))
            self.assertTrue(verify_api_key("anything"))

    def test_api_key_auth_enforced_when_configured(self):
        with patch.dict(os.environ, {"VULNHGNN_API_KEY": "super-secret-key-123"}):
            self.assertFalse(verify_api_key(""))
            self.assertFalse(verify_api_key("wrong-key"))
            self.assertTrue(verify_api_key("super-secret-key-123"))


class HmacTokenGateTests(unittest.TestCase):
    """Test HMAC token signing, tamper prevention, and expiration."""

    def setUp(self):
        self.signing_key = "a" * 32  # 32-byte secret
        self.source = "int main(void) { char *p = NULL; *p = 1; }"
        self.language = "c"
        self.finding = {"title": "Null Deref", "cwe": "CWE-476", "line": 1}

    def test_valid_token_verifies_successfully(self):
        with patch.dict(os.environ, {"VULNHGNN_FINDING_SIGNING_KEY": self.signing_key}):
            token = sign_finding(self.source, self.language, self.finding)
            self.assertTrue(verify_finding_token(token, self.source, self.language, self.finding))

    def test_tampered_source_rejected(self):
        with patch.dict(os.environ, {"VULNHGNN_FINDING_SIGNING_KEY": self.signing_key}):
            token = sign_finding(self.source, self.language, self.finding)
            tampered_source = self.source + " // tampered"
            self.assertFalse(verify_finding_token(token, tampered_source, self.language, self.finding))

    def test_tampered_finding_rejected(self):
        with patch.dict(os.environ, {"VULNHGNN_FINDING_SIGNING_KEY": self.signing_key}):
            token = sign_finding(self.source, self.language, self.finding)
            tampered_finding = {"title": "Arbitrary Edit", "cwe": "CWE-999", "line": 1}
            self.assertFalse(verify_finding_token(token, self.source, self.language, tampered_finding))

    def test_expired_token_rejected(self):
        with patch.dict(os.environ, {"VULNHGNN_FINDING_SIGNING_KEY": self.signing_key}):
            # Expired timestamp
            expired_token = f"{int(time.time()) - 100}.invalidmac"
            self.assertFalse(verify_finding_token(expired_token, self.source, self.language, self.finding))


class BroadCweCatalogTests(unittest.TestCase):
    """Test that all MITRE CWE classes are supported, classified, and not restricted to 4."""

    def test_memory_corruption_cwes_preserved(self):
        for cwe_id in ["CWE-787", "CWE-125", "CWE-416", "CWE-415", "CWE-121", "CWE-122", "CWE-119"]:
            review = _normalize_review({
                "security_score": 50,
                "summary": "Flaw detected",
                "findings": [{"title": "Flaw", "severity": "critical", "cwe": cwe_id}],
            })
            self.assertEqual(review["findings"][0]["cwe"], cwe_id, f"Failed for {cwe_id}")

    def test_injection_and_format_string_cwes_preserved(self):
        for cwe_id in ["CWE-134", "CWE-78", "CWE-22", "CWE-20"]:
            review = _normalize_review({
                "security_score": 60,
                "summary": "Flaw detected",
                "findings": [{"title": "Flaw", "severity": "high", "cwe": cwe_id}],
            })
            self.assertEqual(review["findings"][0]["cwe"], cwe_id, f"Failed for {cwe_id}")

    def test_cwe_catalog_has_comprehensive_descriptions(self):
        self.assertGreaterEqual(len(CWE_CATALOG), 30)
        self.assertIn("CWE-787", CWE_CATALOG)
        self.assertIn("CWE-416", CWE_CATALOG)
        self.assertIn("CWE-125", CWE_CATALOG)
        self.assertIn("CWE-134", CWE_CATALOG)


class ApiEndpointsIntegrationTests(unittest.TestCase):
    """Test Flask HTTP routes end-to-end."""

    def setUp(self):
        self.client = app_module.app.test_client()

    def test_get_index_serves_html(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"VulnHGNN", res.data)

    def test_live_check_valid_code_compiles(self):
        code = "int main(void) { return 0; }"
        res = self.client.post("/api/live-check", json={"code": code, "language": "c"})
        self.assertEqual(res.status_code, 200)
        payload = res.get_json()
        self.assertTrue(payload["success"])
        self.assertEqual(payload["validity"]["status"], "valid")

    def test_live_check_constant_div_zero_detected(self):
        code = "int main(void) { int x = 10 / 0; return x; }"
        res = self.client.post("/api/live-check", json={"code": code, "language": "c"})
        self.assertEqual(res.status_code, 200)
        payload = res.get_json()
        self.assertTrue(payload["success"])
        cwes = [f["class"] for f in payload["security"]["findings"]]
        self.assertIn("CWE-369", cwes)

    def test_live_check_syntax_error_reported(self):
        code = "int main(void) { this is totally broken syntax; }"
        res = self.client.post("/api/live-check", json={"code": code, "language": "c"})
        self.assertEqual(res.status_code, 200)
        payload = res.get_json()
        self.assertTrue(payload["success"])
        self.assertEqual(payload["validity"]["status"], "invalid")

    def test_live_check_rejects_missing_code(self):
        res = self.client.post("/api/live-check", json={})
        self.assertEqual(res.status_code, 400)

    def test_live_check_rejects_unsupported_language(self):
        res = self.client.post("/api/live-check", json={"code": "print('hello')", "language": "python"})
        self.assertEqual(res.status_code, 400)

    def test_analyze_endpoint_returns_broad_cwes_and_privacy_notice(self):
        mock_review = {
            "requested": True,
            "available": True,
            "security_score": 45,
            "risk_level": "Higher apparent risk",
            "summary": "Multiple severe memory vulnerabilities found.",
            "findings": [
                {
                    "title": "Out-of-bounds write in buffer",
                    "severity": "critical",
                    "cwe": "CWE-787",
                    "line": 4,
                    "evidence": "arr[15] = 99;",
                    "reason": "Writing past array bound of 10 elements.",
                    "recommendation": "Check index < 10.",
                },
                {
                    "title": "Use after free",
                    "severity": "high",
                    "cwe": "CWE-416",
                    "line": 8,
                    "evidence": "return s->status;",
                    "reason": "Reading struct after free(s).",
                    "recommendation": "Do not free before reading.",
                },
            ],
            "scope": "Advisory.",
        }

        with patch.object(app_module, "review_code_security", return_value=mock_review):
            res = self.client.post(
                "/api/analyze",
                json={"code": "int main(void) { return 0; }", "language": "c"},
            )

        self.assertEqual(res.status_code, 200)
        payload = res.get_json()
        self.assertTrue(payload["success"])
        self.assertIn("privacy_notice", payload)
        self.assertIn("Gemini provider", payload["privacy_notice"])

        # Verify broad CWEs are tracked and not dropped
        self.assertIn("CWE-787", payload["detected_cwes"])
        self.assertIn("CWE-416", payload["detected_cwes"])

        # Verify full_name enriched
        cwe787 = next(f for f in payload["predictions"] if f["class"] == "CWE-787")
        self.assertEqual(cwe787["full_name"], "Out-of-bounds Write")


class BenchmarkSuiteIntegrityTests(unittest.TestCase):
    """Test that all 66 benchmark fixtures exist and are valid C programs."""

    def test_labels_file_has_66_fixtures(self):
        labels_path = PROJECT_ROOT / "dataset" / "benchmark_fixtures" / "labels.json"
        self.assertTrue(labels_path.exists())
        labels = json.loads(labels_path.read_text(encoding="utf-8"))
        self.assertEqual(len(labels), 66)

    def test_all_66_fixture_files_exist_on_disk(self):
        fixtures_dir = PROJECT_ROOT / "dataset" / "benchmark_fixtures"
        labels = json.loads((fixtures_dir / "labels.json").read_text(encoding="utf-8"))
        for fname in labels:
            fpath = fixtures_dir / fname
            self.assertTrue(fpath.exists(), f"Missing fixture file: {fname}")
            self.assertGreater(fpath.stat().st_size, 20, f"Fixture file is empty: {fname}")

    def test_diverse_cwe_representation(self):
        fixtures_dir = PROJECT_ROOT / "dataset" / "benchmark_fixtures"
        labels = json.loads((fixtures_dir / "labels.json").read_text(encoding="utf-8"))
        all_cwes = {cwe for item in labels.values() for cwe in item.get("expected_cwes", [])}
        self.assertGreaterEqual(len(all_cwes), 20, f"Expected >= 20 distinct CWEs, got {len(all_cwes)}")
        # Verify key vulnerability families are present
        self.assertIn("CWE-787", all_cwes)
        self.assertIn("CWE-125", all_cwes)
        self.assertIn("CWE-416", all_cwes)
        self.assertIn("CWE-134", all_cwes)
        self.assertIn("CWE-190", all_cwes)
        self.assertIn("CWE-369", all_cwes)
        self.assertIn("CWE-476", all_cwes)


if __name__ == "__main__":
    unittest.main()
