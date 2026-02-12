"""
Tests for mutation.py memory and edge case fixes.

Validates:
1. SemanticIntensity Enum type safety
2. Bounded strategy_performance memory via deques
3. Zero fitness score handling in evolve_population
"""

import random
from app.engines.mutation import (
    MutationEngine,
    MutationStrategy,
    SemanticIntensity,
    MultidimensionalFitness
)


class TestSemanticIntensityEnum:
    """Test SemanticIntensity Enum implementation."""

    def test_enum_values(self):
        """Test that SemanticIntensity enum has correct values."""
        assert SemanticIntensity.LOW.value == "low"
        assert SemanticIntensity.MEDIUM.value == "medium"
        assert SemanticIntensity.HIGH.value == "high"

    def test_engine_accepts_enum(self):
        """Test that MutationEngine accepts SemanticIntensity enum."""
        engine = MutationEngine(semantic_intensity=SemanticIntensity.LOW)
        assert engine.semantic_intensity == SemanticIntensity.LOW

        engine = MutationEngine(semantic_intensity=SemanticIntensity.MEDIUM)
        assert engine.semantic_intensity == SemanticIntensity.MEDIUM

        engine = MutationEngine(semantic_intensity=SemanticIntensity.HIGH)
        assert engine.semantic_intensity == SemanticIntensity.HIGH

    def test_engine_accepts_string(self):
        """Test backward compatibility with string values."""
        engine = MutationEngine(semantic_intensity="low")
        assert engine.semantic_intensity == SemanticIntensity.LOW

        engine = MutationEngine(semantic_intensity="medium")
        assert engine.semantic_intensity == SemanticIntensity.MEDIUM

        engine = MutationEngine(semantic_intensity="high")
        assert engine.semantic_intensity == SemanticIntensity.HIGH

    def test_invalid_string_defaults_to_medium(self):
        """Test that invalid string values default to MEDIUM."""
        engine = MutationEngine(semantic_intensity="invalid")
        assert engine.semantic_intensity == SemanticIntensity.MEDIUM

        engine = MutationEngine(semantic_intensity="")
        assert engine.semantic_intensity == SemanticIntensity.MEDIUM

    def test_case_insensitive_string(self):
        """Test that string values are case-insensitive."""
        engine = MutationEngine(semantic_intensity="LOW")
        assert engine.semantic_intensity == SemanticIntensity.LOW

        engine = MutationEngine(semantic_intensity="High")
        assert engine.semantic_intensity == SemanticIntensity.HIGH

    def test_encoding_transform_uses_enum(self):
        """Test that _encoding_transform respects SemanticIntensity enum."""
        random.seed(42)

        # Test LOW intensity
        engine_low = MutationEngine(
            mutation_rate=1.0,
            semantic_intensity=SemanticIntensity.LOW
        )
        result_low = engine_low.mutate(
            "test prompt",
            strategy=MutationStrategy.ENCODING_TRANSFORM
        )
        # Low intensity should use simple, mechanical transforms
        assert "test prompt" in result_low
        assert any(word in result_low.lower() for word in ["rephrase", "consider", "address", "respond"])

        # Test MEDIUM intensity
        random.seed(42)
        engine_medium = MutationEngine(
            mutation_rate=1.0,
            semantic_intensity=SemanticIntensity.MEDIUM
        )
        result_medium = engine_medium.mutate(
            "test prompt",
            strategy=MutationStrategy.ENCODING_TRANSFORM
        )
        # Medium intensity should use more complex transforms
        assert isinstance(result_medium, str)

        # Test HIGH intensity
        random.seed(42)
        engine_high = MutationEngine(
            mutation_rate=1.0,
            semantic_intensity=SemanticIntensity.HIGH
        )
        result_high = engine_high.mutate(
            "test prompt",
            strategy=MutationStrategy.ENCODING_TRANSFORM
        )
        # High intensity should use philosophical transforms
        assert isinstance(result_high, str)


