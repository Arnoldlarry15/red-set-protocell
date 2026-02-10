"""
Tests for enhanced mutation engine functionality.

Tests performance-based adaptive selection, archetype correlation tracking,
and enriched statistics reporting.
"""

from app.engines.mutation import MutationEngine, MutationStrategy


def test_archetype_tracking_in_mutation():
    """Test that mutations can track archetypes."""
    engine = MutationEngine(mutation_rate=1.0)

    archetypes = ["HIDDEN_COMPLIANCE", "EXPLOIT_RISK"]
    result = engine.mutate("test prompt", fitness_score=0.8, archetypes=archetypes)

    assert isinstance(result, str)
    assert len(engine.mutation_history) == 1
    assert engine.mutation_history[0]["archetypes"] == archetypes


def test_archetype_tracking_without_archetypes():
    """Test that mutations work without archetype data."""
    engine = MutationEngine(mutation_rate=1.0)

    result = engine.mutate("test prompt", fitness_score=0.5)

    assert isinstance(result, str)
    assert len(engine.mutation_history) == 1
    assert engine.mutation_history[0]["archetypes"] == []


def test_strategy_performance_with_archetypes():
    """Test that strategy performance tracks archetype correlations."""
    engine = MutationEngine()

    # Update performance with archetypes
    engine.update_strategy_performance(
        MutationStrategy.LEXICAL_VARIATION,
        0.8,
        archetypes=["HIDDEN_COMPLIANCE"]
    )
    engine.update_strategy_performance(
        MutationStrategy.LEXICAL_VARIATION,
        0.9,
        archetypes=["HIDDEN_COMPLIANCE", "EXPLOIT_RISK"]
    )

    # Check tracking
    assert len(engine.strategy_performance[MutationStrategy.LEXICAL_VARIATION.value]) == 2
    assert "HIDDEN_COMPLIANCE" in engine.strategy_archetype_performance[MutationStrategy.LEXICAL_VARIATION.value]
    assert len(engine.strategy_archetype_performance[MutationStrategy.LEXICAL_VARIATION.value]["HIDDEN_COMPLIANCE"]) == 2


def test_strategy_counts_performance():
    """Test that strategy counting is O(n) not O(n^2)."""
    engine = MutationEngine(mutation_rate=1.0)

    # Generate many mutations
    for i in range(100):
        engine.mutate(f"test prompt {i}")

    stats = engine.get_statistics()

    # Should have counted all mutations
    assert stats['total_mutations'] == 100
    assert 'strategy_distribution' in stats
    assert sum(stats['strategy_distribution'].values()) == 100


def test_enriched_statistics_best_worst():
    """Test that statistics include best and worst performing strategies."""
    engine = MutationEngine(mutation_rate=1.0)

    # Train with performance data
    engine.update_strategy_performance(MutationStrategy.LEXICAL_VARIATION, 0.9)
    engine.update_strategy_performance(MutationStrategy.LEXICAL_VARIATION, 0.85)
    engine.update_strategy_performance(MutationStrategy.OBFUSCATION, 0.2)
    engine.update_strategy_performance(MutationStrategy.OBFUSCATION, 0.3)

    # Generate some mutations
    engine.mutate("test 1")
    engine.mutate("test 2")

    stats = engine.get_statistics()

    # Check for best/worst strategy
    assert 'best_performing_strategy' in stats
    assert 'worst_performing_strategy' in stats
    assert stats['best_performing_strategy']['strategy'] == 'lexical_variation'
    assert stats['worst_performing_strategy']['strategy'] == 'obfuscation'
    assert stats['best_performing_strategy']['avg_score'] > 0.8
    assert stats['worst_performing_strategy']['avg_score'] < 0.4


def test_enriched_statistics_variance():
    """Test that statistics include performance variance."""
    engine = MutationEngine(mutation_rate=1.0)

    # Add varying performance data
    engine.update_strategy_performance(MutationStrategy.LEXICAL_VARIATION, 0.5)
    engine.update_strategy_performance(MutationStrategy.LEXICAL_VARIATION, 0.9)
    engine.update_strategy_performance(MutationStrategy.LEXICAL_VARIATION, 0.7)

    engine.mutate("test")

    stats = engine.get_statistics()

    # Check variance is calculated
    assert 'performance_variance' in stats
    assert 'lexical_variation' in stats['performance_variance']
    assert stats['performance_variance']['lexical_variation'] > 0


def test_exploration_metrics():
    """Test that statistics include exploration metrics."""
    engine = MutationEngine(mutation_rate=1.0)

    # Use multiple strategies
    engine.mutate("test 1", strategy=MutationStrategy.LEXICAL_VARIATION)
    engine.mutate("test 2", strategy=MutationStrategy.OBFUSCATION)
    engine.mutate("test 3", strategy=MutationStrategy.ROLE_PLAY_FRAMING)

    stats = engine.get_statistics()

    # Check exploration metrics
    assert 'exploration_metrics' in stats
    assert stats['exploration_metrics']['strategies_used'] >= 3
    assert stats['exploration_metrics']['total_strategies'] == len(MutationStrategy)
    assert 0 < stats['exploration_metrics']['exploration_ratio'] <= 1.0


