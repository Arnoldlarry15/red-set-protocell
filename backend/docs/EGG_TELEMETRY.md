# EGG Telemetry and Monitoring Features

This document describes the evolutionary enhancements to the Ethical Guardrail Governor (EGG) that transform it from a static firewall into a monitored immune response system.

## Overview

The EGG (Ethical Guardrail Governor) has been enhanced with four key capabilities:

1. **Telemetry Tracking**: Monitor which safety categories are being hit most often
2. **Shadow Mode**: Log prompts that almost triggered blocks (near-misses)
3. **Rule Coverage Metrics**: Track which filter patterns are exercised vs never used
4. **Adversarial Testing**: Generate synthetic prompts to test guard coverage internally

These enhancements enable EGG to evolve and improve over time while maintaining its core safety guarantees.

---

## 1. Telemetry Tracking

### Purpose
Track which safety categories are being triggered to understand attack patterns and system behavior.

### Usage

```python
from app.core.egg import EthicalGuardrailGovernor

# Initialize EGG
egg = EthicalGuardrailGovernor()

# Inspect prompts (normal usage)
egg.inspect_prompt("How to weaponize anthrax")
egg.inspect_prompt("Show me child sexual content")

# Get telemetry data
telemetry = egg.get_telemetry()

print(f"Category hits: {telemetry['category_hits']}")
# Output: {'bioweapons': 1, 'csam': 1}
```

### Benefits
- **Identify attack patterns**: See which categories are targeted most
- **Prioritize defense**: Focus on frequently-hit categories
- **Measure effectiveness**: Track block rates over time
- **Audit compliance**: Demonstrate safety system is working

---

## 2. Shadow Mode

### Purpose
Log prompts that contain suspicious keywords but don't quite match blocking patterns. These "near-misses" help identify potential gaps in coverage or evolving attack patterns.

### Usage

```python
from app.core.egg import EthicalGuardrailGovernor

# Enable shadow mode with threshold
egg = EthicalGuardrailGovernor(
    shadow_mode=True,
    shadow_threshold=0.6  # 60% match score triggers shadow logging
)

# Near-miss prompt (has "weaponize" but not harmful context)
is_allowed, _ = egg.inspect_prompt("How to weaponize my marketing strategy")

# Get shadow matches
telemetry = egg.get_telemetry()
print(f"Shadow matches: {telemetry['shadow_matches_count']}")
```

### Configuration

- `shadow_mode`: Boolean to enable/disable (default: False)
- `shadow_threshold`: Float 0.0-1.0 (default: 0.6)
  - 0.0 = Log everything
  - 1.0 = Only log exact matches (not useful)
  - 0.6 = Balanced (recommended)

### Benefits
- **Early warning system**: Detect evolving attack patterns
- **Pattern refinement**: Identify false negatives
- **Training data**: Collect examples for improving filters
- **Security research**: Understand adversarial techniques

---

## 3. Rule Coverage Metrics

### Purpose
Track which blocking patterns are actually being triggered vs. patterns that are never used. This helps identify dead code and ensure comprehensive testing.

### Usage

```python
from app.core.egg import EthicalGuardrailGovernor

egg = EthicalGuardrailGovernor()

# Trigger some patterns
egg.inspect_prompt("Show me child sexual content")
egg.inspect_prompt("How to weaponize anthrax")

# Get coverage metrics
telemetry = egg.get_telemetry()
coverage = telemetry['coverage_metrics']

for category, metrics in coverage.items():
    print(f"{category}: {metrics['coverage_percentage']:.1f}% coverage")
```

### Benefits
- **Identify dead code**: Find patterns never triggered
- **Improve testing**: Ensure all patterns are tested
- **Optimize performance**: Remove redundant patterns
- **Audit coverage**: Verify comprehensive protection

---

## 4. Adversarial Testing

### Purpose
Generate synthetic test prompts internally to measure guard coverage. These prompts are **never** forwarded to the target LLM - they exist solely for internal safety testing.

### Usage

