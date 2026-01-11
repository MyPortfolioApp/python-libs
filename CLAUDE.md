# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Monorepo for personal Python libraries using UV workspace. Each package lives in `packages/` with its own `pyproject.toml`.

## Common Commands

```bash
# Run all tests
pytest packages/

# Run tests for a specific package
pytest packages/logger

# Run a single test file
pytest packages/logger/tests/test_logger.py

# Run a single test
pytest packages/logger/tests/test_logger.py::test_function_name

# Format code
ruff format .

# Lint (with auto-fix)
ruff check . --fix

# Type check
mypy packages/

# Run all pre-commit hooks
pre-commit run --all-files

# Install a package in editable mode
uv pip install -e packages/logger
```

## Architecture

### Package Structure

Each package follows this layout:
```
packages/<package-name>/
├── src/<module_name>/    # Source code (note: underscores in module names)
│   ├── __init__.py       # Public API exports
│   └── core.py           # Main implementation
├── tests/
├── pyproject.toml        # Package-specific config (uses hatchling)
└── README.md
```

### Current Packages

- **mylogger** (`packages/logger/`): Structured logging built on structlog. Output mode controlled by `DEBUG` env var (true=colored console, false=JSON).

- **example-lib** (`packages/example-lib/`): Template for creating new packages.

### Workspace Configuration

- Root `pyproject.toml` defines UV workspace and shared tool configs (ruff, mypy, pytest)
- Individual packages declare their own dependencies in their `pyproject.toml`
- Build backend is hatchling for all packages

## Code Style

- Python 3.12+ required
- Type hints required (mypy with `disallow_untyped_defs`)
- Ruff handles formatting and linting (line length 88)
- Pre-commit hooks run ruff, mypy, and basic file checks
