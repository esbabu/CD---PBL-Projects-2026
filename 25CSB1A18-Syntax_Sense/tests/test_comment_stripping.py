import os
import tempfile
import unittest

from lexer import strip_comments, tokenize_file_clean


def tokenize_source(source):
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".cpp", encoding="utf-8", delete=False
    ) as source_file:
        source_file.write(source)
        path = source_file.name

    try:
        return tokenize_file_clean(path)
    finally:
        os.unlink(path)


class CommentStrippingTests(unittest.TestCase):
    def test_url_in_string_is_preserved(self):
        tokens = tokenize_source('const char* url = "https://example.com";\n')

        self.assertIn(
            ("STRING", '"https://example.com"', 1, 19),
            [
                (token["token_type"], token["token_value"], token["line"], token["column"])
                for token in tokens
            ],
        )

    def test_block_comment_text_in_string_is_preserved(self):
        tokens = tokenize_source('const char* text = "/* text */";\n')

        self.assertIn(
            ("STRING", '"/* text */"'),
            [(token["token_type"], token["token_value"]) for token in tokens],
        )

    def test_slash_character_literal_is_preserved(self):
        tokens = tokenize_source("char slash = '/';\n")

        self.assertIn(
            ("CHAR", "'/'"),
            [(token["token_type"], token["token_value"]) for token in tokens],
        )

    def test_single_line_comment_is_ignored_without_shifting_next_line(self):
        tokens = tokenize_source("int x = 1; // ignored comment\nint y = 2;\n")

        token_values = [token["token_value"] for token in tokens]
        y_token = next(token for token in tokens if token["token_value"] == "y")
        self.assertNotIn("ignored", token_values)
        self.assertEqual((y_token["line"], y_token["column"]), (2, 5))

    def test_multiline_comment_preserves_later_token_line_and_column(self):
        source = "int x = 1;\n/* first line\n   second line */\nint y = 2;\n"
        tokens = tokenize_source(source)
        y_token = next(token for token in tokens if token["token_value"] == "y")

        self.assertEqual(strip_comments(source).count("\n"), source.count("\n"))
        self.assertEqual((y_token["line"], y_token["column"]), (4, 5))


if __name__ == "__main__":
    unittest.main()
