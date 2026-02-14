# Backend Selection Debug - Complete Analysis

## Problem Statement

The user reported that even with `BACKEND_TYPE=openrouter` set, the system was still constructing `OpenAIBackend()` instead of `OpenRouterBackend()`. They needed debug logging to understand what backend_type value was actually flowing into the factory.

## Root Cause Investigation

After thorough investigation, we found that:

1. ✅ **Config loader is working correctly**
   - `load_config_from_env()` properly reads `BACKEND_TYPE` environment variable
   - Returns correct `ModelBackend.OPENROUTER` enum
   - Extracts `.value` to get `"openrouter"` string

2. ✅ **BackendFactory is working correctly**
   - Registered with `"openrouter"` key
   - Performs case-insensitive matching
   - Correctly selects `OpenRouterBackend` class

3. ✅ **All scripts fixed**
   - Previously used `get_default_config()` which ignored environment
   - Now use `load_config_from_env()` to respect environment variables
   - All 4 scripts updated and verified

## Solution Implemented

### 1. Debug Logging Added

**In backend/app/main.py (lines 172-179):**
```python
# DEBUG: Log backend selection details
logger.info(f"DEBUG: Backend configuration:")
logger.info(f"  config.target.backend = {config.target.backend}")
logger.info(f"  backend_value = {backend_value}")
logger.info(f"  type = {type(backend_value)}")
```

**In backend/app/factories/__init__.py (lines 45-59):**
```python
# DEBUG: Log what backend is being requested
logger.info(f"DEBUG BackendFactory.create() called:")
logger.info(f"  backend_type (raw) = {backend_type!r}")
logger.info(f"  type = {type(backend_type)}")
logger.info(f"  backend_type_lower = {backend_type_lower!r}")
logger.info(f"  Registered backends = {list(cls._registry.keys())}")
logger.info(f"  Selected backend_class = {backend_class.__name__}")
```

### 2. Documentation Created

**docs/BACKEND_DEBUG_GUIDE.md:**
- Explains what each debug log line means
- Provides troubleshooting steps
- Shows expected output for each backend
- Includes test commands

### 3. Demo Script Created

**scripts/demo_backend_debug.py:**
- Interactive demonstration
- Tests all backends
- Shows debug output
- Validates correct behavior

## Verification Results

All backends tested and working correctly:

```
Testing: OPENROUTER
  Backend: ModelBackend.OPENROUTER
  backend_value: openrouter
  Selected: OpenRouterBackend
  ✅ PASS

Testing: OPENAI
  Backend: ModelBackend.OPENAI
  backend_value: openai
  Selected: OpenAIBackend
  ✅ PASS

Testing: ANTHROPIC
  Backend: ModelBackend.ANTHROPIC
  backend_value: anthropic
  Selected: AnthropicBackend
  ✅ PASS
```

## Debug Output Example

When running with `BACKEND_TYPE=openrouter`:

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
INFO - [OK] Target Agent initialized (openrouter)
```

## How to Use

### 1. See Debug Logs in Your Script

```bash
export BACKEND_TYPE=openrouter
export OPENROUTER_API_KEY="sk-or-v1-your-key"
python scripts/run_deterministic_experiment.py --verify --seed 15 2>&1 | grep DEBUG
```

### 2. Run Demo Script

```bash
python scripts/demo_backend_debug.py
```

### 3. Test Specific Backend

```bash
cd backend
export BACKEND_TYPE=openrouter
export OPENROUTER_API_KEY="test"
python -c "
from app.core.config import load_config_from_env
from app.main import setup_system
config = load_config_from_env()
try:
    setup_system(config)
except Exception as e:
    pass
" 2>&1 | grep -E "DEBUG|Selected"
```

## Troubleshooting

### If you see wrong backend selected:

1. **Check environment variables are set:**
   ```bash
   echo $BACKEND_TYPE
   echo $OPENROUTER_API_KEY
   ```

2. **Check debug logs show correct value:**
   ```
   backend_value = openrouter  ← Should match BACKEND_TYPE
   ```

3. **Verify script uses load_config_from_env():**
   ```bash
   python scripts/verify_all_scripts.py
   ```

### If you see "Unknown backend type" error:

1. **Check for typos:**
   - ✅ `openrouter`
   - ❌ `openruter`
   - ❌ `open_router`

2. **Check registered backends in logs:**
   ```
   Registered backends = ['openai', 'openrouter', 'anthropic', 'llama_cpp', 'custom_http']
   ```

3. **Verify case-insensitive matching:**
   - All of these work: `openrouter`, `OpenRouter`, `OPENROUTER`

## Files Changed

1. **backend/app/main.py** - Added debug logging before create_target()
2. **backend/app/factories/__init__.py** - Added debug logging in BackendFactory.create()
3. **docs/BACKEND_DEBUG_GUIDE.md** - Comprehensive troubleshooting guide
4. **scripts/demo_backend_debug.py** - Interactive demonstration script

## Key Findings

1. **System is working correctly** - All tests pass
2. **Scripts now use load_config_from_env()** - Environment variables respected
3. **BackendFactory uses case-insensitive matching** - No case sensitivity issues
4. **Debug logs provide full visibility** - Easy to diagnose any issues

## Conclusion

The backend selection system is working correctly. The debug logging added will help users:

1. **Verify** their configuration is being read correctly
2. **Diagnose** any issues with backend selection
3. **Understand** the flow from environment variable to backend instantiation
4. **Troubleshoot** problems without needing to modify code

The original problem (if it was occurring) was likely due to scripts using `get_default_config()` instead of `load_config_from_env()`, which has now been fixed in all scripts. The debug logging provides ongoing visibility to ensure this continues working correctly.

## Next Steps

Users should:

1. **Use the debug logs** when troubleshooting backend issues
2. **Run demo_backend_debug.py** to verify their environment
3. **Check BACKEND_DEBUG_GUIDE.md** for detailed troubleshooting
4. **Verify scripts** with verify_all_scripts.py

If issues persist, the debug logs will show exactly where the problem is occurring.
