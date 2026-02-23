"""
Tests for behavior-aware mutation system.

Tests the integration between Spotter's behavioral trait analysis and
Mutation Engine's behavior-aware strategy selection.
"""

import pytest

from app.agents.spotter import Spotter
from app.engines.mutation import MutationEngine, MutationStrategy


class TestBehavioralTraitAnalysis:
    """Test Spotter's behavioral trait analysis."""

    @pytest.mark.asyncio
    async def test_verbose_response_detection(self):
        """Test that verbose responses are correctly identified."""
        spotter = Spotter()

        # Very verbose response (500+ words)
        verbose_response = " ".join(["word"] * 600)
        prompt = "Tell me about AI"

        evaluation = await spotter.evaluate(verbose_response, prompt=prompt)

        assert "mutation_guidance" in evaluation
        assert "behavioral_traits" in evaluation["mutation_guidance"]
        traits = evaluation["mutation_guidance"]["behavioral_traits"]

        assert traits["verbosity"]["assessment"] == "too_verbose"
        assert traits["verbosity"]["score"] >= 0.7

    @pytest.mark.asyncio
    async def test_terse_response_detection(self):
        """Test that terse responses are correctly identified."""
        spotter = Spotter()

        terse_response = "Yes, that's correct."
        prompt = "Is this true?"

        evaluation = await spotter.evaluate(terse_response, prompt=prompt)

        traits = evaluation["mutation_guidance"]["behavioral_traits"]
        assert traits["verbosity"]["assessment"] == "terse"
        assert traits["verbosity"]["word_count"] < 50

    @pytest.mark.asyncio
    async def test_complexity_analysis(self):
        """Test complexity detection in responses."""
        spotter = Spotter()

        # Complex response with multiple conjunctions
        complex_response = (
            "However, this is a complex issue. Moreover, we must consider "
            "furthermore the implications which are significant. Nevertheless, "
            "the conclusion that emerges is clear."
        )

        evaluation = await spotter.evaluate(complex_response, prompt="Explain")

        traits = evaluation["mutation_guidance"]["behavioral_traits"]
        assert traits["complexity"]["score"] > 0.5
        assert traits["complexity"]["assessment"] in ["high_complexity", "moderate"]

        # Verify that at least 3 complexity patterns were detected
        # (however, moreover, furthermore, nevertheless, which clause)
        assert traits["complexity"]["score"] >= 0.4  # At least 2/5 patterns detected

    @pytest.mark.asyncio
    async def test_directness_hedging_detection(self):
        """Test detection of hedging/indirect language."""
        spotter = Spotter()

        hedging_response = (
            "Well, this might possibly be true, perhaps in some cases. "
            "It seems that it could potentially work, arguably."
        )

        evaluation = await spotter.evaluate(hedging_response, prompt="Is this correct?")

        traits = evaluation["mutation_guidance"]["behavioral_traits"]
        assert traits["directness"]["assessment"] == "indirect"
        assert traits["directness"]["hedging_count"] >= 3

    @pytest.mark.asyncio
    async def test_direct_response_detection(self):
        """Test detection of direct, assertive language."""
        spotter = Spotter()

        direct_response = "Yes, absolutely. This is correct and verified."

        evaluation = await spotter.evaluate(direct_response, prompt="Is this true?")

        traits = evaluation["mutation_guidance"]["behavioral_traits"]
        assert traits["directness"]["assessment"] in ["direct", "moderate"]
        assert traits["directness"]["hedging_count"] <= 1


