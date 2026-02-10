# EGG (Ethical Guardrail Governor) Improvements

## Overview

This document describes the improvements made to the EGG system to address concerns about pattern handling, feedback loops, test generation, and category separation.

## Changes Made

### 1. Pattern Error Handling: Align Philosophy with Implementation

**Problem**: The docstring stated "Pattern matching errors default to ALLOW (with error log)" but malformed regex would crash during initialization.

**Solution**:
- Added `_validate_patterns()` method that runs at initialization
- Validates all regex patterns and catches `re.error` exceptions
- Malformed patterns are logged and added to `malformed_patterns` dictionary
- System continues to run with valid patterns (fail-open behavior)
- Runtime regex errors are also caught and logged during `inspect_prompt()`
- Updated docstring to reflect actual behavior

**Benefits**:
- No more crashes due to malformed patterns
- Clear logging of pattern issues
- Maintains philosophy of defaulting to ALLOW on errors
- Provides visibility into which patterns are problematic

### 2. Shadow Mode Feedback Loop: Make Shadow Mode Actionable

**Problem**: Shadow mode logs near-misses but nothing in RSP automatically uses that data.

**Solution**:
- Added `get_shadow_mode_suggestions()` method that analyzes shadow matches
- Identifies high-confidence near-misses (score > 0.8)
- Detects patterns with frequent near-misses
- Generates actionable suggestions for pattern improvements
- Added `export_shadow_data_for_analysis()` for external analysis

**Benefits**:
- Shadow mode data is now actionable
- Can identify evasion patterns
- Provides feedback loop for pattern refinement
- Supports continuous improvement of EGG patterns

**Example Usage**:
```python
egg = EthicalGuardrailGovernor(shadow_mode=True)

# After running inspections...
suggestions = egg.get_shadow_mode_suggestions()
# Returns: {
#   'bioweapons': [
#     'Found 5 high-confidence near-misses. Consider reviewing...',
#     'Patterns with frequent near-misses (2 patterns): May need refinement...'
#   ]
# }

# Export for detailed analysis
shadow_data = egg.export_shadow_data_for_analysis()
# Returns list of all shadow matches with full details
```

### 3. Adversarial Test Generator: Improve Sophistication

**Problem**: Test generator only pulled terms from patterns, which is naive and might miss devious constructions.

**Solution**:
- Improved `generate_adversarial_test_prompts()` to create 4 types of tests:
  1. **Direct extraction** (baseline) - existing behavior
  2. **Paraphrased** - uses hypothetical/theoretical framing
  3. **Obfuscated** - adds character spacing and other obfuscation
  4. **Boundary cases** - partial matches with noise
- Each test is marked with its type for easy identification
- Tests cycle through all 4 types to ensure coverage

**Benefits**:
- More comprehensive testing of pattern coverage
- Tests evasion techniques
- Identifies edge cases where patterns might fail
- Better validation of EGG effectiveness

**Example Output**:
```python
test_prompts = egg.generate_adversarial_test_prompts(count=8)
# [
#   "Test: weaponize anthrax for [SYNTHETIC TEST]",
#   "Theoretically speaking, weaponize anthrax biological [PARAPHRASE TEST]",
#   "w e a p o n i z e anthrax for [OBFUSCATION TEST]",
#   "Boundary case with weaponize anthrax and unrelated content [BOUNDARY TEST]",
#   ...
# ]
```

### 4. Real Hacking Category: Add Dedicated Flag

**Problem**: `real_hacking` patterns were only checked when `block_real_exploits=True`, bundling them together conceptually.

**Solution**:
- Added `block_real_hacking` parameter to `EthicalGuardrailGovernor.__init__()`
- Added `block_real_hacking` to `EGGConfig` dataclass
- Updated `inspect_prompt()` to check `real_hacking` patterns independently
- Updated all callsites (`api_server.py`, `main.py`) to pass the new flag
- Defaults to `True` for backward compatibility

