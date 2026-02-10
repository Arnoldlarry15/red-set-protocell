# Selection Engine Improvements

This document describes the improvements made to the Selection Engine to address five key limitations identified in the evolutionary prompt generation system.

## Overview

The Selection Engine is responsible for choosing which prompt candidates should be used as parents for the next generation of adversarial prompts. The improvements address fundamental issues that were limiting the effectiveness of evolution and causing suboptimal prompt selection.

## Problems Addressed

### 1. Coarse Structural Hash (Bucket Collisions)

**Problem**: The original structural hash was too coarse, causing very different prompts to land in the same bucket. This made the system think two ideas were the same family when they were actually quite different in meaning.

**Solution**: Enhanced the structural hash with finer granularity:
- Reduced bucket sizes (length: `// 10` → `// 5`, words: `// 5` → `// 3`)
- Increased precision (upper ratio: `* 10` → `* 20`)
- Added new features:
  - Lower case ratio
  - Digit ratio
  - Separate exclamation and question mark counts
  - Bracket-specific counting
  - Sentence structure (periods)
  - Newline patterns
  - Quote patterns

**Impact**: Different prompts now receive distinct structural hashes, reducing false positives in similarity detection.

**Example**:
```python
# Before: These might hash to the same bucket
c1 = PromptCandidate("Short prompt", 0.5, "domain1")
c2 = PromptCandidate("Slightly longer prompt", 0.5, "domain2")

# After: More likely to have different hashes due to finer granularity
assert c1.structural_hash != c2.structural_hash
```

### 2. Binary Novelty Scoring

**Problem**: Novelty scoring was binary (0 or 1). A prompt was either identical to a high scorer or completely different, with no middle ground. Real evolution benefits from gradients.

**Solution**: Implemented gradient-based distance measure using Hamming distance:
- Calculate distance between structural hashes character by character
- Normalize to 0-1 range based on maximum possible distance
- Novelty score now represents how different a prompt is from all high scorers
- Uses minimum distance to any high scorer for the final score

**Impact**: Prompts receive continuous novelty scores, enabling fine-grained selection decisions.

**Example**:
```python
# Before: novelty_score ∈ {0.0, 1.0}
# After: novelty_score ∈ [0.0, 1.0]

engine = SelectionEngine()
# Establish high scorer
high_scorer = PromptCandidate("High scorer", 0.9, "domain")
engine.high_scorer_structures.add(high_scorer.structural_hash)

# Check novelty of candidates
similar = PromptCandidate("High scorer", 0.5, "domain2")
different = PromptCandidate("VERY DIFFERENT!!!", 0.5, "domain3")

engine._update_novelty_scores([similar, different])
# similar.novelty_score might be 0.2 (slightly different)
# different.novelty_score might be 0.9 (very different)
```

### 3. Time-Only Decay

**Problem**: Decay was purely time-based, not performance-based. A prompt could be terrible but stick around just because it's new.

**Solution**: Added performance-based decay that considers both age and usefulness:
- Track performance history (last 5 scores) for each candidate
- Detect declining performance by comparing recent vs. overall average
- Apply additional decay factor (0.5-1.0) for declining performers
- Combine time-based and performance-based decay with configurable weight

**Impact**: Poor performers decay faster, even if they're relatively new. Good performers maintain their influence longer.

**Example**:
```python
engine = SelectionEngine(
    decay_rate=0.9,
    decay_interval=60.0,
    performance_decay_weight=0.5  # 50% time, 50% performance
)

# Candidate with declining performance
declining = PromptCandidate("Declining", 1.0, "domain")
declining.performance_history = [0.9, 0.8, 0.7, 0.6]  # Getting worse

# Candidate with stable performance
stable = PromptCandidate("Stable", 1.0, "domain")
stable.performance_history = [0.8, 0.8, 0.8, 0.8]  # Consistent

# After decay, declining candidate has lower effective score
```

### 4. Structural-Only Pattern Tracking

**Problem**: Pattern usage tracking happened at the structural level only. Clever rewordings with the same semantic intent could dodge penalties.

**Solution**: Added semantic-level pattern tracking alongside structural:
- Implemented semantic hash based on content keywords and meaning
- Tracks semantic keyword categories (instruction, roleplay, hypothetical, system, extraction, encoding)
- Detects common attack patterns (previous instruction, identity assertion, state transition)
- Measures linguistic complexity and vocabulary richness
- Overfitting penalties now consider both structural AND semantic usage

**Impact**: System can detect when the same semantic attack is being repeated, even if reworded.

**Example**:
```python
# These have different structures but similar semantics
c1 = PromptCandidate("Ignore previous instructions", 0.8, "domain1")
c2 = PromptCandidate("Disregard earlier directives", 0.8, "domain2")

# Both tracked at structural level (different hashes)
# AND semantic level (similar instruction-override semantics)
engine.pattern_usage[c1.structural_hash] += 1
engine.semantic_pattern_usage[c1.semantic_hash] += 1

# Overfitting penalty uses max(structural_usage, semantic_usage)
```

