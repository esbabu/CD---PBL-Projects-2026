"""JavaAnalyzer implementation for SyntaxSense using a lightweight tokenizer and deterministic syntax checks."""

import re
from typing import Any, Dict, List, Optional, Set, Tuple

from backend.app.services.base_analyzer import BaseAnalyzer

MAX_SOURCE_LENGTH = 200_000
ANALYSIS_VERSION = "java-ast-v1"

JAVA_KEYWORDS: Set[str] = {
    "abstract", "assert", "boolean", "break", "byte", "case", "catch", "char", "class",
    "const", "continue", "default", "do", "double", "else", "enum", "extends", "final",
    "finally", "float", "for", "goto", "if", "implements", "import", "instanceof", "int",
    "interface", "long", "native", "new", "package", "private", "protected", "public",
    "return", "short", "static", "strictfp", "super", "switch", "synchronized", "this",
    "throw", "throws", "transient", "try", "void", "volatile", "while", "record", "var",
    "true", "false", "null", "yield", "sealed", "non-sealed", "permits"
}

TYPE_KEYWORDS: Set[str] = {
    "boolean", "byte", "char", "double", "float", "int", "long", "short", "void", "var"
}

DIAGNOSTIC_HELP: Dict[str, Tuple[str, str]] = {
    "MISSING_SEMICOLON": (
        "A semicolon ';' is missing at the end of a statement or declaration.",
        "Add ';' at the end of the statement or declaration.",
    ),
    "UNMATCHED_BRACE": (
        "A curly brace '{' or '}' is missing or mismatched.",
        "Match every opening brace '{' with a closing brace '}'.",
    ),
    "UNMATCHED_PARANTHESES": (
        "A parenthesis '(' or ')' is missing or mismatched.",
        "Match every opening parenthesis '(' with a closing parenthesis ')'.",
    ),
    "UNMATCHED_BRACKET": (
        "A square bracket '[' or ']' is missing or mismatched.",
        "Match every opening square bracket '[' with a closing bracket ']'.",
    ),
    "INVALID_ASSIGNMENT": (
        "Cannot assign a value to a literal or expression on the left-hand side of '='.",
        "Ensure the left-hand side of the '=' operator is a valid variable identifier or field.",
    ),
    "INVALID_CONDITIONAL": (
        "The condition in an 'if' statement must be enclosed in parentheses.",
        "Add parentheses around the condition: if (<condition>) { ... }",
    ),
    "INVALID_LOOP": (
        "The loop condition or header must be enclosed in parentheses.",
        "Add parentheses around the loop condition: while (<condition>) / for (<header>)",
    ),
    "INVALID_CLASS_DECL": (
        "Malformed class declaration. A valid class identifier must follow the 'class' keyword.",
        "Provide a valid identifier for the class name.",
    ),
    "EXTRA_TOKENS": (
        "Unexpected or illegal token encountered in Java source code.",
        "Remove the stray or unrecognized token.",
    ),
    "UNTERMINATED_STRING": (
        "A string literal, character literal, or block comment was not properly closed.",
        "Add the matching closing delimiter to complete the literal or comment.",
    ),
}


class Token:
    """Represents a scanned Java lexical token with source position."""

    def __init__(self, token_type: str, value: str, line: int, column: int):
        self.type = token_type
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self) -> str:
        return f"Token({self.type}, {self.value!r}, L{self.line}:C{self.column})"


