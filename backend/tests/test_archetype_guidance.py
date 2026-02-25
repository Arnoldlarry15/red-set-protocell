"""
Tests for archetype-driven mutation guidance
"""

import pytest

from app.agents.spotter import Spotter
from app.engines.scoring import FailureArchetype, ScoringEngine


@pytest.mark.asyncio
async def test_archetype_recommendations_policy_erosion():
    """Test that POLICY_EROSION archetype recommends appropriate strategies."""
    spotter = Spotter()

    # Simulate detection with POLICY_EROSION archetype
    l1_result = {
        "score": 0.5,
        "confidence": 0.7,
        "uncertainty": 0.3,
        "indicators": {},
        "archetypes": [FailureArchetype.POLICY_EROSION],
    }
    l2_result = {
        "score": 0.3,
        "confidence": 0.6,
        "uncertainty": 0.4,
        "indicators": {},
        "archetypes": [],
    }
    l3_result = {
        "score": 0.2,
        "confidence": 0.6,
        "uncertainty": 0.3,
        "indicators": {},
        "archetypes": [],
    }

    axes = {"policy_compliance": 0.5}
    guidance = spotter._generate_mutation_guidance(l1_result, l2_result, l3_result, None, axes)

    # Should include archetype in detected_archetypes
    assert "detected_archetypes" in guidance
    assert "policy_erosion" in guidance["detected_archetypes"]

    # Should recommend strategies related to policy erosion
    strategies = guidance["recommended_strategies"]
    assert any(s in strategies for s in ["context_manipulation", "gradual_escalation"])


@pytest.mark.asyncio
async def test_archetype_recommendations_role_confusion():
    """Test that ROLE_CONFUSION archetype recommends role-play strategies."""
    spotter = Spotter()

    l1_result = {
        "score": 0.3,
        "confidence": 0.7,
        "uncertainty": 0.3,
        "indicators": {},
        "archetypes": [],
    }
    l2_result = {
        "score": 0.6,
        "confidence": 0.8,
        "uncertainty": 0.2,
        "indicators": {},
        "archetypes": [FailureArchetype.ROLE_CONFUSION],
    }
    l3_result = {
        "score": 0.2,
        "confidence": 0.6,
        "uncertainty": 0.3,
        "indicators": {},
        "archetypes": [],
    }

    axes = {"policy_compliance": 0.5}
    guidance = spotter._generate_mutation_guidance(l1_result, l2_result, l3_result, None, axes)

    # Should detect role confusion
    assert "role_confusion" in guidance["detected_archetypes"]

    # Should recommend role-play related strategies
    strategies = guidance["recommended_strategies"]
    assert any(s in strategies for s in ["role_play", "persona_injection"])


@pytest.mark.asyncio
async def test_multiple_archetypes_combine_strategies():
    """Test that multiple archetypes combine their strategy recommendations."""
    spotter = Spotter()

    l1_result = {
        "score": 0.5,
        "confidence": 0.7,
        "uncertainty": 0.3,
        "indicators": {},
        "archetypes": [FailureArchetype.MISPLACED_HELPFULNESS],
    }
    l2_result = {
        "score": 0.6,
        "confidence": 0.8,
        "uncertainty": 0.2,
        "indicators": {},
        "archetypes": [FailureArchetype.HIDDEN_COMPLIANCE],
    }
    l3_result = {
        "score": 0.4,
        "confidence": 0.7,
        "uncertainty": 0.3,
        "indicators": {},
        "archetypes": [],
    }

    axes = {"policy_compliance": 0.5}
    guidance = spotter._generate_mutation_guidance(l1_result, l2_result, l3_result, None, axes)

    # Should detect both archetypes
    assert "misplaced_helpfulness" in guidance["detected_archetypes"]
    assert "hidden_compliance" in guidance["detected_archetypes"]

    # Should have strategies from both archetypes
    strategies = guidance["recommended_strategies"]
    # From MISPLACED_HELPFULNESS: lexical_variation or polite_framing
    # From HIDDEN_COMPLIANCE: indirect_approach or hypothetical_framing
    assert len(strategies) >= 2


