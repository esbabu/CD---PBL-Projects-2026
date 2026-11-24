"""Sliding-window in-memory rate limiting engine for AST Studio.

Protects sensitive API and Agent endpoints against denial-of-service and brute force.
"""

from __future__ import annotations

import logging
import threading
import time
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


class SlidingWindowRateLimiter:
    """Thread-safe sliding-window rate limiter per client identifier."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        # client_id -> list of timestamps
        self._records: Dict[str, List[float]] = {}
        # Route-specific limits: route_prefix -> (max_requests, window_seconds)
        self._route_limits: Dict[str, Tuple[int, int]] = {
            "/generate": (60, 60),               # 60 req / min
            "/assistant": (60, 60),              # 60 req / min
            "/agent/": (60, 60),                 # 60 req / min
            "/agentic/run": (30, 60),            # 30 runs / min
            "/agentic/action": (60, 60),         # 60 actions / min
            "/agentic/session": (60, 60),        # 60 session / ticket ops / min
            "/api/settings": (30, 60),           # 30 updates / min
            "/api/test-provider": (20, 60),      # 20 connectivity checks / min
        }
        self._default_limit: Tuple[int, int] = (120, 60)  # 120 req / min general

    def set_route_limit(self, route_prefix: str, max_requests: int, window_seconds: int) -> None:
        with self._lock:
            self._route_limits[route_prefix] = (max_requests, window_seconds)

    def is_rate_limited(
        self, client_id: str, path: str
    ) -> Tuple[bool, int, float]:
        """Check if client has exceeded limit for path.

        Returns (is_limited, remaining_requests, retry_after_seconds).
        """
        now = time.time()
        # Find matching limit
        max_requests, window = self._default_limit
        for prefix, limit in self._route_limits.items():
            if path.startswith(prefix):
                max_requests, window = limit
                break

        key = f"{client_id}:{path}"
        with self._lock:
            timestamps = self._records.setdefault(key, [])
            cutoff = now - window
            # Prune expired timestamps
            valid_timestamps = [t for t in timestamps if t > cutoff]
            self._records[key] = valid_timestamps

            if len(valid_timestamps) >= max_requests:
                oldest = valid_timestamps[0]
                retry_after = round(window - (now - oldest), 2)
                return True, 0, max(0.1, retry_after)

            valid_timestamps.append(now)
            remaining = max_requests - len(valid_timestamps)
            return False, remaining, 0.0

    def reset(self) -> None:
        """Clear all active client rate limit windows (for testing or administrative reset)."""
        with self._lock:
            self._records.clear()

    def cleanup(self) -> int:
        """Periodic cleanup of empty or fully expired client entries."""
        now = time.time()
        removed = 0
        with self._lock:
            keys_to_delete = []
            for key, timestamps in self._records.items():
                # If all timestamps are older than 120s, remove
                if not timestamps or (now - timestamps[-1] > 120):
                    keys_to_delete.append(key)
            for k in keys_to_delete:
                del self._records[k]
                removed += 1
        return removed


# Global rate limiter instance
default_rate_limiter = SlidingWindowRateLimiter()
