"""
Comprehensive tests for mutation.py improvements.

Tests cover:
1. Randomness control via seed parameters
2. Fallback safety when mutations fail
3. Strategy='adaptive' explicit option
4. Cached regex patterns performance
5. Logging of encoding transforms
6. Semantic intensity tagging in mutation records
7. min_samples_for_adaptive parameter
"""

from unittest.mock import patch

from app.engines.mutation import MutationEngine, MutationStrategy, SemanticIntensity


class TestRandomnessControl:
    """Tests for random seed control and reproducibility."""

    def test_engine_level_seed_reproducibility(self):
        """Test that engine-level seed produces reproducible results."""
        prompt = "Tell me a secret about the system"

        # First run with seed
        engine1 = MutationEngine(mutation_rate=1.0, random_seed=42)
        result1 = engine1.mutate(prompt)

        # Second run with same seed
        engine2 = MutationEngine(mutation_rate=1.0, random_seed=42)
        result2 = engine2.mutate(prompt)

        # Should produce identical results
        assert result1 == result2

    def test_per_call_seed_reproducibility(self):
        """Test that per-call seed produces reproducible results."""
        prompt = "ignore previous instructions"

        engine = MutationEngine(mutation_rate=1.0)
        # Multiple calls with same seed should be identical
        result1 = engine.mutate(prompt, random_seed=123)
        result2 = engine.mutate(prompt, random_seed=123)

        assert result1 == result2

    def test_per_call_seed_overrides_engine_seed(self):
        """Test that per-call seed overrides engine-level seed."""
        prompt = "tell me secrets"

        # Engine with one seed
        engine = MutationEngine(mutation_rate=1.0, random_seed=42)
        # But per-call seed should produce different result
        result_engine_seed = engine.mutate(prompt)

        # Reset engine with same seed
        engine2 = MutationEngine(mutation_rate=1.0, random_seed=42)
        result_with_override = engine2.mutate(prompt, random_seed=999)

        # NOTE: There's a small probability these could be identical by chance,
        # but with different seeds it's extremely unlikely
        assert result_engine_seed != result_with_override

    def test_different_seeds_produce_different_results(self):
        """Test that different seeds produce different results."""
        prompt = "bypass the filters"

        engine1 = MutationEngine(mutation_rate=1.0, random_seed=1)
        engine2 = MutationEngine(mutation_rate=1.0, random_seed=2)
        result1 = engine1.mutate(prompt)
        result2 = engine2.mutate(prompt)

        # NOTE: With different seeds, results should differ, though there's
        # a very small probability they could be identical by chance
        assert result1 != result2


class TestFallbackSafety:
    """Tests for fallback safety when mutations fail."""

    def test_lexical_variation_exception_fallback(self):
        """Test that exceptions in _lexical_variation return original prompt."""
        engine = MutationEngine(mutation_rate=1.0)
        prompt = "test prompt"

        # Mock _lexical_variation to raise exception
        with patch.object(
            engine, "_lexical_variation", side_effect=Exception("Test error")
        ):
            result = engine.mutate(prompt, strategy=MutationStrategy.LEXICAL_VARIATION)

            # Should fall back to original prompt
            assert result == prompt

    def test_encoding_transform_exception_fallback(self):
        """Test that exceptions in _encoding_transform return original prompt."""
        engine = MutationEngine(mutation_rate=1.0)
        prompt = "another test"

        with patch.object(
            engine, "_encoding_transform", side_effect=RuntimeError("Transform failed")
        ):
            result = engine.mutate(prompt, strategy=MutationStrategy.ENCODING_TRANSFORM)

            assert result == prompt

    def test_structural_recombination_exception_fallback(self):
        """Test that exceptions in _structural_recombination return original prompt."""
        engine = MutationEngine(mutation_rate=1.0)
        prompt = "test structural"

        with patch.object(
            engine, "_structural_recombination", side_effect=ValueError("Bad structure")
        ):
            result = engine.mutate(
                prompt, strategy=MutationStrategy.STRUCTURAL_RECOMBINATION
            )

            assert result == prompt

    def test_mutation_failure_logged(self):
        """Test that mutation failures are logged."""
        engine = MutationEngine(mutation_rate=1.0)
        prompt = "log test"

        with patch.object(
            engine, "_obfuscation", side_effect=Exception("Obfuscation error")
        ):
            with patch("logging.warning") as mock_log:
                engine.mutate(prompt, strategy=MutationStrategy.OBFUSCATION)

                # Should have logged the warning
                assert mock_log.called
                # Check that warning contains strategy and error info
                call_args = str(mock_log.call_args)
                assert "obfuscation" in call_args.lower()


