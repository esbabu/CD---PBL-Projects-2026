import os
import shutil
import subprocess
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")


def _as_bool(value):
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def _resolve_github_token():
    executable_candidates = []
    gh_candidates = [
        shutil.which("gh"),
        os.path.join(os.environ.get("ProgramFiles", r"C:\Program Files"), "GitHub CLI", "gh.exe"),
        os.path.join(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)"), "GitHub CLI", "gh.exe"),
    ]
    for candidate in gh_candidates:
        if candidate and os.path.exists(candidate):
            executable_candidates.append(candidate)

    copilot_candidates = [
        shutil.which("github-copilot-cli"),
        os.path.join(os.environ.get("ProgramFiles", r"C:\Program Files"), "GitHub CLI", "github-copilot-cli.exe"),
        os.path.join(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)"), "GitHub CLI", "github-copilot-cli.exe"),
    ]
    for candidate in copilot_candidates:
        if candidate and os.path.exists(candidate):
            executable_candidates.append(candidate)

    if not executable_candidates:
        executable_candidates = ["gh", "github-copilot-cli"]

    for executable in dict.fromkeys(executable_candidates):
        try:
            cmd = (executable, "auth", "token")
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        except (FileNotFoundError, OSError):
            continue
        if result.returncode == 0:
            token = result.stdout.strip()
            if token:
                return token
    return ""


def validate_api_key_strength(key: str) -> tuple[bool, str]:
    """Validate that an API key meets enterprise entropy and complexity requirements."""
    if not isinstance(key, str) or not key.strip():
        return False, "API key cannot be empty."
    clean_key = key.strip()
    if len(clean_key) < 16:
        return False, f"API key must be at least 16 characters long (got {len(clean_key)})."
    trivial_fragments = ("changeme", "change-me", "password", "12345678", "secret", "admin", "apikey", "default")
    if any(trivial in clean_key.lower() for trivial in trivial_fragments) or clean_key.lower().startswith("test_key"):
        return False, "API key cannot be or contain a well-known trivial or default placeholder."
    return True, "API key meets complexity requirements."


class AppConfig:
    ENVIRONMENT = os.getenv("ENVIRONMENT", os.getenv("FLASK_ENV", "development")).strip().lower()
    IS_PRODUCTION = ENVIRONMENT in {"production", "prod", "live"}

    DEBUG = False if IS_PRODUCTION else _as_bool(os.getenv("FLASK_DEBUG", ""))
    # Separate application server access key from provider credentials
    SERVER_API_KEY = os.getenv("SERVER_API_KEY", os.getenv("API_KEY", "")).strip()
    API_KEY = SERVER_API_KEY
    AI_PROVIDER = os.getenv("AI_PROVIDER", "ast").strip().lower()
    API_KEY_PROVIDER = AI_PROVIDER
    DOCSTRING_STYLE = os.getenv("DOCSTRING_STYLE", "google").strip().lower()

    # Hugging Face
    HF_TOKEN = os.getenv("HF_TOKEN", "").strip()
    HF_MODEL = os.getenv("HF_MODEL", "Qwen/Qwen3.5-35B-A3B").strip()

    # GitHub Copilot
    COPILOT_TOKEN = os.getenv("COPILOT_TOKEN", "").strip()
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "").strip()
    GH_TOKEN = os.getenv("GH_TOKEN", "").strip()
    COPILOT_MODEL = os.getenv("COPILOT_MODEL", "gpt-4o").strip() or "gpt-4o"
    COPILOT_BASE_URL = os.getenv(
        "COPILOT_BASE_URL", "https://api.githubcopilot.com"
    ).strip().rstrip("/")

    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip() or "gpt-4o-mini"
    OPENAI_BASE_URL = os.getenv(
        "OPENAI_BASE_URL", "https://api.openai.com/v1"
    ).strip().rstrip("/")

    # Google Gemini
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash").strip() or "gemini-2.0-flash"
    GEMINI_BASE_URL = os.getenv(
        "GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai"
    ).strip().rstrip("/")

    # Groq Cloud
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
    GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile").strip() or "llama-3.3-70b-versatile"
    GROQ_BASE_URL = os.getenv(
        "GROQ_BASE_URL", "https://api.groq.com/openai/v1"
    ).strip().rstrip("/")

    # Anthropic
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "").strip()
    ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022").strip() or "claude-3-5-sonnet-20241022"
    ANTHROPIC_BASE_URL = os.getenv(
        "ANTHROPIC_BASE_URL", "https://api.anthropic.com/v1"
    ).strip().rstrip("/")

    # Local Ollama
    OLLAMA_BASE_URL = os.getenv(
        "OLLAMA_BASE_URL", "http://127.0.0.1:11434/v1"
    ).strip().rstrip("/")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:7b").strip()
    OLLAMA_TIMEOUT = float(os.getenv("OLLAMA_TIMEOUT", "180"))

    # In production, default REQUIRE_API_KEY to True unless explicitly disabled
    REQUIRE_API_KEY = (
        True
        if IS_PRODUCTION and "REQUIRE_API_KEY" not in os.environ
        else _as_bool(os.getenv("REQUIRE_API_KEY", "false"))
    )
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", str(30 * 1024 * 1024)))
    MAX_SOURCE_LENGTH = 50_000
    AGENT_MAX_TOKENS = int(os.getenv("AGENT_MAX_TOKENS", "1500"))
    AGENT_MAX_STEPS = int(os.getenv("AGENT_MAX_STEPS", "6"))
    CORS_ORIGINS = tuple(
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", "").split(",")
        if origin.strip()
    )

    SUPPORTED_PROVIDERS = {
        "huggingface",
        "ollama",
        "copilot",
        "openai",
        "gemini",
        "groq",
        "anthropic",
        "ast",
    }

    if AI_PROVIDER not in SUPPORTED_PROVIDERS:
        raise ValueError(
            f"AI_PROVIDER must be one of {', '.join(sorted(SUPPORTED_PROVIDERS))}."
        )
    if AI_PROVIDER == "huggingface" and (not HF_MODEL):
        raise ValueError("AI model and endpoint settings must not be empty.")
    if AI_PROVIDER == "ollama" and (not OLLAMA_BASE_URL or not OLLAMA_MODEL):
        raise ValueError("AI model and endpoint settings must not be empty.")
    if AI_PROVIDER == "copilot" and (not COPILOT_BASE_URL or not COPILOT_MODEL):
        raise ValueError("Copilot configuration is incomplete.")
    if AI_PROVIDER == "openai" and (not OPENAI_BASE_URL or not OPENAI_MODEL):
        raise ValueError("OpenAI configuration is incomplete.")
    if AI_PROVIDER == "gemini" and (not GEMINI_BASE_URL or not GEMINI_MODEL):
        raise ValueError("Gemini configuration is incomplete.")
    if AI_PROVIDER == "groq" and (not GROQ_BASE_URL or not GROQ_MODEL):
        raise ValueError("Groq configuration is incomplete.")
    if AI_PROVIDER == "anthropic" and (not ANTHROPIC_BASE_URL or not ANTHROPIC_MODEL):
        raise ValueError("Anthropic configuration is incomplete.")


SUPPORTED_PROVIDERS = AppConfig.SUPPORTED_PROVIDERS
