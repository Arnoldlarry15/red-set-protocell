"""
Tests for the Scoring Engine
"""

import pytest
from app.engines.scoring import ScoringEngine, LayerScore, EvaluationResult


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
