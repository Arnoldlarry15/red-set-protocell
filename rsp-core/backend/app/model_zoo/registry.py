"""
Red Set ProtoCell - Model Registry

Registry of reference models for benchmarking.
"""

import json
import logging
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class ModelProvider(Enum):
    """Supported model providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"
    CUSTOM = "custom"


@dataclass
class ModelVersion:
    """Version information for a model."""
    version_id: str
    release_date: str
    description: str
    deprecated: bool = False
    notes: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class ModelInfo:
    """Information about a reference model."""
    model_id: str
    display_name: str
    provider: ModelProvider
    backend_type: str  # openai, anthropic, llama_cpp, custom_http
    model_name: str  # API model name
    versions: List[ModelVersion]
    default_version: str
    capabilities: List[str]
    context_window: int
    description: str
    recommended_for: List[str]
    benchmark_baseline: Optional[Dict[str, float]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['provider'] = self.provider.value
        return data
    
    def get_version(self, version_id: str) -> Optional[ModelVersion]:
        """Get specific version info."""
        for version in self.versions:
            if version.version_id == version_id:
                return version
        return None
    
    def get_latest_version(self) -> ModelVersion:
        """Get latest non-deprecated version."""
        active_versions = [v for v in self.versions if not v.deprecated]
        if active_versions:
            return active_versions[-1]
        return self.versions[-1] if self.versions else None


class ModelRegistry:
    """
    Registry of reference models for benchmarking.
    
    Provides:
    - Preconfigured reference models
    - Version tracking
    - Model comparison utilities
    """
    
    def __init__(self, registry_file: Optional[str] = None):
        """
        Initialize model registry.
        
        Args:
            registry_file: Optional path to registry JSON file
        """
        self.models: Dict[str, ModelInfo] = {}
        self.registry_file = Path(registry_file) if registry_file else None
        
        if self.registry_file and self.registry_file.exists():
            self.load_from_file(self.registry_file)
        
        logger.info(f"Model registry initialized with {len(self.models)} models")
    
    def register_model(self, model: ModelInfo):
        """
        Register a model in the registry.
        
        Args:
            model: Model information to register
        """
        self.models[model.model_id] = model
        logger.info(f"Registered model: {model.model_id}")
    
    def get_model(self, model_id: str) -> Optional[ModelInfo]:
        """
        Get model information by ID.
        
        Args:
            model_id: Model identifier
            
        Returns:
            Model information or None if not found
        """
        return self.models.get(model_id)
    
    def list_models(
        self,
        provider: Optional[ModelProvider] = None,
        capability: Optional[str] = None,
    ) -> List[ModelInfo]:
        """
        List all registered models.
        
        Args:
            provider: Optional filter by provider
            capability: Optional filter by capability
            
        Returns:
            List of model information
        """
        models = list(self.models.values())
        
        if provider:
            models = [m for m in models if m.provider == provider]
        
        if capability:
            models = [m for m in models if capability in m.capabilities]
        
        return models
    
    def get_model_config(
        self,
        model_id: str,
        version_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get configuration for using a model with RSP.
        
        Args:
            model_id: Model identifier
            version_id: Optional version (uses default if not specified)
            
        Returns:
            Configuration dictionary for RSP
        """
        model = self.get_model(model_id)
        if not model:
            raise ValueError(f"Model not found: {model_id}")
        
        version = version_id or model.default_version
        version_info = model.get_version(version)
        
        config = {
            'backend': model.backend_type,
            'model_name': model.model_name,
            'model_version': version,
            'provider': model.provider.value,
            'context_window': model.context_window,
        }
        
        return config
    
    def save_to_file(self, filepath: Path):
        """
        Save registry to JSON file.
        
        Args:
            filepath: Path to save file
        """
        data = {
            'timestamp': datetime.now().isoformat(),
            'models': [model.to_dict() for model in self.models.values()],
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Saved model registry to {filepath}")
    
    def load_from_file(self, filepath: Path):
        """
        Load registry from JSON file.
        
        Args:
            filepath: Path to registry file
        """
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        for model_data in data.get('models', []):
            # Reconstruct ModelInfo
            provider = ModelProvider(model_data['provider'])
            
            versions = [
                ModelVersion(**v) for v in model_data.get('versions', [])
            ]
            
            model = ModelInfo(
                model_id=model_data['model_id'],
                display_name=model_data['display_name'],
                provider=provider,
                backend_type=model_data['backend_type'],
                model_name=model_data['model_name'],
                versions=versions,
                default_version=model_data['default_version'],
                capabilities=model_data['capabilities'],
                context_window=model_data['context_window'],
                description=model_data['description'],
                recommended_for=model_data['recommended_for'],
                benchmark_baseline=model_data.get('benchmark_baseline'),
            )
            
            self.register_model(model)
        
        logger.info(f"Loaded {len(self.models)} models from {filepath}")
    
    def compare_models(
        self,
        model_ids: List[str],
    ) -> Dict[str, Any]:
        """
        Generate comparison table for models.
        
        Args:
            model_ids: List of model IDs to compare
            
        Returns:
            Comparison data
        """
        models = [self.get_model(mid) for mid in model_ids]
        models = [m for m in models if m is not None]
        
        if not models:
            return {'error': 'No valid models to compare'}
        
        comparison = {
            'models': [m.model_id for m in models],
            'providers': [m.provider.value for m in models],
            'context_windows': [m.context_window for m in models],
            'capabilities': {
                m.model_id: m.capabilities for m in models
            },
            'baselines': {
                m.model_id: m.benchmark_baseline for m in models
                if m.benchmark_baseline
            },
        }
        
        return comparison
