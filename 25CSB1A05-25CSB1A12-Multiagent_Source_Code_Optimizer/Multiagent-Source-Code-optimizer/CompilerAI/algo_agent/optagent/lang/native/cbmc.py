"""CBMC bounded equivalence miter generator and verifier for C/C++ (max evidence tier T3)."""
from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .clang_facts import analyze_native_source
from .marshal import FunctionSignature, build_signature


@dataclass
class CBMCResult:
    passed: bool
    skipped: bool = False
    reason: str = ""
    unwind_bound: int = 16
    max_array_len: int = 8
    elapsed_s: float = 0.0
    details: dict[str, Any] = field(default_factory=dict)


def _rename_entry(source: str, entry: str, new_name: str) -> str:
    return re.sub(rf"\b{re.escape(entry)}\b", new_name, source)


def generate_cbmc_miter(
    orig_source: str,
    cand_source: str,
    sig: FunctionSignature,
    max_array_len: int = 8,
) -> str:
    """Generate a C/C++ CBMC miter harness calling orig and cand on nondet inputs and asserting equality."""
    orig_fn = f"__opt_orig_{sig.name}"
    cand_fn = f"__opt_cand_{sig.name}"

    lines = [
        "/* Auto-generated OptAgent CBMC bounded equivalence miter */",
        "#include <assert.h>",
        "#include <stdbool.h>",
        "#include <stdint.h>",
        "",
        "extern int nondet_int(void);",
        "extern void __CPROVER_assume(int);",
        "",
        _rename_entry(orig_source, sig.name, orig_fn),
        "",
        _rename_entry(cand_source, sig.name, cand_fn),
        "",
        "int main(void) {",
    ]

    call_args_orig = []
    call_args_cand = []
    out_checks = []

    for b in sig.params:
        if b.is_out_param:
            elem = b.ntype.elem.c_type if b.ntype.elem else "int"
            lines.append(f"    {elem} out_orig_{b.name}[{b.out_length}] = {{0}};")
            lines.append(f"    {elem} out_cand_{b.name}[{b.out_length}] = {{0}};")
            call_args_orig.append(f"out_orig_{b.name}")
            call_args_cand.append(f"out_cand_{b.name}")
            for k in range(b.out_length):
                out_checks.append(f"    assert(out_orig_{b.name}[{k}] == out_cand_{b.name}[{k}]);")
        elif b.is_length_for:
            call_args_orig.append(f"n_{b.is_length_for}")
            call_args_cand.append(f"n_{b.is_length_for}")
        elif b.ntype.kind == "ptr_array":
            elem = b.ntype.elem.c_type if b.ntype.elem else "int"
            lines.append(f"    int n_{b.name} = nondet_int();")
            lines.append(f"    __CPROVER_assume(n_{b.name} >= 0 && n_{b.name} <= {max_array_len});")
            lines.append(f"    {elem} arr_orig_{b.name}[{max_array_len}];")
            lines.append(f"    {elem} arr_cand_{b.name}[{max_array_len}];")
            lines.append(f"    for (int _i = 0; _i < n_{b.name}; _i++) {{")
            lines.append(f"        {elem} _v = ({elem})nondet_int();")
            lines.append("        __CPROVER_assume(_v >= -1000 && _v <= 1000);")
            lines.append(f"        arr_orig_{b.name}[_i] = _v;")
            lines.append(f"        arr_cand_{b.name}[_i] = _v;")
            lines.append("    }")
            call_args_orig.append(f"arr_orig_{b.name}")
            call_args_cand.append(f"arr_cand_{b.name}")
        else:
            lines.append(f"    {b.ntype.c_type} p_{b.name} = ({b.ntype.c_type})nondet_int();")
            lines.append(f"    __CPROVER_assume(p_{b.name} >= -1000 && p_{b.name} <= 1000);")
            call_args_orig.append(f"p_{b.name}")
            call_args_cand.append(f"p_{b.name}")

    if sig.return_type.kind != "void":
        lines.append(f"    {sig.return_type.c_type} r_orig = {orig_fn}({', '.join(call_args_orig)});")
        lines.append(f"    {sig.return_type.c_type} r_cand = {cand_fn}({', '.join(call_args_cand)});")
        lines.append("    assert(r_orig == r_cand);")
    else:
        lines.append(f"    {orig_fn}({', '.join(call_args_orig)});")
        lines.append(f"    {cand_fn}({', '.join(call_args_cand)});")

    lines.extend(out_checks)
    lines.append("    return 0;")
    lines.append("}")
    return "\n".join(lines) + "\n"


