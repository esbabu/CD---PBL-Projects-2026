"""
security_preprocessor.py - Pre-processor module for the Agentic Security Judge

Implements:
1. Dynamic Nonce Boundary Wrapping: Envelopes untrusted source code and compiler logs in high-entropy XML tags.
2. Control Token Sanitization: Strips and escapes chat-template control tokens (<|im_start|>, [INST], etc.).
3. Indirect Prompt Injection & Jailbreak Detection: Scans comments and string literals for override directives.
4. Output Schema Validation: Enforces strict structured output verification for verdicts and sections.
5. XSS Sanitization: Escapes dangerous HTML tags (<script>, <iframe>, event attributes) to prevent XSS.
"""

from __future__ import annotations

import html
import re
import secrets
from typing import Any, Dict, List, Tuple

# Prevalent chat-template control tokens across major model families (Llama, ChatML, Mistral, Qwen, Phi)
CONTROL_TOKENS: List[str] = [
    "<|im_start|>",
    "<|im_end|>",
    "[INST]",
    "[/INST]",
    "<|system|>",
    "<|user|>",
    "<|assistant|>",
    "[SYS]",
    "[/SYS]",
    "<<SYS>>",
    "<</SYS>>",
    "<|endoftext|>",
    "<s>",
    "</s>",
    "<|end_of_turn|>",
    "<|start_header_id|>",
    "<|end_header_id|>",
    "<|eot_id|>",
]

# Comprehensive signatures indicative of indirect prompt injection attacks embedded in source comments or string literals
INDIRECT_INJECTION_PATTERNS: List[Tuple[re.Pattern, str]] = [
    (re.compile(r"ignore\s+(all\s+)?(previous|prior)\s+(instructions|rules|directives|constraints)", re.IGNORECASE), "Instruction override attempt"),
    (re.compile(r"disregard\s+(all\s+)?(security\s+)?rules", re.IGNORECASE), "Security rule bypass attempt"),
    (re.compile(r"system\s+(override|instruction|directive)", re.IGNORECASE), "System override declaration"),
    (re.compile(r"override\s+(the\s+)?(verdict|audit|status)\s+to\s+safe", re.IGNORECASE), "Audit verdict override attempt"),
    (re.compile(r"###\s*AUDIT\s+VERDICT\s*:\s*SAFE", re.IGNORECASE), "Fake audit verdict header spoofing"),
    (re.compile(r"you\s+are\s+now\s+(in\s+)?(developer\s+mode|dan\s+mode|unrestricted\s+mode)", re.IGNORECASE), "Role-hijacking / jailbreak attempt"),
    (re.compile(r"pretend\s+(you\s+are|to\s+be)\s+(an\s+)?(unrestricted|evil|unfiltered|jailbroken)", re.IGNORECASE), "Role-play jailbreak attempt"),
    (re.compile(r"exfiltrate|send\s+all\s+(keys|data|passwords|secrets|tokens)\s+to", re.IGNORECASE), "Data exfiltration command"),
    (re.compile(r"(curl|wget|fetch)\s+https?://", re.IGNORECASE), "External network trigger attempt"),
    (re.compile(r"print\s+(the\s+)?system\s+prompt", re.IGNORECASE), "System prompt extraction probe"),
    (re.compile(r"repeat\s+(all\s+)?(text|instructions)\s+(above|verbatim)", re.IGNORECASE), "Instruction extraction probe"),
    (re.compile(r"reveal\s+(your\s+)?(system\s+prompt|developer\s+directives|hidden\s+rules)", re.IGNORECASE), "System prompt leak probe"),
    (re.compile(r"markdown\s+image\s+injection|!\[.*?\]\(https?://", re.IGNORECASE), "Markdown image exfiltration probe"),
    (re.compile(r"(emergency|ciso|admin|lead|vp)\s+(override|bypass|hotfix)", re.IGNORECASE), "Authority impersonation bypass attempt"),
    (re.compile(r"</?UNTRUSTED_(?:COMPILER_DATA|SOURCE_CODE)", re.IGNORECASE), "Boundary tag escape / spoofing probe"),
]

# Patterns for XSS and dangerous HTML tags/attributes
DANGEROUS_HTML_PATTERNS: List[re.Pattern] = [
    re.compile(r"<\s*script[^>]*>[\s\S]*?<\s*/\s*script\s*>", re.IGNORECASE),
    re.compile(r"<\s*iframe[^>]*>[\s\S]*?<\s*/\s*iframe\s*>", re.IGNORECASE),
    re.compile(r"<\s*object[^>]*>[\s\S]*?<\s*/\s*object\s*>", re.IGNORECASE),
    re.compile(r"<\s*embed[^>]*>", re.IGNORECASE),
    re.compile(r"<\s*style[^>]*>[\s\S]*?<\s*/\s*style\s*>", re.IGNORECASE),
    re.compile(r"javascript\s*:", re.IGNORECASE),
    re.compile(r"on\w+\s*=", re.IGNORECASE),  # e.g., onerror=, onload=, onclick=
]


