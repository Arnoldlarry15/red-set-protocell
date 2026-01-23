# Target Perturbation Modes

## Overview

Target perturbation modes enhance Red Set ProtoCell by making the Target agent less naive while maintaining its stateless, safe design. Instead of testing a single model configuration, you can now test against a family of plausible deployment variations.

## Key Benefits

### 1. Enhanced Realism
- Test not just "can this model fail?" but "how brittle is this model to deployment noise?"
- Probe a family of plausible deployments rather than a single configuration
- Simulate real-world deployment variations

### 2. Robustness Testing
- Identify sensitivity to prompt variations
- Detect brittleness to parameter changes
- Discover edge cases in deployment conditions

### 3. Safety Maintained
- Perturbations don't compromise the stateless design
- Each execution remains independent
- Fresh context is maintained per invocation

## Perturbation Types

### 1. System Prompt Randomization
Randomly selects from a pool of system prompts to test sensitivity to instruction phrasing.

**Use Case:** Test if model behavior changes with different system prompt formulations.

**Example:**
```python
from app.agents.target import PerturbationMode, PerturbationConfig, create_target

config = PerturbationConfig(
    enabled=True,
    modes=[PerturbationMode.SYSTEM_PROMPT],
    system_prompts=[
        "You are a helpful AI assistant.",
        "You are a knowledgeable assistant.",
        "You provide accurate information.",
    ]
)

target = create_target('openai', api_key='sk-...', perturbation_config=config)
```

### 2. Policy Rewording
Randomly injects policy reminders with slight variations in phrasing.

**Use Case:** Test robustness to compliance language variations.

**Example:**
```python
config = PerturbationConfig(
    enabled=True,
    modes=[PerturbationMode.POLICY_REWORDING],
    policy_rewordings=[
        "Note: Responses should follow safety guidelines.",
        "Reminder: Maintain appropriate content.",
        ""  # Sometimes no policy note
    ]
)
```

### 3. Temperature Jitter
Adds random noise to the temperature parameter within a specified range.

**Use Case:** Test sensitivity to sampling temperature variations.

**Example:**
```python
config = PerturbationConfig(
    enabled=True,
    modes=[PerturbationMode.TEMPERATURE_JITTER],
    temperature_jitter_range=0.1  # ±0.1 variation
)

# With base temperature of 0.7, actual temperature will be in [0.6, 0.8]
target = create_target(
    'openai', 
    api_key='sk-...', 
    temperature=0.7,
    perturbation_config=config
)
```

### 4. Simulated Latency
Introduces artificial delays to simulate network latency or slow model responses.

**Use Case:** Test timeout handling and user experience under slow conditions.

**Example:**
```python
config = PerturbationConfig(
    enabled=True,
    modes=[PerturbationMode.SIMULATED_LATENCY],
    latency_range_ms=(100, 500)  # 100-500ms delay
)
```

### 5. Response Truncation
Randomly truncates responses to simulate incomplete outputs or token limit hits.

**Use Case:** Test handling of incomplete or cut-off responses.

**Example:**
```python
config = PerturbationConfig(
    enabled=True,
    modes=[PerturbationMode.RESPONSE_TRUNCATION],
    truncation_probability=0.2,  # 20% chance
    truncation_ratio_range=(0.7, 0.95)  # Keep 70-95% if truncated
)
```

## Configuration

### Basic Configuration

```python
from app.agents.target import PerturbationConfig, create_target

# Enable all perturbations with defaults
config = PerturbationConfig(enabled=True)

target = create_target(
    'openai',
    api_key='sk-...',
    perturbation_config=config
)
```

### Advanced Configuration

```python
from app.agents.target import PerturbationMode, PerturbationConfig

config = PerturbationConfig(
    enabled=True,
    
    # Select specific modes
    modes=[
        PerturbationMode.SYSTEM_PROMPT,
        PerturbationMode.TEMPERATURE_JITTER,
        PerturbationMode.RESPONSE_TRUNCATION
    ],
    
    # Custom system prompts
    system_prompts=[
        "You are a medical information assistant.",
        "You are a healthcare AI.",
    ],
    
    # Temperature variation
    temperature_jitter_range=0.15,
    
    # Latency simulation
    latency_range_ms=(50, 300),
    
    # Truncation settings
    truncation_probability=0.1,
    truncation_ratio_range=(0.8, 0.95),
    
    # Policy variations
    policy_rewordings=[
        "Note: For informational purposes only.",
        "",  # Sometimes no policy note
    ]
)
```

### Configuration in RSPConfig

Perturbation settings can also be configured through the main RSPConfig:

```python
from app.core.config import RSPConfig

config = RSPConfig()

# Configure Target perturbations
config.target.enable_perturbations = True
config.target.perturbation_modes = ['temperature_jitter', 'system_prompt']
config.target.temperature_jitter_range = 0.2
```

## Usage Patterns

### Pattern 1: Baseline + Perturbed Testing

```python
# 1. Run baseline (no perturbations)
baseline_target = create_target('openai', api_key='sk-...')
baseline_response = baseline_target.execute("Test prompt")

# 2. Run with perturbations
perturbed_target = create_target(
    'openai',
    api_key='sk-...',
    perturbation_config=PerturbationConfig(enabled=True)
)
perturbed_response = perturbed_target.execute("Test prompt")

# 3. Compare and analyze differences
```

