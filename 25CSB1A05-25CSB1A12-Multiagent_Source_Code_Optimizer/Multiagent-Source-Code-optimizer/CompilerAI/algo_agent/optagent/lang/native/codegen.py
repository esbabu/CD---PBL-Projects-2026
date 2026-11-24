"""Jinja2 code generator for C11 and C++17 native test harness drivers."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader

from .marshal import FunctionSignature

TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"


def generate_driver(
    sig: FunctionSignature,
    target_filename: str | None = None,
    hints: dict[str, Any] | None = None,
) -> str:
    """Render standalone driver.c or driver.cpp that #includes the target file."""
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    is_cpp = sig.language == "cpp"
    tpl_name = "driver.cpp.j2" if is_cpp else "driver.c.j2"
    target = target_filename or ("target.cpp" if is_cpp else "target.c")

    # Map visible parameter names -> positional index in JSON args array
    visible_index: dict[str, int] = {}
    vidx = 0
    for b in sig.params:
        if b.is_length_for or b.is_out_param:
            continue
        visible_index[b.name] = vidx
        vidx += 1

    tpl = env.get_template(tpl_name)
    return tpl.render(
        sig=sig,
        target_filename=target,
        visible_index=visible_index,
        hints=hints or {},
    )
