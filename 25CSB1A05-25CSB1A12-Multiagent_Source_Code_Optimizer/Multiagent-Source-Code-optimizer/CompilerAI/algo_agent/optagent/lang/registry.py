"""Global registry of OptAgent language adapters."""
from __future__ import annotations

from typing import Any

from .base import LanguageAdapter
from .detect import detect_language, normalize_language
from .python_adapter import PythonAdapter

_ADAPTERS: dict[str, LanguageAdapter] = {}
_BUILTINS_LOADED = False


def register_adapter(adapter: LanguageAdapter) -> None:
    _ADAPTERS[adapter.id] = adapter


def _ensure_builtins() -> None:
    global _BUILTINS_LOADED
    if _BUILTINS_LOADED:
        return
    _BUILTINS_LOADED = True
    register_adapter(PythonAdapter())
    # Lazy-load optional language adapters as they are implemented
    for mod_path, cls_name in (
        ("optagent.lang.js.adapter", "JavaScriptAdapter"),
        ("optagent.lang.native.adapter_c", "CAdapter"),
        ("optagent.lang.native.adapter_cpp", "CppAdapter"),
    ):
        try:
            import importlib
            mod = importlib.import_module(mod_path)
            cls = getattr(mod, cls_name)
            register_adapter(cls())
        except ImportError:
            pass


def get_adapter(language: str = "python") -> LanguageAdapter:
    _ensure_builtins()
    lang_id = normalize_language(language)
    if lang_id not in _ADAPTERS:
        raise ValueError(
            f"Language adapter '{lang_id}' is not registered. Available: {sorted(_ADAPTERS)}"
        )
    return _ADAPTERS[lang_id]


def list_adapters() -> list[str]:
    _ensure_builtins()
    return sorted(_ADAPTERS.keys())


__all__ = ["get_adapter", "register_adapter", "list_adapters", "detect_language", "normalize_language"]
