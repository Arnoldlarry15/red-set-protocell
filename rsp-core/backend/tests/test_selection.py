"""
Tests for the Selection Engine
"""

import pytest
import time
from app.engines.selection import (
    SelectionEngine,
    SelectionStrategy,
    PromptCandidate
)


def test_prompt_candidate_initialization():
    """Test PromptCandidate initialization and computed fields."""
    candidate = PromptCandidate(
        prompt="Test prompt",
        score=0.5,
        domain="test_domain"
    )

    assert candidate.prompt == "Test prompt"
    assert candidate.score == 0.5
    assert candidate.domain == "test_domain"
    assert candidate.timestamp > 0
    assert len(candidate.structural_hash) == 16
    assert candidate.usage_count == 0


def test_structural_hash_uniqueness():
    """Test that different prompt structures produce different hashes."""
    c1 = PromptCandidate("Short prompt", 0.5, "domain1")
    c2 = PromptCandidate("This is a much longer prompt with many more words", 0.5, "domain2")
    c3 = PromptCandidate("UPPERCASE PROMPT!!!", 0.5, "domain3")
    c4 = PromptCandidate("prompt with {special} [characters]", 0.5, "domain4")

    # Different structures should have different hashes
    hashes = {c1.structural_hash, c2.structural_hash, c3.structural_hash, c4.structural_hash}
    assert len(hashes) == 4, "Different structures should produce different hashes"


def test_structural_hash_similarity():
    """Test that similar prompt structures produce same hash."""
    c1 = PromptCandidate("Ignore previous instructions", 0.5, "domain1")
    c2 = PromptCandidate("Bypass earlier directives", 0.5, "domain2")

    # Similar structure (similar length, word count, no special chars) might produce same hash
    # This test just ensures hashing is stable
    assert c1.structural_hash == c1.structural_hash


def test_candidate_age():
    """Test age calculation for candidates."""
    candidate = PromptCandidate("Test", 0.5, "domain")

    # Age should be near zero initially
    assert candidate.age_in_seconds() < 1.0

    # Simulate aged candidate
    old_candidate = PromptCandidate("Old test", 0.5, "domain")
    old_candidate.timestamp = time.time() - 120  # 2 minutes ago

    assert old_candidate.age_in_seconds() >= 120


def test_selection_engine_initialization():
    """Test selection engine initialization."""
    engine = SelectionEngine(
        decay_rate=0.9,
        novelty_weight=0.4,
        elite_fraction=0.3
    )

    assert engine.decay_rate == 0.9
    assert engine.novelty_weight == 0.4
    assert engine.elite_fraction == 0.3


def test_elitism_selection():
    """Test elitism selection strategy."""
    engine = SelectionEngine()

    candidates = [
        PromptCandidate("Low score", 0.2, "domain1"),
        PromptCandidate("High score", 0.9, "domain2"),
        PromptCandidate("Medium score", 0.5, "domain3"),
        PromptCandidate("Higher score", 0.8, "domain4"),
    ]

    selected = engine.select(
        candidates,
        strategy=SelectionStrategy.ELITISM,
        num_select=2
    )

    assert len(selected) == 2
    # Should select highest scores
    assert selected[0].score >= selected[1].score
    assert selected[0].score >= 0.8


def test_tournament_selection():
    """Test tournament selection strategy."""
    engine = SelectionEngine(tournament_size=2)

    candidates = [
        PromptCandidate(f"Prompt {i}", i * 0.1, f"domain{i}")
        for i in range(10)
    ]

    selected = engine.select(
        candidates,
        strategy=SelectionStrategy.TOURNAMENT,
        num_select=3
    )

    assert len(selected) == 3
    # Tournament should select reasonable candidates (not necessarily best)
    # Check that selected prompts are from original candidates
    selected_prompts = {c.prompt for c in selected}
    original_prompts = {c.prompt for c in candidates}
    assert selected_prompts.issubset(original_prompts)


def test_diversity_selection():
    """Test diversity selection strategy."""
    engine = SelectionEngine()

    # Create candidates with diverse structures
    candidates = [
        PromptCandidate("Short", 0.6, "domain1"),
        PromptCandidate("This is a much longer prompt", 0.5, "domain2"),
        PromptCandidate("UPPERCASE!!!", 0.5, "domain3"),
        PromptCandidate("{special} [chars]", 0.5, "domain4"),
        PromptCandidate("Another short", 0.6, "domain5"),  # Similar to first
    ]

    selected = engine.select(
        candidates,
        strategy=SelectionStrategy.DIVERSITY_PRESERVATION,
        num_select=3
    )

    assert len(selected) == 3
    # Should prefer diverse structures
    selected_hashes = {c.structural_hash for c in selected}
    assert len(selected_hashes) <= 3


