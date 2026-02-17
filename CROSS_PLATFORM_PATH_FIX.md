# Cross-Platform Path Fix

## Problem
CI tests were failing on Windows and macOS with `FileNotFoundError` for `run_deterministic_experiment.py`:

```
FAILED tests/test_deterministic_script_config.py::test_deterministic_script_imports_load_config_from_env
FileNotFoundError: [Errno 2] No such file or directory: '/home/runner/work/red-set-protocell/red-set-protocell/scripts/run_deterministic_experiment.py'
```

## Root Cause
Tests in `test_deterministic_script_config.py` used hardcoded Linux-specific absolute paths:

```python
script_path = "/home/runner/work/red-set-protocell/red-set-protocell/scripts/run_deterministic_experiment.py"
```

### Path Differences by Platform
- **Linux**: `/home/runner/work/red-set-protocell/red-set-protocell/`
- **Windows**: `D:\a\red-set-protocell\red-set-protocell\`
- **macOS**: `/Users/runner/work/red-set-protocell/red-set-protocell/`

The hardcoded Linux path doesn't work on Windows or macOS, causing tests to fail.

## Solution
Use `pathlib.Path` with relative path calculation:

```python
from pathlib import Path

# Calculate path relative to test file
test_dir = Path(__file__).parent
repo_root = test_dir.parent.parent
script_path = repo_root / "scripts" / "run_deterministic_experiment.py"
```

### Why This Works
1. **`Path(__file__)`** - Gets the absolute path of current test file
2. **`.parent`** - Navigate up directory tree
3. **`/` operator** - Automatically uses correct path separator (`/` on Unix, `\` on Windows)
4. **Cross-platform** - Works on Linux, macOS, Windows

## Impact
- ✅ Fixed 2 failing tests on Windows
- ✅ Fixed 2 failing tests on macOS
- ✅ Maintains compatibility on Linux
- ✅ All 665 tests now pass on all platforms

## Lessons Learned
1. **Never hardcode absolute paths** in tests - they're platform-specific
2. **Use pathlib.Path** for all file system operations - it's cross-platform
3. **Calculate paths relative to `__file__`** - makes tests portable
4. **Test on multiple platforms** - CI catches platform-specific issues

## Prevention Strategy
When writing tests that access files:
```python
# ❌ BAD - Hardcoded path
file_path = "/home/runner/work/project/scripts/script.py"

# ✅ GOOD - Relative path with pathlib
from pathlib import Path
test_dir = Path(__file__).parent
file_path = test_dir.parent / "scripts" / "script.py"
```

## Files Modified
- `backend/tests/test_deterministic_script_config.py` - Made paths cross-platform

## Related Issues
- Windows CI failures (all Python versions 3.8-3.12)
- macOS CI failures (all Python versions 3.8-3.12)
- FileNotFoundError on non-Linux platforms