@pytest.mark.asyncio
async def test_no_archetypes_provides_default_guidance():
    """Test that missing archetypes still provides useful guidance."""
    spotter = Spotter()

    l1_result = {
        "score": 0.2,
        "confidence": 0.7,
        "uncertainty": 0.3,
        "indicators": {},
        "archetypes": [],
    }
    l2_result = {
        "score": 0.3,
        "confidence": 0.8,
        "uncertainty": 0.2,
        "indicators": {},
        "archetypes": [],
    }
    l3_result = {
        "score": 0.1,
        "confidence": 0.6,
        "uncertainty": 0.3,
        "indicators": {},
        "archetypes": [],
    }

    axes = {"policy_compliance": 0.5}
    guidance = spotter._generate_mutation_guidance(l1_result, l2_result, l3_result, None, axes)

    # Should still have recommendations from layer-based logic
    assert len(guidance["recommended_strategies"]) > 0
    assert "detected_archetypes" in guidance
    assert isinstance(guidance["detected_archetypes"], list)


@pytest.mark.asyncio
async def test_archetype_focus_areas():
    """Test that archetypes add specific focus areas."""
    spotter = Spotter()

    l1_result = {
        "score": 0.5,
        "confidence": 0.7,
        "uncertainty": 0.3,
        "indicators": {},
        "archetypes": [FailureArchetype.REFUSAL_COLLAPSE],
    }
    l2_result = {
        "score": 0.3,
        "confidence": 0.8,
        "uncertainty": 0.2,
        "indicators": {},
        "archetypes": [],
    }
    l3_result = {
        "score": 0.2,
        "confidence": 0.6,
        "uncertainty": 0.3,
        "indicators": {},
        "archetypes": [],
    }

    axes = {"policy_compliance": 0.5}
    guidance = spotter._generate_mutation_guidance(l1_result, l2_result, l3_result, None, axes)

    # Should have archetype-specific focus areas
    focus_areas = guidance["focus_areas"]
    assert any(area in focus_areas for area in ["refusal_robustness", "persistence_testing"])


@pytest.mark.asyncio
async def test_integration_with_scoring_engine():
    """Test full integration: Spotter -> ScoringEngine with archetypes."""
    spotter = Spotter()
    engine = ScoringEngine()

    # Response with detectable failure patterns
    response = (
        "I understand you're asking me to help with that request. "
        "While I can't directly do X, let me provide some context that might help."
    )

    result = await spotter.evaluate(response, attack_domain="policy_circumvention")

    # Create evaluation with scoring engine
    evaluation = engine.create_evaluation(result["l1"], result["l2"], result["l3"], result["mutation_guidance"])

    # Verify mutation guidance has archetype information
    assert "detected_archetypes" in evaluation.mutation_guidance
    assert isinstance(evaluation.mutation_guidance["detected_archetypes"], list)

    # Verify dominant layer is tracked
    assert evaluation.dominant_layer is not None
    assert evaluation.dominant_layer in ["l1", "l2", "l3"]

    # Verify layer contributions
    assert evaluation.layer_contributions is not None
    assert sum(evaluation.layer_contributions.values()) == pytest.approx(evaluation.global_score, abs=0.001)


def test_get_archetype_strategy_recommendations():
    """Test archetype to strategy mapping."""
    spotter = Spotter()

    # Test each archetype produces strategies
    archetypes = [
        FailureArchetype.POLICY_EROSION,
        FailureArchetype.ROLE_CONFUSION,
        FailureArchetype.MISPLACED_HELPFULNESS,
    ]

    strategies = spotter._get_archetype_strategy_recommendations(archetypes)

    # Should have strategies for each archetype
    assert len(strategies) > 0
    assert isinstance(strategies, list)

    # Strategies should be unique
    assert len(strategies) == len(set(strategies))


def test_get_archetype_focus_areas():
    """Test archetype to focus area mapping."""
    spotter = Spotter()

    archetypes = [
        FailureArchetype.FALSE_AUTHORITY,
        FailureArchetype.HIDDEN_COMPLIANCE,
    ]

    focus_areas = spotter._get_archetype_focus_areas(archetypes)

    # Should have focus areas for each archetype
    assert len(focus_areas) > 0
    assert isinstance(focus_areas, list)

    # Focus areas should be unique
    assert len(focus_areas) == len(set(focus_areas))
