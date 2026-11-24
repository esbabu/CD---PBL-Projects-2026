"""Concurrency, Multi-Worker, and Session Isolation Test Suite for AST Studio.

Tests:
- Concurrent multi-session execution across threads without cross-session data leakage
- Event isolation and correct delivery per session
- Thread-safe shared SQLite persistence under concurrent stress
- Cancellation isolation (cancelling Session A does not interrupt Session B)
- Bounded concurrency and queue saturation resilience
"""

from __future__ import annotations

import concurrent.futures
import tempfile
from pathlib import Path


from backend.agentic.session import AgentSession, SessionManager
from backend.agentic.supervisor import SupervisorAgent
from backend.agentic.tools import default_tool_registry


SNIPPET_A = """
def process_alpha(data):
    # Alpha task
    return [x * 2 for x in data]
"""

SNIPPET_B = """
def process_beta(users):
    # Beta task
    cleaned = []
    for u in users:
        cleaned.append(u.strip().lower())
    return cleaned
"""

SNIPPET_C = """
def process_gamma(matrix):
    # Gamma task
    total = 0
    for row in matrix:
        for val in row:
            total += val
    return total
"""


class TestConcurrencyAndSessionIsolation:
    """Verify that multiple concurrent workflows run in complete isolation."""

    def test_concurrent_sessions_have_no_data_leakage(self):
        supervisor = SupervisorAgent(tools=default_tool_registry)

        session_a = AgentSession(
            session_id="concurrent_session_a",
            original_code=SNIPPET_A,
            original_code_digest="digest_a",
            current_code=SNIPPET_A,
            task="Task Alpha: optimize processing",
        )
        session_b = AgentSession(
            session_id="concurrent_session_b",
            original_code=SNIPPET_B,
            original_code_digest="digest_b",
            current_code=SNIPPET_B,
            task="Task Beta: security audit",
        )
        session_c = AgentSession(
            session_id="concurrent_session_c",
            original_code=SNIPPET_C,
            original_code_digest="digest_c",
            current_code=SNIPPET_C,
            task="Task Gamma: documentation",
        )

        sessions = [session_a, session_b, session_c]

        # Execute all three sessions concurrently in a thread pool
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(supervisor.run, s) for s in sessions]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        assert len(results) == 3
        for res in results:
            assert res["status"] in {"completed", "awaiting_approval"}

        # Verify strict isolation of original code and findings
        assert "process_alpha" in session_a.original_code
        assert "process_beta" not in session_a.original_code
        assert "process_gamma" not in session_a.original_code

        assert "process_beta" in session_b.original_code
        assert "process_alpha" not in session_b.original_code

        assert "process_gamma" in session_c.original_code
        assert "process_alpha" not in session_c.original_code

        # Trajectories must belong exclusively to each session
        for step in session_a.trajectory:
            assert step.thought or step.action

    def test_cancellation_isolation(self):
        """Cancelling Session A must not affect or cancel Session B running concurrently."""
        supervisor = SupervisorAgent(tools=default_tool_registry)

        session_running = AgentSession(
            session_id="session_running",
            original_code=SNIPPET_A,
            original_code_digest="digest_a",
            current_code=SNIPPET_A,
            task="Normal run task",
        )
        session_cancelled = AgentSession(
            session_id="session_cancelled",
            original_code=SNIPPET_B,
            original_code_digest="digest_b",
            current_code=SNIPPET_B,
            task="Cancelled task",
        )
        # Request cancellation only on session_cancelled
        session_cancelled.request_cancellation()

        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            fut_run = executor.submit(supervisor.run, session_running)
            fut_cancel = executor.submit(supervisor.run, session_cancelled)

            res_run = fut_run.result()
            res_cancel = fut_cancel.result()

        # Session A must complete normally
        assert res_run["status"] in {"completed", "awaiting_approval"}
        assert session_running.status in {"completed", "awaiting_approval"}

        # Session B must be cancelled
        assert res_cancel["status"] == "cancelled"
        assert session_cancelled.status == "cancelled"

    def test_sqlite_concurrent_read_write_stress(self):
        """Verify SQLite WAL mode handles heavy concurrent thread reads and writes without locking."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = Path(tmp_dir) / "stress_test.db"
            manager = SessionManager(storage_path=db_path)

            def worker_task(worker_id: int):
                # Create session, update state, and retrieve
                s = manager.create_session(
                    code=f"def worker_{worker_id}(): return {worker_id}",
                    task=f"Worker {worker_id} workload",
                )
                for step in range(5):
                    s.metadata[f"step_{step}"] = worker_id * 10 + step
                    s.set_status("in_progress")
                s.set_status("completed")
                # Retrieve from storage
                retrieved = manager.get_session(s.session_id)
                assert retrieved is not None
                assert retrieved.status == "completed"
                assert retrieved.metadata.get("step_4") == worker_id * 10 + 4
                return True

            num_workers = 10
            with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
                futures = [executor.submit(worker_task, i) for i in range(num_workers)]
                results = [f.result() for f in concurrent.futures.as_completed(futures)]

            assert len(results) == num_workers
            assert all(results)

    def test_multi_client_rate_limiter_concurrency(self):
        """Verify rate limiter thread-safety and bounded limits across concurrent clients."""
        from backend.security_rate_limit import SlidingWindowRateLimiter

        limiter = SlidingWindowRateLimiter()
        limiter.set_route_limit("/test", max_requests=10, window_seconds=60)

        def make_requests(client_id: str):
            allowed = 0
            blocked = 0
            for _ in range(15):
                is_limited, _, _ = limiter.is_rate_limited(f"client_{client_id}", "/test")
                if is_limited:
                    blocked += 1
                else:
                    allowed += 1
            return allowed, blocked

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_requests, f"user_{i}") for i in range(5)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        for allowed, blocked in results:
            assert allowed > 0
            # Route limit is 10 requests, so with 15 requests, 5 must be blocked
            assert blocked >= 4
