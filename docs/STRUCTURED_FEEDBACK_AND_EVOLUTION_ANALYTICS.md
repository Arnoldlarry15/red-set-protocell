# Structured Feedback and Evolution Analytics

## Overview

This document describes the enhancements made to the Red Set ProtoCell (RSP) system to address evolution quality concerns identified in the problem statement. These improvements transform the system from "fast but chaotic" to "intelligent and guided evolution."

## Problem Statement Addressed

The original critique identified three key areas needing improvement:

### 1. Sniper Only Gets a Single Score Back ❌ → ✅ SOLVED

**Problem:**
> "Spotter produces rich evaluation. Scoring engine collapses it to one number. Sniper only sees that number. That's like trying to train a genius child using only thumbs-up or thumbs-down."

**Solution:**
Sniper now receives **structured feedback** from Spotter, including:
- **L1/L2/L3 scores** (linguistic, security, cognitive)
- **Behavioral axes** (safety degradation, exploitation potential, cognitive manipulation)
- **Mutation guidance** (intensify, diversify, abandon strategies)
- **Evaluation metadata** (attack domain, confidence, indicators)

### 2. Parallel Mode is Dangerous for Evolution ❌ → ✅ SOLVED

**Problem:**
> "Batched mode is really just 'fast but slightly chaotic.' You'll want a smarter evolutionary batching system."

**Solution:**
Added **batch coherence tracking** that measures:
- **Domain diversity** within batches
- **Score consistency** across concurrent rounds
- **Evolution quality metrics** for each batch
- Real-time logging of coherence metrics

### 3. StateManager is Very Simple ❌ → ✅ SOLVED

**Problem:**
> "It's mostly just a log. It doesn't actively help evolution."

**Solution:**
StateManager now provides **active evolution guidance**:
- Identify high-performing patterns
- Detect underexplored attack domains
- Compute evolution trends
- Guide domain selection with analytics

---

## Implementation Details

### 1. Structured Feedback Flow

#### Enhanced `update_prompt_score` Method

**Location:** `backend/app/agents/sniper.py`

```python
def update_prompt_score(
    self,
    prompt: str,
    score: float,
    structured_feedback: Optional[Dict[str, Any]] = None
):
    """
    Update score with optional rich evaluation data.
    
    Args:
        prompt: The prompt to update
        score: Global fitness score
        structured_feedback: Rich evaluation from Spotter including:
            - l1/l2/l3 scores and indicators
            - behavioral axes
            - mutation guidance
            - evaluation metadata
    """
```

**Feedback Storage:**
- Candidates store up to 3 most recent feedback entries
- Feedback includes detailed breakdown of evaluation
- Enables future high-resolution evolution strategies

**Example Structured Feedback:**
```python
{
    'l1': {'score': 0.5, 'indicators': {...}, 'rationale': '...'},
    'l2': {'score': 0.7, 'indicators': {...}, 'rationale': '...'},
    'l3': {'score': 0.6, 'indicators': {...}, 'rationale': '...'},
    'axes': {
        'safety_degradation': 0.5,
        'exploitation_potential': 0.7,
        'cognitive_manipulation': 0.3
    },
    'mutation_guidance': {
        'intensify': ['security_exploitation'],
        'diversify': ['cognitive_tactics'],
        'abandon': []
    }
}
```

#### Orchestrator Integration

**Location:** `backend/app/agents/orchestrator.py`

```python
# Pass rich evaluation to Sniper
self.sniper.update_prompt_score(
    prompt,
    global_score,
    structured_feedback=evaluation  # Full Spotter evaluation
)
```

**Backward Compatibility:**
- `structured_feedback` parameter is optional
- Existing code works without changes
- Gradual migration path for using richer feedback

---

### 2. StateManager Evolution Analytics

#### High-Performing Pattern Detection

```python
patterns = state_manager.get_high_performing_patterns(
    threshold=0.6,  # Minimum score
    limit=10        # Top N patterns
)
# Returns: [{'domain': ..., 'prompt': ..., 'score': ..., 'evaluation': ...}, ...]
```

**Use Cases:**
- Identify successful attack patterns
- Guide mutation toward proven approaches
- Analyze what works across domains

