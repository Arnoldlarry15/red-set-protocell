"""
Red Set ProtoCell - Attack Manifest

Machine-readable record of experiment parameters produced at run start.
This is the experiment contract: a record of intent, not configuration.

Purpose:
--------
Every run produces exactly one Attack Manifest. No exceptions.
The manifest enables reproducible experimentation by capturing:
- Policy versions (what rules governed this run)
- System configuration (what constraints were in effect)
- Target definition (what system was tested)
- Evolutionary parameters (how attacks were generated)

This single artifact upgrades Red Set ProtoCell from "tool" to "instrument."

Guarantees:
-----------
1. Immutable: Written once at run start, never modified
2. Complete: Contains all parameters needed for reproducibility
3. Linked: All Failure Specimens reference their parent manifest
4. Auditable: Timestamp and version tracking for compliance
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Dict, Optional
import json
import hashlib
import uuid


@dataclass
class TargetDefinition:
    """Target system under test."""
    model_name: str
    provider: str
    endpoint: str
    scope_description: str
    api_version: Optional[str] = None


@dataclass
class MutationPolicy:
    """Mutation operators enabled for this run."""
    operator_id: str
    operator_version: str
    enabled: bool = True


@dataclass
class FitnessFunction:
    """Fitness function configuration."""
    function_id: str
    function_version: str
    threshold: float
    scoring_weights: Dict[str, float] = field(default_factory=dict)


@dataclass
class AgentBoundaries:
    """Dual-agent separation assertions."""
    sniper_cannot_score: bool = True
    spotter_cannot_generate: bool = True
    strict_separation: bool = True


@dataclass
class ResourceLimits:
    """Resource constraints for this run."""
    max_generations: int
    population_size: int
    total_evaluations: int
    time_budget_seconds: Optional[int] = None
    concurrency_cap: Optional[int] = None
    cost_limit_usd: Optional[float] = None


@dataclass
class AttackManifest:
    """
    Attack Manifest - The Experiment Contract
    
    This is NOT configuration. This is a record of intent captured at run start.
    It allows you to say, with a straight face:
    "These failures were produced under these constraints."
    
    Once written, this manifest is immutable and referenced by all Failure Specimens.
    """
    # Versioning
    protocell_version: str
    policy_version: str
    manifest_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp_utc: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    # Target
    target: TargetDefinition = field(default_factory=lambda: TargetDefinition(
        model_name="unknown",
        provider="unknown",
        endpoint="unknown",
        scope_description="undefined"
    ))
    
    # Evolutionary parameters
    seed: Optional[int] = None
    iteration_limits: ResourceLimits = field(default_factory=lambda: ResourceLimits(
        max_generations=100,
        population_size=10,
        total_evaluations=1000
    ))
    
    # Mutation configuration
    mutation_policy: List[MutationPolicy] = field(default_factory=list)
    
    # Fitness configuration
    fitness_function: FitnessFunction = field(default_factory=lambda: FitnessFunction(
        function_id="default",
        function_version="1.0.0",
        threshold=0.5
    ))
    
    # Agent architecture
    agent_boundaries: AgentBoundaries = field(default_factory=AgentBoundaries)
    
    # Additional metadata
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """Convert manifest to dictionary."""
        return asdict(self)
    
    def to_json(self, indent: int = 2) -> str:
        """Convert manifest to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)
    
    def save(self, filepath: str) -> None:
        """Save manifest to file."""
        with open(filepath, 'w') as f:
            f.write(self.to_json())
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'AttackManifest':
        """Create manifest from dictionary."""
        # Reconstruct nested objects
        if 'target' in data and isinstance(data['target'], dict):
            data['target'] = TargetDefinition(**data['target'])
        
        if 'iteration_limits' in data and isinstance(data['iteration_limits'], dict):
            data['iteration_limits'] = ResourceLimits(**data['iteration_limits'])
        
        if 'mutation_policy' in data and isinstance(data['mutation_policy'], list):
            data['mutation_policy'] = [
                MutationPolicy(**m) if isinstance(m, dict) else m 
                for m in data['mutation_policy']
            ]
        
        if 'fitness_function' in data and isinstance(data['fitness_function'], dict):
            data['fitness_function'] = FitnessFunction(**data['fitness_function'])
        
        if 'agent_boundaries' in data and isinstance(data['agent_boundaries'], dict):
            data['agent_boundaries'] = AgentBoundaries(**data['agent_boundaries'])
        
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'AttackManifest':
        """Create manifest from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    @classmethod
    def load(cls, filepath: str) -> 'AttackManifest':
        """Load manifest from file."""
        with open(filepath, 'r') as f:
            return cls.from_json(f.read())
    
    def get_fingerprint(self) -> str:
        """Generate SHA-256 fingerprint of manifest for auditing."""
        manifest_json = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(manifest_json.encode()).hexdigest()


def create_manifest_from_config(config) -> AttackManifest:
    """
    Create an Attack Manifest from RSP configuration.
    
    This function bridges the gap between runtime configuration and
    the immutable experiment record.
    
    Args:
        config: RSPConfig instance
    
    Returns:
        AttackManifest ready to be saved
    """
    # Extract target information
    target = TargetDefinition(
        model_name=getattr(config.target, 'model', 'unknown'),
        provider=getattr(config.target, 'backend', 'unknown'),
        endpoint=getattr(config.target, 'api_endpoint', 'unknown'),
        scope_description=getattr(config.target, 'scope', 'Automated red teaming test')
    )
    
    # Extract mutation policy
    mutation_policy = [
        MutationPolicy(
            operator_id="semantic_perturbation",
            operator_version="1.0.0",
            enabled=True
        ),
        MutationPolicy(
            operator_id="adversarial_suffix",
            operator_version="1.0.0",
            enabled=True
        ),
        MutationPolicy(
            operator_id="role_play_injection",
            operator_version="1.0.0",
            enabled=True
        ),
        MutationPolicy(
            operator_id="context_manipulation",
            operator_version="1.0.0",
            enabled=True
        ),
    ]
    
    # Extract fitness function
    fitness_function = FitnessFunction(
        function_id="three_layer_taxonomy",
        function_version="1.0.0",
        threshold=config.spotter.confidence_threshold,
        scoring_weights={
            "linguistic_safety": config.spotter.linguistic_safety_weight,
            "security_exploitability": config.spotter.security_exploitability_weight,
            "cognitive_stability": config.spotter.cognitive_stability_weight
        }
    )
    
    # Extract resource limits
    iteration_limits = ResourceLimits(
        max_generations=config.orchestrator.max_rounds,
        population_size=config.sniper.evolution_pool_size,
        total_evaluations=config.orchestrator.max_rounds * config.sniper.evolution_pool_size,
        time_budget_seconds=config.orchestrator.round_timeout_seconds * config.orchestrator.max_rounds,
        concurrency_cap=config.orchestrator.concurrent_rounds if config.orchestrator.concurrent_evaluations else 1
    )
    
    # Create manifest
    manifest = AttackManifest(
        protocell_version="1.0.0",
        policy_version="attack-policy-1.0.0",
        target=target,
        seed=None,  # TODO: Add RNG seed support
        iteration_limits=iteration_limits,
        mutation_policy=mutation_policy,
        fitness_function=fitness_function,
        agent_boundaries=AgentBoundaries(),
        description="Automated adversarial testing session"
    )
    
    return manifest
