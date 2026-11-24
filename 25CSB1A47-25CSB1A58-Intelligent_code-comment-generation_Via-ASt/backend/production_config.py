"""Production configuration and security hardening for AST Studio.

This module provides enterprise-grade configuration defaults for production
deployments, including strict TLS/cookie policies, bounded resource limits,
database WAL settings, and API authentication enforcement.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any, Dict

from .config import AppConfig, validate_api_key_strength

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
INSTANCE_DIR = BASE_DIR / "instance"
INSTANCE_DIR.mkdir(parents=True, exist_ok=True)


class ProductionConfig(AppConfig):
    """Hardened production settings extending AppConfig."""

    ENVIRONMENT = "production"
    IS_PRODUCTION = True
    DEBUG = False
    TESTING = False

    # Force secure cookies and strict CSRF/session handling
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Strict"
    PERMANENT_SESSION_LIFETIME = 1800  # 30 minutes

    # Security headers
    SECURITY_HEADERS = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
        "Content-Security-Policy": (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net; "
            "font-src 'self' https://fonts.gstatic.com data:; "
            "img-src 'self' data:; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        ),
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
    }

    # Bounded resource limits
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", str(30 * 1024 * 1024)))  # 30MB (allows 25MB archive + multipart overhead)
    MAX_SOURCE_LENGTH = int(os.getenv("MAX_SOURCE_LENGTH", "100000"))
    MAX_CONCURRENT_SESSIONS = int(os.getenv("MAX_CONCURRENT_SESSIONS", "50"))
    MAX_EXECUTION_WALL_CLOCK_SECONDS = int(os.getenv("MAX_EXECUTION_WALL_CLOCK_SECONDS", "300"))

    # Database configuration with SQLite WAL support
    DATABASE_PATH = os.getenv("DATABASE_PATH", str(INSTANCE_DIR / "session_store.db"))
    DB_BUSY_TIMEOUT_MS = int(os.getenv("DB_BUSY_TIMEOUT_MS", "5000"))
    DB_ENABLE_WAL = True

    # Rate limiting defaults for production
    RATELIMIT_DEFAULT = os.getenv("RATELIMIT_DEFAULT", "120/minute")
    RATELIMIT_BURST = os.getenv("RATELIMIT_BURST", "30/minute")

    # API authentication enforcement
    REQUIRE_API_KEY = True

    @classmethod
    def validate_production_readiness(cls) -> Dict[str, Any]:
        """Validate production configuration and return a health report."""
        warnings: list[str] = []
        errors: list[str] = []

        # Check server API key strength
        server_key = cls.SERVER_API_KEY
        if not server_key:
            errors.append("SERVER_API_KEY is not configured in production environment.")
        else:
            valid, msg = validate_api_key_strength(server_key)
            if not valid:
                warnings.append(f"SERVER_API_KEY security warning: {msg}")

        # Check AI provider credentials
        provider = cls.AI_PROVIDER
        if provider == "openai" and not cls.OPENAI_API_KEY:
            warnings.append("AI_PROVIDER is 'openai' but OPENAI_API_KEY is unset.")
        elif provider == "huggingface" and not cls.HF_TOKEN:
            warnings.append("AI_PROVIDER is 'huggingface' but HF_TOKEN is unset.")
        elif provider == "gemini" and not cls.GEMINI_API_KEY:
            warnings.append("AI_PROVIDER is 'gemini' but GEMINI_API_KEY is unset.")
        elif provider == "groq" and not cls.GROQ_API_KEY:
            warnings.append("AI_PROVIDER is 'groq' but GROQ_API_KEY is unset.")
        elif provider == "anthropic" and not cls.ANTHROPIC_API_KEY:
            warnings.append("AI_PROVIDER is 'anthropic' but ANTHROPIC_API_KEY is unset.")

        # Check database directory permissions
        db_path = Path(cls.DATABASE_PATH)
        if not db_path.parent.exists():
            try:
                db_path.parent.mkdir(parents=True, exist_ok=True)
            except Exception as exc:
                errors.append(f"Cannot create database parent directory: {exc}")

        return {
            "status": "ready" if not errors else "misconfigured",
            "environment": cls.ENVIRONMENT,
            "errors": errors,
            "warnings": warnings,
            "database_path": str(db_path),
            "require_api_key": cls.REQUIRE_API_KEY,
            "ai_provider": cls.AI_PROVIDER,
        }
