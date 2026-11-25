from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, render_template, request

APP_ROOT = Path(__file__).resolve().parent
REPO_ROOT = APP_ROOT.parent
TESTS_DIR = REPO_ROOT / "tests"
PYTHON_TESTS_DIR = TESTS_DIR / "python"
POLICIES_DIR = REPO_ROOT / "policies"
SECURE_CLANG = REPO_ROOT / "secure-clang"
SECURE_PYTHON = REPO_ROOT / "secure-python"
SECURE_PYTHON_TOOL = REPO_ROOT / "tools" / "secure_python.py"

app = Flask(__name__)
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
app.config["TEMPLATES_AUTO_RELOAD"] = True


@app.after_request
def add_no_cache_headers(response: Any) -> Any:
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


def _find_line_hints(source_code: str, messages: list[str]) -> list[dict[str, Any]]:
    lines = source_code.splitlines()
    hints: list[dict[str, Any]] = []

    # Map common violation keywords to line-level hints in source.
    keyword_map = {
        "printf": "Sensitive logging API",
        "puts": "Sensitive logging API",
        "fprintf": "Sensitive logging API",
        "perror": "Sensitive logging API",
        "rand": "Weak entropy API",
        "srand": "Weak entropy API",
        "sha1": "Weak crypto API",
        "md5": "Weak crypto API",
        "install": "Install path check",
        "verifysignature": "Signature dominance check",
        "verify_signature": "Signature dominance check",
        "verifyimagehash": "Image hash dominance check",
        "verify_image_hash": "Image hash dominance check",
        "checkimagehash": "Image hash dominance check",
        "sourcetrusted": "Trusted source check",
        "source_trusted": "Trusted source check",
        "validatesource": "Trusted source check",
        "vendor_private_key": "Hardcoded secret / private key",
        "private key": "Hardcoded private key",
        "eval": "Dynamic execution API",
        "exec": "Dynamic execution API",
        "os.system": "Arbitrary command execution API",
        "pickle": "Insecure deserialization API",
        "ghp_": "Hardcoded API token",
        "bearer": "Hardcoded credential token",
    }

    lower_msgs = "\n".join(messages).lower()

    for idx, line in enumerate(lines, start=1):
        normalized = line.lower()
        for key, label in keyword_map.items():
            if key in normalized and key in lower_msgs:
                hints.append(
                    {
                        "line": idx,
                        "kind": "warning",
                        "label": label,
                        "source": line.strip(),
                    }
                )
                break

    return hints


def _extract_syntax_hints(raw_output: str) -> list[dict[str, Any]]:
    hints: list[dict[str, Any]] = []
    # Clang format: /tmp/file.c:12:5: error: ...
    clang_pattern = re.compile(r"[^:\n]+:(\d+):(\d+):\s+error:\s+(.*)")
    for match in clang_pattern.finditer(raw_output):
        hints.append(
            {
                "line": int(match.group(1)),
                "column": int(match.group(2)),
                "kind": "error",
                "label": match.group(3).strip(),
            }
        )
    # Python format: SyntaxError: ... at line 12:5
    py_pattern = re.compile(r"SyntaxError:\s+(.+?)\s+at line (\d+)(?::(\d+))?")
    for match in py_pattern.finditer(raw_output):
        hints.append(
            {
                "line": int(match.group(2)),
                "column": int(match.group(3)) if match.group(3) else 1,
                "kind": "error",
                "label": match.group(1).strip(),
            }
        )
    return hints