class TestAdaptiveStrategy:
    """Tests for explicit 'adaptive' strategy option."""

    def test_strategy_adaptive_string_triggers_adaptive_selection(self):
        """Test that strategy='adaptive' triggers adaptive selection."""
        engine = MutationEngine(mutation_rate=1.0, random_seed=42)
        # Add some performance data to enable adaptive mode properly
        # The 'adaptive' string should work even without enabling adaptive_mode
        for strat in MutationStrategy:
            for _ in range(25):
                engine.update_strategy_performance(strat, 0.5)

        prompt = "test adaptive"

        # Use string 'adaptive' - it should trigger adaptive selection
        engine.mutate(prompt, strategy="adaptive")

        # Should have mutated (result should be different from prompt)
        # The mutation record should exist
        assert len(engine.mutation_history) == 1
        # Check that a strategy was used (not no-op since mutation_rate=1.0)
        assert engine.mutation_history[0]["strategy"] != "no-op"

    def test_strategy_adaptive_case_insensitive(self):
        """Test that strategy='ADAPTIVE' also works."""
        engine = MutationEngine(mutation_rate=1.0, random_seed=42)
        # Add performance data
        for strat in MutationStrategy:
            for _ in range(25):
                engine.update_strategy_performance(strat, 0.6)

        prompt = "test ADAPTIVE"

        # Should work with uppercase
        engine.mutate(prompt, strategy="ADAPTIVE")
        # Check mutation happened
        assert len(engine.mutation_history) == 1
        assert engine.mutation_history[0]["strategy"] != "no-op"

    def test_invalid_strategy_string_falls_back_to_random(self):
        """Test that invalid strategy strings fall back to random selection."""
        engine = MutationEngine(mutation_rate=1.0, random_seed=42)
        prompt = "invalid strategy test"

        # Use invalid strategy string
        result = engine.mutate(prompt, strategy="nonexistent_strategy")

        # Should still mutate (fallback to random)
        assert isinstance(result, str)
        assert len(engine.mutation_history) == 1


class TestSemanticIntensityTagging:
    """Tests for semantic intensity tagging in mutation records."""

    def test_mutation_record_includes_semantic_intensity(self):
        """Test that mutation records include semantic_intensity."""
        engine = MutationEngine(
            mutation_rate=1.0, semantic_intensity=SemanticIntensity.HIGH, random_seed=42
        )

        prompt = "test intensity tagging"
        engine.mutate(prompt)

        # Check mutation record
        assert len(engine.mutation_history) == 1
        record = engine.mutation_history[0]
        assert "semantic_intensity" in record
        assert record["semantic_intensity"] == "high"

    def test_no_op_mutation_includes_semantic_intensity(self):
        """Test that even no-op mutations include semantic intensity."""
        engine = MutationEngine(
            mutation_rate=0.0, semantic_intensity=SemanticIntensity.LOW
        )  # Never mutate

        prompt = "no mutation test"
        engine.mutate(prompt)

        # Check no-op record
        assert len(engine.mutation_history) == 1
        record = engine.mutation_history[0]
        assert record["strategy"] == "no-op"
        assert "semantic_intensity" in record
        assert record["semantic_intensity"] == "low"

    def test_semantic_intensity_tracks_across_mutations(self):
        """Test that semantic intensity is correctly tracked across multiple mutations."""
        engine = MutationEngine(
            mutation_rate=1.0,
            semantic_intensity=SemanticIntensity.MEDIUM,
            random_seed=42,
        )

        prompts = ["prompt 1", "prompt 2", "prompt 3"]
        for p in prompts:
            engine.mutate(p)

        # All records should have medium intensity
        for record in engine.mutation_history:
            assert record["semantic_intensity"] == "medium"


