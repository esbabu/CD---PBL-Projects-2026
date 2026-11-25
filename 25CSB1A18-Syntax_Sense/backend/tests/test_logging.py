"""Unit tests for centralized structured logging in SyntaxSense."""

import logging
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.app.logging_config import DEFAULT_LOGGER_NAME, get_logger, setup_logging
from backend.app.main import app


class LoggingConfigTests(unittest.TestCase):
    def test_setup_logging_configures_handler_and_level(self):
        logger = setup_logging(level="DEBUG")
        self.assertEqual(logger.level, logging.DEBUG)
        self.assertGreaterEqual(len(logger.handlers), 1)
        self.assertFalse(logger.propagate)

    def test_setup_logging_avoids_duplicate_handlers(self):
        logger = setup_logging()
        initial_count = len(logger.handlers)

        # Calling setup_logging multiple times should not add duplicate handlers
        setup_logging()
        setup_logging()
        self.assertEqual(len(logger.handlers), initial_count)

    def test_get_logger_returns_namespaced_child(self):
        logger = get_logger("services.cpp")
        self.assertEqual(logger.name, f"{DEFAULT_LOGGER_NAME}.services.cpp")

        root_named = get_logger(DEFAULT_LOGGER_NAME)
        self.assertEqual(root_named.name, DEFAULT_LOGGER_NAME)


class ApiLoggingIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_analyze_request_logs_metadata_without_source_code(self):
        secret_marker = "SUPER_SECRET_TOKEN_DO_NOT_LOG"
        sample_code = f"int main() {{ return 0; }} // {secret_marker}\n"

        with self.assertLogs("syntaxsense.api", level="INFO") as captured:
            response = self.client.post("/api/v1/analyze", json={"language": "cpp", "code": sample_code})
            self.assertEqual(response.status_code, 200)

        log_text = "\n".join(captured.output)
        # Verify metadata logged
        self.assertIn("Received analyze request", log_text)
        self.assertIn("language='cpp'", log_text)
        self.assertIn("Analysis completed", log_text)
        self.assertIn("duration=", log_text)
        # Verify submitted source code is NOT logged
        self.assertNotIn(secret_marker, log_text)

    def test_unexpected_exception_logs_exception_traceback(self):
        with patch("backend.app.services.cpp_analyzer.analyze_cpp_source", side_effect=RuntimeError("Test crash")):
            with self.assertLogs("syntaxsense.api", level="ERROR") as captured:
                response = self.client.post("/api/v1/analyze", json={"language": "cpp", "code": "int main() {}"})
                self.assertEqual(response.status_code, 500)

        log_text = "\n".join(captured.output)
        self.assertIn("Unhandled exception during C++ analysis", log_text)
        self.assertIn("Test crash", log_text)


if __name__ == "__main__":
    unittest.main()