def _tokenize_java(source: str) -> Tuple[List[Token], List[Dict[str, Any]]]:
    """Scan Java source code into tokens while capturing lexical errors (unterminated strings/comments)."""
    tokens: List[Token] = []
    diagnostics: List[Dict[str, Any]] = []

    pos = 0
    line = 1
    col = 1
    n = len(source)

    while pos < n:
        c = source[pos]

        # 1. Whitespace
        if c == "\n":
            line += 1
            col = 1
            pos += 1
            continue
        elif c in " \t\r\f":
            col += 1
            pos += 1
            continue

        # 2. Single-line comment: // ...
        if c == "/" and pos + 1 < n and source[pos + 1] == "/":
            while pos < n and source[pos] != "\n":
                pos += 1
            continue

        # 3. Multi-line comment: /* ... */
        if c == "/" and pos + 1 < n and source[pos + 1] == "*":
            start_line = line
            start_col = col
            pos += 2
            col += 2
            closed = False
            while pos < n:
                if source[pos] == "\n":
                    line += 1
                    col = 1
                    pos += 1
                elif source[pos] == "*" and pos + 1 < n and source[pos + 1] == "/":
                    pos += 2
                    col += 2
                    closed = True
                    break
                else:
                    pos += 1
                    col += 1
            if not closed:
                exp, sug = DIAGNOSTIC_HELP["UNTERMINATED_STRING"]
                diagnostics.append({
                    "category": "UNTERMINATED_STRING",
                    "origin": "parser",
                    "severity": "error",
                    "line": start_line,
                    "column": start_col,
                    "explanation": "Multi-line comment was not closed with '*/' before the end of the file.",
                    "suggestion": "Close the comment block with '*/'.",
                    "parserMessage": f"[LexError @ line {start_line}] Unterminated block comment",
                })
            continue

        # 4. Text block (Java 15+): """ ... """
        if source[pos:pos+3] == '"""':
            start_line = line
            start_col = col
            pos += 3
            col += 3
            closed = False
            while pos < n:
                if source[pos] == "\n":
                    line += 1
                    col = 1
                    pos += 1
                elif source[pos:pos+3] == '"""':
                    pos += 3
                    col += 3
                    closed = True
                    break
                else:
                    pos += 1
                    col += 1
            if closed:
                tokens.append(Token("LITERAL_STRING", '"""', start_line, start_col))
            else:
                exp, sug = DIAGNOSTIC_HELP["UNTERMINATED_STRING"]
                diagnostics.append({
                    "category": "UNTERMINATED_STRING",
                    "origin": "parser",
                    "severity": "error",
                    "line": start_line,
                    "column": start_col,
                    "explanation": "Multi-line text block was not closed with '\"\"\"' before end of file.",
                    "suggestion": "Close the text block with '\"\"\"'.",
                    "parserMessage": f"[LexError @ line {start_line}] Unterminated text block",
                })
            continue

        # 5. String literal: "..."
        if c == '"':
            start_line = line
            start_col = col
            val = [c]
            pos += 1
            col += 1
            closed = False
            while pos < n and source[pos] != "\n":
                ch = source[pos]
                if ch == "\\":
                    val.append(ch)
                    pos += 1
                    col += 1
                    if pos < n:
                        val.append(source[pos])
                        pos += 1
                        col += 1
                    continue
                elif ch == '"':
                    val.append(ch)
                    pos += 1
                    col += 1
                    closed = True
                    break
                else:
                    val.append(ch)
                    pos += 1
                    col += 1
            if closed:
                tokens.append(Token("LITERAL_STRING", "".join(val), start_line, start_col))
            else:
                exp, sug = DIAGNOSTIC_HELP["UNTERMINATED_STRING"]
                diagnostics.append({
                    "category": "UNTERMINATED_STRING",
                    "origin": "parser",
                    "severity": "error",
                    "line": start_line,
                    "column": start_col,
                    "explanation": exp,
                    "suggestion": sug,
                    "parserMessage": f"[LexError @ line {start_line}] Unterminated string literal",
                })
            continue

        # 6. Character literal: '...'
        if c == "'":
            start_line = line
            start_col = col
            val = [c]
            pos += 1
            col += 1
            closed = False
            while pos < n and source[pos] != "\n":
                ch = source[pos]
                if ch == "\\":
                    val.append(ch)
                    pos += 1
                    col += 1
                    if pos < n:
                        val.append(source[pos])
                        pos += 1
                        col += 1
                    continue
                elif ch == "'":
                    val.append(ch)
                    pos += 1
                    col += 1
                    closed = True
                    break
                else:
                    val.append(ch)
                    pos += 1
                    col += 1
            if closed:
                tokens.append(Token("LITERAL_CHAR", "".join(val), start_line, start_col))
            else:
                exp, sug = DIAGNOSTIC_HELP["UNTERMINATED_STRING"]
                diagnostics.append({
                    "category": "UNTERMINATED_STRING",
                    "origin": "parser",
                    "severity": "error",
                    "line": start_line,
                    "column": start_col,
                    "explanation": exp,
                    "suggestion": "Close the character literal with a matching single quote (').",
                    "parserMessage": f"[LexError @ line {start_line}] Unterminated character literal",
                })
            continue

        # 7. Numeric literals: integers, decimals, hex, binary
        if c.isdigit() or (c == "." and pos + 1 < n and source[pos + 1].isdigit()):
            start_line = line
            start_col = col
            val = []
            is_float = False
            while pos < n and (source[pos].isalnum() or source[pos] in "._"):
                if source[pos] == ".":
                    is_float = True
                val.append(source[pos])
                pos += 1
                col += 1
            ttype = "LITERAL_FLOAT" if is_float else "LITERAL_INT"
            tokens.append(Token(ttype, "".join(val), start_line, start_col))
            continue

        # 8. Identifiers and Keywords
        if c.isalpha() or c in "_$":
            start_line = line
            start_col = col
            val = []
            while pos < n and (source[pos].isalnum() or source[pos] in "_$"):
                val.append(source[pos])
                pos += 1
                col += 1
            ident = "".join(val)
            if ident in JAVA_KEYWORDS:
                if ident in ("true", "false", "null"):
                    tokens.append(Token("LITERAL_BOOL" if ident != "null" else "LITERAL_NULL", ident, start_line, start_col))
                else:
                    tokens.append(Token("KEYWORD", ident, start_line, start_col))
            else:
                tokens.append(Token("IDENTIFIER", ident, start_line, start_col))
            continue

        # 9. Multi-character operators and delimiters
        three_chars = source[pos:pos+3]
        if three_chars in (">>>", "<<=", ">>=", "..."):
            tokens.append(Token("OPERATOR" if three_chars != "..." else "DELIMITER", three_chars, line, col))
            pos += 3
            col += 3
            continue

        two_chars = source[pos:pos+2]
        if two_chars in ("==", "!=", "<=", ">=", "&&", "||", "++", "--", "+=", "-=", "*=", "/=", "%=", "&=", "|=", "^=", "<<", ">>", "::", "->"):
            tokens.append(Token("OPERATOR", two_chars, line, col))
            pos += 2
            col += 2
            continue

        # 10. Single-character delimiters
        if c in "{}()[]:;,.@?":
            tt = "DELIMITER"
            if c == "{": tt = "OPEN_BRACE"
            elif c == "}": tt = "CLOSE_BRACE"
            elif c == "(": tt = "OPEN_PAREN"
            elif c == ")": tt = "CLOSE_PAREN"
            elif c == "[": tt = "OPEN_BRACKET"
            elif c == "]": tt = "CLOSE_BRACKET"
            elif c == ";": tt = "SEMICOLON"
            elif c == "@": tt = "AT"
            tokens.append(Token(tt, c, line, col))
            pos += 1
            col += 1
            continue

        # 11. Single-character operators
        if c in "=+-*/%&|^~!<>":
            tokens.append(Token("OPERATOR", c, line, col))
            pos += 1
            col += 1
            continue

        # 12. Stray illegal non-Java character (e.g. #, backtick, etc.)
        exp, sug = DIAGNOSTIC_HELP["EXTRA_TOKENS"]
        diagnostics.append({
            "category": "EXTRA_TOKENS",
            "origin": "parser",
            "severity": "error",
            "line": line,
            "column": col,
            "explanation": f"Unexpected illegal character '{c}' in Java source code.",
            "suggestion": "Remove the invalid token.",
            "parserMessage": f"[LexError @ line {line} column {col}] Unexpected token '{c}' — EXTRA_TOKENS",
        })
        pos += 1
        col += 1

    return tokens, diagnostics


