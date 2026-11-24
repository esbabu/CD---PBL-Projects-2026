"""
Unit tests for OptimizationAgent and time complexity tutoring
"""

import unittest
from src.optimizer import OptimizationAgent
from src.error_capture import ErrorCapture
from src.pipeline import AIErrorTutor


class TestOptimizationAgent(unittest.TestCase):

    def setUp(self):
        self.error_capture = ErrorCapture()
        self.optimizer = OptimizationAgent(self.error_capture)
        self.tutor = AIErrorTutor(use_ai=False)

    def test_exponential_recursion_optimization(self):
        code = """def fib(n):
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)

print(fib(5))"""
        res = self.optimizer.analyze_and_optimize(code)
        self.assertTrue(res["success"])
        self.assertTrue(res["has_bottleneck"])
        self.assertIn("2ᴺ", res["original_complexity"])
        self.assertIn("lru_cache", res["candidate_code"])
        self.assertTrue(res["is_validated"])
        self.assertIn("Dynamic Programming", res["tutoring"]["concept"])

    def test_membership_in_loop_optimization(self):
        code = """items = [1, 2, 3, 4, 5]
target_list = [3, 4, 10]
found = []
for x in items:
    if x in target_list:
        found.append(x)
print(found)"""
        res = self.optimizer.analyze_and_optimize(code)
        self.assertTrue(res["success"])
        self.assertTrue(res["has_bottleneck"])
        self.assertIn("target_list_set", res["candidate_code"])
        self.assertTrue(res["is_validated"])
        self.assertIn("Hash Set", res["tutoring"]["concept"])

    def test_pop_zero_queue_optimization(self):
        code = """queue = [1, 2, 3, 4, 5]
while queue:
    item = queue.pop(0)
    print(item)"""
        res = self.optimizer.analyze_and_optimize(code)
        self.assertTrue(res["success"])
        self.assertTrue(res["has_bottleneck"])
        self.assertIn("popleft()", res["candidate_code"])
        self.assertIn("deque", res["candidate_code"])
        self.assertIn("Doubly-Linked Lists", res["tutoring"]["concept"])

    def test_string_concatenation_in_loop(self):
        code = """words = ['hello', 'world', 'python']
result = ""
for w in words:
    result += w
print(result)"""
        res = self.optimizer.analyze_and_optimize(code)
        self.assertTrue(res["success"])
        self.assertTrue(res["has_bottleneck"])
        self.assertIn("Buffer & Join", res["tutoring"]["concept"])

    def test_already_optimal_code(self):
        code = """total = 0
for i in range(100):
    total += i
print(total)"""
        res = self.optimizer.analyze_and_optimize(code)
        self.assertTrue(res["success"])
        self.assertFalse(res["has_bottleneck"])
        self.assertIn("O(N)", res["original_complexity"])

    def test_syntax_error_prevention(self):
        code = """def broken(x)
    return x"""
        res = self.optimizer.analyze_and_optimize(code)
        self.assertFalse(res["success"])
        self.assertTrue(res["has_syntax_error"])

    def test_pipeline_integration(self):
        code = """def fib(n):
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)"""
        res = self.tutor.optimize_code(code)
        self.assertTrue(res["success"])
        self.assertTrue(res["has_bottleneck"])


if __name__ == "__main__":
    unittest.main()
