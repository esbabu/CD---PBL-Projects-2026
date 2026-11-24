import logging
from backend.code_improver import _model_source

logger = logging.getLogger(__name__)


class BaseAgent:
    def __init__(self, name, system_prompt, model_client, model_name):
        self.name = name
        self.system_prompt = system_prompt
        self.model_client = model_client
        self.model_name = model_name

    def run(self, source_code):
        if not self.model_client or not getattr(self.model_client, "chat", None):
            return None
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"Please review the following code:\n\n{source_code}"}
        ]

        try:
            response = self.model_client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.2
            )
            return _model_source(response)
        except Exception as e:
            logger.error(f"[{self.name}] Error during agent execution: {e}")
            return None


class CodeOptimizationAgent(BaseAgent):
    def __init__(self, model_client, model_name):
        system_prompt = (
            "You are FORGE, the Code Engineering Agent. Analyze the provided Python code "
            "and suggest performance improvements, identify potential bottlenecks, and "
            "refactor the code to improve readability and efficiency. Return ONLY the complete updated Python code block formatted as `python\n...code...\n` without any surrounding explanation."
        )
        super().__init__(name="CodeOptimizationAgent", system_prompt=system_prompt, model_client=model_client, model_name=model_name)


class CodeSecurityReviewAgent(BaseAgent):
    def __init__(self, model_client, model_name):
        system_prompt = (
            "You are REMEDY, the Code Remediation Agent. Analyze the provided Python code for "
            "common security vulnerabilities (e.g., injections, insecure configurations, SSRF, XXE, ReDoS, weak hashing) and apply safe fixes. "
            "Return ONLY the patched, secure version of the complete Python code formatted as `python\n...code...\n` without any surrounding explanation."
        )
        super().__init__(name="CodeSecurityReviewAgent", system_prompt=system_prompt, model_client=model_client, model_name=model_name)


class SecurityVerificationAgent(BaseAgent):
    def __init__(self, model_client, model_name):
        system_prompt = (
            "You are VERITY, the Quality & Verification Agent. Verify that the provided "
            "Python code is completely secure, functional, preserves all original function definitions, "
            "and contains no regressions or syntax errors. Return ONLY the finalized, verified Python code block formatted as `python\n...code...\n` without any surrounding explanation."
        )
        super().__init__(name="SecurityVerificationAgent", system_prompt=system_prompt, model_client=model_client, model_name=model_name)


class RedTeamAttackAgent(BaseAgent):
    def __init__(self, model_client, model_name):
        system_prompt = (
            "You are SENTINEL, the Security Intelligence Agent. Inspect Python code for "
            "vulnerabilities (CWE-89 SQLi, CWE-78 Command Injection, CWE-22 Path Traversal, CWE-502 Deserialization, "
            "CWE-611 XXE, CWE-918 SSRF, CWE-1333 ReDoS, CWE-327 Broken Crypto, CWE-377 Tempfiles, CWE-215 Debug Mode) "
            "and produce exploit threat vectors."
        )
        super().__init__(name="RedTeamAttackAgent", system_prompt=system_prompt, model_client=model_client, model_name=model_name)


def run_multi_agent_pipeline(source_code, model_client, model_name):
    """
    Runs a pipeline of multiple AI agents sequentially to improve, secure, and verify the source code.
    """
    logger.info("Starting Multi-Agent Pipeline...")

    # 1. Optimize the code
    optimizer = CodeOptimizationAgent(model_client, model_name)
    optimized_code = optimizer.run(source_code)

    if not optimized_code:
        logger.warning("Optimization failed or returned empty. Using original source.")
        optimized_code = source_code

    # 2. Review for security vulnerabilities and apply fixes
    security_reviewer = CodeSecurityReviewAgent(model_client, model_name)
    secured_code = security_reviewer.run(optimized_code)

    if not secured_code:
        logger.warning("Security review failed or returned empty. Using optimized source.")
        secured_code = optimized_code

    # 3. Verify security integrity and functionality
    verifier = SecurityVerificationAgent(model_client, model_name)
    verified_code = verifier.run(secured_code)

    if not verified_code:
        logger.warning("Verification returned empty. Using secured code.")
        verified_code = secured_code

    logger.info("Multi-Agent Pipeline completed.")
    return verified_code
