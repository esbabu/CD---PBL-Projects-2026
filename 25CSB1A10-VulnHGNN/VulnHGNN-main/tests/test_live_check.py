import tempfile
import unittest
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import patch

from src import app as app_module


class LiveCheckEndpointTests(unittest.TestCase):
    def test_live_check_uses_only_local_clang_checks(self):
        with tempfile.NamedTemporaryFile(suffix=".ll", delete=False) as ir_file:
            ir_path = Path(ir_file.name)
        try:
            with ExitStack() as stack:
                stack.enter_context(patch.object(app_module, "MODEL", object()))
                stack.enter_context(
                    patch.object(app_module, "compile_to_ll", return_value=str(ir_path))
                )
                stack.enter_context(
                    patch.object(
                        app_module, "find_division_by_zero_warnings", return_value=[4]
                    )
                )
                agent_review = stack.enter_context(
                    patch.object(app_module, "review_code_security")
                )
                response = app_module.app.test_client().post(
                    "/api/live-check",
                    json={"code": "int main(void) { return 1; }", "language": "c"},
                )

            payload = response.get_json()
            self.assertEqual(response.status_code, 200, payload)
            self.assertEqual(
                payload["security"]["checked_classes"],
                ["CWE-369"],
            )
            self.assertEqual(
                {finding["class"] for finding in payload["security"]["findings"]},
                {"CWE-369"},
            )
            divide_by_zero = next(
                finding for finding in payload["security"]["findings"]
                if finding["class"] == "CWE-369"
            )
            self.assertEqual(divide_by_zero["severity"], "CLANG CONFIRMED")
            self.assertEqual(divide_by_zero["lines"], [4])
            self.assertEqual(payload["security"]["predictions"], [])
            self.assertIn("do not call Gemini", payload["security"]["scope"])
            agent_review.assert_not_called()
            self.assertFalse(ir_path.exists())
        finally:
            if ir_path.exists():
                ir_path.unlink()


class AgentAnalyzeEndpointTests(unittest.TestCase):
    def test_analyze_uses_agent_and_clang_without_loading_gnn(self):
        with tempfile.NamedTemporaryFile(suffix=".ll", delete=False) as ir_file:
            ir_path = Path(ir_file.name)
        review = {
            "requested": True,
            "available": True,
            "security_score": 72,
            "risk_level": "Moderate apparent risk",
            "summary": "Potential integer overflow.",
            "findings": [{
                "title": "Unchecked addition",
                "severity": "high",
                "cwe": "CWE-190",
                "line": 3,
                "evidence": "The addition can exceed the type range.",
                "reason": "The input is not bounded.",
                "recommendation": "Check the arithmetic bounds.",
            }],
            "scope": "Advisory only.",
        }
        try:
            with ExitStack() as stack:
                stack.enter_context(patch.object(app_module, "MODEL", None))
                stack.enter_context(
                    patch.object(app_module, "compile_to_ll", return_value=str(ir_path))
                )
                stack.enter_context(
                    patch.object(
                        app_module, "find_division_by_zero_warnings", return_value=[5]
                    )
                )
                review_call = stack.enter_context(
                    patch.object(app_module, "review_code_security", return_value=review)
                )
                predict_call = stack.enter_context(
                    patch.object(app_module, "predict_file")
                )
                response = app_module.app.test_client().post(
                    "/api/analyze",
                    json={"code": "int main(void) { return 0; }", "language": "c"},
                )

            payload = response.get_json()
            self.assertEqual(response.status_code, 200, payload)
            self.assertEqual(payload["detected_cwes"], ["CWE-190", "CWE-369"])
            self.assertEqual(payload["security_estimate"]["score"], 72)
            self.assertEqual(
                {finding["source"] for finding in payload["predictions"]},
                {"Gemini agent", "Clang"},
            )
            review_call.assert_called_once()
            predict_call.assert_not_called()
            self.assertFalse(ir_path.exists())
        finally:
            if ir_path.exists():
                ir_path.unlink()

    def test_analyze_fails_explicitly_when_agent_is_unavailable(self):
        with tempfile.NamedTemporaryFile(suffix=".ll", delete=False) as ir_file:
            ir_path = Path(ir_file.name)
        try:
            with ExitStack() as stack:
                stack.enter_context(
                    patch.object(app_module, "compile_to_ll", return_value=str(ir_path))
                )
                stack.enter_context(
                    patch.object(app_module, "find_division_by_zero_warnings", return_value=[])
                )
                stack.enter_context(
                    patch.object(
                        app_module,
                        "review_code_security",
                        return_value={
                            "requested": True,
                            "available": False,
                            "message": "Provider unavailable.",
                        },
                    )
                )
                response = app_module.app.test_client().post(
                    "/api/analyze",
                    json={"code": "int main(void) { return 0; }", "language": "c"},
                )

            payload = response.get_json()
            self.assertEqual(response.status_code, 503)
            self.assertFalse(payload["success"])
            self.assertIn("no agent-based analysis result", payload["error"])
            self.assertEqual(payload["security_checks"]["clang_compilation"], "passed")
            self.assertFalse(ir_path.exists())
        finally:
            if ir_path.exists():
                ir_path.unlink()


if __name__ == "__main__":
    unittest.main()
