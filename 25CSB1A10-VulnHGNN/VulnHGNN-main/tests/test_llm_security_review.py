import unittest

from src.llm_security_review import _normalize_review


class GeminiReviewNormalizationTests(unittest.TestCase):
    def test_supported_cwe_is_preserved(self):
        review = _normalize_review({
            "security_score": 70,
            "summary": "Potential integer overflow.",
            "findings": [{"title": "Overflow", "severity": "high", "cwe": "CWE-190"}],
        })

        self.assertEqual(review["findings"][0]["cwe"], "CWE-190")

    def test_unsupported_cwe_is_not_promoted_to_supported_class(self):
        review = _normalize_review({
            "security_score": 70,
            "summary": "Potential issue.",
            "findings": [{"title": "Issue", "severity": "medium", "cwe": "CWE-999"}],
        })

        self.assertIsNone(review["findings"][0]["cwe"])

    def test_malformed_cwe_is_discarded(self):
        review = _normalize_review({
            "security_score": 70,
            "summary": "Potential issue.",
            "findings": [{"title": "Issue", "severity": "medium", "cwe": ["CWE-190"]}],
        })

        self.assertIsNone(review["findings"][0]["cwe"])


if __name__ == "__main__":
    unittest.main()
