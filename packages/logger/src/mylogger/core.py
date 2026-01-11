"""
Structured logger with hybrid output:
- console (default): Colored readable output in terminal
- json: Structured JSON for log aggregation

Controlled via MYLOGGER_FORMAT env var or configure(format=...).
"""

import os
from typing import Any

import structlog
from dotenv import load_dotenv
from structlog.typing import Processor

# Load .env file if present
load_dotenv()

# Global settings
_log_format: str | None = None
_exclude_levels: set[str] | None = None
_configured: bool = False


def _get_format() -> str:
    """Get log format from environment or configuration."""
    global _log_format
    if _log_format is not None:
        return _log_format
    # Default: check MYLOGGER_FORMAT environment variable
    return os.environ.get("MYLOGGER_FORMAT", "console").lower()


def _get_exclude_levels() -> set[str]:
    """Get excluded log levels from environment or configuration."""
    global _exclude_levels
    if _exclude_levels is not None:
        return _exclude_levels
    # Default: check MYLOGGER_EXCLUDE environment variable
    exclude_str = os.environ.get("MYLOGGER_EXCLUDE", "")
    if not exclude_str:
        return set()
    return {level.strip().lower() for level in exclude_str.split(",") if level.strip()}


def _filter_by_level(
    _logger: Any, _method_name: str, event_dict: dict[str, Any]
) -> dict[str, Any]:
    """Filter out excluded log levels."""
    exclude = _get_exclude_levels()
    if exclude and event_dict.get("level", "").lower() in exclude:
        raise structlog.DropEvent
    return event_dict


def configure(format: str | None = None, exclude: list[str] | None = None) -> None:
    """
    Configure structlog based on environment.

    Args:
        format: Log format ("console" or "json"). If None, uses MYLOGGER_FORMAT env var.
        exclude: List of log levels to exclude. If None, uses MYLOGGER_EXCLUDE env var.
    """
    global _log_format, _exclude_levels, _configured

    if format is not None:
        _log_format = format.lower()

    if exclude is not None:
        _exclude_levels = {level.lower() for level in exclude}

    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        _filter_by_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.ExtraAdder(),
    ]

    if _get_format() == "console":
        # Dev: Colored and readable output
        structlog.configure(
            processors=[
                *shared_processors,
                structlog.dev.ConsoleRenderer(
                    colors=True,
                    exception_formatter=structlog.dev.plain_traceback,
                ),
            ],
            wrapper_class=structlog.make_filtering_bound_logger(0),
            context_class=dict,
            logger_factory=structlog.PrintLoggerFactory(),
            cache_logger_on_first_use=False,
        )
    else:
        # Prod: Structured JSON
        structlog.configure(
            processors=[
                *shared_processors,
                structlog.processors.dict_tracebacks,
                structlog.processors.JSONRenderer(),
            ],
            wrapper_class=structlog.make_filtering_bound_logger(0),
            context_class=dict,
            logger_factory=structlog.PrintLoggerFactory(),
            cache_logger_on_first_use=False,
        )

    _configured = True


def _ensure_configured() -> None:
    """Ensure structlog is configured before use."""
    global _configured
    if not _configured:
        configure()


def get_logger(name: str = "app") -> structlog.stdlib.BoundLogger:
    """Get a structured logger with specific name."""
    _ensure_configured()
    return structlog.get_logger(name)


# Main application logger
def _get_default_logger() -> structlog.stdlib.BoundLogger:
    """Get the default logger, ensuring configuration."""
    _ensure_configured()
    return structlog.get_logger("app")


class _LazyLogger:
    """Lazy logger that configures on first access."""

    _instance: structlog.stdlib.BoundLogger | None = None

    def __getattr__(self, name: str) -> Any:
        if self._instance is None:
            self._instance = _get_default_logger()
        return getattr(self._instance, name)


logger = _LazyLogger()


# ---------------------------------------------------------------------------
# Compatibility functions with common logging patterns
# ---------------------------------------------------------------------------


def log_success(msg: str, **kwargs: Any) -> None:
    """Log success message."""
    _ensure_configured()
    structlog.get_logger("app").info(msg, status="success", **kwargs)


def log_error(msg: str, **kwargs: Any) -> None:
    """Log error message."""
    _ensure_configured()
    structlog.get_logger("app").error(msg, **kwargs)


def log_warning(msg: str, **kwargs: Any) -> None:
    """Log warning message."""
    _ensure_configured()
    structlog.get_logger("app").warning(msg, **kwargs)


def log_info(msg: str, **kwargs: Any) -> None:
    """Log info message."""
    _ensure_configured()
    structlog.get_logger("app").info(msg, **kwargs)


def log_start(msg: str, **kwargs: Any) -> None:
    """Log operation start."""
    _ensure_configured()
    structlog.get_logger("app").info(msg, phase="start", **kwargs)


def log_end(msg: str, **kwargs: Any) -> None:
    """Log operation end."""
    _ensure_configured()
    structlog.get_logger("app").info(msg, phase="end", **kwargs)


def log_db(msg: str, **kwargs: Any) -> None:
    """Log database operations."""
    _ensure_configured()
    structlog.get_logger("app").info(msg, component="database", **kwargs)


def log_progress(msg: str, **kwargs: Any) -> None:
    """Log progress."""
    _ensure_configured()
    structlog.get_logger("app").info(msg, phase="progress", **kwargs)


def log_completion(msg: str, **kwargs: Any) -> None:
    """Log completion."""
    _ensure_configured()
    structlog.get_logger("app").info(msg, phase="complete", **kwargs)


def log_extract(msg: str, **kwargs: Any) -> None:
    """Log data extraction."""
    _ensure_configured()
    structlog.get_logger("app").info(msg, operation="extract", **kwargs)


def log_input(msg: str, **kwargs: Any) -> None:
    """Log incoming request."""
    _ensure_configured()
    structlog.get_logger("app").info(msg, direction="input", **kwargs)


def log_output(msg: str, **kwargs: Any) -> None:
    """Log outgoing response."""
    _ensure_configured()
    structlog.get_logger("app").info(msg, direction="output", **kwargs)


# ---------------------------------------------------------------------------
# Context management for adding context to logs
# ---------------------------------------------------------------------------


def bind_context(**kwargs: Any) -> None:
    """Add context to all subsequent logs in current thread."""
    structlog.contextvars.bind_contextvars(**kwargs)


def clear_context() -> None:
    """Remove all context."""
    structlog.contextvars.clear_contextvars()


def unbind_context(*keys: str) -> None:
    """Remove specific keys from context."""
    structlog.contextvars.unbind_contextvars(*keys)
