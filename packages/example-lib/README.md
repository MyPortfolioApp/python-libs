# example-lib

Example library - use as template for new packages.

## Installation

```bash
pip install example-lib
```

Or install from the monorepo:

```bash
uv pip install -e packages/example-lib
```

## Usage

```python
from example_lib import greet

message = greet("World")
print(message)  # Hello, World!
```