def _extract_energy_metrics(raw_output: str) -> dict[str, Any]:
    phase_pattern = re.compile(
        r"^\[CodeCarbon\]\s+phase=([a-zA-Z0-9_-]+)\s+energy_kwh=([0-9.eE+-]+)\s+emissions_kg=([0-9.eE+-]+)$"
    )
    total_pattern = re.compile(
        r"^\[CodeCarbon\]\s+total\s+energy_kwh=([0-9.eE+-]+)\s+emissions_kg=([0-9.eE+-]+)$"
    )

    phases: list[dict[str, Any]] = []
    total = {"energy_kwh": 0.0, "emissions_kg": 0.0}

    for line in raw_output.splitlines():
        candidate = line.strip()
        m_phase = phase_pattern.match(candidate)
        if m_phase:
            phases.append(
                {
                    "phase": m_phase.group(1),
                    "energy_kwh": float(m_phase.group(2)),
                    "emissions_kg": float(m_phase.group(3)),
                }
            )
            continue

        m_total = total_pattern.match(candidate)
        if m_total:
            total = {
                "energy_kwh": float(m_total.group(1)),
                "emissions_kg": float(m_total.group(2)),
            }

    return {"phases": phases, "total": total, "available": bool(phases)}


def run_secure_compile(
    source_code: str,
    filename: str,
    policy: str = "original_protocol.json",
    energy: bool = False,
) -> dict[str, Any]:
    if not SECURE_CLANG.exists():
        return {
            "ok": False,
            "status": "setup-error",
            "message": "secure-clang wrapper was not found in repository root.",
            "rawOutput": "",
            "violations": [],
            "hints": [],
        }

    safe_name = Path(filename).name
    if not safe_name.endswith(".c"):
        safe_name += ".c"

    with tempfile.TemporaryDirectory(prefix="ota-demo-") as tmp:
        tmp_path = Path(tmp)
        src_path = tmp_path / safe_name
        out_path = tmp_path / "demo.out"
        src_path.write_text(source_code, encoding="utf-8")

        cmd = [sys.executable, str(SECURE_CLANG)]
        if energy:
            cmd.append("--energy")
        if policy:
            policy_name = Path(policy).name
            if not policy_name.endswith(".json"):
                policy_name += ".json"
            policy_file = POLICIES_DIR / policy_name
            if policy_file.exists():
                cmd.extend(["--policy", str(policy_file)])

        has_main = bool(re.search(r'\b(?:int|void)\s+main\s*\(', source_code))
        cmd.append(str(src_path))
        if not has_main:
            cmd.append("-c")
        cmd.extend(["-o", str(out_path)])

        try:
            proc = subprocess.run(
                cmd,
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                timeout=120,
            )
        except subprocess.TimeoutExpired as exc:
            raw_output = ((exc.stdout or "") + "\n" + (exc.stderr or "")).strip()
            return {
                "ok": False,
                "status": "failed",
                "message": "Compilation timed out after 120 seconds.",
                "rawOutput": raw_output or "Process timed out.",
                "violations": [],
                "hints": [],
                "energy": {"phases": [], "total": {"energy_kwh": 0.0, "emissions_kg": 0.0}, "available": False},
            }

        raw_output = (proc.stdout or "") + ("\n" if proc.stdout and proc.stderr else "") + (proc.stderr or "")

        violations = [
            line.strip()[2:].strip()
            for line in raw_output.splitlines()
            if line.strip().startswith("-")
        ]

        hints = _find_line_hints(source_code, violations)
        hints.extend(_extract_syntax_hints(raw_output))
        energy = _extract_energy_metrics(raw_output)

        if proc.returncode == 0:
            return {
                "ok": True,
                "status": "passed",
                "message": "Compilation passed. No security violations were reported.",
                "rawOutput": raw_output.strip(),
                "violations": [],
                "hints": hints,
                "energy": energy,
            }

        status = "failed"
        if "setup-error" in raw_output.lower() or "not found" in raw_output.lower():
            status = "setup-error"

        return {
            "ok": False,
            "status": status,
            "message": "Compilation blocked by secure-clang policy checks.",
            "rawOutput": raw_output.strip(),
            "violations": violations,
            "hints": hints,
            "energy": energy,
        }


