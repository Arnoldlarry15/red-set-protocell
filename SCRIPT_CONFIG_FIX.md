# Script Configuration Fix Summary

## Problem Statement

The deterministic experiment script (and other scripts) were not calling `load_config_from_env()`, instead using `get_default_config()` which always defaults to OpenAI backend. This caused the scripts to ignore the `BACKEND_TYPE` and `OPENROUTER_API_KEY` environment variables.

## Root Cause

Scripts were using:
```python
from app.core.config import get_default_config
config = get_default_config()
```

Instead of:
```python
from app.core.config import load_config_from_env
config = load_config_from_env()
```

The `get_default_config()` function returns a config with hardcoded defaults (OpenAI backend), while `load_config_from_env()` reads environment variables to set the backend type and API keys.

## Scripts Fixed

1. **scripts/run_deterministic_experiment.py**
   - Changed 3 calls from `get_default_config()` to `load_config_from_env()`
   - In: `run_session()`, `verify_determinism()` (2 places)

2. **scripts/run_experiment.py**
   - Changed 1 call from `get_default_config()` to `load_config_from_env()`
   - In: `run_session()`

3. **backend/examples/benchmarking.py**
   - Changed 1 call from `get_default_config()` to `load_config_from_env()`
   - Removed manual backend selection logic (now handled by config loader)
   - Simplified API key checking
   - In: `run_quick_benchmark()`

4. **backend/examples/time_analytics.py**
   - Changed 1 call from `get_default_config()` to `load_config_from_env()`
   - Removed manual backend/API key selection logic
   - Simplified target creation using config
   - In: `run_test_session()`

## New Files Added

1. **scripts/verify_all_scripts.py**
   - Comprehensive verification script
   - Checks all scripts use `load_config_from_env`
   - Verifies no scripts use `get_default_config`
   - Tests config loader with multiple backends
   - Provides detailed pass/fail report

2. **docs/DETERMINISTIC_EXPERIMENTS.md** (updated)
   - Renamed from deterministic-specific to cover all scripts
   - Added usage examples for all backends
   - Documented all fixed scripts
   - Added verification script usage

3. **backend/tests/test_deterministic_script_config.py**
   - Test file to verify script configuration
   - Checks imports and function calls
   - Tests config loader behavior with environment variables

## Verification

Run the verification script to ensure all scripts are properly configured:

```bash
python scripts/verify_all_scripts.py
```

Expected output:
```
🎉 ALL VERIFICATION CHECKS PASSED!

All scripts now properly:
  ✓ Import load_config_from_env
  ✓ Call load_config_from_env() to get configuration
  ✓ Respect BACKEND_TYPE environment variable
  ✓ Respect backend-specific API keys
```

## Usage Examples

### Using OpenRouter

```bash
export BACKEND_TYPE=openrouter
export OPENROUTER_API_KEY="sk-or-v1-your-key"

# All scripts now work with OpenRouter
python scripts/run_deterministic_experiment.py --verify --seed 15
python scripts/run_experiment.py
python backend/examples/benchmarking.py
python backend/examples/time_analytics.py
```

### Using OpenAI (default)

```bash
export OPENAI_API_KEY="sk-your-key"
# BACKEND_TYPE defaults to openai if not set

python scripts/run_deterministic_experiment.py --rounds 100
```

### Using Anthropic

```bash
export BACKEND_TYPE=anthropic
export ANTHROPIC_API_KEY="sk-ant-your-key"

python scripts/run_experiment.py
```

## Testing

All scripts were verified to:
1. Compile successfully
2. Import `load_config_from_env`
3. Call `load_config_from_env()` for configuration
4. Not use `get_default_config`
5. Respect environment variables

Config loader was tested with:
- OpenRouter backend (BACKEND_TYPE=openrouter + OPENROUTER_API_KEY)
- OpenAI backend (default, OPENAI_API_KEY)
- Anthropic backend (BACKEND_TYPE=anthropic + ANTHROPIC_API_KEY)

All tests passed successfully.

## Best Practices for Future Scripts

When creating new scripts that need RSP configuration:

1. **Always use `load_config_from_env()`:**
   ```python
   from app.core.config import load_config_from_env
   config = load_config_from_env()
   ```

2. **Never use `get_default_config()` in scripts:**
   - Use `get_default_config()` only in tests or when you explicitly want defaults
   - Production scripts should always respect environment variables

3. **Verify your script:**
   ```bash
   python scripts/verify_all_scripts.py
   ```

4. **Add helpful error messages:**
   ```python
   if not config.target.api_key:
       print("ERROR: No API key found in configuration.")
       print("Set appropriate environment variables:")
       print("  - For OpenRouter: BACKEND_TYPE=openrouter and OPENROUTER_API_KEY")
       print("  - For OpenAI: OPENAI_API_KEY (default backend)")
       print("  - For Anthropic: BACKEND_TYPE=anthropic and ANTHROPIC_API_KEY")
       raise ValueError("API key required")
   ```

## Impact

This fix ensures that:
- Users can easily switch between backends without modifying code
- All scripts behave consistently with environment configuration
- OpenRouter and other backends are fully supported in all scripts
- Configuration is centralized and predictable

## References

- Config loader implementation: `backend/app/core/config.py:195-261`
- Environment variable documentation: `backend/.env.example:26-45`
- Test coverage: `backend/tests/test_config.py:146-199`
- Verification script: `scripts/verify_all_scripts.py`