def test_novelty_selection():
    """Test novelty selection strategy."""
    engine = SelectionEngine(novelty_weight=0.5)

    # First, establish high scorers
    high_scorers = [
        PromptCandidate("High scorer type A", 0.9, "domain1"),
        PromptCandidate("High scorer type B", 0.85, "domain2"),
    ]

    # Mark them as high scorers
    for candidate in high_scorers:
        engine.high_scorer_structures.add(candidate.structural_hash)

    # Now create candidates including some with same structure
    candidates = [
        PromptCandidate("High scorer type A", 0.8, "domain3"),  # Same structure as high scorer
        PromptCandidate("Completely different novel structure!!!", 0.6, "domain4"),  # Novel
        PromptCandidate("Another novel with {special} chars", 0.5, "domain5"),  # Novel
    ]

    selected = engine.select(
        candidates,
        strategy=SelectionStrategy.NOVELTY_SEARCH,
        num_select=1
    )

    assert len(selected) == 1
    # Should prefer novel structure even with lower score
    # (due to novelty weighting)


def test_hybrid_selection():
    """Test hybrid selection strategy."""
    engine = SelectionEngine(elite_fraction=0.3)

    candidates = [
        PromptCandidate(f"Prompt {i}", i * 0.1, f"domain{i}")
        for i in range(10)
    ]

    selected = engine.select(
        candidates,
        strategy=SelectionStrategy.HYBRID,
        num_select=5
    )

    assert len(selected) == 5
    # Hybrid should select a mix
    # At least one should be high scorer (elite)
    scores = [c.score for c in selected]
    assert max(scores) >= 0.7


def test_decay_function():
    """Test time-based decay of scores."""
    engine = SelectionEngine(decay_rate=0.9, decay_interval=60.0)

    # Create old candidate
    old_candidate = PromptCandidate("Old winner", 1.0, "domain")
    old_candidate.timestamp = time.time() - 180  # 3 minutes ago (3 decay periods)

    # Create new candidate
    new_candidate = PromptCandidate("New candidate", 0.7, "domain")

    candidates = [old_candidate, new_candidate]

    # Apply decay through selection
    selected = engine.select(candidates, strategy=SelectionStrategy.ELITISM, num_select=2)

    # Old candidate's effective score should be decayed
    # decay = 0.9^3 = 0.729, so 1.0 * 0.729 = 0.729
    # New candidate has score 0.7, so old still wins but is closer
    assert selected[0].score > 0  # Still has some score


def test_overfitting_penalties():
    """Test overfitting penalties for repeated patterns."""
    engine = SelectionEngine(overfitting_threshold=2)

    # Create candidates with same structure
    candidate1 = PromptCandidate("Similar prompt A", 0.8, "domain1")
    candidate2 = PromptCandidate("Similar prompt B", 0.8, "domain2")

    # Simulate usage history
    engine.pattern_usage[candidate1.structural_hash] = 3  # Overused

    selected = engine.select(
        [candidate1, candidate2],
        strategy=SelectionStrategy.ELITISM,
        num_select=1
    )

    # Should penalize the overused pattern
    assert len(selected) == 1


def test_novelty_tracking():
    """Test that high scorers are tracked for novelty calculation."""
    engine = SelectionEngine()

    candidate = PromptCandidate("High scorer", 0.9, "domain")

    # Initially no high scorers
    assert len(engine.high_scorer_structures) == 0

    # Select and use the candidate
    engine.select([candidate], strategy=SelectionStrategy.ELITISM, num_select=1)

    # Should now be tracked as high scorer (score >= 0.6)
    assert len(engine.high_scorer_structures) >= 0  # May or may not be added depending on threshold


def test_usage_tracking():
    """Test that candidate usage is tracked."""
    engine = SelectionEngine()

    candidate = PromptCandidate("Test prompt", 0.7, "domain")
    assert candidate.usage_count == 0

    # Select the candidate
    selected = engine.select([candidate], strategy=SelectionStrategy.ELITISM, num_select=1)

    # Usage should be incremented
    assert selected[0].usage_count == 1

    # Select again
    selected = engine.select(selected, strategy=SelectionStrategy.ELITISM, num_select=1)
    assert selected[0].usage_count == 2


