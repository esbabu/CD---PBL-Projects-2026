"""Structured AI prompt construction."""

from backend.ast_analyzer import get_pretty_ast


def build_prompt_payload(source_code, analysis):
    return {
        "source_code": source_code,
        "ast_summary": analysis["summary"],
        "warnings": analysis["warnings"],
        "context": "Use the AST summary as the source of truth; do not invent behavior. Add comments only where they are useful, preserve execution logic exactly, and return valid Python.",
    }


def build_ai_messages(source_code, analysis):
    pretty_ast = get_pretty_ast(source_code)
    return [
        {
            "role": "system",
            "content": (
                "You are an expert Python code documenter. Document the provided Python code with high technical depth and precision. "
                "Include clear, informative comments above import statements (explaining the domain purpose of the imported libraries, such as NumPy for multi-dimensional numerical computing or Pandas for data analysis). "
                "Add a substantive multi-line docstring to every function and method that lacks one. "
                "For non-trivial functions, use at least two informative sentences: explain the function's purpose, the actual algorithm in execution order, "
                "important conditions or edge cases, and what it returns or changes, but include only details supported by the source and AST. "
                "For a truly trivial function, keep the docstring brief but still explain what its result means. "
                "Add inline comments before non-obvious transformations, data structures, loops, or branches to explain what the step does and why it matters; "
                "do not leave a function with only a generic one-line comment. "
                "Do not infer parameter types or guarantees. Do not write typed Args, Parameters, or Returns sections. "
                'Treat item["score"] as key/index access, not an object attribute; describe sorted(items) as sorting an iterable unless its type is explicit. '
                "Do not add complexity badges or numbers. Avoid restating obvious syntax, and preserve executable code exactly. Return valid Python."
            ),
        },
        {
            "role": "user",
            "content": (
                f"=== Source Code ===\n\n{source_code}\n\n"
                f"=== Pretty-printed AST ===\n\n{pretty_ast}\n\n"
                f"=== Deterministic Findings ===\n\n{analysis.get('warnings', [])}\n\n"
                "Document this code thoroughly. For any imports, add comments explaining their domain purpose. "
                "Write enough detail that a reader can follow the code's purpose, the transformation in execution order, and how its result is produced. "
                "Every function or method without an existing docstring needs one; for non-trivial functions, include at least two useful sentences "
                "covering applicable conditions, edge cases, return values, and side effects. Add inline comments for meaningful non-obvious steps, "
                "especially filtering, sorting, accumulation, mutation, and branch decisions. A vague comment such as 'processes the data' is not sufficient. "
                "Do not pad the explanation by repeating the code or stating obvious syntax. "
                "Use generic terms such as iterable when the input type is not established. Do not add typed parameter sections, filler comments, or complexity labels. "
                "Return only the commented Python code, with no markdown fences or extra explanation."
            ),
        },
    ]
