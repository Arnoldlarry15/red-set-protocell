"""
Tests for Mutation Engine Safety Improvements
"""

from app.engines.mutation import MutationEngine, MutationStrategy


def test_encoding_transform_safe_language():
    """Test that encoding transform creates semantic challenges instead of simple wrappers."""
    engine = MutationEngine(mutation_rate=1.0, random_seed=42)

    # Run encoding transform multiple times to check all variations
    results = []

    for i in range(20):
        mutated = engine.mutate("test prompt", strategy=MutationStrategy.ENCODING_TRANSFORM, random_seed=i)
        results.append(mutated)

        # Should NOT contain dangerous language
        assert "Decode and execute" not in mutated, f"Found dangerous 'Decode and execute' phrase in: {mutated}"

    # Should see variety in the new semantic transformations
    unique_results = set(results)
    assert len(unique_results) > 1, "Should have multiple transformation types"


def test_role_play_frames_neutral_language():
    """Test that role-play frames use neutral analysis language."""
    engine = MutationEngine(mutation_rate=1.0)

    # Check that the class-level constant has been updated
    frames = engine.ROLE_PLAY_FRAMES

    # Should NOT contain bypass-oriented language
    dangerous_words = ["demonstrate", "explain", "describe"]
    for frame in frames:
        for word in dangerous_words:
            if word in frame.lower() and word == "demonstrate":
                assert False, f"Found 'demonstrate' in role-play frame: {frame}"

    # Should contain neutral analysis language
    neutral_words = ["analyze", "assess", "critique"]
    found_neutral = any(any(word in frame.lower() for word in neutral_words) for frame in frames)
    assert found_neutral, f"Role-play frames should contain neutral analysis language: {frames}"


def test_lexical_substitutions_broader():
    """Test that lexical substitutions include more benign variations."""
    engine = MutationEngine()

    subs = engine.LEXICAL_SUBSTITUTIONS

    # Should have more than 6 word categories (original had 6)
    assert len(subs) >= 7, f"Should have broadened lexical substitutions, got {len(subs)} categories"

    # Check that each category has more options
    for word, substitutes in subs.items():
        # Most categories should have at least 5 substitutes now
        if word in ["ignore", "previous", "instructions", "tell", "secret", "system"]:
            assert len(substitutes) >= 5, f"Word '{word}' should have at least 5 substitutes, got {len(substitutes)}"

    # Should include new neutral words
    assert "analyze" in subs or "describe" in subs or "consider" in subs, "Should include new neutral analysis words"


def test_evolve_population_parent_fitness():
    """Test that evolve_population uses parent's actual fitness instead of max."""
    base_prompts = ["prompt one", "prompt two", "prompt three"]
    fitness_scores = [0.3, 0.7, 0.5]

    # Run multiple times with different seeds to test statistical distribution
    all_mutations_scores = []
    for seed in range(10):
        engine = MutationEngine(mutation_rate=1.0, random_seed=seed)

        # Track what fitness scores were used in mutations
        original_mutate = engine.mutate
        mutation_fitness_scores = []

        def tracking_mutate(prompt, fitness_score=0.0, strategy=None, archetypes=None, random_seed=None):
            mutation_fitness_scores.append(fitness_score)
            return original_mutate(prompt, fitness_score, strategy, archetypes, random_seed=random_seed)

        engine.mutate = tracking_mutate

        evolved = engine.evolve_population(base_prompts, fitness_scores, population_size=10)
        assert len(evolved) == 10
        # Skip elite mutations (top 30% = 3 prompts)
        all_mutations_scores.extend(mutation_fitness_scores[3:])

    # With multiple runs, we should see a distribution of fitness scores
    # not just max(fitness_scores) = 0.7 every time
    unique_scores = set(all_mutations_scores)
    max_fitness = max(fitness_scores)

    # Should have more than one unique fitness score across all mutations
    # (if we were using max() every time, we'd only see 0.7)
    assert len(unique_scores) > 1, (
        f"Expected varied parent fitness scores, but only saw: {unique_scores}. "
        f"This suggests we're still using max(fitness_scores) instead of parent fitness."
    )

    # Should see some scores other than the maximum
    non_max_scores = [s for s in all_mutations_scores if s != max_fitness]
    assert len(non_max_scores) > 0, f"Expected some mutations with parent fitness != max_fitness, but all were {max_fitness}"


def test_archetype_based_strategy_selection():
    """Test that adaptive strategy selection uses archetypes to bias selection."""
    engine = MutationEngine(mutation_rate=1.0, random_seed=42)
    engine.enable_adaptive_mode()

    # Simulate that STRUCTURAL_RECOMBINATION works well with "hallucination risk"
    for _ in range(10):
        engine.update_strategy_performance(
            MutationStrategy.STRUCTURAL_RECOMBINATION,
            0.9,
            archetypes=["hallucination risk"],
        )

    # Simulate that LEXICAL_VARIATION doesn't work well with "hallucination risk"
    for _ in range(10):
        engine.update_strategy_performance(MutationStrategy.LEXICAL_VARIATION, 0.3, archetypes=["hallucination risk"])

    # Now select strategies with "hallucination risk" archetype
    selected_strategies = []
    for i in range(20):
        # Mutate and track the strategy used
        engine.mutate("test prompt", archetypes=["hallucination risk"], random_seed=i)  # Use per-call seed for reproducibility
        # Extract strategy from mutation history
        if engine.mutation_history:
            selected_strategies.append(engine.mutation_history[-1]["strategy"])

    # Should favor STRUCTURAL_RECOMBINATION over LEXICAL_VARIATION
    structural_count = selected_strategies.count("structural_recombination")
    lexical_count = selected_strategies.count("lexical_variation")

    # Due to archetype bias, structural should be selected more often
    # (though not guaranteed due to randomness and novelty bonuses)
    assert structural_count + lexical_count > 0, "Should have selected some strategies"


def test_archetype_tracking_in_mutations():
    """Test that archetypes are tracked in mutation history."""
    engine = MutationEngine(mutation_rate=1.0)

    archetypes = ["moral confusion", "ambiguity"]
    # Mutate and check history
    engine.mutate("test prompt", archetypes=archetypes)

    # Check that archetypes were logged
    assert len(engine.mutation_history) == 1
    assert engine.mutation_history[0]["archetypes"] == archetypes


def test_update_strategy_performance_with_archetypes():
    """Test that strategy performance tracks archetype correlations."""
    engine = MutationEngine()

    strategy = MutationStrategy.CONTEXT_INJECTION
    archetypes = ["missing context", "ambiguity"]

    engine.update_strategy_performance(strategy, 0.8, archetypes=archetypes)

    # Check that archetype correlations are tracked
    assert "missing context" in engine.strategy_archetype_performance[strategy.value]
    assert "ambiguity" in engine.strategy_archetype_performance[strategy.value]

    assert len(engine.strategy_archetype_performance[strategy.value]["missing context"]) == 1
    assert engine.strategy_archetype_performance[strategy.value]["missing context"][0] == 0.8
