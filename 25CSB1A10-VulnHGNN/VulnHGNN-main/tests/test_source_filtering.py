import os
import unittest
from pathlib import Path

from src.ir_parser import filter_functions_to_source


class FilterFunctionsToSourceTests(unittest.TestCase):
    def test_relative_ir_source_matches_absolute_debug_source(self):
        source_path = Path("test_files/test_10_all_vulnerabilities.c")
        ir_data = {
            "source_file": os.path.relpath(source_path, Path.cwd()),
            "functions": [
                {"name": "the_ultimate_test", "source_file": str(source_path.resolve())},
                {"name": "included_header", "source_file": str(Path("header.c").resolve())},
            ],
        }

        filtered = filter_functions_to_source(ir_data)

        self.assertEqual(
            [function["name"] for function in filtered["functions"]],
            ["the_ultimate_test"],
        )

    def test_unavailable_source_metadata_preserves_functions(self):
        functions = [{"name": "main", "source_file": None}]

        filtered = filter_functions_to_source({
            "source_file": "",
            "functions": functions,
        })

        self.assertIs(filtered["functions"], functions)


if __name__ == "__main__":
    unittest.main()
