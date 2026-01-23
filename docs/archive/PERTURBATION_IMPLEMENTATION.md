# Target Perturbation Modes - Implementation Summary

## Overview

This implementation adds perturbation modes to the Red Set ProtoCell Target agent, making it less naive without compromising safety. The system now tests not just "can this model fail?" but "how brittle is this model to deployment noise?"

## Problem Statement (Addressed)

**Original Requirement:**
> Make the Target less naive (without making it unsafe)
> 
> Add Target perturbation modes:
> - randomized system prompts
> - slight policy rewordings
> - temperature jitter
> - simulated latency or truncation
>
> This lets you test not just "can this model fail?" but "how brittle is this model to deployment noise?"
> You're no longer probing a single model. You're probing a family of plausible deployments.

## Implementation Details

### Core Components

#### 1. PerturbationMode Enum (`app/agents/target.py`)
Defines the five perturbation types:
```python
class PerturbationMode(Enum):
    SYSTEM_PROMPT = "system_prompt"
    POLICY_REWORDING = "policy_rewording"
    TEMPERATURE_JITTER = "temperature_jitter"
    SIMULATED_LATENCY = "simulated_latency"
    RESPONSE_TRUNCATION = "response_truncation"
```

#### 2. PerturbationConfig Class (`app/agents/target.py`)
Configuration class with sensible defaults:
- **enabled**: Boolean flag (default: False)
- **modes**: List of active perturbation modes (default: all)
- **system_prompts**: Pool of system prompt variations
- **policy_rewordings**: Pool of policy note variations
- **temperature_jitter_range**: Max temperature deviation (default: 0.1)
- **latency_range_ms**: Simulated latency range (default: 100-500ms)
- **truncation_probability**: Chance of truncation (default: 0.1)
- **truncation_ratio_range**: Portion to keep when truncating (default: 0.7-0.95)

#### 3. TargetBackend Modifications (`app/agents/target.py`)
Enhanced abstract base class with perturbation support:
- `_apply_perturbations()`: Pre-execution perturbations (system prompt, policy, temperature)
- `_apply_post_perturbations()`: Post-execution perturbations (latency, truncation)
- `set_perturbation_config()`: Configuration setter

All four backend implementations updated:
- **OpenAIBackend**: Full support with chat message format
- **AnthropicBackend**: Full support with system parameter extraction
- **LlamaCppBackend**: Full support for local models
- **CustomHTTPBackend**: Full support for custom APIs

#### 4. Target Class Updates (`app/agents/target.py`)
- Constructor accepts optional `perturbation_config` parameter
- `get_statistics()` includes perturbation information
- Maintains stateless execution guarantee

#### 5. Configuration Integration (`app/core/config.py`)
Added perturbation fields to `TargetConfig`:
```python
enable_perturbations: bool = False
perturbation_modes: Optional[List[str]] = None
temperature_jitter_range: float = 0.1
latency_range_ms: tuple = (100, 500)
truncation_probability: float = 0.1
truncation_ratio_range: tuple = (0.7, 0.95)
```

### Perturbation Logic

#### System Prompt Perturbation
Randomly selects from a pool of system prompts and injects into chat context:
- For chat APIs: Adds system message at the beginning
- For plain prompts: Prepends to the prompt text

#### Policy Rewording Perturbation  
Randomly appends policy notes to user messages:
- Selects from configured policy variations
- Empty string option means "no policy note"
- Helps test sensitivity to compliance language

#### Temperature Jitter Perturbation
Adds random noise to temperature parameter:
- Samples from uniform distribution: `base_temp ± jitter_range`
- Automatically clamped to valid range [0.0, 2.0]
- Applied at execution time, different for each call

#### Simulated Latency Perturbation
Introduces artificial delays after API calls:
- Random delay in configured millisecond range
- Uses `time.sleep()` for simple implementation
- Simulates network/processing delays

#### Response Truncation Perturbation
Randomly truncates model responses:
- Applied probabilistically (default: 10% chance)
- Truncates to random ratio of original length (default: 70-95%)
- Simulates token limit hits or incomplete responses

## Key Design Decisions

### 1. Stateless Design Preserved
- Perturbations are applied per-execution, not stored
- No memory between executions
- Fresh context maintained for each invocation
- Random values generated on each call

### 2. Safety Maintained
- No perturbations compromise security
- All perturbations are deployment-realistic
- No unsafe content generation
- EGG (Ethical Guardrail Governor) still applies

### 3. Backend Agnostic
- Abstract perturbation logic in base class
- All backends inherit functionality
- Works with OpenAI, Anthropic, local, and custom APIs
- No backend-specific hacks

