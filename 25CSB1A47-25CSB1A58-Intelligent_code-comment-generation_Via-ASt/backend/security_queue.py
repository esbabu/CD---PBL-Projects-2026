"""Bounded execution queue and executor manager for asynchronous background tasks.

Prevents worker saturation and memory exhaustion under concurrent load.
"""

from __future__ import annotations

import logging
from concurrent.futures import Future, ThreadPoolExecutor
from threading import Semaphore
from typing import Any, Callable

logger = logging.getLogger(__name__)


class BoundedExecutor:
    """Thread pool executor guarded by a maximum pending task capacity semaphore."""

    def __init__(self, max_workers: int = 5, max_queue_size: int = 20, name_prefix: str = "worker") -> None:
        self.max_workers = max_workers
        self.max_queue_size = max_queue_size
        self._semaphore = Semaphore(max_workers + max_queue_size)
        self._executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix=name_prefix)

    def submit(self, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> Future:
        """Submit a task to the pool, raising QueueFullError if bounded capacity is reached."""
        acquired = self._semaphore.acquire(blocking=False)
        if not acquired:
            logger.warning("BoundedExecutor queue is full (max_capacity=%d)", self.max_workers + self.max_queue_size)
            raise QueueFullError("Background task queue is at maximum capacity. Please retry shortly.")

        def _wrapped_task():
            try:
                return fn(*args, **kwargs)
            finally:
                self._semaphore.release()

        try:
            return self._executor.submit(_wrapped_task)
        except Exception:
            self._semaphore.release()
            raise

    def shutdown(self, wait: bool = True) -> None:
        self._executor.shutdown(wait=wait)


class QueueFullError(RuntimeError):
    """Raised when the bounded background task queue is saturated."""
