"""
Red Set ProtoCell - Model Zoo Demo

Demonstrates model zoo and registry capabilities.
"""

import logging

from app.model_zoo import (
    ModelRegistry,
    get_openai_models,
    get_anthropic_models,
    get_all_reference_models,
)
from app.model_zoo.presets import create_default_registry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def demo_model_listing():
    """Demonstrate model listing functionality."""
    logger.info("=== Model Listing Demo ===")
    
    registry = create_default_registry()
    
    # List all models
    all_models = registry.list_models()
    logger.info(f"\nTotal models in registry: {len(all_models)}")
    
    for model in all_models:
        logger.info(f"\n{model.display_name} ({model.model_id})")
        logger.info(f"  Provider: {model.provider.value}")
        logger.info(f"  Context: {model.context_window:,} tokens")
        logger.info(f"  Capabilities: {', '.join(model.capabilities)}")
        logger.info(f"  Recommended for: {', '.join(model.recommended_for)}")


def demo_model_config():
    """Demonstrate getting model configuration."""
    logger.info("\n\n=== Model Configuration Demo ===")
    
    registry = create_default_registry()
    
    # Get config for specific model
    model_id = "openai-gpt-3.5-turbo"
    config = registry.get_model_config(model_id)
    
    logger.info(f"\nConfiguration for {model_id}:")
    logger.info(f"  Backend: {config['backend']}")
    logger.info(f"  Model name: {config['model_name']}")
    logger.info(f"  Version: {config['model_version']}")
    logger.info(f"  Context window: {config['context_window']:,} tokens")


def demo_model_comparison():
    """Demonstrate model comparison functionality."""
    logger.info("\n\n=== Model Comparison Demo ===")
    
    registry = create_default_registry()
    
    # Compare multiple models
    model_ids = [
        "openai-gpt-3.5-turbo",
        "openai-gpt-4",
        "anthropic-claude-3-sonnet",
        "anthropic-claude-3-opus",
    ]
    
    comparison = registry.compare_models(model_ids)
    
    logger.info("\nModel Comparison:")
    logger.info(f"Models: {', '.join(comparison['models'])}")
    logger.info(f"\nProviders: {', '.join(comparison['providers'])}")
    logger.info(f"\nContext windows:")
    for model_id, context in zip(comparison['models'], comparison['context_windows']):
        logger.info(f"  {model_id}: {context:,} tokens")
    
    logger.info(f"\nCapabilities:")
    for model_id, caps in comparison['capabilities'].items():
        logger.info(f"  {model_id}: {', '.join(caps)}")


def demo_version_tracking():
    """Demonstrate version tracking functionality."""
    logger.info("\n\n=== Version Tracking Demo ===")
    
    registry = create_default_registry()
    
    # Get model with versions
    model = registry.get_model("openai-gpt-4")
    
    logger.info(f"\n{model.display_name} versions:")
    for version in model.versions:
        logger.info(f"\n  Version: {version.version_id}")
        logger.info(f"  Released: {version.release_date}")
        logger.info(f"  Description: {version.description}")
        if version.deprecated:
            logger.info(f"  Status: DEPRECATED")
    
    # Get latest version
    latest = model.get_latest_version()
    logger.info(f"\nLatest version: {latest.version_id}")


def demo_provider_filtering():
    """Demonstrate filtering by provider."""
    logger.info("\n\n=== Provider Filtering Demo ===")
    
    registry = create_default_registry()
    
    from app.model_zoo.registry import ModelProvider
    
    # List OpenAI models
    openai_models = registry.list_models(provider=ModelProvider.OPENAI)
    logger.info(f"\nOpenAI models ({len(openai_models)}):")
    for model in openai_models:
        logger.info(f"  - {model.display_name}")
    
    # List Anthropic models
    anthropic_models = registry.list_models(provider=ModelProvider.ANTHROPIC)
    logger.info(f"\nAnthropic models ({len(anthropic_models)}):")
    for model in anthropic_models:
        logger.info(f"  - {model.display_name}")


def main():
    """Main demo function."""
    print("\n" + "="*60)
    print("Red Set ProtoCell - Model Zoo Demo")
    print("="*60 + "\n")
    
    print("This demo shows the new model zoo capabilities:")
    print("1. Reference model registry with preconfigured models")
    print("2. Model version tracking")
    print("3. Model comparison utilities")
    print("4. Provider filtering")
    print("5. Easy configuration for benchmarking")
    print("\n")
    
    demo_model_listing()
    demo_model_config()
    demo_model_comparison()
    demo_version_tracking()
    demo_provider_filtering()
    
    print("\n" + "="*60)
    print("Demo completed!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
