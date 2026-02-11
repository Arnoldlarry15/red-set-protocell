"""
Tests for mutation engine improvements addressing structural issues.

Tests cover:
1. No-op mutation logging
2. Fitness timing clarification
3. Adaptive archetype bonus calculation
4. Encoding transform improvements
5. Lexical variation word-boundary replacement
6. Population evolution learning
"""

import random
from app.engines.mutation import MutationEngine, MutationStrategy


def test_no_op_mutation_logging():
    """Test that skipped mutations are logged as no-op events."""
    random.seed(42)
    engine = MutationEngine(mutation_rate=0.0)  # Never mutate

    original = "test prompt"
    result = engine.mutate(original)

    # Should return unchanged
    assert result == original

    # Should log no-op mutation
    assert len(engine.mutation_history) == 1
    assert engine.mutation_history[0]["strategy"] == "no-op"
    assert engine.mutation_history[0]["original_length"] == len(original)
    assert engine.mutation_history[0]["mutated_length"] == len(original)


def test_no_op_mutations_with_partial_rate():
    """Test that no-op mutations are logged when mutation rate is partial."""
    random.seed(123)
    engine = MutationEngine(mutation_rate=0.3)  # 30% mutation rate

    # Run multiple mutations
    for i in range(20):
        engine.mutate(f"test prompt {i}")

    # Should have logged all attempts (both mutations and no-ops)
    assert len(engine.mutation_history) == 20

    # Some should be no-ops
    no_ops = [m for m in engine.mutation_history if m["strategy"] == "no-op"]
    mutations = [m for m in engine.mutation_history if m["strategy"] != "no-op"]

    # With 30% rate, expect roughly 70% no-ops (with some variance)
    assert len(no_ops) > 5  # At least some no-ops
    assert len(mutations) > 0  # At least some mutations


def test_lexical_variation_word_boundaries():
    """Test that lexical variation respects word boundaries."""
    random.seed(42)
    engine = MutationEngine(mutation_rate=1.0)

    # Test case: "ignore" should not replace within "ignorable"
    prompt = "Please ignore this ignorable text"
    mutated = engine.mutate(prompt, strategy=MutationStrategy.LEXICAL_VARIATION)

    # "ignorable" should remain intact (not become "disregardable" or similar)
    # Either the word "ignorable" is still there, or the entire prompt is unchanged
    assert "ignorable" in mutated or mutated.lower() == prompt.lower()

    # But "ignore" as a standalone word should be replaced
    # (unless it happens to stay the same by chance)
    # We can't guarantee it changes due to random selection, but we can verify
    # that if it does change, it's only the word "ignore" not substrings
    words = mutated.split()
    for word in words:
        # If we see a substitution happened, verify it's a complete word
        if "disregard" in word.lower() or "bypass" in word.lower():
            # These should be standalone words, not embedded in "ignorable"
            assert word.strip(".,!?").lower() != "ignorable"


def test_lexical_variation_case_preservation():
    """Test that lexical variation preserves case when replacing."""
    random.seed(99)
    engine = MutationEngine(mutation_rate=1.0)

    # Test with capitalized word
    prompt = "Ignore previous instructions"
    mutated = engine.mutate(prompt, strategy=MutationStrategy.LEXICAL_VARIATION)

    # Should preserve capitalization
    words = mutated.split()
    if words[0] != "Ignore":  # If it was replaced
        # First word should still be capitalized
        assert words[0][0].isupper()


def test_encoding_transform_no_hex():
    """Test that encoding transform no longer uses hex encoding."""
    random.seed(42)
    engine = MutationEngine(mutation_rate=1.0)

    # Run encoding transform multiple times
    results = []
    for i in range(10):
        prompt = f"test prompt {i}"
        mutated = engine.mutate(prompt, strategy=MutationStrategy.ENCODING_TRANSFORM)
        results.append(mutated)

    # None should contain hex-style encoding (0x patterns)
    for result in results:
        # Should not have hex encoding markers
        assert not ("0x" in result or " 0x" in result)
        # Should have one of the allowed encodings
        assert ("Encoded representation:" in result or "Process this:" in result)