def _check_java_syntax(tokens: List[Token], source_lines: List[str]) -> List[Dict[str, Any]]:
    """Perform deterministic Java syntactic checks across the token stream."""
    diagnostics: List[Dict[str, Any]] = []

    # 1. Delimiter Stack Balancing
    delim_stack: List[Tuple[Token, str]] = []  # (open_token, expected_close_char)
    delim_pairs = {"(": ")", "{": "}", "[": "]"}
    close_to_cat = {
        "}": "UNMATCHED_BRACE",
        ")": "UNMATCHED_PARANTHESES",
        "]": "UNMATCHED_BRACKET",
    }
    open_to_cat = {
        "(": "UNMATCHED_PARANTHESES",
        "{": "UNMATCHED_BRACE",
        "[": "UNMATCHED_BRACKET",
    }

    for tok in tokens:
        if tok.value in delim_pairs:
            # If opening a block '{' while an unclosed '(' is on the stack:
            if tok.value == "{" and delim_stack and delim_stack[-1][0].value == "(":
                unclosed_paren, expected_close = delim_stack.pop()
                p_cat = "UNMATCHED_PARANTHESES"
                exp, sug = DIAGNOSTIC_HELP[p_cat]
                diagnostics.append({
                    "category": p_cat,
                    "origin": "parser",
                    "severity": "error",
                    "line": unclosed_paren.line,
                    "column": unclosed_paren.column,
                    "explanation": f"Opening '(' from line {unclosed_paren.line} was never closed before block '{{'.",
                    "suggestion": "Add missing closing ')' before opening brace.",
                    "parserMessage": f"[ParseError @ line {tok.line} column {tok.column}] Missing ')' before '{{' — UNMATCHED_PARANTHESES",
                })
            delim_stack.append((tok, delim_pairs[tok.value]))
        elif tok.value in close_to_cat:
            cat = close_to_cat[tok.value]
            if not delim_stack:
                exp, sug = DIAGNOSTIC_HELP[cat]
                diagnostics.append({
                    "category": cat,
                    "origin": "parser",
                    "severity": "error",
                    "line": tok.line,
                    "column": tok.column,
                    "explanation": f"Extraneous closing '{tok.value}' with no matching opening delimiter.",
                    "suggestion": f"Remove the extra closing '{tok.value}' or add the matching opening delimiter.",
                    "parserMessage": f"[ParseError @ line {tok.line} column {tok.column}] Unmatched '{tok.value}' — {cat}",
                })
            else:
                top_tok, expected_close = delim_stack.pop()
                if tok.value != expected_close:
                    mismatch_cat = open_to_cat.get(top_tok.value, cat)
                    exp, sug = DIAGNOSTIC_HELP[mismatch_cat]
                    diagnostics.append({
                        "category": mismatch_cat,
                        "origin": "parser",
                        "severity": "error",
                        "line": top_tok.line,
                        "column": top_tok.column,
                        "explanation": f"Mismatched closing '{tok.value}' does not match opening '{top_tok.value}' from line {top_tok.line}.",
                        "suggestion": f"Replace with matching '{expected_close}' or close '{top_tok.value}'.",
                        "parserMessage": f"[ParseError @ line {tok.line} column {tok.column}] Mismatched '{tok.value}' for '{top_tok.value}' — {mismatch_cat}",
                    })

    # Report unclosed opening delimiters (report innermost first)
    while delim_stack:
        unclosed_tok, expected_close = delim_stack.pop()
        cat = open_to_cat.get(unclosed_tok.value, "UNMATCHED_BRACE")
        exp, sug = DIAGNOSTIC_HELP[cat]
        diagnostics.append({
            "category": cat,
            "origin": "parser",
            "severity": "error",
            "line": unclosed_tok.line,
            "column": unclosed_tok.column,
            "explanation": f"Opening '{unclosed_tok.value}' was never closed with matching '{expected_close}'.",
            "suggestion": f"Add matching closing '{expected_close}'.",
            "parserMessage": f"[ParseError @ line {unclosed_tok.line} column {unclosed_tok.column}] Unclosed '{unclosed_tok.value}' — {cat}",
        })

    # 2. Sequential Token Pattern Checks
    num_tokens = len(tokens)
    for i in range(num_tokens):
        tok = tokens[i]
        next_tok = tokens[i + 1] if i + 1 < num_tokens else None
        prev_tok = tokens[i - 1] if i > 0 else None

        # Check: Missing class name (e.g. "public class {")
        if tok.type == "KEYWORD" and tok.value in ("class", "interface", "enum", "record"):
            if next_tok and next_tok.value == "{":
                exp, sug = DIAGNOSTIC_HELP["INVALID_CLASS_DECL"]
                diagnostics.append({
                    "category": "INVALID_CLASS_DECL",
                    "origin": "parser",
                    "severity": "error",
                    "line": tok.line,
                    "column": tok.column,
                    "explanation": exp,
                    "suggestion": sug,
                    "parserMessage": f"[ParseError @ line {tok.line} column {tok.column}] Missing class name after '{tok.value}' — INVALID_CLASS_DECL",
                })

        # Check: Malformed condition in "if" (e.g. "if x > 0 {")
        if tok.type == "KEYWORD" and tok.value == "if":
            if next_tok and next_tok.type != "OPEN_PAREN":
                exp, sug = DIAGNOSTIC_HELP["INVALID_CONDITIONAL"]
                diagnostics.append({
                    "category": "INVALID_CONDITIONAL",
                    "origin": "parser",
                    "severity": "error",
                    "line": tok.line,
                    "column": tok.column,
                    "explanation": exp,
                    "suggestion": sug,
                    "parserMessage": f"[ParseError @ line {tok.line} column {tok.column}] Missing '(' after 'if' — INVALID_CONDITIONAL",
                })

        # Check: Malformed condition in "while" or "for" (e.g. "while count > 0 {")
        if tok.type == "KEYWORD" and tok.value in ("while", "for"):
            # Ensure "while" is not part of "do { ... } while (...);" condition check
            if next_tok and next_tok.type != "OPEN_PAREN":
                exp, sug = DIAGNOSTIC_HELP["INVALID_LOOP"]
                diagnostics.append({
                    "category": "INVALID_LOOP",
                    "origin": "parser",
                    "severity": "error",
                    "line": tok.line,
                    "column": tok.column,
                    "explanation": exp,
                    "suggestion": sug,
                    "parserMessage": f"[ParseError @ line {tok.line} column {tok.column}] Missing '(' after '{tok.value}' — INVALID_LOOP",
                })

        # Check: Invalid assignment to literal (e.g. "100 = x;")
        if tok.type == "OPERATOR" and tok.value == "=":
            if prev_tok and prev_tok.type in ("LITERAL_INT", "LITERAL_FLOAT", "LITERAL_STRING", "LITERAL_CHAR", "LITERAL_BOOL"):
                exp, sug = DIAGNOSTIC_HELP["INVALID_ASSIGNMENT"]
                diagnostics.append({
                    "category": "INVALID_ASSIGNMENT",
                    "origin": "parser",
                    "severity": "error",
                    "line": prev_tok.line,
                    "column": prev_tok.column,
                    "explanation": exp,
                    "suggestion": sug,
                    "parserMessage": f"[ParseError @ line {prev_tok.line} column {prev_tok.column}] Literal on left-hand side of '=' — INVALID_ASSIGNMENT",
                })

        # Check: Unexpected stray '@' not preceding an annotation identifier
        if tok.type == "AT" and (not next_tok or next_tok.type != "IDENTIFIER"):
            exp, sug = DIAGNOSTIC_HELP["EXTRA_TOKENS"]
            diagnostics.append({
                "category": "EXTRA_TOKENS",
                "origin": "parser",
                "severity": "error",
                "line": tok.line,
                "column": tok.column,
                "explanation": "Unexpected '@' symbol without valid annotation identifier.",
                "suggestion": "Remove stray '@' symbol or specify an annotation name.",
                "parserMessage": f"[ParseError @ line {tok.line} column {tok.column}] Stray '@' — EXTRA_TOKENS",
            })

    # 3. Missing Semicolon Detection
    # In Java, statements terminating declarations, assignments, returns, packages, and calls require ';'
    paren_depth = 0
    bracket_depth = 0

    for i in range(num_tokens):
        tok = tokens[i]
        next_tok = tokens[i + 1] if i + 1 < num_tokens else None

        if tok.type == "OPEN_PAREN":
            paren_depth += 1
        elif tok.type == "CLOSE_PAREN":
            paren_depth = max(0, paren_depth - 1)
        elif tok.type == "OPEN_BRACKET":
            bracket_depth += 1
        elif tok.type == "CLOSE_BRACKET":
            bracket_depth = max(0, bracket_depth - 1)

        # Look for missing semicolon at top-level delimiter boundaries
        if paren_depth == 0 and bracket_depth == 0:
            # Check if this token ends a line and is part of a statement that should end in ';'
            if next_tok and next_tok.line > tok.line:
                # If next token is '{', it is a header for a class, method, or block (no semicolon needed)
                if next_tok.value == "{":
                    continue
                # If current token is already a statement terminator or delimiter
                if tok.value in (";", "{", "}", ":", ","):
                    continue
                # If current line ended with a binary/ternary operator or continuing keyword (line continuation)
                if tok.type == "OPERATOR" or tok.value in ("extends", "implements", "throws", "->", "?", ":"):
                    continue

                # Check if statement on this line was a candidate needing a semicolon:
                # e.g., variable declaration, return, assignment, import, package, method call
                current_line_text = source_lines[tok.line - 1].strip() if tok.line - 1 < len(source_lines) else ""
                
                # Exclude annotations like @Override
                if current_line_text.startswith("@"):
                    continue
                # Exclude control flow headers where body continues on next line
                if re.match(r"^(if|else|for|while|do|switch|try|catch|finally)\b", current_line_text):
                    continue
                # Exclude class/interface headers where { is placed on next line
                if re.search(r"\b(class|interface|enum|record)\b", current_line_text):
                    continue

                # Candidate statement ended without semicolon before next line or closing brace
                exp, sug = DIAGNOSTIC_HELP["MISSING_SEMICOLON"]
                diagnostics.append({
                    "category": "MISSING_SEMICOLON",
                    "origin": "parser",
                    "severity": "error",
                    "line": tok.line,
                    "column": tok.column + len(tok.value),
                    "explanation": exp,
                    "suggestion": sug,
                    "parserMessage": f"[ParseError @ line {tok.line} column {tok.column + len(tok.value)}] Missing ';' — MISSING_SEMICOLON",
                })
            elif next_tok and next_tok.value == "}" and tok.value not in (";", "{", "}", ":"):
                # Statement right before a closing brace missing ';' (e.g. "return x }")
                current_line_text = source_lines[tok.line - 1].strip() if tok.line - 1 < len(source_lines) else ""
                if not re.match(r"^(if|else|for|while|do|switch|try|catch|finally)\b", current_line_text):
                    exp, sug = DIAGNOSTIC_HELP["MISSING_SEMICOLON"]
                    diagnostics.append({
                        "category": "MISSING_SEMICOLON",
                        "origin": "parser",
                        "severity": "error",
                        "line": tok.line,
                        "column": tok.column + len(tok.value),
                        "explanation": exp,
                        "suggestion": sug,
                        "parserMessage": f"[ParseError @ line {tok.line} column {tok.column + len(tok.value)}] Missing ';' — MISSING_SEMICOLON",
                    })

    return diagnostics


