"""
Red Set ProtoCell - Model Zoo

Reference models and versions for consistent comparisons.
"""

from app.model_zoo.presets import get_all_reference_models, get_anthropic_models, get_openai_models
from app.model_zoo.registry import ModelInfo, ModelProvider, ModelRegistry, ModelVersion

__all__ = [
    "ModelRegistry",
    "ModelInfo",
    "ModelVersion",
    "ModelProvider",
    "get_openai_models",
    "get_anthropic_models",
    "get_all_reference_models",
]