def run_secure_python_compile(
    source_code: str,
    filename: str,
    policy: str = "original_protocol.json",
    energy: bool = False,
) -> dict[str, Any]:
    safe_name = Path(filename).name
    if not safe_name.endswith(".py"):
        safe_name += ".py"

    with tempfile.TemporaryDirectory(prefix="ota-demo-py-") as tmp:
        tmp_path = Path(tmp)
        src_path = tmp_path / safe_name
        out_path = tmp_path / "demo.pyc"
        src_path.write_text(source_code, encoding="utf-8")

        script = SECURE_PYTHON if SECURE_PYTHON.exists() else SECURE_PYTHON_TOOL
        cmd = [sys.executable, str(script)]
        if energy:
            cmd.append("--energy")
        if policy:
            policy_name = Path(policy).name
            if not policy_name.endswith(".json"):
                policy_name += ".json"
            policy_file = POLICIES_DIR / policy_name
            if policy_file.exists():
                cmd.extend(["--policy", str(policy_file)])

        cmd.extend(["-o", str(out_path)])
        cmd.append(str(src_path))

        try:
            proc = subprocess.run(
                cmd,
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                timeout=60,
            )
        except subprocess.TimeoutExpired as exc:
            raw_output = ((exc.stdout or "") + "\n" + (exc.stderr or "")).strip()
            return {
                "ok": False,
                "status": "failed",
                "message": "Compilation timed out after 60 seconds.",
                "rawOutput": raw_output or "Process timed out.",
                "violations": [],
                "hints": [],
                "energy": {"phases": [], "total": {"energy_kwh": 0.0, "emissions_kg": 0.0}, "available": False},
            }

        raw_output = (proc.stdout or "") + ("\n" if proc.stdout and proc.stderr else "") + (proc.stderr or "")

        violations = [
            line.strip()[2:].strip()
            for line in raw_output.splitlines()
            if line.strip().startswith("-")
        ]

        hints = _find_line_hints(source_code, violations)
        hints.extend(_extract_syntax_hints(raw_output))
        energy_metrics = _extract_energy_metrics(raw_output)

        if proc.returncode == 0:
            return {
                "ok": True,
                "status": "passed",
                "message": "Compilation passed. No security violations were reported by secure-python.",
                "rawOutput": raw_output.strip() or "secure-python: Clean build. Bytecode generated.",
                "violations": [],
                "hints": hints,
                "energy": energy_metrics,
            }

        return {
            "ok": False,
            "status": "failed",
            "message": "Compilation blocked by secure-python policy checks.",
            "rawOutput": raw_output.strip(),
            "violations": violations,
            "hints": hints,
            "energy": energy_metrics,
        }


@app.route("/")
def index() -> str:
    return render_template("index.html")


@app.get("/api/samples")
def list_samples() -> Any:
    lang = request.args.get("lang", "c").lower()
    samples = []
    if lang == "python":
        if PYTHON_TESTS_DIR.exists():
            for path in sorted(PYTHON_TESTS_DIR.glob("*.py")):
                samples.append(path.name)
    else:
        for path in sorted(TESTS_DIR.glob("*.c")):
            samples.append(path.name)
    return jsonify({"samples": samples, "lang": lang})


@app.get("/api/samples/<name>")
def get_sample(name: str) -> Any:
    safe_name = Path(name).name
    sample_path = None
    if safe_name.endswith(".py"):
        cand = (PYTHON_TESTS_DIR / safe_name).resolve()
        if cand.exists():
            sample_path = cand
    if not sample_path:
        cand = (TESTS_DIR / safe_name).resolve()
        if cand.exists():
            sample_path = cand

    if not sample_path or not sample_path.exists():
        return jsonify({"error": "Sample not found"}), 404

    return jsonify({"name": sample_path.name, "code": sample_path.read_text(encoding="utf-8")})


@app.get("/api/policies")
def list_policies() -> Any:
    policies = []
    if POLICIES_DIR.exists():
        for path in sorted(POLICIES_DIR.glob("*.json")):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                policies.append(
                    {
                        "filename": path.name,
                        "id": data.get("id", path.stem),
                        "name": data.get("name", path.stem),
                        "description": data.get("description", ""),
                        "rules": data.get("rules", {}),
                    }
                )
            except Exception:
                policies.append(
                    {
                        "filename": path.name,
                        "id": path.stem,
                        "name": path.stem,
                        "description": "",
                        "rules": {},
                    }
                )
    return jsonify({"policies": policies})


