"""
Tests for structured feedback flow and StateManager evolution analytics.

These tests validate the improvements made to address the problem statement:
- Sniper receives structured feedback, not just scalar scores
- StateManager actively helps evolution with analytics methods
- Batch coherence tracking for parallel evolution mode
"""

import os
import tempfile
from typing import Any, Dict

import pytest

from app.agents.orchestrator import RoundResult, StateManager
from app.agents.sniper import Sniper
from app.engines.mutation import MutationEngine
from app.engines.selection import SelectionEngine, SelectionStrategy


@pytest.fixture
def temp_db():
    """Create a temporary database file for testing."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    # Cleanup
    try:
        os.unlink(path)
    except Exception:
        pass


@pytest.fixture
def state_manager(temp_db):
    """Create a StateManager for testing."""
    return StateManager(
        database_path=temp_db,
        zero_retention=False,
        model_version="test-model-v1",  # Don't delete during tests
    )


@pytest.fixture
def sniper():
    """Create a Sniper agent for testing."""
    mutation_engine = MutationEngine(mutation_rate=0.7)
    selection_engine = SelectionEngine(
        decay_rate=0.95, novelty_weight=0.3, diversity_weight=0.2
    )
    return Sniper(
        mutation_engine=mutation_engine,
        selection_engine=selection_engine,
        selection_strategy=SelectionStrategy.HYBRID,
        evolution_pool_size=10,
    )


def create_mock_evaluation(
    l1_score: float, l2_score: float, l3_score: float
) -> Dict[str, Any]:
    """Create a mock evaluation structure from Spotter."""
    return {
        "l1": {
            "score": l1_score,
            "indicators": {"refusal_degradation": {"detected": False}},
            "rationale": "L1 evaluation",
        },
        "l2": {
            "score": l2_score,
            "indicators": {"sql_injection": {"detected": True}},
            "rationale": "L2 evaluation",
        },
        "l3": {
            "score": l3_score,
            "indicators": {"identity_confusion": {"detected": False}},
            "rationale": "L3 evaluation",
        },
        "axes": {
            "safety_degradation": 0.5,
            "exploitation_potential": 0.7,
            "cognitive_manipulation": 0.3,
        },
        "mutation_guidance": {
            "intensify": ["security_exploitation"],
            "diversify": ["cognitive_tactics"],
            "abandon": [],
        },
        "metadata": {
            "attack_domain": "prompt_injection",
            "evaluation_id": 1,
            "confidence_threshold": 0.6,
        },
    }


class TestStructuredFeedbackFlow:
    """Test that Sniper receives and stores structured feedback."""

    def test_sniper_accepts_structured_feedback(self, sniper):
        """Test that Sniper can receive structured feedback."""
        # Generate a prompt to add to evolution pool
        prompt, domain = sniper._generate_prompt_sync()

        # Create structured feedback
        structured_feedback = create_mock_evaluation(0.5, 0.7, 0.6)

        # Update with structured feedback
        sniper.update_prompt_score(
            prompt, score=0.65, structured_feedback=structured_feedback
        )

        # Verify feedback was stored
        for candidate in sniper.evolution_pool:
            if candidate.prompt == prompt:
                assert hasattr(candidate, "feedback_history")
                assert len(candidate.feedback_history) == 1
                assert candidate.feedback_history[0] == structured_feedback
                break
        else:
            pytest.fail("Prompt not found in evolution pool")

    def test_structured_feedback_accumulates(self, sniper):
        """Test that structured feedback accumulates over multiple updates."""
        prompt, domain = sniper._generate_prompt_sync()

        # Add multiple feedback entries
        for i in range(5):
            feedback = create_mock_evaluation(
                0.3 + i * 0.1, 0.4 + i * 0.1, 0.5 + i * 0.1
            )
            sniper.update_prompt_score(
                prompt, score=0.5 + i * 0.05, structured_feedback=feedback
            )

        # Verify only last 3 are kept
        for candidate in sniper.evolution_pool:
            if candidate.prompt == prompt:
                assert len(candidate.feedback_history) == 3
                # Most recent should be last
                assert candidate.feedback_history[-1]["l1"]["score"] == pytest.approx(
                    0.7
                )
                break

    def test_backward_compatibility_without_feedback(self, sniper):
        """Test that update_prompt_score still works without structured feedback."""
        prompt, domain = sniper._generate_prompt_sync()

        # Update without structured feedback (backward compatibility)
        sniper.update_prompt_score(prompt, score=0.75)

        # Verify it works without errors
        for candidate in sniper.evolution_pool:
            if candidate.prompt == prompt:
                assert candidate.score == 0.75
                break

    def test_structured_feedback_contains_mutation_guidance(self, sniper):
        """Test that structured feedback includes mutation guidance."""
        prompt, domain = sniper._generate_prompt_sync()

        feedback = create_mock_evaluation(0.6, 0.8, 0.5)
        sniper.update_prompt_score(prompt, score=0.7, structured_feedback=feedback)

        # Verify mutation guidance is present
        for candidate in sniper.evolution_pool:
            if candidate.prompt == prompt:
                assert "mutation_guidance" in candidate.feedback_history[0]
                guidance = candidate.feedback_history[0]["mutation_guidance"]
                assert "intensify" in guidance
                assert "diversify" in guidance
                assert "abandon" in guidance
                break


class TestStateManagerEvolutionAnalytics:
    """Test StateManager evolution analytics methods."""

    def test_get_high_performing_patterns(self, state_manager):
        """Test retrieval of high-performing patterns."""
        # Create some test rounds with varying scores
        test_rounds = [
            RoundResult(
                round_number=i,
                prompt=f"test prompt {i}",
                attack_domain="prompt_injection",
                target_response="response",
                evaluation=create_mock_evaluation(0.5, 0.6, 0.7),
                global_score=0.3 + i * 0.1,
                blocked_by_egg=False,
                timestamp="2024-01-01T00:00:00Z",
                model_version="test-v1",
            )
            for i in range(10)
        ]

        # Save rounds
        for round_result in test_rounds:
            state_manager.save_round(round_result)

        # Get high performers (threshold 0.6 means rounds 4-9)
        high_performers = state_manager.get_high_performing_patterns(
            threshold=0.6, limit=5
        )

        assert len(high_performers) == 5  # Limited to 5
        assert all(p["score"] >= 0.6 for p in high_performers)
        # Should be ordered by score descending
        assert high_performers[0]["score"] >= high_performers[-1]["score"]

    def test_get_underexplored_domains(self, state_manager):
        """Test identification of underexplored attack domains."""
        # Create rounds with uneven domain distribution
        domains_and_counts = [
            ("prompt_injection", 10),
            ("jailbreak", 5),
            ("pii_extraction", 2),
        ]

        round_num = 1
        for domain, count in domains_and_counts:
            for _ in range(count):
                round_result = RoundResult(
                    round_number=round_num,
                    prompt=f"test prompt {round_num}",
                    attack_domain=domain,
                    target_response="response",
                    evaluation=create_mock_evaluation(0.5, 0.6, 0.7),
                    global_score=0.5,
                    blocked_by_egg=False,
                    timestamp="2024-01-01T00:00:00Z",
                )
                state_manager.save_round(round_result)
                round_num += 1

        # Get underexplored domains
        underexplored = state_manager.get_underexplored_domains()

        assert len(underexplored) == 3
        # pii_extraction should have highest exploration priority (fewest attempts)
        pii_domain = next(d for d in underexplored if d["domain"] == "pii_extraction")
        assert pii_domain["attempts"] == 2
        assert pii_domain["exploration_priority"] > 0.3  # 1/(2+1) = 0.33

    def test_get_evolution_analytics_comprehensive(self, state_manager):
        """Test comprehensive evolution analytics."""
        # Create rounds showing evolution progress
        for i in range(20):
            score = 0.3 + (i * 0.02)  # Gradually improving scores
            round_result = RoundResult(
                round_number=i + 1,
                prompt=f"test prompt {i}",
                attack_domain=["prompt_injection", "jailbreak"][i % 2],
                target_response="response",
                evaluation=create_mock_evaluation(score, score, score),
                global_score=score,
                blocked_by_egg=False,
                timestamp="2024-01-01T00:00:00Z",
            )
            state_manager.save_round(round_result)

        # Get comprehensive analytics
        analytics = state_manager.get_evolution_analytics()

        assert "high_performers" in analytics
        assert "underexplored_domains" in analytics
        assert "score_trend" in analytics
        assert "total_patterns" in analytics

        # Verify positive trend (scores improving)
        assert analytics["score_trend"] > 0
        assert analytics["total_patterns"] == 20

    def test_analyze_batch_coherence_high_diversity(self, state_manager):
        """Test batch coherence analysis with diverse domains."""
        # Create a diverse batch
        domains = ["prompt_injection", "jailbreak", "pii_extraction", "refusal_erosion"]
        for i, domain in enumerate(domains):
            round_result = RoundResult(
                round_number=i + 1,
                prompt=f"test prompt {i}",
                attack_domain=domain,
                target_response="response",
                evaluation=create_mock_evaluation(0.5, 0.6, 0.7),
                global_score=0.6,
                blocked_by_egg=False,
                timestamp="2024-01-01T00:00:00Z",
            )
            state_manager.save_round(round_result)

        # Analyze batch coherence
        coherence = state_manager.analyze_batch_coherence([1, 2, 3, 4])

        assert coherence["batch_size"] == 4
        assert coherence["unique_domains"] == 4
        assert coherence["diversity_score"] == 1.0  # All unique
        assert coherence["coherence_score"] > 0.9  # Scores are consistent

    def test_analyze_batch_coherence_low_diversity(self, state_manager):
        """Test batch coherence analysis with repetitive domains."""
        # Create a batch with same domain
        for i in range(5):
            round_result = RoundResult(
                round_number=i + 1,
                prompt=f"test prompt {i}",
                attack_domain="prompt_injection",
                target_response="response",
                evaluation=create_mock_evaluation(0.5, 0.6, 0.7),
                global_score=0.5 + i * 0.1,  # Varying scores
                blocked_by_egg=False,
                timestamp="2024-01-01T00:00:00Z",
            )
            state_manager.save_round(round_result)

        # Analyze batch coherence
        coherence = state_manager.analyze_batch_coherence([1, 2, 3, 4, 5])

        assert coherence["batch_size"] == 5
        assert coherence["unique_domains"] == 1
        assert coherence["diversity_score"] == pytest.approx(0.2)  # 1/5
        assert coherence["score_std"] > 0  # Scores vary

    def test_analyze_batch_coherence_empty_batch(self, state_manager):
        """Test batch coherence analysis with empty batch."""
        coherence = state_manager.analyze_batch_coherence([])

        assert coherence["coherence_score"] == 0.0
        assert coherence["diversity_score"] == 0.0


class TestEvolutionModeImprovements:
    """Test that evolution mode improvements work correctly."""

    def test_batch_coherence_metrics_available(self, state_manager):
        """Test that batch coherence metrics are computed correctly."""
        # Create a batch with mixed performance
        test_data = [
            (1, "prompt_injection", 0.8),
            (2, "jailbreak", 0.5),
            (3, "prompt_injection", 0.7),
            (4, "pii_extraction", 0.6),
        ]

        for round_num, domain, score in test_data:
            round_result = RoundResult(
                round_number=round_num,
                prompt=f"test prompt {round_num}",
                attack_domain=domain,
                target_response="response",
                evaluation=create_mock_evaluation(score, score, score),
                global_score=score,
                blocked_by_egg=False,
                timestamp="2024-01-01T00:00:00Z",
            )
            state_manager.save_round(round_result)

        # Analyze coherence
        coherence = state_manager.analyze_batch_coherence([1, 2, 3, 4])

        # Verify all expected metrics are present
        assert "coherence_score" in coherence
        assert "diversity_score" in coherence
        assert "batch_size" in coherence
        assert "unique_domains" in coherence
        assert "avg_score" in coherence
        assert "score_std" in coherence

        assert coherence["batch_size"] == 4
        assert coherence["unique_domains"] == 3
        assert coherence["avg_score"] == pytest.approx(0.65)

    def test_evolution_analytics_guides_domain_selection(self, state_manager):
        """Test that evolution analytics can guide domain selection."""
        # Create unbalanced domain exploration
        for i in range(15):
            domain = "prompt_injection" if i < 12 else "jailbreak"
            round_result = RoundResult(
                round_number=i + 1,
                prompt=f"test prompt {i}",
                attack_domain=domain,
                target_response="response",
                evaluation=create_mock_evaluation(0.5, 0.6, 0.7),
                global_score=0.6,
                blocked_by_egg=False,
                timestamp="2024-01-01T00:00:00Z",
            )
            state_manager.save_round(round_result)

        # Get underexplored domains
        underexplored = state_manager.get_underexplored_domains()

        # jailbreak should be flagged as underexplored
        jailbreak = next(d for d in underexplored if d["domain"] == "jailbreak")
        prompt_inj = next(d for d in underexplored if d["domain"] == "prompt_injection")

        # jailbreak should have higher exploration priority
        assert jailbreak["exploration_priority"] > prompt_inj["exploration_priority"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
