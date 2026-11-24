"""C11 and C++17 type system, marshalling descriptors, ParamSchema & seed derivation."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from ...oracle.schema_infer import ParamSchema, VS as ValSchema
from ...schemas import FunctionFacts

_LEN_NAMES = {"n", "len", "length", "size", "sz", "count", "cnt", "num"}

_INT_TYPES = {
    "int", "short", "long", "long long", "signed", "signed int", "signed long",
    "signed long long", "unsigned", "unsigned int", "unsigned short", "unsigned long",
    "unsigned long long", "size_t", "ssize_t", "ptrdiff_t",
    "int8_t", "int16_t", "int32_t", "int64_t",
    "uint8_t", "uint16_t", "uint32_t", "uint64_t",
    "char", "signed char", "unsigned char",
}
_FLOAT_TYPES = {"float", "double", "long double"}
_UNSUPPORTED_TOKENS = ("void*", "void *", "union ", "std::variant", "std::any")


@dataclass
class NativeType:
    raw: str
    kind: str                 # int | float | bool | char | cstr | ptr_array | out_scalar | string | vector | array | pair | tuple | set | map | uset | umap | optional | void | unsupported
    elem: "NativeType | None" = None
    val_type: "NativeType | None" = None   # for map/pair
    elem_types: list["NativeType"] = field(default_factory=list)  # for tuple
    is_const: bool = False
    is_ref: bool = False
    is_rvalue_ref: bool = False
    fixed_size: int | None = None
    c_type: str = "int"


@dataclass
class ParamBinding:
    name: str
    index: int
    ntype: NativeType
    length_param: str | None = None      # for C arrays: name of companion length parameter
    length_index: int | None = None
    is_length_for: str | None = None     # set on the companion length param itself
    is_out_param: bool = False
    out_length: int = 2                  # default buffer length for out array pointers


@dataclass
class FunctionSignature:
    name: str
    language: str                        # "c" | "cpp"
    return_type: NativeType
    params: list[ParamBinding]
    template_params: list[str] = field(default_factory=list)
    globals_list: list[tuple[str, NativeType]] = field(default_factory=list)


def _split_top_level(s: str, sep: str = ",") -> list[str]:
    parts, cur, depth = [], [], 0
    for ch in s:
        if ch in "<([":
            depth += 1
        elif ch in ">)]":
            depth = max(0, depth - 1)
        if ch == sep and depth == 0:
            parts.append("".join(cur).strip())
            cur = []
        else:
            cur.append(ch)
    if cur:
        parts.append("".join(cur).strip())
    return [p for p in parts if p]


def parse_native_type(raw: str, language: str = "c") -> NativeType:
    """Parse a C11 or C++17 type string into a structured NativeType."""
    s = " ".join(raw.strip().split())
    if not s:
        return NativeType(raw=raw, kind="int", c_type="int")

    for bad in _UNSUPPORTED_TOKENS:
        if bad in s:
            return NativeType(raw=raw, kind="unsupported", c_type=s)

    is_rval = s.endswith("&&")
    is_ref = (not is_rval) and s.endswith("&")
    core = s[:-2].strip() if is_rval else (s[:-1].strip() if is_ref else s)

    is_const = False
    if core.startswith("const "):
        is_const = True
        core = core[6:].strip()
    elif core.endswith(" const"):
        is_const = True
        core = core[:-6].strip()

    if core == "void":
        return NativeType(raw=raw, kind="void", is_const=is_const, c_type="void")
    if core == "bool" or core == "_Bool":
        return NativeType(raw=raw, kind="bool", is_const=is_const, is_ref=is_ref, is_rvalue_ref=is_rval, c_type="bool")
    if core in ("const char*", "const char *", "char const*", "char const *") or (is_const and core in ("char*", "char *")):
        return NativeType(raw=raw, kind="cstr", is_const=True, c_type="const char*")
    if core in ("char*", "char *"):
        return NativeType(raw=raw, kind="cstr", is_const=False, c_type="char*")

    # C++ STL types
    if language == "cpp":
        if core in ("std::string", "string", "std::string_view", "string_view"):
            return NativeType(raw=raw, kind="string", is_const=is_const, is_ref=is_ref, is_rvalue_ref=is_rval, c_type=core)
        m = re.match(r"^(?:std::)?vector\s*<(.+)>$", core)
        if m:
            inner = parse_native_type(m.group(1), "cpp")
            return NativeType(raw=raw, kind="vector", elem=inner, is_const=is_const, is_ref=is_ref, is_rvalue_ref=is_rval, c_type=core)
        m = re.match(r"^(?:std::)?array\s*<(.+)>$", core)
        if m:
            args = _split_top_level(m.group(1))
            if len(args) == 2 and args[1].isdigit():
                inner = parse_native_type(args[0], "cpp")
                return NativeType(raw=raw, kind="array", elem=inner, fixed_size=int(args[1]), is_const=is_const, is_ref=is_ref, is_rvalue_ref=is_rval, c_type=core)
        m = re.match(r"^(?:std::)?pair\s*<(.+)>$", core)
        if m:
            args = _split_top_level(m.group(1))
            if len(args) == 2:
                return NativeType(
                    raw=raw, kind="pair",
                    elem=parse_native_type(args[0], "cpp"),
                    val_type=parse_native_type(args[1], "cpp"),
                    is_const=is_const, is_ref=is_ref, is_rvalue_ref=is_rval, c_type=core,
                )
        m = re.match(r"^(?:std::)?tuple\s*<(.+)>$", core)
        if m:
            args = _split_top_level(m.group(1))
            return NativeType(
                raw=raw, kind="tuple",
                elem_types=[parse_native_type(a, "cpp") for a in args],
                is_const=is_const, is_ref=is_ref, is_rvalue_ref=is_rval, c_type=core,
            )
        m = re.match(r"^(?:std::)?set\s*<(.+)>$", core)
        if m:
            return NativeType(raw=raw, kind="set", elem=parse_native_type(m.group(1), "cpp"), is_const=is_const, is_ref=is_ref, is_rvalue_ref=is_rval, c_type=core)
        m = re.match(r"^(?:std::)?unordered_set\s*<(.+)>$", core)
        if m:
            return NativeType(raw=raw, kind="uset", elem=parse_native_type(m.group(1), "cpp"), is_const=is_const, is_ref=is_ref, is_rvalue_ref=is_rval, c_type=core)
        m = re.match(r"^(?:std::)?map\s*<(.+)>$", core)
        if m:
            args = _split_top_level(m.group(1))
            if len(args) >= 2:
                return NativeType(
                    raw=raw, kind="map",
                    elem=parse_native_type(args[0], "cpp"),
                    val_type=parse_native_type(args[1], "cpp"),
                    is_const=is_const, is_ref=is_ref, is_rvalue_ref=is_rval, c_type=core,
                )
        m = re.match(r"^(?:std::)?unordered_map\s*<(.+)>$", core)
        if m:
            args = _split_top_level(m.group(1))
            if len(args) >= 2:
                return NativeType(
                    raw=raw, kind="umap",
                    elem=parse_native_type(args[0], "cpp"),
                    val_type=parse_native_type(args[1], "cpp"),
                    is_const=is_const, is_ref=is_ref, is_rvalue_ref=is_rval, c_type=core,
                )
        m = re.match(r"^(?:std::)?optional\s*<(.+)>$", core)
        if m:
            return NativeType(raw=raw, kind="optional", elem=parse_native_type(m.group(1), "cpp"), is_const=is_const, is_ref=is_ref, is_rvalue_ref=is_rval, c_type=core)

    # C pointers and arrays: `T*`, `const T*`, `T[N]`
    m_arr = re.match(r"^(.+?)\s*\[\s*(\d*)\s*\]$", core)
    if m_arr:
        base = parse_native_type(m_arr.group(1), language)
        sz = int(m_arr.group(2)) if m_arr.group(2) else None
        return NativeType(raw=raw, kind="ptr_array", elem=base, is_const=is_const, fixed_size=sz, c_type=f"{base.c_type}*")

    if core.endswith("*"):
        base_str = core[:-1].strip()
        base_const = is_const or base_str.startswith("const ")
        base = parse_native_type(base_str, language)
        if base.c_type == "char":
            return NativeType(raw=raw, kind="cstr", is_const=base_const, c_type="const char*" if base_const else "char*")
        return NativeType(raw=raw, kind="ptr_array", elem=base, is_const=base_const, c_type=f"{'const ' if base_const else ''}{base.c_type}*")

    if core in _FLOAT_TYPES:
        return NativeType(raw=raw, kind="float", is_const=is_const, is_ref=is_ref, is_rvalue_ref=is_rval, c_type=core)
    if core in _INT_TYPES or core.startswith("enum "):
        return NativeType(raw=raw, kind="int", is_const=is_const, is_ref=is_ref, is_rvalue_ref=is_rval, c_type=core)

    return NativeType(raw=raw, kind="unsupported", is_const=is_const, is_ref=is_ref, is_rvalue_ref=is_rval, c_type=core)


def build_signature(fn: FunctionFacts, language: str, hints: dict[str, Any] | None = None) -> FunctionSignature:
    """Construct a FunctionSignature with pointer-length pairing and out-param hints."""
    hints = hints or {}
    param_hints: dict[str, Any] = hints.get("params") or {}
    ret_type = parse_native_type(fn.returns_annotation or "int", language)

    bindings: list[ParamBinding] = []
    for idx, p in enumerate(fn.params):
        nt = parse_native_type(p.annotation or "int", language)
        ph = param_hints.get(p.name) or {}
        if ph.get("array_of"):
            nt = NativeType(
                raw=p.annotation or f"{ph['array_of']}*",
                kind="ptr_array",
                elem=parse_native_type(ph["array_of"], language),
                is_const=nt.is_const,
                c_type=nt.c_type,
            )
        is_out = bool(ph.get("out_param")) or (
            nt.kind == "ptr_array" and not nt.is_const and p.name.lower() in ("out", "res", "result", "dst", "output")
        )
        b = ParamBinding(
            name=p.name,
            index=idx,
            ntype=nt,
            length_param=ph.get("length_param"),
            is_out_param=is_out,
            out_length=int(ph.get("out_length", 2)),
        )
        bindings.append(b)

    name_to_idx = {b.name: b.index for b in bindings}
    # Pair C pointer arrays with adjacent length params (`n`, `len`, `size`, `count`)
    for i, b in enumerate(bindings):
        if b.ntype.kind != "ptr_array":
            continue
        if b.length_param and b.length_param in name_to_idx:
            li = name_to_idx[b.length_param]
            b.length_index = li
            bindings[li].is_length_for = b.name
            continue
        if b.is_out_param:
            continue
        if i + 1 < len(bindings):
            nxt = bindings[i + 1]
            if nxt.ntype.kind == "int" and nxt.name.lower() in _LEN_NAMES and not nxt.is_length_for:
                b.length_param = nxt.name
                b.length_index = nxt.index
                nxt.is_length_for = b.name
        elif i - 1 >= 0:
            prev = bindings[i - 1]
            if prev.ntype.kind == "int" and prev.name.lower() in _LEN_NAMES and not prev.is_length_for:
                b.length_param = prev.name
                b.length_index = prev.index
                prev.is_length_for = b.name

    return FunctionSignature(
        name=fn.name,
        language=language,
        return_type=ret_type,
        params=bindings,
        template_params=list(fn.extra.get("template_params") or []),
    )


def native_type_to_valschema(nt: NativeType) -> ValSchema:
    """Convert a NativeType to OptAgent's host-side ValSchema for generation."""
    if nt.kind == "int":
        return ValSchema(kind="int", lo=-100, hi=100)
    if nt.kind == "float":
        return ValSchema(kind="float", lo=-100.0, hi=100.0)
    if nt.kind == "bool":
        return ValSchema(kind="bool")
    if nt.kind in ("cstr", "string"):
        return ValSchema(kind="str")
    if nt.kind in ("ptr_array", "vector", "array"):
        elem = native_type_to_valschema(nt.elem) if nt.elem else ValSchema(kind="int", lo=-50, hi=50)
        mx = nt.fixed_size if nt.fixed_size is not None else 20
        mn = nt.fixed_size if nt.fixed_size is not None else 0
        return ValSchema(kind="list", elem=elem, min_len=mn, max_len=mx)
    if nt.kind in ("set", "uset"):
        elem = native_type_to_valschema(nt.elem) if nt.elem else ValSchema(kind="int", lo=-50, hi=50)
        return ValSchema(kind="set", elem=elem, min_len=0, max_len=15)
    if nt.kind in ("map", "umap"):
        k = native_type_to_valschema(nt.elem) if nt.elem else ValSchema(kind="str")
        v = native_type_to_valschema(nt.val_type) if nt.val_type else ValSchema(kind="int", lo=-50, hi=50)
        return ValSchema(kind="dict", key=k, val=v, min_len=0, max_len=15)
    return ValSchema(kind="int", lo=-50, hi=50)


