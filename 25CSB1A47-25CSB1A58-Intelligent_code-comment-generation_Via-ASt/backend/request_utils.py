"""Shared request parsing and validation helpers for Flask routes."""


def request_data(request):
    """Return a JSON object for the request, or an empty object for invalid JSON."""
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else {}


def extract_code(data):
    """Return the source-code field if it is a string."""
    code = data.get("code", "")
    return code if isinstance(code, str) else None


def valid_cursor(cursor):
    """Check the accepted integer-offset and line/column cursor shapes."""
    if isinstance(cursor, int) and not isinstance(cursor, bool):
        return cursor >= 0
    if not isinstance(cursor, dict):
        return False
    line = cursor.get("line", 1)
    column = cursor.get("column", cursor.get("col", 0))
    return (
        all(
            isinstance(value, int) and not isinstance(value, bool)
            for value in (line, column)
        )
        and line >= 1
        and column >= 0
    )


def _utf16_offset_to_index(text, offset):
    """Convert a JavaScript UTF-16 offset to a Python string index."""
    remaining = max(0, offset)
    for index, character in enumerate(text):
        width = len(character.encode("utf-16-le", errors="surrogatepass")) // 2
        if remaining < width:
            return index
        remaining -= width
    return len(text)


def cursor_to_offset(source_code, cursor):
    """Convert an API cursor (JavaScript UTF-16 units) to a Python string index."""
    if isinstance(cursor, bool):
        raise TypeError("Boolean values are not valid cursor positions.")
    if isinstance(cursor, int) and not isinstance(cursor, bool):
        return _utf16_offset_to_index(
            source_code,
            min(
                cursor,
                len(source_code.encode("utf-16-le", errors="surrogatepass")) // 2,
            ),
        )
    if not isinstance(cursor, dict):
        raise TypeError("Cursor must be an integer offset or a line/column object.")

    lines = source_code.split("\n")
    line_number = cursor.get("line", 1) - 1
    if line_number >= len(lines):
        return len(source_code)
    line_start = sum(len(line) + 1 for line in lines[:line_number])
    line_text = lines[line_number]
    column = cursor.get("column", cursor.get("col", 0))
    return line_start + _utf16_offset_to_index(line_text, column)


def to_utf16_offset(source_code, offset):
    """Convert a Python string index to the browser's JavaScript offset units."""
    return len(source_code[:offset].encode("utf-16-le", errors="surrogatepass")) // 2


def undefined_name_findings(undefined_names):
    """Convert name-checker output to the common warning format."""
    return [
        {
            "rule_id": "NAME001",
            "severity": "error",
            "message": f"Name '{item['name']}' may be undefined in this scope.",
            "line": item["lineno"],
        }
        for item in undefined_names
    ]
