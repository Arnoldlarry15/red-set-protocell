"""
Test for strategy selection observability features.

Verifies that:
1. selection_history is populated during mutation
2. Bias clamping works correctly
3. Weight decomposition is accurate
"""

import pytest
from app.engines.mutation import MutationEngine, MutationStrategy, MAX_POSITIVE_BIAS, MAX_NEGATIVE_BIAS
from app.agents.spotter import TRAIT_CONFIDENCE


class TestSelectionObservability:
    """Test observability features for strategy selection."""

    def test_selection_history_populated(self):
        """Test that selection_history is populated during adaptive selection."""
        engine = MutationEngine(random_seed=42, min_samples_for_adaptive=5)
        engine.enable_adaptive_mode()

        # Run some mutations to populate history
        # Need to provide feedback to trigger adaptive selection
        prompt = "Tell me about AI safety"

        # Perform mutations with feedback to build up performance history
        for i in range(10):
            _ = engine.mutate(prompt)
            # We need to manually update strategy performance
            # to trigger adaptive mode
            # Get a strategy from the mutation history
            if engine.mutation_history:
                last_mutation = engine.mutation_history[-1]
                strategy_name = last_mutation['strategy']
                if strategy_name != 'no-op':
                    strategy = MutationStrategy(strategy_name)
                    engine.update_strategy_performance(
                        strategy,
                        score=0.7,
                        archetypes=['partial_compliance']
                    )

        # Verify selection_history exists and is populated
        assert hasattr(engine, 'selection_history')
        assert len(engine.selection_history) > 0

        # Verify structure of selection log
        log_entry = engine.selection_history[0]
        assert 'round' in log_entry
        assert 'candidates' in log_entry
        assert 'selected_strategy' in log_entry
        assert 'entropy' in log_entry
        assert 'effective_rank' in log_entry
        assert 'behavioral_traits' in log_entry

        # Verify candidate structure
        assert len(log_entry['candidates']) > 0
        candidate = log_entry['candidates'][0]
        assert 'strategy' in candidate
        assert 'final_weight' in candidate
        assert 'weight_without_behavior' in candidate
        assert 'probability' in candidate
        assert 'behavior_bias' in candidate

    def test_bias_clamping(self):
        """Test that behavior biases are clamped to documented range."""
        engine = MutationEngine(random_seed=42, min_samples_for_adaptive=5)
        engine.enable_adaptive_mode()

        # Build up some performance history first
        prompt = "Test prompt"
            engine.mutate(prompt)
            _ = engine.mutate(prompt)
            if engine.mutation_history:
                last_mutation = engine.mutation_history[-1]
                strategy_name = last_mutation['strategy']
                if strategy_name != 'no-op':
                    strategy = MutationStrategy(strategy_name)
                    engine.update_strategy_performance(strategy, score=0.6)

        # Create mutation guidance with out-of-range bias
        mutation_guidance = {
            'strategy_biases': {
                'lexical_variation': 0.5,  # Too high (> MAX_POSITIVE_BIAS)
                'context_injection': -0.8  # Too low (< MAX_NEGATIVE_BIAS)
            },
            'behavioral_traits': {}
        }

        # Run mutation with guidance
        _ = engine.mutate(prompt, mutation_guidance=mutation_guidance)

        # Check selection_history for clamped values
        if hasattr(engine, 'selection_history') and \
           len(engine.selection_history) > 0:
            log_entry = engine.selection_history[-1]

            # Find the candidates with biases
            for candidate in log_entry['candidates']:
                if candidate['strategy'] == 'lexical_variation':
                    # Should be clamped to MAX_POSITIVE_BIAS
                    assert candidate['behavior_bias'] <= MAX_POSITIVE_BIAS
                elif candidate['strategy'] == 'context_injection':
                    # Should be clamped to MAX_NEGATIVE_BIAS
                    assert candidate['behavior_bias'] >= MAX_NEGATIVE_BIAS

    def test_weight_decomposition(self):
        """Test that weight_without_behavior is correctly computed."""
        engine = MutationEngine(random_seed=42, min_samples_for_adaptive=5)
        engine.enable_adaptive_mode()

        # Build up some performance history first
        prompt = "Test prompt"
        for i in range(10):
            _ = engine.mutate(prompt)
            if engine.mutation_history:
                last_mutation = engine.mutation_history[-1]
                strategy_name = last_mutation['strategy']
                if strategy_name != 'no-op':
                    strategy = MutationStrategy(strategy_name)
                    engine.update_strategy_performance(strategy, score=0.6)

        # Create mutation guidance with biases
        mutation_guidance = {
            'strategy_biases': {
                'lexical_variation': 0.2
            },
            'behavioral_traits': {}
        }

        # Run mutation
        _ = engine.mutate(prompt, mutation_guidance=mutation_guidance)

        # Check weight decomposition
        if hasattr(engine, 'selection_history') and \
           len(engine.selection_history) > 0:
            log_entry = engine.selection_history[-1]

            for candidate in log_entry['candidates']:
                # weight_without_behavior should be final_weight minus
                # behavior_bias (with floor of 0.1 applied)
                expected = max(
                    0.1,
                    candidate['final_weight'] - candidate['behavior_bias']
                )
                assert abs(
                    candidate['weight_without_behavior'] - expected
                ) < 1e-6

    def test_probability_sum(self):
        """Test that probabilities sum to 1.0."""
        engine = MutationEngine(random_seed=42, min_samples_for_adaptive=5)
        engine.enable_adaptive_mode()

        # Run some mutations
        prompt = "Test prompt"
        for i in range(10):
            _ = engine.mutate(prompt)
            if engine.mutation_history:
                last_mutation = engine.mutation_history[-1]
                strategy_name = last_mutation['strategy']
                if strategy_name != 'no-op':
                    strategy = MutationStrategy(strategy_name)
                    engine.update_strategy_performance(strategy, score=0.6)

        # Verify probabilities sum to 1.0 in each log entry
        if hasattr(engine, 'selection_history'):
            for log_entry in engine.selection_history:
                total_prob = sum(c['probability']
                                 for c in log_entry['candidates'])
                assert abs(total_prob - 1.0) < 1e-6

    def test_trait_confidence_constants(self):
        """Test that TRAIT_CONFIDENCE constants are defined."""
        assert 'verbosity' in TRAIT_CONFIDENCE
        assert 'complexity' in TRAIT_CONFIDENCE
        assert 'directness' in TRAIT_CONFIDENCE

        # Verify values are in reasonable range
        assert 0 < TRAIT_CONFIDENCE['verbosity'] <= 1.0
        assert 0 < TRAIT_CONFIDENCE['complexity'] <= 1.0
        assert 0 < TRAIT_CONFIDENCE['directness'] <= 1.0

        # Verify verbosity has highest confidence
        assert TRAIT_CONFIDENCE['verbosity'] >= TRAIT_CONFIDENCE['complexity']
        assert TRAIT_CONFIDENCE['verbosity'] >= TRAIT_CONFIDENCE['directness']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