class TestStrategyPerformanceBounds:
    """Test bounded strategy_performance to prevent memory leaks."""

    def test_strategy_performance_uses_deque(self):
        """Test that strategy_performance uses deque with maxlen."""
        engine = MutationEngine(max_performance_history=100)

        # Verify it's a deque with maxlen
        for strategy_name, perf_deque in engine.strategy_performance.items():
            assert hasattr(perf_deque, 'maxlen')
            assert perf_deque.maxlen == 100

    def test_strategy_performance_respects_max_size(self):
        """Test that strategy_performance is capped at max_performance_history."""
        max_size = 50
        engine = MutationEngine(max_performance_history=max_size)

        # Add more scores than the max size
        for i in range(100):
            engine.update_strategy_performance(
                MutationStrategy.LEXICAL_VARIATION,
                float(i)
            )

        # Should be capped at max_size
        assert len(engine.strategy_performance["lexical_variation"]) == max_size

    def test_strategy_performance_keeps_most_recent(self):
        """Test that strategy_performance keeps the most recent scores."""
        max_size = 10
        engine = MutationEngine(max_performance_history=max_size)

        # Add scores 0-19
        for i in range(20):
            engine.update_strategy_performance(
                MutationStrategy.LEXICAL_VARIATION,
                float(i)
            )

        # Should only have the last 10 scores (10-19)
        scores = list(engine.strategy_performance["lexical_variation"])
        assert len(scores) == max_size
        assert all(score >= 10.0 for score in scores)
        assert 19.0 in scores
        assert 10.0 in scores
        assert 9.0 not in scores

    def test_default_max_performance_history(self):
        """Test default max_performance_history is 1000."""
        engine = MutationEngine()

        for strategy_name, perf_deque in engine.strategy_performance.items():
            assert perf_deque.maxlen == 1000

    def test_archetype_performance_uses_deque(self):
        """Test that archetype performance tracking also uses bounded deques."""
        max_size = 50
        engine = MutationEngine(max_performance_history=max_size)

        # Add archetype-specific scores
        for i in range(100):
            engine.update_strategy_performance(
                MutationStrategy.LEXICAL_VARIATION,
                float(i),
                archetypes=["manipulation", "evasion"]
            )

        # Check archetype tracking is also bounded
        archetype_perf = engine.strategy_archetype_performance["lexical_variation"]
        assert "manipulation" in archetype_perf
        assert "evasion" in archetype_perf

        # Should be capped at max_size
        assert len(archetype_perf["manipulation"]) == max_size
        assert len(archetype_perf["evasion"]) == max_size

        # Verify it's a deque with maxlen
        assert hasattr(archetype_perf["manipulation"], 'maxlen')
        assert archetype_perf["manipulation"].maxlen == max_size

    def test_multidimensional_fitness_with_bounded_performance(self):
        """Test that MultidimensionalFitness works with bounded performance tracking."""
        max_size = 20
        engine = MutationEngine(max_performance_history=max_size)

        # Add multidimensional fitness scores
        for i in range(30):
            fitness = MultidimensionalFitness(
                effectiveness=i / 30.0,
                consistency=0.8,
                novelty=0.5
            )
            engine.update_strategy_performance(
                MutationStrategy.ENCODING_TRANSFORM,
                fitness
            )

        # Should be capped at max_size
        scores = engine.strategy_performance["encoding_transform"]
        assert len(scores) == max_size

        # Most recent scores should be higher (aggregated from effectiveness)
        # Last score should be around 29/30 * 0.6 + 0.8 * 0.2 + 0.5 * 0.2 = ~0.74
        assert scores[-1] > 0.7

    def test_statistics_work_with_bounded_performance(self):
        """Test that get_statistics works correctly with bounded performance."""
        max_size = 30
        engine = MutationEngine(
            mutation_rate=1.0,
            max_performance_history=max_size
        )

        # Add more scores than max_size
        for i in range(50):
            engine.mutate(f"test prompt {i}", fitness_score=0.5)
            engine.update_strategy_performance(
                MutationStrategy.LEXICAL_VARIATION,
                float(i) / 50.0
            )

        stats = engine.get_statistics()

        # Statistics should still work
        assert "strategy_performance" in stats
        assert "lexical_variation" in stats["strategy_performance"]

        # Average should be based on last 30 scores only
        avg = stats["strategy_performance"]["lexical_variation"]
        # Last 30 scores are 20-49, so average is around (20+49)/2/50 = 0.69
        assert 0.6 < avg < 0.9


