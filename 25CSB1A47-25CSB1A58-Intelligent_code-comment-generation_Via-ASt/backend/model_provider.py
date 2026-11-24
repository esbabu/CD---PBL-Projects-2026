"""Shared Hugging Face, local Ollama, and GitHub Copilot model configuration."""

import json
import hashlib
import logging
import threading
from types import SimpleNamespace
from urllib import request as urllib_request
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit, urlunsplit
from urllib.request import urlopen

from backend.config import AppConfig, _resolve_github_token
from backend.provider_errors import classify_provider_error
from backend.security_ssrf import validate_url_against_ssrf

try:
    from huggingface_hub import InferenceClient
except ImportError:  # pragma: no cover
    InferenceClient = None

logger = logging.getLogger(__name__)

_PROVIDER_STATUS_LOCK = threading.Lock()
_LAST_PROVIDER_TEST = None


def _get_active_model_name(provider=None):
    p = (provider or AppConfig.AI_PROVIDER).strip().lower()
    if p == "copilot":
        return AppConfig.COPILOT_MODEL
    if p == "openai":
        return AppConfig.OPENAI_MODEL
    if p == "gemini":
        return AppConfig.GEMINI_MODEL
    if p == "groq":
        return AppConfig.GROQ_MODEL
    if p == "anthropic":
        return AppConfig.ANTHROPIC_MODEL
    if p == "ollama":
        return AppConfig.OLLAMA_MODEL
    if p == "ast":
        return "Deterministic AST"
    return AppConfig.HF_MODEL


MODEL_NAME = _get_active_model_name()


def provider_extra_body(provider_id=None) -> dict:
    """Return provider-specific extra body parameters.

    Returns {"chat_template_kwargs": {"enable_thinking": False}} exclusively for
    the 'huggingface' provider and {} for all other providers (copilot, openai,
    gemini, groq, anthropic, ollama, ast).
    """
    p = (provider_id or AppConfig.AI_PROVIDER or "").strip().lower()
    if p in {"huggingface", "hf"}:
        return {"chat_template_kwargs": {"enable_thinking": False}}
    return {}

_BASE_URL_ATTRIBUTES = {
    "copilot": "COPILOT_BASE_URL",
    "openai": "OPENAI_BASE_URL",
    "gemini": "GEMINI_BASE_URL",
    "groq": "GROQ_BASE_URL",
    "anthropic": "ANTHROPIC_BASE_URL",
    "ollama": "OLLAMA_BASE_URL",
}
_DEFAULT_BASE_URLS = {
    provider: getattr(AppConfig, attribute)
    for provider, attribute in _BASE_URL_ATTRIBUTES.items()
}
_PROVIDER_KEY_ATTRIBUTES = {
    "huggingface": "HF_TOKEN",
    "copilot": "COPILOT_TOKEN",
    "openai": "OPENAI_API_KEY",
    "gemini": "GEMINI_API_KEY",
    "groq": "GROQ_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
}


class ModelRequestError(RuntimeError):
    def __init__(self, message, status_code=None):
        super().__init__(message)
        self.response = SimpleNamespace(status_code=status_code)


class CopilotRequestError(ModelRequestError):
    pass


class OpenAICompatibleCompletions:
    def __init__(
        self,
        api_key,
        base_url,
        model_name,
        custom_headers=None,
        timeout: float = 120,
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model_name = model_name
        self.custom_headers = custom_headers or {}
        self.timeout = timeout

    def create(self, **kwargs):
        if not self.api_key and "ollama" not in self.base_url:
            raise ModelRequestError("API key is not configured for this provider.", 401)

        payload = {
            "model": kwargs.get("model") or self.model_name,
            "messages": kwargs.get("messages", []),
            "temperature": kwargs.get("temperature", 0.1),
            "max_tokens": kwargs.get("max_tokens", 1500),
        }
        extra_body = kwargs.get("extra_body", {})
        if isinstance(extra_body, dict):
            payload.update(
                {
                    key: value
                    for key, value in extra_body.items()
                    if key != "chat_template_kwargs"
                }
            )

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        headers.update(self.custom_headers)

        endpoint = f"{self.base_url}/chat/completions"
        allow_local = "ollama" in self.base_url or "127.0.0.1" in self.base_url or "localhost" in self.base_url
        is_safe, reason = validate_url_against_ssrf(endpoint, allow_local=allow_local)
        if not is_safe:
            raise ModelRequestError(f"SSRF protection blocked request to '{endpoint}': {reason}", 403)

        data = json.dumps(payload).encode("utf-8")
        req = urllib_request.Request(endpoint, data=data, headers=headers, method="POST")
        try:
            with urllib_request.urlopen(req, timeout=self.timeout) as response:
                body = response.read().decode("utf-8")
                result = json.loads(body)
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise ModelRequestError(
                f"Provider request failed: {detail or exc.reason}",
                getattr(exc, "code", None),
            ) from exc
        except (URLError, TimeoutError, ValueError) as exc:
            raise ModelRequestError(
                f"Provider request failed: {exc}",
                None,
            ) from exc

        choice = (result.get("choices") or [{}])[0]
        message = choice.get("message") or {}
        content = message.get("content") or ""
        if isinstance(content, list):
            parts = []
            for part in content:
                if isinstance(part, dict):
                    text = part.get("text") or part.get("content") or ""
                    if isinstance(text, str):
                        parts.append(text)
                elif isinstance(part, str):
                    parts.append(part)
            content = "".join(parts)
        if not isinstance(content, str):
            content = str(content)
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=content))]
        )


