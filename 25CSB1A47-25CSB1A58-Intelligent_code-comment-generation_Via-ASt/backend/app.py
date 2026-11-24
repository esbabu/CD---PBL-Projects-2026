"""Flask routes for Intelligent Code Comment Generation via AST."""

import logging
import os
import secrets
import time
from io import BytesIO
from urllib.parse import urlsplit

from flask import Blueprint, Flask, current_app, jsonify, request, send_file, send_from_directory

from .agent import AgentRunError, run_agent
from .agentic.routes import (
    agentic_model_ready,
    agentic_routes,
    refresh_agentic_model_client,
    run_agentic_workflow_sync,
)
from .monitoring import metrics_collector, monitoring_routes
from .project import project_routes
from .professor_student_engine import ProfessorStudentOrchestrator
from .optimization_agent import optimize_code
from .security_attack_agent import simulate_attacks
from .security_fixing_agent import fix_attack_vulnerabilities
from .security_rate_limit import default_rate_limiter
from .security_secrets import install_log_redaction
from .security_ssrf import validate_url_against_ssrf
from . import model_provider
from .assistant import (
    AssistantModelError,
    UnsafeAISuggestionError,
    build_assistant_response,
    build_live_ai_suggestion,
    classify_nexus_request,
    validate_assistant_history,
)
from .attack_guard import detect_attack, evaluate_attack_suite
from .code_analysis import (
    CC_THRESHOLD,
    CommentGenerationError,
    _build_prompt_payload,
    analyze_code,
    build_smart_ast_explanations,
    client,
    _fallback_comment_code,
    validate_code,
)
from .code_improver import improve_code_quality
from .config import AppConfig
from .editor_assist import editor_assist
from .model_provider import (
    get_current_settings,
    provider_display_name,
    provider_ready,
    test_provider_connectivity,
    update_provider_settings,
)
from .pipeline import run_pipeline
from .provider_errors import classify_provider_error
from .request_utils import (
    cursor_to_offset as _cursor_to_offset,
)
from .request_utils import (
    extract_code as _extract_code,
)
from .request_utils import (
    request_data as _parse_request_data,
)
from .request_utils import (
    to_utf16_offset as _to_utf16_offset,
)
from .request_utils import (
    undefined_name_findings as _undefined_name_findings,
)
from .request_utils import (
    valid_cursor as _valid_cursor,
)
from .rules import build_review_score, summarize_quality
from .validator import check_undefined_names, format_name_errors, format_python_error
from .visualise import graphviz_available, open_ast_pdf

FRONTEND_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "frontend")
)

main_routes = Blueprint("main", __name__)
security_routes = Blueprint("security", __name__)
agent_routes = Blueprint("agent", __name__)
analysis_routes = Blueprint("analysis", __name__)
editor_routes = Blueprint("editor", __name__)
assistant_routes = Blueprint("assistant", __name__)
artifact_routes = Blueprint("artifacts", __name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _log_blocked_attack(endpoint, detection):
    logger.warning(
        "Blocked AI security attack endpoint=%s categories=%s risk_score=%s",
        endpoint,
        ",".join(detection["categories"]),
        detection["risk_score"],
    )


def _scan_assistant_input(prompt, code):
    prompt_result = detect_attack(prompt)
    source_result = detect_attack(code, content_type="code")
    categories = list(
        dict.fromkeys(prompt_result["categories"] + source_result["categories"])
    )
    risk_score = max(prompt_result["risk_score"], source_result["risk_score"])
    return {
        "detected": bool(categories),
        "decision": "block" if categories else "allow",
        "risk_score": risk_score,
        "severity": (
            prompt_result["severity"]
            if prompt_result["risk_score"] >= source_result["risk_score"]
            else source_result["severity"]
        ),
        "categories": categories,
        "reasons": list(
            dict.fromkeys(prompt_result["reasons"] + source_result["reasons"])
        ),
        "detection_latency_ms": round(
            prompt_result["detection_latency_ms"]
            + source_result["detection_latency_ms"],
            3,
        ),
    }



def _provider_error_response(error):
    classified = classify_provider_error(error, provider_display_name())
    if classified is None:
        return None
    payload, status = classified
    return jsonify(payload), status

def _request_data():
    return _parse_request_data(request)


def _valid_provider_base_url(value):
    try:
        parsed = urlsplit(value)
        if not (
            parsed.scheme.lower() in {"http", "https"}
            and bool(parsed.hostname)
            and parsed.username is None
            and parsed.password is None
            and not parsed.query
            and not parsed.fragment
        ):
            return False
        is_safe, _ = validate_url_against_ssrf(value, allow_local=True)
        return is_safe
    except ValueError:
        return False


def _record_start_time():
    request._start_time = time.time()


def _enforce_rate_limit():
    if request.method == "OPTIONS":
        return None
    if request.path in {"/health", "/health/live", "/health/ready", "/metrics", "/favicon.ico"}:
        return None
    client_ip = (
        request.headers.get("X-Forwarded-For", request.remote_addr or "127.0.0.1")
        .split(",")[0]
        .strip()
    )
    is_limited, remaining, retry_after = default_rate_limiter.is_rate_limited(
        client_ip, request.path
    )
    if is_limited:
        return (
            jsonify(
                {
                    "error": "Rate limit exceeded. Please slow down your requests.",
                    "status": "rate_limited",
                    "retry_after": retry_after,
                }
            ),
            429,
            {"Retry-After": str(int(retry_after) + 1)},
        )
    return None


def _enforce_csrf():
    if request.method in {"POST", "PUT", "DELETE", "PATCH"}:
        origin = request.headers.get("Origin")
        if origin:
            allowed_origins = current_app.config.get("CORS_ORIGINS", ())
            host_origin = f"{request.scheme}://{request.host}"
            if allowed_origins and origin != host_origin and origin not in allowed_origins:
                logger.warning("CSRF origin mismatch: origin=%s host=%s", origin, host_origin)
                return jsonify({"error": "Cross-Origin request blocked by CSRF policy."}), 403
    return None


def _api_key_required():
    if not current_app.config.get("REQUIRE_API_KEY", False):
        return False
    expected = (current_app.config.get("API_KEY") or "").strip()
    if not expected:
        return True
    authorization = request.headers.get("Authorization", "")
    if authorization.lower().startswith("bearer "):
        provided = authorization.split(None, 1)[1].strip()
    else:
        provided = request.headers.get("X-API-Key", "").strip()
    return not provided or not secrets.compare_digest(provided, expected)


def _enforce_model_api_key():
    if request.method == "OPTIONS":
        return None
    protected_paths = {
        "/api/settings",
        "/api/test-provider",
        "/generate",
        "/assist/ai",
        "/assistant",
        "/assistant/intent",
        "/assistant/improve",
        "/agent/run",
        "/agent/optimize",
        "/agent/simulate-attacks",
        "/agent/fix-attacks",
        "/agent/multi-agent-workflow",
        "/agent/professor-student",
        "/agentic/run",
        "/agentic/action",
        "/open_ast_pdf",
        "/download_ast_pdf",
    }
    agentic_session_path = request.path.startswith(
        ("/agentic/session/", "/agentic/stream/", "/agentic/cancel/")
    ) or request.path == "/agentic/action"
    is_project_path = request.path.startswith("/api/project/")
    if request.path not in protected_paths and not agentic_session_path and not is_project_path:
        return None
    if agentic_session_path:
        has_session_token = bool(
            request.headers.get("X-Session-Token")
            or request.args.get("ticket")
            or any(cookie_name.startswith("ast_session_") for cookie_name in request.cookies)
            or (request.is_json and (request.get_json(silent=True) or {}).get("token"))
            or (request.is_json and (request.get_json(silent=True) or {}).get("owner_token"))
        )
        if has_session_token:
            return None
    if current_app.config.get("REQUIRE_API_KEY", False) and not (
        current_app.config.get("API_KEY") or ""
    ).strip():
        logger.error(
            "API key authentication is enabled, but no API_KEY is configured."
        )
        return jsonify(
            {
                "error": "API key authentication is enabled, but API_KEY is not configured on the server."
            }
        ), 503
    if _api_key_required():
        return jsonify(
            {
                "error": "Authentication required. Provide Authorization: Bearer <API_KEY> or X-API-Key."
            }
        ), 401
    return None


def _syntax_finding(source_code, severity):
    try:
        compile(source_code, "<editor-suggestion>", "exec")
    except SyntaxError as exc:
        return {
            "rule_id": "SYNTAX001",
            "severity": severity,
            "message": f"Python syntax is incomplete: {exc.msg}",
            "line": exc.lineno or 0,
            "column": exc.offset or 0,
        }
    return None


def after_request(response):
    logger.info(f"{request.method} {request.path} - {response.status_code}")
    origin = request.headers.get("Origin")
    allowed_origins = current_app.config["CORS_ORIGINS"]
    if origin:
        if "*" in allowed_origins:
            logger.warning(
                "Wildcard CORS origin is disabled for safety; use an explicit allowlist."
            )
            allowed_origins = ()
        if origin in allowed_origins:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Headers"] = (
                "Content-Type,Authorization,X-API-Key,X-Session-Token"
            )
            response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
            response.headers.add("Vary", "Origin")
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault(
        "Permissions-Policy", "geolocation=(), microphone=(), camera=()"
    )
    response.headers.setdefault("Cross-Origin-Opener-Policy", "same-origin")
    response.headers.setdefault("Cross-Origin-Resource-Policy", "same-origin")
    response.headers.setdefault(
        "Content-Security-Policy",
        "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; font-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; object-src 'none'; base-uri 'self';",
    )
    if current_app.config.get("IS_PRODUCTION") or request.is_secure:
        response.headers.setdefault(
            "Strict-Transport-Security", "max-age=31536000; includeSubDomains"
        )
    start_time = getattr(request, "_start_time", None)
    if start_time is not None:
        metrics_collector.record_request(response.status_code, time.time() - start_time)
    return response


