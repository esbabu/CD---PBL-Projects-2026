import os
import sys
import tempfile
import types
import unittest

# cpp_parser imports pandas only for its command-line entry point. Supply a
# test-only placeholder when pandas is not installed in the test environment.
try:
    import pandas
except ImportError:
    sys.modules.setdefault("pandas", types.ModuleType("pandas"))

from cpp_parser import build_ast
from lexer import tokenize_file


def tokenize_source(source):
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".cpp", encoding="utf-8", delete=False
    ) as source_file:
        source_file.write(source)
        path = source_file.name

    try:
        return tokenize_file(path)
    finally:
        os.unlink(path)


class ColonTokenTests(unittest.TestCase):
    def test_switch_case_and_default_labels_parse_without_errors(self):
        source = (
            "int main() {\n"
            "    switch (value) {\n"
            "        case 1:\n"
            "            return 1;\n"
            "        default:\n"
            "            return 0;\n"
            "    }\n"
            "}\n"
        )

        tokens = tokenize_source(source)
        colon_locations = [
            (token["line"], token["column"])
            for token in tokens
            if token["token_type"] == "COLON" and token["token_value"] == ":"
        ]
        _, errors = build_ast(tokens)

        self.assertEqual(colon_locations, [(3, 15), (5, 16)])
        self.assertEqual(errors, [])

    def test_class_access_specifiers_parse_without_errors(self):
        source = (
            "class Example {\n"
            "public:\n"
            "    int first;\n"
            "private:\n"
            "    int second;\n"
            "protected:\n"
            "    int third;\n"
            "};\n"
        )

        tokens = tokenize_source(source)
        colon_locations = [
            (token["line"], token["column"])
            for token in tokens
            if token["token_type"] == "COLON" and token["token_value"] == ":"
        ]
        _, errors = build_ast(tokens)

        self.assertEqual(colon_locations, [(2, 7), (4, 8), (6, 10)])
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