class CopilotCompletions(OpenAICompatibleCompletions):
    def __init__(self, api_key, base_url, model_name):
        super().__init__(
            api_key=api_key,
            base_url=base_url,
            model_name=model_name,
            custom_headers={
                "Editor-Version": "vscode/1.0",
                "Copilot-Integration-Id": "vscode-chat",
            },
            timeout=180,
        )


class AnthropicCompletions:
    def __init__(self, api_key, base_url, model_name, timeout: float = 120):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model_name = model_name
        self.timeout = timeout

    def create(self, **kwargs):
        if not self.api_key:
            raise ModelRequestError("Anthropic API key is not configured.", 401)

        messages = kwargs.get("messages", [])
        system_content = ""
        user_messages = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "system":
                system_content = content
            else:
                user_messages.append({"role": role, "content": content})

        payload = {
            "model": kwargs.get("model") or self.model_name,
            "messages": user_messages or [{"role": "user", "content": "Hello"}],
            "max_tokens": kwargs.get("max_tokens", 1500),
            "temperature": kwargs.get("temperature", 0.1),
        }
        if system_content:
            payload["system"] = system_content

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
            "accept": "application/json",
        }
        endpoint = f"{self.base_url}/messages"
        allow_local = "127.0.0.1" in self.base_url or "localhost" in self.base_url
        is_safe, reason = validate_url_against_ssrf(endpoint, allow_local=allow_local)
        if not is_safe:
            raise ModelRequestError(f"SSRF protection blocked request to '{endpoint}': {reason}", 403)

        data = json.dumps(payload).encode("utf-8")
        req = urllib_request.Request(endpoint, data=data, headers=headers, method="POST")
        try:
            with urllib_request.urlopen(req, timeout=self.timeout) as response:
                body = response.read().decode("utf-8")
                result = json.loads(body)
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise ModelRequestError(
                f"Anthropic request failed: {detail or exc.reason}",
                getattr(exc, "code", None),
            ) from exc
        except (URLError, TimeoutError, ValueError) as exc:
            raise ModelRequestError(
                f"Anthropic request failed: {exc}",
                None,
            ) from exc

        content_parts = result.get("content", [])
        text_parts = [p.get("text", "") for p in content_parts if isinstance(p, dict)]
        content = "".join(text_parts)
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=content))]
        )


class CopilotClient:
    def __init__(self, api_key, base_url, model_name):
        self.chat = SimpleNamespace(
            completions=CopilotCompletions(api_key, base_url, model_name)
        )


class UniversalClient:
    def __init__(self, completions_obj):
        self.chat = SimpleNamespace(completions=completions_obj)


def _provider_api_key(provider, api_key_override=None):
    """Resolve only credentials intended for the selected provider."""
    if api_key_override:
        return str(api_key_override).strip()
    if (
        provider == AppConfig.API_KEY_PROVIDER
        and AppConfig.API_KEY
        and AppConfig.API_KEY.strip()
    ):
        return AppConfig.API_KEY.strip()
    attribute = _PROVIDER_KEY_ATTRIBUTES.get(provider)
    if attribute:
        key = getattr(AppConfig, attribute, "")
        if key and key.strip():
            return key.strip()
    if provider == "copilot":
        for attribute in ("GITHUB_TOKEN", "GH_TOKEN"):
            key = getattr(AppConfig, attribute, "")
            if key and key.strip():
                return key.strip()
        return _resolve_github_token()
    return ""


