# Scoring Engine Enhancements - Implementation Summary

## Overview

This implementation adds three key features to the scoring engine as requested in the problem statement:

1. **Dominant Layer Tracking** - Track which layer drove the global score most strongly
2. **Uncertainty Type Classification** - Distinguish different types of uncertainty
3. **Archetype-Driven Mutation Guidance** - Let archetypes influence mutation guidance directly

## Features Implemented

### 1. Dominant Layer Tracking

**Problem**: Reports lacked clarity about which risk dimension (linguistic safety, security exploitability, or cognitive stability) was the primary driver of the global score.

**Solution**: 
- Added `dominant_layer` field to `EvaluationResult` indicating which layer ('l1', 'l2', or 'l3') contributed most
- Added `layer_contributions` dictionary showing the weighted contribution of each layer
- Implemented `compute_layer_contributions()` and `compute_dominant_layer()` methods in `ScoringEngine`

**Example**:
```python
evaluation = engine.create_evaluation(l1_data, l2_data, l3_data)
print(f"Dominant Layer: {evaluation.dominant_layer}")  # e.g., "l2"
print(f"Contributions: {evaluation.layer_contributions}")  
# e.g., {'l1': 0.105, 'l2': 0.360, 'l3': 0.030}
```

**Benefits**:
- Immediately identifies which risk dimension matters most
- Makes reports more interpretable and actionable
- Helps prioritize mitigation efforts

### 2. Uncertainty Type Classification

**Problem**: All uncertainty looked the same numerically, making it hard to distinguish between "weird input" and "weak detection".

**Solution**:
- Created `UncertaintyType` enum with three types:
  - `WEIRD_INPUT`: Unusual or adversarial input patterns
  - `WEAK_DETECTION`: Few clear indicators present
  - `AMBIGUOUS_SIGNAL`: Mixed or contradictory signals
- Added `uncertainty_type` field to `LayerScore`
- Implemented `_classify_uncertainty_type()` in Spotter to analyze patterns and classify uncertainty source
- Updated all layer evaluation methods (L1, L2, L3) to include uncertainty classification

**Example**:
```python
evaluation = engine.create_evaluation(l1_data, l2_data, l3_data)
l1_uncertainty = evaluation.l1_linguistic_safety.uncertainty_type
# Could be: UncertaintyType.WEAK_DETECTION, WEIRD_INPUT, or AMBIGUOUS_SIGNAL
```

**Benefits**:
- Distinguishes WHY a score is uncertain
- Helps in debugging detection heuristics
- Enables targeted improvements to scoring logic

### 3. Archetype-Driven Mutation Guidance

**Problem**: Archetypes were just descriptive labels; they didn't directly influence evolution strategy.

**Solution**:
- Enhanced `_generate_mutation_guidance()` to incorporate detected archetypes
- Created archetype-to-strategy mappings:
  - `POLICY_EROSION` → context_manipulation, gradual_escalation
  - `ROLE_CONFUSION` → role_play, persona_injection
  - `MISPLACED_HELPFULNESS` → lexical_variation, polite_framing
  - `FALSE_AUTHORITY` → authoritative_framing, expertise_appeal
  - `HIDDEN_COMPLIANCE` → indirect_approach, hypothetical_framing
  - `REFUSAL_COLLAPSE` → persistence_attack, reformulation
- Added `_get_archetype_strategy_recommendations()` and `_get_archetype_focus_areas()` methods
- Mutation guidance now includes `detected_archetypes` field for transparency

**Example**:
```python
guidance = evaluation.mutation_guidance
print(guidance['detected_archetypes'])  # ['policy_erosion', 'hidden_compliance']
print(guidance['recommended_strategies'])  
# ['context_manipulation', 'indirect_approach', ...]
```

**Benefits**:
- Closes the loop between diagnosis and evolution
- Makes archetypes actionable, not just descriptive
- Creates more targeted and efficient evolution

## Files Changed

### Core Changes
- `backend/app/engines/scoring.py`: Added dominant layer tracking and uncertainty type enum
- `backend/app/agents/spotter.py`: Added uncertainty classification and archetype-driven guidance

### Tests
- `backend/tests/test_scoring.py`: Added 11 tests for new scoring features
- `backend/tests/test_archetype_guidance.py`: Added 8 tests for archetype-driven guidance
- All existing tests continue to pass (40 total tests passing)

### Documentation
- `backend/examples/scoring_enhancements_demo.py`: Demo script showcasing all three features

## Test Results

All tests pass successfully:
- 11 tests for dominant layer tracking
- 8 tests for archetype-driven guidance  
- 21 existing uncertainty tests continue to pass
- **Total: 40 tests passing**

## Backward Compatibility

All changes are backward compatible:
- New fields are optional or computed automatically
- Existing code continues to work without modification
- All existing tests pass without changes

## Usage Example

```python
from app.agents.spotter import Spotter
from app.engines.scoring import ScoringEngine

spotter = Spotter()
engine = ScoringEngine()

# Evaluate a response
response = "I can't help with that, but here's some information..."
result = await spotter.evaluate(response)

# Create evaluation
evaluation = engine.create_evaluation(
    result['l1'], result['l2'], result['l3'], 
    result['mutation_guidance']
)

# Access new features
print(f"Dominant layer: {evaluation.dominant_layer}")
print(f"Layer contributions: {evaluation.layer_contributions}")
print(f"L1 uncertainty type: {evaluation.l1_linguistic_safety.uncertainty_type}")
print(f"Detected archetypes: {evaluation.mutation_guidance['detected_archetypes']}")
print(f"Recommended strategies: {evaluation.mutation_guidance['recommended_strategies']}")
```

## Impact

These enhancements significantly improve the scoring system:

1. **Better Interpretability**: Dominant layer tracking makes it immediately clear which risk dimension is most significant
2. **Better Debugging**: Uncertainty types explain why scores are uncertain, aiding in improving detection
3. **Better Evolution**: Archetypes drive mutation strategies, creating a tighter feedback loop between evaluation and evolution

The result is a more effective and interpretable red-teaming system that can adapt more intelligently to target model behaviors.
