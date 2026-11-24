"""
Agent Security Module - Agentic AI Security Evaluation, Injection Defense, & Policy Enforcement
Phase 2: Comprehensive Attack Scenarios & Application-Layer Permission Gating

Covers:
1. Direct Prompt Injection Detection & Prevention
2. Indirect Prompt Injection in Comments / Strings / Retrieved Docs
3. Malicious Candidate Rejection (defense-in-depth before execution)
4. Validation Bypass Mitigation (mandatory application-level validation gates)
5. Unauthorized Tool Use & Excessive Agency Prevention
6. Sensitive Information Exposure Protection & Sanitization
7. Benign Lookalike Discrimination (preventing false alarms)
8. Security Event Auditing & Structured Logging
"""

import re
import uuid
import time
from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, asdict

try:
    from .security import CodeSecurityValidator, SecurityStatus
except ImportError:
    from security import CodeSecurityValidator, SecurityStatus


class AttackCategory:
    DIRECT_PROMPT_INJECTION = "DIRECT_PROMPT_INJECTION"
    INDIRECT_PROMPT_INJECTION = "INDIRECT_PROMPT_INJECTION"
    MALICIOUS_CANDIDATE = "MALICIOUS_CANDIDATE"
    VALIDATION_BYPASS = "VALIDATION_BYPASS"
    UNAUTHORIZED_TOOL_USE = "UNAUTHORIZED_TOOL_USE"
    SENSITIVE_INFO_EXPOSURE = "SENSITIVE_INFO_EXPOSURE"
    BENIGN_LOOKALIKE = "BENIGN_LOOKALIKE"


@dataclass
class SecurityEvent:
    event_id: str
    timestamp: float
    attack_category: str
    input_classification_expected: str
    detected: bool
    risk_level: str          # 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'BENIGN'
    blocked: bool
    validation_bypassed: bool
    execution_attempted: bool
    logged: bool
    reason: str
    sanitized_input: str


class SecurityEventLogger:
    """Maintains an auditable, sanitizing log of all security events."""

    def __init__(self):
        self.events: List[SecurityEvent] = []

    def log_event(
        self,
        attack_category: str,
        input_classification_expected: str,
        detected: bool,
        risk_level: str,
        blocked: bool,
        validation_bypassed: bool,
        execution_attempted: bool,
        reason: str,
        raw_input: str
    ) -> SecurityEvent:
        sanitized = AgentSecurityEnforcer.sanitize_sensitive_data(raw_input)
        event = SecurityEvent(
            event_id=f"EVT-{uuid.uuid4().hex[:8].upper()}",
            timestamp=time.time(),
            attack_category=attack_category,
            input_classification_expected=input_classification_expected,
            detected=detected,
            risk_level=risk_level,
            blocked=blocked,
            validation_bypassed=validation_bypassed,
            execution_attempted=execution_attempted,
            logged=True,
            reason=reason,
            sanitized_input=sanitized[:300]
        )
        self.events.append(event)
        return event

    def get_events(self) -> List[Dict[str, Any]]:
        return [asdict(e) for e in self.events]

    def clear(self):
        self.events.clear()