@app.get("/api/policies/<name>")
def get_policy(name: str) -> Any:
    safe_name = Path(name).name
    if not safe_name.endswith(".json"):
        safe_name += ".json"

    policy_path = (POLICIES_DIR / safe_name).resolve()
    if POLICIES_DIR.resolve() not in policy_path.parents and policy_path != POLICIES_DIR.resolve():
        return jsonify({"error": "Invalid policy path"}), 400

    if not policy_path.exists():
        return jsonify({"error": "Policy not found"}), 404

    try:
        data = json.loads(policy_path.read_text(encoding="utf-8"))
        return jsonify(data)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.post("/api/compile")
def compile_code() -> Any:
    payload = request.get_json(silent=True) or {}
    source_code = payload.get("code", "")
    filename = payload.get("filename", "")
    language = payload.get("language", "").lower()
    policy = payload.get("policy", "original_protocol.json")
    energy = bool(payload.get("energy", False))

    if not source_code.strip():
        return jsonify({"error": "Code is empty."}), 400

    is_python = language == "python" or (filename and filename.endswith(".py"))
    if not filename:
        filename = "firmware_demo.py" if is_python else "firmware_demo.c"

    if is_python:
        result = run_secure_python_compile(source_code, filename, policy, energy=energy)
    else:
        result = run_secure_compile(source_code, filename, policy, energy=energy)
    return jsonify(result)


try:
    from advisory_copilot import (
        orchestrate_advisory_copilot,
        check_local_ollama_available,
        LOCAL_OLLAMA_ENDPOINT,
    )
except ImportError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    from advisory_copilot import (
        orchestrate_advisory_copilot,
        check_local_ollama_available,
        LOCAL_OLLAMA_ENDPOINT,
    )


@app.get("/api/advisory-copilot/models")
def get_copilot_models() -> Any:
    online, models = check_local_ollama_available()
    return jsonify({
        "online": online,
        "endpoint": LOCAL_OLLAMA_ENDPOINT,
        "models": models,
        "backend": f"Ollama ({LOCAL_OLLAMA_ENDPOINT})" if online else "Local In-Memory Security Engine (0 Telemetry)",
        "telemetry": "ZERO CLOUD TELEMETRY: Strictly localhost (127.0.0.1)",
    })


@app.post("/api/advisory-copilot")
def run_copilot() -> Any:
    payload = request.get_json(silent=True) or {}
    source_code = payload.get("code", "")
    violations = payload.get("violations", [])
    hints = payload.get("hints", [])
    policy = payload.get("policy", "original_protocol.json")
    filename = payload.get("filename", "")
    language = payload.get("language", "").lower()
    raw_output = payload.get("rawOutput", "")
    model = payload.get("model", None)

    if not source_code.strip():
        return jsonify({"error": "Source code is empty."}), 400

    is_python = language == "python" or (filename and filename.endswith(".py")) or ((bool(re.search(r'\bdef\s+\w+', source_code)) or "import " in source_code or "from " in source_code) and "#include" not in source_code and "typedef" not in source_code)
    if not filename:
        filename = "firmware_demo.py" if is_python else "firmware_demo.c"
    elif is_python and filename == "firmware_demo.c":
        filename = "firmware_demo.py"

    compile_res = None
    if not violations or not raw_output:
        if is_python:
            compile_res = run_secure_python_compile(source_code, filename, policy, energy=False)
        else:
            compile_res = run_secure_compile(source_code, filename, policy, energy=False)
        if not violations:
            violations = compile_res.get("violations", [])
        if not hints:
            hints = compile_res.get("hints", [])
        if not raw_output:
            raw_output = compile_res.get("rawOutput", "")

    result = orchestrate_advisory_copilot(
        source_code=source_code,
        violations=violations,
        hints=hints,
        policy=policy,
        filename=filename,
        raw_output=raw_output,
        requested_model=model,
    )
    if compile_res:
        result["compile_result"] = compile_res

    return jsonify(result)


if __name__ == "__main__":
    # Host 0.0.0.0 for Ubuntu VM browser access.
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5050")), debug=True, use_reloader=True)
