# mylogger

Structured logger with hybrid output:
- **Dev** (`DEBUG=true`): Colored readable output in terminal
- **Prod** (`DEBUG=false`): Structured JSON for log aggregation

Built on top of [structlog](https://www.structlog.org/).

## Installation

```bash
pip install mylogger
```

Or from the monorepo:

```bash
uv pip install -e packages/logger
```

## Quick Start

```python
from mylogger import logger, log_info, log_error, configure

# Optional: explicitly configure (auto-configures on first use)
configure(debug=True)  # or set DEBUG env var

# Use the default logger
logger.info("Application started", version="1.0.0")

# Use convenience functions
log_info("Processing request", request_id="abc-123")
log_error("Something failed", error_code=500)
```

## Convenience Functions

```python
from mylogger import (
    log_info,      # General info
    log_error,     # Errors
    log_warning,   # Warnings
    log_success,   # Success (adds status="success")
    log_start,     # Operation start (adds phase="start")
    log_end,       # Operation end (adds phase="end")
    log_progress,  # Progress updates (adds phase="progress")
    log_completion,# Completion (adds phase="complete")
    log_db,        # Database ops (adds component="database")
    log_extract,   # Data extraction (adds operation="extract")
    log_input,     # Incoming requests (adds direction="input")
    log_output,    # Outgoing responses (adds direction="output")
)
```

## Context Binding

Add context that persists across multiple log calls:

```python
from mylogger import bind_context, clear_context, unbind_context, log_info

# Add context for current request
bind_context(request_id="abc-123", user_id=456)

log_info("Processing started")  # includes request_id and user_id
log_info("Step 1 complete")     # includes request_id and user_id

# Remove specific context
unbind_context("user_id")

# Clear all context
clear_context()
```

## Named Loggers

```python
from mylogger import get_logger

db_logger = get_logger("database")
api_logger = get_logger("api")

db_logger.info("Query executed", table="users")
api_logger.info("Request received", endpoint="/users")
```

## Output Examples

### Dev Mode (DEBUG=true)

```
2024-01-15T10:30:00.000000Z [info     ] Processing request    request_id=abc-123
2024-01-15T10:30:01.000000Z [error    ] Something failed      error_code=500
```

### Production Mode (DEBUG=false)

```json
{"event": "Processing request", "request_id": "abc-123", "timestamp": "2024-01-15T10:30:00.000000Z", "log_level": "info"}
{"event": "Something failed", "error_code": 500, "timestamp": "2024-01-15T10:30:01.000000Z", "log_level": "error"}
```

## Configuration

### Environment Variable

```bash
export DEBUG=false  # Production mode (JSON output)
export DEBUG=true   # Dev mode (colored output)
```

### Programmatic

```python
from mylogger import configure

# Force debug mode
configure(debug=True)

# Force production mode
configure(debug=False)
```
