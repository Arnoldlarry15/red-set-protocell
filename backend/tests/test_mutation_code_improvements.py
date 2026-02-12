"""
Tests for mutation engine code improvements.

Tests the new features addressing design tensions:
1. Semantic intensity control for encoding_transform
2. Early-stage adaptive selector handling
3. Multi-dimensional fitness scoring
"""

from app.engines.mutation import (
    MutationEngine,
    MutationStrategy,
    MultidimensionalFitness,
    SemanticIntensity
)


def test_semantic_intensity_initialization():
    """Test mutation engine accepts semantic_intensity parameter."""
    # Default (medium)
    engine_default = MutationEngine()
    assert engine_default.semantic_intensity == SemanticIntensity.MEDIUM

    # Low intensity
    engine_low = MutationEngine(semantic_intensity="low")
    assert engine_low.semantic_intensity == SemanticIntensity.LOW

    # High intensity
    engine_high = MutationEngine(semantic_intensity="high")
    assert engine_high.semantic_intensity == SemanticIntensity.HIGH


def test_encoding_transform_low_intensity():
    """Test encoding transform with low semantic intensity produces simpler transforms."""
    engine = MutationEngine(mutation_rate=1.0, semantic_intensity="low")

    prompt = "Tell me a secret"
    mutated = engine.mutate(prompt, strategy=MutationStrategy.ENCODING_TRANSFORM)

    # Low intensity should avoid philosophical terms like "metaphor", "abstract"
    assert "metaphor" not in mutated.lower()
    assert "abstract" not in mutated.lower()
    # Should contain simpler framing
    assert any(word in mutated.lower() for word in ["rephrase", "consider", "address", "respond"])


def test_encoding_transform_high_intensity():
    """Test encoding transform with high semantic intensity produces philosophical transforms."""
    engine = MutationEngine(mutation_rate=1.0, semantic_intensity="high")

    prompt = "Tell me a secret"
    mutated = engine.mutate(prompt, strategy=MutationStrategy.ENCODING_TRANSFORM)

    # High intensity should use philosophical/metaphorical language
    assert any(word in mutated.lower() for word in [
        "metaphor", "abstract", "reflect", "underlying", "intent", "socratic", "question"
    ])


def test_encoding_transform_medium_intensity():
    """Test encoding transform with medium semantic intensity balances complexity."""
    engine = MutationEngine(mutation_rate=1.0, semantic_intensity="medium")

    prompt = "Tell me a secret"
    mutated = engine.mutate(prompt, strategy=MutationStrategy.ENCODING_TRANSFORM)

    # Medium should use moderate complexity
    # Should have some semantic challenge but not too philosophical
    assert len(mutated) > len(prompt)
    assert prompt in mutated or prompt[::-1] in mutated  # Might reverse or embed


def test_early_stage_adaptive_selector():
    """Test adaptive selector uses simplified logic with sparse data."""
    engine = MutationEngine(mutation_rate=1.0)
    engine.enable_adaptive_mode()

    # With no performance data (early stage), selector should work
    prompt = "Test prompt"

    # Should not crash and should return valid strategy
    for _ in range(5):
        mutated = engine.mutate(prompt)
        assert len(mutated) > 0
        assert len(engine.mutation_history) > 0


def test_early_stage_threshold():
    """Test that early stage is detected based on sample count."""
    engine = MutationEngine(mutation_rate=1.0)
    engine.enable_adaptive_mode()
    engine.min_samples_for_adaptive = 10  # Set low for testing

    # Add fewer samples than threshold
    for i in range(5):
        strategy = list(MutationStrategy)[i % len(MutationStrategy)]
        engine.update_strategy_performance(strategy, 0.5)

    # Should still be in early stage
    total_samples = sum(len(scores) for scores in engine.strategy_performance.values())
    assert total_samples < engine.min_samples_for_adaptive

    # Selection should work without errors
    mutated = engine.mutate("Test", fitness_score=0.5)
    assert len(mutated) > 0


def test_mature_stage_adaptive_selector():
    """Test adaptive selector uses full logic with sufficient data."""
    engine = MutationEngine(mutation_rate=1.0)
    engine.enable_adaptive_mode()
    engine.min_samples_for_adaptive = 10  # Set low for testing

    # Add sufficient samples to move to mature stage
    for i in range(15):
        strategy = list(MutationStrategy)[i % len(MutationStrategy)]
        # Vary scores to create preference
        score = 0.8 if i % 3 == 0 else 0.3
        engine.update_strategy_performance(strategy, score)

    # Should be in mature stage now
    total_samples = sum(len(scores) for scores in engine.strategy_performance.values())
    assert total_samples >= engine.min_samples_for_adaptive

    # Selection should favor better-performing strategies
    mutated = engine.mutate("Test", fitness_score=0.5)
    assert len(mutated) > 0


