# python-libs

Monorepo for personal Python libraries.

## Structure

```
python-libs/
├── packages/
│   ├── logger/         # Structured logging library
│   └── example-lib/    # Example package (use as template)
├── pyproject.toml      # Workspace config + dev tools
└── .pre-commit-config.yaml
```

## Setup

### Prerequisites

- Python 3.12+

### Installation

```bash
# Create virtual environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate

# Install dev dependencies
pip install pytest ruff mypy pre-commit

# Install pre-commit hooks
pre-commit install
```

## Development

### Running tests

```bash
# Run all tests
pytest packages/

# Run tests for a specific package
pytest packages/logger
```

### Code quality

```bash
# Format code
ruff format .

# Lint code
ruff check .

# Type check
mypy packages/
```

### Pre-commit hooks

Hooks run automatically on commit. To run manually:

```bash
pre-commit run --all-files
```

## Creating a new package

1. Copy the `packages/example-lib` directory:
   ```bash
   cp -r packages/example-lib packages/my-new-lib
   ```

2. Rename the source directory:
   ```bash
   mv packages/my-new-lib/src/example_lib packages/my-new-lib/src/my_new_lib
   ```

3. Update `packages/my-new-lib/pyproject.toml`:
   - Change `name` to your package name
   - Update `description`
   - Update the `packages` path in `[tool.hatch.build.targets.wheel]`

4. Update imports in `__init__.py` and tests

## Available Packages

### mylogger

Structured logger with hybrid output (colored for dev, JSON for production).

```bash
pip install -e packages/logger
```

```python
from mylogger import log_info, log_error, bind_context

log_info("Starting", user_id=123)
bind_context(request_id="abc-123")
log_error("Something failed")
```

## Installing packages in other projects

### From local path

```bash
pip install -e /path/to/python-libs/packages/logger
```

### From git (once pushed to a remote)

```bash
pip install git+https://github.com/carlogasparini/python-libs.git#subdirectory=packages/logger
```
