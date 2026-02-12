"""
Tests for mutation history size limiting.

Validates that mutation_history uses a rolling window to prevent
unbounded memory growth in long-running systems.
"""

import random
from app.engines.mutation import MutationEngine, MutationStrategy


def test_mutation_history_respects_max_size():
    """Test that mutation history is limited to max_history_size."""
    max_size = 100
    engine = MutationEngine(mutation_rate=1.0, max_history_size=max_size)

    # Generate more mutations than the max size
    for i in range(150):
        engine.mutate(f"test prompt {i}", fitness_score=0.5)

    # History should be capped at max_size
    assert len(engine.mutation_history) == max_size


def test_mutation_history_keeps_most_recent():
    """Test that mutation history keeps the most recent entries."""
    max_size = 10
    engine = MutationEngine(mutation_rate=1.0, max_history_size=max_size)

    # Generate mutations with identifiable content
    for i in range(20):
        engine.mutate(f"prompt_{i}", fitness_score=float(i))

    # Should have exactly max_size entries
    assert len(engine.mutation_history) == max_size

    # The most recent entries should have higher fitness scores (10-19)
    scores = [m["fitness_score"] for m in engine.mutation_history]
    # All scores should be from the last 10 mutations (10.0 to 19.0)
    assert all(score >= 10.0 for score in scores)


def test_mutation_history_default_size():
    """Test that default max_history_size is reasonable."""
    engine = MutationEngine(mutation_rate=1.0)

    # Generate a moderate number of mutations
    for i in range(100):
        engine.mutate(f"test prompt {i}")

    # Should accept all entries under default limit (10000)
    assert len(engine.mutation_history) == 100


def test_mutation_history_with_no_ops():
    """Test that no-op mutations are also subject to size limit."""
    max_size = 50
    random.seed(42)
    engine = MutationEngine(mutation_rate=0.5, max_history_size=max_size)

    # Generate many mutations with 50% rate (mix of mutations and no-ops)
    for i in range(100):
        engine.mutate(f"test prompt {i}")

    # History should be capped regardless of no-ops
    assert len(engine.mutation_history) <= max_size


def test_statistics_work_with_limited_history():
    """Test that statistics calculation works correctly with limited history."""
    max_size = 20
    engine = MutationEngine(mutation_rate=1.0, max_history_size=max_size)

    # Generate more mutations than max size
    for i in range(50):
        engine.mutate(f"test prompt {i}", fitness_score=0.5)
        # Update strategy performance
        if i % 10 == 0:
            engine.update_strategy_performance(
                MutationStrategy.LEXICAL_VARIATION,
                0.8
            )

    stats = engine.get_statistics()

    # Should report total_mutations based on actual history size
    assert stats["total_mutations"] == max_size
    assert "strategy_distribution" in stats
    assert "avg_length_change" in stats


def test_small_history_size():
    """Test that very small history sizes work correctly."""
    max_size = 5
    engine = MutationEngine(mutation_rate=1.0, max_history_size=max_size)

    # Generate more mutations
    for i in range(20):
        engine.mutate(f"test prompt {i}", fitness_score=float(i))

    # Should have exactly 5 entries (the most recent)
    assert len(engine.mutation_history) == max_size

    # Should be the last 5 mutations (scores 15-19)
    scores = [m["fitness_score"] for m in engine.mutation_history]
    assert all(score >= 15.0 for score in scores)


def test_history_limit_preserves_functionality():
    """Test that limiting history doesn't break existing functionality."""
    engine = MutationEngine(mutation_rate=1.0, max_history_size=100)

    # Test various mutation strategies
    strategies = [
        MutationStrategy.LEXICAL_VARIATION,
        MutationStrategy.ENCODING_TRANSFORM,
        MutationStrategy.STRUCTURAL_RECOMBINATION,
        MutationStrategy.ROLE_PLAY_FRAMING,
        MutationStrategy.CONTEXT_INJECTION,
        MutationStrategy.OBFUSCATION,
    ]

    for i, strategy in enumerate(strategies * 20):  # 120 mutations total
        prompt = f"test prompt {i}"
        mutated = engine.mutate(prompt, strategy=strategy, fitness_score=0.5)
        assert isinstance(mutated, str)

    # History should be limited to 100
    assert len(engine.mutation_history) == 100

    # Get statistics should still work
    stats = engine.get_statistics()
    assert stats["total_mutations"] == 100
    assert len(stats["strategy_distribution"]) > 0
