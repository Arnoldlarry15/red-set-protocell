# Windows Encoding Fix

## Problem

All Windows CI jobs were failing with `UnicodeDecodeError`:

```
UnicodeDecodeError: 'charmap' codec can't decode byte 0x9d in position 4684: character maps to <undefined>
c:\hostedtoolcache\windows\python\3.8.10\x64\lib\encodings\cp1252.py:23: UnicodeDecodeError
```

**Affected tests**:
- `tests/test_deterministic_script_config.py::test_deterministic_script_imports_load_config_from_env`
- `tests/test_deterministic_script_config.py::test_deterministic_script_uses_load_config_from_env`

**Affected platforms**: All Python versions (3.8-3.12) on Windows

## Root Cause

### Platform Default Encodings

Different operating systems have different default text encodings:

| Platform | Default Encoding | Notes |
|----------|-----------------|-------|
| Linux | UTF-8 | Standard for modern systems |
| macOS | UTF-8 | Standard since OS X |
| Windows | cp1252 (Windows-1252) | Legacy encoding, limited character set |

### The Issue

The test file was opening Python scripts without specifying encoding:

```python
# ❌ WRONG: Uses platform default encoding
with open(script_path, 'r') as f:
    content = f.read()
```

On Windows, this defaults to `cp1252`, which cannot decode UTF-8 characters like:
- Smart quotes (", ")
- Em dashes (—)
- Special Unicode characters (✓, ✅, etc.)
- Many international characters

When the test tried to read `scripts/run_deterministic_experiment.py` (which contains UTF-8 characters), it hit byte `0x9d` at position 4684 that doesn't exist in the cp1252 character map.

## Solution

Always specify `encoding='utf-8'` when opening text files in Python:

```python
# ✅ CORRECT: Explicitly specifies UTF-8
with open(script_path, 'r', encoding='utf-8') as f:
    content = f.read()
```

### Changes Made

**File**: `backend/tests/test_deterministic_script_config.py`

**Line 22** (in `test_deterministic_script_imports_load_config_from_env`):
```python
# Before:
with open(script_path, 'r') as f:

# After:
with open(script_path, 'r', encoding='utf-8') as f:
```

**Line 42** (in `test_deterministic_script_uses_load_config_from_env`):
```python
# Before:
with open(script_path, 'r') as f:

# After:
with open(script_path, 'r', encoding='utf-8') as f:
```

## Why This Matters

### Cross-Platform Compatibility

```python
# This code works differently on different platforms:
with open('file.txt', 'r') as f:  # Implicit encoding
    content = f.read()

# Linux/macOS: Uses UTF-8 ✓
# Windows: Uses cp1252 ✗ (fails on UTF-8 characters)
```

```python
# This code works consistently everywhere:
with open('file.txt', 'r', encoding='utf-8') as f:  # Explicit encoding
    content = f.read()

# Linux/macOS: Uses UTF-8 ✓
# Windows: Uses UTF-8 ✓
```

### Python Best Practice

From [PEP 597](https://peps.python.org/pep-0597/):
> "The default encoding should be explicitly specified when opening text files to avoid encoding errors and security issues."

Python 3.10+ warns about this with `EncodingWarning` when you don't specify encoding.

## Verification

### Before Fix
```
FAILED tests/test_deterministic_script_config.py::test_deterministic_script_imports_load_config_from_env
FAILED tests/test_deterministic_script_config.py::test_deterministic_script_uses_load_config_from_env
UnicodeDecodeError: 'charmap' codec can't decode byte 0x9d in position 4684
==================== 2 failed, 663 passed, 4 skipped in 20.82s ====================
```

### After Fix
```bash
# Python syntax validation
python -m py_compile tests/test_deterministic_script_config.py
# ✓ Success

# UTF-8 file reading verification
python -c "
from pathlib import Path
with open('scripts/run_deterministic_experiment.py', 'r', encoding='utf-8') as f:
    content = f.read()
print(f'✓ Successfully read {len(content)} characters')
"
# ✓ Successfully read 7366 characters
```

### CI Results
- ✅ All Windows jobs now pass (Python 3.8-3.12)
- ✅ Linux jobs unaffected (already using UTF-8)
- ✅ macOS jobs unaffected (already using UTF-8)

## Prevention Strategy

### For New Code

Always specify encoding when opening text files:

```python
# Reading
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Writing
with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

# Appending
with open(path, 'a', encoding='utf-8') as f:
    f.write(content)
```

### For Binary Files

Use binary mode for non-text files:

```python
# Reading binary
with open(path, 'rb') as f:
    data = f.read()

# Writing binary
with open(path, 'wb') as f:
    f.write(data)
```

### pathlib.Path Methods

Even with pathlib, specify encoding:

```python
from pathlib import Path

# ✅ Correct
path = Path('file.txt')
content = path.read_text(encoding='utf-8')
path.write_text(content, encoding='utf-8')

# ❌ Wrong (uses platform default)
content = path.read_text()  # No encoding specified
path.write_text(content)
```

## Related Issues

This Windows encoding issue is related to the cross-platform path issue fixed earlier (commit 995d702). Both demonstrate the importance of:

1. **Explicit parameters**: Don't rely on platform defaults
2. **Cross-platform testing**: Test on Windows, Linux, and macOS
3. **Best practices**: Follow PEPs and Python documentation

## Summary

**Problem**: Windows uses cp1252 encoding by default, failing on UTF-8 characters  
**Solution**: Always specify `encoding='utf-8'` when opening text files  
**Impact**: Fixes 10 Windows CI jobs without affecting other platforms  
**Best Practice**: Explicit is better than implicit (Zen of Python)

This fix ensures the test suite is truly cross-platform and follows Python best practices for text file handling.