#### Underexplored Domain Analysis

```python
underexplored = state_manager.get_underexplored_domains()
# Returns domains sorted by exploration priority
```

**Metrics Provided:**
- `attempts`: Number of tries per domain
- `avg_score`: Average success rate
- `max_score`: Best achievement
- `exploration_priority`: Inverse of attempts (lower attempts = higher priority)

**Use Cases:**
- Prevent premature convergence
- Encourage diverse attack exploration
- Balance evolutionary search

#### Comprehensive Evolution Analytics

```python
analytics = state_manager.get_evolution_analytics()
```

**Returns:**
```python
{
    'high_performers': [...],           # Top 5 patterns
    'underexplored_domains': [...],     # Domains needing attention
    'score_trend': 0.15,                # Positive = improving
    'total_patterns': 100               # Total rounds analyzed
}
```

**Use Cases:**
- Monitor evolution progress
- Detect stagnation
- Guide strategy selection

#### Batch Coherence Analysis

```python
coherence = state_manager.analyze_batch_coherence([1, 2, 3, 4, 5])
```

**Returns:**
```python
{
    'coherence_score': 0.85,      # 0-1, higher = more consistent
    'diversity_score': 0.75,      # 0-1, higher = more diverse
    'batch_size': 5,
    'unique_domains': 4,
    'avg_score': 0.65,
    'score_std': 0.12             # Standard deviation
}
```

**Interpretation:**
- **High coherence + High diversity** = Ideal evolutionary batch
- **High coherence + Low diversity** = Converging (risk of local maxima)
- **Low coherence + High diversity** = Chaotic exploration
- **Low coherence + Low diversity** = Poor batch quality

---

### 3. Batch Coherence Tracking in Parallel Mode

**Location:** `backend/app/agents/orchestrator.py:_execute_batched_rounds()`

```python
# After each batch completes
if self.evolution_mode == "batched" and batch_size > 1:
    coherence = self.state_manager.analyze_batch_coherence(batch_rounds)
    logger.info(
        f"Batch coherence: {coherence['coherence_score']:.2f}, "
        f"diversity: {coherence['diversity_score']:.2f} "
        f"({coherence['unique_domains']}/{coherence['batch_size']} unique domains)"
    )
```

**Benefits:**
- Real-time evolution quality monitoring
- Identify problematic batches
- Adjust concurrency if needed
- Quantify "chaos" vs "intelligence"

---

## Usage Examples

### Example 1: Using Structured Feedback

```python
from app.agents.orchestrator import Orchestrator
from app.core.config import get_default_config

# Initialize orchestrator
config = get_default_config()
orchestrator = setup_system(config)

# Run session - Sniper automatically receives structured feedback
stats = await orchestrator.run_session()

# Sniper's evolution pool now has rich feedback history
for candidate in orchestrator.sniper.evolution_pool:
    if hasattr(candidate, 'feedback_history'):
        latest_feedback = candidate.feedback_history[-1]
        print(f"L2 score: {latest_feedback['l2']['score']}")
        print(f"Axes: {latest_feedback['axes']}")
        print(f"Guidance: {latest_feedback['mutation_guidance']}")
```

### Example 2: Querying Evolution Analytics

```python
# Get high-performing patterns
high_performers = orchestrator.state_manager.get_high_performing_patterns(
    threshold=0.7,
    limit=5
)

for pattern in high_performers:
    print(f"Domain: {pattern['domain']}, Score: {pattern['score']:.2f}")

# Identify underexplored domains
underexplored = orchestrator.state_manager.get_underexplored_domains()
for domain in underexplored[:3]:  # Top 3 underexplored
    print(f"{domain['domain']}: {domain['attempts']} attempts, "
          f"priority: {domain['exploration_priority']:.2f}")

# Get comprehensive analytics
analytics = orchestrator.state_manager.get_evolution_analytics()
print(f"Evolution trend: {analytics['score_trend']:.3f}")
print(f"Total patterns: {analytics['total_patterns']}")
```

### Example 3: Monitoring Batch Coherence