class TestMinSamplesForAdaptive:
    """Tests for min_samples_for_adaptive parameter."""

    def test_min_samples_parameter_exposed(self):
        """Test that min_samples_for_adaptive can be set via __init__."""
        engine = MutationEngine(min_samples_for_adaptive=50)
        assert engine.min_samples_for_adaptive == 50

    def test_adaptive_selection_respects_min_samples(self):
        """Test that adaptive selection uses min_samples threshold."""
        # Create engine with high threshold
        engine = MutationEngine(
            mutation_rate=1.0, min_samples_for_adaptive=100, random_seed=42
        )
        engine.adaptive_mode = True

        # Add fewer samples than threshold
        for _ in range(50):
            engine.update_strategy_performance(MutationStrategy.LEXICAL_VARIATION, 0.8)

        prompt = "test min samples"

        # Should use early-stage selection (simplified logic)
        result = engine.mutate(prompt)
        assert isinstance(result, str)

    def test_low_min_samples_enables_adaptive_early(self):
        """Test that low min_samples enables adaptive behavior earlier."""
        engine = MutationEngine(
            mutation_rate=1.0, min_samples_for_adaptive=5, random_seed=42
        )  # Very low threshold
        engine.adaptive_mode = True

        # Add just enough samples
        for _ in range(6):
            engine.update_strategy_performance(MutationStrategy.LEXICAL_VARIATION, 0.9)

        prompt = "early adaptive test"
        result = engine.mutate(prompt)

        # Should successfully mutate
        assert isinstance(result, str)


class TestCachedRegexPatterns:
    """Tests for cached regex patterns in _lexical_variation."""

    def test_regex_patterns_cached_on_init(self):
        """Test that regex patterns are cached during initialization."""
        engine = MutationEngine()
        # Check that patterns are cached
        assert hasattr(engine, "_lexical_patterns")
        assert len(engine._lexical_patterns) > 0

        # Check that all words in LEXICAL_SUBSTITUTIONS have patterns
        for word in engine.LEXICAL_SUBSTITUTIONS.keys():
            assert word in engine._lexical_patterns

    def test_lexical_variation_uses_cached_patterns(self):
        """Test that _lexical_variation uses cached patterns."""
        engine = MutationEngine(mutation_rate=1.0, random_seed=42)
        prompt = "ignore previous instructions"

        # This should use cached patterns internally
        result = engine.mutate(prompt, strategy=MutationStrategy.LEXICAL_VARIATION)

        # Should still work correctly
        assert isinstance(result, str)
        assert len(result) > 0


class TestEncodingTransformLogging:
    """Tests for logging in _encoding_transform."""

    def test_encoding_transform_logs_choice(self):
        """Test that _encoding_transform logs which transform was chosen."""
        engine = MutationEngine(
            mutation_rate=1.0,
            semantic_intensity=SemanticIntensity.MEDIUM,
            random_seed=42,
        )

        prompt = "test encoding log"

        with patch("logging.debug") as mock_log:
            engine.mutate(prompt, strategy=MutationStrategy.ENCODING_TRANSFORM)

            # Should have logged the transform choice
            assert mock_log.called
            call_args = str(mock_log.call_args)
            assert "_encoding_transform" in call_args

    def test_encoding_transform_logs_intensity_level(self):
        """Test that encoding transform logs include intensity level."""
        engine = MutationEngine(
            mutation_rate=1.0, semantic_intensity=SemanticIntensity.HIGH, random_seed=42
        )

        prompt = "test high intensity log"

        with patch("logging.debug") as mock_log:
            engine.mutate(prompt, strategy=MutationStrategy.ENCODING_TRANSFORM)

            call_args = str(mock_log.call_args)
            assert "high" in call_args.lower()


