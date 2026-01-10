"""
Structured logger with hybrid output:
- Dev (debug=True): Colored readable output in terminal
- Prod (debug=False): Structured JSON for log aggregation
"""

import os
from typing import Any

import structlog
from structlog.typing import Processor

# Global debug mode flag
_debug_mode: bool | None = None
_configured: bool = False


def _get_debug_mode() -> bool:
    """Get debug mode from environment or configuration."""
    global _debug_mode
    if _debug_mode is not None:
        return _debug_mode
    # Default: check DEBUG environment variable
    return os.environ.get("DEBUG", "true").lower() in ("true", "1", "yes")


def configure(debug: bool | None = None) -> None:
    """
    Configure structlog based on environment.

    Args:
        debug: Force debug mode. If None, uses DEBUG env var.
    """
    global _debug_mode, _configured

    if debug is not None:
        _debug_mode = debug

    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.ExtraAdder(),
    ]

    if _get_debug_mode():
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