def _provider_base_url(provider, override=None):
    attribute = _BASE_URL_ATTRIBUTES.get(provider)
    if attribute is None:
        return None
    if isinstance(override, str) and override.strip():
        return override.strip().rstrip("/")
    return getattr(AppConfig, attribute)


def create_model_client(
    provider_override=None,
    api_key_override=None,
    model_override=None,
    base_url_override=None,
):
    """Create the configured provider client."""
    provider = (provider_override or AppConfig.AI_PROVIDER).strip().lower()
    api_key = _provider_api_key(provider, api_key_override)

    if provider == "ast":
        return None

    if provider == "copilot":
        token = api_key
        if not token:
            return None
        return CopilotClient(
            api_key=token,
            base_url=_provider_base_url(provider, base_url_override),
            model_name=model_override or AppConfig.COPILOT_MODEL,
        )

    if provider == "openai":
        if not api_key:
            return None
        return UniversalClient(
            OpenAICompatibleCompletions(
                api_key=api_key,
                base_url=_provider_base_url(provider, base_url_override),
                model_name=model_override or AppConfig.OPENAI_MODEL,
            )
        )

    if provider == "gemini":
        if not api_key:
            return None
        return UniversalClient(
            OpenAICompatibleCompletions(
                api_key=api_key,
                base_url=_provider_base_url(provider, base_url_override),
                model_name=model_override or AppConfig.GEMINI_MODEL,
            )
        )

    if provider == "groq":
        if not api_key:
            return None
        return UniversalClient(
            OpenAICompatibleCompletions(
                api_key=api_key,
                base_url=_provider_base_url(provider, base_url_override),
                model_name=model_override or AppConfig.GROQ_MODEL,
            )
        )

    if provider == "anthropic":
        if not api_key:
            return None
        return UniversalClient(
            AnthropicCompletions(
                api_key=api_key,
                base_url=_provider_base_url(provider, base_url_override),
                model_name=model_override or AppConfig.ANTHROPIC_MODEL,
            )
        )

    if provider == "ollama":
        return UniversalClient(
            OpenAICompatibleCompletions(
                api_key="ollama",
                base_url=_provider_base_url(provider, base_url_override),
                model_name=model_override or AppConfig.OLLAMA_MODEL,
                timeout=AppConfig.OLLAMA_TIMEOUT,
            )
        )

    # Hugging Face default
    if InferenceClient is None:
        return None
    if not api_key:
        return None
    return InferenceClient(api_key=api_key)


def provider_ready(client):
    """Check provider reachability and model availability for UI health."""
    if AppConfig.AI_PROVIDER == "ast":
        return True
    if client is None:
        return False
    if AppConfig.AI_PROVIDER in _PROVIDER_KEY_ATTRIBUTES:
        return bool(_provider_api_key(AppConfig.AI_PROVIDER))
    if AppConfig.AI_PROVIDER != "ollama":
        return True

    parsed_url = urlsplit(AppConfig.OLLAMA_BASE_URL)
    path = parsed_url.path.rstrip("/")
    if path.endswith("/v1"):
        path = path[:-3]
    tags_url = urlunsplit(
        (parsed_url.scheme, parsed_url.netloc, f"{path}/api/tags", "", "")
    )
    try:
        with urlopen(tags_url, timeout=1.5) as response:
            models = json.load(response).get("models", [])
    except (OSError, URLError, TimeoutError, ValueError) as exc:
        logger.info("Local Ollama is not ready (%s).", type(exc).__name__)
        return False

    return any(
        isinstance(model, dict)
        and model.get("name") == AppConfig.OLLAMA_MODEL
        for model in models
    )


def _provider_config_signature(provider, api_key=None, model=None, base_url=None):
    resolved_model = model or _get_active_model_name(provider)
    resolved_base_url = _provider_base_url(provider, base_url) or ""
    resolved_key = _provider_api_key(provider, api_key)
    signature_input = "\0".join(
        (provider, resolved_model, resolved_base_url, resolved_key)
    ).encode("utf-8")
    return hashlib.sha256(signature_input).hexdigest()


def _provider_is_configured(provider):
    if provider == "ast":
        return False
    if provider in _PROVIDER_KEY_ATTRIBUTES:
        return bool(_provider_api_key(provider))
    return create_model_client(provider_override=provider) is not None


