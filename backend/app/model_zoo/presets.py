"""
Red Set ProtoCell - Model Presets

Preconfigured reference models from major providers.
"""

from typing import Dict, List

from app.model_zoo.registry import ModelInfo, ModelProvider, ModelVersion


def get_openai_models() -> List[ModelInfo]:
    """
    Get OpenAI reference models.

    Returns:
        List of OpenAI model configurations
    """
    return [
        ModelInfo(
            model_id="openai-gpt-3.5-turbo",
            display_name="GPT-3.5 Turbo",
            provider=ModelProvider.OPENAI,
            backend_type="openai",
            model_name="gpt-3.5-turbo",
            versions=[
                ModelVersion(
                    version_id="gpt-3.5-turbo-0125",
                    release_date="2024-01-25",
                    description="Latest GPT-3.5 Turbo with improved accuracy",
                ),
                ModelVersion(
                    version_id="gpt-3.5-turbo-1106",
                    release_date="2023-11-06",
                    description="GPT-3.5 Turbo with function calling support",
                ),
            ],
            default_version="gpt-3.5-turbo-0125",
            capabilities=["chat", "function-calling", "json-mode"],
            context_window=16385,
            description="Fast and cost-effective model for most tasks",
            recommended_for=["quick-benchmarks", "development", "baseline-testing"],
        ),
        ModelInfo(
            model_id="openai-gpt-4",
            display_name="GPT-4",
            provider=ModelProvider.OPENAI,
            backend_type="openai",
            model_name="gpt-4",
            versions=[
                ModelVersion(
                    version_id="gpt-4-0613",
                    release_date="2023-06-13",
                    description="Snapshot of GPT-4 from June 2023",
                ),
                ModelVersion(
                    version_id="gpt-4-0125-preview",
                    release_date="2024-01-25",
                    description="Latest GPT-4 Turbo preview",
                ),
            ],
            default_version="gpt-4-0613",
            capabilities=["chat", "function-calling", "json-mode", "vision"],
            context_window=8192,
            description="Most capable OpenAI model for complex tasks",
            recommended_for=[
                "comprehensive-benchmarks",
                "production-testing",
                "safety-critical",
            ],
        ),
        ModelInfo(
            model_id="openai-gpt-4-turbo",
            display_name="GPT-4 Turbo",
            provider=ModelProvider.OPENAI,
            backend_type="openai",
            model_name="gpt-4-turbo-preview",
            versions=[
                ModelVersion(
                    version_id="gpt-4-turbo-2024-04-09",
                    release_date="2024-04-09",
                    description="Latest GPT-4 Turbo with 128K context",
                ),
            ],
            default_version="gpt-4-turbo-2024-04-09",
            capabilities=["chat", "function-calling", "json-mode", "vision"],
            context_window=128000,
            description="Faster GPT-4 with larger context window",
            recommended_for=["comprehensive-benchmarks", "long-context-testing"],
        ),
    ]


def get_anthropic_models() -> List[ModelInfo]:
    """
    Get Anthropic reference models.

    Returns:
        List of Anthropic model configurations
    """
    return [
        ModelInfo(
            model_id="anthropic-claude-3-haiku",
            display_name="Claude 3 Haiku",
            provider=ModelProvider.ANTHROPIC,
            backend_type="anthropic",
            model_name="claude-3-haiku-20240307",
            versions=[
                ModelVersion(
                    version_id="claude-3-haiku-20240307",
                    release_date="2024-03-07",
                    description="Fastest and most compact Claude 3 model",
                ),
            ],
            default_version="claude-3-haiku-20240307",
            capabilities=["chat", "long-context"],
            context_window=200000,
            description="Fast and cost-effective Claude model",
            recommended_for=["quick-benchmarks", "high-throughput-testing"],
        ),
        ModelInfo(
            model_id="anthropic-claude-3-sonnet",
            display_name="Claude 3 Sonnet",
            provider=ModelProvider.ANTHROPIC,
            backend_type="anthropic",
            model_name="claude-3-sonnet-20240229",
            versions=[
                ModelVersion(
                    version_id="claude-3-sonnet-20240229",
                    release_date="2024-02-29",
                    description="Balanced Claude 3 model",
                ),
            ],
            default_version="claude-3-sonnet-20240229",
            capabilities=["chat", "long-context", "vision"],
            context_window=200000,
            description="Balanced performance and cost",
            recommended_for=["standard-benchmarks", "production-testing"],
        ),
        ModelInfo(
            model_id="anthropic-claude-3-opus",
            display_name="Claude 3 Opus",
            provider=ModelProvider.ANTHROPIC,
            backend_type="anthropic",
            model_name="claude-3-opus-20240229",
            versions=[
                ModelVersion(
                    version_id="claude-3-opus-20240229",
                    release_date="2024-02-29",
                    description="Most capable Claude 3 model",
                ),
            ],
            default_version="claude-3-opus-20240229",
            capabilities=["chat", "long-context", "vision"],
            context_window=200000,
            description="Most capable Anthropic model",
            recommended_for=["comprehensive-benchmarks", "safety-critical", "research"],
        ),
    ]


def get_all_reference_models() -> Dict[str, List[ModelInfo]]:
    """
    Get all reference models organized by provider.

    Returns:
        Dictionary mapping provider names to model lists
    """
    return {
        "openai": get_openai_models(),
        "anthropic": get_anthropic_models(),
    }


def create_default_registry():
    """
    Create a model registry with all reference models.

    Returns:
        Populated model registry
    """
    from app.model_zoo.registry import ModelRegistry

    registry = ModelRegistry()

    # Register all models
    for models in get_all_reference_models().values():
        for model in models:
            registry.register_model(model)

    return registry
