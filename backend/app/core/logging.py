"""Structured logging setup."""

import logging
import sys

from app.core.config import Settings


class RequestIdFormatter(logging.Formatter):
    """Inject a default request_id placeholder when none exists on the record.

    This formatter must be used instead of a per-logger Filter because
    filters attached to the root logger are *not* consulted during
    handler-level formatting of records that propagate from child loggers
    (e.g. sentence-transformers, httpx).
    """

    def format(self, record: logging.LogRecord) -> str:
        if not hasattr(record, "request_id"):
            record.request_id = "-"
        return super().format(record)


def configure_logging(settings: Settings) -> None:
    """Configure process-wide logging once at application startup."""
    root_logger = logging.getLogger()

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        RequestIdFormatter(
            "%(asctime)s %(levelname)s [%(name)s] [%(request_id)s] %(message)s"
        )
    )
    root_logger.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))
    # Clear any pre-existing handlers (e.g. from basicConfig)
    root_logger.handlers.clear()
    root_logger.addHandler(handler)

    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("chromadb").setLevel(logging.WARNING)
