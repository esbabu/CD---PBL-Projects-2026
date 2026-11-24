"""Phase 0 tests: language adapter registry, detection, capabilities, and metadata."""
from __future__ import annotations

import pytest

from optagent.lang import (
    LanguageAdapter,
    detect_language,
    get_adapter,
    list_adapters,
)
from optagent.lang.pipeline_hooks import cap_tier_by_capability, list_language_metadata
from optagent.oracle.oracle import source_sha


def test_all_four_adapters_registered():
    langs = list_adapters()
    assert set(langs) >= {"python", "javascript", "c", "cpp"}
    for lid in ("python", "javascript", "c", "cpp"):
        ad = get_adapter(lid)
        assert isinstance(ad, LanguageAdapter)
        assert ad.id == lid


def test_aliases():
    assert get_adapter("py").id == "python"
    assert get_adapter("js").id == "javascript"
    assert get_adapter("node").id == "javascript"
    assert get_adapter("c11").id == "c"
    assert get_adapter("c++").id == "cpp"
    assert get_adapter("cxx").id == "cpp"


def test_detect_language_extensions():
    assert detect_language("foo.py") == "python"
    assert detect_language("foo.js") == "javascript"
    assert detect_language("foo.mjs") == "javascript"
    assert detect_language("foo.cjs") == "javascript"
    assert detect_language("foo.c") == "c"
    assert detect_language("foo.cpp") == "cpp"
    assert detect_language("foo.cc") == "cpp"
    assert detect_language("foo.cxx") == "cpp"
    assert detect_language("foo.hpp") == "cpp"


def test_detect_language_header_ambiguous():
    with pytest.raises(ValueError, match="ambiguous"):
        detect_language("util.h")
    # Explicit request always wins
    assert detect_language("util.h", requested="c") == "c"
    assert detect_language("util.h", requested="cpp") == "cpp"
    assert detect_language("foo.py", requested="javascript") == "javascript"


def test_capabilities_and_evidence_ceilings():
    py = get_adapter("python")
    js = get_adapter("javascript")
    c = get_adapter("c")
    cpp = get_adapter("cpp")

    assert py.caps.max_evidence_tier == "T4"
    assert py.caps.isolation_required is False
    assert py.caps.perturbation == "hashseed"

    assert js.caps.max_evidence_tier == "T2"
    assert js.caps.isolation_required is False
    assert js.caps.perturbation == "prng_seed"

    assert c.caps.max_evidence_tier == "T3"
    assert c.caps.isolation_required is True
    assert c.caps.static_types is True
    assert c.caps.perturbation == "malloc_perturb"

    assert cpp.caps.max_evidence_tier == "T3"
    assert cpp.caps.isolation_required is True
    assert cpp.caps.static_types is True
    assert cpp.caps.perturbation == "malloc_perturb"

    assert cap_tier_by_capability("T4", "T2")[0] == "T2"
    assert cap_tier_by_capability("T4", "T3")[0] == "T3"
    assert cap_tier_by_capability("T2", "T3")[0] == "T2"


def test_source_sha_backward_compat_and_salting():
    src = "def f(x): return x\n"
    import hashlib
    expected_py = hashlib.sha256(src.encode()).hexdigest()[:12]
    assert source_sha(src) == expected_py
    assert source_sha(src, "python") == expected_py
    assert source_sha(src, "javascript") != expected_py
    assert source_sha(src, "c") != source_sha(src, "cpp")


def test_language_metadata_and_security_profiles():
    meta = {m["id"]: m for m in list_language_metadata()}
    assert set(meta.keys()) >= {"python", "javascript", "c", "cpp"}
    assert "eslint" in meta["javascript"]["security_profile"]["static_tools"]
    assert "cppcheck" in meta["c"]["security_profile"]["static_tools"]
    assert meta["cpp"]["capabilities"]["isolation_required"] is True
    assert "memory_safety" in meta["c"]["aspects"]
    assert "key_enumeration_order" in meta["javascript"]["aspects"]
