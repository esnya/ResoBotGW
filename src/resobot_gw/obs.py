"""Observability helpers: correlation ID in logs.

Adds a logging Filter that injects a correlation ID from a contextvar.
"""

from __future__ import annotations

import logging
import uuid
from contextvars import ContextVar

correlation_id: ContextVar[str] = ContextVar("correlation_id", default="-")


class CorrelationFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:  # pragma: no cover - trivial
        record.cid = correlation_id.get()
        return True


def new_correlation_id() -> str:
    cid = uuid.uuid4().hex[:12]
    correlation_id.set(cid)
    return cid