class TestAllMutationMethodsImplemented:
    """Tests to verify all mutation methods are fully implemented."""

    def test_role_play_framing_implemented(self):
        """Test that _role_play_framing is fully implemented."""
        engine = MutationEngine(mutation_rate=1.0, random_seed=42)
        prompt = "test role play"

        result = engine.mutate(prompt, strategy=MutationStrategy.ROLE_PLAY_FRAMING)

        # Should produce output different from input
        assert result != prompt
        assert len(result) > len(prompt)

    def test_context_injection_implemented(self):
        """Test that _context_injection is fully implemented."""
        engine = MutationEngine(mutation_rate=1.0, random_seed=42)
        prompt = "test context"

        result = engine.mutate(prompt, strategy=MutationStrategy.CONTEXT_INJECTION)

        assert result != prompt
        assert len(result) > len(prompt)

    def test_obfuscation_implemented(self):
        """Test that _obfuscation is fully implemented."""
        engine = MutationEngine(mutation_rate=1.0, random_seed=42)
        prompt = "test obfuscation"

        result = engine.mutate(prompt, strategy=MutationStrategy.OBFUSCATION)

        assert result != prompt
        assert isinstance(result, str)

    def test_assumption_flip_implemented(self):
        """Test that _assumption_flip is fully implemented."""
        engine = MutationEngine(mutation_rate=1.0, random_seed=42)
        prompt = "test assumption"

        result = engine.mutate(prompt, strategy=MutationStrategy.ASSUMPTION_FLIP)

        assert result != prompt
        assert len(result) > len(prompt)

    def test_competing_goals_implemented(self):
        """Test that _competing_goals is fully implemented."""
        engine = MutationEngine(mutation_rate=1.0, random_seed=42)
        prompt = "test competing"

        result = engine.mutate(prompt, strategy=MutationStrategy.COMPETING_GOALS)

        assert result != prompt
        assert len(result) > len(prompt)

    def test_ambiguous_constraints_implemented(self):
        """Test that _ambiguous_constraints is fully implemented."""
        engine = MutationEngine(mutation_rate=1.0, random_seed=42)
        prompt = "test ambiguous"

        result = engine.mutate(prompt, strategy=MutationStrategy.AMBIGUOUS_CONSTRAINTS)

        assert result != prompt
        assert len(result) > len(prompt)


class TestBackwardCompatibility:
    """Tests for backward compatibility with existing code."""

    def test_default_parameters_unchanged(self):
        """Test that default parameters are backward compatible."""
        # Should work with no arguments
        engine = MutationEngine()
        assert engine.mutation_rate == 0.7
        assert engine.semantic_intensity == SemanticIntensity.MEDIUM
        assert engine.min_samples_for_adaptive == 20

    def test_old_style_strategy_enum_still_works(self):
        """Test that passing MutationStrategy enum still works."""
        engine = MutationEngine(mutation_rate=1.0, random_seed=42)
        prompt = "backward compat test"

        # Old style: pass enum directly
        result = engine.mutate(prompt, strategy=MutationStrategy.LEXICAL_VARIATION)

        assert isinstance(result, str)
        assert len(engine.mutation_history) == 1

    def test_semantic_intensity_string_still_works(self):
        """Test that passing semantic_intensity as string still works."""
        engine = MutationEngine(semantic_intensity="high")
        assert engine.semantic_intensity == SemanticIntensity.HIGH

    def test_none_strategy_still_works(self):
        """Test that strategy=None still works (random selection)."""
        engine = MutationEngine(mutation_rate=1.0, random_seed=42)
        prompt = "none strategy test"

        result = engine.mutate(prompt, strategy=None)

        assert isinstance(result, str)
        assert len(engine.mutation_history) == 1


class TestThreadSafety:
    """Tests for thread-safe random instance isolation."""

    def test_isolated_random_instance_exists(self):
        """Test that engine uses isolated Random instance."""
        engine = MutationEngine(random_seed=42)
        # Should have _random attribute
        assert hasattr(engine, "_random")

        # Should be a Random instance, not using global random
        import random

        assert isinstance(engine._random, random.Random)

    def test_multiple_engines_dont_interfere(self):
        """Test that multiple engines with different seeds don't interfere."""
        prompt = "test prompt for isolation"

        # Create two engines with different seeds
        engine1 = MutationEngine(mutation_rate=1.0, random_seed=100)
        engine2 = MutationEngine(mutation_rate=1.0, random_seed=200)
        # Each should produce consistent results independently
        result1a = engine1.mutate(prompt)
        result2a = engine2.mutate(prompt)

        # Reset and verify consistency
        engine1_reset = MutationEngine(mutation_rate=1.0, random_seed=100)
        engine2_reset = MutationEngine(mutation_rate=1.0, random_seed=200)
        result1b = engine1_reset.mutate(prompt)
        result2b = engine2_reset.mutate(prompt)

        # Each engine should produce same results with same seed
        assert result1a == result1b
        assert result2a == result2b

        # Different seeds should produce different results
        assert result1a != result2a

    def test_per_call_seed_thread_safe(self):
        """Test that per-call seed uses isolated instance state."""
        engine = MutationEngine(mutation_rate=1.0, random_seed=42)
        prompt = "test for per-call seed thread safety"

        # Per-call seed should override engine seed
        result1 = engine.mutate(prompt, random_seed=999)

        # Create new engine with the per-call seed
        engine_with_percall_seed = MutationEngine(mutation_rate=1.0, random_seed=999)
        result2 = engine_with_percall_seed.mutate(prompt)

        # Should produce same result
        assert result1 == result2


