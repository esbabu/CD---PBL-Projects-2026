from __future__ import annotations
import json
from enum import Enum
from typing import Any, Literal
from pydantic import BaseModel, Field, field_validator, model_validator


# ---------- contract vocabulary (downstream steps key off these enums) ----------
class Aspect(str, Enum):
    RETURN_VALUE = "return_value"
    RETURN_TYPE = "return_type"
    RETURN_ORDER = "return_order"
    FLOAT_EXACTNESS = "float_exactness"
    ARG_MUTATION = "arg_mutation"
    RETURN_ALIASING = "return_aliasing"
    STDOUT = "stdout"
    EXCEPTION_TYPE = "exception_type"
    EXCEPTION_MESSAGE = "exception_message"
    GLOBAL_STATE = "global_state"
    EXTERNAL_IO = "external_io"
    DETERMINISM = "determinism"
    SORT_STABILITY = "sort_stability"
    RECURSION_LIMIT = "recursion_limit"
    # Multi-language aspects (additive)
    MEMORY_SAFETY = "memory_safety"
    UNDEFINED_BEHAVIOR = "undefined_behavior"
    INTEGER_SEMANTICS = "integer_semantics"
    ABI_SIGNATURE = "abi_signature"
    RESOURCE_OWNERSHIP = "resource_ownership"
    ERRNO_STATE = "errno_state"
    THREAD_SAFETY = "thread_safety"
    ASYNC_SEMANTICS = "async_semantics"
    KEY_ENUMERATION_ORDER = "key_enumeration_order"
    PROTOTYPE_STATE = "prototype_state"
    SELF_STATE = "self_state"


class Level(str, Enum):
    MUST = "must_preserve"
    MAY = "may_change"


class Source(str, Enum):
    DEFAULT = "default"
    STATIC = "static"
    DYNAMIC = "dynamic"
    LLM = "llm"
    USER = "user"


class PreservationItem(BaseModel):
    aspect: Aspect
    level: Level
    applicable: bool
    rationale: str
    source: Source


class Constraints(BaseModel):
    allow_approximation: bool = False
    allow_parallelism: bool = False
    allow_native_extensions: bool = False
    allow_new_dependencies: bool = False
    optimize_for: Literal["time", "space", "balanced"] = "balanced"
    float_rel_tol: float | None = None      # None => bitwise float equality
    input_size_hint: str | None = None      # e.g. "n up to 1e5"
    notes: str | None = None


# ---------- static facts ----------
class EffectKind(str, Enum):
    PRINT = "print"
    INPUT = "input"
    FILE_IO = "file_io"
    NETWORK = "network"
    SUBPROCESS = "subprocess"
    RANDOM = "random"
    TIME = "time"
    ENV = "env"
    GLOBAL_READ = "global_read"
    GLOBAL_WRITE = "global_write"
    ARG_MUTATION = "arg_mutation"
    DYNAMIC_EXEC = "dynamic_exec"
    CONCURRENCY = "concurrency"


class Effect(BaseModel):
    kind: EffectKind
    line: int
    detail: str
    certainty: Literal["definite", "possible"] = "definite"


class Pattern(BaseModel):
    kind: str
    line: int
    in_loop: bool
    detail: str


class ParamInfo(BaseModel):
    name: str
    annotation: str | None = None
    default: str | None = None
    kind: Literal["positional", "kwonly", "vararg", "kwarg"] = "positional"


class CallSite(BaseModel):
    callee: str
    line: int
    arg_roots: list[str | None]


class FunctionFacts(BaseModel):
    name: str
    lineno: int
    end_lineno: int
    params: list[ParamInfo]
    returns_annotation: str | None = None
    docstring: str | None = None
    decorators: list[str] = []
    is_generator: bool = False
    is_async: bool = False
    is_recursive: bool = False
    in_recursive_cycle: bool = False
    branching_self_calls: int = 0
    callees_local: list[str] = []
    callees_external: list[str] = []
    call_sites: list[CallSite] = []
    effects: list[Effect] = []
    transitive_effect_kinds: list[EffectKind] = []
    mutated_params: list[str] = []
    reads_globals: list[str] = []
    raises: list[str] = []
    handled_exceptions: list[str] = []
    implicit_raises: list[str] = []
    loop_count: int = 0
    max_loop_depth: int = 0
    float_reasons: list[str] = []
    sort_uses: list[Pattern] = []
    unordered_iterations: list[Pattern] = []
    cost_patterns: list[Pattern] = []
    uses_hash_or_id: bool = False
    may_return_input_alias: bool = False
    extra: dict[str, Any] = Field(default_factory=dict)