def signature_to_param_schema(sig: FunctionSignature) -> ParamSchema:
    """Derive host-side ParamSchema for visible call arguments (excluding auto-bound C length params)."""
    args: list[ValSchema] = []
    for b in sig.params:
        if b.is_length_for or b.is_out_param:
            continue
        args.append(native_type_to_valschema(b.ntype))
    return ParamSchema(args=args, kwargs={})


def seed_inputs_for_signature(sig: FunctionSignature) -> list[dict[str, Any]]:
    """Generate type-derived seed inputs including boundary values (0, negatives, empty, duplicates)."""
    visible = [b for b in sig.params if not b.is_length_for and not b.is_out_param]
    if not visible:
        return [{"args": [], "kwargs": {}}]

    def samples_for(nt: NativeType) -> list[Any]:
        if nt.kind == "int":
            return [9, 0, -5, 6, 42]
        if nt.kind == "float":
            return [1.5, 0.0, -2.5, 3.14159, 100.0]
        if nt.kind == "bool":
            return [True, False, True, False, True]
        if nt.kind in ("cstr", "string"):
            return ["hello", "", "ababa", "foo", "test123"]
        if nt.kind in ("ptr_array", "vector", "array"):
            ek = nt.elem.kind if nt.elem else "int"
            if ek in ("cstr", "string"):
                return [["a", "b", "a", "c"], [], ["x", "y", "x", "y", "z"], ["one"], ["b", "a", "b", "a"]]
            if ek == "float":
                return [[1.0, 2.5, 3.5], [], [0.0, -1.0], [5.0, 5.0], [1.1, 2.2, 3.3]]
            return [[2, 7, 11, 15], [], [3, 3], [1, 1, 2], [-3, 4, 3, 90]]
        if nt.kind in ("set", "uset"):
            return [[1, 2, 3], [], [5]]
        if nt.kind in ("map", "umap"):
            return [{"a": 1, "b": 2}, {}, {"x": 10}]
        return [0, 1, -1]

    cols = [samples_for(b.ntype) for b in visible]
    n = min(5, max(len(c) for c in cols))
    return [{"args": [c[i % len(c)] for c in cols], "kwargs": {}} for i in range(n)]
