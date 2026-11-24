import unittest
from pathlib import Path

from src.predict import run_model_per_function, validate_ir_with_clang


class RunModelPerFunctionTests(unittest.TestCase):
    def test_no_source_functions_is_not_reported_as_clean(self):
        with self.assertRaisesRegex(RuntimeError, "No analyzable functions"):
            run_model_per_function(
                {"source_file": "", "functions": []},
                model=None,
                device=None,
                threshold=0.5,
            )

    def test_relative_source_path_does_not_drop_user_functions(self):
        source_path = "test_files/test_10_all_vulnerabilities.c"
        function = {
            "name": "the_ultimate_test",
            "source_file": str(Path(source_path).resolve()),
            "is_declaration": False,
            "blocks": [{"instructions": [
                {"text": "%1 = add i32 %a, %b"},
                {"text": "%2 = sub i32 %b, 1"},
                {"text": "ret i32 %2"},
            ]}],
        }
        with self.assertLogs("predict", level="ERROR"):
            with self.assertRaisesRegex(
                RuntimeError,
                "Inference failed for source function the_ultimate_test",
            ):
                run_model_per_function(
                    {"source_file": source_path, "functions": [function]},
                    model=None,
                    device=None,
                    threshold=0.5,
                )

    def test_clang_accepts_valid_ir(self):
        result = validate_ir_with_clang(
            "define i32 @main() {\nentry:\n  ret i32 0\n}\n"
        )
        self.assertTrue(result["valid"], result["diagnostics"])

    def test_clang_rejects_malformed_ir(self):
        result = validate_ir_with_clang("this is not valid LLVM IR")
        self.assertFalse(result["valid"])
        self.assertTrue(result["diagnostics"])


if __name__ == "__main__":
    unittest.main()
