"""Unit tests verifying lexical token extraction across C++, Python, and Java analyzers."""

from __future__ import annotations

import unittest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.services.java_analyzer import JavaAnalyzer
from backend.app.services.python_analyzer import PythonAnalyzer


class TestTokenStreamExtraction(unittest.TestCase):
    """Verifies that each analyzer produces structured lexical tokens."""

    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_java_tokens_structure_and_types(self) -> None:
        analyzer = JavaAnalyzer()
        code = (
            "public class Main {\n"
            "    public static void main(String[] args) {\n"
            "        int x = 10;\n"
            "        System.out.println(x);\n"
            "    }\n"
            "}"
        )
        res = analyzer.analyze(code)
        self.assertIn("tokens", res)
        tokens = res["tokens"]
        self.assertGreater(len(tokens), 0)

        # Verify fields
        for tok in tokens:
            self.assertIn("type", tok)
            self.assertIn("value", tok)
            self.assertIn("line", tok)
            self.assertIn("column", tok)
            self.assertIsInstance(tok["line"], int)
            self.assertIsInstance(tok["column"], int)

        types = {t["type"] for t in tokens}
        self.assertIn("KEYWORD", types)
        self.assertIn("IDENTIFIER", types)
        self.assertIn("LITERAL_INT", types)
        self.assertIn("SEMICOLON", types)
        self.assertIn("OPEN_BRACE", types)
        self.assertIn("CLOSE_BRACE", types)

    def test_python_tokens_structure_and_types(self) -> None:
        analyzer = PythonAnalyzer()
        code = "def greet(name):\n    return f'Hello, {name}'\n"
        res = analyzer.analyze(code)
        self.assertIn("tokens", res)
        tokens = res["tokens"]
        self.assertGreater(len(tokens), 0)

        # Verify fields
        for tok in tokens:
            self.assertIn("type", tok)
            self.assertIn("value", tok)
            self.assertIn("line", tok)
            self.assertIn("column", tok)

        types = {t["type"] for t in tokens}
        self.assertIn("NAME", types)
        self.assertIn("OP", types)

    def test_api_returns_tokens_java(self) -> None:
        response = self.client.post(
            "/api/v1/analyze",
            json={"language": "java", "code": "class A { int x = 1; }"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("tokens", data)
        self.assertIsInstance(data["tokens"], list)
        self.assertGreater(len(data["tokens"]), 0)

    def test_api_returns_tokens_python(self) -> None:
        response = self.client.post(
            "/api/v1/analyze",
            json={"language": "python", "code": "x = 42\ny = x + 1\n"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("tokens", data)
        self.assertIsInstance(data["tokens"], list)
        self.assertGreater(len(data["tokens"]), 0)

    def test_api_returns_tokens_cpp(self) -> None:
        response = self.client.post(
            "/api/v1/analyze",
            json={"language": "cpp", "code": "int main() { return 0; }"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("tokens", data)
        self.assertIsInstance(data["tokens"], list)
        self.assertGreater(len(data["tokens"]), 0)


if __name__ == "__main__":
    unittest.main()
