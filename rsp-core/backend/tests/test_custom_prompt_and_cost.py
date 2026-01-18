"""
Tests for custom prompt execution and cost tracking functionality.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from app.agents.orchestrator import Orchestrator
from app.core.cost_tracking import (
    CostTracker, TokenUsage, CostEstimate,
    estimate_tokens_from_text, estimate_cost_from_text
)


class TestCostTracking:
    """Test cost tracking utilities."""

    def test_token_usage_creation(self):
        """Test TokenUsage dataclass creation."""
        usage = TokenUsage(
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150
        )
        assert usage.prompt_tokens == 100
        assert usage.completion_tokens == 50
        assert usage.total_tokens == 150

    def test_token_usage_to_dict(self):
        """Test TokenUsage to_dict conversion."""
        usage = TokenUsage(
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150
        )
        result = usage.to_dict()
        assert result["prompt_tokens"] == 100
        assert result["completion_tokens"] == 50
        assert result["total_tokens"] == 150

    def test_cost_estimate_creation(self):
        """Test CostEstimate dataclass creation."""
        usage = TokenUsage(100, 50, 150)
        estimate = CostEstimate(
            prompt_cost=0.001,
            completion_cost=0.002,
            total_cost=0.003,
            token_usage=usage
        )
        assert estimate.total_cost == 0.003

    def test_cost_tracker_initialization(self):
        """Test CostTracker initialization."""
        tracker = CostTracker()
        assert tracker.total_prompt_tokens == 0
        assert tracker.total_completion_tokens == 0
        assert tracker.total_cost == 0.0
        assert tracker.call_count == 0

    def test_cost_tracker_extract_openai_usage(self):
        """Test extracting token usage from OpenAI response."""
        tracker = CostTracker()
        
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.usage = Mock()
        mock_response.usage.prompt_tokens = 100
        mock_response.usage.completion_tokens = 50
        mock_response.usage.total_tokens = 150

        usage = tracker.extract_token_usage_from_response(mock_response, "openai")
        
        assert usage is not None
        assert usage.prompt_tokens == 100
        assert usage.completion_tokens == 50
        assert usage.total_tokens == 150

    def test_cost_tracker_extract_anthropic_usage(self):
        """Test extracting token usage from Anthropic response."""
        tracker = CostTracker()
        
        # Mock Anthropic response
        mock_response = Mock()
        mock_response.usage = Mock()
        mock_response.usage.input_tokens = 100
        mock_response.usage.output_tokens = 50

        usage = tracker.extract_token_usage_from_response(mock_response, "anthropic")
        
        assert usage is not None
        assert usage.prompt_tokens == 100
        assert usage.completion_tokens == 50
        assert usage.total_tokens == 150

    def test_cost_tracker_estimate_cost_gpt4(self):
        """Test cost estimation for GPT-4."""
        tracker = CostTracker()
        usage = TokenUsage(1000, 500, 1500)
        
        estimate = tracker.estimate_cost(usage, "gpt-4")
        
        # GPT-4: $0.03/1K input, $0.06/1K output
        expected_prompt = (1000 / 1000.0) * 0.03
        expected_completion = (500 / 1000.0) * 0.06
        expected_total = expected_prompt + expected_completion
        
        assert estimate.prompt_cost == pytest.approx(expected_prompt)
        assert estimate.completion_cost == pytest.approx(expected_completion)
        assert estimate.total_cost == pytest.approx(expected_total)

    def test_cost_tracker_estimate_cost_claude(self):
        """Test cost estimation for Claude."""
        tracker = CostTracker()
        usage = TokenUsage(1000, 500, 1500)
        
        estimate = tracker.estimate_cost(usage, "claude-3-sonnet")
        
        # Claude 3 Sonnet: $0.003/1K input, $0.015/1K output
        expected_prompt = (1000 / 1000.0) * 0.003
        expected_completion = (500 / 1000.0) * 0.015
        expected_total = expected_prompt + expected_completion
        
        assert estimate.prompt_cost == pytest.approx(expected_prompt)
        assert estimate.completion_cost == pytest.approx(expected_completion)
        assert estimate.total_cost == pytest.approx(expected_total)

    def test_cost_tracker_track_call(self):
        """Test tracking a single API call."""
        tracker = CostTracker()
        
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.usage = Mock()
        mock_response.usage.prompt_tokens = 100
        mock_response.usage.completion_tokens = 50
        mock_response.usage.total_tokens = 150

        estimate = tracker.track_call(mock_response, "openai", "gpt-3.5-turbo")
        
        assert estimate is not None
        assert tracker.total_prompt_tokens == 100
        assert tracker.total_completion_tokens == 50
        assert tracker.call_count == 1
        assert tracker.total_cost > 0

    def test_cost_tracker_get_totals(self):
        """Test getting total usage statistics."""
        tracker = CostTracker()
        
        # Simulate multiple calls
        for _ in range(3):
            mock_response = Mock()
            mock_response.usage = Mock()
            mock_response.usage.prompt_tokens = 100
            mock_response.usage.completion_tokens = 50
            mock_response.usage.total_tokens = 150
            tracker.track_call(mock_response, "openai", "gpt-3.5-turbo")

        totals = tracker.get_totals()
        
        assert totals["total_prompt_tokens"] == 300
        assert totals["total_completion_tokens"] == 150
        assert totals["total_tokens"] == 450
        assert totals["call_count"] == 3
        assert totals["average_cost_per_call"] > 0

    def test_cost_tracker_reset(self):
        """Test resetting tracker counters."""
        tracker = CostTracker()
        
        # Add some data
        mock_response = Mock()
        mock_response.usage = Mock()
        mock_response.usage.prompt_tokens = 100
        mock_response.usage.completion_tokens = 50
        mock_response.usage.total_tokens = 150
        tracker.track_call(mock_response, "openai", "gpt-3.5-turbo")

        # Reset
        tracker.reset()
        
        assert tracker.total_prompt_tokens == 0
        assert tracker.total_completion_tokens == 0
        assert tracker.total_cost == 0.0
        assert tracker.call_count == 0

    def test_estimate_tokens_from_text(self):
        """Test token estimation from text."""
        text = "This is a test message with some words."
        tokens = estimate_tokens_from_text(text)
        
        # Should be roughly text length / 4
        expected = len(text) // 4
        assert tokens == expected

    def test_estimate_cost_from_text(self):
        """Test cost estimation from text."""
        prompt = "This is a prompt with some content."
        response = "This is a response with some content."
        
        estimate = estimate_cost_from_text(prompt, response, "gpt-4")
        
        assert estimate.total_cost > 0
        assert estimate.token_usage.total_tokens > 0

    def test_cost_tracker_unknown_model(self):
        """Test cost estimation for unknown model uses default pricing."""
        tracker = CostTracker()
        usage = TokenUsage(1000, 500, 1500)
        
        estimate = tracker.estimate_cost(usage, "unknown-model-xyz")
        
        # Should use default pricing: $0.01/1K input, $0.03/1K output
        expected_prompt = (1000 / 1000.0) * 0.01
        expected_completion = (500 / 1000.0) * 0.03
        expected_total = expected_prompt + expected_completion
        
        assert estimate.prompt_cost == pytest.approx(expected_prompt)
        assert estimate.completion_cost == pytest.approx(expected_completion)
        assert estimate.total_cost == pytest.approx(expected_total)


@pytest.mark.asyncio
class TestCustomPromptExecution:
    """Test custom prompt execution in orchestrator."""

    async def test_execute_custom_prompt_basic(self):
        """Test basic custom prompt execution."""
        # Create mock components
        mock_sniper = Mock()
        mock_target = Mock()
        mock_target.execute = AsyncMock(return_value="Test response")
        mock_target.get_last_cost_estimate = Mock(return_value=None)
        mock_target.get_statistics = Mock(return_value={"total_executions": 1})
        
        mock_spotter = Mock()
        mock_spotter.evaluate = AsyncMock(return_value={
            "l1": {"score": 0.2},
            "l2": {"score": 0.3},
            "l3": {"score": 0.1},
        })
        mock_spotter.get_statistics = Mock(return_value={"total_evaluations": 1})
        
        mock_egg = Mock()
        mock_egg.inspect_prompt = Mock(return_value=(True, None))
        mock_egg.get_statistics = Mock(return_value={"total_blocked": 0})
        
        mock_scoring = Mock()
        mock_scoring.compute_global_score = Mock(return_value=0.25)
        
        mock_state = Mock()
        mock_state.get_statistics = Mock(return_value={"average_score": 0.0, "blocked_count": 0})
        mock_state.session_id = "test_session"
        mock_state.model_version = "test_model"
        mock_state.session_start_time = "2024-01-01T00:00:00Z"

        # Create orchestrator
        orchestrator = Orchestrator(
            sniper=mock_sniper,
            target=mock_target,
            spotter=mock_spotter,
            egg=mock_egg,
            scoring_engine=mock_scoring,
            state_manager=mock_state,
            max_rounds=10
        )

        # Execute custom prompt
        result = await orchestrator.execute_custom_prompt("Test prompt")

        # Verify result
        assert result["prompt"] == "Test prompt"
        assert result["response"] == "Test response"
        assert result["global_score"] == 0.25
        assert result["blocked_by_egg"] is False
        assert "evaluation" in result
        assert "timestamp" in result

    async def test_execute_custom_prompt_blocked_by_egg(self):
        """Test custom prompt blocked by EGG."""
        # Create mock components
        mock_sniper = Mock()
        mock_target = Mock()
        
        mock_spotter = Mock()
        
        # Mock EGG to block the prompt
        mock_blocked = Mock()
        mock_blocked.category = Mock()
        mock_blocked.category.value = "csam"
        
        mock_egg = Mock()
        mock_egg.inspect_prompt = Mock(return_value=(False, mock_blocked))
        mock_egg.get_blocked_replacement = Mock(return_value="[BLOCKED BY EGG]")
        mock_egg.get_statistics = Mock(return_value={"total_blocked": 1})
        
        mock_scoring = Mock()
        
        mock_state = Mock()
        mock_state.get_statistics = Mock(return_value={"average_score": 0.0, "blocked_count": 1})

        # Create orchestrator
        orchestrator = Orchestrator(
            sniper=mock_sniper,
            target=mock_target,
            spotter=mock_spotter,
            egg=mock_egg,
            scoring_engine=mock_scoring,
            state_manager=mock_state,
            max_rounds=10
        )

        # Execute custom prompt
        result = await orchestrator.execute_custom_prompt("Harmful prompt")

        # Verify result
        assert result["blocked_by_egg"] is True
        assert result["response"] == "[BLOCKED BY EGG]"
        assert result["global_score"] == 0.0
        assert result["block_reason"] == "csam"

    async def test_execute_custom_prompt_empty_string(self):
        """Test custom prompt with empty string raises error."""
        # Create minimal orchestrator
        mock_components = [Mock() for _ in range(6)]
        orchestrator = Orchestrator(*mock_components, max_rounds=10)

        # Should raise ValueError
        with pytest.raises(ValueError, match="non-empty string"):
            await orchestrator.execute_custom_prompt("")

    async def test_execute_custom_prompt_none(self):
        """Test custom prompt with None raises error."""
        # Create minimal orchestrator
        mock_components = [Mock() for _ in range(6)]
        orchestrator = Orchestrator(*mock_components, max_rounds=10)

        # Should raise ValueError
        with pytest.raises(ValueError, match="non-empty string"):
            await orchestrator.execute_custom_prompt(None)

    async def test_execute_custom_prompt_whitespace_only(self):
        """Test custom prompt with whitespace only raises error."""
        # Create minimal orchestrator
        mock_components = [Mock() for _ in range(6)]
        orchestrator = Orchestrator(*mock_components, max_rounds=10)

        # Should raise ValueError
        with pytest.raises(ValueError, match="non-empty string"):
            await orchestrator.execute_custom_prompt("   ")
