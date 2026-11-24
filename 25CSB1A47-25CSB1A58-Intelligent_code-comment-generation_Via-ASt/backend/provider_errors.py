"""Provider-neutral translation of model-service failures into API errors."""


def classify_provider_error(
    error: Exception | None, provider_name: str
) -> tuple[dict[str, str], int] | None:
    """Return a safe public error payload and HTTP status for known provider errors."""
    if error is None:
        return None

    error_name = type(error).__name__.lower()
    message = str(error).lower()
    response = getattr(error, "response", None)
    status = getattr(response, "status_code", None)

    if status in {401, 403} or any(code in message for code in ("401", "403")):
        public_message = (
            f"{provider_name} rejected the configured token. Check the provider "
            "credentials and model permissions."
        )
        http_status = 502
    elif status == 402 or "402" in message or "payment" in message or "credits" in message:
        public_message = (
            f"{provider_name} inference is unavailable because provider credits "
            "or billing are insufficient."
        )
        http_status = 502
    elif status == 429 or "429" in message or "rate limit" in message:
        public_message = (
            f"{provider_name} inference is rate-limited. Please try again later."
        )
        http_status = 429
    elif (
        status == 504
        or "504" in message
        or "timeout" in message
        or "timed out" in error_name
    ):
        public_message = f"{provider_name} inference timed out. Please try again."
        http_status = 504
    elif status == 503 or "503" in message or "overloaded" in message:
        public_message = (
            f"{provider_name} inference is temporarily unavailable or overloaded. "
            "Please try again later."
        )
        http_status = 503
    elif status == 413 or "413" in message or "too large" in message:
        public_message = "Payload Too Large: input exceeded model capacity."
        http_status = 413
    elif status in {400, 422}:
        public_message = (
            f"{provider_name} rejected the inference request. Check model/provider "
            "access and request compatibility."
        )
        http_status = 502
    elif (
        status == 404
        or "404" in message
        or "not found" in message
        or "not supported" in message
        or "no provider available" in message
    ):
        public_message = (
            f"The selected {provider_name} model or provider is unavailable. "
            "Check the model/provider configuration."
        )
        http_status = 502
    else:
        return None

    return {"error": public_message, "agent_status": "failed"}, http_status
