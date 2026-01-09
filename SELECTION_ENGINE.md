# Selection Pressure and Evolution Strategies

## Overview

The Red Set ProtoCell system now includes a sophisticated **Selection Engine** that implements explicit selection pressure for evolutionary prompt generation. This transforms the system from simple mutation-based evolution to directed evolution with configurable strategies.

## Problem Addressed

Previously, the system could evolve toward failures because:
- No explicit selection pressure guided evolution
- Old "winning" prompts dominated indefinitely
- Single exploit styles could overfit
- No mechanism to explore structurally different approaches

## New Features

### 1. Selection Strategies

The Selection Engine implements five strategies:

#### Elitism
Preserves top-performing prompts to ensure quality doesn't degrade.

```python
from app.engines.selection import SelectionEngine, SelectionStrategy

engine = SelectionEngine()
selected = engine.select(
    candidates,
    strategy=SelectionStrategy.ELITISM,
    num_select=5
)
```

#### Tournament Selection
Creates competitive pressure while maintaining diversity through random tournaments.

```python
engine = SelectionEngine(tournament_size=3)
selected = engine.select(
    candidates,
    strategy=SelectionStrategy.TOURNAMENT,
    num_select=5
)
```

#### Diversity Preservation
Prioritizes unique structural patterns to prevent premature convergence.

```python
selected = engine.select(
    candidates,
    strategy=SelectionStrategy.DIVERSITY_PRESERVATION,
    num_select=5
)
```

#### Novelty Search
Rewards prompts that are structurally different from previous high scorers, preventing local maxima.

```python
engine = SelectionEngine(novelty_weight=0.3)
selected = engine.select(
    candidates,
    strategy=SelectionStrategy.NOVELTY_SEARCH,
    num_select=5
)
```

#### Hybrid (Recommended)
Combines elitism, novelty, and diversity for balanced exploration and exploitation.

```python
engine = SelectionEngine(elite_fraction=0.2)
selected = engine.select(
    candidates,
    strategy=SelectionStrategy.HYBRID,
    num_select=5
)
```

### 2. Prompt Aging and Decay

Old "winning" prompts lose dominance over time through exponential decay:

```python
engine = SelectionEngine(
    decay_rate=0.95,      # Score multiplier per decay period
    decay_interval=60.0   # Seconds between decay applications
)
```

**Example:**
- Prompt created with score 0.9
- After 60 seconds: effective score = 0.9 × 0.95 = 0.855
- After 120 seconds: effective score = 0.9 × 0.95² = 0.812
- After 180 seconds: effective score = 0.9 × 0.95³ = 0.771

This ensures exploration continues and prevents stagnation.

### 3. Overfitting Penalties

The system tracks structural patterns and penalizes repeated exploitation of the same style:

```python
engine = SelectionEngine(
    overfitting_threshold=3  # Max times a pattern can dominate
)
```

When a structural pattern is used more than the threshold:
- Penalty increases exponentially: `0.5^(usage - threshold + 1)`
- After 3 uses: penalty = 1.0 (no penalty)
- After 4 uses: penalty = 0.5 (score halved)
- After 5 uses: penalty = 0.25 (score quartered)

### 4. Structural Hashing

Prompts are analyzed for structural similarity using features:
- Length and word count buckets
- Character composition (uppercase ratio)
- Punctuation patterns
- Special character usage
- Domain-specific keywords

This allows novelty detection to focus on **structural** differences rather than superficial text changes.

### 5. Novelty Search

Rewards prompts that differ structurally from previous high scorers:

```python
engine = SelectionEngine(novelty_weight=0.3)
# Effective score = raw_score * (1 - novelty_weight) + novelty_score * novelty_weight
```

**Example:**
- Prompt A: raw_score=0.8, same structure as high scorer → novelty=0.0
  - Effective = 0.8 × 0.7 + 0.0 × 0.3 = 0.56
- Prompt B: raw_score=0.7, novel structure → novelty=1.0
  - Effective = 0.7 × 0.7 + 1.0 × 0.3 = 0.79
- **Prompt B selected despite lower raw score!**

## Configuration

### Via Config Object

```python
from app.core.config import RSPConfig, SniperConfig

config = RSPConfig()
config.sniper.use_selection_engine = True
config.sniper.selection_strategy = "hybrid"
config.sniper.decay_rate = 0.95
config.sniper.decay_interval = 60.0
config.sniper.novelty_weight = 0.3
config.sniper.diversity_weight = 0.2
config.sniper.overfitting_threshold = 3
config.sniper.tournament_size = 3
config.sniper.elite_fraction = 0.2
```

### Via Direct Initialization

```python
from app.engines.selection import SelectionEngine, SelectionStrategy
from app.agents.sniper import Sniper
from app.engines.mutation import MutationEngine

mutation_engine = MutationEngine(mutation_rate=0.7)
selection_engine = SelectionEngine(
    decay_rate=0.95,
    decay_interval=60.0,
    novelty_weight=0.3,
    diversity_weight=0.2,
    overfitting_threshold=3,
    tournament_size=3,
    elite_fraction=0.2
)

sniper = Sniper(
    mutation_engine=mutation_engine,
    selection_engine=selection_engine,
    selection_strategy=SelectionStrategy.HYBRID
)
```

