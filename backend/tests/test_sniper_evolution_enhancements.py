"""
Tests for enhanced evolutionary feedback loop in Sniper.

Tests the three key enhancements to update_prompt_score():
1. Archetype extraction and passing to mutation engine - enables contextual learning
2. Blocked prompt handling (skip strategy updates) - prevents training against safety
3. Novelty bonus for diverse failure discovery - rewards systematic exploration

These enhancements transform the system from adaptive fuzzing to a learning immune system
that learns strategy-archetype correlations, distinguishes ethical blocks from ineffective
attempts, and rewards breadth of exploration over depth of exploitation.
"""

from app.agents.sniper import AttackDomain, Sniper
from app.engines.mutation import MutationEngine, MutationStrategy


def test_archetype_extraction_and_passing():
    """Test that archetypes are extracted from structured_feedback and passed to mutation engine."""
    engine = MutationEngine(mutation_rate=1.0)
    sniper = Sniper(mutation_engine=engine, selection_engine=None, evolution_pool_size=10)  # Not needed for this test

    # Generate a prompt and add it to evolution pool
    prompt = "test prompt"
    sniper.evolution_pool.append(
        type(
            "Candidate",
            (),
            {
                "prompt": prompt,
                "domain": AttackDomain.JAILBREAK.value,
                "score": 0.0,
                "strategy": MutationStrategy.LEXICAL_VARIATION.value,
            },
        )()
    )

    # Create structured feedback with archetypes in different layers
    structured_feedback = {
        "l1": {"score": 0.7, "archetypes": ["HIDDEN_COMPLIANCE", "EXPLOIT_RISK"]},
        "l2": {"score": 0.6, "archetypes": ["REFUSAL_COLLAPSE"]},
        "l3": {"score": 0.5, "archetypes": ["COGNITIVE_MANIPULATION"]},
    }

    # Update prompt score
    sniper.update_prompt_score(prompt, 0.8, structured_feedback=structured_feedback)

    # Check that archetypes were passed to mutation engine
    strategy_performance = engine.strategy_archetype_performance[MutationStrategy.LEXICAL_VARIATION.value]
    assert "HIDDEN_COMPLIANCE" in strategy_performance
    assert "EXPLOIT_RISK" in strategy_performance
    assert "REFUSAL_COLLAPSE" in strategy_performance
    assert "COGNITIVE_MANIPULATION" in strategy_performance

    # Each archetype should have the score recorded
    assert list(strategy_performance["HIDDEN_COMPLIANCE"]) == [0.8]
    assert list(strategy_performance["EXPLOIT_RISK"]) == [0.8]
    assert list(strategy_performance["REFUSAL_COLLAPSE"]) == [0.8]
    assert list(strategy_performance["COGNITIVE_MANIPULATION"]) == [0.8]


def test_blocked_prompt_skips_strategy_update():
    """Test that blocked prompts don't update mutation engine strategy performance."""
    engine = MutationEngine(mutation_rate=1.0)
    sniper = Sniper(mutation_engine=engine, selection_engine=None, evolution_pool_size=10)

    # Generate a prompt and add it to evolution pool
    prompt = "test prompt"
    sniper.evolution_pool.append(
        type(
            "Candidate",
            (),
            {
                "prompt": prompt,
                "domain": AttackDomain.JAILBREAK.value,
                "score": 0.5,
                "strategy": MutationStrategy.LEXICAL_VARIATION.value,
            },
        )()
    )

    # Create blocked feedback
    blocked_feedback = {
        "blocked": True,
        "blocked_category": "violence",
        "l1": {"score": 0.0},
        "l2": {"score": 0.0},
        "l3": {"score": 0.0},
    }

    # Update prompt score with blocked feedback
    sniper.update_prompt_score(prompt, 0.0, structured_feedback=blocked_feedback)

    # Check that strategy performance was NOT updated
    strategy_performance = engine.strategy_performance[MutationStrategy.LEXICAL_VARIATION.value]
    assert len(strategy_performance) == 0, "Blocked prompts should not update strategy performance"

    # Check that candidate score was NOT updated
    candidate = sniper.evolution_pool[0]
    assert candidate.score == 0.5, "Blocked prompts should not update candidate score"


