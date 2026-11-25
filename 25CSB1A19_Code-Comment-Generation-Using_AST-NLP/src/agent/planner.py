class SecurityPlanner:
    """Local planning component for the security agent."""

    def create_plan(self, ast_result, source_code, language="python"):
        plan = [f"Inspect {language} source structure", "Run configured security checks", "Run malware-behaviour indicator correlation"]
        if ast_result.get("functions") or ast_result.get("loops", 0) or ast_result.get("conditionals", 0):
            plan.append("Run available code-quality checks")
        keywords = ["eval(", "exec(", "subprocess", "pickle", "yaml.load", "password",
                    "api_key", "token", "execute(", "shell=true", "base64", "powershell"]
        if any(k.lower() in source_code.lower() for k in keywords):
            plan.append("Prioritize security and malware indicators")
        plan.append("Build evidence-based report and recommendations")
        return plan
