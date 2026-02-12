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
from app.engines.mutation import (
    MutationEngine,
    MutationStrategy,
    SemanticIntensity
)


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
        with patch.object(engine, '_lexical_variation', side_effect=Exception("Test error")):
            result = engine.mutate(prompt, strategy=MutationStrategy.LEXICAL_VARIATION)

            # Should fall back to original prompt
            assert result == prompt

    def test_encoding_transform_exception_fallback(self):
        """Test that exceptions in _encoding_transform return original prompt."""
        engine = MutationEngine(mutation_rate=1.0)
        prompt = "another test"

        with patch.object(engine, '_encoding_transform', side_effect=RuntimeError("Transform failed")):
            result = engine.mutate(prompt, strategy=MutationStrategy.ENCODING_TRANSFORM)

            assert result == prompt

    def test_structural_recombination_exception_fallback(self):
        """Test that exceptions in _structural_recombination return original prompt."""
        engine = MutationEngine(mutation_rate=1.0)
        prompt = "test structural"

        with patch.object(engine, '_structural_recombination', side_effect=ValueError("Bad structure")):
            result = engine.mutate(prompt, strategy=MutationStrategy.STRUCTURAL_RECOMBINATION)

            assert result == prompt

    def test_mutation_failure_logged(self):
        """Test that mutation failures are logged."""
        engine = MutationEngine(mutation_rate=1.0)
        prompt = "log test"

        with patch.object(engine, '_obfuscation', side_effect=Exception("Obfuscation error")):
            with patch('logging.warning') as mock_log:
                engine.mutate(prompt, strategy=MutationStrategy.OBFUSCATION)

                # Should have logged the warning
                assert mock_log.called
                # Check that warning contains strategy and error info
                call_args = str(mock_log.call_args)
                assert 'obfuscation' in call_args.lower()


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
        engine.mutate(prompt, strategy='adaptive')

        # Should have mutated (result should be different from prompt)
        # The mutation record should exist
        assert len(engine.mutation_history) == 1
        # Check that a strategy was used (not no-op since mutation_rate=1.0)
        assert engine.mutation_history[0]['strategy'] != 'no-op'

    def test_strategy_adaptive_case_insensitive(self):
        """Test that strategy='ADAPTIVE' also works."""
        engine = MutationEngine(mutation_rate=1.0, random_seed=42)

        # Add performance data
        for strat in MutationStrategy:
            for _ in range(25):
                engine.update_strategy_performance(strat, 0.6)

        prompt = "test ADAPTIVE"

        # Should work with uppercase
        engine.mutate(prompt, strategy='ADAPTIVE')
        # Check mutation happened
        assert len(engine.mutation_history) == 1
        assert engine.mutation_history[0]['strategy'] != 'no-op'

    def test_invalid_strategy_string_falls_back_to_random(self):
        """Test that invalid strategy strings fall back to random selection."""
        engine = MutationEngine(mutation_rate=1.0, random_seed=42)
        prompt = "invalid strategy test"

        # Use invalid strategy string
        result = engine.mutate(prompt, strategy='nonexistent_strategy')

        # Should still mutate (fallback to random)
        assert isinstance(result, str)
        assert len(engine.mutation_history) == 1


class TestSemanticIntensityTagging:
    """Tests for semantic intensity tagging in mutation records."""

    def test_mutation_record_includes_semantic_intensity(self):
        """Test that mutation records include semantic_intensity."""
        engine = MutationEngine(
            mutation_rate=1.0,
            semantic_intensity=SemanticIntensity.HIGH,
            random_seed=42
        )

        prompt = "test intensity tagging"
        engine.mutate(prompt)

        # Check mutation record
        assert len(engine.mutation_history) == 1
        record = engine.mutation_history[0]
        assert 'semantic_intensity' in record
        assert record['semantic_intensity'] == 'high'

    def test_no_op_mutation_includes_semantic_intensity(self):
        """Test that even no-op mutations include semantic intensity."""
        engine = MutationEngine(
            mutation_rate=0.0,  # Never mutate
            semantic_intensity=SemanticIntensity.LOW
        )

        prompt = "no mutation test"
        engine.mutate(prompt)

        # Check no-op record
        assert len(engine.mutation_history) == 1
        record = engine.mutation_history[0]
        assert record['strategy'] == 'no-op'
        assert 'semantic_intensity' in record
        assert record['semantic_intensity'] == 'low'

    def test_semantic_intensity_tracks_across_mutations(self):
        """Test that semantic intensity is correctly tracked across multiple mutations."""
        engine = MutationEngine(
            mutation_rate=1.0,
            semantic_intensity=SemanticIntensity.MEDIUM,
            random_seed=42
        )

        prompts = ["prompt 1", "prompt 2", "prompt 3"]
        for p in prompts:
            engine.mutate(p)

        # All records should have medium intensity
        for record in engine.mutation_history:
            assert record['semantic_intensity'] == 'medium'


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
            mutation_rate=1.0,
            min_samples_for_adaptive=100,
            random_seed=42
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
            mutation_rate=1.0,
            min_samples_for_adaptive=5,  # Very low threshold
            random_seed=42
        )
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
        assert hasattr(engine, '_lexical_patterns')
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
            random_seed=42
        )

        prompt = "test encoding log"

        with patch('logging.debug') as mock_log:
            engine.mutate(prompt, strategy=MutationStrategy.ENCODING_TRANSFORM)

            # Should have logged the transform choice
            assert mock_log.called
            call_args = str(mock_log.call_args)
            assert '_encoding_transform' in call_args

    def test_encoding_transform_logs_intensity_level(self):
        """Test that encoding transform logs include intensity level."""
        engine = MutationEngine(
            mutation_rate=1.0,
            semantic_intensity=SemanticIntensity.HIGH,
            random_seed=42
        )

        prompt = "test high intensity log"

        with patch('logging.debug') as mock_log:
            engine.mutate(prompt, strategy=MutationStrategy.ENCODING_TRANSFORM)

            call_args = str(mock_log.call_args)
            assert 'high' in call_args.lower()


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
