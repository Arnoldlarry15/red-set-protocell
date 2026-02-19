"""
Tests for Attack Manifest functionality.

Verifies immutable experiment contract generation and validation.
"""

import json
import os
import tempfile

from app.core.config import get_default_config
from app.core.manifest import (
    AgentBoundaries,
    AttackManifest,
    DeterminismConfig,
    FitnessFunctionConfig,
    IterationLimits,
    MutationPolicyConfig,
    ResourceLimits,
    TargetDefinition,
    compute_fitness_fingerprint,
    create_manifest_from_config,
)


class TestManifestDataclasses:
    """Test manifest dataclass structures."""

    def test_target_definition_creation(self):
        """Test TargetDefinition creation and fields."""
        target = TargetDefinition(
            provider="openai",
            model="gpt-4",
            model_revision="observed-2026-01-21",
            endpoint="chat.completions",
            provider_metadata={"api_version": "v1"},
            scope="Test scope",
        )

        assert target.provider == "openai"
        assert target.model == "gpt-4"
        assert target.model_revision == "observed-2026-01-21"
        assert target.endpoint == "chat.completions"
        assert target.provider_metadata == {"api_version": "v1"}
        assert target.scope == "Test scope"

    def test_determinism_config(self):
        """Test DeterminismConfig with seed and RNG."""
        config = DeterminismConfig(seed=12345, rng="pcg64")

        assert config.seed == 12345
        assert config.rng == "pcg64"

    def test_fitness_function_with_fingerprint(self):
        """Test FitnessFunctionConfig includes code fingerprint."""
        fitness = FitnessFunctionConfig(
            function_id="failure-severity-v1",
            version="1.0.0",
            code_fingerprint="abc123",
            thresholds={"minor": 0.3, "major": 0.6, "critical": 0.85},
        )

        assert fitness.function_id == "failure-severity-v1"
        assert fitness.version == "1.0.0"
        assert fitness.code_fingerprint == "abc123"
        assert fitness.thresholds["critical"] == 0.85

    def test_agent_boundaries(self):
        """Test AgentBoundaries enforces separation."""
        boundaries = AgentBoundaries(
            sniper_can_generate=True, sniper_can_score=False, spotter_can_generate=False, spotter_can_score=True
        )

        assert boundaries.sniper_can_generate is True
        assert boundaries.sniper_can_score is False
        assert boundaries.spotter_can_generate is False
        assert boundaries.spotter_can_score is True