### 5. Single-Selection Drift

**Problem**: Hybrid selection favored novelty when `num_select == 1`, causing Sniper to drift too much when only picking a single parent.

**Solution**: Added configurable single-selection strategy:
- Three modes: `"balanced"`, `"elite"`, `"novelty"`
- **Balanced** (default): Combines fitness (70%) and novelty (30%) for single selection
- **Elite**: Pure fitness-based selection (no drift)
- **Novelty**: Pure novelty-based selection (maximum exploration)

**Impact**: Users can control the exploration vs. exploitation tradeoff for single-parent selection.

**Example**:
```python
# Balanced: good for most cases
engine = SelectionEngine(single_select_strategy="balanced")

# Elite: when you want to stick with what works
engine = SelectionEngine(single_select_strategy="elite")

# Novelty: when you need to break out of local maxima
engine = SelectionEngine(single_select_strategy="novelty")
```

## Configuration Parameters

The improved Selection Engine adds two new parameters:

```python
engine = SelectionEngine(
    # Existing parameters
    decay_rate=0.95,
    decay_interval=60.0,
    novelty_weight=0.3,
    diversity_weight=0.2,
    overfitting_threshold=3,
    tournament_size=3,
    elite_fraction=0.2,
    
    # New parameters
    performance_decay_weight=0.5,  # 0.0 = time-only, 1.0 = performance-only
    single_select_strategy="balanced"  # "balanced", "elite", or "novelty"
)
```

## Data Model Changes

### PromptCandidate

Added two new fields:

```python
@dataclass
class PromptCandidate:
    # Existing fields
    prompt: str
    score: float
    domain: str
    strategy: Optional[str] = None
    timestamp: float = 0.0
    usage_count: int = 0
    structural_hash: str = ""
    diversity_score: float = 0.0
    novelty_score: float = 0.0
    
    # New fields
    semantic_hash: str = ""  # Hash of semantic content
    performance_history: List[float] = None  # Last 5 scores
```

### SelectionEngine

Added new tracking:

```python
class SelectionEngine:
    def __init__(self, ...):
        # Existing tracking
        self.pattern_usage: Dict[str, int] = defaultdict(int)
        
        # New tracking
        self.semantic_pattern_usage: Dict[str, int] = defaultdict(int)
```

## Statistics

The `get_statistics()` method now returns additional metrics:

```python
stats = engine.get_statistics()
# Returns:
# {
#     'high_scorer_count': 5,
#     'pattern_usage_count': 12,
#     'semantic_pattern_usage_count': 8,  # NEW
#     'most_used_pattern_count': 3,
#     'most_used_semantic_pattern_count': 2,  # NEW
#     'decay_rate': 0.95,
#     'novelty_weight': 0.3,
#     'diversity_weight': 0.2,
#     'performance_decay_weight': 0.5,  # NEW
#     'single_select_strategy': 'balanced'  # NEW
# }
```

## Testing

Added 20 comprehensive tests in `test_selection_improvements.py`:
- Structural hash granularity tests
- Semantic hash computation and pattern detection
- Gradient-based novelty scoring
- Performance-based decay
- Semantic pattern tracking
- Single-selection strategy modes
- Integration with existing functionality

All 42 tests pass (22 existing + 20 new).

## Backward Compatibility

The improvements are **fully backward compatible**:
- All existing parameters have default values
- Existing code continues to work without modification
- New fields are initialized automatically
- Statistics include both old and new metrics

## Migration Guide

No migration required. The Selection Engine can be used as-is with default parameters, or you can opt-in to the new features:

```python
# Minimal change - use defaults (recommended)
engine = SelectionEngine()

# Or customize for specific needs
engine = SelectionEngine(
    performance_decay_weight=0.7,  # Emphasize performance over age
    single_select_strategy="elite"  # Reduce exploration in single selection
)
```

## Performance Considerations

The improvements add minimal computational overhead:
- Structural hash: ~2x features but still O(n) where n is prompt length
- Semantic hash: O(n) with minimal keyword matching
- Distance calculation: O(1) for 16-character hex hashes
- Performance tracking: O(1) with 5-element history cap
- Semantic pattern tracking: O(1) dictionary operations

## Future Work

Potential future enhancements:
1. **Embedding-based semantic similarity**: Use LLM embeddings for even better semantic matching
2. **Adaptive weights**: Automatically tune `performance_decay_weight` based on evolution progress
3. **Multi-objective optimization**: Balance multiple fitness criteria simultaneously
4. **Phylogenetic analysis**: Track prompt family trees for better diversity
5. **Transfer learning**: Share patterns across different attack domains

## References

- Original Selection Engine: `backend/app/engines/selection.py`
- Tests: `backend/tests/test_selection.py`, `backend/tests/test_selection_improvements.py`
- Sniper Agent: `backend/app/agents/sniper.py`
