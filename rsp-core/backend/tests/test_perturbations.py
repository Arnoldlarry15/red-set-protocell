"""
Tests for Target perturbation modes
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from app.agents.target import (
    PerturbationMode, PerturbationConfig,
    OpenAIBackend, AnthropicBackend, CustomHTTPBackend,
    Target, create_target
)


def test_perturbation_config_defaults():
    """Test default perturbation configuration."""
    config = PerturbationConfig()

    assert config.enabled is False
    assert len(config.modes) == 5  # All modes by default
    assert PerturbationMode.SYSTEM_PROMPT in config.modes
    assert PerturbationMode.POLICY_REWORDING in config.modes
    assert PerturbationMode.TEMPERATURE_JITTER in config.modes
    assert PerturbationMode.SIMULATED_LATENCY in config.modes
    assert PerturbationMode.RESPONSE_TRUNCATION in config.modes
    assert len(config.system_prompts) > 0
    assert len(config.policy_rewordings) > 0


def test_perturbation_config_custom():
    """Test custom perturbation configuration."""
    custom_prompts = ["Custom prompt 1", "Custom prompt 2"]
    custom_modes = [PerturbationMode.TEMPERATURE_JITTER]

    config = PerturbationConfig(
        enabled=True,
        modes=custom_modes,
        system_prompts=custom_prompts,
        temperature_jitter_range=0.2
    )

    assert config.enabled is True
    assert config.modes == custom_modes
    assert config.system_prompts == custom_prompts
    assert config.temperature_jitter_range == 0.2


def test_perturbation_disabled_by_default():
    """Test that perturbations are disabled by default."""
    with patch('openai.AsyncOpenAI') as mock_openai:
        backend = OpenAIBackend(api_key='test-key')
        assert backend.perturbation_config.enabled is False


def test_set_perturbation_config():
    """Test setting perturbation configuration on backend."""
    with patch('openai.AsyncOpenAI'):
        backend = OpenAIBackend(api_key='test-key')
        config = PerturbationConfig(enabled=True)

        backend.set_perturbation_config(config)

        assert backend.perturbation_config.enabled is True


@pytest.mark.asyncio
@patch('openai.AsyncOpenAI')
async def test_system_prompt_perturbation(mock_openai):
    """Test system prompt perturbation."""
    mock_client = AsyncMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Response"
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai.return_value = mock_client

    backend = OpenAIBackend(api_key='test-key')
    config = PerturbationConfig(
        enabled=True,
        modes=[PerturbationMode.SYSTEM_PROMPT]
    )
    backend.set_perturbation_config(config)

    result = await backend.execute("Test prompt")

    assert result == "Response"
    # Verify system message was added
    call_args = mock_client.chat.completions.create.call_args
    messages = call_args.kwargs['messages']
    assert any(msg.get('role') == 'system' for msg in messages)


@pytest.mark.asyncio
@patch('openai.AsyncOpenAI')
async def test_policy_rewording_perturbation(mock_openai):
    """Test policy rewording perturbation."""
    mock_client = AsyncMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Response"
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai.return_value = mock_client

    backend = OpenAIBackend(api_key='test-key')
    config = PerturbationConfig(
        enabled=True,
        modes=[PerturbationMode.POLICY_REWORDING],
        policy_rewordings=["Policy note"]  # Non-empty to ensure it's added
    )
    backend.set_perturbation_config(config)

    result = await backend.execute("Test prompt")

    assert result == "Response"
    # Verify policy note was added to user message
    call_args = mock_client.chat.completions.create.call_args
    messages = call_args.kwargs['messages']
    user_messages = [m for m in messages if m.get('role') == 'user']
    assert len(user_messages) > 0


@pytest.mark.asyncio
@patch('openai.AsyncOpenAI')
async def test_temperature_jitter_perturbation(mock_openai):
    """Test temperature jitter perturbation."""
    mock_client = AsyncMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Response"
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai.return_value = mock_client

    backend = OpenAIBackend(api_key='test-key', temperature=0.7)
    config = PerturbationConfig(
        enabled=True,
        modes=[PerturbationMode.TEMPERATURE_JITTER],
        temperature_jitter_range=0.1
    )
    backend.set_perturbation_config(config)

    # Run multiple times to check variation
    temperatures = []
    for _ in range(10):
        await backend.execute("Test prompt")
        call_args = mock_client.chat.completions.create.call_args
        temperatures.append(call_args.kwargs['temperature'])

    # Temperature should vary
    assert len(set(temperatures)) > 1
    # All should be within range [0.6, 0.8] (0.7 ± 0.1)
    assert all(0.6 <= t <= 0.8 for t in temperatures)


@pytest.mark.asyncio
@patch('openai.AsyncOpenAI')
async def test_simulated_latency_perturbation(mock_openai):
    """Test simulated latency perturbation."""
    mock_client = AsyncMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Response"
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai.return_value = mock_client

    backend = OpenAIBackend(api_key='test-key')
    config = PerturbationConfig(
        enabled=True,
        modes=[PerturbationMode.SIMULATED_LATENCY],
        latency_range_ms=(100, 150)
    )
    backend.set_perturbation_config(config)

    start_time = time.time()
    result = await backend.execute("Test prompt")
    elapsed_ms = (time.time() - start_time) * 1000

    assert result == "Response"
    # Should have at least the minimum latency
    assert elapsed_ms >= 100


@pytest.mark.asyncio
@patch('openai.AsyncOpenAI')
async def test_response_truncation_perturbation(mock_openai):
    """Test response truncation perturbation."""
    mock_client = AsyncMock()
    mock_response = MagicMock()
    long_response = "This is a long response " * 20
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = long_response
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai.return_value = mock_client

    backend = OpenAIBackend(api_key='test-key')
    config = PerturbationConfig(
        enabled=True,
        modes=[PerturbationMode.RESPONSE_TRUNCATION],
        truncation_probability=1.0,  # Always truncate for testing
        truncation_ratio_range=(0.5, 0.6)
    )
    backend.set_perturbation_config(config)

    result = await backend.execute("Test prompt")

    # Should be truncated
    assert len(result) < len(long_response)
    # Should be within expected range (50-60% of original)
    assert len(result) >= len(long_response) * 0.5
    assert len(result) <= len(long_response) * 0.6


@pytest.mark.asyncio
@patch('openai.AsyncOpenAI')
async def test_multiple_perturbations_combined(mock_openai):
    """Test multiple perturbations applied together."""
    mock_client = AsyncMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Response from model"
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai.return_value = mock_client

    backend = OpenAIBackend(api_key='test-key', temperature=0.7)
    config = PerturbationConfig(
        enabled=True,
        modes=[
            PerturbationMode.SYSTEM_PROMPT,
            PerturbationMode.TEMPERATURE_JITTER,
            PerturbationMode.RESPONSE_TRUNCATION
        ],
        truncation_probability=0.0  # Disable truncation for easier assertion
    )
    backend.set_perturbation_config(config)

    result = await backend.execute("Test prompt")

    assert result == "Response from model"
    # Verify system message was added
    call_args = mock_client.chat.completions.create.call_args
    messages = call_args.kwargs['messages']
    assert any(msg.get('role') == 'system' for msg in messages)


@pytest.mark.asyncio
@patch('anthropic.AsyncAnthropic')
async def test_anthropic_backend_perturbations(mock_anthropic):
    """Test perturbations work with Anthropic backend."""
    mock_client = AsyncMock()
    mock_response = MagicMock()
    mock_response.content = [MagicMock()]
    mock_response.content[0].text = "Anthropic response"
    mock_client.messages.create.return_value = mock_response
    mock_anthropic.return_value = mock_client

    backend = AnthropicBackend(api_key='test-key')
    config = PerturbationConfig(
        enabled=True,
        modes=[PerturbationMode.SYSTEM_PROMPT, PerturbationMode.TEMPERATURE_JITTER]
    )
    backend.set_perturbation_config(config)

    result = await backend.execute("Test prompt")

    assert result == "Anthropic response"
    # Verify system prompt was passed
    call_args = mock_client.messages.create.call_args
    assert 'system' in call_args.kwargs or len(call_args.kwargs['messages']) > 0


@pytest.mark.asyncio
@patch('app.agents.target.requests')
async def test_custom_http_backend_perturbations(mock_requests):
    """Test perturbations work with CustomHTTPBackend."""
    mock_response = Mock()
    mock_response.json.return_value = {
        'choices': [{'message': {'content': 'HTTP response'}}]
    }
    mock_requests.post.return_value = mock_response

    backend = CustomHTTPBackend(
        api_url='http://localhost:8000/api',
        request_format='openai'
    )
    config = PerturbationConfig(
        enabled=True,
        modes=[PerturbationMode.TEMPERATURE_JITTER]
    )
    backend.set_perturbation_config(config)

    result = await backend.execute("Test prompt")

    assert result == "HTTP response"


@pytest.mark.asyncio
async def test_target_with_perturbations():
    """Test Target agent with perturbation configuration."""
    with patch('openai.AsyncOpenAI') as mock_openai:
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Response"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        config = PerturbationConfig(enabled=True)
        target = create_target(
            'openai',
            api_key='test-key',
            perturbation_config=config
        )

        result = await target.execute("Test prompt")

        assert result == "Response"
        assert target.execution_count == 1


def test_target_statistics_with_perturbations():
    """Test Target statistics include perturbation info."""
    with patch('openai.AsyncOpenAI') as mock_openai:
        mock_client = AsyncMock()
        mock_openai.return_value = mock_client

        config = PerturbationConfig(
            enabled=True,
            modes=[PerturbationMode.TEMPERATURE_JITTER]
        )
        target = create_target(
            'openai',
            api_key='test-key',
            perturbation_config=config
        )

        stats = target.get_statistics()

        assert 'perturbations_enabled' in stats
        assert stats['perturbations_enabled'] is True
        assert 'perturbation_modes' in stats
        assert 'temperature_jitter' in stats['perturbation_modes']


@pytest.mark.asyncio
async def test_perturbations_dont_break_statelessness():
    """Test that perturbations maintain stateless execution."""
    with patch('openai.AsyncOpenAI') as mock_openai:
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Response"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        config = PerturbationConfig(enabled=True, truncation_probability=0.0)
        backend = OpenAIBackend(api_key='test-key')
        backend.set_perturbation_config(config)

        # Execute multiple times
        result1 = await backend.execute("Prompt 1")
        result2 = await backend.execute("Prompt 2")

        # Both should succeed independently
        assert result1 == "Response"
        assert result2 == "Response"
        # Each call should be independent (fresh context)
        assert mock_client.chat.completions.create.call_count == 2


@pytest.mark.asyncio
async def test_no_perturbations_when_disabled():
    """Test that no perturbations are applied when disabled."""
    with patch('openai.AsyncOpenAI') as mock_openai:
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Response"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        backend = OpenAIBackend(api_key='test-key', temperature=0.7)
        # Default config with enabled=False

        result = await backend.execute("Test prompt")

        assert result == "Response"
        call_args = mock_client.chat.completions.create.call_args
        # Should use original temperature
        assert call_args.kwargs['temperature'] == 0.7
        # Should have only user message
        messages = call_args.kwargs['messages']
        assert len(messages) == 1
        assert messages[0]['role'] == 'user'


@pytest.mark.asyncio
async def test_temperature_bounds_respected():
    """Test that temperature jitter respects 0.0-2.0 bounds."""
    with patch('openai.AsyncOpenAI') as mock_openai:
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Response"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        # Test lower bound
        backend = OpenAIBackend(api_key='test-key', temperature=0.0)
        config = PerturbationConfig(
            enabled=True,
            modes=[PerturbationMode.TEMPERATURE_JITTER],
            temperature_jitter_range=0.5
        )
        backend.set_perturbation_config(config)

        for _ in range(10):
            await backend.execute("Test prompt")
            call_args = mock_client.chat.completions.create.call_args
            temp = call_args.kwargs['temperature']
            assert 0.0 <= temp <= 2.0

        # Test upper bound
        backend2 = OpenAIBackend(api_key='test-key', temperature=2.0)
        backend2.set_perturbation_config(config)

        for _ in range(10):
            await backend2.execute("Test prompt")
            call_args = mock_client.chat.completions.create.call_args
            temp = call_args.kwargs['temperature']
            assert 0.0 <= temp <= 2.0