class TestAttackManifest:
    """Test AttackManifest creation and serialization."""

    def test_manifest_creation(self):
        """Test creating a complete Attack Manifest."""
        manifest = AttackManifest(
            manifest_id="test-manifest-123",
            protocell_version="1.0.0",
            policy_version="attack-policy-1.0.0",
            timestamp_utc="2026-01-21T12:00:00Z",
            operator_intent="Test intent",
            target=TargetDefinition(
                provider="openai",
                model="gpt-4",
                model_revision="observed-2026-01-21",
                endpoint="chat.completions",
                provider_metadata={},
                scope="Test",
            ),
            determinism=DeterminismConfig(seed=42, rng="pcg64"),
            iteration_limits=IterationLimits(max_generations=10, population_size=5, max_evaluations=50),
            mutation_policy=MutationPolicyConfig(policy_id="test-policy", version="1.0.0", operators=["op1", "op2"]),
            fitness_function=FitnessFunctionConfig(function_id="test-fitness", version="1.0.0", code_fingerprint="test123"),
            agent_boundaries=AgentBoundaries(),
            resource_limits=ResourceLimits(max_runtime_seconds=3600, max_concurrency=1),
        )

        assert manifest.manifest_id == "test-manifest-123"
        assert manifest.protocell_version == "1.0.0"
        assert manifest.determinism.seed == 42

    def test_manifest_to_json(self):
        """Test manifest JSON serialization."""
        manifest = AttackManifest(
            manifest_id="test-123",
            protocell_version="1.0.0",
            policy_version="attack-policy-1.0.0",
            timestamp_utc="2026-01-21T12:00:00Z",
            operator_intent="Test",
            target=TargetDefinition(
                provider="test", model="test", model_revision="test", endpoint="test", provider_metadata={}, scope="test"
            ),
            determinism=DeterminismConfig(seed=42),
            iteration_limits=IterationLimits(max_generations=10, population_size=5, max_evaluations=50),
            mutation_policy=MutationPolicyConfig(policy_id="test", version="1.0.0", operators=[]),
            fitness_function=FitnessFunctionConfig(function_id="test", version="1.0.0", code_fingerprint="test"),
            agent_boundaries=AgentBoundaries(),
            resource_limits=ResourceLimits(max_runtime_seconds=60, max_concurrency=1),
        )

        json_str = manifest.to_json()
        data = json.loads(json_str)

        assert data["manifest_id"] == "test-123"
        assert data["protocell_version"] == "1.0.0"
        assert data["determinism"]["seed"] == 42

    def test_manifest_from_json(self):
        """Test manifest deserialization from JSON."""
        json_data = {
            "manifest_id": "test-456",
            "protocell_version": "1.0.0",
            "policy_version": "attack-policy-1.0.0",
            "timestamp_utc": "2026-01-21T12:00:00Z",
            "operator_intent": "Test",
            "target": {
                "provider": "test",
                "model": "test",
                "model_revision": "test",
                "endpoint": "test",
                "provider_metadata": {},
                "scope": "test",
            },
            "determinism": {"seed": 99, "rng": "pcg64"},
            "iteration_limits": {"max_generations": 20, "population_size": 10, "max_evaluations": 200},
            "mutation_policy": {"policy_id": "test", "version": "1.0.0", "operators": ["op1"]},
            "fitness_function": {
                "function_id": "test",
                "version": "1.0.0",
                "code_fingerprint": "test",
                "thresholds": {"minor": 0.3, "major": 0.6, "critical": 0.85},
            },
            "agent_boundaries": {
                "sniper_can_generate": True,
                "sniper_can_score": False,
                "spotter_can_generate": False,
                "spotter_can_score": True,
            },
            "resource_limits": {"max_runtime_seconds": 120, "max_concurrency": 2},
        }

        manifest = AttackManifest.from_dict(json_data)

        assert manifest.manifest_id == "test-456"
        assert manifest.determinism.seed == 99
        assert manifest.iteration_limits.max_generations == 20

    def test_manifest_save_and_load(self):
        """Test saving and loading manifest from file."""
        manifest = AttackManifest(
            manifest_id="test-save-load",
            protocell_version="1.0.0",
            policy_version="attack-policy-1.0.0",
            timestamp_utc="2026-01-21T12:00:00Z",
            operator_intent="Test",
            target=TargetDefinition(
                provider="test", model="test", model_revision="test", endpoint="test", provider_metadata={}, scope="test"
            ),
            determinism=DeterminismConfig(seed=777),
            iteration_limits=IterationLimits(max_generations=5, population_size=3, max_evaluations=15),
            mutation_policy=MutationPolicyConfig(policy_id="test", version="1.0.0", operators=[]),
            fitness_function=FitnessFunctionConfig(function_id="test", version="1.0.0", code_fingerprint="test"),
            agent_boundaries=AgentBoundaries(),
            resource_limits=ResourceLimits(max_runtime_seconds=60, max_concurrency=1),
        )

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            temp_path = f.name
            manifest.save(temp_path)

        try:
            loaded_manifest = AttackManifest.load(temp_path)
            assert loaded_manifest.manifest_id == "test-save-load"
            assert loaded_manifest.determinism.seed == 777
        finally:
            os.unlink(temp_path)

    def test_manifest_fingerprint(self):
        """Test manifest fingerprint generation."""
        manifest = AttackManifest(
            manifest_id="test-fingerprint",
            protocell_version="1.0.0",
            policy_version="attack-policy-1.0.0",
            timestamp_utc="2026-01-21T12:00:00Z",
            operator_intent="Test",
            target=TargetDefinition(
                provider="test", model="test", model_revision="test", endpoint="test", provider_metadata={}, scope="test"
            ),
            determinism=DeterminismConfig(seed=42),
            iteration_limits=IterationLimits(max_generations=10, population_size=5, max_evaluations=50),
            mutation_policy=MutationPolicyConfig(policy_id="test", version="1.0.0", operators=[]),
            fitness_function=FitnessFunctionConfig(function_id="test", version="1.0.0", code_fingerprint="test"),
            agent_boundaries=AgentBoundaries(),
            resource_limits=ResourceLimits(max_runtime_seconds=60, max_concurrency=1),
        )

        fingerprint = manifest.get_fingerprint()
        assert len(fingerprint) == 64  # SHA-256 produces 64-char hex string
        assert isinstance(fingerprint, str)

        # Same manifest should produce same fingerprint
        fingerprint2 = manifest.get_fingerprint()
        assert fingerprint == fingerprint2


class TestManifestCreation:
    """Test manifest creation from config."""

    def test_create_manifest_from_config(self):
        """Test creating manifest from RSPConfig."""
        config = get_default_config()
        manifest = create_manifest_from_config(config, seed=12345)

        assert manifest.protocell_version == "1.0.0"
        assert manifest.policy_version == "attack-policy-1.0.0"
        assert manifest.determinism.seed == 12345
        assert manifest.determinism.rng == "pcg64"
        assert manifest.agent_boundaries.sniper_can_score is False
        assert manifest.agent_boundaries.spotter_can_generate is False

    def test_manifest_includes_operator_intent(self):
        """Test manifest includes operator intent declaration."""
        config = get_default_config()
        manifest = create_manifest_from_config(config)

        assert "Authorized adversarial testing" in manifest.operator_intent
        assert "failure discovery" in manifest.operator_intent

    def test_manifest_includes_fitness_fingerprint(self):
        """Test manifest includes fitness code fingerprint."""
        config = get_default_config()
        manifest = create_manifest_from_config(config)

        assert manifest.fitness_function.code_fingerprint
        assert len(manifest.fitness_function.code_fingerprint) > 0

    def test_compute_fitness_fingerprint(self):
        """Test fitness fingerprint computation."""
        fingerprint = compute_fitness_fingerprint()

        # Should return valid SHA-256 hash or fallback
        assert isinstance(fingerprint, str)
        assert len(fingerprint) > 0

    def test_manifest_target_snapshot(self):
        """Test manifest captures target snapshot."""
        config = get_default_config()
        manifest = create_manifest_from_config(config)

        assert manifest.target.model_revision.startswith("observed-")
        assert "observed_at" in manifest.target.provider_metadata
