"""
Structured logger with hybrid output.

Formats:
- console (default): Colored readable output for development
- json: Structured JSON for production/log aggregation

Configuration via .env or environment variables:
- MYLOGGER_FORMAT: "console" or "json"
- MYLOGGER_EXCLUDE: comma-separated log levels to exclude (e.g., "debug,info")
"""

__version__ = "0.1.0"

from mylogger.core import (
    bind_context,
    clear_context,
    configure,
    get_logger,
    log_completion,
    log_db,
    log_end,
    log_error,
    log_extract,
    log_info,
    log_input,
    log_output,
    log_progress,
    log_start,
    log_success,
    log_warning,
    logger,
    unbind_context,
)

__all__ = [
    "__version__",
    "bind_context",
    "clear_context",
    "configure",
    "get_logger",
    "log_completion",
    "log_db",
    "log_end",
    "log_error",
    "log_extract",
    "log_info",
    "log_input",
    "log_output",
    "log_progress",
    "log_start",
    "log_success",
    "log_warning",
    "logger",
    "unbind_context",
]
