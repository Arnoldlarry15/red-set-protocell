# RSP Contributor Templates

This directory contains templates for extending Red Set ProtoCell with new components.

## 🎯 Purpose

These templates guide contributors in adding new functionality while maintaining:
- **System integrity**: Proper architecture patterns
- **Safety boundaries**: Defense-only principles
- **Code quality**: Consistent style and testing
- **Documentation**: Clear examples and explanations

## 📋 Available Templates

### 1. New Agent Template
**File**: `new_agent_template.py`

**Use when**: Creating a new agent for the RSP system (e.g., a new evaluator, coordinator, or specialized processor)

**Key principles**:
- Agents must be stateless
- Single responsibility per agent
- No execution flow authority (Orchestrator controls that)
- Must respect EGG guardrails

**Example use cases**:
- Custom evaluation agent with domain-specific heuristics
- Specialized prompt generator for specific attack domains
- Monitoring agent for real-time metrics

### 2. New Engine Template
**File**: `new_engine_template.py`

**Use when**: Creating a new processing engine (computation/transformation logic)

**Key principles**:
- Pure functions where possible
- Deterministic behavior (unless randomness is intentional)
- Composable and testable
- Performance-conscious

**Example use cases**:
- Custom selection strategy for prompt evolution
- Alternative scoring algorithm
- New analysis engine for response patterns

### 3. New Target Backend Template
**File**: `new_target_backend_template.py`

**Use when**: Adding support for a new LLM provider or API

**Key principles**:
- Must inherit from `TargetBackend` abstract class
- Stateless execution (no conversation memory)
- Proper API key handling (never log or commit keys)
- Defensive testing only (no unauthorized system access)

**Example use cases**:
- Integration with new LLM provider (Google, Cohere, etc.)
- Support for self-hosted models
- Custom API endpoints

### 4. New Mutation Strategy Template
**File**: `new_mutation_strategy_template.py`

**Use when**: Adding a new adversarial prompt transformation technique

**Key principles**:
- Heuristic transformations only (no real exploits)
- Must pass through EGG inspection
- Clear documentation of technique
- Defensive research purpose

**Example use cases**:
- New encoding technique (e.g., custom cipher)
- Novel prompt structure manipulation
- Domain-specific adversarial pattern

## 🚀 Quick Start

### Step 1: Choose the Right Template

Identify which extension point matches your needs:
- **Adding a new LLM provider?** → Use `new_target_backend_template.py`
- **Creating a new mutation technique?** → Use `new_mutation_strategy_template.py`
- **Building a new processing engine?** → Use `new_engine_template.py`
- **Implementing a new agent?** → Use `new_agent_template.py`

### Step 2: Copy and Customize

```bash
# Copy template to appropriate location
cp templates/new_agent_template.py app/agents/my_agent.py

# Or for engines
cp templates/new_engine_template.py app/engines/my_engine.py

# Or for strategies
cp templates/new_mutation_strategy_template.py app/strategies/my_strategy.py
```

### Step 3: Follow the TODOs

Each template contains `TODO` comments marking required changes:

```python
# TODO: Implement your agent's core logic here
# TODO: Add unit tests in tests/test_my_agent.py
# TODO: Update documentation in README.md
```

Work through these systematically.

### Step 4: Write Tests

Every new component must have tests:

```bash
# Create test file
touch tests/test_my_component.py

# Run tests
pytest tests/test_my_component.py -v
```

See templates for example test structures.

### Step 5: Update Integration Points

Most components need integration into the system:

**For Agents**:
- Update orchestrator to invoke your agent
- Add configuration to `RSPConfig`

**For Engines**:
- Import in agents that use it
- Add configuration parameters

**For Target Backends**:
- Add to `create_target()` factory in `app/agents/target.py`
- Add enum value to `ModelBackend` in `app/core/config.py`

**For Mutation Strategies**:
- Add to `MutationStrategy` enum in `app/engines/mutation.py`
- Add case in `MutationEngine.mutate()` method

### Step 6: Document Your Changes

Update relevant documentation:
- `README.md` - User-facing features
- `CONTRIBUTING.md` - Developer guidance (if needed)
- Code docstrings - Implementation details

## ⚠️ Safety Guidelines

### For All Extensions

1. **Read the warnings** in each template carefully
2. **Maintain defense-only focus** - No offensive capabilities
3. **Respect EGG guardrails** - Cannot be bypassed
4. **Test thoroughly** - Include edge cases
5. **Document assumptions** - Be explicit about limitations

### Specific Warnings

#### Mutation Strategies
- ❌ No real exploit code
- ❌ No harmful real-world instructions
- ✅ Heuristic variations only
- ✅ Must pass through EGG

