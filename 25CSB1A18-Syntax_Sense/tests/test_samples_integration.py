"""End-to-end integration test verifying all frontend sample snippets against the API."""

import unittest
from fastapi.testclient import TestClient
from backend.app.main import app


class SamplesIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_all_cpp_samples(self):
        cpp_samples = [
            ("missing-semicolon", "#include <iostream>\n\nint main() {\n    int total = 100\n    std::cout << \"Total: \" << total << std::endl;\n    return 0;\n}\n", 1),
            ("unmatched-brace", "#include <iostream>\n\nint main() {\n    if (true) {\n        int x = 1;\n    return 0;\n}\n", 1),
            ("unmatched-closing-brace", "#include <iostream>\n\nint main() {\n    int a = 1;\n    return 0;\n}}\n", 1),
            ("unmatched-paren", "#include <iostream>\n\nint main() {\n    int x = 10;\n    if (x > 5 {\n        std::cout << \"Greater\" << std::endl;\n    }\n    return 0;\n}\n", 1),
            ("invalid-assignment", "#include <iostream>\n\nint main() {\n    int x = 10;\n    42 = x;\n    return 0;\n}\n", 1),
            ("missing-operand", "#include <iostream>\n\nint main() {\n    int total = 10 + ;\n    return 0;\n}\n", 1),
            ("unexpected-token", "#include <iostream>\n\nint main() {\n    int x = 5 @ 10;\n    return 0;\n}\n", 1),
            ("multiple-errors", "#include <iostream>\n\nint main() {\n    int a = 10\n    100 = a;\n    if (a > 0 {\n        return 1;\n    }\n    return 0;\n}\n", 2),
            ("valid-program", "#include <iostream>\n\nint main() {\n    int value = 42;\n    std::cout << \"The answer is: \" << value << std::endl;\n    return 0;\n}\n", 0),
        ]

        for sid, code, min_diags in cpp_samples:
            with self.subTest(sample_id=sid):
                res = self.client.post("/api/v1/analyze", json={"language": "cpp", "code": code})
                self.assertEqual(res.status_code, 200)
                data = res.json()
                count = data["summary"]["diagnosticCount"]
                if min_diags == 0:
                    self.assertEqual(count, 0)
                    self.assertEqual(data["classification"]["label"], "CLEAN")
                else:
                    self.assertGreaterEqual(count, min_diags)

    def test_all_python_samples(self):
        py_samples = [
            ("valid-python", "def greet(name: str, count: int = 1) -> None:\n    for i in range(count):\n        print(f\"Hello, {name}! ({i + 1})\")\n\ngreet(\"SyntaxSense\", 3)\n", 0, "CLEAN"),
            ("missing-colon-py", "def check_number(val: int) -> str:\n    if val > 0\n        return \"Positive\"\n    return \"Non-positive\"\n\nprint(check_number(10))\n", 1, "MISSING_COLON"),
            ("indentation-error-py", "def process_items(items):\n    results = []\n    for item in items:\n        results.append(item * 2)\n      print(\"Processed item\")\n    return results\n\nprint(process_items([1, 2, 3]))\n", 1, "UNINDENT_MISMATCH"),
            ("unmatched-delimiter-py", "scores = [98, 85, 92, 77\naverage = sum(scores) / len(scores)\nprint(f\"Average: {average}\")\n", 1, "UNMATCHED_DELIMITER"),
            ("unclosed-string-py", "greeting = \"Welcome to SyntaxSense\nprint(greeting)\n", 1, "UNTERMINATED_STRING"),
            ("invalid-assignment-py", "total = 50\n100 = total\nprint(total)\n", 1, "INVALID_ASSIGNMENT"),
        ]

        for sid, code, min_diags, exp_cat in py_samples:
            with self.subTest(sample_id=sid):
                res = self.client.post("/api/v1/analyze", json={"language": "python", "code": code})
                self.assertEqual(res.status_code, 200)
                data = res.json()
                count = data["summary"]["diagnosticCount"]
                label = data["classification"]["label"]
                if min_diags == 0:
                    self.assertEqual(count, 0)
                    self.assertEqual(data["classification"]["label"], "CLEAN")
                else:
                    self.assertGreaterEqual(count, min_diags)
                    self.assertEqual(label, exp_cat)

    def test_all_java_samples(self):
        java_samples = [
            ("valid-java", "public class Calculator {\n    public static int add(int a, int b) {\n        return a + b;\n    }\n\n    public static void main(String[] args) {\n        System.out.println(\"Result: \" + add(5, 7));\n    }\n}\n", 0, "CLEAN"),
            ("missing-semicolon-java", "public class Main {\n    public static void main(String[] args) {\n        int x = 10\n        System.out.println(x);\n    }\n}\n", 1, "MISSING_SEMICOLON"),
            ("unmatched-brace-java", "public class UnmatchedBrace {\n    public static void main(String[] args) {\n        if (true) {\n            System.out.println(\"Missing closing brace\");\n    }\n}\n", 1, "UNMATCHED_BRACE"),
            ("unmatched-paren-java", "public class UnmatchedParen {\n    public static void main(String[] args) {\n        int x = 10;\n        if (x > 5 {\n            System.out.println(\"Missing closing parenthesis\");\n        }\n    }\n}\n", 1, "UNMATCHED_PARANTHESES"),
            ("invalid-conditional-java", "public class InvalidConditional {\n    public static void main(String[] args) {\n        int x = 10;\n        if x > 5 {\n            System.out.println(\"Missing parentheses around condition\");\n        }\n    }\n}\n", 1, "INVALID_CONDITIONAL"),
            ("invalid-assignment-java", "public class InvalidAssignment {\n    public static void main(String[] args) {\n        int count = 5;\n        10 = count;\n        System.out.println(count);\n    }\n}\n", 1, "INVALID_ASSIGNMENT"),
        ]

        for sid, code, min_diags, exp_cat in java_samples:
            with self.subTest(sample_id=sid):
                res = self.client.post("/api/v1/analyze", json={"language": "java", "code": code})
                self.assertEqual(res.status_code, 200)
                data = res.json()
                count = data["summary"]["diagnosticCount"]
                label = data["classification"]["label"]
                if min_diags == 0:
                    self.assertEqual(count, 0)
                    self.assertEqual(data["classification"]["label"], "CLEAN")
                else:
                    self.assertGreaterEqual(count, min_diags)
                    self.assertEqual(label, exp_cat)

    def test_unsupported_language_returns_error(self):
        res = self.client.post("/api/v1/analyze", json={"language": "rust", "code": "fn main() {}"})
        self.assertEqual(res.status_code, 422)
        data = res.json()
        self.assertEqual(data["error"]["code"], "unsupported_language")
        self.assertIn("java", data["error"]["supportedLanguages"])


if __name__ == "__main__":
    unittest.main()