def _remember_provider_test(provider, signature, success, error=None):
    if provider != AppConfig.AI_PROVIDER:
        return
    if signature != _provider_config_signature(provider):
        return
    global _LAST_PROVIDER_TEST
    with _PROVIDER_STATUS_LOCK:
        _LAST_PROVIDER_TEST = {
            "signature": signature,
            "success": success,
            "error": error,
        }


def provider_connection_status():
    """Return a truthful status for the currently selected provider profile."""
    provider = AppConfig.AI_PROVIDER.strip().lower()
    if provider == "ast":
        return "AST MODE", "Deterministic analysis is active; no external model is used."
    if not _provider_is_configured(provider):
        return "NOT CONFIGURED", "Configure credentials or a local model before using AI."

    signature = _provider_config_signature(provider)
    with _PROVIDER_STATUS_LOCK:
        last_test = _LAST_PROVIDER_TEST
        if last_test and last_test["signature"] == signature:
            if last_test["success"]:
                return "CONNECTED", "The current provider settings passed a live request."
            return "FAILED", last_test["error"]
    return "CONFIGURED / NOT TESTED", "Credentials are configured; run Test Provider to verify connectivity."


def provider_display_name(provider=None):
    """Return a user-facing name for the configured AI provider."""
    p = (provider or AppConfig.AI_PROVIDER).strip().lower()
    names = {
        "openai": "OpenAI",
        "gemini": "Google Gemini",
        "groq": "Groq Cloud",
        "anthropic": "Anthropic Claude",
        "copilot": "GitHub Copilot",
        "ollama": "Local Ollama",
        "huggingface": "Hugging Face",
        "ast": "Deterministic AST Engine",
    }
    return names.get(p, p.capitalize())


def test_provider_connectivity(provider, api_key=None, model=None, base_url=None):
    """Live verification of provider API credentials and latency."""
    import time

    started = time.perf_counter()
    p = provider.strip().lower()
    signature = _provider_config_signature(p, api_key, model, base_url)
    if p == "ast":
        return {
            "success": True,
            "latency_ms": 0.5,
            "provider": "Deterministic AST Engine",
            "model": "Zero-Cloud Offline AST",
            "provider_status": "AST MODE",
        }

    if base_url:
        is_safe, reason = validate_url_against_ssrf(
            base_url,
            allow_local=(p == "ollama"),
            provider=p,
        )
        if not is_safe:
            return {
                "success": False,
                "error": f"Invalid provider URL (SSRF blocked): {reason}",
                "provider": provider_display_name(p),
            }

    temp_client = create_model_client(
        provider_override=p,
        api_key_override=api_key,
        model_override=model,
        base_url_override=base_url,
    )
    if not temp_client:
        result = {
            "success": False,
            "error": f"API key is missing or could not initialize client for {p}.",
            "provider": provider_display_name(p),
            "provider_status": "NOT CONFIGURED",
        }
        _remember_provider_test(p, signature, False, result["error"])
        return result

    try:
        if hasattr(temp_client, "chat"):
            target_model = model or _get_active_model_name(p)
            resp = temp_client.chat.completions.create(
                model=target_model,
                messages=[{"role": "user", "content": "Respond with 'OK'"}],
                max_tokens=10,
                temperature=0.0,
            )
            content = resp.choices[0].message.content or ""
        elif callable(getattr(temp_client, "text_generation", None)):
            text_generation = getattr(temp_client, "text_generation")
            content = text_generation("Respond with 'OK'", max_new_tokens=5)
        else:
            raise RuntimeError("The configured provider client has no completion interface.")

        if not isinstance(content, str) or not content.strip():
            raise RuntimeError("The provider returned an empty connectivity response.")

        elapsed = round((time.perf_counter() - started) * 1000, 1)
        result = {
            "success": True,
            "latency_ms": elapsed,
            "provider": provider_display_name(p),
            "model": model or _get_active_model_name(p),
            "sample_response": content.strip()[:60],
            "provider_status": "CONNECTED",
        }
        _remember_provider_test(p, signature, True)
        return result
    except Exception as exc:
        classified = classify_provider_error(exc, provider_display_name(p))
        safe_error = (
            classified[0]["error"]
            if classified
            else "Provider request failed. Check network access, model availability, and provider settings."
        )
        logger.warning(
            "Provider connectivity test failed provider=%s error_type=%s",
            p,
            type(exc).__name__,
        )
        _remember_provider_test(p, signature, False, safe_error)
        return {
            "success": False,
            "error": safe_error,
            "provider": provider_display_name(p),
            "provider_status": "FAILED",
        }