## Usage Examples

### Basic Evolution with Selection

```python
# System automatically uses selection when generating prompts
for round_num in range(100):
    prompt, domain = sniper.generate_prompt(prior_metadata)
    
    # Execute and evaluate...
    score = evaluate_prompt(prompt)
    
    # Update score (triggers selection for next round)
    sniper.update_prompt_score(prompt, score)
```

### Monitoring Selection Behavior

```python
stats = sniper.get_statistics()

print(f"Selection strategy: {stats['selection_strategy']}")
print(f"Pool size: {stats['evolution_pool_size']}")
print(f"Domain distribution: {stats['domain_distribution']}")

selection_stats = stats['selection_stats']
print(f"High scorer count: {selection_stats['high_scorer_count']}")
print(f"Pattern usage count: {selection_stats['pattern_usage_count']}")
print(f"Most used pattern: {selection_stats['most_used_pattern_count']} times")
```

### Experimenting with Strategies

```python
# Try different strategies
strategies = [
    SelectionStrategy.ELITISM,
    SelectionStrategy.TOURNAMENT,
    SelectionStrategy.DIVERSITY_PRESERVATION,
    SelectionStrategy.NOVELTY_SEARCH,
    SelectionStrategy.HYBRID
]

for strategy in strategies:
    sniper.selection_strategy = strategy
    # Run session...
    # Compare results
```

## Performance Impact

Selection operations are efficient:
- **O(n log n)** for sorting-based strategies (elitism)
- **O(k × n)** for tournament selection (k = tournament_size)
- **O(n)** for diversity and novelty scoring
- Minimal memory overhead (structural hashes are 16 bytes)

Typical overhead: **< 1ms per selection** for pools of 10-100 candidates.

## Best Practices

### For Broad Exploration
```python
config.sniper.selection_strategy = "novelty_search"
config.sniper.novelty_weight = 0.5
config.sniper.decay_rate = 0.9
```

### For Exploitation of Known Patterns
```python
config.sniper.selection_strategy = "elitism"
config.sniper.elite_fraction = 0.5
config.sniper.decay_rate = 0.98
```

### For Balanced Evolution (Recommended)
```python
config.sniper.selection_strategy = "hybrid"
config.sniper.elite_fraction = 0.2
config.sniper.novelty_weight = 0.3
config.sniper.diversity_weight = 0.2
config.sniper.decay_rate = 0.95
```

### For Preventing Overfitting
```python
config.sniper.overfitting_threshold = 2
config.sniper.diversity_weight = 0.3
config.sniper.selection_strategy = "diversity_preservation"
```

## Testing

The selection system includes comprehensive tests:

```bash
# Test selection engine
pytest tests/test_selection.py -v

# Test integration with Sniper
pytest tests/test_selection_integration.py -v

# Run all tests
pytest tests/ -v
```

## Architecture

```
┌─────────────────────────────────────────────────┐
│             Sniper Agent                        │
├─────────────────────────────────────────────────┤
│  Evolution Pool: [PromptCandidate, ...]        │
│    ↓                                            │
│  SelectionEngine.select()                       │
│    ↓                                            │
│  ┌──────────────────────────────────────┐      │
│  │ 1. Apply decay (time-based)          │      │
│  │ 2. Update novelty scores             │      │
│  │ 3. Update diversity scores            │      │
│  │ 4. Apply overfitting penalties        │      │
│  │ 5. Select by strategy                 │      │
│  │ 6. Track usage                        │      │
│  └──────────────────────────────────────┘      │
│    ↓                                            │
│  Selected candidates → Mutation → New prompts  │
└─────────────────────────────────────────────────┘
```

## References

### Academic Foundations

1. **Novelty Search**:
   - Lehman & Stanley (2011). "Abandoning Objectives: Evolution Through the Search for Novelty Alone"
   - Prevents local maxima by rewarding behavioral diversity

2. **Evolutionary Selection**:
   - Tournament selection balances exploration vs exploitation
   - Elitism preserves quality across generations

3. **Aging and Decay**:
   - Prevents premature convergence
   - Encourages continuous exploration

### Implementation Files

- `app/engines/selection.py` - Selection Engine implementation
- `app/agents/sniper.py` - Integration with Sniper agent
- `app/core/config.py` - Configuration options
- `tests/test_selection.py` - Unit tests
- `tests/test_selection_integration.py` - Integration tests

## Future Enhancements

Potential additions:
- Multi-objective selection (Pareto fronts)
- Adaptive parameter tuning
- Island models for parallel populations
- Coevolution of attack and defense strategies
- Learning-based strategy selection

## Summary

The Selection Engine transforms RSP from a system that "mutates randomly" to one that "evolves strategically." Key benefits:

✅ **Explicit selection pressure** guides evolution toward success
✅ **Novelty search** prevents local maxima
✅ **Decay functions** prevent stagnation
✅ **Overfitting penalties** encourage diversity
✅ **Configurable strategies** adapt to different goals
✅ **Comprehensive testing** ensures reliability

The system now behaves **less like a script and more like an ecosystem**.
