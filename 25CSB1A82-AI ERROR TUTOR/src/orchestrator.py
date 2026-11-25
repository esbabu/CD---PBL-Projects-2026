from .agents import (
    SecurityAgent, ExecutionSandbox, 
    DiagnosticAgent, FixerAgent, ExplainerAgent
)

class Orchestrator:
    def __init__(self, ai_model=None):
        self.security = SecurityAgent()
        self.sandbox = ExecutionSandbox()
        self.diagnostic = DiagnosticAgent()
        self.fixer = FixerAgent()
        self.explainer = ExplainerAgent(ai_model=ai_model)

    def run(self, code: str):
        # 1. Security Check
        is_safe, warnings = self.security.check(code)
        if not is_safe:
            return {
                "success": False,
                "error_type": "SecurityError",
                "friendly_explanation": "🚫 Code blocked for security reasons.",
                "suggested_fix": "Remove dangerous system calls.",
                "security_warnings": warnings
            }

        # 2. Execute Original Code
        success, error_info = self.sandbox.run(code)
        if success:
            return {
                "success": True,
                "friendly_explanation": "✓ Code ran successfully!",
                "security_warnings": warnings
            }

        # 3. Diagnose Error
        diagnosis = self.diagnostic.diagnose(error_info)

        # 4. The Self-Correction Loop (Max 3 attempts)
        current_code = code
        fixed_successfully = False
        max_attempts = 3

        for attempt in range(max_attempts):
            # Fix the code
            fixed_code = self.fixer.fix(current_code, diagnosis)
            
            # Test the fix in the sandbox
            test_success, test_error = self.sandbox.run(fixed_code)
            
            if test_success:
                fixed_successfully = True
                break
            else:
                # If fix failed, diagnose the NEW error and try again
                current_code = fixed_code
                diagnosis = self.diagnostic.diagnose(test_error)

        # 5. Explain the results
        explanation, suggested_fix = self.explainer.explain(
            diagnosis, 
            fixed_code if fixed_successfully else "Could not automatically fix.", 
            error_info
        )

        return {
            "success": False,
            "error_type": error_info.get("error_type"),
            "friendly_explanation": explanation,
            "suggested_fix": suggested_fix,
            "line_number": error_info.get("line_number"),
            "code_context": error_info.get("code_context"),
            "raw_error": error_info.get("message"),
            "similar_names": diagnosis["similar_names"],
            "security_warnings": warnings
        }