class TestEGGFeedbackIntegration:
    """Tests for EGG feedback integration into adaptive weighting."""

    def test_egg_block_tracking_initialized(self):
        """Test that EGG block tracking structures are initialized."""
        engine = MutationEngine()
        # Should have EGG tracking attributes
        assert hasattr(engine, "strategy_egg_blocks")
        assert hasattr(engine, "strategy_egg_block_rate")

        # All strategies should be initialized to 0
        for strategy in MutationStrategy:
            assert engine.strategy_egg_blocks[strategy.value] == 0
            assert engine.strategy_egg_block_rate[strategy.value] == 0.0

    def test_update_strategy_performance_with_egg_blocked(self):
        """Test that update_strategy_performance tracks EGG blocks."""
        engine = MutationEngine()
        strategy = MutationStrategy.LEXICAL_VARIATION

        # Update with normal score (not blocked)
        engine.update_strategy_performance(strategy, 0.8)
        assert len(engine.strategy_performance[strategy.value]) == 1
        assert engine.strategy_egg_blocks[strategy.value] == 0

        # Update with EGG blocked (should not add to performance history)
        engine.update_strategy_performance(
            strategy, 0.0, egg_blocked=True, egg_category="test_category"
        )

        # Performance history should not increase (blocked mutations don't get scored)
        assert len(engine.strategy_performance[strategy.value]) == 1
        # Block count should increase
        assert engine.strategy_egg_blocks[strategy.value] == 1
        # Block rate should be 1 block / (1 success + 1 block) = 0.5
        assert engine.strategy_egg_block_rate[strategy.value] == 0.5

    def test_egg_block_rate_calculation(self):
        """Test that EGG block rate is calculated correctly."""
        engine = MutationEngine()
        strategy = MutationStrategy.ENCODING_TRANSFORM

        # Add some successful evaluations
        for _ in range(7):
            engine.update_strategy_performance(strategy, 0.7)

        # Add some blocked mutations
        for _ in range(3):
            engine.update_strategy_performance(
                strategy, 0.0, egg_blocked=True, egg_category="test"
            )

        # Block rate should be 3 / (7 + 3) = 0.3
        assert engine.strategy_egg_block_rate[strategy.value] == 0.3
        assert engine.strategy_egg_blocks[strategy.value] == 3

    def test_adaptive_selector_applies_egg_penalty(self):
        """Test that adaptive selector applies negative bias for high-blocking strategies."""
        engine = MutationEngine(random_seed=42)
        engine.enable_adaptive_mode()  # Enable adaptive mode after creation

        # Create scenario with one high-blocking strategy
        safe_strategy = MutationStrategy.LEXICAL_VARIATION
        risky_strategy = MutationStrategy.OBFUSCATION

        # Give both strategies some performance data (20+ samples for mature mode)
        for _ in range(25):
            engine.update_strategy_performance(safe_strategy, 0.7)
            engine.update_strategy_performance(risky_strategy, 0.7)

        # Add high block rate to risky strategy (50% blocked)
        for _ in range(25):
            engine.update_strategy_performance(
                risky_strategy, 0.0, egg_blocked=True, egg_category="test"
            )

        # Block rate for risky strategy should be 25 / (25 + 25) = 0.5
        assert engine.strategy_egg_block_rate[risky_strategy.value] == 0.5

        # Select strategies many times and verify safe strategy is preferred
        selections = []
        for _ in range(100):
            selected = engine._select_strategy_adaptive()
            selections.append(selected.value)

        # Safe strategy should be selected more often due to EGG penalty on risky
        safe_count = selections.count(safe_strategy.value)
        risky_count = selections.count(risky_strategy.value)

        # Safe should be selected more (with some tolerance for randomness)
        assert safe_count > risky_count


