"""Gunicorn production WSGI server configuration for AST Studio."""

import multiprocessing
import os

# Bind address and port
bind = os.getenv("BIND_ADDRESS", f"0.0.0.0:{os.getenv('PORT', '5000')}")

# Worker concurrency
# In thread-worker mode, workers handle distinct OS processes, while threads handle concurrent requests
default_workers = max(2, min(8, multiprocessing.cpu_count()))
workers = int(os.getenv("WEB_CONCURRENCY", default_workers))
worker_class = os.getenv("GUNICORN_WORKER_CLASS", "gthread")
threads = int(os.getenv("GUNICORN_THREADS", "4"))

# Worker lifecycle and recycling to prevent memory leaks in continuous AI tasks
max_requests = int(os.getenv("GUNICORN_MAX_REQUESTS", "1000"))
max_requests_jitter = int(os.getenv("GUNICORN_MAX_REQUESTS_JITTER", "100"))
timeout = int(os.getenv("GUNICORN_TIMEOUT", "120"))
graceful_timeout = int(os.getenv("GUNICORN_GRACEFUL_TIMEOUT", "30"))
keepalive = int(os.getenv("GUNICORN_KEEPALIVE", "5"))

# Logging
accesslog = os.getenv("GUNICORN_ACCESS_LOG", "-")
errorlog = os.getenv("GUNICORN_ERROR_LOG", "-")
loglevel = os.getenv("LOG_LEVEL", "info").lower()
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Security: do not preload app to ensure clean DB connections per worker process
preload_app = False


def on_starting(server):
    """Lifecycle hook executed once when Gunicorn master process starts."""
    server.log.info("Starting AST Studio production server on %s", bind)
    server.log.info(
        "Workers: %d (%s), Threads per worker: %d, Request timeout: %ds",
        workers,
        worker_class,
        threads,
        timeout,
    )


def post_fork(server, worker):
    """Lifecycle hook executed after each worker process is forked."""
    server.log.info("Worker spawned (pid: %s)", worker.pid)


def worker_exit(server, worker):
    """Lifecycle hook executed when a worker process terminates."""
    server.log.info("Worker exiting (pid: %s)", worker.pid)
