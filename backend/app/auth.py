"""Authentication and redaction helpers for API server."""

import logging
import re
import traceback

logger = logging.getLogger(__name__)


def redact_sensitive_text(text: str) -> str:
    """Redact sensitive credential-like tokens from logs and error messages."""
    redacted = re.sub(r"sk-[A-Za-z0-9_-]{8,}", "sk-***REDACTED***", text)
    redacted = re.sub(r"Bearer\s+[A-Za-z0-9._-]+", "Bearer ***REDACTED***", redacted, flags=re.IGNORECASE)
    return redacted


def log_exception_safely(context: str, exc: Exception) -> None:
    """Log redacted exception details and traceback for internal debugging."""
    redacted_message = redact_sensitive_text(str(exc))
    redacted_traceback = redact_sensitive_text(traceback.format_exc())
    logger.error(f"{context}: {type(exc).__name__} - {redacted_message}")
    logger.error(redacted_traceback)