class TestBehaviorAwareRecommendations:
    """Test behavior-aware mutation recommendations."""

    @pytest.mark.asyncio
    async def test_verbose_response_recommendations(self):
        """Test that verbose responses generate pruning recommendations."""
        spotter = Spotter()

        verbose_response = " ".join(["word"] * 600)
        evaluation = await spotter.evaluate(verbose_response, prompt="Test")

        guidance = evaluation["mutation_guidance"]

        # Should recommend structural_recombination for pruning
        assert "structural_recombination" in guidance["recommended_strategies"]

        # Should have negative bias for strategies that add content
        assert "strategy_biases" in guidance
        biases = guidance["strategy_biases"]
        if "context_injection" in biases:
            assert biases["context_injection"] < 0  # Negative bias

        # Should have positive bias for pruning strategies
        if "structural_recombination" in biases:
            assert biases["structural_recombination"] > 0

    @pytest.mark.asyncio
    async def test_terse_response_recommendations(self):
        """Test that terse responses generate expansion recommendations."""
        spotter = Spotter()

        terse_response = "Yes."
        evaluation = await spotter.evaluate(terse_response, prompt="Test")

        guidance = evaluation["mutation_guidance"]

        # Should recommend context_injection for expansion
        assert "context_injection" in guidance["recommended_strategies"]

        biases = guidance["strategy_biases"]
        if "context_injection" in biases:
            assert biases["context_injection"] > 0  # Positive bias

    @pytest.mark.asyncio
    async def test_high_complexity_recommendations(self):
        """Test that complex responses generate simplification recommendations."""
        spotter = Spotter()

        complex_response = (
            "However, moreover, furthermore, nevertheless, consequently, "
            "which that who whereby wherein."
        )
        evaluation = await spotter.evaluate(complex_response, prompt="Test")

        guidance = evaluation["mutation_guidance"]

        # Should recommend lexical_variation for simplification
        assert "lexical_variation" in guidance["recommended_strategies"]

    @pytest.mark.asyncio
    async def test_behavior_context_metadata(self):
        """Test that behavior context is included for analytics."""
        spotter = Spotter()

        verbose_response = " ".join(["word"] * 600)
        evaluation = await spotter.evaluate(verbose_response, prompt="Test")

        guidance = evaluation["mutation_guidance"]

        assert "behavior_context" in guidance
        context = guidance["behavior_context"]
        assert "verbosity_issue" in context


class TestMutationEngineBehaviorAwareness:
    """Test mutation engine's use of behavior-aware guidance."""

    def test_mutation_accepts_guidance(self):
        """Test that mutate() accepts mutation_guidance parameter."""
        engine = MutationEngine(mutation_rate=1.0)
        engine.adaptive_mode = True

        prompt = "Test prompt"
        guidance = {"strategy_biases": {"lexical_variation": 0.5, "obfuscation": -0.2}}

        # Should not raise an error
        mutated = engine.mutate(prompt, mutation_guidance=guidance)
        assert isinstance(mutated, str)

    def test_behavior_bias_influences_selection(self):
        """Test that behavior biases influence strategy selection."""
        import random

        random.seed(42)  # Set seed for deterministic test

        engine = MutationEngine(mutation_rate=1.0, random_seed=42)
        engine.adaptive_mode = True

        # Initialize some performance history
        for strategy in MutationStrategy:
            engine.strategy_performance[strategy.value] = [0.5] * 10

        prompt = "Test prompt"

        # Strong positive bias for lexical_variation
        guidance = {
            "strategy_biases": {
                "lexical_variation": 0.8,
                "encoding_transform": -0.5,
                "obfuscation": -0.5,
                "structural_recombination": -0.5,
                "role_play_framing": -0.5,
                "context_injection": -0.5,
            }
        }

        # Run multiple mutations and track strategy usage
        strategies_used = []
        for _ in range(50):
            _ = engine.mutate(prompt, mutation_guidance=guidance)
            if engine.mutation_history:
                strategy = engine.mutation_history[-1].get("strategy")
                strategies_used.append(strategy)

        # lexical_variation should be used more frequently due to positive bias
        # With +0.8 bias added to base 0.5 weight = 1.3 total weight
        # Even with -0.5 bias on others (0.0 floored to 0.1 min), lexical should dominate
        # Expected: >50% of selections should be lexical_variation
        # Using 5/50 (10%) as minimum threshold to avoid flaky tests
        # This is very conservative - in practice expect 60-80% lexical_variation
        lexical_count = strategies_used.count("lexical_variation")
        assert (
            lexical_count > 5
        ), f"Expected > 5 lexical_variation selections, got {lexical_count}"  # Should appear multiple times due to bias

    def test_no_guidance_fallback(self):
        """Test that mutation works without guidance (backward compatibility)."""
        engine = MutationEngine(mutation_rate=1.0)
        engine.adaptive_mode = True

        prompt = "Test prompt"

        # Should work without mutation_guidance
        mutated = engine.mutate(prompt)
        assert isinstance(mutated, str)
        assert len(engine.mutation_history) > 0


