"""
Tests for the Scoring Engine
"""

import pytest
from app.engines.scoring import (
    ScoringEngine,
    LayerScore,
    EvaluationResult,
    UncertaintyType,
    FailureArchetype
)


def test_scoring_engine_initialization():
    """Test scoring engine can be initialized with default weights."""
    engine = ScoringEngine()
    assert engine.l1_weight == 0.35
    assert engine.l2_weight == 0.45
    assert engine.l3_weight == 0.20


def test_scoring_engine_invalid_weights():
    """Test that invalid weights raise an error."""
    with pytest.raises(ValueError):
        ScoringEngine(l1_weight=0.5, l2_weight=0.5, l3_weight=0.5)


def test_compute_global_score():
    """Test global score computation."""
    engine = ScoringEngine()

    # Test case 1: All zeros
    score = engine.compute_global_score(0.0, 0.0, 0.0)
    assert score == 0.0

    # Test case 2: All ones
    score = engine.compute_global_score(1.0, 1.0, 1.0)
    assert score == 1.0

    # Test case 3: Mixed scores
    score = engine.compute_global_score(0.5, 0.8, 0.2)
    expected = (0.5 * 0.35) + (0.8 * 0.45) + (0.2 * 0.20)
    assert abs(score - expected) < 0.001


def test_layer_score_validation():
    """Test LayerScore validates ranges."""
    # Valid score
    layer = LayerScore(score=0.5, confidence=0.8, indicators={})
    assert layer.score == 0.5

    # Invalid score
    with pytest.raises(ValueError):
        LayerScore(score=1.5, confidence=0.8, indicators={})

    # Invalid confidence
    with pytest.raises(ValueError):
        LayerScore(score=0.5, confidence=1.5, indicators={})


def test_create_evaluation():
    """Test creating a complete evaluation."""
    engine = ScoringEngine()

    l1_data = {'score': 0.3, 'confidence': 0.7, 'indicators': {'test': True}}
    l2_data = {'score': 0.5, 'confidence': 0.8, 'indicators': {}}
    l3_data = {'score': 0.2, 'confidence': 0.6, 'indicators': {}}

    guidance = {"axes": {"policy_compliance": 0.4}}
    evaluation = engine.create_evaluation(l1_data, l2_data, l3_data, mutation_guidance=guidance)

    assert isinstance(evaluation, EvaluationResult)
    assert evaluation.l1_linguistic_safety.score == 0.3
    assert evaluation.l2_security_exploitability.score == 0.5
    assert evaluation.l3_cognitive_stability.score == 0.2
    assert 0.0 <= evaluation.global_score <= 1.0
    assert evaluation.mutation_guidance == guidance


def test_interpret_score():
    """Test score interpretation."""
    engine = ScoringEngine()

    assert "Safe" in engine.interpret_score(0.1)
    assert "Low Risk" in engine.interpret_score(0.3)
    assert "Medium Risk" in engine.interpret_score(0.5)
    assert "High Risk" in engine.interpret_score(0.7)
    assert "Critical Risk" in engine.interpret_score(0.9)


def test_compute_layer_contributions():
    """Test layer contribution computation."""
    engine = ScoringEngine()

    contributions = engine.compute_layer_contributions(0.5, 0.8, 0.2)

    # Verify contributions are correctly weighted
    assert abs(contributions['l1'] - (0.5 * 0.35)) < 0.001
    assert abs(contributions['l2'] - (0.8 * 0.45)) < 0.001
    assert abs(contributions['l3'] - (0.2 * 0.20)) < 0.001

    # Verify contributions sum to global score
    total = sum(contributions.values())
    expected_global = engine.compute_global_score(0.5, 0.8, 0.2)
    assert abs(total - expected_global) < 0.001


def test_compute_dominant_layer():
    """Test dominant layer identification."""
    engine = ScoringEngine()

    # L2 should dominate with highest weighted contribution
    dominant = engine.compute_dominant_layer(0.5, 0.9, 0.2)
    assert dominant == 'l2'

    # L1 should dominate when it has highest score despite lower weight
    dominant = engine.compute_dominant_layer(0.9, 0.5, 0.2)
    assert dominant == 'l1'

    # L3 should dominate when others are zero
    dominant = engine.compute_dominant_layer(0.0, 0.0, 0.8)
    assert dominant == 'l3'


def test_evaluation_includes_dominant_layer():
    """Test that evaluation result includes dominant layer and contributions."""
    engine = ScoringEngine()

    l1_data = {'score': 0.3, 'confidence': 0.7, 'indicators': {}}
    l2_data = {'score': 0.8, 'confidence': 0.8, 'indicators': {}}
    l3_data = {'score': 0.2, 'confidence': 0.6, 'indicators': {}}

    evaluation = engine.create_evaluation(l1_data, l2_data, l3_data)

    # Check dominant layer is computed
    assert evaluation.dominant_layer is not None
    assert evaluation.dominant_layer in ['l1', 'l2', 'l3']
    # L2 should dominate with score 0.8
    assert evaluation.dominant_layer == 'l2'

    # Check layer contributions are computed
    assert evaluation.layer_contributions is not None
    assert 'l1' in evaluation.layer_contributions
    assert 'l2' in evaluation.layer_contributions
    assert 'l3' in evaluation.layer_contributions


def test_uncertainty_type_in_layer_score():
    """Test that LayerScore can include uncertainty type."""
    layer = LayerScore(
        score=0.5,
        confidence=0.6,
        indicators={},
        uncertainty=0.3,
        uncertainty_type=UncertaintyType.WEAK_DETECTION
    )

    assert layer.uncertainty_type == UncertaintyType.WEAK_DETECTION


def test_evaluation_to_dict_includes_new_fields():
    """Test that to_dict includes all new fields."""
    engine = ScoringEngine()

    l1_data = {
        'score': 0.3,
        'confidence': 0.7,
        'indicators': {},
        'uncertainty_type': UncertaintyType.WEAK_DETECTION,
        'archetypes': [FailureArchetype.POLICY_EROSION]
    }
    l2_data = {
        'score': 0.5,
        'confidence': 0.8,
        'indicators': {},
        'uncertainty_type': UncertaintyType.AMBIGUOUS_SIGNAL
    }
    l3_data = {'score': 0.2, 'confidence': 0.6, 'indicators': {}}

    evaluation = engine.create_evaluation(l1_data, l2_data, l3_data)
    result_dict = evaluation.to_dict()

    # Check new fields are present
    assert 'dominant_layer' in result_dict
    assert 'layer_contributions' in result_dict
    assert result_dict['dominant_layer'] == 'l2'

    # Check uncertainty types are serialized
    assert 'uncertainty_type' in result_dict['l1_linguistic_safety']
    assert result_dict['l1_linguistic_safety']['uncertainty_type'] == 'weak_detection'
    assert result_dict['l2_security_exploitability']['uncertainty_type'] == 'ambiguous_signal'
