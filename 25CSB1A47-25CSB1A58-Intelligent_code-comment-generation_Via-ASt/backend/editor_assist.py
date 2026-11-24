"""Cursor-aware Python editor suggestions and diagnostics."""

import ast
import re

from .code_analysis import analyze_code
from .request_utils import cursor_to_offset, to_utf16_offset, undefined_name_findings
from .rules import build_review_score, summarize_quality
from .validator import check_undefined_names


def editor_assist(source_code, cursor):
    """Generate a small completion or warning suggestion at the cursor."""
    if not source_code.strip():
        return {
            "suggestion": "pass",
            "replacement_range": {"start": 0, "end": 0},
            "suggestion_type": "completion",
            "explanation": "The file is empty; a safe default is to add a no-op placeholder statement.",
            "validation_status": "validated",
            "warnings": [],
            "cursor_offset": 4,
            "analysis": None,
            "quality_summary": summarize_quality([]),
            "quality_score": 100,
            "review_score": build_review_score([]),
        }

    offset = cursor_to_offset(source_code, cursor)
    syntax_warnings = []
    analysis = None
    try:
        ast.parse(source_code)
    except SyntaxError as exc:
        syntax_warnings.append(
            {
                "rule_id": "SYNTAX001",
                "severity": "error",
                "message": f"Syntax error at line {exc.lineno}, column {exc.offset}: {exc.msg}",
                "line": exc.lineno,
                "column": exc.offset,
                "end_column": getattr(exc, "end_offset", None),
            }
        )
    else:
        analysis = analyze_code(source_code)
        analysis["warnings"].extend(
            undefined_name_findings(check_undefined_names(source_code))
        )
    prefix = source_code[:offset]
    suffix = source_code[offset:]
    trimmed = prefix.rstrip()
    last_line = trimmed.splitlines()[-1] if trimmed else ""
    code_before_cursor = source_code[:offset]
    current_word_match = re.search(r"([A-Za-z_][A-Za-z0-9_]*)$", code_before_cursor)
    current_word = current_word_match.group(1) if current_word_match else ""
    stripped_line = last_line.strip()
    missing_colon = (
        re.match(r"^(if|elif|while)\s+.+$", stripped_line)
        or re.match(r"^for\s+.+\s+in\s+.+$", stripped_line)
        or re.match(r"^(def|class|with|except|match|case)\s+.+$", stripped_line)
        or stripped_line in {"else", "try", "finally"}
    )

    suggestion = ""
    suggestion_type = "completion"
    explanation = "No safe completion is available at this cursor position."
    validation_status = "needs_review" if syntax_warnings else "validated"
    if syntax_warnings:
        warnings = syntax_warnings
    else:
        if analysis is None:
            raise RuntimeError("Valid source code did not produce an AST analysis.")
        warnings = analysis["warnings"]
    quality_summary = summarize_quality(warnings)
    cursor_offset = offset
    start = offset
    end = offset
    replacement_mode = "cursor"
    pair_completions = {"'": "'", '"': '"', "(": ")", "[": "]", "{": "}"}

    if (
        prefix
        and prefix[-1] in pair_completions
        and not suffix.startswith(pair_completions[prefix[-1]])
    ):
        opener = prefix[-1]
        closer = pair_completions[opener]
        suggestion = opener + closer
        suggestion_type = "pair"
        explanation = f"The editor adds the matching {closer} so the cursor stays inside a balanced pair."
        validation_status = "validated"
        warnings = []
        start = offset - 1
        end = offset
        cursor_offset = start + 1

    elif prefix.rstrip().endswith(":"):
        suggestion = "\n    pass"
        explanation = "The block started with a colon, so the editor inserts an indented placeholder body to keep the structure valid."
        start = offset
        end = offset
        cursor_offset = offset + len("\n    pass")
        replacement_mode = "insert"
    elif (
        (not suffix or suffix[0] in "\r\n")
        and missing_colon
        and not stripped_line.endswith(":")
    ):
        indentation = len(last_line) - len(last_line.lstrip())
        suggestion = ":\n" + " " * (indentation + 4) + "pass"
        explanation = "This block header is missing its colon and body; the suggestion completes both without changing surrounding code."
        start = offset
        end = offset
        cursor_offset = offset + len(suggestion)
        replacement_mode = "insert"
    elif current_word:
        completions = {
            "print": "print()",
            "input": "input()",
            "open": "open()",
            "str": "str()",
            "int": "int()",
            "float": "float()",
            "bool": "bool()",
            "list": "list()",
            "dict": "dict()",
            "set": "set()",
            "tuple": "tuple()",
            "enumerate": "enumerate()",
            "zip": "zip()",
            "sorted": "sorted()",
            "sum": "sum()",
            "min": "min()",
            "max": "max()",
            "abs": "abs()",
            "isinstance": "isinstance()",
            "type": "type()",
            "if": "if :\n    pass",
            "for": "for item in items:\n    pass",
            "while": "while condition:\n    pass",
            "def": "def function_name():\n    pass",
            "class": "class ClassName:\n    pass",
            "return": "return ",
            "elif": "elif :\n    pass",
            "else": "else:\n    pass",
            "try": "try:\n    pass\nexcept Exception:\n    pass",
            "import": "import ",
            "from": "from module import ",
            "len": "len()",
            "range": "range()",
            "with": "with :\n    pass",
            "lambda": "lambda x: x",
            "async": "async ",
            "await": "await ",
            "yield": "yield ",
            "break": "break",
            "continue": "continue",
            "pass": "pass",
            "raise": "raise ",
            "assert": "assert ",
            "and": "and ",
            "or": "or ",
            "not": "not ",
            "in": "in ",
            "is": "is ",
            "True": "True",
            "False": "False",
            "None": "None",
        }
        match = None
        for name, value in completions.items():
            if name.lower().startswith(current_word.lower()):
                match = (name, value)
                break
        if match:
            name, value = match
            start = max(0, offset - len(current_word))
            end = offset
            while end < len(source_code) and (
                source_code[end].isalnum() or source_code[end] == "_"
            ):
                end += 1
            suggestion = value
            explanation = f"The editor completed '{current_word}' into the Python pattern '{name}' commonly used in this context."
            cursor_offset = start + len(value) - (1 if value.endswith("()") else 0)
            replacement_mode = "replace"

    # Module attribute completions (e.g. np., pd., math., os., plt.)
    dot_match = re.search(
        r"([A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*)\.([A-Za-z0-9_]*)$",
        code_before_cursor,
    )
    if not suggestion and dot_match:
        mod_base = dot_match.group(1)
        attr_query = dot_match.group(2).lower()
        module_members = {
            "np": {
                "array": "array([1, 2, 3])",
                "zeros": "zeros((10, 10))",
                "ones": "ones((10, 10))",
                "arange": "arange(10)",
                "linspace": "linspace(0, 1, 100)",
                "mean": "mean()",
                "sum": "sum()",
                "dot": "dot()",
                "reshape": "reshape()",
            },
            "numpy": {
                "array": "array([1, 2, 3])",
                "zeros": "zeros((10, 10))",
                "ones": "ones((10, 10))",
                "arange": "arange(10)",
                "linspace": "linspace(0, 1, 100)",
                "mean": "mean()",
                "sum": "sum()",
                "dot": "dot()",
                "reshape": "reshape()",
            },
            "pd": {
                "DataFrame": "DataFrame()",
                "Series": "Series()",
                "read_csv": "read_csv('data.csv')",
                "concat": "concat()",
            },
            "pandas": {
                "DataFrame": "DataFrame()",
                "Series": "Series()",
                "read_csv": "read_csv('data.csv')",
                "concat": "concat()",
            },
            "plt": {
                "plot": "plot([1, 2, 3])",
                "show": "show()",
                "figure": "figure()",
                "title": "title('')",
                "xlabel": "xlabel('')",
                "ylabel": "ylabel('')",
            },
            "math": {
                "sqrt": "sqrt()",
                "floor": "floor()",
                "ceil": "ceil()",
                "pi": "pi",
                "sin": "sin()",
                "cos": "cos()",
            },
            "os.path": {
                "join": "join()",
                "exists": "exists()",
                "basename": "basename()",
                "dirname": "dirname()",
            },
            "os": {
                "getcwd": "getcwd()",
                "environ": "environ",
                "listdir": "listdir('.')",
                "path": "path.join()",
            },
            "json": {
                "loads": "loads()",
                "dumps": "dumps()",
                "load": "load()",
                "dump": "dump()",
            },
            "re": {
                "search": "search(r'', )",
                "match": "match(r'', )",
                "findall": "findall(r'', )",
                "sub": "sub(r'', '', )",
            },
            "sys": {
                "argv": "argv",
                "exit": "exit(0)",
                "path": "path",
            },
        }
        members = module_members.get(mod_base, {})
        attr_match_item = None
        for m_name, m_val in members.items():
            if m_name.lower().startswith(attr_query):
                attr_match_item = (m_name, m_val)
                break
        if attr_match_item:
            m_name, m_val = attr_match_item
            start = max(0, offset - len(attr_query))
            end = offset
            suggestion = m_val
            explanation = f"Completes {mod_base} member to '{m_name}'."
            cursor_offset = start + len(m_val) - (1 if m_val.endswith("()") else 0)
            replacement_mode = "replace"
            validation_status = "validated"

    # Contextual completions following an import statement
    lines_split = prefix.split("\n")
    current_line_content = lines_split[-1] if lines_split else ""
    is_line_start = not current_line_content.strip()
    nonempty_lines = [l.strip() for l in prefix.splitlines() if l.strip()]
    prev_line = nonempty_lines[-1] if nonempty_lines else ""
    if not suggestion and is_line_start and prev_line.startswith(("import ", "from ")):
        indentation = " " * len(current_line_content)
        if "numpy" in prev_line or "as np" in prev_line:
            suggestion = "data = np.array([1, 2, 3])"
            explanation = "Common NumPy workflow: initialize an array to work with the imported library."
        elif "pandas" in prev_line or "as pd" in prev_line:
            suggestion = "df = pd.DataFrame({'a': [1, 2, 3]})"
            explanation = "Common Pandas workflow: initialize a DataFrame from the imported module."
        elif "matplotlib" in prev_line or "as plt" in prev_line:
            suggestion = "plt.plot([1, 2, 3])"
            explanation = "Common Matplotlib workflow: create a figure using plt.plot()."
        elif "os" in prev_line:
            suggestion = "cwd = os.getcwd()"
            explanation = "Common os module workflow: obtain the current working directory."
        elif "sys" in prev_line:
            suggestion = "args = sys.argv"
            explanation = "Common sys module workflow: access command line arguments."
        elif "json" in prev_line:
            suggestion = "data = json.loads('{}')"
            explanation = "Common json module workflow: parse structured JSON data."
        elif "math" in prev_line:
            suggestion = "result = math.sqrt(16)"
            explanation = "Common math module workflow: compute mathematical square root."
        else:
            suggestion = "def main():\n" + indentation + "    pass"
            explanation = "Define a main application entrypoint following module imports."
        start = offset
        end = offset
        cursor_offset = offset + len(suggestion)
        replacement_mode = "insert"
        validation_status = "validated"

    elif not suggestion and last_line.strip().startswith(("import ", "from ")) and not suffix.strip():
        if "numpy" in last_line or "as np" in last_line:
            suggestion = "\ndata = np.array([1, 2, 3])"
            explanation = "Common NumPy workflow: initialize an array following the import statement."
        elif "pandas" in last_line or "as pd" in last_line:
            suggestion = "\ndf = pd.DataFrame({'a': [1, 2, 3]})"
            explanation = "Common Pandas workflow: initialize a DataFrame following the import statement."
        elif "matplotlib" in last_line or "as plt" in last_line:
            suggestion = "\nplt.plot([1, 2, 3])"
            explanation = "Common Matplotlib workflow: create a plot following the import statement."
        elif "os" in last_line:
            suggestion = "\ncwd = os.getcwd()"
            explanation = "Common os workflow: obtain current working directory."
        elif "sys" in last_line:
            suggestion = "\nargs = sys.argv"
            explanation = "Common sys workflow: access command line arguments."
        elif "json" in last_line:
            suggestion = "\ndata = json.loads('{}')"
            explanation = "Common json workflow: parse structured JSON data."
        elif "math" in last_line:
            suggestion = "\nresult = math.sqrt(16)"
            explanation = "Common math workflow: compute mathematical square root."
        else:
            suggestion = "\ndef main():\n    pass"
            explanation = "Define a main application entrypoint following module imports."
        start = offset
        end = offset
        cursor_offset = offset + len(suggestion)
        replacement_mode = "insert"
        validation_status = "validated"

    elif not suggestion and last_line.strip() == "print":
        suggestion = "print()"
        explanation = "A print statement is often used for quick debug output; the editor completes the call and keeps the cursor inside the parentheses."
        cursor_offset = offset + 6
    elif not suggestion and (last_line.strip().startswith("if ") or last_line.strip().startswith("elif ")):
        suggestion = "\n    pass"
        explanation = "The condition is active; a pass placeholder keeps the branch syntactically valid until you add the body."
    elif not suggestion and (last_line.strip().startswith("for ") or last_line.strip().startswith("while ")):
        suggestion = "\n    break"
        explanation = "The loop needs a body, and a break is a safe placeholder until the iteration logic is defined."
    elif not suggestion and last_line.strip().startswith("def "):
        suggestion = "\n    pass"
        explanation = "A function body must be defined; a pass placeholder preserves valid Python without changing behavior."
    elif not suggestion and last_line.strip().endswith("="):
        suggestion = " 0"
        explanation = "The assignment is incomplete; a default value placeholder keeps the statement valid for editing."
    elif not suggestion and "print(" in last_line and last_line.count("(") > last_line.count(")"):
        suggestion = ")"
        explanation = "This looks like an incomplete print call; the completion closes the call expression."

    if replacement_mode == "cursor":
        end = (
            offset + len(suffix) - len(suffix.lstrip())
            if suffix and suffix[:1].isspace() and len(suffix.strip()) > 0
            else offset
        )
        end = max(end, start)

    if last_line.strip() == "print":
        start = max(0, offset - len("print"))
        end = offset
        cursor_offset = start + len("print()") - 1

    valid_suggestion_types = {
        "completion",
        "comment",
        "docstring",
        "warning",
        "fix",
        "pair",
    }
    normalized_type = (
        suggestion_type if suggestion_type in valid_suggestion_types else "completion"
    )

    updated_source = source_code[:start] + suggestion + source_code[end:]
    return {
        "suggestion": suggestion,
        "replacement_range": {
            "start": to_utf16_offset(source_code, start),
            "end": to_utf16_offset(source_code, end),
        },
        "suggestion_type": normalized_type,
        "explanation": explanation,
        "validation_status": validation_status,
        "warnings": warnings,
        "cursor_offset": to_utf16_offset(updated_source, cursor_offset),
        "analysis": analysis,
        "quality_summary": quality_summary,
        "quality_score": quality_summary["score"],
        "review_score": build_review_score(warnings),
    }