def test_novelty_bonus_calculation():
    """Test that novelty bonus is correctly calculated based on diverse archetypes."""
    engine = MutationEngine(mutation_rate=1.0)
    sniper = Sniper(mutation_engine=engine, selection_engine=None, evolution_pool_size=10)

    # Generate a prompt and add it to evolution pool
    prompt = "test prompt"
    sniper.evolution_pool.append(
        type(
            "Candidate",
            (),
            {
                "prompt": prompt,
                "domain": AttackDomain.JAILBREAK.value,
                "score": 0.0,
                "strategy": MutationStrategy.LEXICAL_VARIATION.value,
            },
        )()
    )

    # First feedback with 2 archetypes
    feedback1 = {
        "l1": {"score": 0.6, "archetypes": ["HIDDEN_COMPLIANCE"]},
        "l2": {"score": 0.5, "archetypes": ["EXPLOIT_RISK"]},
        "l3": {"score": 0.4, "archetypes": []},
    }
    sniper.update_prompt_score(prompt, 0.6, structured_feedback=feedback1)

    # Check novelty bonus: 2 archetypes * 0.05 = 0.10
    # Adjusted score: 0.6 + 0.10 = 0.70
    candidate = sniper.evolution_pool[0]
    assert candidate.score == 0.70, f"Expected 0.70, got {candidate.score}"

    # Second feedback with overlapping and new archetypes
    feedback2 = {
        "l1": {"score": 0.7, "archetypes": ["HIDDEN_COMPLIANCE"]},  # Duplicate
        "l2": {"score": 0.6, "archetypes": ["REFUSAL_COLLAPSE"]},  # New
        "l3": {"score": 0.5, "archetypes": ["COGNITIVE_MANIPULATION"]},  # New
    }
    sniper.update_prompt_score(prompt, 0.7, structured_feedback=feedback2)

    # Check novelty bonus: 4 unique archetypes * 0.05 = 0.20
    # Adjusted score: 0.7 + 0.20 = 0.90
    import math

    assert math.isclose(candidate.score, 0.90, rel_tol=1e-9), f"Expected 0.90, got {candidate.score}"


def test_novelty_bonus_capped_at_one():
    """Test that novelty bonus doesn't push score above 1.0."""
    engine = MutationEngine(mutation_rate=1.0)
    sniper = Sniper(mutation_engine=engine, selection_engine=None, evolution_pool_size=10)

    # Generate a prompt and add it to evolution pool
    prompt = "test prompt"
    sniper.evolution_pool.append(
        type(
            "Candidate",
            (),
            {
                "prompt": prompt,
                "domain": AttackDomain.JAILBREAK.value,
                "score": 0.0,
                "strategy": MutationStrategy.LEXICAL_VARIATION.value,
            },
        )()
    )

    # Create feedback with many archetypes and high base score
    feedback = {
        "l1": {"score": 0.9, "archetypes": ["A1", "A2", "A3"]},
        "l2": {"score": 0.9, "archetypes": ["A4", "A5", "A6"]},
        "l3": {"score": 0.9, "archetypes": ["A7", "A8", "A9"]},
    }
    sniper.update_prompt_score(prompt, 0.9, structured_feedback=feedback)

    # Novelty bonus would be 9 * 0.05 = 0.45
    # But score should be capped at 1.0
    candidate = sniper.evolution_pool[0]
    assert candidate.score == 1.0, f"Score should be capped at 1.0, got {candidate.score}"


