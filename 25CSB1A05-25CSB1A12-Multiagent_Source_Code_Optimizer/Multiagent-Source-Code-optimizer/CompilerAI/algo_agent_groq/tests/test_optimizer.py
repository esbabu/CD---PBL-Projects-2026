import unittest

from algo_agent.optimizer import OptimizationError, Optimizer, detect_language
from algo_agent.validation import validate_source


class FakeClient:
    def __init__(self, response):
        self.response = response

    def generate_json(self, system_prompt, user_prompt):
        return self.response


class OptimizerTests(unittest.TestCase):
    def test_language_detection_for_all_supported_languages(self):
        cases = {
            "source.c": "c",
            "source.h": "c",
            "source.cpp": "cpp",
            "source.hpp": "cpp",
            "source.py": "python",
            "source.js": "javascript",
            "source.mjs": "javascript",
        }
        for filename, expected in cases.items():
            with self.subTest(filename=filename):
                self.assertEqual(detect_language("", filename), expected)

    def test_explicit_language_aliases(self):
        self.assertEqual(detect_language("", explicit="c++"), "cpp")
        self.assertEqual(detect_language("", explicit="js"), "javascript")
        self.assertEqual(detect_language("", explicit="py"), "python")

    def test_python_syntax_validation(self):
        self.assertTrue(validate_source("def f(): return 1", "python").valid)
        self.assertFalse(validate_source("def f(:", "python").valid)

    def test_valid_python_candidate_is_returned(self):
        original = "def contains(items, target):\n    for item in items:\n        if item == target: return True\n    return False\n"
        candidate = "def contains(items, target):\n    return target in items\n"
        client = FakeClient({
            "optimized_code": candidate,
            "time_complexity_before": "O(n)",
            "time_complexity_after": "O(n)",
            "space_complexity_before": "O(1)",
            "space_complexity_after": "O(1)",
            "summary": "Use built-in membership.",
            "changes": ["Simplified the search."],
        })
        result = Optimizer(client=client).optimize(original, "sample.py")
        self.assertEqual(result.optimized_code, candidate)
        self.assertTrue(result.optimized)
        self.assertTrue(result.validation["valid"])

    def test_invalid_candidate_falls_back_to_original(self):
        original = "def add(a, b):\n    return a + b\n"
        client = FakeClient({
            "optimized_code": "def add(:\n    pass\n",
            "summary": "invalid candidate",
            "changes": [],
        })
        result = Optimizer(client=client).optimize(original, "add.py")
        self.assertEqual(result.optimized_code, original)
        self.assertFalse(result.optimized)
        self.assertTrue(result.warnings)

    def test_empty_input_is_rejected(self):
        with self.assertRaises(OptimizationError):
            Optimizer(client=FakeClient({})).optimize("", "empty.py")

    def test_unsupported_language_is_rejected(self):
        with self.assertRaises(OptimizationError):
            detect_language("", "file.java")


if __name__ == "__main__":
    unittest.main()