class ModuleFacts(BaseModel):
    functions: dict[str, FunctionFacts]
    imports: dict[str, str]
    module_vars: list[str]
    mutable_module_vars: list[str]
    module_side_effects: list[str]
    root_functions: list[str]


# ---------- spec ----------
class ParamSpec(BaseModel):
    name: str
    type: str = ""
    description: str = ""
    constraints: str = ""


class _Lenient(BaseModel):
    """Small local models often emit null / bare strings where lists are expected."""

    @model_validator(mode="before")
    @classmethod
    def _coerce(cls, data):
        if not isinstance(data, dict):
            return data
        data = dict(data)
        for name, f in cls.model_fields.items():
            v, ann = data.get(name), str(f.annotation)
            if ann.startswith("list"):
                if v is None:
                    data[name] = []
                elif not isinstance(v, list):
                    data[name] = [v]
            elif ann in ("str", "<class 'str'>"):
                if v is None:
                    data[name] = ""
                elif isinstance(v, (list, dict)):
                    data[name] = json.dumps(v)
        return data


class SpecDraft(_Lenient):
    summary: str = ""
    parameters: list[ParamSpec] = []
    return_type: str = ""
    return_description: str = ""
    preconditions: list[str] = []
    postconditions: list[str] = []
    invariants: list[str] = []
    error_behavior: list[str] = []
    ordering_semantics: str = ""
    numeric_semantics: str = ""
    quirks: list[str] = []

    @field_validator("parameters", mode="before")
    @classmethod
    def _params(cls, v):
        return [{"name": x} if isinstance(x, str) else x for x in v]

    @field_validator("preconditions", "postconditions", "invariants",
                     "error_behavior", "quirks", mode="before")
    @classmethod
    def _strs(cls, v):
        return [x if isinstance(x, str) else json.dumps(x) for x in v]


class Spec(SpecDraft):
    entry_point: str = ""
    version: int = 1
    side_effects: list[str] = []                 # filled from static/dynamic facts, not the LLM
    determinism: Literal["deterministic", "nondeterministic", "unknown"] = "unknown"
    reconciliation_notes: list[str] = []


# ---------- dynamic execution ----------
class ExecRecord(BaseModel):
    origin: str                                   # llm | annotation | user
    args: list[Any]
    kwargs: dict[str, Any] = {}
    status: Literal["ok", "exception", "timeout", "crash", "load_error"]
    ret: Any = None                               # canonical-encoded (see canon.py)
    return_type: str | None = None
    exc_type: str | None = None
    exc_msg: str | None = None
    stdout: str = ""
    mutated_args: list[str] = []                  # "arg0", "kw:name"
    globals_changed: list[str] = []
    returns_input_alias: list[int] = []
    elapsed_s: float | None = None
    generator: bool = False
    nondeterministic_fields: list[str] = []       # differs across PYTHONHASHSEED runs


# ---------- validation ----------
class CaseCheck(BaseModel):
    args: Any
    predicted: str
    actual: str
    agree: bool


class RoundReport(BaseModel):
    spec_version: int
    checked: int
    score: float
    cases: list[CaseCheck]


class ValidationReport(BaseModel):
    status: Literal["validated", "partially_validated", "unvalidated", "skipped"] = "skipped"
    rounds: list[RoundReport] = []


class IntentBundle(BaseModel):
    schema_version: str = "1"
    language: str = "python"
    source_sha: str
    source_path: str
    entry_point: str
    source: str
    module_facts: ModuleFacts
    spec: Spec
    contract: list[PreservationItem]
    constraints: Constraints
    golden_seed: list[ExecRecord]
    validation: ValidationReport
    warnings: list[str] = []