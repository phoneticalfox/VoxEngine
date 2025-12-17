"""Logging utilities."""

from __future__ import annotations
import logging
import os


def configure_logging() -> None:
    """Configure root logging once.

    The level can be overridden with ``VOXENGINE_LOG_LEVEL``.
    """
    level = os.getenv("VOXENGINE_LOG_LEVEL", "INFO").upper()
    logging.basicConfig(level=level, format="%(levelname)s %(name)s: %(message)s")


def get_logger(name: str) -> logging.Logger:
    """Return a logger after ensuring basic config is applied."""
    configure_logging()
    return logging.getLogger(name)