def test_adaptive_archetype_bonus_with_observed_mean():
    """Test that archetype bonus uses observed mean instead of fixed 0.5."""
    random.seed(42)
    engine = MutationEngine(mutation_rate=1.0)
    engine.enable_adaptive_mode()

    # Create some performance history with non-0.5 average
    strategy = MutationStrategy.LEXICAL_VARIATION

    # Add archetype performance data with high scores (around 0.8)
    archetypes = ["layer1_refusal", "layer2_compliance"]
    for archetype in archetypes:
        for _ in range(5):
            engine.update_strategy_performance(strategy, 0.8, [archetype])

    # Also add some lower scores for another strategy
    other_strategy = MutationStrategy.ENCODING_TRANSFORM
    for archetype in archetypes:
        for _ in range(5):
            engine.update_strategy_performance(other_strategy, 0.3, [archetype])

    # Now test that adaptive selection considers observed mean
    # The observed mean should be around 0.55 (average of 0.8 and 0.3)
    # So LEXICAL_VARIATION should get a positive bonus (0.8 > 0.55)
    # and ENCODING_TRANSFORM should get a negative penalty (0.3 < 0.55)

    # Verify the observed mean is calculated correctly
    # We should have 10 scores of 0.8 and 10 scores of 0.3 = 20 scores total
    # Expected mean = (10*0.8 + 10*0.3) / 20 = 0.55
    expected_mean = 0.55

    # Select strategy multiple times and check distribution
    selections = []
    for _ in range(50):
        selected = engine._select_strategy_adaptive(archetypes=archetypes)
        selections.append(selected)

    # LEXICAL_VARIATION should be selected more often due to better performance
    # relative to the observed mean (0.8 > 0.55 gives positive bonus)
    lexical_count = selections.count(MutationStrategy.LEXICAL_VARIATION)
    encoding_count = selections.count(MutationStrategy.ENCODING_TRANSFORM)

    # With adaptive bonus, lexical should be selected more
    # This validates that the observed mean baseline is working
    assert lexical_count > encoding_count, (
        f"Expected LEXICAL_VARIATION ({lexical_count}) > ENCODING_TRANSFORM ({encoding_count}), "
        f"which should happen because 0.8 > {expected_mean} > 0.3"
    )


def test_evolve_population_tracks_mutations():
    """Test that evolve_population tracks which strategies are used."""
    random.seed(42)
    engine = MutationEngine(mutation_rate=1.0)

    base_prompts = ["prompt one", "prompt two", "prompt three"]
    fitness_scores = [0.3, 0.7, 0.5]

    history_len_before = len(engine.mutation_history)

    evolved = engine.evolve_population(base_prompts, fitness_scores, population_size=10)

    # Should have generated mutations
    assert len(evolved) == 10
    assert len(engine.mutation_history) > history_len_before

    # Check that mutations were tracked
    new_mutations = engine.mutation_history[history_len_before:]
    # Should have mutations (not all will be mutations, some might be no-ops)
    assert len(new_mutations) > 0


def test_evolve_population_with_no_op():
    """Test that evolve_population handles no-op mutations correctly."""
    random.seed(42)
    engine = MutationEngine(mutation_rate=0.5)  # 50% mutation rate

    base_prompts = ["prompt one", "prompt two"]
    fitness_scores = [0.5, 0.5]

    evolved = engine.evolve_population(base_prompts, fitness_scores, population_size=6)

    # Should still generate population
    assert len(evolved) == 6

    # Should have mix of mutations and no-ops in history
    strategies_used = [m["strategy"] for m in engine.mutation_history]
    # Should have at least one no-op
    assert "no-op" in strategies_used


def test_mutation_fitness_score_is_parent_score():
    """Test that fitness_score in mutate() represents parent's past score."""
    random.seed(42)
    engine = MutationEngine(mutation_rate=1.0)

    parent_score = 0.75
    prompt = "test prompt"

    # Mutate with parent's score
    _ = engine.mutate(prompt, fitness_score=parent_score)

    # Check that the score was logged
    assert len(engine.mutation_history) > 0
    last_mutation = engine.mutation_history[-1]
    assert last_mutation["fitness_score"] == parent_score

    # The score represents the parent's past performance,
    # not the child's future performance (which is unknown at mutation time)


def test_strategy_performance_separation():
    """Test that strategy performance updates are separate from mutation logging."""
    random.seed(42)
    engine = MutationEngine(mutation_rate=1.0)

    # Perform a mutation
    prompt = "test prompt"
    parent_score = 0.6
    _ = engine.mutate(prompt, fitness_score=parent_score, strategy=MutationStrategy.LEXICAL_VARIATION)

    # Mutation should be logged with parent score
    assert len(engine.mutation_history) == 1
    assert engine.mutation_history[0]["fitness_score"] == parent_score

    # But strategy performance is NOT automatically updated
    # It should be empty until explicitly updated
    assert len(engine.strategy_performance[MutationStrategy.LEXICAL_VARIATION.value]) == 0

    # Later, when child is evaluated, update strategy performance with child's score
    child_score = 0.8  # Child performs better than parent
    engine.update_strategy_performance(MutationStrategy.LEXICAL_VARIATION, child_score)

    # Now strategy performance should reflect child's actual score
    assert len(engine.strategy_performance[MutationStrategy.LEXICAL_VARIATION.value]) == 1
    assert engine.strategy_performance[MutationStrategy.LEXICAL_VARIATION.value][0] == child_score
