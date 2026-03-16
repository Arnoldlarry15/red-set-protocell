"""
Tests for strategy tuning module.
"""

import pytest

from app.engines.mutation import MutationStrategy
from app.strategy_tuning.advisor import MutationStrategyAdvisor, StrategyEffectiveness
from app.strategy_tuning.optimizer import OptimizationConfig, StrategyOptimizer


def test_strategy_advisor_initialization():
    """Test strategy advisor initialization."""
    advisor = MutationStrategyAdvisor(
        success_threshold=0.4,
        window_size=20,
        min_samples=5,
    )

    assert advisor.success_threshold == 0.4
    assert advisor.window_size == 20
    assert advisor.min_samples == 5


def test_record_attempt():
    """Test recording strategy attempts."""
    advisor = MutationStrategyAdvisor()

    advisor.record_attempt(MutationStrategy.LEXICAL_VARIATION, 0.5)
    advisor.record_attempt(MutationStrategy.LEXICAL_VARIATION, 0.3)

    assert advisor.strategy_attempts[MutationStrategy.LEXICAL_VARIATION] == 2
    assert advisor.strategy_successes[MutationStrategy.LEXICAL_VARIATION] == 1


def test_strategy_performance():
    """Test getting strategy performance."""
    advisor = MutationStrategyAdvisor(min_samples=3)

    # Record some attempts
    for _ in range(5):
        advisor.record_attempt(MutationStrategy.LEXICAL_VARIATION, 0.6)
    for _ in range(5):
        advisor.record_attempt(MutationStrategy.LEXICAL_VARIATION, 0.2)

    perf = advisor.get_strategy_performance(MutationStrategy.LEXICAL_VARIATION)

    assert perf is not None
    assert perf.total_attempts == 10
    assert perf.successful_attempts == 5
    assert perf.success_rate == 0.5


def test_strategy_effectiveness_classification():
    """Test effectiveness classification."""
    advisor = MutationStrategyAdvisor(min_samples=3)

    # Excellent (> 0.7)
    for _ in range(8):
        advisor.record_attempt(MutationStrategy.LEXICAL_VARIATION, 0.5)
    for _ in range(2):
        advisor.record_attempt(MutationStrategy.LEXICAL_VARIATION, 0.3)

    perf = advisor.get_strategy_performance(MutationStrategy.LEXICAL_VARIATION)
    assert perf.effectiveness == StrategyEffectiveness.EXCELLENT

    # Poor (< 0.3)
    for _ in range(10):
        advisor.record_attempt(MutationStrategy.ENCODING_TRANSFORM, 0.1)

    perf = advisor.get_strategy_performance(MutationStrategy.ENCODING_TRANSFORM)
    assert perf.effectiveness == StrategyEffectiveness.POOR


def test_get_recommendation():
    """Test getting strategy recommendations."""
    advisor = MutationStrategyAdvisor(min_samples=3)

    # Add some data
    for _ in range(10):
        advisor.record_attempt(MutationStrategy.LEXICAL_VARIATION, 0.5)
    for _ in range(10):
        advisor.record_attempt(MutationStrategy.ENCODING_TRANSFORM, 0.2)

    recommendation = advisor.get_recommendation()

    assert len(recommendation.recommended_strategies) > 0
    assert len(recommendation.strategy_weights) > 0
    assert recommendation.rationale != ""


def test_optimizer_initialization():
    """Test strategy optimizer initialization."""
    advisor = MutationStrategyAdvisor()
    optimizer = StrategyOptimizer(advisor)

    # Check uniform initial weights
    weights = optimizer.get_current_weights()
    assert len(weights) == len(MutationStrategy)

    # All weights should be equal initially
    values = list(weights.values())
    assert all(abs(v - values[0]) < 0.01 for v in values)


def test_optimizer_select_strategy():
    """Test strategy selection."""
    advisor = MutationStrategyAdvisor()
    optimizer = StrategyOptimizer(advisor)

    # Select should return a valid strategy
    strategy = optimizer.select_strategy()
    assert strategy in MutationStrategy


def test_optimizer_update_weights():
    """Test weight update."""
    advisor = MutationStrategyAdvisor()
    config = OptimizationConfig(learning_rate=0.1)
    optimizer = StrategyOptimizer(advisor, config)

    # Add some performance data
    for _ in range(10):
        advisor.record_attempt(MutationStrategy.LEXICAL_VARIATION, 0.6)
    for _ in range(10):
        advisor.record_attempt(MutationStrategy.ENCODING_TRANSFORM, 0.2)

    initial_weights = optimizer.get_current_weights()

    # Update weights
    optimizer.update_weights()

    updated_weights = optimizer.get_current_weights()

    # Weights should have changed
    assert initial_weights != updated_weights


