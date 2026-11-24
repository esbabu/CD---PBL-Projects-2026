"""Cross-cutting compatibility tests: P1-P7 backward compat, encoding, sandbox guards."""
from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

from optagent.config import Settings
from optagent.lang.registry import get_adapter
from optagent.oracle.compare import Comparator
from optagent.oracle.schemas import Case, CaseResult, GoldenRecord, OracleBundle
from optagent.runtime import canon
from optagent.runtime.sandbox import Sandbox, SandboxError, SandboxProfile
from optagent.schemas import (
    Aspect,
    Constraints,
    FunctionFacts,
    IntentBundle,
    Level,
    ModuleFacts,
    PreservationItem,
    Source,
    Spec,
    ValidationReport,
)


def test_old_intent_json_loads_without_language_or_extra():
    """P1: Legacy IntentBundle JSON (no `language`, no `extra`) loads cleanly."""
    legacy = {
        "schema_version": "1",
        "source_sha": "deadbeef1234",
        "source_path": "old.py",
        "entry_point": "f",
        "source": "def f(x): return x\n",
        "module_facts": {
            "functions": {
                "f": {
                    "name": "f", "lineno": 1, "end_lineno": 1,
                    "params": [{"name": "x"}],
                }
            },
            "imports": {},
            "module_vars": [],
            "mutable_module_vars": [],
            "module_side_effects": [],
            "root_functions": ["f"],
        },
        "spec": {"summary": "identity", "entry_point": "f"},
        "contract": [],
        "constraints": {},
        "golden_seed": [],
        "validation": {"status": "skipped", "rounds": []},
    }
    b = IntentBundle.model_validate_json(json.dumps(legacy))
    assert b.language == "python"
    assert b.module_facts.functions["f"].extra == {}


def test_old_oracle_json_loads_without_new_fields():
    """P2: Legacy OracleBundle & CaseResult JSON load cleanly with None defaults."""
    legacy = {
        "schema_version": "2",
        "source_sha": "deadbeef1234",
        "entry_point": "f",
        "param_schema": {"args": [], "kwargs": {}},
        "cases": [],
        "golden": {
            "c1": {
                "case_id": "c1",
                "result": {"idx": 0, "status": "ok", "ret": 42},
                "unstable": [],
            }
        },
    }
    ob = OracleBundle.model_validate_json(json.dumps(legacy))
    assert ob.language == "python"
    r = ob.golden["c1"].result
    assert r.sanitizer is None
    assert r.signal is None
    assert r.build_log is None


def test_value_encoding_tags_passthrough():
    """Section 6: Known tags round-trip; unknown foreign tags pass through canon.decode untouched."""
    # Known tags
    assert math.isnan(canon.decode({"__float__": "nan"}))
    assert math.isinf(canon.decode({"__float__": "inf"}))
    assert math.copysign(1.0, canon.decode({"__float__": "-0"})) == -1.0
    assert canon.decode({"__tuple__": [1, 2]}) == (1, 2)
    assert canon.decode({"__bytes__": "deadbeef"}) == b"\xde\xad\xbe\xef"

    # Foreign language tags pass through canon.decode untouched
    for tag_val in (
        {"__undefined__": 1},
        {"__bigint__": "900719925474099312345"},
        {"__date__": 1700000000000},
        {"__regexp__": ["[a-z]+", "gi"]},
        {"__map__": [["a", 1], ["b", 2]]},
        {"__typed__": ["Int32Array", [1, 2, 3]]},
        {"__uset__": [3, 1, 2]},
        {"__udict__": [["b", 2], ["a", 1]]},
    ):
        assert canon.decode(tag_val) == tag_val


def test_native_docker_required_guard(monkeypatch):
    """Native code MUST refuse local sandbox unless OPT_ALLOW_LOCAL_NATIVE=1."""
    monkeypatch.delenv("OPT_ALLOW_LOCAL_NATIVE", raising=False)
    s = Settings(sandbox_backend="local", allow_local_native=False)
    c_profile = get_adapter("c").sandbox_profile({})
    cpp_profile = get_adapter("cpp").sandbox_profile({})

    with pytest.raises(SandboxError, match="Docker isolation is required"):
        Sandbox(s, backend="local", profile=c_profile)
    with pytest.raises(SandboxError, match="Docker isolation is required"):
        Sandbox(s, backend="local", profile=cpp_profile)

    # Explicitly allowing local native succeeds
    s_allow = Settings(sandbox_backend="local", allow_local_native=True)
    sb = Sandbox(s_allow, backend="local", profile=c_profile)
    assert sb.backend == "local"


