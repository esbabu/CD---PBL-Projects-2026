from __future__ import annotations
import json
import math
import hashlib
from ..runtime import canon
from ..schemas import Constraints, Level, PreservationItem
from .schemas import Case, CaseResult, GoldenRecord, ScalePoint, Violation


def _short(x, n: int = 220) -> str:
    s = json.dumps(x, default=str)
    return s if len(s) <= n else s[:n] + "…"


def eq(a, b, tol) -> bool:
    """Strict structural equality on canonical encodings: 1 != 1.0 != True, [] != (), -0.0 != 0.0."""
    ta, tb = type(a), type(b)
    if ta is not tb:
        return False
    if ta is float:
        if a == b:
            return tol is not None or a != 0 or math.copysign(1, a) == math.copysign(1, b)
        return tol is not None and math.isclose(a, b, rel_tol=tol, abs_tol=tol)
    if ta is list:
        return len(a) == len(b) and all(eq(x, y, tol) for x, y in zip(a, b))
    if ta is dict:
        return a.keys() == b.keys() and all(eq(a[k], b[k], tol) for k in a)
    return a == b


class Comparator:
    def __init__(self, contract: list[PreservationItem], constraints: Constraints, strict_probes: bool = False):
        self.items = {it.aspect.value: it for it in contract}
        self.strict_probes = strict_probes
        tol = constraints.float_rel_tol
        self.tol = tol if tol is not None else (None if self.must("float_exactness") else 1e-9)

    def must(self, aspect: str) -> bool:
        it = self.items.get(aspect)
        return it is not None and it.level == Level.MUST

    # ------------------------------------------------------------------
    def compare(self, case: Case, g: GoldenRecord, c: CaseResult,
                c_seed1: CaseResult | None = None) -> list[Violation]:
        vs = self._cmp(g.result, g.unstable, c)
        if vs and g.alt is not None and "ret" in g.unstable and not self._cmp(g.alt, g.unstable, c):
            vs = []
        if c_seed1 is not None and self.must("determinism") and c.status in ("ok", "exception"):
            for f in ("ret", "stdout", "exc_type", "status"):
                if f not in g.unstable and getattr(c, f) != getattr(c_seed1, f):
                    vs.append(Violation(aspect="determinism",
                                        detail=f"candidate '{f}' changes with PYTHONHASHSEED; original is stable",
                                        expected=_short(getattr(c, f)), actual=_short(getattr(c_seed1, f))))
                    break
        if case.kind == "probe" and not self.strict_probes:
            for v in vs:
                v.severity = "warn"
        return vs

    def _cmp(self, g: CaseResult, unstable: list[str], c: CaseResult) -> list[Violation]:
        V = Violation
        out: list[V] = []
        if "status" in unstable:
            return out
        # Sanitizer / memory-safety / UB checks (native languages; no-op when sanitizer is None)
        if c.sanitizer and not g.sanitizer:
            low = c.sanitizer.lower()
            is_ub = ("undefinedbehavior" in low or "ubsan" in low or "runtime error:" in low)
            if is_ub and self.must("undefined_behavior"):
                return [V(aspect="undefined_behavior", detail=f"candidate triggered UBSan: {c.sanitizer[:200]}",
                          expected="no UB", actual=c.sanitizer[:200])]
            if self.must("memory_safety") or not is_ub:
                aspect = "undefined_behavior" if is_ub else "memory_safety"
                return [V(aspect=aspect, detail=f"candidate sanitizer report: {c.sanitizer[:200]}",
                          expected="sanitizer clean", actual=c.sanitizer[:200])]
        if c.status in ("timeout", "crash", "load_error"):
            if c.status == "crash" and c.signal and self.must("memory_safety") and c.signal in ("SIGSEGV", "SIGBUS", "SIGABRT"):
                if not (g.status == "crash" and g.signal == c.signal):
                    return [V(aspect="memory_safety",
                              detail=f"candidate crashed with signal {c.signal}" + (f": {c.exc_msg}" if c.exc_msg else ""),
                              expected=g.status, actual=f"{c.status} ({c.signal})")]
            sig_info = f" ({c.signal})" if c.signal else ""
            return [V(aspect="return_value", detail=f"candidate {c.status}{sig_info}" + (f": {c.exc_msg}" if c.exc_msg else ""),
                      expected=g.status, actual=c.status)]
        if g.status == "crash" and g.signal == "SIGSEGV" and not self.must("recursion_limit"):
            return out
        if g.status not in ("ok", "exception"):
            return out
        if g.status == "exception" and g.exc_type in ("RecursionError", "RangeError") and not self.must("recursion_limit"):
            return out

        if g.status != c.status:
            return [V(aspect="return_value",
                      detail="original raises but candidate returns" if g.status == "exception"
                      else f"original returns but candidate raises {c.exc_type}: {c.exc_msg}",
                      expected=f"{g.status} {g.exc_type or ''}", actual=f"{c.status} {c.exc_type or ''}")]

        if g.status == "exception":
            if self.must("exception_type") and g.exc_type != c.exc_type:
                out.append(V(aspect="exception_type", detail="different exception type",
                             expected=g.exc_type or "", actual=c.exc_type or ""))
            elif self.must("exception_message") and g.exc_msg != c.exc_msg:
                out.append(V(aspect="exception_message", detail="different exception message",
                             expected=_short(g.exc_msg), actual=_short(c.exc_msg)))
        else:
            v = self._ret(g, c, unstable)
            if v:
                out.append(v)

        if self.must("arg_mutation") and "mut" not in unstable and not eq(g.mut, c.mut, self.tol):
            out.append(V(aspect="arg_mutation",
                         detail=f"inputs mutated differently (original: {sorted(g.mut)}, candidate: {sorted(c.mut)})",
                         expected=_short(g.mut), actual=_short(c.mut)))
        if self.must("stdout") and "stdout" not in unstable and g.stdout != c.stdout:
            out.append(V(aspect="stdout", detail="printed output differs",
                         expected=_short(g.stdout), actual=_short(c.stdout)))
        if self.must("global_state") and "glob" not in unstable and not eq(g.glob, c.glob, None):
            out.append(V(aspect="global_state", detail="module-level state differs after the call",
                         expected=_short(g.glob), actual=_short(c.glob)))
        if self.must("prototype_state") and "glob" not in unstable:
            gp, cp = g.glob.get("__prototype__"), c.glob.get("__prototype__")
            if gp != cp:
                out.append(V(aspect="prototype_state", detail="prototype or global intrinsic state mutated",
                             expected=_short(gp), actual=_short(cp)))
        if self.must("errno_state") and "glob" not in unstable:
            ge, ce = g.glob.get("__errno__"), c.glob.get("__errno__")
            if ge != ce:
                out.append(V(aspect="errno_state", detail="errno differs after call",
                             expected=_short(ge), actual=_short(ce)))
        if g.alias != c.alias:
            if self.must("return_aliasing"):
                out.append(V(aspect="return_aliasing", detail="identity of returned object differs",
                             expected=str(g.alias), actual=str(c.alias)))
            elif c.alias and not g.alias:
                out.append(V(aspect="return_aliasing", severity="warn",
                             detail="candidate returns one of its inputs; original returns a fresh object",
                             expected="fresh object", actual=f"alias of arg {c.alias}"))
        new_props = [p for p in c.prop_failures if p not in g.prop_failures]
        for p in new_props:
            out.append(V(aspect=f"property:{p}", detail=f"property {p} violated", expected="holds", actual="violated"))
        return out

    def _ret(self, g: CaseResult, c: CaseResult, unstable: list[str]) -> Violation | None:
        V = Violation
        if self.must("async_semantics"):
            g_async = bool(g.return_type and "Promise" in g.return_type)
            c_async = bool(c.return_type and "Promise" in c.return_type)
            if g_async != c_async:
                return V(aspect="async_semantics", detail="async/Promise semantics differ",
                         expected=g.return_type or "", actual=c.return_type or "")
        if g.return_type != c.return_type and self.must("return_type"):
            return V(aspect="return_type", detail="return type differs",
                     expected=g.return_type or "", actual=c.return_type or "")
        if eq(g.ret, c.ret, self.tol):
            return None
        # Check key enumeration order for dicts/maps (JS / C++ ordered maps)
        if self.must("key_enumeration_order") and isinstance(g.ret, dict) and isinstance(c.ret, dict):
            for tag in ("__dict__", "__map__"):
                if tag in g.ret and tag in c.ret:
                    g_sorted = sorted(g.ret[tag], key=lambda x: json.dumps(x, sort_keys=True))
                    c_sorted = sorted(c.ret[tag], key=lambda x: json.dumps(x, sort_keys=True))
                    if eq(g_sorted, c_sorted, self.tol):
                        return V(aspect="key_enumeration_order", detail="same keys/values, different key enumeration order",
                                 expected=_short(g.ret), actual=_short(c.ret))
        relaxed = "ret" in unstable or not self.must("return_order")
        if eq(canon.as_multiset(g.ret), canon.as_multiset(c.ret), self.tol):
            if relaxed:
                return None
            return V(aspect="return_order", detail="same elements, different order",
                     expected=_short(g.ret), actual=_short(c.ret))
        return V(aspect="return_value", detail="returned value differs",
                 expected=_short(g.ret), actual=_short(c.ret))

    # ------------------------------------------------------------------
    def compare_scale(self, p: ScalePoint, c: CaseResult) -> bool:
        if p.status not in ("ok", "exception"):
            return True                                   # original could not finish: no ground truth
        if c.status not in ("ok", "exception"):
            return False
        return hashlib.sha1(scale_digest(c).encode()).hexdigest()[:16] == p.digest


def scale_digest(r: CaseResult) -> str:
    return json.dumps([r.status, r.ret_digest, r.exc_type, r.mut], sort_keys=True)