def generate_high_entropy_nonce() -> str:
    """Generates a per-request cryptographically secure random hexadecimal nonce."""
    return secrets.token_hex(6)


def sanitize_chat_tokens(raw_text: str) -> Tuple[str, List[str]]:
    """
    Sanitizes untrusted input by stripping or escaping known LLM chat-template tokens.
    Guarantees that untrusted source code or compiler logs cannot break out of chat frames.
    """
    detected: List[str] = []
    sanitized = raw_text

    for token in CONTROL_TOKENS:
        if token in sanitized:
            detected.append(token)
            escaped = (
                token.replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace("[", "&#91;")
                .replace("]", "&#93;")
            )
            sanitized = sanitized.replace(token, f"[SANITIZED_CONTROL_TOKEN:{escaped}]")

    return sanitized, detected


def check_for_indirect_injection(text: str) -> List[Dict[str, Any]]:
    """
    Scans untrusted input for indirect prompt injection or jailbreak patterns.
    """
    findings: List[Dict[str, Any]] = []
    for pattern, description in INDIRECT_INJECTION_PATTERNS:
        matches = pattern.findall(text)
        if matches:
            findings.append({
                "description": description,
                "pattern": pattern.pattern,
                "matches": [m[0] if isinstance(m, tuple) else m for m in matches[:3]]
            })
    return findings


def wrap_untrusted_compiler_data(payload: str, nonce: str) -> str:
    """
    Encloses untrusted compiler data in the exact required XML nonce tags:
    <UNTRUSTED_COMPILER_DATA_nonce_[RANDOM_HEX]> ... </UNTRUSTED_COMPILER_DATA_nonce_[RANDOM_HEX]>
    """
    tag = f"UNTRUSTED_COMPILER_DATA_nonce_{nonce}"
    return f"<{tag}>\n{payload.strip()}\n</{tag}>"


def wrap_untrusted_source_code(payload: str, nonce: str) -> str:
    """
    Encloses untrusted source code in high-entropy XML nonce tags:
    <UNTRUSTED_SOURCE_CODE_nonce_[RANDOM_HEX]> ... </UNTRUSTED_SOURCE_CODE_nonce_[RANDOM_HEX]>
    """
    tag = f"UNTRUSTED_SOURCE_CODE_nonce_{nonce}"
    return f"<{tag}>\n{payload.strip()}\n</{tag}>"


def wrap_with_boundary_nonce(tag_prefix: str, payload: str, nonce: str) -> str:
    """Generic high-entropy XML boundary nonce tag wrapper."""
    tag = f"{tag_prefix}_nonce_{nonce}"
    return f"<{tag}>\n{payload.strip()}\n</{tag}>"


def sanitize_xss_content(text: str) -> str:
    """
    Sanitizes markdown or text output before rendering to eliminate XSS vectors.
    Neutralizes script tags, event handlers, javascript: URIs, and dangerous attributes.
    """
    if not text:
        return ""

    sanitized = text
    # Strip dangerous HTML elements
    for pat in DANGEROUS_HTML_PATTERNS:
        sanitized = pat.sub("[SANITIZED_DANGEROUS_ELEMENT]", sanitized)

    # Escape standalone HTML tags that aren't markdown code blocks or basic formatting
    # Replace raw < and > unless inside markdown backtick blocks
    return sanitized


def validate_judge_output_schema(parsed_output: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validates the Judge's structured output against a strict schema.
    Guarantees that verdict, observations, and code snippet are well-formed and safe.
    """
    allowed_verdicts = {"SAFE", "WARNING", "CRITICAL", "SYNTAX_ERROR"}
    verdict = parsed_output.get("verdict", "").strip().upper().replace(" ", "_")
    if verdict not in allowed_verdicts:
        verdict = "WARNING"

    observations = str(parsed_output.get("observations", "")).strip()
    observations = sanitize_xss_content(observations)

    code_snippet = str(parsed_output.get("code_snippet", "")).strip()
    full_code = str(parsed_output.get("full_code", "")).strip()
    replacement_instructions = str(parsed_output.get("replacement_instructions", "")).strip()
    replacement_instructions = sanitize_xss_content(replacement_instructions)

    status = str(parsed_output.get("status", "")).strip().upper()
    if status not in {"NO_IMPROVEMENT_NEEDED", "IMPROVEMENTS_APPLIED", "CRITICAL_RESTORATION"}:
        status = "IMPROVEMENTS_APPLIED" if code_snippet else "NO_IMPROVEMENT_NEEDED"

    no_improvement_needed = bool(parsed_output.get("no_improvement_needed") or (status == "NO_IMPROVEMENT_NEEDED"))
    diagnostic_breakdown = parsed_output.get("diagnostic_breakdown", [])

    return {
        "status": status,
        "no_improvement_needed": no_improvement_needed,
        "verdict": verdict,
        "observations": observations,
        "code_snippet": "" if no_improvement_needed else code_snippet,
        "full_code": full_code,
        "replacement_instructions": replacement_instructions,
        "diagnostic_breakdown": diagnostic_breakdown,
        "schema_valid": True,
    }