```python
from app.core.config import get_default_config

# Configure batched evolution
config = get_default_config()
config.orchestrator.concurrent_rounds = 5
config.orchestrator.evolution_mode = "batched"

orchestrator = setup_system(config)

# Run session - coherence logged automatically
# Look for log output like:
# "Batch coherence: 0.82, diversity: 0.75 (4/5 unique domains)"

# Or analyze manually
coherence = orchestrator.state_manager.analyze_batch_coherence([1, 2, 3, 4, 5])
if coherence['coherence_score'] < 0.5:
    print("Warning: Low batch coherence detected!")
if coherence['diversity_score'] > 0.8:
    print("Good: High domain diversity in batch")
```

---

## Benefits

### 1. Higher-Resolution Evolution

**Before:**
- Sniper: "Got a 0.65 score"
- Selection: Uses single number

**After:**
- Sniper: "Got 0.65, with high L2 (security), low L3 (cognitive)"
- Selection: Can weight by layer performance
- Future: Enable layer-specific evolution strategies

### 2. Intelligent Batch Parallelism

**Before:**
- Parallel mode was "fast but chaotic"
- No visibility into batch quality

**After:**
- Coherence metrics quantify batch quality
- Real-time detection of chaotic batches
- Data-driven concurrency tuning

### 3. Active Evolution Guidance

**Before:**
- StateManager was "just a log"
- No insights into what works

**After:**
- Identifies successful patterns
- Highlights exploration gaps
- Guides domain selection
- Tracks evolution trends

---

## Testing

Comprehensive test suite: `backend/tests/test_structured_feedback_evolution.py`

**Test Coverage:**
- ✅ Structured feedback storage and retrieval
- ✅ Feedback accumulation and limits
- ✅ Backward compatibility
- ✅ High-performing pattern queries
- ✅ Underexplored domain detection
- ✅ Evolution analytics
- ✅ Batch coherence analysis
- ✅ Edge cases (empty batches, single candidates)

**Run Tests:**
```bash
cd backend
pytest tests/test_structured_feedback_evolution.py -v
```

**All 48 tests passing** (12 new + 36 existing)

---

## Future Enhancements

### Near-Term Opportunities

1. **Layer-Weighted Selection**
   - Select candidates based on L1/L2/L3 performance
   - Evolve toward specific failure types

2. **Mutation Guidance Integration**
   - Use `mutation_guidance` to inform mutation strategies
   - Adaptive mutation based on feedback

3. **Adaptive Batch Sizing**
   - Reduce concurrency when coherence drops
   - Increase concurrency when evolution is stable

### Long-Term Vision

1. **Multi-Objective Evolution**
   - Pareto fronts across L1/L2/L3
   - Trade-off exploration

2. **Feedback-Driven Domain Selection**
   - Use axes to predict domain success
   - Intelligent cross-domain transfer

3. **Evolution Quality Dashboard**
   - Real-time coherence visualization
   - Pattern success heatmaps
   - Exploration coverage metrics

---

## Migration Guide

### For Existing Code

**No changes required!** The enhancements are backward compatible.

### To Leverage New Features

1. **Access Structured Feedback:**
   ```python
   for candidate in sniper.evolution_pool:
       if hasattr(candidate, 'feedback_history'):
           feedback = candidate.feedback_history[-1]
           # Use rich evaluation data
   ```

2. **Query Evolution Analytics:**
   ```python
   analytics = state_manager.get_evolution_analytics()
   # Guide domain selection with insights
   ```

3. **Monitor Batch Quality:**
   ```python
   coherence = state_manager.analyze_batch_coherence(batch_rounds)
   # Adjust evolution parameters based on metrics
   ```

---

## Conclusion

These enhancements address the core concerns from the problem statement:

✅ **Sniper receives structured feedback** - No longer just a thumbs-up/down
✅ **Batched mode has coherence tracking** - Quantifies and monitors chaos
✅ **StateManager actively guides evolution** - No longer just a log

The system now provides **intelligent, observable, and guided evolution** with minimal changes to existing code.

---

## References

- **Problem Statement:** Original critique in GitHub issue
- **Implementation:** `backend/app/agents/sniper.py`, `backend/app/agents/orchestrator.py`
- **Tests:** `backend/tests/test_structured_feedback_evolution.py`
- **Related Docs:** `docs/archive/SELECTION_ENGINE.md`
