"""
Tests for Spotter code quality improvements:
- Import statements (math module)
- State initialization (_archetype_frequency, _pattern_history)
- Empty archetype handling in saturation score
- Consistent .get() usage in failure explanations
"""

from app.agents.spotter import Spotter
from app.engines.scoring import FailureArchetype


class TestSpotterInitialization:
    """Test that Spotter initializes state correctly."""

    def test_archetype_frequency_initialized(self):
        """Test that _archetype_frequency is initialized as empty dict."""
        spotter = Spotter()
        assert hasattr(spotter, "_archetype_frequency")
        assert isinstance(spotter._archetype_frequency, dict)
        assert len(spotter._archetype_frequency) == 0

    def test_pattern_history_initialized(self):
        """Test that _pattern_history is initialized as empty list."""
        spotter = Spotter()
        assert hasattr(spotter, "_pattern_history")
        assert isinstance(spotter._pattern_history, list)
        assert len(spotter._pattern_history) == 0

    def test_pattern_drift_tracking_enabled_by_default(self):
        """Test that pattern drift tracking is enabled by default."""
        spotter = Spotter()
        assert spotter.enable_pattern_drift_tracking is True

    def test_pattern_drift_tracking_can_be_disabled(self):
        """Test that pattern drift tracking can be disabled."""
        spotter = Spotter(enable_pattern_drift_tracking=False)
        assert spotter.enable_pattern_drift_tracking is False


class TestPatternDriftEmptyArchetypes:
    """Test handling of empty archetypes in pattern drift tracking."""

    def test_empty_archetypes_saturation_score(self):
        """Test that empty archetypes result in 0.0 saturation score."""
        spotter = Spotter(enable_pattern_drift_tracking=True)

        # Simulate multiple evaluations with empty archetypes
        for _ in range(10):
            drift_result = spotter._track_pattern_drift(archetypes=[], indicators={})

        # With all empty archetypes, saturation should be 0.0
        assert drift_result["saturation_score"] == 0.0
        assert drift_result["recommendation"] in [
            "continue",
            "healthy_continue_current_strategy",
        ]

    def test_mixed_empty_and_nonempty_archetypes(self):
        """Test saturation with mix of empty and non-empty archetypes."""
        spotter = Spotter(enable_pattern_drift_tracking=True)

        # Mix of empty and non-empty archetypes
        for i in range(10):
            if i % 2 == 0:
                archetypes = []
            else:
                archetypes = [FailureArchetype.POLICY_EROSION]

            drift_result = spotter._track_pattern_drift(
                archetypes=archetypes, indicators={}
            )

        # Should have non-zero saturation due to varied patterns
        assert drift_result["saturation_score"] > 0.0
        assert "saturation_score" in drift_result
        assert "diversity_score" in drift_result

    def test_all_same_nonempty_archetypes(self):
        """Test high saturation with repeated non-empty archetypes."""
        spotter = Spotter(enable_pattern_drift_tracking=True)

        # All same archetype (high saturation)
        for _ in range(10):
            drift_result = spotter._track_pattern_drift(
                archetypes=[FailureArchetype.POLICY_EROSION], indicators={}
            )

        # Should have high saturation (all patterns the same)
        assert drift_result["saturation_score"] > 0.5
        assert (
            "high_saturation" in drift_result["recommendation"]
            or "moderate_saturation" in drift_result["recommendation"]
        )

    def test_diverse_archetypes_low_saturation(self):
        """Test low saturation with diverse archetypes."""
        spotter = Spotter(enable_pattern_drift_tracking=True)

        # Ensure we have enough history
        for _ in range(5):
            spotter._track_pattern_drift(archetypes=[], indicators={})

        # Different archetype each time (low saturation)
        # Use as many unique archetypes as possible
        archetypes_list = [
            [FailureArchetype.POLICY_EROSION],
            [FailureArchetype.ROLE_CONFUSION],
            [FailureArchetype.MISPLACED_HELPFULNESS],
            [FailureArchetype.FALSE_AUTHORITY],
            [FailureArchetype.HIDDEN_COMPLIANCE],
            [FailureArchetype.REFUSAL_COLLAPSE],
            # Alternate combinations for variety
            [FailureArchetype.POLICY_EROSION, FailureArchetype.ROLE_CONFUSION],
            [FailureArchetype.MISPLACED_HELPFULNESS, FailureArchetype.FALSE_AUTHORITY],
            [FailureArchetype.HIDDEN_COMPLIANCE, FailureArchetype.REFUSAL_COLLAPSE],
            [],  # Empty for variety
        ]

        for archetypes in archetypes_list:
            drift_result = spotter._track_pattern_drift(
                archetypes=archetypes, indicators={}
            )

        # Should have low saturation (varied patterns)
        assert drift_result["saturation_score"] < 0.5


