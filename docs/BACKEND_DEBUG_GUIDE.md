# Backend Selection Debug Guide

## Overview

Debug logging has been added to help diagnose backend selection issues. When you run any RSP script or system, you'll now see detailed logs showing exactly which backend is being selected and why.

## Debug Output

When the system initializes, you'll see logs like this:

```
INFO - DEBUG: Backend configuration:
INFO -   config.target.backend = ModelBackend.OPENROUTER
INFO -   backend_value = openrouter
INFO -   type = <class 'str'>
INFO - DEBUG BackendFactory.create() called:
INFO -   backend_type (raw) = 'openrouter'
INFO -   type = <class 'str'>
INFO -   backend_type_lower = 'openrouter'
INFO -   Registered backends = ['openai', 'openrouter', 'anthropic', 'llama_cpp', 'custom_http']
INFO -   Selected backend_class = OpenRouterBackend
```

## What Each Line Means

### Main.py Debug Logs

1. **`config.target.backend`** - The enum value from configuration
   - Example: `ModelBackend.OPENROUTER`
   - This comes from `load_config_from_env()` reading `BACKEND_TYPE`

2. **`backend_value`** - The string extracted from the enum
   - Example: `"openrouter"`
   - This is what gets passed to `BackendFactory.create()`

3. **`type`** - The Python type of backend_value
   - Should always be `<class 'str'>`

### BackendFactory Debug Logs

1. **`backend_type (raw)`** - The exact value received by the factory
   - Should match `backend_value` from main.py

2. **`backend_type_lower`** - After case-insensitive normalization
   - Example: `"openrouter"`, `"OpenRouter"` → `"openrouter"`

3. **`Registered backends`** - All available backend types
   - Shows what backends are registered in the system

4. **`Selected backend_class`** - The actual backend class that will be instantiated
   - Example: `OpenRouterBackend`, `OpenAIBackend`, `AnthropicBackend`

## Troubleshooting with Debug Logs

### Problem: Wrong backend being selected

Check the debug logs:

```bash
export BACKEND_TYPE=openrouter
export OPENROUTER_API_KEY="your-key"
python your_script.py 2>&1 | grep -E "DEBUG|Selected backend"
```

**Expected output:**
```
DEBUG: Backend configuration:
  backend_value = openrouter
Selected backend_class = OpenRouterBackend
```

**If you see:**
```
backend_value = openai
Selected backend_class = OpenAIBackend
```

Then `BACKEND_TYPE` is not being read correctly. Check:
1. Is the environment variable set in the same shell?
2. Are you using `load_config_from_env()` or `get_default_config()`?
3. Is the environment variable exported: `export BACKEND_TYPE=openrouter`?

### Problem: Backend not found

If you see an error like:
```
ValueError: Unknown backend type: openruter. Available backends: openai, openrouter, anthropic, llama_cpp, custom_http
```

Check the `backend_type_lower` in debug logs - you likely have a typo:
- ✅ `openrouter`
- ❌ `openruter`
- ❌ `open_router`
- ❌ `OpenRouter` (works due to case-insensitive matching)

### Problem: Case sensitivity

The factory is **case-insensitive**, so these all work:
- `BACKEND_TYPE=openrouter` ✅
- `BACKEND_TYPE=OpenRouter` ✅
- `BACKEND_TYPE=OPENROUTER` ✅

## Testing Backend Selection

### Test OpenRouter:
```bash
cd backend
export BACKEND_TYPE=openrouter
export OPENROUTER_API_KEY="sk-or-v1-your-key"
python -c "
from app.core.config import load_config_from_env
from app.main import setup_system
config = load_config_from_env()
print(f'Backend: {config.target.backend.value}')
try:
    setup_system(config)
except Exception as e:
    print(f'Note: {e}')
" 2>&1 | grep -E "DEBUG|Selected|Backend:"
```

### Test OpenAI (default):
```bash
cd backend
export OPENAI_API_KEY="sk-your-key"
# BACKEND_TYPE not set - should default to openai
python -c "
from app.core.config import load_config_from_env
from app.main import setup_system
config = load_config_from_env()
print(f'Backend: {config.target.backend.value}')
" 2>&1 | grep -E "DEBUG|Selected|Backend:"
```

### Test Anthropic:
```bash
cd backend
export BACKEND_TYPE=anthropic
export ANTHROPIC_API_KEY="sk-ant-your-key"
python -c "
from app.core.config import load_config_from_env
from app.main import setup_system
config = load_config_from_env()
print(f'Backend: {config.target.backend.value}')
" 2>&1 | grep -E "DEBUG|Selected|Backend:"
```

## Expected Flow

1. **Environment Variable** → `BACKEND_TYPE=openrouter`
2. **Config Loader** → Reads env var, returns `ModelBackend.OPENROUTER` enum
3. **Main.py** → Extracts `.value` → `"openrouter"` string
4. **BackendFactory** → Normalizes to lowercase → `"openrouter"`
5. **Registry Lookup** → Finds `OpenRouterBackend` class
6. **Instantiation** → Creates `OpenRouterBackend` instance with config

## Debug Logs Location

Debug logs are added in:
- **backend/app/main.py** (lines ~172-179) - Before `create_target()` call
- **backend/app/factories/__init__.py** (lines ~45-59) - In `BackendFactory.create()`

## Removing Debug Logs

If you want to remove the verbose debug logging after troubleshooting, you can:

1. Comment out the debug lines in `backend/app/main.py`:
```python
# DEBUG: Log backend selection details
# logger.info(f"DEBUG: Backend configuration:")
# logger.info(f"  config.target.backend = {config.target.backend}")
# ...
```

2. Comment out the debug lines in `backend/app/factories/__init__.py`:
```python
# DEBUG: Log what backend is being requested
# logger.info(f"DEBUG BackendFactory.create() called:")
# logger.info(f"  backend_type (raw) = {backend_type!r}")
# ...
```

Or set logging level to WARNING to hide INFO logs:
```python
logging.basicConfig(level=logging.WARNING)
```

## Verification

All backends have been tested and work correctly:
- ✅ OpenRouter: `BACKEND_TYPE=openrouter` → `OpenRouterBackend`
- ✅ OpenAI: `BACKEND_TYPE=openai` or default → `OpenAIBackend`
- ✅ Anthropic: `BACKEND_TYPE=anthropic` → `AnthropicBackend`
- ✅ Llama.cpp: `BACKEND_TYPE=llama_cpp` → `LlamaCppBackend`
- ✅ Custom HTTP: `BACKEND_TYPE=custom_http` → `CustomHTTPBackend`

The backend selection system is working correctly with proper case-insensitive matching.