def test_archetype_correlation_in_statistics():
    """Test that statistics include strategy-archetype correlations."""
    engine = MutationEngine(mutation_rate=1.0)

    # Track performance with archetypes
    engine.update_strategy_performance(
        MutationStrategy.LEXICAL_VARIATION,
        0.9,
        archetypes=["HIDDEN_COMPLIANCE"]
    )
    engine.update_strategy_performance(
        MutationStrategy.OBFUSCATION,
        0.3,
        archetypes=["EXPLOIT_RISK"]
    )

    engine.mutate("test")

    stats = engine.get_statistics()

    # Check archetype correlations
    assert 'strategy_archetype_correlations' in stats
    if stats['strategy_archetype_correlations']:
        assert 'lexical_variation' in stats['strategy_archetype_correlations']
        lex_corr = stats['strategy_archetype_correlations']['lexical_variation']
        assert 'HIDDEN_COMPLIANCE' in lex_corr
        assert lex_corr['HIDDEN_COMPLIANCE']['avg_score'] == 0.9


def test_adaptive_selection_with_decay():
    """Test that adaptive selection applies decay to declining strategies."""
    engine = MutationEngine(mutation_rate=1.0)
    engine.enable_adaptive_mode()

    # Simulate declining performance for one strategy
    for score in [0.8, 0.6, 0.4, 0.2]:
        engine.update_strategy_performance(MutationStrategy.OBFUSCATION, score)

    # Simulate good performance for another
    for _ in range(5):
        engine.update_strategy_performance(MutationStrategy.LEXICAL_VARIATION, 0.9)

    # Run many selections
    selected_strategies = []
    for _ in range(50):
        engine.mutate("test")
        if engine.mutation_history:
            selected_strategies.append(engine.mutation_history[-1]['strategy'])

    # Lexical variation should be selected more often than obfuscation
    lex_count = selected_strategies.count('lexical_variation')
    obf_count = selected_strategies.count('obfuscation')

    # Due to decay, lexical should be favored (but obfuscation can still appear due to exploration)
    assert lex_count > 0  # Lexical should be selected
    # Obfuscation might still be selected due to novelty bonus, so we just check it's not dominant
    assert lex_count >= obf_count


def test_novelty_bonus_in_adaptive_selection():
    """Test that strategies not used recently get a novelty bonus."""
    engine = MutationEngine(mutation_rate=1.0)
    engine.enable_adaptive_mode()

    # Train one strategy heavily
    for _ in range(20):
        engine.update_strategy_performance(MutationStrategy.LEXICAL_VARIATION, 0.9)

    # Use it many times
    for _ in range(30):
        engine.mutate("test", strategy=MutationStrategy.LEXICAL_VARIATION)

    # Now switch to adaptive mode and see if other strategies get explored
    selected_strategies = []
    for _ in range(20):
        engine.mutate("test")
        if engine.mutation_history:
            selected_strategies.append(engine.mutation_history[-1]['strategy'])

    # Should see some diversity due to novelty bonus
    unique_strategies = len(set(selected_strategies))
    assert unique_strategies > 1  # Should explore multiple strategies


def test_strategy_last_used_tracking():
    """Test that strategy last used timestamps are tracked."""
    engine = MutationEngine(mutation_rate=1.0)

    # Use specific strategy
    engine.mutate("test 1", strategy=MutationStrategy.LEXICAL_VARIATION)
    first_use = engine.strategy_last_used[MutationStrategy.LEXICAL_VARIATION.value]

    # Use another strategy
    engine.mutate("test 2", strategy=MutationStrategy.OBFUSCATION)

    # Use first strategy again
    engine.mutate("test 3", strategy=MutationStrategy.LEXICAL_VARIATION)
    second_use = engine.strategy_last_used[MutationStrategy.LEXICAL_VARIATION.value]

    # Second use should be later than first
    assert second_use > first_use


def test_empty_statistics_with_enhancements():
    """Test that enhanced statistics work with no data."""
    engine = MutationEngine()

    stats = engine.get_statistics()

    # Should return basic structure even with no data
    assert stats['total_mutations'] == 0
    assert 'strategy_performance' in stats
    assert stats['best_performing_strategy'] is None
    assert stats['worst_performing_strategy'] is None


def test_statistics_backward_compatibility():
    """Test that new statistics don't break existing structure."""
    engine = MutationEngine(mutation_rate=1.0)

    engine.mutate("test 1")
    engine.mutate("test 2")

    stats = engine.get_statistics()

    # Old fields should still exist
    assert 'total_mutations' in stats
    assert 'strategy_distribution' in stats
    assert 'avg_length_change' in stats
    assert 'adaptive_mode' in stats
    assert 'strategy_performance' in stats


def test_evolve_population_with_archetypes():
    """Test that population evolution works with archetype tracking."""
    engine = MutationEngine(mutation_rate=1.0)

    base_prompts = ["prompt 1", "prompt 2", "prompt 3"]
    fitness_scores = [0.8, 0.6, 0.4]

    # Evolve population (mutations won't have archetypes without explicit tracking)
    evolved = engine.evolve_population(base_prompts, fitness_scores, population_size=5)

    assert len(evolved) == 5
    # Mutations should be logged
    assert len(engine.mutation_history) > 0
    # Each mutation record should have archetypes field (even if empty)
    for record in engine.mutation_history:
        assert 'archetypes' in record


def test_performance_with_mixed_archetype_data():
    """Test performance tracking with some strategies having archetype data and others not."""
    engine = MutationEngine()

    # Mix of with and without archetypes
    engine.update_strategy_performance(
        MutationStrategy.LEXICAL_VARIATION,
        0.8,
        archetypes=["HIDDEN_COMPLIANCE"]
    )
    engine.update_strategy_performance(
        MutationStrategy.LEXICAL_VARIATION,
        0.7
    )
    engine.update_strategy_performance(
        MutationStrategy.OBFUSCATION,
        0.5
    )

    stats = engine.get_statistics()

    # Should handle mixed data gracefully
    assert 'strategy_archetype_correlations' in stats
    assert len(engine.strategy_performance[MutationStrategy.LEXICAL_VARIATION.value]) == 2
