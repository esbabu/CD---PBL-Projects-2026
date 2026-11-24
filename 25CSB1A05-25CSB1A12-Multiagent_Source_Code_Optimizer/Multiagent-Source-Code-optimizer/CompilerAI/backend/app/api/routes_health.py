import os
import sys
import time
from pathlib import Path
from typing import Any, Dict
from fastapi import APIRouter
from app.core.config import settings

router = APIRouter(tags=["health"])

_OLLAMA_CACHE: Any = None
_TOOLCHAIN_CACHE: Dict[str, Any] = {"ts": 0.0, "data": {}}


def _ensure_algo_path() -> bool:
    algo_path = Path(settings.algo_agent_path).resolve()
    if not algo_path.is_dir():
        return False
    if str(algo_path) not in sys.path:
        sys.path.insert(0, str(algo_path))
    return True


def get_live_ollama_status() -> Dict[str, Any]:
    """Read-only cached probe of the local Ollama server (never starts/pulls)."""
    global _OLLAMA_CACHE
    if not _ensure_algo_path():
        return {
            "reachable": False,
            "base_url": "http://localhost:11434",
            "models": [],
            "active_model": None,
            "roles": {},
            "reason_kind": "not_configured",
            "remediation": "OptAgent package not found; LLM gateway unavailable.",
        }
    try:
        from optagent.config import Settings as OptSettings
        from optagent.llm.health import HealthCache, resolve_role_models

        if _OLLAMA_CACHE is None:
            _OLLAMA_CACHE = HealthCache(ttl_s=30.0)
        opt_settings = OptSettings()
        probe_url = opt_settings.ollama_base.replace("://localhost:", "://127.0.0.1:")
        h = _OLLAMA_CACHE.check(probe_url, connect_timeout=0.5)
        if h.reachable and h.models:
            res = resolve_role_models(h.models, opt_settings)
            roles = res.get("resolved", {})
            active = roles.get("proposer") or roles.get("spec") or h.model_names[0]
            return {
                "reachable": True,
                "base_url": h.base_url,
                "version": h.version,
                "models": h.model_names,
                "active_model": active,
                "roles": roles,
                "reason_kind": "ok",
                "remediation": "",
            }
        return {
            "reachable": h.reachable,
            "base_url": h.base_url,
            "version": h.version,
            "models": h.model_names,
            "active_model": None,
            "roles": {},
            "reason_kind": h.reason_kind,
            "remediation": h.remediation,
        }
    except Exception as exc:
        return {
            "reachable": False,
            "base_url": "http://localhost:11434",
            "models": [],
            "active_model": None,
            "roles": {},
            "reason_kind": "error",
            "remediation": str(exc),
        }


def get_toolchain_readiness() -> Dict[str, Any]:
    now = time.time()
    if _TOOLCHAIN_CACHE["data"] and (now - _TOOLCHAIN_CACHE["ts"]) < 60.0:
        return _TOOLCHAIN_CACHE["data"]
    import shutil

    node_ok = bool(shutil.which("node") or (Path.home() / ".nodejs" / "node-v20.18.0-win-x64" / "node.exe").is_file())
    c_ok = bool(shutil.which("clang") or shutil.which("gcc"))
    cpp_ok = bool(shutil.which("clang++") or shutil.which("g++"))
    docker_ok = bool(shutil.which("docker"))
    langs = {
        "python": {"ready": True, "backend": "local", "remediation": None},
        "javascript": {
            "ready": node_ok or docker_ok,
            "backend": "local" if node_ok else ("docker" if docker_ok else "unavailable"),
            "remediation": None if (node_ok or docker_ok) else "Install Node.js >= 18 or build docker/sandbox-js.Dockerfile.",
        },
        "c": {
            "ready": c_ok or docker_ok,
            "backend": "local" if c_ok else ("docker" if docker_ok else "unavailable"),
            "remediation": None if (c_ok or docker_ok) else "Install clang/gcc (and set OPT_ALLOW_LOCAL_NATIVE=1) or build docker/sandbox-native.Dockerfile.",
        },
        "cpp": {
            "ready": cpp_ok or docker_ok,
            "backend": "local" if cpp_ok else ("docker" if docker_ok else "unavailable"),
            "remediation": None if (cpp_ok or docker_ok) else "Install clang++/g++ (and set OPT_ALLOW_LOCAL_NATIVE=1) or build docker/sandbox-native.Dockerfile.",
        },
    }
    _TOOLCHAIN_CACHE["data"] = langs
    _TOOLCHAIN_CACHE["ts"] = now
    return langs


@router.get("/health")
def get_health():
    groq_api_key = os.getenv("GROQ_API_KEY")
    ollama = get_live_ollama_status()
    if groq_api_key or (ollama.get("reachable") and ollama.get("models")):
        llm_connection = "connected"
    elif ollama.get("reason_kind") == "no_models":
        llm_connection = "no_models"
    elif not groq_api_key and not ollama.get("reachable"):
        llm_connection = "not_configured"
    else:
        llm_connection = "unreachable"

    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "demo_mode": settings.demo_mode,
        "adapters": {
            "optimization": settings.optimization_adapter_mode,
            "security": settings.security_adapter_mode,
        },
        "llm_connection": llm_connection,
        "ollama": ollama,
        "toolchains": get_toolchain_readiness(),
        "supported_modes": ["pipeline", "optimize", "security"],
        "supported_languages": ["cpp", "c", "python", "javascript"],
    }
