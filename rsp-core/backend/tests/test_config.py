"""
Tests for configuration module
"""

import pytest
from app.core.config import (
    RSPConfig,
    get_default_config,
    ScoringConfig,
    StorageMode,
    ModelBackend
)


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
    assert ModelBackend.LOCAL.value == "local"


def test_config_customization():
    """Test config can be customized."""
    config = get_default_config()
    
    config.orchestrator.max_rounds = 50
    config.target.backend = ModelBackend.ANTHROPIC
    config.storage.zero_retention = False
    
    assert config.orchestrator.max_rounds == 50
    assert config.target.backend == ModelBackend.ANTHROPIC
    assert config.storage.zero_retention is False
