# Installazione mylogger

## Da path locale

```bash
pip install -e /Users/carlogasparini/Projects/python-libs/packages/logger
```

## Da Git (dopo aver pushato)

```bash
pip install git+https://github.com/carlogasparini/python-libs.git#subdirectory=packages/logger
```

## Uso

```python
from mylogger import log_info, log_error, log_success, configure

# Opzionale: forza modalità produzione (JSON output)
configure(debug=False)

# Oppure usa variabile d'ambiente
# export DEBUG=false

# Log semplici
log_info("Server started", port=8000)
log_success("User created", user_id=123)
log_error("Connection failed", error="timeout")
```

## Context binding (per request tracking)

```python
from mylogger import bind_context, clear_context, log_info

# In un middleware FastAPI/Flask
bind_context(request_id="abc-123", user_id=456)

# Tutti i log successivi includeranno request_id e user_id
log_info("Processing request")
log_info("Query executed")

# A fine request
clear_context()
```

## Esempio FastAPI middleware

```python
import uuid
from fastapi import Request
from mylogger import bind_context, clear_context, log_info

@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    bind_context(request_id=request_id, path=request.url.path)

    log_info("Request started")
    response = await call_next(request)
    log_info("Request completed", status_code=response.status_code)

    clear_context()
    return response
```

## Output

### Dev (DEBUG=true)
```
2024-01-15T10:30:00.000000Z [info     ] Server started        port=8000
2024-01-15T10:30:01.000000Z [error    ] Connection failed     error=timeout
```

### Prod (DEBUG=false)
```json
{"event": "Server started", "port": 8000, "timestamp": "2024-01-15T10:30:00.000000Z", "log_level": "info"}
{"event": "Connection failed", "error": "timeout", "timestamp": "2024-01-15T10:30:01.000000Z", "log_level": "error"}
```
