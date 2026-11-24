"""
Agent Module - Agentic Error Correction System (Version 1.0)
Orchestrates the generation and validation of candidate code fixes.
"""

from typing import Dict, Any, Optional
import re

try:
    from .optimizer import OptimizationAgent
except ImportError:
    from optimizer import OptimizationAgent

class RepairAgent:
    def __init__(self, error_capture):
        """
        Initialize the Agent with the existing ErrorCapture instance.
        This allows the agent to validate candidate code using the same security
        and execution pipeline as the rest of the application.
        """
        self.error_capture = error_capture

    def attempt_repair(self, original_code: str, error_info: Dict[str, Any], ast_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Agentic loop:
        1. Generate a candidate fix.
        2. Validate the fix using ErrorCapture.
        3. If invalid, try one more time (max 2 attempts).
        4. Return the final result.
        """
        max_attempts = 2
        attempts = 0
        candidate_code = original_code
        validated = False
        last_validation_error = None

        while attempts < max_attempts and not validated:
            attempts += 1
            
            # Step 1: Generate candidate correction
            candidate_code = self._generate_candidate_code(
                candidate_code, # Pass the latest candidate for retry
                error_info, 
                ast_context, 
                last_validation_error
            )

            # Check if we didn't actually change anything, avoid infinite useless loops
            if candidate_code == original_code and attempts > 1:
                break

            # Step 2: Validate the candidate code via existing security + exec pipeline
            success, new_error_info = self.error_capture.execute_code(candidate_code)

            if success:
                validated = True
                break
            else:
                last_validation_error = new_error_info

        status = "VERIFIED_FIX" if validated else ("AMBIGUOUS_NO_FIX" if candidate_code == original_code else "UNVERIFIED")

        refusal_explanation = None
        if not validated and candidate_code == original_code:
            error_type = error_info.get('error_type')
            if error_type == 'NameError':
                match = re.search(r"name '([^']+)' is not defined", error_info.get('message', ''))
                if match:
                    bad_name = match.group(1)
                    node_type = ast_context.get('node_type')
                    if node_type == 'For':
                        refusal_explanation = (
                            f"**WHAT HAPPENED?**\n'{bad_name}' is being used in the loop, but Python cannot find a definition for it.\n\n"
                            f"**WHY?**\nA variable must be defined before it is used.\n\n"
                            f"**HOW TO FIX IT?**\nDefine '{bad_name}' before the loop, or replace '{bad_name}' with the collection you intended to iterate over.\n\n"
                            f"**AUTOMATIC FIX?**\nI can't safely choose the correct value for '{bad_name}' from the available code."
                        )
                    else:
                        refusal_explanation = (
                            f"**WHAT HAPPENED?**\n'{bad_name}' is being used, but Python cannot find a definition for it.\n\n"
                            f"**WHY?**\nA variable must be defined before it is used.\n\n"
                            f"**HOW TO FIX IT?**\nDefine '{bad_name}' before using it.\n\n"
                            f"**AUTOMATIC FIX?**\nI can't safely choose the correct value for '{bad_name}' from the available code."
                        )

        return {
            "candidate_code": candidate_code,
            "validated": validated,
            "attempts": attempts,
            "status": status,
            "refusal_explanation": refusal_explanation
        }

    def _generate_candidate_code(self, code: str, error_info: Dict[str, Any], ast_context: Dict[str, Any], last_validation_error: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate a corrected version of the code.
        For Version 1.0, we use a basic heuristic approach to generate runnable code fixes.
        In later phases, an LLM will generate the code.
        """
        # If we failed validation on the first attempt, we use the new error info to try again
        current_error = last_validation_error if last_validation_error else error_info
        
        error_type = current_error.get('error_type')
        line_num = current_error.get('line_number')
        
        if not line_num:
            return code

        lines = code.split('\n')
        if not (1 <= line_num <= len(lines)):
            return code
            
        target_line_idx = line_num - 1
        original_line = lines[target_line_idx]
        modified_line = original_line

        # Version 1.0 heuristic logic to provide ACTUAL corrected code
        if error_type == 'NameError':
            message = current_error.get('message', '')
            match = re.search(r"name '([^']+)' is not defined", message)
            if match:
                bad_name = match.group(1)
                
                similar_names = ast_context.get('similar_names', [])
                builtins = ['print', 'len', 'range', 'str', 'int', 'float', 'list', 'dict', 'set', 'tuple', 'sum', 'min', 'max', 'abs', 'round', 'enumerate', 'zip', 'sorted', 'open']
                
                def levenshtein(s1, s2):
                    if len(s1) < len(s2): return levenshtein(s2, s1)
                    if len(s2) == 0: return len(s1)
                    prev_row = range(len(s2) + 1)
                    for i, c1 in enumerate(s1):
                        curr_row = [i + 1]
                        for j, c2 in enumerate(s2):
                            ins = prev_row[j + 1] + 1
                            delete = curr_row[j] + 1
                            sub = prev_row[j] + (c1 != c2)
                            curr_row.append(min(ins, delete, sub))
                        prev_row = curr_row
                    return prev_row[-1]
                
                candidates = similar_names.copy()
                for b in builtins:
                    if levenshtein(b, bad_name) <= 2 and b not in candidates:
                        candidates.append(b)
                
                if candidates:
                    best_guess = candidates[0]
                    # Replace whole word
                    modified_line = re.sub(r'\b' + re.escape(bad_name) + r'\b', best_guess, original_line)
                
        elif error_type == 'SyntaxError':
            message = current_error.get('message', '')
            stripped = original_line.strip()
            # Fix single '=' in if/while/elif conditions
            if re.search(r'\b(if|elif|while)\b.*(?<![!=<>])=(?![=])', original_line):
                modified_line = re.sub(r'(?<=\s)=(?=\s)', '==', original_line, count=1)
            # Fix missing colons
            elif stripped.startswith(('def ', 'if ', 'for ', 'while ', 'class ', 'elif ', 'else')):
                if not stripped.endswith(':'):
                    modified_line = original_line + ':'
            # Fix missing closing parenthesis (basic heuristic)
            elif "unexpected EOF" in message or "invalid syntax" in message:
                open_parens = modified_line.count('(')
                close_parens = modified_line.count(')')
                if open_parens > close_parens:
                    modified_line += ')' * (open_parens - close_parens)
            # Fix Python 2 style print statement
            elif re.match(r'^\s*print\s+["\']', original_line):
                indent = len(original_line) - len(original_line.lstrip())
                content = original_line.strip()[5:].strip()
                modified_line = (" " * indent) + f"print({content})"

        elif error_type == 'TypeError':
            message = current_error.get('message', '')
            if 'can only concatenate str' in message or 'unsupported operand type(s) for +' in message:
                match = re.search(r'\+\s*([a-zA-Z_]\w*|\d+)(?!\s*\()', original_line)
                if match:
                    val = match.group(1)
                    if val != 'str':
                        modified_line = original_line[:match.start()] + f"+ str({val})" + original_line[match.end():]

        elif error_type == 'ZeroDivisionError':
            # Replace literal / 0 with / 1 or safe division
            modified_line = re.sub(r'/\s*0(?:\.0*)?(?!\d)', '/ 1', original_line)

        elif error_type == 'KeyError':
            # Convert dict[key] access to dict.get(key)
            match = re.search(r'([a-zA-Z_]\w*)\[([^\]]+)\]', original_line)
            if match:
                d_name, k_name = match.group(1), match.group(2)
                modified_line = original_line.replace(f"{d_name}[{k_name}]", f"{d_name}.get({k_name})")

        elif error_type == 'IndexError':
            # Convert arr[len(arr)] to arr[len(arr) - 1]
            if re.search(r'\[\s*len\s*\([^)]+\)\s*\]', original_line):
                modified_line = re.sub(r'\[\s*len\s*\(([^)]+)\)\s*\]', r'[len(\1) - 1]', original_line)

        elif error_type == 'IndentationError':
            # Indent if inside block
            if target_line_idx > 0 and lines[target_line_idx - 1].rstrip().endswith(':'):
                prev_indent = len(lines[target_line_idx - 1]) - len(lines[target_line_idx - 1].lstrip())
                modified_line = (" " * (prev_indent + 4)) + original_line.lstrip()

        lines[target_line_idx] = modified_line
        return '\n'.join(lines)