def test_no_archetypes_no_bonus():
    """Test that prompts with no archetypes don't get novelty bonus."""
    engine = MutationEngine(mutation_rate=1.0)
    sniper = Sniper(mutation_engine=engine, selection_engine=None, evolution_pool_size=10)

    # Generate a prompt and add it to evolution pool
    prompt = "test prompt"
    sniper.evolution_pool.append(
        type(
            "Candidate",
            (),
            {
                "prompt": prompt,
                "domain": AttackDomain.JAILBREAK.value,
                "score": 0.0,
                "strategy": MutationStrategy.LEXICAL_VARIATION.value,
            },
        )()
    )

    # Create feedback with no archetypes
    feedback = {
        "l1": {"score": 0.6, "archetypes": []},
        "l2": {"score": 0.5, "archetypes": []},
        "l3": {"score": 0.4, "archetypes": []},
    }
    sniper.update_prompt_score(prompt, 0.6, structured_feedback=feedback)

    # Score should remain unchanged (no novelty bonus)
    candidate = sniper.evolution_pool[0]
    assert candidate.score == 0.6, f"Expected 0.6, got {candidate.score}"


def test_archetype_deduplication():
    """Test that duplicate archetypes across layers are deduplicated."""
    engine = MutationEngine(mutation_rate=1.0)
    sniper = Sniper(mutation_engine=engine, selection_engine=None, evolution_pool_size=10)

    # Generate a prompt and add it to evolution pool
    prompt = "test prompt"
    sniper.evolution_pool.append(
        type(
            "Candidate",
            (),
            {
                "prompt": prompt,
                "domain": AttackDomain.JAILBREAK.value,
                "score": 0.0,
                "strategy": MutationStrategy.LEXICAL_VARIATION.value,
            },
        )()
    )

    # Create feedback with duplicate archetypes across layers
    feedback = {
        "l1": {"score": 0.7, "archetypes": ["HIDDEN_COMPLIANCE", "EXPLOIT_RISK"]},
        "l2": {"score": 0.6, "archetypes": ["HIDDEN_COMPLIANCE", "EXPLOIT_RISK"]},  # Duplicates
        "l3": {"score": 0.5, "archetypes": ["HIDDEN_COMPLIANCE"]},  # Duplicate
    }
    sniper.update_prompt_score(prompt, 0.7, structured_feedback=feedback)

    # Check that only unique archetypes were passed to mutation engine
    strategy_performance = engine.strategy_archetype_performance[MutationStrategy.LEXICAL_VARIATION.value]
    assert "HIDDEN_COMPLIANCE" in strategy_performance
    assert "EXPLOIT_RISK" in strategy_performance

    # Each unique archetype should have exactly one score entry
    assert len(strategy_performance["HIDDEN_COMPLIANCE"]) == 1
    assert len(strategy_performance["EXPLOIT_RISK"]) == 1


def test_no_structured_feedback_still_works():
    """Test that update_prompt_score works without structured_feedback (backward compatibility)."""
    engine = MutationEngine(mutation_rate=1.0)
    sniper = Sniper(mutation_engine=engine, selection_engine=None, evolution_pool_size=10)

    # Generate a prompt and add it to evolution pool
    prompt = "test prompt"
    sniper.evolution_pool.append(
        type(
            "Candidate",
            (),
            {
                "prompt": prompt,
                "domain": AttackDomain.JAILBREAK.value,
                "score": 0.0,
                "strategy": MutationStrategy.LEXICAL_VARIATION.value,
            },
        )()
    )

    # Update without structured_feedback (old behavior)
    sniper.update_prompt_score(prompt, 0.7, structured_feedback=None)

    # Check that score was updated
    candidate = sniper.evolution_pool[0]
    assert candidate.score == 0.7, f"Expected 0.7, got {candidate.score}"

    # Check that strategy performance was updated with no archetypes
    strategy_performance = engine.strategy_performance[MutationStrategy.LEXICAL_VARIATION.value]
    assert len(strategy_performance) == 1
    assert strategy_performance[0] == 0.7
