import ast
import copy
import re  # Added for the fallback typo detection
from .security import CodeSecurityValidator
from .error_capture import ErrorCapture
from .ast_parser import ASTContextExtractor

class SecurityAgent:
    """The Bouncer: Checks code for safety before execution."""
    def __init__(self):
        self.validator = CodeSecurityValidator()

    def check(self, code: str):
        is_safe, warnings = self.validator.validate(code)
        return is_safe, warnings

class ExecutionSandbox:
    """The Safe Room: Runs code and captures errors."""
    def __init__(self):
        self.capturer = ErrorCapture()

    def run(self, code: str):
        success, error_info = self.capturer.execute_code(code)
        return success, error_info

class DiagnosticAgent:
    """The Doctor: Analyzes the error and finds the root cause."""
    def __init__(self):
        self.ast_extractor = ASTContextExtractor()

    def diagnose(self, error_info: dict):
        ast_context = self.ast_extractor.analyze_error_context(error_info)
        return {
            "error_type": error_info.get("error_type"),
            "message": error_info.get("message"),
            "line_number": error_info.get("line_number"),
            "similar_names": ast_context.get("similar_names", []),
            "context": ast_context
        }

class FixerAgent:
    """The Handyman: Attempts to automatically fix the code."""
    def __init__(self):
        pass

    def fix(self, code: str, diagnosis: dict):
        """
        A rule-based fixer with a smart fallback for NameErrors.
        """
        error_type = diagnosis["error_type"]
        line_number = diagnosis["line_number"]
        similar_names = diagnosis.get("similar_names", [])

        lines = code.split("\n")

        # Rule 1: Fix NameError typos (e.g., prnt -> print, score -> total_score)
        if error_type == "NameError":
            typo = None
            if "name '" in diagnosis["message"]:
                typo = diagnosis["message"].split("'")[1]
            
            if typo:
                replacement = None
                
                # 1. First try the AST similar names (Levenshtein distance)
                if similar_names:
                    replacement = similar_names[0]
                else:
                    # 2. FALLBACK: Find any variable in the code that contains the typo
                    variables = re.findall(r'\b[A-Za-z_][A-Za-z0-9_]*\b', code)
                    for var in variables:
                        if typo in var and var != typo:  # e.g., 'score' is in 'total_score'
                            replacement = var
                            break
                
                # Apply the fix to the specific line
                if replacement and line_number and 1 <= line_number <= len(lines):
                    lines[line_number - 1] = lines[line_number - 1].replace(typo, replacement)

        # Rule 2: Fix ZeroDivisionError
        elif error_type == "ZeroDivisionError":
            if line_number and 1 <= line_number <= len(lines):
                lines[line_number - 1] = f"# Fixed ZeroDivision: {lines[line_number - 1]}\npass"

        # Add more rules here for other error types...
        
        return "\n".join(lines)

class ExplainerAgent:
    """The Teacher: Generates the final human-friendly explanation."""
    def __init__(self, ai_model=None):
        self.ai_model = ai_model # Pass your T5 model here if you want

    def explain(self, diagnosis: dict, fixed_code: str, original_error_info: dict):
        # For now, use the fallback rule-based explanation to ensure it works
        from .model import FallbackExplainer
        fallback = FallbackExplainer()
        
        explanation = fallback.explain(
            diagnosis["error_type"],
            diagnosis["message"]
        )
        
        # Add typo suggestions if they exist
        if diagnosis["similar_names"]:
            explanation += f" Did you mean: {', '.join(diagnosis['similar_names'])}?"

        suggested_fix = f"Here is the corrected code:\n\n```python\n{fixed_code}\n```"

        return explanation, suggested_fix
