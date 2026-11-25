import unittest
from unittest.mock import patch

try:
    from fastapi.testclient import TestClient
    from backend.app.main import app
except ModuleNotFoundError as exc:
    raise unittest.SkipTest(
        "API tests require FastAPI and HTTPX; install them in .venv before running this suite."
    ) from exc


class AnalyzeEndpointTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    @patch("backend.app.services.cpp_analyzer.analyze_cpp_source")
    def test_valid_cpp_request_delegates_to_adapter(self, analyze_cpp_source):
        adapter_result = {
            "language": "cpp",
            "analysisVersion": "cpp-legacy-ml-v1",
            "classification": {"label": "MISSING_SEMICOLON", "confidence": 80.0, "source": "model"},
            "diagnostics": [],
            "summary": {"diagnosticCount": 0, "parserDiagnosticCount": 0, "sourceHeuristicDiagnosticCount": 0},
        }
        analyze_cpp_source.return_value = adapter_result

        response = self.client.post(
            "/api/v1/analyze", json={"language": "cpp", "code": "int main() {}"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), adapter_result)
        analyze_cpp_source.assert_called_once_with("int main() {}")

    def test_invalid_request_returns_structured_validation_error(self):
        response = self.client.post(
            "/api/v1/analyze", json={"language": "cpp", "code": 123}
        )

        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["error"]["code"], "invalid_request")

    def test_unsupported_language_returns_structured_error(self):
        response = self.client.post(
            "/api/v1/analyze", json={"language": "ruby", "code": "puts 'hello'"}
        )

        self.assertEqual(response.status_code, 422)
        data = response.json()
        self.assertEqual(data["error"]["code"], "unsupported_language")
        self.assertIn("cpp", data["error"]["supportedLanguages"])
        self.assertIn("python", data["error"]["supportedLanguages"])
        self.assertIn("java", data["error"]["supportedLanguages"])

    def test_java_language_returns_success_via_api(self):
        response = self.client.post(
            "/api/v1/analyze", json={"language": "java", "code": "public class Main { public static void main(String[] args) {} }"}
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["language"], "java")
        self.assertEqual(data["summary"]["diagnosticCount"], 0)
        self.assertEqual(data["classification"]["label"], "CLEAN")

    def test_python_language_returns_success_via_api(self):
        response = self.client.post(
            "/api/v1/analyze", json={"language": "python", "code": "x = 42\nprint(x)\n"}
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["language"], "python")
        self.assertEqual(data["summary"]["diagnosticCount"], 0)
        self.assertEqual(data["classification"]["label"], "CLEAN")

    @patch("backend.app.services.cpp_analyzer.analyze_cpp_source", side_effect=RuntimeError("model unavailable"))
    def test_adapter_error_returns_safe_structured_error(self, analyze_cpp_source):
        response = self.client.post(
            "/api/v1/analyze", json={"language": "cpp", "code": "int main() {}"}
        )

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json(), {
            "error": {
                "code": "analysis_failed",
                "message": "C++ analysis could not be completed.",
            }
        })
        analyze_cpp_source.assert_called_once()

    def test_healthcheck_returns_ok_status(self):
        response = self.client.get("/api/v1/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["supportedLanguage"], "cpp")
        self.assertIn("cpp", data["supportedLanguages"])
        self.assertIn("python", data["supportedLanguages"])
        self.assertIn("java", data["supportedLanguages"])

    def test_root_returns_ok_status(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    @patch("backend.app.services.cpp_analyzer.analyze_cpp_source")
    def test_cpp_alias_cplusplus_resolves_cleanly(self, analyze_cpp_source):
        analyze_cpp_source.return_value = {
            "language": "cpp",
            "analysisVersion": "cpp-legacy-ml-v1",
            "classification": {"label": "CLEAN", "confidence": 100.0, "source": "model"},
            "diagnostics": [],
            "summary": {"diagnosticCount": 0, "parserDiagnosticCount": 0, "sourceHeuristicDiagnosticCount": 0},
        }
        for alias in ["c++", "C++", "cplusplus"]:
            response = self.client.post("/api/v1/analyze", json={"language": alias, "code": "int main() {}"})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["language"], "cpp")

    def test_global_exception_handler_returns_valid_json_on_unexpected_error(self):
        client = TestClient(app, raise_server_exceptions=False)
        with patch("backend.app.services.registry.AnalyzerRegistry.get_analyzer", side_effect=RuntimeError("Critical system failure")):
            response = client.post("/api/v1/analyze", json={"language": "cpp", "code": "int main() {}"})
            self.assertEqual(response.status_code, 500)
            self.assertEqual(response.headers.get("content-type"), "application/json")
            data = response.json()
            self.assertIn("error", data)
            self.assertIn("message", data["error"])
            self.assertIn("Critical system failure", data["error"]["message"])


if __name__ == "__main__":
    unittest.main()
