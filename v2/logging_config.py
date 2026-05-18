from __future__ import annotations

import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Optional


DEFAULT_V2_LOG_PATH = os.getenv("V2_LOG_PATH", "logs/api-v2.log")


def setup_v2_file_logger(
    *,
    log_path: str = DEFAULT_V2_LOG_PATH,
    level: int = logging.INFO,
    max_bytes: int = 10 * 1024 * 1024,
    backup_count: int = 5,
) -> logging.Logger:
    """
    Creates a dedicated logger for API v2 traffic that writes to a rotating log file.
    Safe to call multiple times (won't duplicate handlers).
    """
    logger = logging.getLogger("monlam.api.v2")
    logger.setLevel(level)
    logger.propagate = False  # keep v2 file logs separate from root logger

    abs_path = os.path.abspath(log_path)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)

    handler_id = f"rotating:{abs_path}"
    for h in logger.handlers:
        if getattr(h, "_monlam_handler_id", None) == handler_id:
            return logger

    handler = RotatingFileHandler(abs_path, maxBytes=max_bytes, backupCount=backup_count)
    handler._monlam_handler_id = handler_id  # type: ignore[attr-defined]
    handler.setLevel(level)
    handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s | %(levelname)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    logger.addHandler(handler)
    return logger


def get_v2_logger() -> logging.Logger:
    """
    Returns the v2 logger; if not configured, returns a no-op-ish logger that propagates.
    """
    return logging.getLogger("monlam.api.v2")