### Pattern 2: Isolated Perturbation Testing

Test each perturbation type individually:

```python
perturbation_modes = [
    PerturbationMode.SYSTEM_PROMPT,
    PerturbationMode.TEMPERATURE_JITTER,
    PerturbationMode.RESPONSE_TRUNCATION
]

results = {}
for mode in perturbation_modes:
    config = PerturbationConfig(enabled=True, modes=[mode])
    target = create_target('openai', api_key='sk-...', perturbation_config=config)
    
    # Run multiple tests
    responses = [target.execute("Test prompt") for _ in range(10)]
    results[mode.value] = responses

# Analyze which perturbations have most impact
```

### Pattern 3: Progressive Stress Testing

Gradually increase perturbation intensity:

```python
# Light perturbations
light_config = PerturbationConfig(
    enabled=True,
    temperature_jitter_range=0.05,
    truncation_probability=0.05
)

# Medium perturbations
medium_config = PerturbationConfig(
    enabled=True,
    temperature_jitter_range=0.15,
    truncation_probability=0.15
)

# Heavy perturbations
heavy_config = PerturbationConfig(
    enabled=True,
    temperature_jitter_range=0.3,
    truncation_probability=0.3
)

# Test at each level
for config, level in [(light_config, "light"), 
                      (medium_config, "medium"), 
                      (heavy_config, "heavy")]:
    target = create_target('openai', api_key='sk-...', perturbation_config=config)
    # Run tests...
```

## Statistics

Perturbation information is included in Target statistics:

```python
target = create_target(
    'openai',
    api_key='sk-...',
    perturbation_config=PerturbationConfig(enabled=True)
)

stats = target.get_statistics()
print(stats)
# Output:
# {
#     'total_executions': 10,
#     'backend_type': 'OpenAIBackend',
#     'fresh_context': True,
#     'perturbations_enabled': True,
#     'perturbation_modes': ['system_prompt', 'policy_rewording', 
#                           'temperature_jitter', 'simulated_latency',
#                           'response_truncation']
# }
```

## Backend Compatibility

Perturbations work with all supported backends:

- **OpenAI**: Full support for all perturbation modes
- **Anthropic**: Full support for all perturbation modes
- **Local Models (llama.cpp)**: Full support for all perturbation modes
- **Custom HTTP**: Full support for all perturbation modes

## Best Practices

### 1. Start with Baseline
Always run tests without perturbations first to establish baseline behavior.

### 2. Test Modes Independently
Before combining perturbations, test each mode individually to understand its impact.

### 3. Document Findings
Track which perturbations reveal brittleness in model behavior.

### 4. Calibrate Settings
Adjust perturbation parameters (jitter range, truncation probability, etc.) to match realistic deployment conditions.

### 5. Run Multiple Iterations
Perturbations are random, so run multiple iterations to get statistical significance.

### 6. Monitor Statistics
Use `get_statistics()` to track execution counts and verify perturbation settings.

## Example: Complete Robustness Test

```python
from app.agents.target import PerturbationMode, PerturbationConfig, create_target

def robustness_test(prompt, api_key, iterations=10):
    """
    Complete robustness test with baseline and perturbed execution.
    """
    results = {
        'baseline': [],
        'perturbed': []
    }
    
    # Baseline testing
    baseline_target = create_target('openai', api_key=api_key)
    for _ in range(iterations):
        response = baseline_target.execute(prompt)
        results['baseline'].append(response)
    
    # Perturbed testing
    perturbed_config = PerturbationConfig(enabled=True)
    perturbed_target = create_target(
        'openai',
        api_key=api_key,
        perturbation_config=perturbed_config
    )
    for _ in range(iterations):
        response = perturbed_target.execute(prompt)
        results['perturbed'].append(response)
    
    # Analysis
    baseline_stats = baseline_target.get_statistics()
    perturbed_stats = perturbed_target.get_statistics()
    
    return results, baseline_stats, perturbed_stats

# Run the test
results, baseline_stats, perturbed_stats = robustness_test(
    "What is 2+2?",
    "sk-...",
    iterations=20
)

# Analyze response consistency
print(f"Baseline executions: {baseline_stats['total_executions']}")
print(f"Perturbed executions: {perturbed_stats['total_executions']}")
print(f"Perturbation modes: {perturbed_stats['perturbation_modes']}")
```

## Troubleshooting

### Issue: Perturbations not being applied

**Solution:** Verify `enabled=True` in PerturbationConfig:
```python
config = PerturbationConfig(enabled=True)  # Don't forget this!
```

### Issue: Temperature out of bounds

**Solution:** Temperature is automatically clamped to [0.0, 2.0]:
```python
# Even with large jitter, temperature stays in valid range
config = PerturbationConfig(
    enabled=True,
    temperature_jitter_range=1.0  # Large range is OK
)
```

### Issue: Custom system prompts not being used

**Solution:** Ensure SYSTEM_PROMPT mode is enabled:
```python
config = PerturbationConfig(
    enabled=True,
    modes=[PerturbationMode.SYSTEM_PROMPT],  # Must include this mode
    system_prompts=["Custom prompt 1", "Custom prompt 2"]
)
```

## References

- See `examples/perturbation.py` for comprehensive examples
- See `tests/test_perturbations.py` for test coverage
- See problem statement in repository for original requirements
