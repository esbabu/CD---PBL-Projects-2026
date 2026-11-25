import os
from pathlib import Path
import unittest
from unittest.mock import patch

from backend.app.services import cpp_analysis


class FakeScaler:
    def transform(self, values):
        return values


class FakeModel:
    def predict(self, values):
        return [0]

    def predict_proba(self, values):
        return [[0.8]]


class FakeLabelEncoder:
    def inverse_transform(self, values):
        return ["MISSING_SEMICOLON"]


class CppAnalysisTests(unittest.TestCase):
    def test_returns_structured_result_and_removes_temporary_source(self):
        seen_paths = []

        def tokenize(path):
            seen_paths.append(path)
            self.assertTrue(Path(path).is_file())
            self.assertEqual(Path(path).read_text(encoding="utf-8"), "int value = 1\n")
            return [{"line": 1, "column": 1, "token_type": "KEYWORD", "token_value": "int"}]

        def build_ast(tokens):
            return object(), ["[ParseError @ line 1] Missing ';' — MISSING_SEMICOLON"]

        with patch.object(cpp_analysis, "_legacy_pipeline", return_value=(tokenize, build_ast, lambda root, errors: {})), patch.object(
            cpp_analysis, "_load_artifacts", return_value=(FakeModel(), FakeScaler(), FakeLabelEncoder())
        ):
            result = cpp_analysis.analyze_cpp_source("int value = 1\n")

        self.assertEqual(result["language"], "cpp")
        self.assertEqual(result["analysisVersion"], "cpp-legacy-ml-v1")
        self.assertEqual(result["classification"], {
            "label": "MISSING_SEMICOLON", "confidence": 80.0, "source": "model"
        })
        self.assertEqual(result["summary"], {
            "diagnosticCount": 2,
            "parserDiagnosticCount": 1,
            "sourceHeuristicDiagnosticCount": 1,
        })
        self.assertEqual(result["diagnostics"][0]["column"], None)
        self.assertEqual(result["diagnostics"][1]["column"], 14)
        self.assertFalse(os.path.exists(seen_paths[0]))

    def test_source_length_limit_rejects_input_before_pipeline_access(self):
        with patch.object(cpp_analysis, "_legacy_pipeline") as pipeline:
            with self.assertRaises(ValueError):
                cpp_analysis.analyze_cpp_source("x" * (cpp_analysis.MAX_SOURCE_LENGTH + 1))
        pipeline.assert_not_called()

    def test_source_diagnostics_report_unknown_columns_as_none(self):
        diagnostics = cpp_analysis._source_diagnostics('int main() {\n  cout << "unterminated;\n')

        by_category = {item["category"]: item for item in diagnostics}
        self.assertEqual(by_category["UNTERMINATED_STRING"]["line"], 2)
        self.assertIsNone(by_category["UNTERMINATED_STRING"]["column"])
        self.assertIsNone(by_category["UNMATCHED_BRACE"]["line"])
        self.assertIsNone(by_category["UNMATCHED_BRACE"]["column"])

    def test_artifacts_are_resolved_from_project_root(self):
        self.assertEqual(cpp_analysis.PROJECT_ROOT, Path(__file__).resolve().parents[2])
        self.assertEqual(cpp_analysis.ARTIFACT_PATHS["model"], cpp_analysis.PROJECT_ROOT / "model.pkl")

    def test_clean_cpp_code_normalizes_classification_to_clean(self):
        def tokenize(path):
            return [{"line": 1, "column": 1, "token_type": "KEYWORD", "token_value": "int"}]

        def build_ast(tokens):
            return object(), []  # 0 parse errors

        with patch.object(cpp_analysis, "_legacy_pipeline", return_value=(tokenize, build_ast, lambda root, errors: {})), patch.object(
            cpp_analysis, "_load_artifacts", return_value=(FakeModel(), FakeScaler(), FakeLabelEncoder())
        ), patch.object(cpp_analysis, "_source_diagnostics", return_value=[]):  # 0 source diagnostics
            result = cpp_analysis.analyze_cpp_source("int main() { return 0; }\n")

        self.assertEqual(result["language"], "cpp")
        self.assertEqual(result["summary"]["diagnosticCount"], 0)
        self.assertEqual(result["classification"]["label"], "CLEAN")
        self.assertEqual(result["classification"]["confidence"], 100.0)
        self.assertEqual(result["classification"]["source"], "model")

    def test_artifacts_load_once_and_cache_in_memory(self):
        cpp_analysis._clear_artifact_cache()
        try:
            with patch("joblib.load") as mock_joblib_load:
                mock_joblib_load.side_effect = [FakeModel(), FakeScaler(), FakeLabelEncoder()]
                artifacts_first = cpp_analysis._load_artifacts()
                self.assertEqual(mock_joblib_load.call_count, 3)

                artifacts_second = cpp_analysis._load_artifacts()
                # No additional joblib.load calls on second invocation
                self.assertEqual(mock_joblib_load.call_count, 3)
                self.assertIs(artifacts_first, artifacts_second)
        finally:
            cpp_analysis._clear_artifact_cache()

    def test_concurrent_load_artifacts_is_thread_safe(self):
        import concurrent.futures
        cpp_analysis._clear_artifact_cache()

        try:
            with patch("joblib.load") as mock_joblib_load:
                mock_joblib_load.side_effect = [FakeModel(), FakeScaler(), FakeLabelEncoder()]

                results = []
                with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
                    futures = [executor.submit(cpp_analysis._load_artifacts) for _ in range(16)]
                    for future in concurrent.futures.as_completed(futures):
                        results.append(future.result())

                # joblib.load must be invoked exactly 3 times across all concurrent threads
                self.assertEqual(mock_joblib_load.call_count, 3)
                # All threads must receive the identical cached artifact tuple
                first = results[0]
                for item in results[1:]:
                    self.assertIs(item, first)
        finally:
            cpp_analysis._clear_artifact_cache()

    def test_missing_artifact_raises_runtime_error(self):
        cpp_analysis._clear_artifact_cache()
        try:
            with patch.dict(cpp_analysis.ARTIFACT_PATHS, {"model": Path("/non/existent/path/model.pkl")}):
                with self.assertRaises(RuntimeError) as ctx:
                    cpp_analysis._load_artifacts()
                self.assertIn("Missing C++ classifier artifact(s)", str(ctx.exception))
        finally:
            cpp_analysis._clear_artifact_cache()

    def test_corrupted_artifact_raises_runtime_error(self):
        cpp_analysis._clear_artifact_cache()
        try:
            with patch("joblib.load", side_effect=ValueError("Corrupted pickle stream")):
                with self.assertRaises(RuntimeError) as ctx:
                    cpp_analysis._load_artifacts()
                self.assertIn("Corrupted or unreadable C++ classifier artifact(s)", str(ctx.exception))
        finally:
            cpp_analysis._clear_artifact_cache()

    def test_predictions_remain_consistent_across_repeated_runs(self):
        cpp_analysis._clear_artifact_cache()
        source = "int main() {\n    int a = 10\n    return 0;\n}\n"
        res1 = cpp_analysis.analyze_cpp_source(source)
        res2 = cpp_analysis.analyze_cpp_source(source)
        self.assertEqual(res1["classification"], res2["classification"])
        self.assertEqual(res1["summary"], res2["summary"])
        self.assertEqual(len(res1["diagnostics"]), len(res2["diagnostics"]))
        self.assertEqual(res1["diagnostics"][0]["category"], res2["diagnostics"][0]["category"])


if __name__ == "__main__":
    unittest.main()