class TestFailureExplanationConsistency:
    """Test that failure explanation handles missing indicators gracefully."""

    def test_explanation_with_missing_indicators(self):
        """Test that failure explanation works when indicators key is missing."""
        spotter = Spotter()

        # Create result dicts without 'indicators' key
        l1_result = {"score": 0.6}
        l2_result = {"score": 0.7}
        l3_result = {"score": 0.8}
        archetypes = [FailureArchetype.POLICY_EROSION]

        # Should not raise KeyError
        explanation = spotter._generate_failure_explanation(
            l1_result, l2_result, l3_result, archetypes
        )

        assert isinstance(explanation, str)
        assert "Failure Archetypes" in explanation

    def test_explanation_with_empty_indicators(self):
        """Test that failure explanation works with empty indicators dict."""
        spotter = Spotter()

        # Create result dicts with empty indicators
        l1_result = {"score": 0.6, "indicators": {}}
        l2_result = {"score": 0.7, "indicators": {}}
        l3_result = {"score": 0.8, "indicators": {}}
        archetypes = []

        explanation = spotter._generate_failure_explanation(
            l1_result, l2_result, l3_result, archetypes
        )

        assert isinstance(explanation, str)

    def test_explanation_with_valid_indicators(self):
        """Test that failure explanation includes indicator details."""
        spotter = Spotter()

        # Create result dicts with valid indicators
        l1_result = {
            "score": 0.6,
            "indicators": {"hate_speech": True, "pii_leakage": False},
        }
        l2_result = {"score": 0.7, "indicators": {"prompt_injection": True}}
        l3_result = {"score": 0.4, "indicators": {}}
        archetypes = [FailureArchetype.POLICY_EROSION]

        explanation = spotter._generate_failure_explanation(
            l1_result, l2_result, l3_result, archetypes
        )

        assert isinstance(explanation, str)
        assert "L1 (Linguistic)" in explanation
        assert "hate speech" in explanation
        assert "L2 (Security)" in explanation
        assert "prompt injection" in explanation
        # L3 score is 0.4, below 0.5 threshold, so should not appear in explanation
        assert "L3 (Cognitive)" not in explanation


class TestMathImport:
    """Test that math module is properly imported and used."""

    def test_math_log2_available(self):
        """Test that math.log2 is available for entropy calculation."""
        spotter = Spotter(enable_pattern_drift_tracking=True)

        # Add diverse archetypes to trigger entropy calculation
        for i in range(10):
            archetype = [
                FailureArchetype.POLICY_EROSION,
                FailureArchetype.ROLE_CONFUSION,
            ][i % 2]
            spotter._track_pattern_drift(archetypes=[archetype], indicators={})

        # Should successfully calculate diversity score using math.log2
        drift_result = spotter._track_pattern_drift(
            archetypes=[FailureArchetype.HIDDEN_COMPLIANCE], indicators={}
        )

        assert "diversity_score" in drift_result
        assert 0.0 <= drift_result["diversity_score"] <= 1.0


class TestPatternDriftRecommendations:
    """Test that pattern drift generates appropriate recommendations."""

    def test_recommendation_with_insufficient_data(self):
        """Test recommendation when there's insufficient data."""
        spotter = Spotter(enable_pattern_drift_tracking=True)

        # Only 3 evaluations (less than 5)
        for _ in range(3):
            drift_result = spotter._track_pattern_drift(
                archetypes=[FailureArchetype.POLICY_EROSION], indicators={}
            )

        assert drift_result["recommendation"] == "continue"
        assert drift_result["recent_window_size"] == 3

    def test_high_saturation_recommendation(self):
        """Test that high saturation triggers appropriate recommendation."""
        spotter = Spotter(enable_pattern_drift_tracking=True)

        # Build up history with same archetype
        for _ in range(12):
            drift_result = spotter._track_pattern_drift(
                archetypes=[FailureArchetype.POLICY_EROSION], indicators={}
            )

        # High saturation should recommend exploration
        assert drift_result["saturation_score"] > 0.7
        assert "high_saturation" in drift_result["recommendation"]

    def test_healthy_diverse_patterns(self):
        """Test that diverse patterns result in healthy recommendation."""
        spotter = Spotter(enable_pattern_drift_tracking=True)

        # Build sufficient history first
        for _ in range(5):
            spotter._track_pattern_drift(archetypes=[], indicators={})

        # Add diverse patterns
        archetypes_cycle = [
            FailureArchetype.POLICY_EROSION,
            FailureArchetype.ROLE_CONFUSION,
            FailureArchetype.MISPLACED_HELPFULNESS,
            FailureArchetype.FALSE_AUTHORITY,
            FailureArchetype.HIDDEN_COMPLIANCE,
        ]

        for i in range(10):
            drift_result = spotter._track_pattern_drift(
                archetypes=[archetypes_cycle[i % len(archetypes_cycle)]], indicators={}
            )

        # Should have healthy diversity
        assert drift_result["diversity_score"] > 0.3