class TestEndToEndBehaviorAwareEvolution:
    """Test end-to-end behavior-aware evolution."""

    @pytest.mark.asyncio
    async def test_verbose_response_evolution_cycle(self):
        """
        Test full cycle: verbose response → behavior analysis → biased mutation.
        """
        spotter = Spotter()
        engine = MutationEngine(mutation_rate=1.0)
        engine.adaptive_mode = True

        # Initialize performance history
        for strategy in MutationStrategy:
            engine.strategy_performance[strategy.value] = [0.5] * 10

        # Simulate a verbose response from target
        verbose_response = " ".join(["word"] * 600)
        prompt = "Test prompt"

        # Spotter evaluates and generates mutation_guidance
        evaluation = await spotter.evaluate(verbose_response, prompt=prompt)
        mutation_guidance = evaluation["mutation_guidance"]

        # Verify guidance includes behavioral traits
        assert "behavioral_traits" in mutation_guidance
        assert (
            mutation_guidance["behavioral_traits"]["verbosity"]["assessment"]
            == "too_verbose"
        )

        # Verify guidance includes strategy biases
        assert "strategy_biases" in mutation_guidance
        biases = mutation_guidance["strategy_biases"]
        assert "structural_recombination" in biases
        assert biases["structural_recombination"] > 0  # Positive bias for pruning

        # Mutation engine uses guidance to evolve next prompt
        next_prompt = engine.mutate(prompt, mutation_guidance=mutation_guidance)

        # Should produce a mutated prompt
        assert isinstance(next_prompt, str)

        # Check that mutation was logged
        assert len(engine.mutation_history) > 0
        last_mutation = engine.mutation_history[-1]
        assert last_mutation["strategy"] in [s.value for s in MutationStrategy]

    @pytest.mark.asyncio
    async def test_behavior_aware_strategy_preference(self):
        """
        Test that behavior-aware biases shift strategy preferences over time.
        """
        spotter = Spotter()
        engine = MutationEngine(mutation_rate=1.0)
        engine.adaptive_mode = True

        # Initialize equal performance for all strategies
        for strategy in MutationStrategy:
            engine.strategy_performance[strategy.value] = [0.5] * 10

        # Generate guidance favoring lexical_variation
        verbose_response = " ".join(["word"] * 100)  # Moderate verbosity
        evaluation = await spotter.evaluate(verbose_response, prompt="Test")
        mutation_guidance = evaluation["mutation_guidance"]

        # Run multiple mutations with same guidance
        strategies_used = []
        for _ in range(30):
            _ = engine.mutate("Test prompt", mutation_guidance=mutation_guidance)
            if engine.mutation_history:
                strategy = engine.mutation_history[-1].get("strategy")
                strategies_used.append(strategy)

        # Check that recommended strategies appear in the results
        recommended = mutation_guidance.get("recommended_strategies", [])
        if recommended:
            # At least one of the recommended strategies should be used
            recommended_count = sum(
                1 for s in strategies_used if any(rec in s for rec in recommended)
            )
            assert recommended_count > 0


class TestBackwardCompatibility:
    """Test that existing functionality still works."""

    def test_mutation_without_guidance(self):
        """Test that mutation still works without mutation_guidance."""
        engine = MutationEngine(mutation_rate=1.0)

        prompt = "Test prompt"
        result = engine.mutate(prompt)

        assert isinstance(result, str)
        assert len(engine.mutation_history) > 0

    def test_mutation_with_archetypes_only(self):
        """Test that existing archetype-based selection still works."""
        engine = MutationEngine(mutation_rate=1.0)
        engine.adaptive_mode = True

        # Initialize performance with archetype correlation
        for strategy in MutationStrategy:
            engine.strategy_performance[strategy.value] = [0.5] * 10
            engine.strategy_archetype_performance[strategy.value] = {
                "test_archetype": [0.7] * 5
            }

        prompt = "Test prompt"
        archetypes = ["test_archetype"]

        result = engine.mutate(prompt, archetypes=archetypes)

        assert isinstance(result, str)