def handle_internal_server_error(error):
    logger.exception("Internal server error: %s", error)
    return jsonify({
        "error": "An internal server error occurred. Details have been logged securely.",
        "status": "error",
    }), 500


def request_entity_too_large(error):
    return jsonify({"error": "Payload Too Large"}), error.code or 413


@main_routes.route("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@main_routes.route("/script.js")
def legacy_script():
    """Backward-compatible route serving workbench.js to legacy client requests."""
    return send_from_directory(FRONTEND_DIR, "workbench.js")


@main_routes.route("/health", methods=["GET"])
def health():
    ai_available = provider_ready(client)
    return jsonify(
        {
            "status": "ok",
            "name": "Intelligent Code Comment Generation via AST",
            "version": "2.0",
            "ai_available": ai_available,
            "ai_provider": provider_display_name(),
            "ai_model": model_provider.MODEL_NAME,
            "provider_status": model_provider.provider_connection_status()[0],
            "ast_pdf_available": graphviz_available(),
            "modules": [
                "assistant",
                "agent",
                "agentic",
                "attack_guard",
                "optimization_agent",
                "security_attack_agent",
                "security_fixing_agent",
                "multi_agent_orchestrator",
                "multi_agents",
                "professor_student_engine",
                "ast_analyzer",
                "code_improver",
                "code_analysis",
                "config",
                "editor_assist",
                "models",
                "model_provider",
                "pipeline",
                "prompt_builder",
                "provider_errors",
                "request_utils",
                "rules",
                "type_analyzer",
                "validator",
                "visualise",
            ],
        }
    )


@main_routes.route("/api/settings", methods=["GET"])
def get_settings_route():
    """Get active provider and docstring preferences."""
    return jsonify(get_current_settings())


@main_routes.route("/api/settings", methods=["POST"])
def update_settings_route():
    """Update runtime provider, key, model, or docstring style."""
    data = _request_data()
    provider = data.get("provider")
    if provider is not None and (
        not isinstance(provider, str)
        or provider.strip().lower() not in AppConfig.SUPPORTED_PROVIDERS
    ):
        return jsonify({"error": "Unsupported AI provider."}), 400
    for field in ("api_key", "model", "base_url", "docstring_style"):
        if data.get(field) is not None and not isinstance(data[field], str):
            return jsonify({"error": f"{field} must be a string."}), 400
    base_url = data.get("base_url")
    if base_url and (
        len(base_url) > 2048 or not _valid_provider_base_url(base_url)
    ):
        return jsonify(
            {"error": "Base URL must be a valid HTTP or HTTPS URL without credentials, query, or fragment."}
        ), 400
    docstring_style = data.get("docstring_style")
    if docstring_style is not None and docstring_style.strip().lower() not in {
        "google",
        "sphinx",
        "numpy",
        "standard",
    }:
        return jsonify({"error": "Unsupported docstring style."}), 400
    updated = update_provider_settings(
        provider=provider,
        api_key=data.get("api_key"),
        model=data.get("model"),
        base_url=base_url,
        docstring_style=docstring_style,
    )
    refresh_agentic_model_client()
    return jsonify(updated)


@main_routes.route("/api/test-provider", methods=["POST"])
def test_provider_route():
    """Test live connectivity to a model provider."""
    data = _request_data()
    provider = data.get("provider", AppConfig.AI_PROVIDER)
    api_key = data.get("api_key")
    model = data.get("model")
    base_url = data.get("base_url")
    if not isinstance(provider, str) or provider.strip().lower() not in AppConfig.SUPPORTED_PROVIDERS:
        return jsonify({"error": "Unsupported AI provider."}), 400
    for field, value in (("api_key", api_key), ("model", model), ("base_url", base_url)):
        if value is not None and not isinstance(value, str):
            return jsonify({"error": f"{field} must be a string."}), 400
    if base_url and (
        len(base_url) > 2048 or not _valid_provider_base_url(base_url)
    ):
        return jsonify(
            {"error": "Base URL must be a valid HTTP or HTTPS URL without credentials, query, or fragment."}
        ), 400
    result = test_provider_connectivity(
        provider=provider.strip().lower(),
        api_key=api_key,
        model=model,
        base_url=base_url,
    )
    return jsonify(result)


@security_routes.route("/security/evaluate", methods=["GET"])
def security_evaluate_route():
    """Run the deterministic, labeled attack simulation suite."""
    return jsonify(evaluate_attack_suite())


@security_routes.route("/security/simulate-custom-attack", methods=["POST"])
def security_simulate_custom_attack_route():
    """Simulate a targeted custom or preset attack payload against code or guardrails."""
    data = _request_data()
    payload = str(data.get("payload", "")).strip()
    attack_type = str(data.get("attack_type", "custom")).strip().lower()
    code = _extract_code(data) or ""

    if len(code) > current_app.config.get("MAX_SOURCE_LENGTH", 50000):
        return jsonify({"error": "Payload Too Large"}), 413
    if len(payload) > 4000:
        return jsonify({"error": "Payload is too long"}), 413

    if code:
        valid = validate_code(code)
        if valid is not True:
            formatted = format_python_error(code)
            return jsonify({
                "error": f"Syntax error in your code: {valid}",
                "interpreter_output": formatted,
            }), 400

    prompt_scan = detect_attack(payload, content_type="prompt") if payload else {"detected": False, "categories": [], "reasons": [], "detection_latency_ms": 0.5}
    code_scan = detect_attack(code, content_type="code") if code else {"detected": False, "categories": [], "reasons": []}

    ast_findings = []
    if code:
        try:
            sim_res = simulate_attacks(code)
            ast_findings = sim_res.get("attack_scenarios", [])
        except Exception as exc:
            logger.exception("Static security analysis failed during custom simulation")
            return jsonify({
                "error": "Static security analysis could not be completed.",
                "status": "failed",
                "error_type": type(exc).__name__,
            }), 500

    matched_scenario = None
    for sc in ast_findings:
        cat = sc.get("category", "").lower()
        if (
            ("sql" in attack_type and ("sql" in cat or "89" in sc.get("cwe", "").lower()))
            or (("cmd" in attack_type or "command" in attack_type or "code" in attack_type) and ("command" in cat or "code" in cat or "78" in sc.get("cwe", "").lower() or "94" in sc.get("cwe", "").lower()))
            or (("traversal" in attack_type or "path" in attack_type) and ("path" in cat or "traversal" in cat or "22" in sc.get("cwe", "").lower()))
            or (("pickle" in attack_type or "deserial" in attack_type) and ("deserial" in cat or "502" in sc.get("cwe", "").lower()))
            or (("ssrf" in attack_type or "request" in attack_type) and ("ssrf" in cat or "918" in sc.get("cwe", "").lower()))
            or (("redos" in attack_type or "regex" in attack_type) and ("redos" in cat or "1333" in sc.get("cwe", "").lower() or "dos" in cat))
            or (("xxe" in attack_type or "xml" in attack_type) and ("xml" in cat or "xxe" in cat or "611" in sc.get("cwe", "").lower()))
            or (("hash" in attack_type or "crypto" in attack_type or "md5" in attack_type) and ("crypt" in cat or "hash" in cat or "327" in sc.get("cwe", "").lower()))
            or (("temp" in attack_type or "mktemp" in attack_type) and ("temp" in cat or "377" in sc.get("cwe", "").lower()))
            or (("debug" in attack_type) and ("debug" in cat or "disclosure" in cat or "215" in sc.get("cwe", "").lower()))
            or (("ssl" in attack_type or "tls" in attack_type) and ("transport" in cat or "ssl" in cat or "295" in sc.get("cwe", "").lower()))
            or (("secret" in attack_type or "token" in attack_type or "credential" in attack_type) and ("secret" in cat or "credential" in cat or "798" in sc.get("cwe", "").lower()))
        ):
            matched_scenario = sc
            break

    attack_type_matched = matched_scenario is not None
    if not matched_scenario and ast_findings:
        matched_scenario = ast_findings[0]

    detected = prompt_scan["detected"] or code_scan["detected"] or (matched_scenario is not None)

    target_line = 0
    vuln_code = ""
    mitigation = "Implement strict input sanitization and parameterized queries."
    trace = ""
    cwe = "CWE-20: Improper Input Validation"
    cvss = 5.3

    if matched_scenario:
        cwe = matched_scenario.get("cwe", "CWE-20: Improper Input Validation")
        cvss = 9.8 if matched_scenario.get("severity") == "critical" else 7.5
        target_line = matched_scenario.get("target_line", 1)
        vuln_code = matched_scenario.get("vulnerable_code", "")
        mitigation = matched_scenario.get("mitigation", "Implement strict input sanitization and parameterized queries.")
        trace = (
            f"SENTINEL static analysis identified a vulnerable sink at line {target_line}: '{vuln_code}'. "
            f"Payload '{payload}' targets this vulnerability pattern. {matched_scenario.get('simulation_trace', '')}"
        )
    elif prompt_scan["detected"]:
        cwe = "CWE-77: Command / Prompt Injection"
        cvss = 8.5
        target_line = 0
        vuln_code = "AI Prompt Interface"
        mitigation = "Deterministic Guardrails blocked adversarial tokens before model execution."
        trace = f"Guardrail Alert: {', '.join(prompt_scan.get('reasons', []))}. Payload attempted prompt injection / policy bypass."
    else:
        is_sqli = any(kw in payload.upper() for kw in ("' OR", "UNION SELECT", "DROP TABLE", "--"))
        is_cmdi = any(kw in payload for kw in (";", "|", "&&", "`", "$("))
        is_redos = "(" in payload and "+" in payload and "*" in payload
        is_xxe = "<!ENTITY" in payload.upper() or "<!DOCTYPE" in payload.upper()
        is_ssrf = any(marker in payload.lower() for marker in ("169.254.169.254", "metadata", "localhost", "127.0.0.1"))
        if is_sqli:
            cwe = "CWE-89: SQL Injection"
            cvss = 8.8
            mitigation = "Use parameterized SQL queries with bind variables (? or %s)."
            trace = f"SQL Injection signature detected in payload '{payload}'. In an unescaped query, this alters SQL syntax logic."
            detected = True
        elif is_cmdi:
            cwe = "CWE-78: OS Command Injection"
            cvss = 9.8
            mitigation = "Avoid shell=True and pass argument lists to subprocess.run."
            trace = f"Shell command metacharacter detected in payload '{payload}'. This triggers arbitrary shell execution."
            detected = True
        elif is_redos:
            cwe = "CWE-1333: Inefficient Regular Expression Complexity (ReDoS)"
            cvss = 7.5
            mitigation = "Simplify regex quantifier nesting and use linear-time regex engines."
            trace = f"Exponential backtracking regex bomb detected '{payload}'. Catastrophic backtracking can freeze CPU worker threads."
            detected = True
        elif is_xxe:
            cwe = "CWE-611: XML External Entity Reference (XXE)"
            cvss = 8.6
            mitigation = "Disable DTD processing and external entity resolution via defusedxml."
            trace = f"XML External Entity (XXE) injection payload detected '{payload}'. Unrestricted parser entity resolution can leak files or access internal networks."
            detected = True
        elif is_ssrf:
            cwe = "CWE-918: Server-Side Request Forgery (SSRF)"
            cvss = 8.6
            mitigation = "Validate destination IP/hostname against private subnet allowlists and block cloud metadata IP (169.254.169.254)."
            trace = f"Cloud metadata / internal network SSRF target detected '{payload}'. Unsanitized fetches can leak IAM instance credentials."
            detected = True
        else:
            cwe = "CWE-20: Improper Input Validation" 
            cvss = 5.3
            mitigation = "Enforce allowlists and schema validation on all untrusted inputs."
            trace = f"Custom payload '{payload}' tested against AST model. No immediate critical exploit path detected in active source."

    resolved_ast_nodes = [
        {
            "scenario_id": scenario.get("id"),
            "line": scenario.get("target_line", 0),
            "ast_node_type": scenario.get("ast_node_type"),
            "ast_sink_symbol": scenario.get("ast_sink_symbol"),
            "ast_security_comment": scenario.get("ast_security_comment"),
            "matched": scenario is matched_scenario,
        }
        for scenario in ast_findings
    ]
    ast_sink_matched = matched_scenario is not None
    static_match_status = (
        "attack_type_ast_pattern_matched"
        if attack_type_matched
        else "source_ast_finding_payload_link_unresolved"
        if ast_sink_matched
        else "payload_signature_only"
        if detected
        else "no_static_match"
    )
    execution_notice = (
        "Static AST simulation only: no payload, user code, shell command, database "
        "query, network request, or filesystem operation was executed."
    )
    defense_comment = (
        f"# [AST-DEFENSE] {mitigation}"
        if ast_sink_matched
        else (
            "# [AST-DEFENSE] No source AST sink was resolved; "
            f"{mitigation}"
        )
    )
    ast_trace_steps = [
        {
            "step": 1,
            "name": "AST Lexical & Token Scan",
            "status": "completed",
            "details": {
                "description": "Guardrail inspection of payload and source-code tokens.",
                "payload_detected": prompt_scan.get("detected", False),
                "payload_categories": prompt_scan.get("categories", []),
                "payload_reasons": prompt_scan.get("reasons", []),
                "code_detected": code_scan.get("detected", False),
                "code_categories": code_scan.get("categories", []),
                "source_code_provided": bool(code),
            },
        },
        {
            "step": 2,
            "name": "AST Node & Sink Resolution",
            "status": "resolved" if ast_sink_matched else "unresolved",
            "details": {
                "description": "Resolved source AST nodes and sink symbols; line numbers refer to the submitted source.",
                "resolved_nodes": resolved_ast_nodes,
                "matched_line": target_line,
                "matched_node_type": (
                    matched_scenario.get("ast_node_type")
                    if matched_scenario
                    else None
                ),
                "matched_sink_symbol": (
                    matched_scenario.get("ast_sink_symbol")
                    if matched_scenario
                    else None
                ),
            },
        },
        {
            "step": 3,
            "name": "Static Taint & Impact Analysis",
            "status": "completed",
            "details": {
                "description": "Static pattern association only; this is not runtime taint propagation or exploit execution.",
                "static_match_status": static_match_status,
                "payload_interaction": (
                    f"The attack type matched the static "
                    f"{matched_scenario.get('category', 'detected')} AST sink pattern; "
                    "the payload itself was not executed or dynamically traced."
                    if attack_type_matched and matched_scenario
                    else (
                        "A source AST finding was selected for context, but a specific "
                        "payload-to-sink association was not resolved."
                        if matched_scenario
                        else "No source AST sink was matched to the submitted payload."
                    )
                ),
                "impact": (
                    matched_scenario.get("impact")
                    if matched_scenario
                    else trace
                ),
                "cwe": cwe,
                "cvss": cvss,
                "code_execution": False,
                "execution_notice": execution_notice,
            },
        },
        {
            "step": 4,
            "name": "REMEDY AST Remediation & Comment",
            "status": "recommendation_ready",
            "details": {
                "description": "Recommended defensive code change and AST security-comment specification; source code was not modified.",
                "recommended_code_fix": mitigation,
                "comment_specification": defense_comment,
                "source_line": target_line if ast_sink_matched else None,
                "warning_comment": (
                    matched_scenario.get("ast_security_comment")
                    if matched_scenario
                    else None
                ),
            },
        },
    ]

    return jsonify({
        "status": "success",
        "payload": payload,
        "attack_type": attack_type,
        "detected": detected,
        "blocked_by_guard": prompt_scan["detected"],
        "exploit_successful": matched_scenario is not None,
        "severity": "critical" if cvss >= 9.0 else "high" if cvss >= 7.0 else "medium",
        "risk_score": int(cvss * 10),
        "cvss": cvss,
        "cwe": cwe,
        "target_line": target_line,
        "vulnerable_code": vuln_code,
        "exploit_trace": trace,
        "mitigation": mitigation,
        "latency_ms": prompt_scan.get("detection_latency_ms", 1.2),
        "ast_trace_steps": ast_trace_steps,
    })


@agent_routes.route("/agent/run", methods=["POST"])
def agent_run_route():
    data = _request_data()
    code = _extract_code(data)
    task = data.get("task", "")
    if code is None:
        return jsonify({"error": "Code must be a string"}), 400
    if not code.strip():
        return jsonify({"error": "No code provided"}), 400
    if len(code) > current_app.config["MAX_SOURCE_LENGTH"]:
        return jsonify({"error": "Payload Too Large"}), 413
    if not isinstance(task, str):
        return jsonify({"error": "Task must be a string"}), 400
    if len(task) > 4000:
        return jsonify({"error": "Task is too long"}), 413

    attack_detection = _scan_assistant_input(task, code)
    if attack_detection["detected"]:
        _log_blocked_attack("/agent/run", attack_detection)
        return jsonify(
            {
                "error": "Agent run blocked by the security layer.",
                "security_blocked": True,
                "attack_detection": attack_detection,
            }
        ), 422

    valid = validate_code(code)
    if valid is not True:
        formatted = format_python_error(code)
        return jsonify(
            {
                "error": f"Syntax error in your code: {valid}",
                "interpreter_output": formatted,
            }
        ), 400
    if client is None:
        return jsonify(
            {
                "error": "The AI agent requires a configured model. Set API_KEY and restart the server."
            }
        ), 503

    try:
        analysis = analyze_code(code)
        analysis["warnings"].extend(
            _undefined_name_findings(check_undefined_names(code))
        )
        return jsonify(run_agent(code, task, analysis, client))
    except AgentRunError as exc:
        logger.warning("AI agent run rejected (%s)", type(exc).__name__)
        return jsonify({"error": str(exc), "agent_status": "failed"}), 502
    except Exception as exc:
        logger.exception("AI agent run failed")
        provider_error = _provider_error_response(exc)
        if provider_error:
            return provider_error
        return jsonify({"error": "AI agent run failed", "agent_status": "failed"}), 502


@agent_routes.route("/agent/optimize", methods=["POST"])
def agent_optimize_route():
    data = _request_data()
    code = _extract_code(data)
    if code is None:
        return jsonify({"error": "Code must be a string"}), 400
    if not code.strip():
        return jsonify({"error": "No code provided"}), 400
    if len(code) > current_app.config["MAX_SOURCE_LENGTH"]:
        return jsonify({"error": "Payload Too Large"}), 413

    valid = validate_code(code)
    if valid is not True:
        formatted = format_python_error(code)
        return jsonify(
            {
                "error": f"Syntax error in your code: {valid}",
                "interpreter_output": formatted,
            }
        ), 400

    try:
        return jsonify(optimize_code(code, model_client=client))
    except Exception as exc:
        logger.exception("Code optimization agent failed")
        provider_error = _provider_error_response(exc)
        if provider_error:
            return provider_error
        return jsonify({"error": f"Code optimization agent failed: {exc}", "status": "failed"}), 500


@agent_routes.route("/agent/simulate-attacks", methods=["POST"])
def agent_simulate_attacks_route():
    data = _request_data()
    code = _extract_code(data)
    if code is None:
        return jsonify({"error": "Code must be a string"}), 400
    if not code.strip():
        return jsonify({"error": "No code provided"}), 400
    if len(code) > current_app.config["MAX_SOURCE_LENGTH"]:
        return jsonify({"error": "Payload Too Large"}), 413

    valid = validate_code(code)
    if valid is not True:
        formatted = format_python_error(code)
        return jsonify(
            {
                "error": f"Syntax error in your code: {valid}",
                "interpreter_output": formatted,
            }
        ), 400

    try:
        return jsonify(simulate_attacks(code, model_client=client))
    except Exception as exc:
        logger.exception("Attack simulation agent failed")
        provider_error = _provider_error_response(exc)
        if provider_error:
            return provider_error
        return jsonify({"error": f"Attack simulation agent failed: {exc}", "status": "failed"}), 500


@agent_routes.route("/agent/fix-attacks", methods=["POST"])
def agent_fix_attacks_route():
    data = _request_data()
    code = _extract_code(data)
    if code is None:
        return jsonify({"error": "Code must be a string"}), 400
    if not code.strip():
        return jsonify({"error": "No code provided"}), 400
    if len(code) > current_app.config["MAX_SOURCE_LENGTH"]:
        return jsonify({"error": "Payload Too Large"}), 413

    valid = validate_code(code)
    if valid is not True:
        formatted = format_python_error(code)
        return jsonify(
            {
                "error": f"Syntax error in your code: {valid}",
                "interpreter_output": formatted,
            }
        ), 400

    try:
        return jsonify(fix_attack_vulnerabilities(code, model_client=client))
    except Exception as exc:
        logger.exception("Attack fixing agent failed")
        provider_error = _provider_error_response(exc)
        if provider_error:
            return provider_error
        return jsonify({"error": f"Attack fixing agent failed: {exc}", "status": "failed"}), 500


@agent_routes.route("/agent/multi-agent-workflow", methods=["POST"])
def agent_multi_agent_workflow_route():
    data = _request_data()
    code = _extract_code(data)
    if code is None:
        return jsonify({"error": "Code must be a string"}), 400
    if not code.strip():
        return jsonify({"error": "No code provided"}), 400
    if len(code) > current_app.config["MAX_SOURCE_LENGTH"]:
        return jsonify({"error": "Payload Too Large"}), 413

    valid = validate_code(code)
    if valid is not True:
        formatted = format_python_error(code)
        return jsonify(
            {
                "error": f"Syntax error in your code: {valid}",
                "interpreter_output": formatted,
            }
        ), 400

    if not agentic_model_ready():
        return jsonify({
            "error": (
                "A ready AI model provider is required for this workflow. "
                "Configure and test a provider in Settings, then retry."
            ),
            "configuration_required": True,
            "status": "blocked",
        }), 503

    try:
        full_pipeline = bool(data.get("full_pipeline") or data.get("stages") == 6)
        include_docstrings = bool(data.get("include_docstrings", False))
        task = (
            "Perform a comprehensive full end-to-end multi-agent optimization, "
            "security defense, documentation, and non-regression audit."
            if full_pipeline
            else "Review code security and quality, and document public callables."
            if include_docstrings
            else "Review code security and quality."
        )
        result = run_agentic_workflow_sync(code, task, auto_approve=False)
        task_results = result.get("results", [])
        task_states = result.get("tasks", {})
        stages = []
        for item in task_results:
            state = task_states.get(item.get("task_id"), {})
            stages.append({
                "stage": state.get("stage"),
                "agent_id": item.get("agent_key"),
                "agent_name": state.get("agent_name", item.get("agent_key")),
                "status": item.get("status", "failed"),
                "duration_ms": item.get("duration_ms", 0),
                "findings_count": len(item.get("findings", [])),
                "findings": item.get("findings", []),
                "summary": item.get("summary", ""),
                "details": item.get("summary", ""),
                "execution_mode": item.get("execution_mode"),
                "fallback_reason": item.get("fallback_reason"),
                "code_modified": bool(state.get("candidate_proposed")),
                "candidate_status": state.get("candidate_status"),
            })
        timeline = stages if full_pipeline else stages[:4]
        if result.get("status") != "completed":
            return jsonify({
                **result,
                "workflow": "multi_agent_collaboration",
                "stages": stages,
                "timeline": timeline,
            }), 502

        tool_observations = result.get("tool_observations", [])
        security_checks = sum(
            int(
                observation.get("result", {})
                .get("result", {})
                .get("total_checks_run", 0)
            )
            for observation in tool_observations
            if observation.get("tool") == "probe_security_vulnerabilities"
        )
        findings_remediated = sum(
            int(
                observation.get("result", {})
                .get("result", {})
                .get("neutralized_count", 0)
            )
            for observation in tool_observations
            if observation.get("tool") == "synthesize_defensive_patch"
        )
        agents = {
            stage["agent_id"]: {
                "status": stage["status"],
                "summary": stage["summary"],
                "findings": stage["findings"],
                "execution_mode": stage["execution_mode"],
                "fallback_reason": stage["fallback_reason"],
                "code_modified": stage["code_modified"],
            }
            for stage in stages
        }
        return jsonify({
            **result,
            "workflow": "multi_agent_collaboration",
            "stages": stages,
            "timeline": timeline,
            "final_hardened_code": result.get("final_code", code),
            "agents": agents,
            "summary": {
                "overall_health": (
                    "Verified" if result.get("audit_passed") else "Review required"
                ),
                "audit_passed": result.get("audit_passed"),
                "execution_mode": result.get("execution_mode"),
                "model_call_count": result.get("model_call_count", 0),
                "static_checks_run": security_checks,
                "findings_remediated": findings_remediated,
            },
        })
    except Exception as exc:
        logger.exception("Multi-agent workflow failed")
        provider_error = _provider_error_response(exc)
        if provider_error:
            return provider_error
        return jsonify({"error": f"Multi-agent workflow failed: {exc}", "status": "failed"}), 500


@agent_routes.route("/agent/professor-student", methods=["POST"])
def agent_professor_student_route():
    data = _request_data()
    code = _extract_code(data)
    if code is None:
        return jsonify({"error": "Code must be a string"}), 400
    if not code.strip():
        return jsonify({"error": "No code provided"}), 400
    if len(code) > current_app.config["MAX_SOURCE_LENGTH"]:
        return jsonify({"error": "Payload Too Large"}), 413

    # Security pre-scan against adversarial prompt injection / policy bypass
    attack_detection = _scan_assistant_input("", code)
    if attack_detection["detected"]:
        _log_blocked_attack("/agent/professor-student", attack_detection)
        return jsonify(
            {
                "error": "Autonomous review was blocked by the security layer.",
                "security_blocked": True,
                "attack_detection": attack_detection,
            }
        ), 422

    valid = validate_code(code)
    if valid is not True:
        formatted = format_python_error(code)
        return jsonify(
            {
                "error": f"Syntax error in your code: {valid}",
                "interpreter_output": formatted,
            }
        ), 400

    max_iterations = data.get("max_iterations", 5)
    try:
        max_iterations = max(1, min(10, int(max_iterations)))
    except (ValueError, TypeError):
        max_iterations = 5

    try:
        orchestrator = ProfessorStudentOrchestrator(model_client=client, max_iterations=max_iterations)
        result = orchestrator.run(code)
        return jsonify(result)
    except Exception as exc:
        logger.exception("Autonomous review cycle failed")
        provider_error = _provider_error_response(exc)
        if provider_error:
            return provider_error
        return jsonify({"error": f"Autonomous review failed: {exc}", "status": "failed"}), 500


@analysis_routes.route("/analyze", methods=["POST"])
def analyze_route():
    data = _request_data()
    code = _extract_code(data)
    if code is None:
        return jsonify({"error": "Code must be a string"}), 400
    if not code.strip():
        return jsonify({"error": "No code provided"}), 400
    if len(code) > current_app.config["MAX_SOURCE_LENGTH"]:
        return jsonify({"error": "Payload Too Large"}), 413

    valid = validate_code(code)
    if valid is not True:
        formatted = format_python_error(code)
        syntax_finding = {
            "rule_id": "SYNTAX001",
            "severity": "error",
            "message": f"Syntax error in your code: {valid}",
            "line": 1,
        }
        return jsonify(
            {
                "error": f"Syntax error in your code: {valid}",
                "interpreter_output": formatted,
                "warnings": [syntax_finding],
                "quality_score": 0,
                "quality_summary": summarize_quality([syntax_finding]),
                "review_score": build_review_score([syntax_finding]),
            }
        ), 400

    undefined = check_undefined_names(code)
    name_warnings = format_name_errors(undefined)
    name_findings = _undefined_name_findings(undefined)

    try:
        analysis = analyze_code(code)
        warnings = analysis["warnings"] + name_findings
        analysis["warnings"] = warnings
        quality_summary = summarize_quality(warnings)
        return jsonify(
            {
                "analysis": analysis,
                "warnings": warnings,
                "quality_summary": quality_summary,
                "quality_score": quality_summary["score"],
                "review_score": build_review_score(warnings),
                "execution_status": "not_executed",
                "name_errors": name_warnings,
                "name_findings": name_findings,
                "smart_explanations": build_smart_ast_explanations(code),
            }
        )
    except Exception as exc:
        logger.exception("Code analysis failed")
        provider_error = _provider_error_response(exc)
        if provider_error:
            return provider_error
        return jsonify({"error": "Code analysis failed"}), 500


@analysis_routes.route("/generate", methods=["POST"])
def generate():
    data = _request_data()
    code = _extract_code(data)
    if code is None:
        return jsonify({"error": "Code must be a string"}), 400
    if not code.strip():
        return jsonify({"error": "No code provided"}), 400
    if len(code) > current_app.config["MAX_SOURCE_LENGTH"]:
        return jsonify({"error": "Payload Too Large"}), 413

    valid = validate_code(code)
    if valid is not True:
        formatted = format_python_error(code)
        syntax_finding = {
            "rule_id": "SYNTAX001",
            "severity": "error",
            "message": f"Syntax error in your code: {valid}",
            "line": 1,
        }
        return jsonify(
            {
                "error": f"Syntax error in your code: {valid}",
                "interpreter_output": formatted,
                "warnings": [syntax_finding],
                "quality_score": 0,
                "quality_summary": summarize_quality([syntax_finding]),
                "review_score": build_review_score([syntax_finding]),
            }
        ), 400

    docstring_style = data.get("docstring_style")
    if docstring_style is not None and (
        not isinstance(docstring_style, str)
        or docstring_style.strip().lower() not in {
            "google",
            "sphinx",
            "numpy",
            "standard",
        }
    ):
        return jsonify({"error": "Unsupported docstring style."}), 400
    if isinstance(docstring_style, str):
        docstring_style = docstring_style.strip().lower()

    remediate_and_comment = data.get("remediate_and_comment", False)
    if not isinstance(remediate_and_comment, bool):
        return jsonify({"error": "remediate_and_comment must be a boolean."}), 400

    undefined = check_undefined_names(code)
    name_warnings = format_name_errors(undefined)
    name_findings = _undefined_name_findings(undefined)

    attack_detection = detect_attack(code, content_type="code")
    try:
        preflight = analyze_code(code)
        preflight_warnings = preflight["warnings"] + name_findings
        security_warnings = [
            warning
            for warning in preflight_warnings
            if warning["rule_id"].startswith("SEC")
        ]
        if attack_detection["detected"] and not security_warnings:
            security_warnings = [
                {
                    "rule_id": "SEC006",
                    "severity": "error",
                    "message": "Adversarial instructions or sensitive-data transfer detected before AI generation.",
                    "line": 0,
                }
            ]
            preflight_warnings.extend(security_warnings)
        preflight["warnings"] = preflight_warnings

        has_security_findings = bool(security_warnings) or bool(
            attack_detection.get("detected")
        )
        if has_security_findings:
            q_summary = summarize_quality(preflight_warnings)
            if not remediate_and_comment:
                if attack_detection.get("detected"):
                    _log_blocked_attack("/generate", attack_detection)
                return jsonify(
                    {
                        "error": "Security risks detected. Fix the findings before generating comments. Source code was not executed.",
                        "security_blocked": True,
                        "execution_status": "not_executed",
                        "warnings": security_warnings,
                        "quality_summary": q_summary,
                        "quality_score": q_summary["score"],
                        "review_score": build_review_score(preflight_warnings),
                        "analysis": preflight,
                        "attack_detection": attack_detection,
                        "preview_security_annotated_code": _fallback_comment_code(code),
                    }
                ), 409

            fix_result = fix_attack_vulnerabilities(code, model_client=client)
            hardened_code = fix_result.get("fixed_code")
            if not isinstance(hardened_code, str) or validate_code(hardened_code) is not True:
                return jsonify(
                    {
                        "error": "Security remediation did not produce valid Python code.",
                        "security_blocked": True,
                        "remediation_failed": True,
                        "execution_status": "not_executed",
                        "warnings": security_warnings,
                    }
                ), 422
            verification = fix_result.get("verification", {})
            if (
                fix_result.get("remaining_vulnerabilities", 0) > 0
                or verification.get("all_detected_static_findings_addressed") is False
            ):
                return jsonify(
                    {
                        "error": "Security remediation could not verify that all detected findings were addressed.",
                        "security_blocked": True,
                        "remediation_failed": True,
                        "execution_status": "not_executed",
                        "warnings": security_warnings,
                        "security_fixes_applied": fix_result.get(
                            "defensive_controls", []
                        ),
                        "security_remediation": {
                            "status": fix_result.get("status"),
                            "remaining_vulnerabilities": fix_result.get(
                                "remaining_vulnerabilities"
                            ),
                            "verification": verification,
                        },
                    }
                ), 422
            pipeline_result = run_pipeline(
                hardened_code,
                docstring_style=docstring_style,
                security_controls=fix_result.get("defensive_controls", []),
            )
            updated_analysis = pipeline_result["analysis"]
            hardened_undefined = check_undefined_names(hardened_code)
            hardened_name_warnings = format_name_errors(hardened_undefined)
            hardened_name_findings = _undefined_name_findings(hardened_undefined)
            updated_analysis["warnings"].extend(hardened_name_findings)
            quality_summary = summarize_quality(updated_analysis["warnings"])
            return jsonify(
                {
                    "commented_code": pipeline_result["commented_code"],
                    "execution_status": "not_executed",
                    "analysis": updated_analysis,
                    "warnings": updated_analysis["warnings"],
                    "quality_summary": quality_summary,
                    "cc_summary": {
                        "file_cc": updated_analysis["summary"]["file_cc"],
                        "per_function": {
                            item["name"]: item["complexity"]
                            for item in updated_analysis["functions"]
                        },
                        "threshold": CC_THRESHOLD,
                    },
                    "validation": pipeline_result["validation"],
                    "ai_status": pipeline_result["method"],
                    "generation_notice": pipeline_result["generation_notice"],
                    "smart_explanations": build_smart_ast_explanations(hardened_code),
                    "prompt_payload": _build_prompt_payload(
                        hardened_code, updated_analysis
                    ),
                    "quality_score": quality_summary["score"],
                    "review_score": build_review_score(updated_analysis["warnings"]),
                    "name_errors": hardened_name_warnings,
                    "name_findings": hardened_name_findings,
                    "original_code": code,
                    "remediated_before_commenting": True,
                    "security_fixes_applied": fix_result.get(
                        "defensive_controls", []
                    ),
                    "security_remediation": {
                        "status": fix_result.get("status"),
                        "remaining_vulnerabilities": fix_result.get(
                            "remaining_vulnerabilities"
                        ),
                        "verification": fix_result.get("verification", {}),
                    },
                    "original_security_warnings": security_warnings,
                    "attack_detection": attack_detection,
                }
            )
        pipeline_result = run_pipeline(code, preflight, docstring_style=docstring_style)
    except CommentGenerationError as exc:
        logger.warning("Comment generation failed: %s", exc)
        provider_error = _provider_error_response(exc.__cause__)
        if provider_error:
            return provider_error
        return jsonify({"error": str(exc)}), 502
    except Exception as exc:
        logger.exception("Code generation pipeline failed")
        provider_error = _provider_error_response(exc)
        if provider_error:
            return provider_error
        return jsonify({"error": "Code generation pipeline failed"}), 500

    analysis = pipeline_result["analysis"]
    analysis["warnings"].extend(name_findings)
    quality_summary = summarize_quality(analysis["warnings"])
    review_score = build_review_score(analysis["warnings"])
    quality_score = quality_summary["score"]
    return jsonify(
        {
            "commented_code": pipeline_result["commented_code"],
            "execution_status": "not_executed",
            "analysis": analysis,
            "warnings": analysis["warnings"],
            "quality_summary": quality_summary,
            "cc_summary": {
                "file_cc": analysis["summary"]["file_cc"],
                "per_function": {
                    item["name"]: item["complexity"] for item in analysis["functions"]
                },
                "threshold": CC_THRESHOLD,
            },
            "validation": pipeline_result["validation"],
            "ai_status": pipeline_result["method"],
            "generation_notice": pipeline_result["generation_notice"],
            "smart_explanations": build_smart_ast_explanations(code),
            "prompt_payload": _build_prompt_payload(code, analysis),
            "quality_score": quality_score,
            "review_score": review_score,
            "name_errors": name_warnings,
        }
    )


@editor_routes.route("/assist", methods=["POST"])
def assist_route():
    data = _request_data()
    code = data.get("code", "")
    cursor = data.get("cursor", 0)
    if not isinstance(code, str):
        return jsonify({"error": "Code must be a string"}), 400
    if len(code) > current_app.config["MAX_SOURCE_LENGTH"]:
        return jsonify({"error": "Payload Too Large"}), 413
    if not _valid_cursor(cursor):
        return jsonify(
            {
                "error": "Cursor must be an integer offset or contain integer line and column values"
            }
        ), 400
    try:
        return jsonify(editor_assist(code, cursor))
    except Exception as exc:
        logger.exception("Editor assistance failed")
        provider_error = _provider_error_response(exc)
        if provider_error:
            return provider_error
        return jsonify({"error": "Editor assistance failed"}), 500


@editor_routes.route("/assist/ai", methods=["POST"])
def live_ai_assist_route():
    data = _request_data()
    code = _extract_code(data)
    cursor = data.get("cursor", 0)
    if code is None:
        return jsonify({"error": "Code must be a string"}), 400
    if not code.strip():
        return jsonify({"error": "No code provided"}), 400
    if len(code) > current_app.config["MAX_SOURCE_LENGTH"]:
        return jsonify({"error": "Payload Too Large"}), 413
    if not _valid_cursor(cursor):
        return jsonify(
            {
                "error": "Cursor must be an integer offset or contain integer line and column values"
            }
        ), 400
    attack_detection = detect_attack(code, content_type="code")
    if attack_detection["detected"]:
        _log_blocked_attack("/assist/ai", attack_detection)
        cursor_index = _cursor_to_offset(code, cursor)
        return jsonify(
            {
                "suggestion": "",
                "suggestion_type": "ai_completion",
                "source": "ai",
                "replacement_range": {
                    "start": _to_utf16_offset(code, cursor_index),
                    "end": _to_utf16_offset(code, cursor_index),
                },
                "cursor_offset": _to_utf16_offset(code, cursor_index),
                "explanation": "AI completion was blocked because the source contains adversarial instructions.",
                "validation_status": "rejected",
                "warnings": [
                    {
                        "rule_id": "SEC006",
                        "severity": "error",
                        "message": "Adversarial instructions in source were blocked before sending it to the AI model.",
                        "line": 0,
                    }
                ],
                "attack_detection": attack_detection,
            }
        )
    if client is None:
        return jsonify(
            {
                "error": "Live AI suggestions are unavailable. Configure API_KEY to enable them."
            }
        ), 503

    try:
        suggestion = build_live_ai_suggestion(code, cursor, client)
    except UnsafeAISuggestionError:
        logger.warning("Rejected unsafe or adversarial AI completion at /assist/ai")
        suggestion = ""
        cursor_index = _cursor_to_offset(code, cursor)
        warnings = [
            {
                "rule_id": "SEC001",
                "severity": "error",
                "message": "AI suggestion was rejected because it introduced unsafe execution logic or prompt-injection content.",
                "line": 0,
            }
        ]
        return jsonify(
            {
                "suggestion": suggestion,
                "suggestion_type": "ai_completion",
                "source": "ai",
                "replacement_range": {
                    "start": _to_utf16_offset(code, cursor_index),
                    "end": _to_utf16_offset(code, cursor_index),
                },
                "cursor_offset": _to_utf16_offset(code, cursor_index),
                "explanation": "AI-generated completion was rejected because it introduced unsafe logic.",
                "validation_status": "rejected",
                "warnings": warnings,
            }
        )
    except Exception as exc:
        logger.exception("Live AI completion request failed")
        provider_error = _provider_error_response(exc)
        if provider_error:
            return provider_error
        return jsonify(
            {
                "error": "The live AI provider request failed. Check the server log for its diagnostic."
            }
        ), 502
    try:
        cursor_index = _cursor_to_offset(code, cursor)
        candidate = code[:cursor_index] + suggestion + code[cursor_index:]
        original_syntax = _syntax_finding(code, "warning")
        candidate_syntax = _syntax_finding(candidate, "error")
        original_valid = original_syntax is None
        candidate_valid = candidate_syntax is None
        warnings = []
        validation_status = "needs_review"

        if not candidate_valid:
            warnings.append(candidate_syntax)
            if original_valid:
                validation_status = "rejected"
        elif not original_valid:
            warnings.append(original_syntax)
        elif original_valid:
            original_security = [
                warning
                for warning in analyze_code(code)["warnings"]
                if warning["rule_id"].startswith("SEC")
            ]
            candidate_security = [
                warning
                for warning in analyze_code(candidate)["warnings"]
                if warning["rule_id"].startswith("SEC")
            ]
            original_counts = {}
            for warning in original_security:
                key = warning["rule_id"], warning["message"]
                original_counts[key] = original_counts.get(key, 0) + 1
            remaining_original = original_counts.copy()
            added_security = []
            for warning in candidate_security:
                key = warning["rule_id"], warning["message"]
                if remaining_original.get(key, 0):
                    remaining_original[key] -= 1
                else:
                    added_security.append(warning)
            if added_security:
                warnings.extend(added_security)
                validation_status = "rejected"
            else:
                warnings.extend(original_security)
                validation_status = "needs_review" if original_security else "validated"
        if validation_status == "rejected":
            suggestion = ""
        return jsonify(
            {
                "suggestion": suggestion,
                "suggestion_type": "ai_completion",
                "source": "ai",
                "replacement_range": {
                    "start": _to_utf16_offset(code, cursor_index),
                    "end": _to_utf16_offset(code, cursor_index),
                },
                "cursor_offset": _to_utf16_offset(
                    candidate, cursor_index + len(suggestion)
                ),
                "explanation": (
                    "Suggestion rejected because it introduces invalid syntax or a new security finding."
                    if validation_status == "rejected"
                    else "AI-generated completion; review its behavior before accepting."
                ),
                "validation_status": validation_status,
                "warnings": warnings,
            }
        )
    except Exception as exc:
        logger.exception("Live AI completion validation failed")
        provider_error = _provider_error_response(exc)
        if provider_error:
            return provider_error
        return jsonify(
            {
                "error": "The AI completion could not be validated safely. Check the server log for its diagnostic."
            }
        ), 502


@assistant_routes.route("/assistant", methods=["POST"])
def assistant_route():
    data = _request_data()
    code = _extract_code(data)
    prompt = data.get("prompt", "") if isinstance(data, dict) else ""
    if code is None:
        return jsonify({"error": "Code must be a string"}), 400
    if not code.strip():
        return jsonify({"error": "No code provided"}), 400
    if len(code) > current_app.config["MAX_SOURCE_LENGTH"]:
        return jsonify({"error": "Payload Too Large"}), 413
    if not isinstance(prompt, str):
        return jsonify({"error": "Prompt must be a string"}), 400
    if len(prompt) > 4000:
        return jsonify({"error": "Prompt is too long"}), 413
    response_mode = data.get("response_mode", "answer") if isinstance(data, dict) else "answer"
    if not isinstance(response_mode, str) or response_mode not in {"answer", "explain", "debug"}:
        return jsonify({"error": "response_mode must be answer, explain, or debug."}), 400
    try:
        history = validate_assistant_history(
            data.get("history", []) if isinstance(data, dict) else []
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    attack_detection = _scan_assistant_input(prompt, code)
    if attack_detection["detected"]:
        _log_blocked_attack("/assistant", attack_detection)
        return jsonify(
            {
                "error": "Request blocked by the Agentic AI security layer.",
                "security_blocked": True,
                "attack_detection": attack_detection,
            }
        ), 422

    valid = validate_code(code)
    if valid is not True:
        formatted = format_python_error(code)
        return jsonify(
            {
                "error": f"Syntax error in your code: {valid}",
                "interpreter_output": formatted,
            }
        ), 400

    try:
        analysis = analyze_code(code)
        name_findings = _undefined_name_findings(check_undefined_names(code))
        analysis["warnings"].extend(name_findings)
        assistant_warning = None
        try:
            assistant = build_assistant_response(
                analysis,
                prompt,
                client,
                code,
                history=history,
                response_mode=response_mode,
            )
        except AssistantModelError as exc:
            if client is None:
                raise
            logger.warning(
                "AI assistant model response failed (%s); returning AST-grounded guidance.",
                type(exc).__name__,
            )
            assistant = build_assistant_response(
                analysis,
                prompt,
                None,
                code,
                history=history,
                response_mode=response_mode,
            )
            assistant_warning = (
                "The configured AI provider could not provide a usable response; this uses "
                "AST-grounded guidance instead."
            )
        return jsonify(
            {
                "assistant_reply": assistant["message"],
                "assistant_type": assistant["type"],
                "assistant_source": assistant["source"],
                "assistant_warning": assistant_warning,
                "suggestions": assistant["suggestions"],
                "analysis_summary": assistant["summary"],
                "warnings": analysis.get("warnings", []),
            }
        )
    except Exception as exc:
        logger.exception("AI assistant request failed")
        provider_error = _provider_error_response(exc)
        if provider_error:
            return provider_error
        return jsonify({"error": "AI assistant request failed"}), 500


@assistant_routes.route("/assistant/intent", methods=["POST"])
def assistant_intent_route():
    data = _request_data()
    prompt = data.get("prompt") if isinstance(data, dict) else None
    if not isinstance(prompt, str) or not prompt.strip():
        return jsonify({"error": "Prompt must contain at least one character."}), 400
    if len(prompt) > 4000:
        return jsonify({"error": "Prompt is too long."}), 413
    return jsonify({"intent": classify_nexus_request(prompt)})


@assistant_routes.route("/assistant/improve", methods=["POST"])
def assistant_improve_route():
    data = _request_data()
    code = _extract_code(data)
    if code is None:
        return jsonify({"error": "Code must be a string"}), 400
    if not code.strip():
        return jsonify({"error": "No code provided"}), 400
    if len(code) > current_app.config["MAX_SOURCE_LENGTH"]:
        return jsonify({"error": "Payload Too Large"}), 413
    prompt_scan = detect_attack(code, content_type="prompt")
    code_scan = detect_attack(code, content_type="code")
    _adv_cats = {"policy_bypass", "safety_control_bypass", "credential_exfiltration", "private_data_exfiltration", "jailbreak_attempt", "sensitive_data_transfer"}
    _adv_detected = any(c in _adv_cats for c in (prompt_scan.get("categories", []) + code_scan.get("categories", [])))
    attack_detection = (prompt_scan if prompt_scan["detected"] else code_scan) if _adv_detected else {"detected": False, "categories": []}
    if attack_detection["detected"]:
        _log_blocked_attack("/assistant/improve", attack_detection)
        return jsonify(
            {
                "error": "AI improvement was blocked because the source contains adversarial instructions.",
                "security_blocked": True,
                "attack_detection": attack_detection,
            }
        ), 422

    valid = validate_code(code)
    if valid is not True:
        formatted = format_python_error(code)
        return jsonify(
            {
                "error": f"Syntax error in your code: {valid}",
                "interpreter_output": formatted,
            }
        ), 400
    if client is None:
        return jsonify(
            {
                "error": "AI code improvement is unavailable. Configure API_KEY to enable it."
            }
        ), 503

    try:
        result = improve_code_quality(code, client)
        return jsonify(result)
    except Exception as exc:
        logger.exception("AI code-quality improvement failed")
        provider_error = _provider_error_response(exc)
        if provider_error:
            return provider_error
        return jsonify({"error": "AI code-quality improvement failed"}), 502


@artifact_routes.route("/open_ast_pdf", methods=["POST"])
def open_ast_pdf_route():
    return _ast_pdf_response(as_attachment=False)


@artifact_routes.route("/download_ast_pdf", methods=["POST"])
def download_ast_pdf_route():
    return _ast_pdf_response(as_attachment=True)


def _ast_pdf_response(*, as_attachment):
    data = _request_data()
    code = _extract_code(data)
    if code is None:
        return jsonify({"error": "Code must be a string"}), 400
    if not code.strip():
        return jsonify({"error": "No code provided"}), 400
    if len(code) > current_app.config["MAX_SOURCE_LENGTH"]:
        return jsonify({"error": "Payload Too Large"}), 413
    valid = validate_code(code)
    if valid is not True:
        formatted = format_python_error(code)
        return jsonify(
            {
                "error": f"Syntax error in your code: {valid}",
                "interpreter_output": formatted,
            }
        ), 400
    try:
        pdf_data = open_ast_pdf(code)
        return send_file(
            BytesIO(pdf_data),
            mimetype="application/pdf",
            as_attachment=as_attachment,
            download_name="ast.pdf",
        )
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 503
    except Exception as exc:
        logger.exception("AST PDF rendering failed")
        provider_error = _provider_error_response(exc)
        if provider_error:
            return provider_error
        return jsonify({"error": "AST PDF rendering failed"}), 500


def create_app(config_overrides=None):
    """Build a Flask application with the API route groups and shared middleware."""
    install_log_redaction()
    flask_app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")
    flask_app.config.from_object(AppConfig)
    if config_overrides:
        flask_app.config.update(config_overrides)

    for blueprint in (
        main_routes,
        security_routes,
        agent_routes,
        analysis_routes,
        editor_routes,
        assistant_routes,
        artifact_routes,
        agentic_routes,
        project_routes,
        monitoring_routes,
    ):
        flask_app.register_blueprint(blueprint)

    flask_app.before_request(_record_start_time)
    flask_app.before_request(_enforce_rate_limit)
    flask_app.before_request(_enforce_csrf)
    flask_app.before_request(_enforce_model_api_key)
    flask_app.after_request(after_request)
    flask_app.register_error_handler(413, request_entity_too_large)
    flask_app.register_error_handler(500, handle_internal_server_error)
    return flask_app


app = create_app()