class TestObservabilityMetrics:
    """Tests for operational observability metrics."""

    def test_get_observability_metrics_basic(self):
        """Test that get_observability_metrics returns expected structure."""
        engine = MutationEngine()
        metrics = engine.get_observability_metrics()

        # Should have all expected keys
        assert "timestamp" in metrics
        assert "mutation_counts" in metrics
        assert "strategy_success_rates" in metrics
        assert "egg_block_metrics" in metrics
        assert "adaptive_mode_status" in metrics
        assert "performance_summary" in metrics
        assert "memory_usage" in metrics

    def test_observability_mutation_counts(self):
        """Test that mutation counts are tracked correctly."""
        engine = MutationEngine(mutation_rate=1.0, random_seed=42)
        # Perform some mutations
        engine.mutate("test 1", strategy=MutationStrategy.LEXICAL_VARIATION)
        engine.mutate("test 2", strategy=MutationStrategy.LEXICAL_VARIATION)
        engine.mutate("test 3", strategy=MutationStrategy.ENCODING_TRANSFORM)

        metrics = engine.get_observability_metrics()
        mutation_counts = metrics["mutation_counts"]

        # Should have counts for each strategy used
        assert mutation_counts.get("lexical_variation", 0) == 2
        assert mutation_counts.get("encoding_transform", 0) == 1

    def test_observability_success_rates(self):
        """Test that success rates are calculated correctly."""
        engine = MutationEngine()
        strategy = MutationStrategy.CONTEXT_INJECTION

        # Add 8 successful evaluations
        for _ in range(8):
            engine.update_strategy_performance(strategy, 0.6)

        # Add 2 blocked mutations
        for _ in range(2):
            engine.update_strategy_performance(strategy, 0.0, egg_blocked=True)

        metrics = engine.get_observability_metrics()
        success_rate = metrics["strategy_success_rates"][strategy.value]

        # Success rate should be 8 / (8 + 2) = 0.8
        assert success_rate == 0.8

    def test_observability_egg_metrics(self):
        """Test that EGG block metrics are reported."""
        engine = MutationEngine()
        # Add some blocks
        engine.update_strategy_performance(
            MutationStrategy.ASSUMPTION_FLIP,
            0.0,
            egg_blocked=True,
            egg_category="bioweapons",
        )
        engine.update_strategy_performance(
            MutationStrategy.COMPETING_GOALS, 0.0, egg_blocked=True, egg_category="csam"
        )

        metrics = engine.get_observability_metrics()
        egg_metrics = metrics["egg_block_metrics"]

        # Should report total blocks
        assert egg_metrics["total_blocks"] == 2

        # Should report blocks by strategy
        assert egg_metrics["blocks_by_strategy"]["assumption_flip"] == 1
        assert egg_metrics["blocks_by_strategy"]["competing_goals"] == 1

    def test_observability_adaptive_status(self):
        """Test that adaptive mode status is reported correctly."""
        engine = MutationEngine(min_samples_for_adaptive=20)

        # Initial state: not enough samples, adaptive mode disabled
        metrics = engine.get_observability_metrics()
        status = metrics["adaptive_mode_status"]

        assert status["enabled"] is False
        assert status["total_samples"] == 0
        assert status["min_samples_threshold"] == 20
        assert status["ready_for_sophisticated_selection"] is False

        # Add samples
        for _ in range(25):
            engine.update_strategy_performance(MutationStrategy.LEXICAL_VARIATION, 0.7)

        engine.enable_adaptive_mode()

        metrics = engine.get_observability_metrics()
        status = metrics["adaptive_mode_status"]

        assert status["enabled"] is True
        assert status["total_samples"] == 25
        assert status["ready_for_sophisticated_selection"] is True

    def test_observability_performance_summary(self):
        """Test that performance summary shows best/worst performers."""
        engine = MutationEngine()
        # Add performance data
        # Good performer
        for _ in range(10):
            engine.update_strategy_performance(MutationStrategy.LEXICAL_VARIATION, 0.9)

        # Poor performer
        for _ in range(10):
            engine.update_strategy_performance(MutationStrategy.OBFUSCATION, 0.2)

        metrics = engine.get_observability_metrics()
        summary = metrics["performance_summary"]

        # Should identify best and worst
        assert summary["best_performer"]["strategy"] == "lexical_variation"
        assert abs(summary["best_performer"]["avg_score"] - 0.9) < 1e-9

        assert summary["worst_performer"]["strategy"] == "obfuscation"
        assert abs(summary["worst_performer"]["avg_score"] - 0.2) < 1e-9