def test_sandbox_build_failure_synthesizes_load_error(tmp_path):
    """P3: When a profile's build step fails, Sandbox synthesizes load_error with build_log."""
    src = tmp_path / "broken.c"
    src.write_text("int bad( { return ; }", encoding="utf-8")

    def fail_build(work, out, entry, s, docker):
        return False, "broken.c:1:10: error: expected parameter declarator"

    prof = SandboxProfile(
        target_name="target.c",
        needs_build=True,
        isolation_required=False,
        language="c",
        build_hook=fail_build,
    )
    sb = Sandbox(Settings(sandbox_backend="local"), backend="local", profile=prof)
    cases = [Case.make([1]), Case.make([2])]
    res = sb.run_batch(src, "bad", cases)
    assert len(res) == 2
    assert all(r.status == "load_error" for r in res)
    assert "expected parameter declarator" in (res[0].exc_msg or "")
    assert res[0].build_log == "broken.c:1:10: error: expected parameter declarator"


def test_comparator_python_unchanged_and_new_aspects():
    """P4: Comparator handles sanitizer/signal/new aspects when MUST and stays unchanged otherwise."""
    contract = [
        PreservationItem(aspect=Aspect.RETURN_VALUE, level=Level.MUST, applicable=True, rationale="", source=Source.DEFAULT),
        PreservationItem(aspect=Aspect.MEMORY_SAFETY, level=Level.MUST, applicable=True, rationale="", source=Source.DEFAULT),
        PreservationItem(aspect=Aspect.UNDEFINED_BEHAVIOR, level=Level.MUST, applicable=True, rationale="", source=Source.DEFAULT),
        PreservationItem(aspect=Aspect.KEY_ENUMERATION_ORDER, level=Level.MUST, applicable=True, rationale="", source=Source.DEFAULT),
        PreservationItem(aspect=Aspect.ASYNC_SEMANTICS, level=Level.MUST, applicable=True, rationale="", source=Source.DEFAULT),
        PreservationItem(aspect=Aspect.PROTOTYPE_STATE, level=Level.MUST, applicable=True, rationale="", source=Source.DEFAULT),
    ]
    cmp = Comparator(contract, Constraints())
    case = Case.make([[1, 2]])
    g = GoldenRecord(case_id=case.id, result=CaseResult(status="ok", ret={"__dict__": [["2", 1], ["1", 1]]}, return_type="Object"))

    # Key enumeration order violation
    c_key = CaseResult(status="ok", ret={"__dict__": [["1", 1], ["2", 1]]}, return_type="Object")
    vs = cmp.compare(case, g, c_key)
    assert any(v.aspect == "key_enumeration_order" for v in vs)

    # ASan memory safety violation
    c_asan = CaseResult(status="ok", ret={"__dict__": [["2", 1], ["1", 1]]}, return_type="Object",
                        sanitizer="ERROR: AddressSanitizer: heap-buffer-overflow")
    vs = cmp.compare(case, g, c_asan)
    assert any(v.aspect == "memory_safety" for v in vs)

    # UBSan undefined behavior violation
    c_ub = CaseResult(status="ok", ret={"__dict__": [["2", 1], ["1", 1]]}, return_type="Object",
                      sanitizer="runtime error: signed integer overflow")
    vs = cmp.compare(case, g, c_ub)
    assert any(v.aspect == "undefined_behavior" for v in vs)

    # Async Promise mismatch
    c_async = CaseResult(status="ok", ret={"__dict__": [["2", 1], ["1", 1]]}, return_type="Promise<Object>")
    vs = cmp.compare(case, g, c_async)
    assert any(v.aspect == "async_semantics" for v in vs)

    # Prototype mutation
    c_proto = CaseResult(status="ok", ret={"__dict__": [["2", 1], ["1", 1]]}, return_type="Object",
                         glob={"__prototype__": "polluted"})
    vs = cmp.compare(case, g, c_proto)
    assert any(v.aspect == "prototype_state" for v in vs)
