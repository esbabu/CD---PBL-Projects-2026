"""Centralized logging configuration for SyntaxSense."""

from __future__ import annotations

import logging
import os
import sys
from typing import Optional

LOG_FORMAT = "%(asctime)s [%(levelname)s] [%(name)s]: %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
DEFAULT_LOGGER_NAME = "syntaxsense"


def setup_logging(level: Optional[str | int] = None) -> logging.Logger:
    """Configure centralized logging for the SyntaxSense application.

    Ensures handlers are attached only once to prevent duplicate log records.
    Level can be overridden via the SYNTAX_SENSE_LOG_LEVEL environment variable.
    """
    if level is None:
        level_name = os.getenv("SYNTAX_SENSE_LOG_LEVEL", "INFO").upper()
        level = getattr(logging, level_name, logging.INFO)
    elif isinstance(level, str):
        level = getattr(logging, level.upper(), logging.INFO)

    logger = logging.getLogger(DEFAULT_LOGGER_NAME)
    logger.setLevel(level)

    # Avoid adding duplicate handlers if already configured
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)
        formatter = logging.Formatter(fmt=LOG_FORMAT, datefmt=DATE_FORMAT)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.propagate = False

    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Return a namespaced logger child of 'syntaxsense'."""
    if not name or name == DEFAULT_LOGGER_NAME:
        return logging.getLogger(DEFAULT_LOGGER_NAME)
    if name.startswith(f"{DEFAULT_LOGGER_NAME}."):
        return logging.getLogger(name)
    return logging.getLogger(f"{DEFAULT_LOGGER_NAME}.{name}")
