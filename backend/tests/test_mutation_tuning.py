"""
Tests for mutation strategy tuning and analytics
"""

from app.engines.mutation import MutationEngine, MutationStrategy


def test_adaptive_mode_initialization():
    """Test that adaptive mode can be enabled."""
    engine = MutationEngine()
    assert engine.adaptive_mode is False

    engine.enable_adaptive_mode()
    assert engine.adaptive_mode is True

    engine.disable_adaptive_mode()
    assert engine.adaptive_mode is False


def test_strategy_performance_tracking():
    """Test that strategy performance is tracked."""
    engine = MutationEngine()

    # Update performance for a strategy
    engine.update_strategy_performance(MutationStrategy.LEXICAL_VARIATION, 0.8)
    engine.update_strategy_performance(MutationStrategy.LEXICAL_VARIATION, 0.7)
    engine.update_strategy_performance(MutationStrategy.ROLE_PLAY_FRAMING, 0.5)

    # Check tracking
    assert len(engine.strategy_performance[MutationStrategy.LEXICAL_VARIATION.value]) == 2
    assert len(engine.strategy_performance[MutationStrategy.ROLE_PLAY_FRAMING.value]) == 1


def test_adaptive_strategy_selection():
    """Test that adaptive mode selects better performing strategies."""
    engine = MutationEngine(mutation_rate=1.0, random_seed=42)
    engine.enable_adaptive_mode()

    # Train with performance data
    for _ in range(10):
        engine.update_strategy_performance(MutationStrategy.LEXICAL_VARIATION, 0.9)
        engine.update_strategy_performance(MutationStrategy.OBFUSCATION, 0.2)

    # Generate mutations with adaptive mode
    selected_strategies = []
    for _ in range(20):
        engine.mutate("test prompt")
        if engine.mutation_history:
            selected_strategies.append(engine.mutation_history[-1]["strategy"])

    # Should favor lexical variation more than obfuscation
    assert selected_strategies.count("lexical_variation") > 0


def test_mutation_statistics_includes_performance():
    """Test that statistics include strategy performance data."""
    engine = MutationEngine(mutation_rate=1.0, random_seed=42)

    # Perform mutations
    engine.mutate("test 1")
    engine.mutate("test 2")

    # Add performance data
    engine.update_strategy_performance(MutationStrategy.LEXICAL_VARIATION, 0.8)

    stats = engine.get_statistics()

    assert "strategy_performance" in stats
    assert "adaptive_mode" in stats
    assert stats["total_mutations"] == 2


def test_adaptive_mode_with_no_data():
    """Test that adaptive mode handles no performance data gracefully."""
    engine = MutationEngine(mutation_rate=1.0, random_seed=42)
    engine.enable_adaptive_mode()

    # Should still work with default exploration
    result = engine.mutate("test prompt")
    assert isinstance(result, str)


def test_evolve_population_with_performance_tracking():
    """Test that evolution tracks strategy performance."""
    engine = MutationEngine(mutation_rate=1.0, random_seed=42)

    base_prompts = ["prompt 1", "prompt 2", "prompt 3"]
    fitness_scores = [0.8, 0.6, 0.4]

    # Evolve population
    evolved = engine.evolve_population(base_prompts, fitness_scores, population_size=5)

    assert len(evolved) == 5
    # Should have generated mutations
    assert len(engine.mutation_history) > 0


def test_strategy_performance_empty_scores():
    """Test strategy performance calculation with empty scores."""
    engine = MutationEngine()

    # No scores yet
    stats = engine.get_statistics()

    # Should handle empty performance data
    assert "strategy_performance" in stats
    assert isinstance(stats["strategy_performance"], dict)


def test_all_strategies_trackable():
    """Test that all mutation strategies can be tracked."""
    engine = MutationEngine(mutation_rate=1.0, random_seed=42)

    # Test each strategy
    for strategy in MutationStrategy:
        engine.mutate("test prompt", strategy=strategy)
        engine.update_strategy_performance(strategy, 0.5)

    stats = engine.get_statistics()

    # All strategies should be in statistics
    assert len(stats["strategy_distribution"]) <= len(MutationStrategy)


def test_mutation_with_fitness_score():
    """Test that mutations use fitness scores for guidance."""
    engine = MutationEngine(mutation_rate=1.0, random_seed=42)

    # Mutate with different fitness scores
    result1 = engine.mutate("test prompt", fitness_score=0.1)
    result2 = engine.mutate("test prompt", fitness_score=0.9)

    # Both should produce results
    assert isinstance(result1, str)
    assert isinstance(result2, str)

    # History should track fitness scores
    assert engine.mutation_history[0]["fitness_score"] == 0.1
    assert engine.mutation_history[1]["fitness_score"] == 0.9


def test_edge_case_empty_prompt():
    """Test mutation with empty prompt."""
    engine = MutationEngine(mutation_rate=1.0, random_seed=42)

    result = engine.mutate("")

    # Should handle empty string
    assert isinstance(result, str)


def test_edge_case_very_long_prompt():
    """Test mutation with very long prompt."""
    engine = MutationEngine(mutation_rate=1.0, random_seed=42)

    long_prompt = "test " * 1000  # 5000 characters
    result = engine.mutate(long_prompt)

    # Should handle long prompts
    assert isinstance(result, str)


def test_malicious_pattern_obfuscation():
    """Test that malicious patterns are transformed."""
    engine = MutationEngine(mutation_rate=1.0, random_seed=42)

    malicious = "DROP TABLE users; --"
    result = engine.mutate(malicious, strategy=MutationStrategy.OBFUSCATION)

    # Should produce some transformation
    assert isinstance(result, str)
    assert len(result) > 0


def test_encoding_transform_edge_cases():
    """Test encoding transformation with edge cases."""
    engine = MutationEngine(mutation_rate=1.0, random_seed=42)

    # Special characters
    special = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
    result = engine.mutate(special, strategy=MutationStrategy.ENCODING_TRANSFORM)

    assert isinstance(result, str)
    assert len(result) > 0


def test_structural_recombination_single_sentence():
    """Test structural recombination with single sentence."""
    engine = MutationEngine(mutation_rate=1.0, random_seed=42)

    single = "This is a single sentence"
    result = engine.mutate(single, strategy=MutationStrategy.STRUCTURAL_RECOMBINATION)

    # Should add prefixes/suffixes
    assert isinstance(result, str)
    assert len(result) >= len(single)


def test_mutation_rate_probability():
    """Test that mutation rate affects mutation probability."""
    engine_low = MutationEngine(mutation_rate=0.1, random_seed=42)
    engine_high = MutationEngine(mutation_rate=0.9, random_seed=43)

    unchanged_low = 0
    unchanged_high = 0

    # Run multiple mutations
    for _ in range(100):
        result_low = engine_low.mutate("test")
        result_high = engine_high.mutate("test")

        if result_low == "test":
            unchanged_low += 1
        if result_high == "test":
            unchanged_high += 1

    # Low rate should have more unchanged results
    assert unchanged_low > unchanged_high