def run_cbmc_equivalence(
    orig_source: str,
    cand_source: str,
    entry: str,
    language: str = "c",
    hints: dict[str, Any] | None = None,
    unwind: int = 16,
    max_array_len: int = 8,
    timeout_s: float = 30.0,
    enabled: bool = False,
) -> CBMCResult:
    """Run CBMC bounded equivalence check; always records bounds in result details."""
    t0 = time.time()
    if not enabled:
        return CBMCResult(
            passed=False,
            skipped=True,
            reason="CBMC bounded equivalence disabled by settings.",
            unwind_bound=unwind,
            max_array_len=max_array_len,
            details={"unwind_bound": unwind, "max_array_len": max_array_len},
        )
    if not shutil.which("cbmc"):
        return CBMCResult(
            passed=False,
            skipped=True,
            reason="cbmc binary not found on PATH (available inside sandbox-native Docker image).",
            unwind_bound=unwind,
            max_array_len=max_array_len,
            details={"unwind_bound": unwind, "max_array_len": max_array_len},
        )

    try:
        mod = analyze_native_source(orig_source, language, hints)
        sig = build_signature(mod.functions[entry], language, hints)
    except Exception as e:
        return CBMCResult(
            passed=False,
            skipped=True,
            reason=f"CBMC signature extraction failed: {e}",
            unwind_bound=unwind,
            max_array_len=max_array_len,
        )

    # Check supported scalar/array types for CBMC
    for b in sig.params:
        if b.ntype.kind not in ("int", "bool", "ptr_array"):
            return CBMCResult(
                passed=False,
                skipped=True,
                reason=f"CBMC does not support parameter type '{b.ntype.raw}' for bounded miter.",
                unwind_bound=unwind,
                max_array_len=max_array_len,
                details={"unwind_bound": unwind, "max_array_len": max_array_len},
            )

    miter = generate_cbmc_miter(orig_source, cand_source, sig, max_array_len=max_array_len)
    suffix = ".cpp" if language == "cpp" else ".c"
    with tempfile.TemporaryDirectory(prefix="optagent_cbmc_") as td:
        mfile = Path(td) / f"miter{suffix}"
        mfile.write_text(miter, encoding="utf-8")
        try:
            proc = subprocess.run(
                ["cbmc", str(mfile), "--unwind", str(unwind), "--bounds-check", "--pointer-check"],
                capture_output=True, text=True, timeout=timeout_s,
            )
            elapsed = round(time.time() - t0, 3)
            out = proc.stdout + "\n" + proc.stderr
            if "VERIFICATION SUCCESSFUL" in out:
                return CBMCResult(
                    passed=True,
                    skipped=False,
                    reason=f"CBMC proved bounded equivalence (unwind={unwind}, n<={max_array_len}, vals in [-1000,1000]).",
                    unwind_bound=unwind,
                    max_array_len=max_array_len,
                    elapsed_s=elapsed,
                    details={"engine": "cbmc", "unwind_bound": unwind, "max_array_len": max_array_len, "value_range": [-1000, 1000]},
                )
            return CBMCResult(
                passed=False,
                skipped=False,
                reason=f"CBMC counterexample or verification failure (unwind={unwind}, n<={max_array_len}).",
                unwind_bound=unwind,
                max_array_len=max_array_len,
                elapsed_s=elapsed,
                details={"engine": "cbmc", "unwind_bound": unwind, "max_array_len": max_array_len, "output": out[-1000:]},
            )
        except subprocess.TimeoutExpired:
            return CBMCResult(
                passed=False,
                skipped=True,
                reason=f"CBMC timed out after {timeout_s}s (unwind={unwind}).",
                unwind_bound=unwind,
                max_array_len=max_array_len,
                elapsed_s=round(time.time() - t0, 3),
            )