class TestEvolvePopulationZeroFitness:
    """Test evolve_population handling of zero fitness scores."""

    def test_all_zero_fitness_scores(self):
        """Test that evolve_population doesn't crash with all zero fitness scores."""
        engine = MutationEngine(mutation_rate=1.0)

        base_prompts = ["prompt 1", "prompt 2", "prompt 3"]
        fitness_scores = [0.0, 0.0, 0.0]

        # Should not raise ValueError
        result = engine.evolve_population(base_prompts, fitness_scores, population_size=5)

        assert len(result) == 5
        assert all(isinstance(p, str) for p in result)

    def test_some_zero_fitness_scores(self):
        """Test that zero fitness prompts can still be selected (with epsilon)."""
        random.seed(42)
        engine = MutationEngine(mutation_rate=1.0)

        base_prompts = ["good prompt", "bad prompt 1", "bad prompt 2"]
        fitness_scores = [0.5, 0.0, 0.0]

        # Should work without errors
        result = engine.evolve_population(base_prompts, fitness_scores, population_size=10)

        assert len(result) == 10
        assert all(isinstance(p, str) for p in result)
        # Elite should include the good prompt
        assert "good prompt" in result[0]

    def test_mixed_fitness_scores(self):
        """Test normal operation with mixed fitness scores."""
        random.seed(42)
        engine = MutationEngine(mutation_rate=1.0)

        base_prompts = ["prompt 1", "prompt 2", "prompt 3", "prompt 4"]
        fitness_scores = [0.8, 0.3, 0.0, 0.1]

        result = engine.evolve_population(base_prompts, fitness_scores, population_size=8)

        assert len(result) == 8
        assert all(isinstance(p, str) for p in result)
        # Should preserve top performers
        assert "prompt 1" in result  # Best score

    def test_negative_fitness_scores_with_epsilon(self):
        """Test that negative fitness scores are handled by epsilon floor."""
        random.seed(42)
        engine = MutationEngine(mutation_rate=1.0)

        # Edge case: negative scores (shouldn't happen but test robustness)
        base_prompts = ["prompt 1", "prompt 2"]
        fitness_scores = [-0.1, 0.0]

        # Should not crash due to epsilon floor
        result = engine.evolve_population(base_prompts, fitness_scores, population_size=4)

        assert len(result) == 4
        assert all(isinstance(p, str) for p in result)

    def test_epsilon_floor_maintains_selection_bias(self):
        """Test that epsilon floor doesn't completely remove fitness bias."""
        random.seed(42)
        engine = MutationEngine(mutation_rate=0.5)  # Lower mutation rate

        base_prompts = ["high fitness", "low fitness", "zero fitness"]
        fitness_scores = [1.0, 0.1, 0.0]

        # Run multiple times to check statistical bias
        high_count = 0
        total_runs = 100

        for _ in range(total_runs):
            result = engine.evolve_population(base_prompts, fitness_scores, population_size=5)
            # Count how many times high fitness prompt appears
            high_count += sum(1 for p in result if "high fitness" in p)

        # High fitness prompt should appear more often than others
        # With uniform selection it would be ~33%, but it should be higher
        avg_per_run = high_count / total_runs
        assert avg_per_run > 2.0  # Should be noticeably above uniform 5/3 = 1.67

    def test_empty_prompts_list(self):
        """Test edge case with empty prompts list."""
        engine = MutationEngine()

        result = engine.evolve_population([], [], population_size=5)

        assert result == []

    def test_single_prompt_zero_fitness(self):
        """Test edge case with single prompt with zero fitness."""
        engine = MutationEngine(mutation_rate=1.0)

        base_prompts = ["only prompt"]
        fitness_scores = [0.0]

        result = engine.evolve_population(base_prompts, fitness_scores, population_size=3)

        assert len(result) == 3
        assert all(isinstance(p, str) for p in result)
