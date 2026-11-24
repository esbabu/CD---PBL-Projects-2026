"""Test configuration to guarantee that the project root is on the Python import path.

When pytest is invoked from the virtual‑environment scripts directory, the
project root may not be automatically added to ``sys.path``. This leads to
import errors such as ``ModuleNotFoundError: No module named 'backend'`` in the
test suite. By inserting the absolute path of the repository root at the
start of ``sys.path`` we make the ``backend`` package (and any other local
modules) importable without affecting the runtime behavior of the application.
"""

import ipaddress
import os
import socket
import sys

import pytest

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def pytest_configure(config):
    config.addinivalue_line("markers", "allow_network: opt-in to network/DNS access")
    config.addinivalue_line("markers", "allow_dns: opt-in to network/DNS access")


_BROWSER_TEST_MODULES = {
    "test_frontend_audit_renderer.py",
    "test_nexus_ui_states.py",
    "test_production_e2e_frontend.py",
}


def pytest_addoption(parser):
    try:
        parser.addoption(
            "--run-browser-tests",
            action="store_true",
            default=False,
            help="Run Playwright browser integration tests (may require a working local browser runtime).",
        )
    except ValueError:
        # Option already added by another plugin; ignore to avoid conflict
        pass


def pytest_collection_modifyitems(config, items):
    if config.getoption("--run-browser-tests"):
        return

    skip_browser = pytest.mark.skip(
        reason="Playwright browser tests are opt-in; pass --run-browser-tests to run them."
    )
    for item in items:
        module_name = item.nodeid.split("::", 1)[0].replace("\\", "/").rsplit("/", 1)[-1]
        if module_name in _BROWSER_TEST_MODULES:
            item.add_marker(skip_browser)


_ORIG_GETADDRINFO = socket.getaddrinfo


@pytest.fixture(autouse=True)
def hermetic_environment(monkeypatch, request):
    """Hermetic test environment fixture:
    1. Clears AI_PROVIDER, API_KEY, GITHUB_TOKEN, and any COPILOT_* or HF_* environment variables.
    2. Sets AI_PROVIDER=ast.
    3. Resets AppConfig provider/credential attributes and prevents ambient CLI credential resolution.
    4. Blocks real DNS/network sockets by monkeypatching socket.getaddrinfo unless opted in.
    """
    for key in list(os.environ.keys()):
        if (
            key in {"AI_PROVIDER", "API_KEY", "GITHUB_TOKEN", "GH_TOKEN"}
            or key.startswith("COPILOT_")
            or key.startswith("HF_")
        ):
            monkeypatch.delenv(key, raising=False)

    monkeypatch.setenv("AI_PROVIDER", "ast")
    monkeypatch.setenv("ALLOW_PROJECT_TEST_EXECUTION", "false")

    from backend.config import AppConfig
    import backend.config as backend_config

    monkeypatch.setattr(AppConfig, "AI_PROVIDER", "ast")
    monkeypatch.setattr(AppConfig, "API_KEY_PROVIDER", "ast")
    monkeypatch.setattr(AppConfig, "API_KEY", "")
    monkeypatch.setattr(AppConfig, "SERVER_API_KEY", "")
    monkeypatch.setattr(AppConfig, "HF_TOKEN", "")
    monkeypatch.setattr(AppConfig, "COPILOT_TOKEN", "")
    monkeypatch.setattr(AppConfig, "GITHUB_TOKEN", "")
    monkeypatch.setattr(AppConfig, "GH_TOKEN", "")
    monkeypatch.setattr(AppConfig, "OPENAI_API_KEY", "")
    monkeypatch.setattr(AppConfig, "GEMINI_API_KEY", "")
    monkeypatch.setattr(AppConfig, "GROQ_API_KEY", "")
    monkeypatch.setattr(AppConfig, "ANTHROPIC_API_KEY", "")
    monkeypatch.setattr(backend_config, "_resolve_github_token", lambda: "")

    from backend.security_rate_limit import default_rate_limiter
    default_rate_limiter.reset()

    def guarded_getaddrinfo(host, port, *args, **kwargs):
        if (
            request.node.get_closest_marker("allow_network")
            or request.node.get_closest_marker("allow_dns")
            or "allow_network" in getattr(request, "fixturenames", ())
        ):
            return _ORIG_GETADDRINFO(host, port, *args, **kwargs)

        if host in ("localhost", "127.0.0.1", "::1"):
            return _ORIG_GETADDRINFO(host, port, *args, **kwargs)

        try:
            if host:
                ipaddress.ip_address(host)
                return _ORIG_GETADDRINFO(host, port, *args, **kwargs)
        except ValueError:
            pass

        raise socket.gaierror(
            -2,
            f"Real DNS/network resolution blocked for '{host}' by hermetic test suite",
        )

    monkeypatch.setattr(socket, "getaddrinfo", guarded_getaddrinfo)
    yield
    default_rate_limiter.reset()

