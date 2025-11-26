# API Refactoring Documentation

## Overview

The FastAPI application has been moved from `sages/api.py` to a dedicated `apis/` module to better separate concerns and improve project organization.

## Changes Made

### 1. New Directory Structure

Created a new `apis/` directory at the project root:

```
opssage/
├── apis/                    # NEW: FastAPI application
│   ├── __init__.py         # Exports app for convenience
│   └── main.py             # Main FastAPI application
├── sages/                   # Core agent logic
│   ├── api.py              # UPDATED: Now re-exports from apis.main
│   ├── subagents/
│   ├── models.py
│   └── ...
```

### 2. File Changes

#### apis/main.py (NEW)
- Contains the complete FastAPI application
- All route handlers (alerts, incidents, health checks)
- Lifespan management
- CORS middleware configuration

#### apis/__init__.py (NEW)
- Simple re-export of `app` from `apis.main`
- Provides cleaner import path: `from apis import app`

#### sages/api.py (UPDATED)
- Now acts as a compatibility shim
- Re-exports `app` from `apis.main`
- Maintains backward compatibility for existing code

### 3. Import Updates

All references to `sages.api` have been updated to `apis.main`:

#### Updated Files:
- `tests/test_api.py` - Tests now import from `apis.main`
- `Makefile` - Updated run commands
- `Dockerfile` - Updated CMD
- `docker/Dockerfile.dev` - Updated CMD
- `README.md` - Updated documentation
- `QUICKSTART.md` - Updated quick start guide
- `docs/DEVELOPER_GUIDE.md` - Updated developer documentation
- `docs/ARCHITECTURE.md` - Updated architecture references

### 4. Tool Import Fix

Fixed Google ADK tool imports in all agent files:

- Changed `from google.adk.tools import tool` → `from google.adk.tools import agent_tool`
- Updated all agent tool registrations to use `agent_tool()` instead of `tool()`

Files updated:
- `sages/subagents/aica.py`
- `sages/subagents/krea.py`
- `sages/subagents/rcara.py`
- `docs/DEVELOPER_GUIDE.md`

## Backward Compatibility

The refactoring maintains full backward compatibility:

```python
# Old import (still works)
from sages.api import app

# New recommended import
from apis.main import app

# Also works
from apis import app
```

## Benefits

1. **Separation of Concerns**: API logic is now separate from agent logic
2. **Clearer Structure**: Easier to find and modify API-related code
3. **Extensibility**: Easy to add multiple API modules (e.g., `apis/v2.py`, `apis/webhooks.py`)
4. **Maintainability**: Changes to API don't affect agent code structure

## Testing

Verify the refactoring works:

```bash
# Test imports
uv run python -c "from apis import app; print(app.title)"

# Test backward compatibility
uv run python -c "from sages.api import app; print(app.title)"

# Run server
uv run uvicorn apis.main:app --reload

# Or use Makefile
make run
```

## Migration Guide

For existing code that imports from `sages.api`:

### Option 1: Update imports (recommended)
```python
# Before
from sages.api import app

# After
from apis.main import app
```

### Option 2: No changes needed
The old import path still works due to the compatibility shim in `sages/api.py`.

## Future Enhancements

With this structure, we can easily:

1. Add API versioning: `apis/v1/`, `apis/v2/`
2. Split routes: `apis/alerts.py`, `apis/incidents.py`
3. Add specialized APIs: `apis/webhooks.py`, `apis/internal.py`
4. Maintain clear separation between API and business logic

## Rollback

If needed, the refactoring can be rolled back by:

1. Moving `apis/main.py` back to `sages/api.py`
2. Reverting import changes in affected files
3. Removing the `apis/` directory

However, backward compatibility means no immediate rollback is needed.