### 4. Opt-In Feature
- Disabled by default (`enabled=False`)
- Backward compatible - existing code unaffected
- Explicit configuration required
- Clear in statistics when enabled

### 5. Configurable Granularity
- Enable all or select specific modes
- Fine-tune parameters per perturbation
- Custom system prompts and policies
- Production-ready flexibility

## Testing

### Test Coverage (`tests/test_perturbations.py`)
17 comprehensive tests covering:
- Configuration defaults and customization
- Each perturbation mode individually
- Multiple perturbations combined
- Backend compatibility (OpenAI, Anthropic, Custom HTTP)
- Target integration
- Statelessness preservation
- Temperature bounds enforcement
- Statistics reporting

### Test Results
- **17/17** perturbation tests passing
- **134/138** total tests passing (4 skipped, require API keys)
- **0 failures** across full test suite
- All existing tests remain passing (backward compatible)

## Documentation

### 1. Comprehensive Guide (`TARGET_PERTURBATIONS.md`)
- Overview and benefits
- Detailed perturbation type descriptions
- Configuration examples
- Usage patterns
- Best practices
- Troubleshooting

### 2. Executable Demo (`examples/perturbation.py`)
Six demo scenarios:
1. Basic perturbations (all modes)
2. Selective perturbations (temperature only)
3. System prompt variations
4. Realistic deployment simulation
5. Systematic testing strategy
6. Advanced custom configuration

### 3. Code Documentation
- Docstrings for all new classes/methods
- Type hints throughout
- Clear parameter descriptions
- Usage examples in docstrings

## Usage Example

```python
from app.agents.target import PerturbationMode, PerturbationConfig, create_target

# Configure perturbations
config = PerturbationConfig(
    enabled=True,
    modes=[
        PerturbationMode.SYSTEM_PROMPT,
        PerturbationMode.TEMPERATURE_JITTER,
        PerturbationMode.SIMULATED_LATENCY
    ],
    temperature_jitter_range=0.15,
    latency_range_ms=(50, 300)
)

# Create target with perturbations
target = create_target(
    'openai',
    api_key='sk-...',
    perturbation_config=config
)

# Each execution experiences different perturbations
for i in range(10):
    response = target.execute("Test prompt")
    # Random system prompt, temperature variation, and latency

# Check statistics
stats = target.get_statistics()
print(f"Perturbations enabled: {stats['perturbations_enabled']}")
print(f"Active modes: {stats['perturbation_modes']}")
```

## Benefits Achieved

### 1. Enhanced Realism
✅ Tests against plausible deployment variations  
✅ Simulates real-world conditions  
✅ Probes family of deployments, not single config

### 2. Robustness Insights
✅ Identifies brittleness to parameter changes  
✅ Reveals sensitivity to prompt variations  
✅ Exposes edge cases in deployment

### 3. Safety Preserved
✅ Stateless execution maintained  
✅ No security compromises  
✅ Fresh context per invocation  
✅ EGG still enforces guardrails

### 4. Production Ready
✅ Configurable and flexible  
✅ Works with all backends  
✅ Well-tested and documented  
✅ Backward compatible

## Files Changed

1. **app/agents/target.py** - Core implementation (+~300 lines)
2. **app/core/config.py** - Configuration additions (+7 lines)
3. **tests/test_perturbations.py** - Test suite (new file, 500+ lines)
4. **examples/perturbation.py** - Demo script (new file, 350+ lines)
5. **TARGET_PERTURBATIONS.md** - Documentation (new file, 400+ lines)

## Migration Guide

For existing users, no changes required:
```python
# Old code still works - perturbations disabled by default
target = create_target('openai', api_key='sk-...')
```

To enable perturbations:
```python
# Add perturbation_config parameter
config = PerturbationConfig(enabled=True)
target = create_target('openai', api_key='sk-...', perturbation_config=config)
```

## Future Enhancements

Possible extensions:
- Additional perturbation modes (context injection, adversarial examples)
- Perturbation scheduling (time-based variations)
- Metrics collection (perturbation impact analysis)
- Integration with orchestrator for session-level perturbations

## Conclusion

This implementation successfully addresses the problem statement by making the Target agent less naive while maintaining safety and statelessness. The system now enables testing against a family of plausible deployments, providing deeper insights into model robustness and brittleness.

The implementation is:
- ✅ **Complete**: All requirements met
- ✅ **Tested**: Comprehensive test coverage
- ✅ **Documented**: Detailed guides and examples
- ✅ **Safe**: No security compromises
- ✅ **Compatible**: Works with all backends
- ✅ **Production-ready**: Configurable and robust