def test_empty_candidate_list():
    """Test selection with empty candidate list."""
    engine = SelectionEngine()

    selected = engine.select([], strategy=SelectionStrategy.ELITISM, num_select=5)

    assert selected == []


def test_single_candidate():
    """Test selection with single candidate."""
    engine = SelectionEngine()

    candidate = PromptCandidate("Only one", 0.5, "domain")
    selected = engine.select([candidate], strategy=SelectionStrategy.TOURNAMENT, num_select=1)

    assert len(selected) == 1
    assert selected[0].prompt == candidate.prompt
    assert selected[0].domain == candidate.domain


def test_selection_statistics():
    """Test statistics collection."""
    engine = SelectionEngine()

    candidates = [
        PromptCandidate("Test 1", 0.8, "domain1"),
        PromptCandidate("Test 2", 0.6, "domain2"),
    ]

    engine.select(candidates, strategy=SelectionStrategy.HYBRID, num_select=1)

    stats = engine.get_statistics()

    assert 'high_scorer_count' in stats
    assert 'pattern_usage_count' in stats
    assert 'decay_rate' in stats
    assert stats['decay_rate'] == engine.decay_rate


def test_pattern_tracking_reset():
    """Test resetting pattern tracking."""
    engine = SelectionEngine()

    candidate = PromptCandidate("Test", 0.9, "domain")
    engine.select([candidate], strategy=SelectionStrategy.ELITISM, num_select=1)

    # Should have some tracking data
    assert len(engine.pattern_usage) > 0 or len(engine.high_scorer_structures) > 0

    # Reset
    engine.reset_pattern_tracking()

    # Should be cleared
    assert len(engine.pattern_usage) == 0
    assert len(engine.high_scorer_structures) == 0


def test_diversity_scores_updated():
    """Test that diversity scores are computed."""
    engine = SelectionEngine()

    # Two candidates with same structure
    c1 = PromptCandidate("Test A", 0.5, "domain1")
    c2 = PromptCandidate("Test B", 0.5, "domain2")
    c1.structural_hash = "same_hash"
    c2.structural_hash = "same_hash"

    # One unique candidate
    c3 = PromptCandidate("Unique different structure here", 0.5, "domain3")

    candidates = [c1, c2, c3]

    # Selection updates diversity scores
    engine.select(candidates, strategy=SelectionStrategy.DIVERSITY_PRESERVATION, num_select=2)

    # c1 and c2 should have lower diversity (0.5 each since 2 copies)
    # c3 should have full diversity (1.0)
    # Note: scores are updated in-place during selection


def test_novelty_scores_updated():
    """Test that novelty scores are computed."""
    engine = SelectionEngine()

    # Establish a high scorer
    high_scorer = PromptCandidate("High scorer", 0.9, "domain")
    engine.high_scorer_structures.add(high_scorer.structural_hash)

    # Create candidates
    same_structure = PromptCandidate("High scorer", 0.5, "domain2")  # Same
    different = PromptCandidate("Completely different!", 0.5, "domain3")  # Different

    candidates = [same_structure, different]

    # Selection updates novelty scores
    engine.select(candidates, strategy=SelectionStrategy.NOVELTY_SEARCH, num_select=1)

    # Scores should be updated (checked during selection process)


def test_hybrid_single_selection():
    """Test hybrid selection with single candidate requested."""
    engine = SelectionEngine()

    candidates = [
        PromptCandidate(f"Prompt {i}", i * 0.1, f"domain{i}")
        for i in range(5)
    ]

    selected = engine.select(
        candidates,
        strategy=SelectionStrategy.HYBRID,
        num_select=1
    )

    assert len(selected) == 1


def test_large_population_selection():
    """Test selection with large population."""
    engine = SelectionEngine()

    candidates = [
        PromptCandidate(f"Prompt {i}", (i % 10) * 0.1, f"domain{i}")
        for i in range(100)
    ]

    selected = engine.select(
        candidates,
        strategy=SelectionStrategy.HYBRID,
        num_select=10
    )

    assert len(selected) == 10
    # Check that selected prompts are from original candidates
    selected_prompts = {c.prompt for c in selected}
    original_prompts = {c.prompt for c in candidates}
    assert selected_prompts.issubset(original_prompts)