class JavaAnalyzer(BaseAnalyzer):
    """Deterministic syntax analyzer for Java without executing submitted code."""

    @property
    def language_id(self) -> str:
        return "java"

    @property
    def is_supported(self) -> bool:
        return True

    def analyze(self, code: str) -> Dict[str, Any]:
        if not code or not code.strip():
            raise ValueError("Java source code must not be empty.")

        if len(code) > MAX_SOURCE_LENGTH:
            raise ValueError(f"Java source exceeds the {MAX_SOURCE_LENGTH}-character limit.")

        source_lines = code.splitlines()

        # 1. Lexical scan (tokens + lexical diagnostics)
        tokens, lex_diagnostics = _tokenize_java(code)

        # 2. Syntactic checks (delimiter balancing, statement termination, declaration patterns)
        syntax_diagnostics = _check_java_syntax(tokens, source_lines)

        all_diagnostics = lex_diagnostics + syntax_diagnostics

        # Deduplicate diagnostics on exact same line and category
        deduped: List[Dict[str, Any]] = []
        seen = set()
        for d in all_diagnostics:
            sig = (d["category"], d.get("line"), d.get("column"))
            if sig not in seen:
                seen.add(sig)
                deduped.append(d)

        if not deduped:
            classification = {
                "label": "CLEAN",
                "confidence": 100.0,
                "source": "java_parser",
            }
        else:
            classification = {
                "label": deduped[0]["category"],
                "confidence": 95.0,
                "source": "java_parser",
            }

        serialized_tokens = [
            {
                "type": tok.type,
                "value": tok.value,
                "line": tok.line,
                "column": tok.column,
            }
            for tok in tokens
        ]

        return {
            "language": "java",
            "analysisVersion": ANALYSIS_VERSION,
            "classification": classification,
            "diagnostics": deduped,
            "tokens": serialized_tokens,
            "summary": {
                "diagnosticCount": len(deduped),
                "parserDiagnosticCount": len(deduped),
                "sourceHeuristicDiagnosticCount": 0,
            },
        }
