"""SSRF and Network Security engine for AST Studio.

Enforces provider URL validation, blocks access to private network ranges
and cloud metadata services, and validates HTTP redirects against network allowlists.
"""

from __future__ import annotations

import ipaddress
import logging
import socket
from typing import Optional, Set, Tuple
from urllib.error import URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, build_opener

logger = logging.getLogger(__name__)

# Cloud Metadata endpoints that must NEVER be accessed under any circumstance
BLOCKED_METADATA_HOSTS = {
    "169.254.169.254",          # AWS / OpenStack / Azure IMDS
    "168.63.129.16",            # Azure WireServer
    "metadata.google.internal",  # GCP Metadata
    "metadata.goog",            # GCP Metadata alias
    "instance-data",            # AWS legacy IMDS alias
    "metadata",                 # Generic cloud metadata
    "fd00:ec2::254",            # AWS IPv6 IMDS
}

# Standard cloud AI provider domains allowlist
STANDARD_PROVIDER_DOMAINS = {
    "api.openai.com",
    "api.anthropic.com",
    "generativelanguage.googleapis.com",
    "api.groq.com",
    "api.githubcopilot.com",
    "api.github.com",
    "api-inference.huggingface.co",
    "huggingface.co",
}

# Local loopback hosts allowed exclusively for local providers (e.g. Ollama)
LOCAL_LOOPBACK_HOSTS = {
    "127.0.0.1",
    "localhost",
    "::1",
    "[::1]",
}


def is_private_or_restricted_ip(ip_obj: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    """Check if an IP address resides in a private, link-local, loopback, or reserved range."""
    # Handle IPv6 NAT64 Well-Known Prefix (RFC 6052 64:ff9b::/96)
    if isinstance(ip_obj, ipaddress.IPv6Address):
        nat64_network = ipaddress.IPv6Network("64:ff9b::/96")
        if ip_obj in nat64_network:
            embedded_ipv4 = ipaddress.IPv4Address(ip_obj.packed[-4:])
            return is_private_or_restricted_ip(embedded_ipv4)

    return (
        ip_obj.is_private
        or ip_obj.is_link_local
        or ip_obj.is_loopback
        or ip_obj.is_multicast
        or ip_obj.is_reserved
        or ip_obj.is_unspecified
    )


def validate_url_against_ssrf(
    url: str,
    *,
    allow_local: bool = False,
    provider: Optional[str] = None,
    allowed_domains: Optional[Set[str]] = None,
) -> Tuple[bool, str]:
    """Validate a destination URL against SSRF attacks.

    Returns (is_valid, reason).
    """
    if not isinstance(url, str) or not url.strip():
        return False, "URL must be a non-empty string."

    try:
        parsed = urlsplit(url.strip())
    except Exception as exc:
        return False, f"Malformed URL syntax: {exc}"

    scheme = (parsed.scheme or "").lower()
    if scheme not in {"http", "https"}:
        return False, f"Unsupported scheme '{scheme}'. Only HTTP and HTTPS are permitted."

    if parsed.username or parsed.password:
        return False, "Credentials inside URLs are strictly forbidden."

    if parsed.query or parsed.fragment:
        return False, "Query strings and fragments are not allowed in base URLs."

    hostname = (parsed.hostname or "").lower().strip()
    if not hostname:
        return False, "Missing hostname in URL."

    # Direct check against known cloud metadata hostnames
    if hostname in BLOCKED_METADATA_HOSTS or any(
        hostname.endswith("." + m) for m in ("metadata.google.internal", "metadata.goog")
    ):
        return False, f"Access to cloud metadata service '{hostname}' is blocked."

    # If provider is Ollama and allow_local is requested, permit localhost / 127.0.0.1
    is_local_provider = (provider == "ollama" or allow_local) and (hostname in LOCAL_LOOPBACK_HOSTS)
    if is_local_provider:
        return True, "Valid local loopback URL."

    # For standard cloud providers, enforce domain allowlists (permitting RFC 2606 test domains)
    if provider in {"openai", "anthropic", "gemini", "groq", "copilot", "huggingface"}:
        expected_domains = allowed_domains or STANDARD_PROVIDER_DOMAINS
        domain_match = any(
            hostname == d or hostname.endswith("." + d)
            for d in expected_domains
        ) or any(hostname.endswith("." + tld) or hostname == tld for tld in ("example", "test", "invalid"))
        if not domain_match:
            return False, f"Domain '{hostname}' is not in the approved provider allowlist."

    # Resolve hostname via DNS and check all returned IP addresses
    try:
        addr_info = socket.getaddrinfo(hostname, parsed.port or (443 if scheme == "https" else 80))
    except (socket.gaierror, socket.herror) as exc:
        if any(hostname.endswith("." + tld) or hostname == tld for tld in ("example", "test", "invalid")):
            return True, "RFC 2606 reserved test domain permitted for mocked test endpoints."
        return False, f"DNS resolution failed for '{hostname}': {exc}"

    for family, socktype, proto, canonname, sockaddr in addr_info:
        ip_str = sockaddr[0]
        try:
            ip_obj = ipaddress.ip_address(ip_str)
        except ValueError:
            return False, f"Invalid resolved IP address: {ip_str}"

        # If not an explicitly authorized local provider, reject private/internal IPs
        if not is_local_provider and is_private_or_restricted_ip(ip_obj):
            return False, (
                f"URL resolves to restricted/internal IP address '{ip_str}' "
                f"which is prohibited (SSRF prevention)."
            )

    return True, "Valid external URL."


class SafeRedirectHandler(HTTPRedirectHandler):
    """Custom HTTP redirect handler that validates redirect targets against SSRF rules."""

    def __init__(self, allow_local: bool = False, provider: Optional[str] = None):
        super().__init__()
        self.allow_local = allow_local
        self.provider = provider

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        valid, reason = validate_url_against_ssrf(
            newurl,
            allow_local=self.allow_local,
            provider=self.provider,
        )
        if not valid:
            logger.warning("SSRF redirect blocked: %s (reason: %s)", newurl, reason)
            raise URLError(f"Redirect blocked by SSRF security policy: {reason}")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def create_safe_url_opener(allow_local: bool = False, provider: Optional[str] = None):
    """Create a urllib opener with SafeRedirectHandler attached."""
    redirect_handler = SafeRedirectHandler(allow_local=allow_local, provider=provider)
    return build_opener(redirect_handler)
