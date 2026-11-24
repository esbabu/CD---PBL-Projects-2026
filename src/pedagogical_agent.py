"""
Pedagogical Agent Module - Intent-Aware Educational Explanations
Analyzes student code and runtime/compile errors to infer pedagogical intent
and provide clear, constructive learning feedback.
Supports Python, C++, and Java with full structured diagnostic cards.
"""

import re
from typing import Optional, Dict, Any, List


class PedagogicalAgent:
    """
    Pedagogical agent that deterministically infers student intent from
    source code and error context to produce beginner-friendly explanations
    and structured diagnostic cards.
    """

    def generate_explanation(self, error_type: str, code: str, error_msg: str) -> str:
        """
        Generate a pedagogical, intent-aware explanation for an error.
        Maintains backward compatibility with pipeline calls.
        """
        card = self.generate_diagnostic_card(
            error_type=error_type,
            code=code,
            error_msg=error_msg,
            language="auto"
        )
        return card.get("pedagogical_explanation", "")

    def generate_diagnostic_card(
        self,
        error_type: str,
        code: str,
        error_msg: str = "",
        line: Optional[int] = None,
        column: Optional[int] = None,
        language: str = "python",
        code_snippet: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generates a comprehensive 5-part teaching card for any error across Python, C++, and Java.
        Accepts optional aliases via kwargs for flexible callers (raw_message, line_number).
        """
        if not error_msg and "raw_message" in kwargs:
            error_msg = kwargs["raw_message"] or ""
        if line is None and "line_number" in kwargs:
            line = kwargs["line_number"]
        if column is None and "column_number" in kwargs:
            column = kwargs["column_number"]
        error_type = (error_type or "RuntimeError").strip()
        error_msg = (error_msg or "").strip()
        code = code or ""
        lang = language.lower() if language else "python"

        # Determine line snippet if omitted
        lines = code.splitlines() if code else []
        if not code_snippet and line and 1 <= line <= len(lines):
            code_snippet = lines[line - 1].strip()

        # Defaults
        severity = "ERROR"
        concept = "Code Syntax and Language Semantics"
        attempted = "The program attempted to execute instructions at the specified line."
        failed = f"The execution or compilation failed with message: {error_msg or error_type}."
        why = "The language interpreter or compiler encountered an instruction that violates language rules."
        cause = "A mismatch between the written syntax/types and the language specification."
        pedagogical = f"An error occurred ({error_type}). Carefully review the indicated line for syntax or logical issues."
        example = None
        how_to_avoid = "Double-check your syntax against language conventions and verify types before operating on them."
        changes_made = None
        assumptions = None
        fix_explanation = None

        # =========================================================================
        # 1. PYTHON ERRORS
        # =========================================================================

        # 1.1 TypeError
        if error_type == "TypeError":
            concept = "Data Types & Type Compatibility"
            if "print" in code and ("can only concatenate str" in error_msg or "unsupported operand type" in error_msg or "+" in code):
                attempted = "The program attempted to concatenate a string with a non-string value (like an integer or float) using the '+' operator inside a print statement."
                failed = "Python disallows implicit type coercion during string concatenation with '+'. Operands must be of matching string types."
                why = "In Python, '+' is overloaded: for numbers it performs addition; for strings it performs concatenation. Python refuses to guess whether you meant to add numbers or concatenate text."
                cause = "One of the expressions combined with '+' is an int, float, or object rather than a string."
                pedagogical = (
                    "It looks like you are trying to print mixed types (such as combining text with a number or variable) using '+'. "
                    "In Python, you cannot concatenate strings and numbers directly with '+'. "
                    "You can wrap the non-string value in str(...), separate items with commas inside print(...), "
                    "or use a modern f-string like f'Value: {variable}'."
                )
                example = "❌ Wrong: print('Age: ' + age)\n✅ Right (f-string): print(f'Age: {age}')\n✅ Right (str wrap): print('Age: ' + str(age))\n✅ Right (commas): print('Age:', age)"
                how_to_avoid = "Prefer using f-strings (f'{var}') or separating arguments with commas in print() statements instead of using '+'."
                changes_made = "Wrapped the non-string variable with str(...) to ensure valid concatenation."
            elif "not callable" in error_msg:
                match = re.search(r"'([^']+)' object is not callable", error_msg)
                obj_t = match.group(1) if match else "variable"
                attempted = f"The program attempted to invoke a {obj_t} as a function using parentheses '()'."
                failed = f"The object of type '{obj_t}' does not implement the __call__ protocol and cannot be executed as a function."
                why = "Only functions, classes, and callable objects can follow an identifier with parentheses '()'."
                cause = f"You may have defined a variable named '{obj_t}' (or shadowed a builtin like 'list', 'str', 'int'), or used '()' instead of '[]' for index lookup."
                pedagogical = (
                    f"It looks like you are calling a {obj_t} with parentheses '()', as if it were a function. "
                    "Check if you accidentally named a variable the same as a built-in function, "
                    "or if you meant to use square brackets '[]' for list/dictionary indexing."
                )
                example = "❌ Wrong: my_list(0)  # Uses parentheses\n✅ Right: my_list[0]  # Uses square brackets for indexing"
                how_to_avoid = "Use square brackets [] for indexing collections, and avoid naming variables after built-in types (e.g., don't name a variable 'str', 'list', or 'dict')."
                changes_made = "Replaced invalid parentheses with square indexing brackets."
            elif "not subscriptable" in error_msg:
                match = re.search(r"'([^']+)' object is not subscriptable", error_msg)
                obj_t = match.group(1) if match else "variable"
                concept = "Sequence Indexing & Data Structures"
                attempted = f"The program attempted to index or slice a {obj_t} object with square brackets '[]'."
                failed = f"A {obj_t} is a single scalar value and does not support indexing (__getitem__)."
                why = "Subscripting requires an iterable collection or sequence such as a list, tuple, dictionary, or string."
                cause = f"The variable being indexed holds a {obj_t} rather than a collection."
                pedagogical = (
                    f"It looks like you are trying to index or slice a {obj_t} using square brackets '[]'. "
                    f"A {obj_t} is a single scalar value and does not contain indexed elements like a list or string. "
                    "Verify the variable holding the collection you want to access."
                )
                example = "❌ Wrong: x = 10; print(x[0])\n✅ Right: x = [10, 20]; print(x[0])"
                how_to_avoid = "Verify that the variable you are indexing is actually a list, tuple, or string before using []."
            else:
                pedagogical = (
                    f"Incompatible types were used in an operation ({error_msg}). "
                    "Python is strongly typed and will not automatically convert types unless told to. "
                    "Convert values explicitly using int(), float(), or str()."
                )

        # 1.2 NameError
        elif error_type == "NameError":
            concept = "Variable Scope & Symbol Definition"
            match = re.search(r"name '([^']+)' is not defined", error_msg)
            bad_name = match.group(1) if match else (code_snippet or "variable")
            
            builtins_map = {
                "prnt": "print", "pritn": "print", "prin": "print", "pirnt": "print",
                "rang": "range", "rnage": "range", "rage": "range",
                "lenght": "len", "leng": "len", "ln": "len",
                "inpt": "input", "imput": "input", "iput": "input",
                "true": "True", "false": "False", "none": "None"
            }
            if bad_name.lower() in builtins_map:
                suggested = builtins_map[bad_name.lower()]
                attempted = f"The code attempted to call or reference the identifier '{bad_name}'."
                failed = f"The name '{bad_name}' does not exist in local, enclosing, global, or built-in scopes."
                why = "Python is strictly case-sensitive and enforces exact spelling for all identifiers."
                cause = f"Typographical error: typed '{bad_name}' instead of standard built-in '{suggested}'."
                pedagogical = (
                    f"It looks like you were trying to use the Python built-in '{suggested}', but typed '{bad_name}'. "
                    f"Python is case-sensitive and requires exact spelling. Replace '{bad_name}' with '{suggested}'."
                )
                example = f"❌ Wrong: {bad_name}('Hello')\n✅ Right: {suggested}('Hello')"
                how_to_avoid = f"Use code editor autocomplete and double-check standard function names like '{suggested}'."
                changes_made = f"Corrected misspelled identifier '{bad_name}' to '{suggested}'."
            elif re.search(rf"\bfor\s+\w+\s+in\s+{re.escape(bad_name)}\b", code):
                attempted = f"The loop attempted to iterate through '{bad_name}'."
                failed = f"Python could not find a variable named '{bad_name}' in the current scope."
                why = "A collection or range must be created and assigned before a for-loop can iterate over it."
                cause = f"The variable '{bad_name}' was never defined prior to the loop."
                pedagogical = (
                    f"It looks like you are trying to loop over '{bad_name}', but '{bad_name}' hasn't been defined yet. "
                    f"Define '{bad_name}' as a list, string, or range before the loop."
                )
                example = f"❌ Wrong: for x in {bad_name}:\n✅ Right:\n{bad_name} = [1, 2, 3]\nfor x in {bad_name}:"
                how_to_avoid = "Always declare and initialize collections before referencing them in iteration loops."
                assumptions = f"Assumed '{bad_name}' was meant to be defined prior to the loop."
            else:
                attempted = f"The program attempted to access the variable '{bad_name}'."
                failed = f"No variable or function named '{bad_name}' has been defined in scope."
                why = "In Python, variables must be assigned a value before they can be read or evaluated."
                cause = f"Either '{bad_name}' has a typo, or you forgot to assign it an initial value earlier in the script."
                pedagogical = (
                    f"It looks like you are trying to use '{bad_name}', but Python cannot find a definition for it. "
                    f"Make sure you define or assign a value to '{bad_name}' before this line, and check for typos."
                )
                example = f"❌ Wrong: result = {bad_name} + 5\n✅ Right:\n{bad_name} = 10\nresult = {bad_name} + 5"
                how_to_avoid = "Check that variables are declared above the line where they are used, and verify case spelling."
                fix_explanation = f"Automatic fix unavailable: Variable '{bad_name}' requires an initial value or declaration appropriate to your algorithm."

        # 1.3 SyntaxError
        elif error_type == "SyntaxError":
            concept = "Grammar, Punctuation & Syntax Rules"
            # Single '=' used in condition
            if re.search(r"\b(?:if|while|elif)\s+[\w\.\[\]]+\s*=\s*[\w\.\[\]]+\s*:", code) or re.search(r"\b(?:if|while|elif)\s+[^=]*=(?!=)[^=]*:", code):
                concept = "Assignment vs Equality Comparison"
                attempted = "The program attempted to test a conditional statement using a single '=' sign."
                failed = "A single '=' is the assignment operator in Python and cannot be used in a condition header."
                why = "Python syntax forbids assignment statements in conditional test expressions to prevent accidental logic errors."
                cause = "Used '=' (assignment) instead of '==' (equality check) in an if/while statement."
                pedagogical = (
                    "It looks like you used a single '=' in a condition (like an if-statement). "
                    "In Python, a single '=' is used for assigning variables (e.g., `x = 10`), "
                    "while double '==' is used to check if two values are equal (e.g., `if x == 10:`)."
                )
                example = "❌ Wrong: if count = 5:\n✅ Right: if count == 5:"
                how_to_avoid = "Remember: single '=' assigns a value; double '==' compares two values."
                changes_made = "Replaced '=' assignment with '==' equality comparison operator."
            # Missing colon
            elif re.search(r"^\s*(?:def|if|for|while|class|elif|else)(?:\s+.*)?[^:]\s*$", code, re.MULTILINE):
                attempted = "The program attempted to open a new compound block statement (such as if, for, while, or def)."
                failed = "The statement header line did not end with a colon ':'."
                why = "In Python grammar, every block header must terminate with a colon ':' to signal the start of an indented suite."
                cause = "Omitted the required colon ':' at the end of the header line."
                pedagogical = (
                    "It looks like you are defining a block (like an if-statement, loop, or function), "
                    "but forgot the colon ':' at the end of the line. "
                    "In Python, headers for 'def', 'if', 'for', 'while', 'elif', and 'else' must end with a colon ':'."
                )
                example = "❌ Wrong: if score > 50\n    print('Pass')\n✅ Right: if score > 50:\n    print('Pass')"
                how_to_avoid = "Always finish lines starting with if, elif, else, for, while, def, and class with a colon ':'."
                changes_made = "Appended the missing ':' colon to the block statement header."
            # Unclosed parens
            elif code.count("(") > code.count(")"):
                open_cnt = code.count("(")
                close_cnt = code.count(")")
                concept = "Delimiters and Parentheses Matching"
                attempted = "The program opened parenthetical expressions."
                failed = f"Found {open_cnt} opening '(' but only {close_cnt} closing ')'."
                why = "All opened grouping delimiters must be closed before the statement ends or file terminates."
                cause = "Missing closing parenthesis ')'."
                pedagogical = (
                    f"It looks like you have an unclosed parenthesis '(' in your code (found {open_cnt} '(' but only {close_cnt} ')'). "
                    "Make sure every opening parenthesis has a matching closing parenthesis."
                )
                example = "❌ Wrong: print(calculate(10, 20)\n✅ Right: print(calculate(10, 20))"
                how_to_avoid = "Count your opening and closing parentheses, or check editor bracket matching highlights."
                changes_made = f"Added {open_cnt - close_cnt} closing parenthesis ')'."
            else:
                pedagogical = (
                    f"Python encountered a syntax error: {error_msg}. "
                    "Check for missing punctuation (like colons or commas), unmatched quotes, or unclosed parentheses."
                )

        # 1.4 IndexError
        elif error_type == "IndexError":
            concept = "Zero-Based Sequence Bounds & Off-by-One"
            attempted = "The code attempted to access a sequence item at an index outside its valid boundary."
            failed = "The index provided is greater than or equal to the length of the list, or negative and out of bounds."
            why = "Python lists are 0-indexed; valid indices range from 0 to len(list) - 1."
            cause = "Accessing index N on a list with N or fewer elements (common off-by-one error)."
            pedagogical = (
                "It looks like you are trying to access an item at an index that doesn't exist in your list or sequence. "
                "Remember that Python uses 0-based indexing (the first element is index 0, and the last is len - 1). "
                "Check that the list isn't empty and that your index is strictly less than len(your_list)."
            )
            example = "❌ Wrong:\nitems = ['apple', 'banana']\nprint(items[2])  # len is 2, valid indices are 0 and 1!\n✅ Right:\nprint(items[1])  # 'banana'"
            how_to_avoid = "Verify list length using len(my_list) or loop directly over items (`for item in my_list:`) rather than indices."

        # 1.5 KeyError
        elif error_type == "KeyError":
            concept = "Dictionary Key Lookup & Safe Access"
            match = re.search(r"KeyError:\s*['\"]?([^'\"]+)['\"]?", error_msg)
            k_name = match.group(1) if match else "key"
            attempted = f"The code attempted to look up the key '{k_name}' in a dictionary using square brackets []."
            failed = f"The dictionary does not contain the key '{k_name}'."
            why = "Using dict[key] raises KeyError when the key is absent from the dictionary hash map."
            cause = f"The key '{k_name}' was never inserted into the dictionary or has a typo."
            pedagogical = (
                f"It looks like you are trying to access the key '{k_name}' from a dictionary, but that key does not exist. "
                "To safely retrieve values that may not be present, use dict.get(key, default) or test `if key in dict:` first."
            )
            example = f"❌ Wrong: val = my_dict['{k_name}']\n✅ Right (Safe get): val = my_dict.get('{k_name}', 0)\n✅ Right (Membership check): if '{k_name}' in my_dict: val = my_dict['{k_name}']"
            how_to_avoid = "Use `.get(key, default_value)` when retrieving optional dictionary keys."

        # 1.6 ZeroDivisionError
        elif error_type == "ZeroDivisionError":
            concept = "Arithmetic Constraints & Zero Division"
            attempted = "The program attempted to divide a number by zero or perform modulo by zero."
            failed = "Division by zero is mathematically undefined and cannot produce a numeric result."
            why = "Computer architectures and language specifications raise hardware or software exceptions on division by 0."
            cause = "The denominator variable or expression evaluated to 0."
            pedagogical = (
                "It looks like your code attempted to divide by zero or compute a modulo with zero. "
                "Division by zero is mathematically undefined. "
                "Always verify that the divisor variable is not zero before dividing, or provide a default fallback."
            )
            example = "❌ Wrong: average = total / count  # If count is 0, crash!\n✅ Right: average = total / count if count != 0 else 0"
            how_to_avoid = "Add an if-check `if divisor != 0:` before performing division or modulo operations."

        # 1.7 IndentationError
        elif error_type == "IndentationError":
            concept = "Block Structure via Indentation Whitespace"
            attempted = "The interpreter parsed the visual whitespace indentation of Python code."
            failed = "A line's indentation level did not match any outer code block."
            why = "Python uses indentation (4 spaces per level) instead of curly braces to delimit code blocks."
            cause = "Mixed tabs and spaces, or an unaligned line inside a function or loop."
            pedagogical = (
                "It looks like the indentation of your code is inconsistent. "
                "In Python, all lines within the same block (such as inside a function or loop) must have the exact same indentation. "
                "The standard practice is to use 4 spaces per indentation level."
            )
            example = "❌ Wrong:\ndef greet():\n  print('Hello')\n    print('World')  # Misaligned!\n✅ Right:\ndef greet():\n    print('Hello')\n    print('World')"
            how_to_avoid = "Configure your code editor to insert 4 spaces when pressing the Tab key."

        # 1.8 ModuleNotFoundError
        elif error_type in ("ModuleNotFoundError", "ImportError"):
            concept = "Package Management & Module Resolution"
            match = re.search(r"No module named '([^']+)'", error_msg)
            mod_name = match.group(1) if match else "module"
            attempted = f"The script attempted to import the external library '{mod_name}'."
            failed = f"Python could not find '{mod_name}' in sys.path or the active virtual environment."
            why = "Third-party libraries must be installed on the system via pip before they can be imported."
            cause = f"The library '{mod_name}' is not installed in the current Python environment."
            pedagogical = (
                f"It looks like you are trying to use the '{mod_name}' library, but it is not installed or not available in the current environment. "
                f"If you are working locally, you can install it by running `pip install {mod_name}` in your terminal. "
                "If you are using a virtual environment, ensure it is activated before running the script."
            )
            example = f"Terminal command:\n$ pip install {mod_name}"
            how_to_avoid = "Check that required packages are listed in your project requirements.txt and installed."

        # =========================================================================
        # 2. C++ ERRORS
        # =========================================================================

        # 2.1 C++ MissingSemicolon
        elif error_type == "MissingSemicolon" or (lang == "cpp" and "expected ';'" in error_msg.lower()):
            concept = "C++ Statement Termination Syntax"
            attempted = "The C++ compiler parsed statement expressions or class/struct definitions."
            failed = "A statement or type declaration ended without a terminating semicolon ';'."
            why = "In C++, semicolons ';' are explicit statement terminators. The compiler cannot infer where a statement ends without ';'."
            cause = "Omitted ';' at the end of an expression, return statement, or after a struct/class closing brace '};'."
            pedagogical = (
                "It looks like you wrote a statement or struct/class block in C++ but forgot to terminate it with a semicolon (';'). "
                "In C++, every statement (like variable declarations, cout statements, and return statements) "
                "as well as every struct and class definition (`struct MyNode { ... };`) must end with a semicolon ';'."
            )
            example = "❌ Wrong:\nint x = 5\nstruct Node { int val; }\n✅ Right:\nint x = 5;\nstruct Node { int val; };"
            how_to_avoid = "Always check the end of variable lines, return lines, and remember that struct/class definitions require `};`."
            changes_made = "Appended the missing ';' semicolon."

        # 2.2 C++ StreamOperatorError
        elif error_type == "StreamOperatorError" or "invalid stream operator" in error_msg.lower():
            concept = "C++ Stream Directionality & Operator Overloading"
            attempted = "The program attempted to send output to cout or read input from cin."
            failed = "Used the wrong operator direction (e.g., 'cout >>' or 'cin <<')."
            why = "'cout' uses the insertion operator '<<' (pointing data INTO the stream), while 'cin' uses the extraction operator '>>' (pulling data FROM the stream into a variable)."
            cause = "Inverted stream operator arrows."
            pedagogical = (
                "In C++, standard streams use arrows that show the direction data travels: "
                "- For output: `std::cout << data;` (arrows point towards cout, sending data to the screen). "
                "- For input: `std::cin >> variable;` (arrows point away from cin, saving input into your variable). "
                "Replace 'cout >>' with 'cout <<' and 'cin <<' with 'cin >>'."
            )
            example = "❌ Wrong: cout >> 'Hello'; cin << age;\n✅ Right: cout << 'Hello'; cin >> age;"
            how_to_avoid = "Think of '<<' as pointing data to the screen, and '>>' as pointing data into your variable."
            changes_made = "Corrected inverted stream operator direction."

        # 2.3 C++ MissingHeaderError
        elif error_type == "MissingHeaderError" or "using 'cout' or 'cin' without" in error_msg.lower() or "was not declared in this scope" in error_msg.lower() and "cout" in error_msg.lower():
            concept = "C++ Preprocessor & Standard Library Headers"
            attempted = "The code referenced std::cout or std::cin."
            failed = "The standard I/O stream declarations have not been included in the compilation unit."
            why = "C++ compilers require header files like `<iostream>` to define standard stream classes and operators."
            cause = "Missing `#include <iostream>` at the top of the file."
            pedagogical = (
                "Standard I/O stream objects (like `cout` and `cin`) live in the C++ Standard Library. "
                "To use them, you must include the `<iostream>` header at the very top of your file using `#include <iostream>`. "
                "Also ensure you use the `std::` prefix (or write `using namespace std;`)."
            )
            example = "❌ Wrong:\nint main() { cout << 'Hi'; }\n✅ Right:\n#include <iostream>\nint main() { std::cout << 'Hi'; }"
            how_to_avoid = "Always include `<iostream>` whenever your program interacts with the console."
            changes_made = "Added `#include <iostream>` header directive."

        # 2.4 C++ UndeclaredIdentifier
        elif error_type == "UndeclaredIdentifier" or (lang == "cpp" and "was not declared in this scope" in error_msg.lower()):
            concept = "C++ Static Typing & Variable Declaration"
            match = re.search(r"'([^']+)' was not declared", error_msg)
            var_name = match.group(1) if match else "variable"
            attempted = f"The program attempted to use the identifier '{var_name}'."
            failed = f"The compiler has no record of '{var_name}' in the current scope."
            why = "C++ is statically typed: every identifier must be declared with an explicit type (e.g. int, double, std::string) before use."
            cause = f"The identifier '{var_name}' was never declared or was misspelled."
            pedagogical = (
                f"It looks like you are trying to use '{var_name}', but it was not declared in this scope. "
                "In C++, every variable must be declared with its type (like `int`, `std::string`, or `double`) "
                "before it can be used. Declare the variable before this line, or check for typos."
            )
            example = f"❌ Wrong: cout << {var_name};\n✅ Right: int {var_name} = 10; cout << {var_name};"
            how_to_avoid = "Declare variables with their type before using them, and check spelling."
            assumptions = f"Assumed '{var_name}' was intended to be declared as an integer."

        # 2.5 C++ UnmatchedBrace / UnclosedBlock
        elif error_type in ("UnmatchedBrace", "UnclosedBlock") or (lang == "cpp" and "expected '}'" in error_msg.lower()):
            concept = "C++ Lexical Scoping & Block Closures"
            attempted = "The compiler parsed nested functions, classes, or control blocks."
            failed = "Found opening curly braces '{' without corresponding closing braces '}'."
            why = "In C++, code blocks must be balanced; every '{' must pair with a matching '}'."
            cause = "Omitted closing brace '}' at the end of a block or function."
            pedagogical = (
                "It looks like you opened a code block with '{' but didn't close it with a matching '}'. "
                "In C++, functions, classes, structs, loops, and if-statements require matching curly braces. "
                "Count your opening and closing braces to ensure they match."
            )
            example = "❌ Wrong: int main() { int x = 5;\n✅ Right: int main() { int x = 5; }"
            how_to_avoid = "Format code with consistent indentation to immediately spot missing closing braces."
            changes_made = "Added matching '}' closing brace."

        # =========================================================================
        # 3. JAVA ERRORS
        # =========================================================================

        # 3.1 Java SystemOutCaseError
        elif error_type == "SystemOutCaseError" or "system.out" in error_msg.lower():
            concept = "Java Class Naming Conventions & Case Sensitivity"
            attempted = "The program attempted to print to standard output via system.out.print*."
            failed = "Java cannot resolve lowercase 'system'."
            why = "In Java, standard library classes follow PascalCase. The standard output class is 'System' (capital S), not 'system'."
            cause = "Typed lowercase 's' in 'system.out.println'."
            pedagogical = (
                "Java is strictly case-sensitive. The standard output stream belongs to the `System` class "
                "with an uppercase 'S'. Writing `system.out.println` with a lowercase 's' causes a compilation error. "
                "Capitalize 'System' to fix the error."
            )
            example = "❌ Wrong: system.out.println('Hello');\n✅ Right: System.out.println('Hello');"
            how_to_avoid = "Remember: in Java, classes start with an uppercase letter: `System.out.println`."
            changes_made = "Capitalized 'System' in System.out.println statement."

        # 3.2 Java MissingMainMethod
        elif error_type == "MissingMainMethod" or "main method not found" in error_msg.lower():
            concept = "Java Program Entry Point Specification"
            attempted = "The Java Virtual Machine (JVM) attempted to launch the program."
            failed = "No valid `public static void main(String[] args)` method was found in the class."
            why = "Java programs require an exact entry point signature to execute standalone: `public static void main(String[] args)`."
            cause = "Missing the main method declaration or having an incorrect signature."
            pedagogical = (
                "Every executable Java program must have an entry point method with this exact signature: "
                "`public static void main(String[] args)`. "
                "Make sure your executable code is placed inside this method."
            )
            example = "✅ Right:\npublic class Main {\n    public static void main(String[] args) {\n        System.out.println('Hello');\n    }\n}"
            how_to_avoid = "Always wrap standalone Java code in a class with a standard `main` method."

        # 3.3 Java CannotFindSymbol
        elif error_type == "CannotFindSymbol" or "cannot find symbol" in error_msg.lower():
            concept = "Java Symbol Resolution & Variable Declaration"
            match = re.search(r"symbol:\s*variable\s+([^\s]+)", error_msg)
            s_name = match.group(1) if match else "identifier"
            attempted = f"The compiler attempted to look up '{s_name}'."
            failed = f"No variable, method, or class named '{s_name}' was found in scope."
            why = "Java is statically typed and requires all symbols to be declared with a type before reference."
            cause = f"The symbol '{s_name}' was not declared or has a spelling mistake."
            pedagogical = (
                f"The Java compiler cannot find the symbol '{s_name}'. "
                "This usually means you forgot to declare the variable with its type (e.g. `int {s_name} = 0;`), "
                "misspelled a method name, or referenced a variable outside the block where it was defined."
            )
            example = f"❌ Wrong: {s_name} = 10;\n✅ Right: int {s_name} = 10;"
            how_to_avoid = "Declare variables before use, check casing, and check scope boundaries."

        # 3.4 Java MissingSemicolon
        elif error_type == "MissingSemicolon" and lang == "java":
            concept = "Java Statement Delimitation"
            attempted = "The Java compiler parsed statements."
            failed = "Found a statement without a closing semicolon ';'."
            why = "In Java grammar, every statement must end with a semicolon ';'."
            cause = "Omitted ';' at the end of a line."
            pedagogical = (
                "In Java, every statement (variable assignment, method call, return statement) must terminate with a semicolon (';'). "
                "Add a semicolon ';' to the end of the statement line."
            )
            example = "❌ Wrong: int x = 5\n✅ Right: int x = 5;"
            how_to_avoid = "Check line endings for missing semicolons."
            changes_made = "Appended the missing ';' semicolon."

        # =========================================================================
        # 4. SECURITY BLOCKS
        # =========================================================================
        elif error_type in ("SecurityError", "SecurityViolation"):
            severity = "CRITICAL"
            concept = "Application Security Policy & Sandboxing"
            attempted = "The submitted code attempted to execute high-risk operations (e.g. system commands, file destruction, unauthorized sockets)."
            failed = f"The security policy intercepted and aborted execution: {error_msg}."
            why = "In an educational sandbox, operations that can modify the host operating system or network are strictly prohibited for safety."
            cause = "Use of prohibited modules (os, subprocess, socket), dangerous calls (eval, exec, system), or unauthorized headers."
            pedagogical = (
                "Your code was blocked because it contains potentially dangerous operations. "
                "In a learning environment, operations like running terminal commands (`os.system`), deleting files, "
                "or dynamic execution (`eval`/`exec`) are disabled to ensure safety. "
                "Remove the prohibited calls and focus on core algorithmic logic."
            )
            example = "❌ Prohibited: import os; os.system('rm -rf /')\n✅ Safe: Focus on algorithms, data structures, and mathematical computation."
            how_to_avoid = "Do not include OS, process-spawning, or socket networking libraries in tutor code."
            fix_explanation = "Security violation: Dangerous operations cannot be repaired automatically; remove prohibited calls."

        # Structured diagnostic card assembly
        diagnostic_text = (
            f"• What was attempted: {attempted}\n"
            f"• What went wrong: {failed}\n"
            f"• Why it is an error: {why}\n"
            f"• Root cause: {cause}"
        )

        full_pedagogical = pedagogical
        if example:
            full_pedagogical += f"\n\n**Illustrative Example:**\n```\n{example}\n```"
        if how_to_avoid:
            full_pedagogical += f"\n\n**How to Avoid:** {how_to_avoid}"

        return {
            "error_type": error_type,
            "severity": severity,
            "line_number": line,
            "column_number": column,
            "code_snippet": code_snippet,
            "underlying_concept": concept,
            "diagnostic": diagnostic_text,
            "diagnostic_details": {
                "attempted": attempted,
                "failed": failed,
                "flagged_reason": why,
                "root_cause": cause
            },
            "pedagogical_explanation": full_pedagogical,
            "illustrative_example": example,
            "how_to_avoid": how_to_avoid,
            "changes_made": changes_made,
            "assumptions": assumptions,
            "fix_explanation": fix_explanation,
            "confidence": 1.0
        }