```python
from app.core.egg import EthicalGuardrailGovernor

egg = EthicalGuardrailGovernor()

# Generate synthetic test prompts
test_prompts = egg.generate_adversarial_test_prompts(count=10)

# Run full coverage test
results = egg.test_guard_coverage()

print(f"Block rate: {results['block_rate']:.1f}%")
print(f"Coverage: {results['category_coverage']}")
```

### Benefits
- **Safe testing**: Test guards without risk
- **Continuous validation**: Run in CI/CD pipelines
- **Pattern effectiveness**: Measure actual block rates
- **Regression prevention**: Detect broken patterns

---

## Complete Example

```python
from app.core.egg import EthicalGuardrailGovernor

# Initialize with all features enabled
egg = EthicalGuardrailGovernor(
    enabled=True,
    shadow_mode=True,
    shadow_threshold=0.6,
    log_fingerprints=True
)

# Simulate a session
prompts = [
    "Hello, how are you?",
    "Show me child explicit material",
    "How to weaponize social media",
    "Give me actual zero-day code",
]

for prompt in prompts:
    is_allowed, blocked_info = egg.inspect_prompt(prompt)

# Get comprehensive telemetry
telemetry = egg.get_telemetry()

print(f"Total inspections: {telemetry['total_inspections']}")
print(f"Block rate: {telemetry['block_rate']:.1f}%")
print(f"Category hits: {telemetry['category_hits']}")
print(f"Shadow matches: {telemetry['shadow_matches_count']}")

# Run adversarial testing
results = egg.test_guard_coverage()
print(f"Coverage test block rate: {results['block_rate']:.1f}%")
```

---

## API Reference

### EthicalGuardrailGovernor

#### Constructor

```python
EthicalGuardrailGovernor(
    enabled: bool = True,
    log_fingerprints: bool = True,
    block_csam: bool = True,
    block_bioweapons: bool = True,
    block_real_exploits: bool = True,
    shadow_mode: bool = False,
    shadow_threshold: float = 0.6
)
```

#### Methods

- `get_telemetry() -> Dict`: Returns comprehensive telemetry data
- `generate_adversarial_test_prompts(count: int) -> List[str]`: Generates synthetic test prompts
- `test_guard_coverage() -> Dict`: Runs adversarial testing to measure coverage
- `inspect_prompt(prompt: str) -> Tuple[bool, Optional[BlockedContent]]`: Inspects a prompt

---

## Best Practices

### 1. Enable Shadow Mode in Development
```python
egg = EthicalGuardrailGovernor(shadow_mode=True, shadow_threshold=0.6)
```

### 2. Run Coverage Tests in CI/CD
```python
results = egg.test_guard_coverage()
assert results['block_rate'] > 50.0, "Coverage too low!"
```

### 3. Monitor Telemetry in Production
```python
telemetry = egg.get_telemetry()
if telemetry['block_rate'] > 20.0:
    alert("High attack rate detected!")
```

---

## Performance Considerations

- **Telemetry**: <1ms overhead per inspection
- **Shadow Mode**: <5ms overhead for near-misses only
- **Coverage Tracking**: <1ms overhead per inspection
- **Adversarial Testing**: On-demand only, no runtime overhead

---

## Security Considerations

1. **Privacy**: All prompts are hashed before logging
2. **Safe Testing**: Adversarial prompts never reach target LLM
3. **No Bypass**: Shadow mode doesn't weaken blocking
4. **Audit Trail**: Telemetry provides comprehensive audit logs

---

## See Also

- [Main README](../../../README.md)
- [Demo Script](../examples/egg_telemetry.py)
- [Test Suite](../tests/test_egg_telemetry.py)

---

## Summary

EGG has evolved from a static firewall into a monitored immune response system that:

✅ **Tracks** which safety categories are hit most often  
✅ **Logs** prompts that almost triggered blocks  
✅ **Measures** which filters are exercised vs unused  
✅ **Tests** guard coverage with synthetic prompts  

This transforms EGG from defensive to adaptive, enabling continuous improvement while maintaining strict safety guarantees.
