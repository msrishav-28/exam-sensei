"""
Centralized logging configuration for ExamSensei.

- Console handler always on (Render captures stdout/stderr).
- Rotating file handler on disk (best-effort; Render's disk is ephemeral).
- JSON formatter in production.
- request_id propagated via a ContextVar so per-handler log lines carry it.
"""
import json
import logging
import sys
from contextvars import ContextVar
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

from config import settings


# Per-request correlation id, set by the request middleware.
request_id_ctx: ContextVar[Optional[str]] = ContextVar("request_id", default=None)


# Standard LogRecord attributes — anything else passed via `extra=` is
# user-supplied context and should be serialized into the JSON payload.
_RESERVED_RECORD_KEYS = {
    "name", "msg", "args", "levelname", "levelno", "pathname", "filename",
    "module", "exc_info", "exc_text", "stack_info", "lineno", "funcName",
    "created", "msecs", "relativeCreated", "thread", "threadName",
    "processName", "process", "message", "asctime", "taskName",
}


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        rid = request_id_ctx.get()
        if rid:
            log_data["request_id"] = rid

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Surface any extra=... fields passed at log time. Previously these
        # were silently dropped because the formatter only checked for two
        # named keys.
        for key, value in record.__dict__.items():
            if key in _RESERVED_RECORD_KEYS or key.startswith("_"):
                continue
            if key in log_data:
                continue
            try:
                json.dumps(value, default=str)
            except (TypeError, ValueError):
                value = repr(value)
            log_data[key] = value

        return json.dumps(log_data, default=str)


def _setup_logging() -> logging.Logger:
    """Configure application logging."""

    # Absolute path relative to this module so logs land in the same place
    # regardless of process working directory.
    log_dir = Path(__file__).resolve().parent / "logs"
    try:
        log_dir.mkdir(exist_ok=True)
    except OSError:
        log_dir = None  # read-only filesystem; we'll skip file handlers

    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))
    root_logger.handlers.clear()

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    if settings.environment == "production":
        console_handler.setFormatter(JSONFormatter())
    else:
        console_handler.setFormatter(logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        ))
    root_logger.addHandler(console_handler)

    if log_dir is not None:
        file_handler = RotatingFileHandler(
            log_dir / "examsensei.log", maxBytes=10 * 1024 * 1024, backupCount=3
        )
        file_handler.setLevel(logging.DEBUG if settings.environment != "production" else logging.INFO)
        file_handler.setFormatter(JSONFormatter() if settings.environment == "production"
                                  else console_handler.formatter)
        root_logger.addHandler(file_handler)

        error_handler = RotatingFileHandler(
            log_dir / "errors.log", maxBytes=10 * 1024 * 1024, backupCount=5
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(JSONFormatter())
        root_logger.addHandler(error_handler)

    # Quiet noisy third-party loggers
    for noisy in ("urllib3", "scrapy", "sqlalchemy.engine"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    return root_logger


logger = _setup_logging()


# Convenience functions — `extra=` keys now flow through to JSON logs.
def log_api_request(method: str, path: str, user_id: Optional[int] = None, status_code: Optional[int] = None):
    extra = {}
    if user_id is not None:
        extra["user_id"] = user_id
    if status_code is not None:
        extra["status_code"] = status_code
    logger.info(f"API {method} {path}", extra=extra)


def log_error(error: Exception, context: Optional[dict] = None):
    extra = dict(context) if context else {}
    logger.error(f"Error: {error}", exc_info=True, extra=extra)


def log_user_activity(user_id: int, activity: str, details: Optional[dict] = None):
    logger.info(
        f"User activity: {activity}",
        extra={"user_id": user_id, "activity_details": details or {}},
    )


def log_scraper_activity(source: str, status: str, items_scraped: int = 0):
    logger.info(
        f"Scraper {source}: {status}",
        extra={"source": source, "items": items_scraped},
    )