def get_current_settings():
    """Retrieve full runtime provider and docstring settings."""
    from backend.config import SUPPORTED_PROVIDERS

    p = AppConfig.AI_PROVIDER
    has_key = p in {"ast", "ollama"} or bool(_provider_api_key(p))
    base_url_attribute = _BASE_URL_ATTRIBUTES.get(p)
    provider_status, provider_status_detail = provider_connection_status()
    return {
        "provider": p,
        "provider_display": provider_display_name(p),
        "model": _get_active_model_name(),
        "base_url": (
            getattr(AppConfig, base_url_attribute)
            if base_url_attribute
            else ""
        ),
        "supports_base_url": base_url_attribute is not None,
        "docstring_style": AppConfig.DOCSTRING_STYLE,
        "supported_providers": sorted(list(SUPPORTED_PROVIDERS)),
        "supported_styles": ["google", "sphinx", "numpy", "standard"],
        "has_api_key": has_key,
        "ai_ready": provider_ready(None if p == "ast" else create_model_client()),
        "provider_status": provider_status,
        "provider_status_detail": provider_status_detail,
    }


def update_provider_settings(
    provider=None,
    api_key=None,
    model=None,
    base_url=None,
    docstring_style=None,
):
    """Dynamically update runtime provider settings."""
    global MODEL_NAME
    from backend.config import SUPPORTED_PROVIDERS

    if provider:
        p = str(provider).strip().lower()
        if p in SUPPORTED_PROVIDERS:
            AppConfig.AI_PROVIDER = p

    active_p = AppConfig.AI_PROVIDER

    if api_key is not None:
        key_str = str(api_key).strip()
        AppConfig.API_KEY_PROVIDER = active_p
        if active_p == "openai":
            AppConfig.OPENAI_API_KEY = key_str
        elif active_p == "gemini":
            AppConfig.GEMINI_API_KEY = key_str
        elif active_p == "groq":
            AppConfig.GROQ_API_KEY = key_str
        elif active_p == "anthropic":
            AppConfig.ANTHROPIC_API_KEY = key_str
        elif active_p == "copilot":
            AppConfig.COPILOT_TOKEN = key_str
        elif active_p == "huggingface":
            AppConfig.HF_TOKEN = key_str

    if model:
        m_str = str(model).strip()
        if active_p == "openai":
            AppConfig.OPENAI_MODEL = m_str
        elif active_p == "gemini":
            AppConfig.GEMINI_MODEL = m_str
        elif active_p == "groq":
            AppConfig.GROQ_MODEL = m_str
        elif active_p == "anthropic":
            AppConfig.ANTHROPIC_MODEL = m_str
        elif active_p == "ollama":
            AppConfig.OLLAMA_MODEL = m_str
        elif active_p == "copilot":
            AppConfig.COPILOT_MODEL = m_str
        elif active_p == "huggingface":
            AppConfig.HF_MODEL = m_str

    base_url_attribute = _BASE_URL_ATTRIBUTES.get(active_p)
    if base_url is not None and base_url_attribute:
        base_url_value = str(base_url).strip().rstrip("/")
        if base_url_value:
            is_safe, reason = validate_url_against_ssrf(
                base_url_value,
                allow_local=(active_p == "ollama"),
                provider=active_p,
            )
            if not is_safe:
                raise ValueError(f"SSRF validation blocked provider base URL: {reason}")
        setattr(
            AppConfig,
            base_url_attribute,
            base_url_value or _DEFAULT_BASE_URLS[active_p],
        )

    if docstring_style:
        style_str = str(docstring_style).strip().lower()
        if style_str in {"google", "sphinx", "numpy", "standard"}:
            AppConfig.DOCSTRING_STYLE = style_str

    MODEL_NAME = _get_active_model_name()
    _refresh_runtime_clients()
    global _LAST_PROVIDER_TEST
    with _PROVIDER_STATUS_LOCK:
        _LAST_PROVIDER_TEST = None

    return get_current_settings()


def _refresh_runtime_clients():
    """Apply updated provider settings to the long-lived app and agent runtimes."""
    model_client = create_model_client()

    import backend.app as app_module
    import backend.code_analysis as code_analysis_module
    from backend.agentic.routes import _runtime

    code_analysis_module.client = model_client
    app_module.client = model_client
    _runtime.set_model_client(model_client, MODEL_NAME)