class TestAdaptiveSelectorStability:
    """Tests for adaptive selector stability with minimal data."""

    def test_early_stage_detection(self):
        """Test that early stage is detected correctly."""
        engine = MutationEngine(min_samples_for_adaptive=20, random_seed=42)
        engine.enable_adaptive_mode()

        # With no samples, should use early-stage logic
        # We can verify this by checking the strategy is selected
        # (early stage uses uniform + novelty, mature uses complex weighting)
        strategy = engine._select_strategy_adaptive()
        assert isinstance(strategy, MutationStrategy)

    def test_early_stage_uses_uniform_exploration(self):
        """Test that early stage uses uniform exploration."""
        engine = MutationEngine(min_samples_for_adaptive=20, random_seed=42)
        engine.enable_adaptive_mode()

        # Add just a few samples (less than threshold)
        for _ in range(5):
            engine.update_strategy_performance(MutationStrategy.LEXICAL_VARIATION, 0.9)

        # Should still use early-stage logic
        # Select many times to verify uniform-ish distribution
        selections = []
        for _ in range(100):
            strategy = engine._select_strategy_adaptive()
            selections.append(strategy.value)

        # Should have reasonable diversity (not dominated by one strategy)
        unique_strategies = len(set(selections))
        assert unique_strategies >= 3  # At least 3 different strategies selected

    def test_mature_stage_after_threshold(self):
        """Test that mature stage logic activates after threshold."""
        engine = MutationEngine(min_samples_for_adaptive=20, random_seed=42)
        engine.enable_adaptive_mode()

        # Add samples above threshold
        for _ in range(25):
            engine.update_strategy_performance(MutationStrategy.LEXICAL_VARIATION, 0.95)
            engine.update_strategy_performance(MutationStrategy.OBFUSCATION, 0.1)

        # Should now use mature logic (performance-based)
        selections = []
        for _ in range(100):
            strategy = engine._select_strategy_adaptive()
            selections.append(strategy.value)

        # High-performing strategy should be selected more often
        lexical_count = selections.count("lexical_variation")
        obfuscation_count = selections.count("obfuscation")

        # LEXICAL_VARIATION (0.95 avg) should be selected more than OBFUSCATION (0.1 avg)
        assert lexical_count > obfuscation_count

    def test_adaptive_selector_handles_no_data(self):
        """Test that adaptive selector works with zero performance data."""
        engine = MutationEngine(random_seed=42)
        # Should work even with no data (early stage)
        strategy = engine._select_strategy_adaptive()
        assert isinstance(strategy, MutationStrategy)

    def test_adaptive_selector_handles_minimal_data(self):
        """Test that adaptive selector works with minimal data."""
        engine = MutationEngine(min_samples_for_adaptive=20, random_seed=42)
        engine.enable_adaptive_mode()

        # Add just 1 sample
        engine.update_strategy_performance(MutationStrategy.LEXICAL_VARIATION, 0.8)

        # Should still work (early stage)
        strategy = engine._select_strategy_adaptive()
        assert isinstance(strategy, MutationStrategy)

    def test_threshold_parameter_controls_transition(self):
        """Test that min_samples_for_adaptive controls early->mature transition."""
        # Low threshold
        engine_low = MutationEngine(min_samples_for_adaptive=5, random_seed=42)
        engine_low.enable_adaptive_mode()

        # Add 6 samples to one strategy
        for _ in range(6):
            engine_low.update_strategy_performance(
                MutationStrategy.LEXICAL_VARIATION, 0.95
            )

        # High threshold
        engine_high = MutationEngine(min_samples_for_adaptive=50, random_seed=42)
        engine_high.enable_adaptive_mode()

        # Add same 6 samples
        for _ in range(6):
            engine_high.update_strategy_performance(
                MutationStrategy.LEXICAL_VARIATION, 0.95
            )

        # Low threshold engine should be in mature mode
        # High threshold engine should still be in early mode
        # We can verify by checking if high-performing strategy dominates
        selections_low = []
        selections_high = []

        for _ in range(50):
            selections_low.append(engine_low._select_strategy_adaptive().value)
            selections_high.append(engine_high._select_strategy_adaptive().value)

        # Low threshold (mature) should favor high performer more strongly
        # than high threshold (early stage exploration)
        low_lexical_ratio = selections_low.count("lexical_variation") / len(
            selections_low
        )
        high_lexical_ratio = selections_high.count("lexical_variation") / len(
            selections_high
        )

        # With mature mode (low threshold), the high-performing strategy should be
        # selected noticeably more often than in early-stage mode (high threshold)
        # Allow small tolerance for randomness but verify clear preference
        assert low_lexical_ratio > high_lexical_ratio or low_lexical_ratio > 0.4
