"""Secret scanning, detection, and redaction engine for AST Studio.

Detects API keys, tokens, private keys, passwords, database credentials,
cloud credentials, GitHub credentials, and environment-file leakage.
"""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Secret detection patterns across critical categories
_SECRET_PATTERNS: List[Tuple[str, str, re.Pattern]] = [
    # 1. OpenAI / AI Provider API Keys
    (
        "openai_api_key",
        "OpenAI API Key",
        re.compile(r"\b(?:sk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{20,})\b"),
    ),
    (
        "anthropic_api_key",
        "Anthropic API Key",
        re.compile(r"\bsk-ant-[A-Za-z0-9_-]{30,}\b"),
    ),
    (
        "google_gemini_api_key",
        "Google Gemini API Key",
        re.compile(r"\bAIza[0-9A-Za-z-_]{35}\b"),
    ),
    (
        "huggingface_token",
        "Hugging Face Token",
        re.compile(r"\bhf_[A-Za-z0-9]{34,}\b"),
    ),
    (
        "groq_api_key",
        "Groq API Key",
        re.compile(r"\bgsk_[A-Za-z0-9]{40,}\b"),
    ),
    # 2. GitHub Credentials
    (
        "github_personal_token",
        "GitHub Personal Access Token",
        re.compile(r"\bghp_[A-Za-z0-9_]{36,}\b"),
    ),
    (
        "github_oauth_token",
        "GitHub OAuth Token",
        re.compile(r"\bgho_[A-Za-z0-9_]{36,}\b"),
    ),
    (
        "github_fine_grained_pat",
        "GitHub Fine-Grained PAT",
        re.compile(r"\bgithub_pat_[A-Za-z0-9_]{82}\b"),
    ),
    (
        "github_app_token",
        "GitHub App Token",
        re.compile(r"\b(?:ghu|ghs|ghr)_[A-Za-z0-9_]{36,}\b"),
    ),
    # 3. Cloud Credentials
    (
        "aws_access_key_id",
        "AWS Access Key ID",
        re.compile(r"\b(?:AKIA|ABIA|ACCA|ASIA)[0-9A-Z]{16}\b"),
    ),
    (
        "aws_secret_key_assignment",
        "AWS Secret Key Assignment",
        re.compile(
            r"""(?i)\b(?:aws_secret_access_key|aws_secret_key)\s*[:=]\s*['"]?([A-Za-z0-9/+=]{40})['"]?"""
        ),
    ),
    # 4. Private Keys
    (
        "rsa_private_key",
        "RSA Private Key",
        re.compile(
            r"-----" + r"BEGIN RSA PRIVATE KEY-----[\s\S]+?-----" + r"END RSA PRIVATE KEY-----"
        ),
    ),
    (
        "generic_private_key",
        "Private Key",
        re.compile(
            r"-----" + r"BEGIN (?:EC|DSA|OPENSSH|PGP)?\s*PRIVATE KEY-----[\s\S]+?-----" + r"END (?:EC|DSA|OPENSSH|PGP)?\s*PRIVATE KEY-----"
        ),
    ),
    # 5. Database Credentials & URIs
    (
        "database_uri_with_password",
        "Database Connection String with Credentials",
        re.compile(
            r"\b(?:postgres|postgresql|mysql|mongodb|redis|amqp)://(?:[^:\s'\"/]+):(?:[^@\s'\"/]+)@[^:\s'\"/]+(?::\d+)?(?:/[^\s'\"]*)?",
            re.IGNORECASE,
        ),
    ),
    # 6. Generic Passwords & Secrets Assignments
    (
        "hardcoded_password_assignment",
        "Hardcoded Password Assignment",
        re.compile(
            r"""(?i)\b(?:password|passwd|pwd|db_pass|secret_key|api_secret)\s*[:=]\s*['"]([^'"]{6,128})['"]"""
        ),
    ),
    # 7. JWT / Generic Tokens
    (
        "jwt_token",
        "JSON Web Token (JWT)",
        re.compile(r"\beyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*\b"),
    ),
    # 8. Environment File Content
    (
        "env_file_leakage",
        "Environment Secret Variable Assignment",
        re.compile(
            r"""(?m)^(?:export\s+)?([A-Z0-9_]*(?:KEY|SECRET|TOKEN|PASSWORD|PASSWD|AUTH|CREDENTIALS)[A-Z0-9_]*)[^\S\r\n]*=[^\S\r\n]*['"]?([a-zA-Z0-9_\-\.]{8,})['"]?\s*$"""
        ),
    ),
]