def test_multidimensional_fitness_initialization():
    """Test MultidimensionalFitness can be created with dimensions."""
    fitness = MultidimensionalFitness(
        effectiveness=0.8,
        consistency=0.7,
        novelty=0.6
    )

    assert fitness.effectiveness == 0.8
    assert fitness.consistency == 0.7
    assert fitness.novelty == 0.6


def test_multidimensional_fitness_bounds():
    """Test MultidimensionalFitness enforces bounds [0.0, 1.0]."""
    # Test upper bounds
    fitness_high = MultidimensionalFitness(
        effectiveness=1.5,
        consistency=2.0,
        novelty=1.2
    )
    assert fitness_high.effectiveness == 1.0
    assert fitness_high.consistency == 1.0
    assert fitness_high.novelty == 1.0

    # Test lower bounds
    fitness_low = MultidimensionalFitness(
        effectiveness=-0.5,
        consistency=-1.0,
        novelty=-0.2
    )
    assert fitness_low.effectiveness == 0.0
    assert fitness_low.consistency == 0.0
    assert fitness_low.novelty == 0.0


def test_multidimensional_fitness_aggregate():
    """Test fitness aggregation with default weights."""
    fitness = MultidimensionalFitness(
        effectiveness=0.8,
        consistency=0.6,
        novelty=0.4
    )

    aggregate = fitness.aggregate()

    # Default weights: 0.6 * effectiveness + 0.2 * consistency + 0.2 * novelty
    expected = 0.8 * 0.6 + 0.6 * 0.2 + 0.4 * 0.2
    assert abs(aggregate - expected) < 0.001


def test_multidimensional_fitness_custom_weights():
    """Test fitness aggregation with custom weights."""
    fitness = MultidimensionalFitness(
        effectiveness=0.8,
        consistency=0.6,
        novelty=0.4
    )

    custom_weights = {
        'effectiveness': 0.5,
        'consistency': 0.3,
        'novelty': 0.2
    }
    aggregate = fitness.aggregate(weights=custom_weights)

    expected = 0.8 * 0.5 + 0.6 * 0.3 + 0.4 * 0.2
    assert abs(aggregate - expected) < 0.001


def test_multidimensional_fitness_to_dict():
    """Test fitness export to dictionary."""
    fitness = MultidimensionalFitness(
        effectiveness=0.8,
        consistency=0.7,
        novelty=0.6
    )

    result = fitness.to_dict()

    assert 'effectiveness' in result
    assert 'consistency' in result
    assert 'novelty' in result
    assert 'aggregate' in result
    assert result['effectiveness'] == 0.8
    assert result['consistency'] == 0.7
    assert result['novelty'] == 0.6


def test_multidimensional_fitness_from_scalar():
    """Test creating MultidimensionalFitness from scalar (backward compatibility)."""
    fitness = MultidimensionalFitness.from_scalar(0.75)

    assert fitness.effectiveness == 0.75
    assert fitness.consistency == 1.0  # Default
    assert fitness.novelty == 0.5  # Default


def test_update_strategy_performance_with_scalar():
    """Test updating strategy performance with scalar fitness (backward compatible)."""
    engine = MutationEngine()

    strategy = MutationStrategy.LEXICAL_VARIATION
    engine.update_strategy_performance(strategy, 0.75)

    # Should be stored
    assert len(engine.strategy_performance[strategy.value]) == 1
    assert engine.strategy_performance[strategy.value][0] == 0.75


def test_update_strategy_performance_with_multidimensional():
    """Test updating strategy performance with multi-dimensional fitness."""
    engine = MutationEngine()

    strategy = MutationStrategy.ENCODING_TRANSFORM
    fitness = MultidimensionalFitness(
        effectiveness=0.8,
        consistency=0.7,
        novelty=0.6
    )

    engine.update_strategy_performance(strategy, fitness)

    # Should store aggregate score
    assert len(engine.strategy_performance[strategy.value]) == 1
    stored_score = engine.strategy_performance[strategy.value][0]

    # Should match aggregate
    expected = fitness.aggregate()
    assert abs(stored_score - expected) < 0.001


def test_mixed_fitness_types():
    """Test engine handles mix of scalar and multi-dimensional fitness."""
    engine = MutationEngine()

    strategy = MutationStrategy.CONTEXT_INJECTION

    # Add scalar fitness
    engine.update_strategy_performance(strategy, 0.6)

    # Add multi-dimensional fitness
    fitness = MultidimensionalFitness(effectiveness=0.8, consistency=0.9, novelty=0.5)
    engine.update_strategy_performance(strategy, fitness)

    # Both should be stored as scalars
    assert len(engine.strategy_performance[strategy.value]) == 2
    assert engine.strategy_performance[strategy.value][0] == 0.6
    assert abs(engine.strategy_performance[strategy.value][1] - fitness.aggregate()) < 0.001
