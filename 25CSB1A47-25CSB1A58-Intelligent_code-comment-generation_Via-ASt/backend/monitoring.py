"""Observability, health check, and runtime metrics blueprint for AST Studio."""

from __future__ import annotations

import logging
import shutil
import sqlite3
import threading
import time
from contextlib import closing
from pathlib import Path
from typing import Any, Dict

from flask import Blueprint, current_app, jsonify

from .agentic.tools import default_tool_registry
from .model_provider import provider_display_name, provider_ready

logger = logging.getLogger(__name__)

monitoring_routes = Blueprint("monitoring", __name__)


class SystemMetrics:
    """Thread-safe telemetry metrics collector."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.start_time = time.time()
        self.total_requests = 0
        self.request_durations_sum = 0.0
        self.status_codes: Dict[int, int] = {}
        self.sessions_started = 0
        self.sessions_completed = 0
        self.sessions_failed = 0
        self.sessions_cancelled = 0
        self.tool_executions = 0
        self.provider_requests = 0
        self.provider_failures = 0

    def record_request(self, status_code: int, duration: float) -> None:
        with self._lock:
            self.total_requests += 1
            self.request_durations_sum += duration
            self.status_codes[status_code] = self.status_codes.get(status_code, 0) + 1

    def record_session_event(self, event_type: str) -> None:
        with self._lock:
            if event_type == "started":
                self.sessions_started += 1
            elif event_type == "completed":
                self.sessions_completed += 1
            elif event_type == "failed":
                self.sessions_failed += 1
            elif event_type == "cancelled":
                self.sessions_cancelled += 1

    def record_tool_call(self) -> None:
        with self._lock:
            self.tool_executions += 1

    def record_provider_call(self, success: bool) -> None:
        with self._lock:
            self.provider_requests += 1
            if not success:
                self.provider_failures += 1

    def snapshot(self) -> Dict[str, Any]:
        with self._lock:
            uptime = max(0.001, time.time() - self.start_time)
            avg_latency_ms = (
                (self.request_durations_sum / self.total_requests * 1000.0)
                if self.total_requests > 0
                else 0.0
            )
            return {
                "uptime_seconds": round(uptime, 2),
                "total_requests": self.total_requests,
                "requests_per_second": round(self.total_requests / uptime, 2),
                "avg_latency_ms": round(avg_latency_ms, 2),
                "status_codes": dict(self.status_codes),
                "sessions": {
                    "started": self.sessions_started,
                    "completed": self.sessions_completed,
                    "failed": self.sessions_failed,
                    "cancelled": self.sessions_cancelled,
                },
                "tool_executions": self.tool_executions,
                "provider_requests": self.provider_requests,
                "provider_failures": self.provider_failures,
            }


metrics_collector = SystemMetrics()


@monitoring_routes.route("/health/live", methods=["GET"])
def liveness_probe():
    """Lightweight liveness probe for Kubernetes and container orchestrators."""
    return jsonify({
        "status": "healthy",
        "service": "ast-studio",
        "timestamp": time.time(),
    }), 200


@monitoring_routes.route("/health/ready", methods=["GET"])
def readiness_probe():
    """Deep readiness probe verifying critical subsystems: DB, Tools, Model Provider, Storage."""
    subsystems: Dict[str, Dict[str, Any]] = {}
    is_ready = True

    # 1. Database Check
    db_path = current_app.config.get(
        "DATABASE_PATH",
        str(Path(__file__).resolve().parent.parent / "instance" / "session_store.db"),
    )
    db_status = "healthy"
    try:
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        with closing(sqlite3.connect(db_path, timeout=2.0)) as conn:
            conn.execute("SELECT 1").fetchone()
    except Exception as exc:
        db_status = f"unhealthy: {exc}"
        is_ready = False
    subsystems["database"] = {"status": db_status, "path": db_path}

    # 2. Tool Registry Check
    tools_count = len(default_tool_registry.list_tools())
    tools_ok = tools_count > 0
    if not tools_ok:
        is_ready = False
    subsystems["tool_registry"] = {
        "status": "healthy" if tools_ok else "unhealthy",
        "registered_tools": tools_count,
    }

    # 3. Model Provider Status
    from . import model_provider
    client = model_provider.create_model_client()
    ai_ready = provider_ready(client)
    subsystems["model_provider"] = {
        "status": "ready" if ai_ready else "degraded (fallback to AST active)",
        "provider": provider_display_name(),
        "model": model_provider.MODEL_NAME,
    }

    # 4. Storage and Disk Space
    try:
        usage = shutil.disk_usage(Path(db_path).parent)
        free_mb = usage.free / (1024 * 1024)
        disk_ok = free_mb > 50  # at least 50MB free
        if not disk_ok:
            is_ready = False
        subsystems["storage"] = {
            "status": "healthy" if disk_ok else "critically low disk space",
            "free_space_mb": round(free_mb, 2),
            "total_space_mb": round(usage.total / (1024 * 1024), 2),
        }
    except Exception as exc:
        subsystems["storage"] = {"status": f"unknown: {exc}"}

    status_code = 200 if is_ready else 503
    return jsonify({
        "status": "ready" if is_ready else "not_ready",
        "ready": is_ready,
        "subsystems": subsystems,
        "timestamp": time.time(),
    }), status_code


@monitoring_routes.route("/metrics", methods=["GET"])
def metrics_endpoint():
    """Return JSON runtime telemetry metrics for monitoring scrapers."""
    snapshot = metrics_collector.snapshot()
    return jsonify(snapshot), 200