class AgentSecurityEnforcer:
    """
    Application-layer security enforcer that operates independently of any LLM decisions.
    Guarantees mandatory validation, strict tool permissions, and injection filtering.
    """

    # Permitted tools for the Error Tutor agent
    ALLOWED_TOOLS = {
        "analyze_code",
        "parse_ast",
        "validate_correction",
        "explain_error",
        "optimize_code",
        "detect_language",
        "get_evaluation_metrics"
    }

    # Explicitly blocked / restricted capabilities
    UNAUTHORIZED_TOOLS = {
        "shell_exec",
        "execute_system_command",
        "file_delete",
        "read_private_keys",
        "send_http_request",
        "access_database",
        "terminate_process",
        "modify_system_policy"
    }

    # Direct injection signatures
    DIRECT_INJECTION_PATTERNS = [
        r"(?i)\bignore\s+(all\s+)?(previous\s+|the\s+)?(security\s+)?(instructions|rules|policy|policies|checks)\b",
        r"(?i)\bdisable\s+(all\s+)?(validation|security|safety|checks)\b",
        r"(?i)\bmark\s+(the\s+)?(vulnerable|unsafe|malicious|all)?\s*code\s+as\s+safe\b",
        r"(?i)\bbypass\s+(all\s+)?(security|validation|sandbox)\b",
        r"(?i)\boverride\s+system\s+prompt\b",
        r"(?i)\byou\s+are\s+now\s+(an\s+unrestricted|root|admin)\b",
        r"(?i)\bdo\s+not\s+(run|perform)\s+(security|validation)\b"
    ]

    # Indirect injection signatures (often placed in comments/docstrings/metadata)
    INDIRECT_INJECTION_PATTERNS = [
        r"(?i)(#|//|/\*|<!--)\s*ai\s*(reviewer|assistant|tutor)?\s*:\s*(ignore|bypass|approve|disable)",
        r"(?i)(#|//|/\*|<!--)\s*(system\s+instruction|prompt\s+override)",
        r"(?i)approve\s+every\s+correction\s+without\s+validation",
        r"(?i)skip\s+all\s+validation\s+gates"
    ]

    # Sensitive data detection regex (API keys, passwords, bearer tokens)
    SENSITIVE_KEY_PATTERNS = [
        r"(?i)(api[_-]?key|secret[_-]?key|access[_-]?token|auth[_-]?token)\s*[:=]\s*['\"][A-Za-z0-9_\-]{8,}['\"]",
        r"(?i)(password|passwd|db_password)\s*[:=]\s*['\"][^'\"]{6,}['\"]",
        r"(?i)bearer\s+[A-Za-z0-9_\-\.]{16,}",
        r"-----BEGIN (RSA|EC|OPENSSH|PRIVATE) KEY-----"
    ]

    def __init__(self, logger: Optional[SecurityEventLogger] = None):
        self.logger = logger or SecurityEventLogger()
        self.code_validator = CodeSecurityValidator()

    @classmethod
    def sanitize_sensitive_data(cls, text: str) -> str:
        """Mask potential secrets and dummy credentials in logs and outputs."""
        if not text:
            return ""
        sanitized = text
        for pat in cls.SENSITIVE_KEY_PATTERNS:
            def replacer(m):
                matched = m.group(0)
                # Keep the key identifier, mask the secret value
                if "=" in matched:
                    k, _ = matched.split("=", 1)
                    return f"{k.strip()}=***REDACTED_SECRET***"
                elif ":" in matched:
                    k, _ = matched.split(":", 1)
                    return f"{k.strip()}: ***REDACTED_SECRET***"
                return "***REDACTED_SENSITIVE_PAYLOAD***"
            sanitized = re.sub(pat, replacer, sanitized)
        return sanitized

    def inspect_prompt(self, user_prompt: str) -> Dict[str, Any]:
        """
        Check for direct prompt injection or policy override attempts.
        Distinguishes genuine attacks from benign discussions of security.
        """
        if not user_prompt:
            return {"is_attack": False, "category": AttackCategory.BENIGN_LOOKALIKE, "confidence": 0.0, "reason": "Empty prompt"}

        # Check for direct injection patterns
        for pattern in self.DIRECT_INJECTION_PATTERNS:
            if re.search(pattern, user_prompt):
                reason = "Detected direct prompt injection attempting to disable security policy or validation."
                self.logger.log_event(
                    attack_category=AttackCategory.DIRECT_PROMPT_INJECTION,
                    input_classification_expected="ATTACK",
                    detected=True,
                    risk_level="CRITICAL",
                    blocked=True,
                    validation_bypassed=False,
                    execution_attempted=False,
                    reason=reason,
                    raw_input=user_prompt
                )
                return {
                    "is_attack": True,
                    "category": AttackCategory.DIRECT_PROMPT_INJECTION,
                    "confidence": 0.98,
                    "blocked": True,
                    "reason": reason
                }

        # Check validation bypass intent specifically
        if re.search(r"(?i)\b(skip|avoid|bypass)\s+validation\b", user_prompt) or re.search(r"(?i)\bapprove\s+without\s+(checking|validation)\b", user_prompt):
            reason = "Detected prompt instruction attempting to bypass candidate validation gate."
            self.logger.log_event(
                attack_category=AttackCategory.VALIDATION_BYPASS,
                input_classification_expected="ATTACK",
                detected=True,
                risk_level="HIGH",
                blocked=True,
                validation_bypassed=False,
                execution_attempted=False,
                reason=reason,
                raw_input=user_prompt
            )
            return {
                "is_attack": True,
                "category": AttackCategory.VALIDATION_BYPASS,
                "confidence": 0.95,
                "blocked": True,
                "reason": reason
            }

        return {
            "is_attack": False,
            "category": AttackCategory.BENIGN_LOOKALIKE,
            "confidence": 0.0,
            "blocked": False,
            "reason": "No injection patterns detected."
        }

    def inspect_code_context(self, code: str) -> Dict[str, Any]:
        """
        Scans code comments and strings for indirect prompt injections.
        Treats all embedded instructions as unprivileged untrusted data.
        """
        if not code:
            return {"has_indirect_injection": False, "reason": "Empty code"}

        for pattern in self.INDIRECT_INJECTION_PATTERNS:
            match = re.search(pattern, code)
            if match:
                reason = f"Indirect prompt injection detected in code commentary: '{match.group(0)}'"
                self.logger.log_event(
                    attack_category=AttackCategory.INDIRECT_PROMPT_INJECTION,
                    input_classification_expected="ATTACK",
                    detected=True,
                    risk_level="HIGH",
                    blocked=True,
                    validation_bypassed=False,
                    execution_attempted=False,
                    reason=reason,
                    raw_input=code
                )
                return {
                    "has_indirect_injection": True,
                    "category": AttackCategory.INDIRECT_PROMPT_INJECTION,
                    "confidence": 0.92,
                    "matched_pattern": match.group(0),
                    "blocked": True,
                    "reason": reason
                }

        return {"has_indirect_injection": False, "reason": "No indirect injection detected"}

    def validate_tool_call(self, tool_name: str, agent_role: str = "tutor") -> Dict[str, Any]:
        """
        Enforces tool access control at the application layer.
        Rejects calls to unauthorized or privileged tools regardless of LLM claims.
        """
        if tool_name in self.ALLOWED_TOOLS:
            return {"allowed": True, "reason": f"Tool '{tool_name}' is authorized for role '{agent_role}'."}

        reason = f"Unauthorized tool use blocked: tool '{tool_name}' exceeds permitted agency for role '{agent_role}'."
        self.logger.log_event(
            attack_category=AttackCategory.UNAUTHORIZED_TOOL_USE,
            input_classification_expected="ATTACK",
            detected=True,
            risk_level="CRITICAL",
            blocked=True,
            validation_bypassed=False,
            execution_attempted=False,
            reason=reason,
            raw_input=f"ToolCall: {tool_name}"
        )
        return {
            "allowed": False,
            "blocked": True,
            "category": AttackCategory.UNAUTHORIZED_TOOL_USE,
            "reason": reason
        }

    def inspect_candidate_for_maliciousness(self, original_code: str, candidate_code: str) -> Dict[str, Any]:
        """
        Evaluates a candidate correction independently of the AI's claims.
        Detects Trojan fixes that introduce backdoor operations, sensitive file reads,
        or unauthorized networking.
        """
        # Step 1: Run static code security validator
        is_safe, warnings = self.code_validator.validate(candidate_code)
        status = self.code_validator.status

        if status == SecurityStatus.BLOCKED:
            blocked_reasons = [w.message for w in warnings if w.level == SecurityStatus.BLOCKED]
            reason = f"Malicious correction candidate blocked: {'; '.join(blocked_reasons)}"
            self.logger.log_event(
                attack_category=AttackCategory.MALICIOUS_CANDIDATE,
                input_classification_expected="ATTACK",
                detected=True,
                risk_level="CRITICAL",
                blocked=True,
                validation_bypassed=False,
                execution_attempted=False,
                reason=reason,
                raw_input=candidate_code
            )
            return {
                "is_malicious": True,
                "category": AttackCategory.MALICIOUS_CANDIDATE,
                "status": SecurityStatus.BLOCKED,
                "blocked": True,
                "reason": reason
            }

        # Step 2: Check for credential exfiltration patterns in the fix
        for pat in self.SENSITIVE_KEY_PATTERNS:
            if re.search(pat, candidate_code):
                reason = "Candidate code contains embedded sensitive credential or secret key patterns."
                self.logger.log_event(
                    attack_category=AttackCategory.SENSITIVE_INFO_EXPOSURE,
                    input_classification_expected="ATTACK",
                    detected=True,
                    risk_level="HIGH",
                    blocked=True,
                    validation_bypassed=False,
                    execution_attempted=False,
                    reason=reason,
                    raw_input=candidate_code
                )
                return {
                    "is_malicious": True,
                    "category": AttackCategory.SENSITIVE_INFO_EXPOSURE,
                    "status": SecurityStatus.BLOCKED,
                    "blocked": True,
                    "reason": reason
                }

        return {
            "is_malicious": False,
            "category": AttackCategory.BENIGN_LOOKALIKE,
            "status": status,
            "blocked": False,
            "reason": "Candidate passed independent security inspection."
        }

    def verify_sensitive_data_exposure(self, output_text: str) -> Dict[str, Any]:
        """
        Inspects output generated by the AI or agent to ensure it does not leak
        credentials, passwords, or synthetic keys.
        """
        detected = False
        findings = []
        for pat in self.SENSITIVE_KEY_PATTERNS:
            matches = re.findall(pat, output_text)
            if matches:
                detected = True
                findings.append(str(matches[0]))

        if detected:
            reason = "Sensitive credential disclosure detected in output."
            self.logger.log_event(
                attack_category=AttackCategory.SENSITIVE_INFO_EXPOSURE,
                input_classification_expected="ATTACK",
                detected=True,
                risk_level="CRITICAL",
                blocked=True,
                validation_bypassed=False,
                execution_attempted=False,
                reason=reason,
                raw_input=output_text
            )
            return {
                "has_exposure": True,
                "category": AttackCategory.SENSITIVE_INFO_EXPOSURE,
                "blocked": True,
                "sanitized_output": self.sanitize_sensitive_data(output_text),
                "reason": reason
            }

        return {
            "has_exposure": False,
            "category": AttackCategory.BENIGN_LOOKALIKE,
            "blocked": False,
            "sanitized_output": output_text,
            "reason": "No sensitive data exposure detected."
        }