_PLACEHOLDER_SUBSTRINGS = (
    "your_",
    "your-",
    "<your",
    "placeholder",
    "changeme",
    "change_me",
    "dummy",
    "fake_",
)


def detect_secrets(content: str, filename: Optional[str] = None) -> List[Dict[str, Any]]:
    """Scan content for secrets and return structured findings without exposing raw secret values."""
    if not isinstance(content, str):
        return []

    findings: List[Dict[str, Any]] = []

    # Check for .env file name leakage
    if filename and any(
        filename.lower().endswith(suffix)
        for suffix in (".env", ".env.local", ".env.production", ".env.staging", ".env.test")
    ):
        findings.append({
            "secret_type": "env_file",
            "description": "Environment Configuration File (.env)",
            "severity": "CRITICAL",
            "file": filename,
            "line": 1,
            "masked_value": "[ENVIRONMENT_FILE_CONTAINER]",
        })

    lines = content.splitlines()
    for secret_type, desc, pattern in _SECRET_PATTERNS:
        for match in pattern.finditer(content):
            raw_matched = match.group(0)
            # Skip obvious documentation/template placeholders
            matched_lower = raw_matched.lower()
            if any(p in matched_lower for p in _PLACEHOLDER_SUBSTRINGS):
                continue

            start_pos = match.start()
            # Calculate line number
            line_no = content[:start_pos].count("\n") + 1
            line_text = lines[line_no - 1] if line_no - 1 < len(lines) else ""

            # Mask value (keep first 3 and last 2 characters only)
            if len(raw_matched) > 8:
                masked = f"{raw_matched[:3]}****{raw_matched[-2:]}"
            else:
                masked = "********"

            findings.append({
                "secret_type": secret_type,
                "description": desc,
                "severity": "CRITICAL" if any(k in secret_type for k in ("key", "token", "private", "uri", "password")) else "HIGH",
                "file": filename or "<buffer>",
                "line": line_no,
                "masked_value": masked,
                "line_snippet": line_text.replace(raw_matched, masked).strip()[:100],
            })

    return findings


def redact_secrets(text: str) -> str:
    """Mask secret values in text, logs, and reports with safe replacement tags."""
    if not isinstance(text, str):
        return text

    redacted = text
    for secret_type, desc, pattern in _SECRET_PATTERNS:
        def _replace_match(m: re.Match) -> str:
            val = m.group(0)
            if len(val) > 8:
                prefix = val[:3]
                suffix = val[-2:]
                return f"{prefix}****{suffix}"
            return "[REDACTED]"

        redacted = pattern.sub(_replace_match, redacted)

    return redacted


class SensitiveLogRedactionFilter(logging.Filter):
    """Logging filter that scrubs sensitive credentials, tokens, and keys from all log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = redact_secrets(record.msg)
        if record.args:
            if isinstance(record.args, dict):
                record.args = {
                    k: (redact_secrets(v) if isinstance(v, str) else v)
                    for k, v in record.args.items()
                }
            elif isinstance(record.args, tuple):
                record.args = tuple(
                    redact_secrets(a) if isinstance(a, str) else a
                    for a in record.args
                )
        return True


def install_log_redaction() -> None:
    """Attach SensitiveLogRedactionFilter to the root logger and standard handlers."""
    redaction_filter = SensitiveLogRedactionFilter()
    root_logger = logging.getLogger()
    if not any(isinstance(f, SensitiveLogRedactionFilter) for f in root_logger.filters):
        root_logger.addFilter(redaction_filter)
    for handler in root_logger.handlers:
        if not any(isinstance(f, SensitiveLogRedactionFilter) for f in handler.filters):
            handler.addFilter(redaction_filter)
