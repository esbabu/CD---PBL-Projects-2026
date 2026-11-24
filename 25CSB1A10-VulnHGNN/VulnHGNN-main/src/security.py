import os
"""
security.py — Security & Robustness layer for VulnHGNN pipeline.

Provides:
  1. Input Validation   : Ensures LLVM IR is well-formed, rejects adversarial inputs
  2. Prediction Filtering: Discards low-confidence predictions
  3. Model Stability     : Verifies model health (dropout, NaN weights, gradient norms)
"""

import re
import logging
import torch
import numpy as np

logger = logging.getLogger("security")

# ════════════════════════════════════════════════════════════════════════
# 1. INPUT VALIDATION
# ════════════════════════════════════════════════════════════════════════

# Maximum IR file size (10 MB) — prevents memory exhaustion
MAX_IR_SIZE_BYTES = 10 * 1024 * 1024

# Source code is compiled and analyzed locally; keep request work bounded.
MAX_SOURCE_SIZE_BYTES = 1 * 1024 * 1024

# Maximum number of functions in a single IR file
MAX_FUNCTIONS = 500

# Maximum number of instructions per function
MAX_INSTRUCTIONS_PER_FUNC = 10_000

# Minimum valid IR must contain at least a define or declare
_DEFINE_RE  = re.compile(r'^\s*define\s+', re.MULTILINE)
_DECLARE_RE = re.compile(r'^\s*declare\s+', re.MULTILINE)

# Patterns that suggest adversarial or malformed input
_SUSPICIOUS_PATTERNS = [
    re.compile(r'inline\s+asm', re.IGNORECASE),          # inline assembly
    re.compile(r'__asm__', re.IGNORECASE),                 # GCC-style asm
    re.compile(r'module\s+asm', re.IGNORECASE),            # module-level asm
]


def validate_source_input(source: str) -> tuple:
    """Validate source text before it is written to disk or compiled."""
    if not isinstance(source, str) or not source.strip():
        return False, "Source code is empty or not a string."
    if "\x00" in source:
        return False, "Source code contains a null byte."

    size = len(source.encode("utf-8", errors="replace"))
    if size > MAX_SOURCE_SIZE_BYTES:
        return False, f"Source code exceeds the {MAX_SOURCE_SIZE_BYTES}-byte limit."

    return True, "Source code is valid."


def validate_ir_input(ll_content: str) -> tuple:
    """
    Validate that LLVM IR content is well-formed and safe to process.

    Returns:
        (is_valid: bool, message: str)
    """
    if not ll_content or not isinstance(ll_content, str):
        return False, "IR content is empty or not a string."

    # Size check
    size = len(ll_content.encode("utf-8", errors="replace"))
    if size > MAX_IR_SIZE_BYTES:
        return False, f"IR too large: {size} bytes (max {MAX_IR_SIZE_BYTES})."

    # Must contain at least one define or declare
    has_define  = bool(_DEFINE_RE.search(ll_content))
    has_declare = bool(_DECLARE_RE.search(ll_content))
    if not has_define and not has_declare:
        return False, "IR contains no 'define' or 'declare' — not valid LLVM IR."

    # Check for suspicious patterns
    for pattern in _SUSPICIOUS_PATTERNS:
        if pattern.search(ll_content):
            return False, f"IR contains suspicious pattern: {pattern.pattern}"

    # Count functions — reject if too many (likely adversarial)
    n_defines = len(_DEFINE_RE.findall(ll_content))
    if n_defines > MAX_FUNCTIONS:
        return False, f"Too many functions: {n_defines} (max {MAX_FUNCTIONS})."

    # Basic structure: should have balanced braces for each define
    open_braces  = ll_content.count("{")
    close_braces = ll_content.count("}")
    if open_braces != close_braces:
        return False, f"Unbalanced braces: {open_braces} open vs {close_braces} close."

    return True, "IR input is valid."


def validate_ir_json(ir_data: dict) -> tuple:
    """
    Validate parsed IR JSON structure.

    Returns:
        (is_valid: bool, message: str)
    """
    if not isinstance(ir_data, dict):
        return False, "IR data is not a dict."

    functions = ir_data.get("functions", [])
    if not isinstance(functions, list):
        return False, "'functions' key missing or not a list."

    if len(functions) == 0:
        return False, "No functions found in IR data."

    if len(functions) > MAX_FUNCTIONS:
        return False, f"Too many functions: {len(functions)} (max {MAX_FUNCTIONS})."

    for func in functions:
        if not isinstance(func, dict):
            return False, "Function entry is not a dict."
        if "name" not in func:
            return False, "Function missing 'name' key."

        # Check instruction count for non-declarations
        if not func.get("is_declaration", False):
            total_insts = 0
            for block in func.get("blocks", []):
                total_insts += len(block.get("instructions", []))
            if total_insts > MAX_INSTRUCTIONS_PER_FUNC:
                return False, (
                    f"Function '{func['name']}' has {total_insts} instructions "
                    f"(max {MAX_INSTRUCTIONS_PER_FUNC})."
                )

    return True, "IR JSON is valid."


