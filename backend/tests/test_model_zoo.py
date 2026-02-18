"""
Tests for model zoo module.
"""

from app.model_zoo.presets import (
    create_default_registry,
    get_anthropic_models,
    get_openai_models,
)
from app.model_zoo.registry import (
    ModelInfo,
    ModelProvider,
    ModelRegistry,
    ModelVersion,
)


def test_model_version_creation():
    """Test creating a model version."""
    version = ModelVersion(
        version_id="gpt-3.5-turbo-0125",
        release_date="2024-01-25",
        description="Latest GPT-3.5 Turbo",
    )

    assert version.version_id == "gpt-3.5-turbo-0125"
    assert not version.deprecated


def test_model_info_creation():
    """Test creating model info."""
    version = ModelVersion(
        version_id="v1",
        release_date="2024-01-01",
        description="Version 1",
    )

    model = ModelInfo(
        model_id="test-model",
        display_name="Test Model",
        provider=ModelProvider.OPENAI,
        backend_type="openai",
        model_name="test-model-api",
        versions=[version],
        default_version="v1",
        capabilities=["chat"],
        context_window=4096,
        description="A test model",
        recommended_for=["testing"],
    )

    assert model.model_id == "test-model"
    assert model.provider == ModelProvider.OPENAI
    assert len(model.versions) == 1


def test_get_version():
    """Test getting specific version."""
    v1 = ModelVersion(version_id="v1", release_date="2024-01-01", description="V1")
    v2 = ModelVersion(version_id="v2", release_date="2024-02-01", description="V2")

    model = ModelInfo(
        model_id="test",
        display_name="Test",
        provider=ModelProvider.OPENAI,
        backend_type="openai",
        model_name="test",
        versions=[v1, v2],
        default_version="v2",
        capabilities=["chat"],
        context_window=4096,
        description="Test",
        recommended_for=["testing"],
    )

    version = model.get_version("v1")
    assert version.version_id == "v1"

    version = model.get_version("v2")
    assert version.version_id == "v2"

    version = model.get_version("v3")
    assert version is None


def test_get_latest_version():
    """Test getting latest version."""
    v1 = ModelVersion(version_id="v1", release_date="2024-01-01", description="V1")
    v2 = ModelVersion(version_id="v2", release_date="2024-02-01", description="V2")
    v3 = ModelVersion(version_id="v3", release_date="2024-03-01", description="V3", deprecated=True)

    model = ModelInfo(
        model_id="test",
        display_name="Test",
        provider=ModelProvider.OPENAI,
        backend_type="openai",
        model_name="test",
        versions=[v1, v2, v3],
        default_version="v2",
        capabilities=["chat"],
        context_window=4096,
        description="Test",
        recommended_for=["testing"],
    )

    latest = model.get_latest_version()
    assert latest.version_id == "v2"  # v3 is deprecated


def test_model_registry():
    """Test model registry."""
    registry = ModelRegistry()

    version = ModelVersion(version_id="v1", release_date="2024-01-01", description="V1")
    model = ModelInfo(
        model_id="test",
        display_name="Test",
        provider=ModelProvider.OPENAI,
        backend_type="openai",
        model_name="test",
        versions=[version],
        default_version="v1",
        capabilities=["chat"],
        context_window=4096,
        description="Test",
        recommended_for=["testing"],
    )

    registry.register_model(model)

    retrieved = registry.get_model("test")
    assert retrieved is not None
    assert retrieved.model_id == "test"


def test_list_models():
    """Test listing models."""
    registry = create_default_registry()

    all_models = registry.list_models()
    assert len(all_models) > 0

    # Filter by provider
    openai_models = registry.list_models(provider=ModelProvider.OPENAI)
    assert all(m.provider == ModelProvider.OPENAI for m in openai_models)


def test_get_model_config():
    """Test getting model configuration."""
    registry = create_default_registry()

    config = registry.get_model_config("openai-gpt-3.5-turbo")

    assert config["backend"] == "openai"
    assert config["model_name"] == "gpt-3.5-turbo"
    assert "model_version" in config
    assert "context_window" in config


def test_compare_models():
    """Test model comparison."""
    registry = create_default_registry()

    comparison = registry.compare_models(
        [
            "openai-gpt-3.5-turbo",
            "openai-gpt-4",
        ]
    )

    assert "models" in comparison
    assert "providers" in comparison
    assert "context_windows" in comparison
    assert len(comparison["models"]) == 2


def test_get_openai_models():
    """Test getting OpenAI models."""
    models = get_openai_models()

    assert len(models) > 0
    assert all(m.provider == ModelProvider.OPENAI for m in models)

    # Check specific models
    model_ids = [m.model_id for m in models]
    assert "openai-gpt-3.5-turbo" in model_ids
    assert "openai-gpt-4" in model_ids


def test_get_anthropic_models():
    """Test getting Anthropic models."""
    models = get_anthropic_models()

    assert len(models) > 0
    assert all(m.provider == ModelProvider.ANTHROPIC for m in models)

    # Check specific models
    model_ids = [m.model_id for m in models]
    assert "anthropic-claude-3-opus" in model_ids


def test_save_and_load_registry(tmp_path):
    """Test saving and loading registry."""
    registry = create_default_registry()

    filepath = tmp_path / "test_registry.json"
    registry.save_to_file(filepath)

    assert filepath.exists()

    # Load into new registry
    new_registry = ModelRegistry(registry_file=str(filepath))

    # Verify models were loaded
    assert len(new_registry.list_models()) == len(registry.list_models())