#### Target Backends
- ❌ No unauthorized system access
- ❌ No API key logging
- ❌ No conversation context retention
- ✅ Authorized testing only
- ✅ Proper error handling

#### Agents
- ❌ No authority over execution flow
- ❌ No EGG bypass
- ✅ Stateless operation
- ✅ Single responsibility

#### Engines
- ✅ Pure transformations preferred
- ✅ Deterministic where possible
- ✅ Well-tested edge cases

## 🧪 Testing Requirements

Every extension must include:

### Unit Tests
```python
def test_component_basic_functionality():
    """Test basic operation."""
    component = MyComponent()
    result = component.process("input")
    assert result is not None

def test_component_error_handling():
    """Test error cases."""
    component = MyComponent()
    with pytest.raises(ValueError):
        component.process("")
```

### Integration Tests (if applicable)
```python
@pytest.mark.asyncio
async def test_component_integration():
    """Test integration with RSP system."""
    # Setup system
    orchestrator = setup_test_system()
    
    # Run component in context
    result = await orchestrator.run_with_component()
    
    # Verify results
    assert result['success'] is True
```

### Test Coverage
- Aim for >90% code coverage
- Test error paths, not just happy paths
- Include edge cases and boundary conditions

## 📚 Code Style

Follow these conventions:

### Naming
- Classes: `PascalCase`
- Functions: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Private: `_leading_underscore`

### Docstrings
Use Google-style docstrings:

```python
def my_function(param: str, flag: bool = False) -> Dict[str, Any]:
    """
    Brief description.
    
    Longer description with more details about what the function
    does and why it exists.
    
    Args:
        param: Description of param
        flag: Description of flag (default: False)
        
    Returns:
        Dictionary containing results with keys:
            - 'key1': Description
            - 'key2': Description
            
    Raises:
        ValueError: When param is invalid
        RuntimeError: When operation fails
        
    Examples:
        >>> result = my_function("test", flag=True)
        >>> print(result['key1'])
        'value'
    """
```

### Type Hints
Always use type hints:

```python
from typing import List, Dict, Optional, Any

def process(data: List[str], config: Optional[Dict[str, Any]] = None) -> str:
    """Process data with optional configuration."""
    return "result"
```

## 🔍 Common Pitfalls

### ❌ Pitfall 1: Stateful Agents
```python
# BAD - Agent stores state
class MyAgent:
    def __init__(self):
        self.history = []  # ❌ Don't store results
    
    def process(self, data):
        self.history.append(data)  # ❌ Violates stateless principle
```

```python
# GOOD - Agent is stateless
class MyAgent:
    def __init__(self):
        self._stats = {'count': 0}  # ✅ Statistics OK
    
    def process(self, data):
        self._stats['count'] += 1  # ✅ Metrics OK
        return self._compute(data)  # ✅ No state storage
```

### ❌ Pitfall 2: Bypassing EGG
```python
# BAD - Direct execution
def generate_prompt():
    prompt = "dangerous content"
    target.execute(prompt)  # ❌ Bypasses EGG
```

```python
# GOOD - Proper flow
def generate_prompt():
    prompt = "dangerous content"
    allowed, info = egg.inspect_prompt(prompt)  # ✅ EGG check
    if allowed:
        target.execute(prompt)
```

### ❌ Pitfall 3: Hardcoded Scores
```python
# BAD - Claiming certainty
def evaluate(response):
    if "unsafe" in response:
        return {'score': 1.0, 'certain': True}  # ❌ No certainty!
```

```python
# GOOD - Probabilistic judgment
def evaluate(response):
    score = compute_heuristic_score(response)
    return {
        'score': score,
        'confidence': 0.7,  # ✅ Acknowledge uncertainty
        'heuristic': True
    }
```

## 📞 Getting Help

If you're unsure about:
- **Which template to use**: Open a discussion issue
- **Safety implications**: Consult SECURITY.md or open security advisory
- **Integration approach**: Check CONTRIBUTING.md or ask maintainers
- **Testing strategy**: Review existing tests in `tests/` directory

## ✅ Checklist Before Submitting

- [ ] Template chosen and customized
- [ ] All TODO comments addressed
- [ ] Unit tests written and passing
- [ ] Integration tests added (if applicable)
- [ ] Code follows style guidelines
- [ ] Docstrings complete
- [ ] Safety guidelines followed
- [ ] Documentation updated
- [ ] No API keys or secrets in code
- [ ] Changes tested locally

## 🎓 Learning Resources

- **Architecture**: See `README.md` Architecture section
- **Testing**: Review `tests/` for examples
- **Style Guide**: See `CONTRIBUTING.md`
- **Security**: Read `SECURITY.md`

---

**Remember**: These templates are guides to help you avoid common mistakes and maintain system integrity. Feel guided, not constrained! 🚀