# ════════════════════════════════════════════════════════════════════════
# 2. PREDICTION FILTERING
# ════════════════════════════════════════════════════════════════════════

DEFAULT_CONFIDENCE_THRESHOLD = 0.6

_SEVERITY_RISK_WEIGHTS = {
    "CRITICAL": 80,
    "HIGH": 60,
    "MEDIUM": 35,
    "LOW": 20,
}


def calculate_security_estimate(predictions: list) -> dict:
    """Estimate risk from detected, supported CWE predictions."""
    findings = [
        prediction for prediction in predictions
        if prediction.get("detected")
        and prediction.get("class") != "non-vulnerable"
    ]

    risk_points = 0.0
    for finding in findings:
        try:
            probability = float(finding.get("probability", 0.0))
        except (TypeError, ValueError):
            continue
        if not np.isfinite(probability):
            continue
        probability = max(0.0, min(1.0, probability))
        severity = str(finding.get("severity", "MEDIUM")).upper()
        risk_points += _SEVERITY_RISK_WEIGHTS.get(severity, 35) * probability

    score = max(0, min(100, round(100 - risk_points)))
    if not findings:
        risk_level = "No supported issues detected"
    elif score >= 80:
        risk_level = "Lower detected risk"
    elif score >= 50:
        risk_level = "Moderate detected risk"
    else:
        risk_level = "Higher detected risk"

    return {
        "score": score,
        "risk_level": risk_level,
        "findings_considered": len(findings),
        "scope": "Heuristic based on detected supported CWEs; not a security guarantee.",
    }


def filter_low_confidence(
    predictions: list,
    threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
) -> list:
    """
    Remove predictions below the confidence threshold.
    
    'non-vulnerable' class is never filtered — it's always included.
    
    Args:
        predictions: List of prediction dicts with 'class', 'probability', 'detected' keys.
        threshold:   Minimum probability to keep a CWE prediction.
    
    Returns:
        Filtered prediction list.
    """
    filtered = []
    removed  = []

    for pred in predictions:
        cwe = pred.get("class", "")

        # Always keep non-vulnerable class
        if cwe == "non-vulnerable":
            filtered.append(pred)
            continue

        prob = pred.get("probability", 0.0)

        if prob >= threshold:
            filtered.append(pred)
        else:
            # Mark as not detected but keep in list for transparency
            removed.append(cwe)
            filtered.append({
                **pred,
                "detected": False,
                "filtered_reason": f"Below confidence threshold ({prob:.2%} < {threshold:.2%})",
            })

    if removed:
        logger.info(
            "Filtered %d low-confidence prediction(s): %s (threshold=%.2f)",
            len(removed), ", ".join(removed), threshold,
        )

    return filtered


# ════════════════════════════════════════════════════════════════════════
# 3. MODEL STABILITY CHECKS
# ════════════════════════════════════════════════════════════════════════

def check_model_stability(model: torch.nn.Module) -> dict:
    """
    Verify model health and stability.

    Checks:
      - Has dropout layers (prevents overfitting)
      - No NaN or Inf weights
      - Weight statistics (mean, std, min, max)
    
    Returns:
        dict with 'healthy' bool and diagnostic details.
    """
    report = {
        "healthy": True,
        "has_dropout": False,
        "nan_params": [],
        "inf_params": [],
        "weight_stats": {},
        "total_parameters": 0,
        "trainable_parameters": 0,
    }

    # Count parameters
    total_params = 0
    trainable_params = 0
    for name, param in model.named_parameters():
        total_params += param.numel()
        if param.requires_grad:
            trainable_params += param.numel()
    
    report["total_parameters"] = total_params
    report["trainable_parameters"] = trainable_params

    # Check for dropout layers
    for name, module in model.named_modules():
        if isinstance(module, (torch.nn.Dropout, torch.nn.Dropout2d)):
            report["has_dropout"] = True
            break

    if not report["has_dropout"]:
        logger.warning("Model has no Dropout layers — risk of overfitting.")

    # Check for NaN/Inf weights
    all_weights = []
    for name, param in model.named_parameters():
        data = param.data.cpu()
        if torch.isnan(data).any():
            report["nan_params"].append(name)
            report["healthy"] = False
        if torch.isinf(data).any():
            report["inf_params"].append(name)
            report["healthy"] = False
        all_weights.append(data.flatten())

    if all_weights:
        combined = torch.cat(all_weights)
        report["weight_stats"] = {
            "mean": float(combined.mean()),
            "std":  float(combined.std()),
            "min":  float(combined.min()),
            "max":  float(combined.max()),
        }

    if report["nan_params"]:
        logger.error("NaN detected in parameters: %s", report["nan_params"])
    if report["inf_params"]:
        logger.error("Inf detected in parameters: %s", report["inf_params"])

    return report


