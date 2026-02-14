"""
Tests for configuration module
"""

import pytest
from app.core.config import (
    RSPConfig,
    get_default_config,
    load_config_from_env,
    ScoringConfig,
    StorageMode,
    ModelBackend
)
from app.agents.sniper import Sniper
from app.agents.spotter import Spotter
from app.engines.mutation import MutationEngine


def test_default_config():
    """Test default configuration."""
    config = get_default_config()

    assert isinstance(config, RSPConfig)
    assert config.orchestrator.max_rounds == 100
    assert config.storage.zero_retention is True
    assert config.egg.enabled is True


def test_scoring_weights_validation():
    """Test scoring weights are validated."""
    # Valid weights
    config = RSPConfig()
    assert config.scoring.l1_weight == 0.35
    assert config.scoring.l2_weight == 0.45
    assert config.scoring.l3_weight == 0.20

    # Invalid weights
    with pytest.raises(ValueError):
        config = RSPConfig(
            scoring=ScoringConfig(l1_weight=0.5, l2_weight=0.5, l3_weight=0.5)
        )


def test_mutation_rate_validation():
    """Test mutation rate is validated."""
    config = RSPConfig()

    # Valid rate
    config.sniper.mutation_rate = 0.7

    # Invalid rate should raise error during validation
    with pytest.raises(ValueError):
        config.sniper.mutation_rate = 1.5
        config.__post_init__()


def test_storage_modes():
    """Test storage mode enum."""
    assert StorageMode.SQLITE.value == "sqlite"
    assert StorageMode.POSTGRES.value == "postgres"


def test_model_backends():
    """Test model backend enum."""
    assert ModelBackend.OPENAI.value == "openai"
    assert ModelBackend.ANTHROPIC.value == "anthropic"
    assert ModelBackend.OPENROUTER.value == "openrouter"


def test_config_customization():
    """Test config can be customized."""
    config = get_default_config()

    config.orchestrator.max_rounds = 50
    config.target.backend = ModelBackend.ANTHROPIC
    config.storage.zero_retention = False

    assert config.orchestrator.max_rounds == 50
    assert config.target.backend == ModelBackend.ANTHROPIC
    assert config.storage.zero_retention is False


def test_separate_agent_api_keys():
    """Test that Sniper and Spotter can have separate API keys."""
    config = get_default_config()

    # Set separate API keys
    config.sniper.api_key = "sniper-key-123"
    config.spotter.api_key = "spotter-key-456"
    config.target.api_key = "target-key-789"

    # Verify they are independent
    assert config.sniper.api_key == "sniper-key-123"
    assert config.spotter.api_key == "spotter-key-456"
    assert config.target.api_key == "target-key-789"
    assert config.sniper.api_key != config.spotter.api_key
    assert config.sniper.api_key != config.target.api_key
    assert config.spotter.api_key != config.target.api_key


def test_agent_initialization_with_api_keys():
    """Test that agents can be initialized with API keys."""
    # Initialize mutation engine for Sniper
    mutation_engine = MutationEngine(mutation_rate=0.7)

    # Initialize Sniper with API key
    sniper = Sniper(
        mutation_engine=mutation_engine,
        evolution_pool_size=10,
        creativity_temperature=0.9,
        api_key="sniper-test-key"
    )
    assert sniper.api_key == "sniper-test-key"

    # Initialize Spotter with API key
    spotter = Spotter(
        confidence_threshold=0.6,
        api_key="spotter-test-key"
    )
    assert spotter.api_key == "spotter-test-key"

    # Verify they have different API keys
    assert sniper.api_key != spotter.api_key


def test_load_config_from_env(monkeypatch):
    """Test loading config from environment variables."""
    # Clear any existing API keys that might interfere
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("BACKEND_TYPE", raising=False)

    # Set environment variables
    monkeypatch.setenv("SNIPER_ANTHROPIC_API_KEY", "sniper-env-key")
    monkeypatch.setenv("SPOTTER_ANTHROPIC_API_KEY", "spotter-env-key")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "target-env-key")

    # Load config from environment
    config = load_config_from_env()

    # Verify API keys were loaded
    assert config.sniper.api_key == "sniper-env-key"
    assert config.spotter.api_key == "spotter-env-key"
    assert config.target.api_key == "target-env-key"


def test_load_openrouter_config_from_env(monkeypatch):
    """Test loading OpenRouter config from environment variables."""
    # Clear any existing API keys that might interfere
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    # Set environment variables for OpenRouter
    monkeypatch.setenv("BACKEND_TYPE", "openrouter")
    monkeypatch.setenv("OPENROUTER_API_KEY", "openrouter-test-key")

    # Load config from environment
    config = load_config_from_env()

    # Verify backend type and API key were loaded
    assert config.target.backend == ModelBackend.OPENROUTER
    assert config.target.api_key == "openrouter-test-key"
    assert config.target.openrouter_api_key == "openrouter-test-key"


def test_load_openrouter_custom_base_url(monkeypatch):
    """Test loading OpenRouter with custom base URL."""
    # Clear any existing API keys that might interfere
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    # Set environment variables
    monkeypatch.setenv("BACKEND_TYPE", "openrouter")
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    monkeypatch.setenv("OPENROUTER_BASE_URL", "https://custom.openrouter.ai/api/v1")

    # Load config from environment
    config = load_config_from_env()

    # Verify custom base URL was loaded
    assert config.target.backend == ModelBackend.OPENROUTER
    assert config.target.openrouter_base_url == "https://custom.openrouter.ai/api/v1"


def test_backend_type_env_defaults_to_openai(monkeypatch):
    """Test that backend type defaults to OpenAI when not specified."""
    # Clear BACKEND_TYPE and other keys that might interfere
    monkeypatch.delenv("BACKEND_TYPE", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)

    # Don't set BACKEND_TYPE, should default to OpenAI
    monkeypatch.setenv("OPENAI_API_KEY", "openai-test-key")

    # Load config from environment
    config = load_config_from_env()

    # Verify default backend is OpenAI
    assert config.target.backend == ModelBackend.OPENAI
    assert config.target.api_key == "openai-test-key"


def test_backend_type_case_insensitive(monkeypatch):
    """Test that backend type is case-insensitive."""
    # Clear any existing API keys that might interfere
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    # Set uppercase backend type
    monkeypatch.setenv("BACKEND_TYPE", "OPENROUTER")
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")

    # Load config from environment
    config = load_config_from_env()

    # Verify backend was set correctly
    assert config.target.backend == ModelBackend.OPENROUTER
