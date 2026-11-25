"""Smoke tests for the multi-language documentation path."""
from src.multilang.universal_commenter import UniversalCommenter


def test_rule_based_comment_generation_for_supported_languages():
    commenter = UniversalCommenter()
    samples = {
        "c": ('int add(int a, int b) {\n    return a + b;\n}\n', "example.c", "add"),
        "cpp": ('class Calculator {\npublic:\n int add(int a, int b) { return a + b; }\n};\n', "example.cpp", "Calculator"),
        "java": ('public class Calculator {\n public int add(int a, int b) { return a + b; }\n}\n', "Calculator.java", "Calculator"),
        "javascript": ('function add(a, b) { return a + b; }\n', "example.js", "add"),
        "typescript": ('export function add(a: number, b: number): number { return a + b; }\n', "example.ts", "add"),
    }
    for language, (source, filename, expected_name) in samples.items():
        annotated, report = commenter.generate_comments(source, filename=filename, language=language)
        assert report["language"] == language
        assert report["comments_generated"] >= 1
        assert expected_name in annotated
        assert "/**" in annotated


def test_language_detection_by_extension():
    commenter = UniversalCommenter()
    assert commenter.detect_language("x.py") == "python"
    assert commenter.detect_language("x.c") == "c"
    assert commenter.detect_language("x.cpp") == "cpp"
    assert commenter.detect_language("x.java") == "java"
    assert commenter.detect_language("x.js") == "javascript"
    assert commenter.detect_language("x.ts") == "typescript"


def test_unsupported_extension_is_not_guessed_as_a_supported_language():
    commenter = UniversalCommenter()
    assert commenter.detect_language("example.unknown", "some source") is None