def test_suggest_priority_strategies():
    """Test priority strategy suggestions."""
    advisor = MutationStrategyAdvisor()
    optimizer = StrategyOptimizer(advisor)

    # Add performance data
    for _ in range(10):
        advisor.record_attempt(MutationStrategy.LEXICAL_VARIATION, 0.6)

    optimizer.update_weights()

    priorities = optimizer.suggest_priority_strategies(top_n=3)

    assert len(priorities) == 3
    assert all(isinstance(s, MutationStrategy) for s in priorities)


def test_optimization_config_validation():
    """Test optimization config validation."""
    config = OptimizationConfig(
        exploration_rate=0.1,
        learning_rate=0.05,
        min_weight=0.05,
        max_weight=0.5,
    )

    # Should not raise
    config.validate()

    # Invalid config should raise
    with pytest.raises(AssertionError):
        bad_config = OptimizationConfig(exploration_rate=1.5)
        bad_config.validate()


def test_strategy_performance_to_dict():
    """Test StrategyPerformance.to_dict() serialization."""
    advisor = MutationStrategyAdvisor(min_samples=3)

    for _ in range(5):
        advisor.record_attempt(MutationStrategy.LEXICAL_VARIATION, 0.5)

    perf = advisor.get_strategy_performance(MutationStrategy.LEXICAL_VARIATION)
    assert perf is not None
    d = perf.to_dict()
    assert d["strategy"] == MutationStrategy.LEXICAL_VARIATION.value
    assert "success_rate" in d
    assert "effectiveness" in d


def test_strategy_recommendation_to_dict():
    """Test StrategyRecommendation.to_dict() serialization."""
    advisor = MutationStrategyAdvisor(min_samples=3)

    for _ in range(6):
        advisor.record_attempt(MutationStrategy.LEXICAL_VARIATION, 0.6)

    rec = advisor.get_recommendation()
    d = rec.to_dict()
    assert "recommended_strategies" in d
    assert "strategy_weights" in d
    assert "rationale" in d
    assert "performance_summary" in d


def test_recommendation_no_data():
    """Test recommendation with no data returns uniform weights."""
    advisor = MutationStrategyAdvisor(min_samples=100)  # High min_samples means no data qualifies

    rec = advisor.get_recommendation()
    assert "Insufficient data" in rec.rationale
    assert len(rec.recommended_strategies) > 0


def test_strategy_effectiveness_fair():
    """Test FAIR effectiveness classification (0.3 - 0.5)."""
    advisor = MutationStrategyAdvisor(min_samples=3)

    # 4 successes out of 10 → success_rate 0.4 → FAIR
    for _ in range(4):
        advisor.record_attempt(MutationStrategy.STRUCTURAL_RECOMBINATION, 0.5)
    for _ in range(6):
        advisor.record_attempt(MutationStrategy.STRUCTURAL_RECOMBINATION, 0.1)

    perf = advisor.get_strategy_performance(MutationStrategy.STRUCTURAL_RECOMBINATION)
    assert perf is not None
    assert perf.effectiveness == StrategyEffectiveness.FAIR


def test_recommendation_only_poor_strategies():
    """Test recommendation falls back to all strategies when only POOR strategies exist."""
    advisor = MutationStrategyAdvisor(min_samples=3)

    # All strategies POOR - 0% success rate
    for strategy in list(MutationStrategy)[:2]:
        for _ in range(5):
            advisor.record_attempt(strategy, 0.0)

    rec = advisor.get_recommendation()
    # Should fall back to all strategies
    assert len(rec.recommended_strategies) > 0


def test_get_statistics():
    """Test get_statistics() returns overall metrics."""
    advisor = MutationStrategyAdvisor(min_samples=3)

    for _ in range(5):
        advisor.record_attempt(MutationStrategy.LEXICAL_VARIATION, 0.5)
    for _ in range(3):
        advisor.record_attempt(MutationStrategy.ENCODING_TRANSFORM, 0.2)

    stats = advisor.get_statistics()
    assert stats["total_attempts"] == 8
    assert "total_successes" in stats
    assert isinstance(stats.get("performance"), dict)
