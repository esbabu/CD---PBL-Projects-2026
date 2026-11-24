"""Read-only environment health report for OptAgent (`python -m optagent.doctor`).

Checks host Python version, Docker reachability, sandbox images & internal tools,
host toolchains (node, clang, clang++, gcc, llvm-cov, valgrind, cbmc),
tree-sitter grammars/API version, Ollama reachability and installed models,
and disk space for `runs/`. Never installs, pulls, or starts anything.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path
from typing import Any

from .config import Settings

ROOT = Path(__file__).resolve().parent.parent


def _run_quick(cmd: list[str], timeout: float = 5.0) -> tuple[bool, str]:
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        out = (p.stdout or p.stderr or "").strip()
        return p.returncode == 0, out.splitlines()[0] if out else ""
    except Exception as e:
        return False, str(e)


def _check_docker() -> dict[str, Any]:
    exe = shutil.which("docker")
    if not exe:
        return {
            "available": False,
            "path": None,
            "version": None,
            "remediation": "Install Docker Desktop/Engine if containerized sandboxing is desired, or set OPT_SANDBOX=local for Python.",
        }
    ok, out = _run_quick([exe, "info", "--format", "{{.ServerVersion}}"], timeout=6.0)
    return {
        "available": ok,
        "path": exe,
        "version": out if ok else None,
        "error": None if ok else out,
        "remediation": None if ok else "Start the Docker daemon so sandbox containers can run.",
    }


def _check_docker_image(image: str, tools: list[str], docker_ok: bool) -> dict[str, Any]:
    if not docker_ok:
        return {"present": False, "tools": {t: False for t in tools}, "reason": "docker_unavailable"}
    ok, _ = _run_quick(["docker", "image", "inspect", image], timeout=5.0)
    if not ok:
        return {
            "present": False,
            "tools": {t: False for t in tools},
            "remediation": f"Build or pull Docker image '{image}' (see docker/ directory).",
        }
    tool_status: dict[str, bool] = {}
    for t in tools:
        tok, _ = _run_quick(["docker", "run", "--rm", "--entrypoint", "sh", image, "-c", f"command -v {t}"], timeout=10.0)
        tool_status[t] = tok
    return {"present": True, "tools": tool_status}


def _check_treesitter() -> dict[str, Any]:
    info: dict[str, Any] = {"installed": False, "version": None, "api_style": None, "grammars": {}}
    try:
        import tree_sitter  # type: ignore

        info["installed"] = True
        info["version"] = getattr(tree_sitter, "__version__", "unknown")
        # >= 0.22 uses Language(capsule) and Parser(lang); older uses Language.build_library
        info["api_style"] = "modern_0.22+" if not hasattr(tree_sitter.Language, "build_library") else "legacy"
    except ImportError as e:
        info["error"] = str(e)
        info["remediation"] = "Install tree-sitter>=0.22 and language grammar packages (tree-sitter-c, tree-sitter-cpp, tree-sitter-javascript)."
        return info

    for mod_name, lang in (
        ("tree_sitter_c", "c"),
        ("tree_sitter_cpp", "cpp"),
        ("tree_sitter_javascript", "javascript"),
    ):
        try:
            m = __import__(mod_name)
            cap = m.language()
            _ = tree_sitter.Language(cap)
            info["grammars"][lang] = True
        except Exception as e:
            info["grammars"][lang] = False
            info.setdefault("grammar_errors", {})[lang] = str(e)
    return info


def _check_host_tools() -> dict[str, Any]:
    tools = ["node", "npm", "clang", "clang++", "gcc", "g++", "llvm-cov", "valgrind", "cbmc"]
    result: dict[str, Any] = {}
    for t in tools:
        exe = shutil.which(t)
        if not exe and t == "node":
            # Check well-known user-local node installation
            cand = Path.home() / ".nodejs" / "node-v20.18.0-win-x64" / "node.exe"
            if cand.exists():
                exe = str(cand)
        if exe:
            ok, ver = _run_quick([exe, "--version"], timeout=4.0)
            result[t] = {"available": True, "path": exe, "version": ver if ok else ""}
        else:
            result[t] = {"available": False, "path": None, "version": None}
    return result


def _check_ollama(settings: Settings) -> dict[str, Any]:
    base = settings.ollama_base.rstrip("/")
    res: dict[str, Any] = {
        "base_url": base,
        "reachable": False,
        "version": None,
        "models": [],
        "roles": {},
        "remediation": None,
    }
    try:
        with urllib.request.urlopen(f"{base}/api/version", timeout=3.0) as r:
            vdata = json.loads(r.read().decode("utf-8", errors="replace"))
            res["version"] = vdata.get("version")
        with urllib.request.urlopen(f"{base}/api/tags", timeout=3.0) as r:
            tdata = json.loads(r.read().decode("utf-8", errors="replace"))
            models = [m.get("name", "") for m in tdata.get("models", []) if m.get("name")]
            res["models"] = models
        res["reachable"] = True
        if not models:
            res["remediation"] = "Ollama is reachable but no models are installed. Run `ollama pull qwen2.5-coder:7b` manually."
    except Exception as e:
        res["error"] = str(e)
        res["remediation"] = f"Ollama not reachable at {base}; start the Ollama service manually or run with OPT_LLM_MODE=off."

    # Resolve roles if gateway health module is available
    try:
        from .llm.health import resolve_role_models

        res["roles"] = resolve_role_models(res["models"], settings)
    except Exception:
        res["roles"] = {
            "spec": settings.spec_model,
            "predictor": settings.predictor_model,
        }
    return res


def _check_disk(runs_dir: str) -> dict[str, Any]:
    p = Path(runs_dir)
    target = p if p.exists() else Path.cwd()
    usage = shutil.disk_usage(target)
    free_gb = round(usage.free / (1024 ** 3), 2)
    return {
        "runs_dir": str(p.resolve()),
        "free_gb": free_gb,
        "ok": free_gb >= 0.5,
        "remediation": None if free_gb >= 0.5 else "Free at least 0.5 GB of disk space for runs/ artifacts.",
    }


def run_doctor(languages: list[str] | None = None, settings: Settings | None = None) -> dict[str, Any]:
    s = settings or Settings()
    req_langs = [l.lower() for l in (languages or ["python"])]
    py_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    docker = _check_docker()
    host_tools = _check_host_tools()
    ts = _check_treesitter()
    ollama = _check_ollama(s)
    disk = _check_disk(s.runs_dir)

    images = {
        "python": _check_docker_image(s.docker_image, ["python3"], docker["available"]),
        "js": _check_docker_image(s.js_docker_image, ["node"], docker["available"]),
        "native": _check_docker_image(s.native_docker_image, ["clang", "clang++", "gcc", "llvm-cov", "cbmc"], docker["available"]),
    }

    # Evaluate per-language readiness
    lang_ready: dict[str, dict[str, Any]] = {}
    for lang in ("python", "javascript", "c", "cpp"):
        if lang == "python":
            ok = disk["ok"]
            lang_ready[lang] = {
                "ready": ok,
                "backend": "docker" if images["python"]["present"] else "local",
                "remediation": None if ok else disk["remediation"],
            }
        elif lang == "javascript":
            has_docker = images["js"]["present"] and images["js"]["tools"].get("node")
            has_local = host_tools["node"]["available"]
            has_ts = bool(ts.get("grammars", {}).get("javascript"))
            ok = (has_docker or has_local) and has_ts
            rems = []
            if not has_ts:
                rems.append("Install tree-sitter and tree-sitter-javascript on host.")
            if not (has_docker or has_local):
                rems.append("Install Node.js 18+ or build docker/sandbox-js.Dockerfile.")
            lang_ready[lang] = {
                "ready": ok,
                "backend": "docker" if has_docker else ("local" if has_local else "unavailable"),
                "remediation": "; ".join(rems) if rems else None,
            }
        else:  # c / cpp
            compiler = "clang" if lang == "c" else "clang++"
            alt = "gcc" if lang == "c" else "g++"
            has_docker = images["native"]["present"] and (
                images["native"]["tools"].get(compiler) or images["native"]["tools"].get(alt)
            )
            has_local = host_tools[compiler]["available"] or host_tools[alt]["available"]
            has_ts = bool(ts.get("grammars", {}).get(lang))
            ok = (has_docker or (has_local and s.allow_local_native)) and has_ts
            rems = []
            if not has_ts:
                rems.append(f"Install tree-sitter and tree-sitter-{lang} on host.")
            if not has_docker and not has_local:
                rems.append(f"Build docker/sandbox-native.Dockerfile or install {compiler}/{alt} (and set OPT_ALLOW_LOCAL_NATIVE=1 for local runs).")
            elif has_local and not has_docker and not s.allow_local_native:
                rems.append("Set OPT_ALLOW_LOCAL_NATIVE=1 or build docker/sandbox-native.Dockerfile.")
            lang_ready[lang] = {
                "ready": ok,
                "backend": "docker" if has_docker else ("local" if has_local else "unavailable"),
                "remediation": "; ".join(rems) if rems else None,
            }

    norm_map = {"py": "python", "python": "python", "js": "javascript", "javascript": "javascript", "c": "c", "cpp": "cpp", "c++": "cpp"}
    overall_ok = all(lang_ready.get(norm_map.get(l, l), {}).get("ready", False) for l in req_langs)

    report = {
        "python": {
            "version": py_ver,
            "minor": f"{sys.version_info.major}.{sys.version_info.minor}",
            "executable": sys.executable,
            "docker_image": s.docker_image,
        },
        "docker": docker,
        "images": images,
        "host_tools": host_tools,
        "tree_sitter": ts,
        "ollama": ollama,
        "disk": disk,
        "languages": lang_ready,
        "requested_languages": req_langs,
        "ok": overall_ok,
    }

    runs_path = Path(s.runs_dir)
    runs_path.mkdir(parents=True, exist_ok=True)
    (runs_path / "doctor.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def format_doctor_table(report: dict[str, Any]) -> str:
    lines = [
        "=== OptAgent Doctor ===",
        f"Python      : {report['python']['version']} ({report['python']['executable']})",
        f"Docker      : {'OK ' + str(report['docker']['version']) if report['docker']['available'] else 'UNAVAILABLE'}",
        f"Tree-sitter : {report['tree_sitter'].get('version')} ({report['tree_sitter'].get('api_style')}) grammars={report['tree_sitter'].get('grammars')}",
        f"Ollama      : {'REACHABLE v' + str(report['ollama']['version']) + ' models=' + str(report['ollama']['models']) if report['ollama']['reachable'] else 'UNREACHABLE (' + report['ollama']['base_url'] + ')'}",
        f"Disk (runs) : {report['disk']['free_gb']} GB free ({'OK' if report['disk']['ok'] else 'LOW'})",
        "",
        "Language Readiness:",
    ]
    for lang, info in report["languages"].items():
        st = "READY" if info["ready"] else "DEGRADED"
        rem = f" -> {info['remediation']}" if info.get("remediation") else ""
        lines.append(f"  - {lang:11s}: {st:8s} (backend={info['backend']}){rem}")
    if report["ollama"].get("remediation"):
        lines.append(f"Ollama Note : {report['ollama']['remediation']}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="OptAgent read-only environment doctor")
    ap.add_argument("--lang", action="append", help="Languages to require (repeatable: py, js, c, cpp)")
    ap.add_argument("--json", action="store_true", help="Print JSON report to stdout")
    args = ap.parse_args(argv)
    rep = run_doctor(languages=args.lang or ["python"])
    if args.json:
        print(json.dumps(rep, indent=2))
    else:
        print(format_doctor_table(rep))
    return 0 if rep["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