**Benefits**:
- Clearer separation of concerns
- More granular control over blocking categories
- Conceptually correct: real hacking and real exploits are distinct
- Easier to configure different blocking policies

**Example Usage**:
```python
# Block real exploits but allow real hacking patterns
egg = EthicalGuardrailGovernor(
    block_real_exploits=True,
    block_real_hacking=False
)

# Block only real hacking
egg = EthicalGuardrailGovernor(
    block_csam=False,
    block_bioweapons=False,
    block_real_exploits=False,
    block_real_hacking=True
)
```

### 5. Documentation: Pattern Limitations

**Status**: Already addressed in the original docstring. The DEFENSIBILITY STATEMENT section explicitly mentions:

> Limitations (Honest Assessment):
> - Pattern-based detection has false negatives
> - Sophisticated prompt engineering may evade patterns
> - Not a replacement for human review
> - Patterns may have cultural/language biases

## Testing

All changes are thoroughly tested:

- `test_egg_real_hacking_independent_flag()` - Tests the new flag works independently
- `test_egg_malformed_pattern_handling()` - Tests graceful handling of malformed patterns
- `test_egg_shadow_mode_suggestions()` - Tests shadow mode feedback generation
- `test_egg_improved_adversarial_tests()` - Tests improved test generation

**Test Results**: 28/28 tests pass, code passes linting

## API Changes

### New Methods

1. `EthicalGuardrailGovernor.get_shadow_mode_suggestions() -> Dict[str, List[str]]`
   - Analyzes shadow matches and returns actionable suggestions

2. `EthicalGuardrailGovernor.export_shadow_data_for_analysis() -> List[Dict]`
   - Exports shadow match data for external analysis

### Modified Methods

1. `EthicalGuardrailGovernor.__init__(..., block_real_hacking: bool = True)`
   - Added new parameter for real hacking blocking

2. `EthicalGuardrailGovernor.generate_adversarial_test_prompts(count: int = None) -> List[str]`
   - Now generates 4 types of tests instead of just direct extraction

### Modified Configuration

1. `EGGConfig` now includes `block_real_hacking: bool = True`

## Backward Compatibility

All changes maintain backward compatibility:
- New `block_real_hacking` parameter defaults to `True`
- Existing code will continue to work without changes
- New test markers are in addition to existing ones
- Shadow mode methods are additive (don't change existing behavior)

## Migration Guide

For most users, no changes are needed. However, if you want to take advantage of new features:

### To use the new real_hacking flag:
```python
egg = EthicalGuardrailGovernor(
    block_real_hacking=True  # explicitly enable
)
```

### To use shadow mode feedback:
```python
egg = EthicalGuardrailGovernor(shadow_mode=True)

# After running inspections
suggestions = egg.get_shadow_mode_suggestions()
for category, category_suggestions in suggestions.items():
    print(f"Category {category}:")
    for suggestion in category_suggestions:
        print(f"  - {suggestion}")
```

### To use improved test generation:
```python
egg = EthicalGuardrailGovernor()

# Generate diverse test prompts
test_prompts = egg.generate_adversarial_test_prompts(count=20)

# Run coverage tests
results = egg.test_guard_coverage(test_count=50)
print(f"Block rate: {results['block_rate']:.1f}%")
```

## Future Improvements

Based on these changes, future enhancements could include:

1. **Automated Pattern Updates**: Use shadow mode data to automatically suggest new patterns
2. **Machine Learning Integration**: Train an ML model on shadow matches to predict evasion attempts
3. **Community Pattern Sharing**: Allow users to share effective patterns (with privacy)
4. **Pattern Performance Metrics**: Track which patterns are most/least effective
5. **Dynamic Pattern Loading**: Load patterns from external sources at runtime

## References

- Original EGG implementation: `backend/app/core/egg.py`
- Test suite: `backend/tests/test_egg.py`
- Configuration: `backend/app/core/config.py`
- Usage examples: `backend/app/api_server.py`, `backend/app/main.py`
