"""
Tests for async interfaces and abstract base classes.
"""

import pytest

from app.agents.target import AnthropicBackend, OpenAIBackend, TargetBackend
from app.interfaces import (
    BaseMutationStrategy,
    BaseScoringStrategy,
    BaseTarget,
    ScoreResult,
)


class MockAsyncBackend(BaseTarget):
    """Mock backend for testing async interface."""

    async def execute(self, prompt: str, **kwargs) -> str:
        """Mock execute method."""
        return f"Mock response to: {prompt}"

    def get_backend_info(self) -> dict:
        """Mock backend info."""
        return {"backend_type": "mock", "model": "test-model"}


class MockMutationStrategy(BaseMutationStrategy):
    """Mock mutation strategy for testing."""

    def mutate(self, prompt: str, **kwargs) -> str:
        """Mock mutation."""
        return f"[MUTATED] {prompt}"

    def get_strategy_info(self) -> dict:
        """Mock strategy info."""
        return {"name": "mock", "type": "test"}


class MockScoringStrategy(BaseScoringStrategy):
    """Mock scoring strategy for testing."""

    async def score(self, response: str, **kwargs) -> ScoreResult:
        """Mock scoring."""
        return ScoreResult(score=0.5, confidence=0.8, uncertainty=0.1, indicators={"test": True})

    def get_strategy_info(self) -> dict:
        """Mock strategy info."""
        return {"name": "mock", "dimension": "safety"}


@pytest.mark.asyncio
async def test_base_target_interface():
    """Test that BaseTarget interface works with mock implementation."""
    backend = MockAsyncBackend()

    # Test execute
    response = await backend.execute("test prompt")
    assert "Mock response" in response
    assert "test prompt" in response

    # Test get_backend_info
    info = backend.get_backend_info()
    assert info["backend_type"] == "mock"
    assert "model" in info


def test_base_mutation_strategy_interface():
    """Test that BaseMutationStrategy interface works."""
    strategy = MockMutationStrategy()

    # Test mutate
    mutated = strategy.mutate("test prompt")
    assert "[MUTATED]" in mutated
    assert "test prompt" in mutated

    # Test get_strategy_info
    info = strategy.get_strategy_info()
    assert info["name"] == "mock"
    assert info["type"] == "test"

    # Test optional methods
    impact = strategy.estimate_fitness_impact("test")
    assert isinstance(impact, float)

    valid = strategy.validate_output("test output")
    assert valid is True


@pytest.mark.asyncio
async def test_base_scoring_strategy_interface():
    """Test that BaseScoringStrategy interface works."""
    strategy = MockScoringStrategy()

    # Test score
    result = await strategy.score("test response")
    assert isinstance(result, ScoreResult)
    assert 0.0 <= result.score <= 1.0
    assert 0.0 <= result.confidence <= 1.0
    assert 0.0 <= result.uncertainty <= 1.0
    assert result.indicators is not None

    # Test get_strategy_info
    info = strategy.get_strategy_info()
    assert info["name"] == "mock"
    assert info["dimension"] == "safety"

    # Test confidence interval
    lower, upper = strategy.get_confidence_interval(0.5, 0.1)
    assert lower == 0.4
    assert upper == 0.6


def test_target_backend_inherits_base_target():
    """Test that TargetBackend properly inherits from BaseTarget."""
    assert issubclass(TargetBackend, BaseTarget)


def test_openai_backend_has_backend_info():
    """Test that OpenAI backend implements get_backend_info."""
    # We can't actually test execution without API key, but we can check the interface
    try:
        backend = OpenAIBackend(api_key="test-key", model_name="gpt-3.5-turbo")
        info = backend.get_backend_info()
        assert info["backend_type"] == "openai"
        assert info["model_name"] == "gpt-3.5-turbo"
    except ImportError:
        pytest.skip("OpenAI package not available")


def test_anthropic_backend_has_backend_info():
    """Test that Anthropic backend implements get_backend_info."""
    try:
        backend = AnthropicBackend(api_key="test-key", model_name="claude-3-5-sonnet-20241022")
        info = backend.get_backend_info()
        assert info["backend_type"] == "anthropic"
        assert info["model_name"] == "claude-3-5-sonnet-20241022"
    except ImportError:
        pytest.skip("Anthropic package not available")


def test_score_result_dataclass():
    """Test ScoreResult dataclass initialization."""
    result = ScoreResult(score=0.7, confidence=0.9, uncertainty=0.05)

    assert result.score == 0.7
    assert result.confidence == 0.9
    assert result.uncertainty == 0.05
    assert result.indicators == {}
    assert result.metadata == {}


def test_score_result_with_indicators():
    """Test ScoreResult with indicators and metadata."""
    result = ScoreResult(
        score=0.7,
        confidence=0.9,
        uncertainty=0.05,
        indicators={"hate_speech": True, "pii": False},
        metadata={"model": "test"},
    )

    assert result.indicators["hate_speech"] is True
    assert result.indicators["pii"] is False
    assert result.metadata["model"] == "test"