def compute_gradient_norms(model: torch.nn.Module) -> dict:
    """
    Compute per-layer gradient norms (call after loss.backward()).
    Useful for monitoring training stability.

    Returns:
        dict: layer_name → gradient L2 norm
    """
    norms = {}
    for name, param in model.named_parameters():
        if param.grad is not None:
            norms[name] = float(param.grad.data.norm(2))
    return norms


def log_gradient_norms(model: torch.nn.Module, epoch: int):
    """Log gradient norms for monitoring during training."""
    norms = compute_gradient_norms(model)
    if norms:
        max_name = max(norms, key=norms.get)
        max_norm = norms[max_name]
        avg_norm = np.mean(list(norms.values()))
        logger.info(
            "Epoch %d gradients — avg: %.4f, max: %.4f (%s)",
            epoch, avg_norm, max_norm, max_name,
        )


# ─────────────────────────────────────────────
# 4. HMAC FINDING TOKEN GATE
# ─────────────────────────────────────────────

import hashlib
import hmac as _hmac
import json
import time

_FINDING_TOKEN_TTL = 600  # 10 minutes


def _get_signing_key() -> bytes:
    """Return the signing key from env, or raise if not configured."""
    key = os.environ.get("VULNHGNN_FINDING_SIGNING_KEY", "").strip()
    if not key or len(key) < 16:
        raise ValueError(
            "VULNHGNN_FINDING_SIGNING_KEY is not set or too short (minimum 16 chars)."
        )
    return key.encode("utf-8")


def sign_finding(source: str, language: str, finding: dict) -> str:
    """
    Sign a Gemini finding with a short-lived HMAC token.
    Token is bound to exact source + language + finding + expiry window.
    Returns a hex-encoded HMAC-SHA256 token string: '<expiry>.<hmac>'.
    """
    expiry = int(time.time()) + _FINDING_TOKEN_TTL
    payload = json.dumps(
        {"source": source, "language": language, "finding": finding, "exp": expiry},
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    key = _get_signing_key()
    mac = _hmac.new(key, payload, hashlib.sha256).hexdigest()
    return f"{expiry}.{mac}"


def verify_finding_token(token: str, source: str, language: str, finding: dict) -> bool:
    """
    Verify an HMAC finding token. Returns True only if:
    - Token format is valid
    - Not expired
    - HMAC matches exact source + language + finding
    """
    if not isinstance(token, str) or "." not in token:
        return False
    try:
        expiry_str, mac = token.split(".", 1)
        expiry = int(expiry_str)
    except (ValueError, TypeError):
        return False
    if int(time.time()) > expiry:
        return False
    payload = json.dumps(
        {"source": source, "language": language, "finding": finding, "exp": expiry},
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    try:
        key = _get_signing_key()
    except ValueError:
        return False
    expected = _hmac.new(key, payload, hashlib.sha256).hexdigest()
    return _hmac.compare_digest(mac, expected)


# ─────────────────────────────────────────────
# 5. IN-MEMORY RATE LIMITER (no extra packages)
# ─────────────────────────────────────────────

import collections
import threading as _threading

_rate_lock = _threading.Lock()
_rate_buckets: dict = collections.defaultdict(list)

def check_rate_limit(ip: str, endpoint: str, max_requests: int, window_seconds: int) -> bool:
    """
    Token-bucket rate limiter. Returns True if request is allowed, False if rate-limited.
    Args:
        ip: Client IP address
        endpoint: Endpoint name (used as namespace)
        max_requests: Max requests allowed in window
        window_seconds: Rolling window size in seconds
    """
    key = f"{endpoint}:{ip}"
    now = time.time()
    cutoff = now - window_seconds
    with _rate_lock:
        timestamps = _rate_buckets[key]
        # Remove timestamps outside window
        _rate_buckets[key] = [t for t in timestamps if t > cutoff]
        if len(_rate_buckets[key]) >= max_requests:
            return False
        _rate_buckets[key].append(now)
    return True


# ─────────────────────────────────────────────
# 6. API KEY AUTHENTICATION
# ─────────────────────────────────────────────

def verify_api_key(provided_key: str) -> bool:
    """
    Verify an API key against the configured VULNHGNN_API_KEY env var.
    Returns True if no key is configured (open mode) or if the key matches.
    Uses constant-time comparison to prevent timing attacks.
    """
    expected = os.environ.get("VULNHGNN_API_KEY", "").strip()
    if not expected:
        return True  # No key configured — open mode
    if not provided_key:
        return False
    return _hmac.compare_digest(provided_key.strip(), expected)
