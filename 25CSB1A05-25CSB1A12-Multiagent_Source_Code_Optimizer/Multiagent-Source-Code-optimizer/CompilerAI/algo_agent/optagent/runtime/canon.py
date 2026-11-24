from __future__ import annotations

import dataclasses
import hashlib
import json
import math
import re
from typing import Any

_ADDR_RE = re.compile(r"0x[0-9a-fA-F]+")


def _normalize_repr(text: str) -> str:
    return _ADDR_RE.sub("0xADDR", text)[:200]


def encode(v: Any, _d: int = 0) -> Any:
    if _d > 60:
        return {"__object__": {"type": type(v).__name__, "repr": "<too deep>"}}
    if v is None or isinstance(v, (bool, str)):
        return v
    if isinstance(v, int):
        return v
    if isinstance(v, float):
        if math.isnan(v):
            return {"__float__": "nan"}
        if math.isinf(v):
            return {"__float__": "inf" if v > 0 else "-inf"}
        return v
    if isinstance(v, bytes):
        return {"__bytes__": v.hex()}
    # Namedtuple structural encoding before plain tuple
    if isinstance(v, tuple) and hasattr(v, "_fields") and isinstance(getattr(v, "_fields"), tuple):
        return {
            "__obj__": [
                type(v).__name__,
                {k: encode(getattr(v, k), _d + 1) for k in v._fields},
            ]
        }
    if isinstance(v, tuple):
        return {"__tuple__": [encode(x, _d + 1) for x in v]}
    if isinstance(v, list):
        return [encode(x, _d + 1) for x in v]
    if isinstance(v, (set, frozenset)):
        items = [encode(x, _d + 1) for x in v]
        items.sort(key=lambda x: json.dumps(x, sort_keys=True))
        return {"__set__": items}
    if isinstance(v, dict):  # insertion order is preserved: it is observable behaviour
        return {"__dict__": [[encode(k, _d + 1), encode(x, _d + 1)] for k, x in v.items()]}

    # numpy.ndarray tag (without hard-importing numpy)
    t = type(v)
    if t.__module__ == "numpy" and t.__name__ == "ndarray":
        try:
            return {
                "__ndarray__": {
                    "dtype": str(v.dtype),
                    "shape": list(v.shape),
                    "data": encode(v.tolist(), _d + 1),
                }
            }
        except Exception:
            pass

    # Dataclasses structural encoding
    if dataclasses.is_dataclass(v) and not isinstance(v, type):
        return {
            "__obj__": [
                t.__name__,
                {f.name: encode(getattr(v, f.name), _d + 1) for f in dataclasses.fields(v)},
            ]
        }

    # Custom user objects with __dict__ or __slots__
    if t.__module__ not in ("builtins", "types") and (hasattr(v, "__dict__") or hasattr(t, "__slots__")):
        try:
            if hasattr(v, "__dict__"):
                fields = {k: encode(val, _d + 1) for k, val in vars(v).items() if not k.startswith("__")}
            else:
                slots = t.__slots__ if isinstance(t.__slots__, (list, tuple)) else (t.__slots__,)
                fields = {s: encode(getattr(v, s), _d + 1) for s in slots if hasattr(v, s)}
            return {"__obj__": [t.__name__, fields]}
        except Exception:
            pass

    return {
        "__object__": {
            "type": t.__module__ + "." + t.__qualname__,
            "repr": _normalize_repr(repr(v)),
        }
    }


def decode(v: Any, namespace: dict[str, Any] | None = None) -> Any:
    """Accepts canonical encoding AND natural JSON (what LLMs write).

    When `namespace` (e.g. target module `__dict__`) is provided, `__obj__` tags
    are re-instantiated against the matching class.
    """
    if isinstance(v, list):
        return [decode(x, namespace) for x in v]
    if isinstance(v, dict):
        if len(v) == 1:
            (k, val), = v.items()
            if k == "__tuple__":
                return tuple(decode(x, namespace) for x in val)
            if k == "__set__":
                return {_hashable(decode(x, namespace)) for x in val}
            if k == "__float__":
                return float(val)
            if k == "__bytes__":
                return bytes.fromhex(val)
            if k == "__dict__":
                return {_hashable(decode(a, namespace)): decode(b, namespace) for a, b in val}
            if k == "__ndarray__" and isinstance(val, dict):
                try:
                    import numpy as np  # type: ignore

                    return np.array(decode(val.get("data", []), namespace), dtype=val.get("dtype"))
                except Exception:
                    return decode(val.get("data", []), namespace)
            if k == "__obj__" and isinstance(val, list) and len(val) == 2:
                cls_name, raw_fields = val
                dec_fields = {fk: decode(fv, namespace) for fk, fv in (raw_fields or {}).items()}
                if namespace:
                    cls = namespace.get(cls_name) or namespace.get(cls_name.split(".")[-1])
                    if isinstance(cls, type):
                        try:
                            return cls(**dec_fields)
                        except Exception:
                            try:
                                inst = cls.__new__(cls)
                                for fk, fv in dec_fields.items():
                                    setattr(inst, fk, fv)
                                return inst
                            except Exception:
                                pass
                return dec_fields
        return {k: decode(x, namespace) for k, x in v.items()}
    return v


def _hashable(x: Any) -> Any:
    if isinstance(x, list):
        return tuple(_hashable(i) for i in x)
    return x


def loose_equal(a: Any, b: Any, rel_tol: float = 1e-9) -> bool:
    """Lenient comparison used ONLY for spec validation (list~tuple, int~float within tol)."""
    if isinstance(a, bool) or isinstance(b, bool):
        return type(a) is type(b) and a == b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        if isinstance(a, float) or isinstance(b, float):
            if math.isnan(a) and math.isnan(b):
                return True
            return math.isclose(a, b, rel_tol=rel_tol, abs_tol=rel_tol)
        return a == b
    if isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        return len(a) == len(b) and all(loose_equal(x, y, rel_tol) for x, y in zip(a, b))
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(loose_equal(a[k], b[k], rel_tol) for k in a)
    return a == b


def as_multiset(enc):
    """Order-insensitive canonical form of the TOP level of an encoded value."""
    def key(x):
        return json.dumps(x, sort_keys=True)

    if isinstance(enc, list):
        return sorted(enc, key=key)
    if isinstance(enc, dict) and len(enc) == 1:
        (k, v), = enc.items()
        if k in ("__tuple__", "__set__", "__dict__"):
            return {k: sorted(v, key=key)}
    return enc


def digest(enc, multiset: bool = False) -> str:
    if multiset:
        enc = as_multiset(enc)
    return hashlib.sha1(json.dumps(enc, sort_keys=True).encode()).hexdigest()[:16]
