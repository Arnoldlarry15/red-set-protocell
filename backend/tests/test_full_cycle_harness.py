"""
Tests for run_full_cycle.py and determinism verification.

These tests verify that the full cycle test harness:
1. Properly computes interaction hashes
2. Maintains audit trail structure
3. Can be imported and used programmatically
"""

import json
import sys
from pathlib import Path

import pytest

# Add scripts directory to path before importing from it
scripts_dir = Path(__file__).parent.parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from run_full_cycle import FullCycleRunner, compute_interaction_hash  # noqa: E402


class TestHashComputation:
    """Test hash computation for determinism verification."""

    def test_compute_interaction_hash_deterministic(self):
        """Test that identical data produces identical hashes."""
        data1 = {
            "seed": 42,
            "rounds": 10,
            "configuration": {"backend": "openai", "model": "gpt-4"},
            "round_details": [{"round": 1, "score": 0.5}, {"round": 2, "score": 0.3}],
        }

        data2 = {
            "seed": 42,
            "rounds": 10,
            "configuration": {"backend": "openai", "model": "gpt-4"},
            "round_details": [{"round": 1, "score": 0.5}, {"round": 2, "score": 0.3}],
        }

        hash1 = compute_interaction_hash(data1)
        hash2 = compute_interaction_hash(data2)

        assert hash1 == hash2
        assert len(hash1) == 64  # SHA-256 produces 64-char hex string

    def test_compute_interaction_hash_different_data(self):
        """Test that different data produces different hashes."""
        data1 = {"seed": 42, "rounds": 10, "round_details": [{"round": 1, "score": 0.5}]}

        data2 = {"seed": 43, "rounds": 10, "round_details": [{"round": 1, "score": 0.5}]}  # Different seed

        hash1 = compute_interaction_hash(data1)
        hash2 = compute_interaction_hash(data2)

        assert hash1 != hash2

    def test_compute_interaction_hash_order_independent(self):
        """Test that key order doesn't affect hash (canonical representation)."""
        data1 = {"seed": 42, "rounds": 10, "configuration": {"backend": "openai", "model": "gpt-4"}}

        data2 = {"configuration": {"model": "gpt-4", "backend": "openai"}, "rounds": 10, "seed": 42}

        hash1 = compute_interaction_hash(data1)
        hash2 = compute_interaction_hash(data2)

        assert hash1 == hash2


class TestFullCycleRunner:
    """Test FullCycleRunner initialization and structure."""

    def test_initialization(self):
        """Test that FullCycleRunner initializes correctly."""
        runner = FullCycleRunner(seed=42, rounds=10, output_dir="test_logs")

        assert runner.seed == 42
        assert runner.rounds == 10
        assert runner.output_dir == Path("test_logs")

        # Check audit trail structure
        assert "metadata" in runner.audit_trail
        assert "configuration" in runner.audit_trail
        assert "role_separation" in runner.audit_trail
        assert "round_details" in runner.audit_trail
        assert "statistics" in runner.audit_trail
        assert "hash" in runner.audit_trail

        # Check metadata
        assert runner.audit_trail["metadata"]["seed"] == 42
        assert runner.audit_trail["metadata"]["rounds"] == 10

    def test_audit_trail_structure(self):
        """Test that audit trail has correct structure."""
        runner = FullCycleRunner(seed=15, rounds=5)

        # Verify role_separation structure
        assert "sniper_instructions" in runner.audit_trail["role_separation"]
        assert "spotter_instructions" in runner.audit_trail["role_separation"]
        assert "target_interactions" in runner.audit_trail["role_separation"]

        # Verify these are lists
        assert isinstance(runner.audit_trail["role_separation"]["sniper_instructions"], list)
        assert isinstance(runner.audit_trail["role_separation"]["spotter_instructions"], list)
        assert isinstance(runner.audit_trail["role_separation"]["target_interactions"], list)

        # Verify round_details is a list
        assert isinstance(runner.audit_trail["round_details"], list)


class TestDeterminismFeatures:
    """Test determinism-related features."""

    def test_seed_setting_deterministic(self):
        """Test that seed setting produces deterministic behavior."""
        import random

        import numpy as np
        from run_full_cycle import set_seed

        # Set seed and generate some random numbers
        set_seed(42)
        r1 = random.random()
        n1 = np.random.random()

        # Reset seed and generate again
        set_seed(42)
        r2 = random.random()
        n2 = np.random.random()

        # Should be identical
        assert r1 == r2
        assert n1 == n2

    def test_different_seeds_produce_different_results(self):
        """Test that different seeds produce different results."""
        import random

        import numpy as np
        from run_full_cycle import set_seed

        set_seed(42)
        r1 = random.random()
        n1 = np.random.random()

        set_seed(43)
        r2 = random.random()
        n2 = np.random.random()

        # Should be different
        assert r1 != r2
        assert n1 != n2


class TestAuditTrailIntegrity:
    """Test audit trail data integrity."""

    def test_audit_trail_json_serializable(self):
        """Test that audit trail can be serialized to JSON."""
        runner = FullCycleRunner(seed=42, rounds=10)

        # Should be JSON serializable
        try:
            json_str = json.dumps(runner.audit_trail)
            assert len(json_str) > 0

            # Should be deserializable
            data = json.loads(json_str)
            assert data["metadata"]["seed"] == 42
        except (TypeError, ValueError) as e:
            pytest.fail(f"Audit trail is not JSON serializable: {e}")

    def test_hashable_data_excludes_timestamps(self):
        """Test that hash computation excludes non-deterministic data."""
        runner = FullCycleRunner(seed=42, rounds=10)

        # The hashable data should not include timestamps
        hashable_data = {
            "seed": runner.audit_trail["metadata"]["seed"],
            "rounds": runner.audit_trail["metadata"]["rounds"],
            "configuration": runner.audit_trail["configuration"],
            "round_details": [],
        }

        # Should be able to compute hash
        hash_value = compute_interaction_hash(hashable_data)
        assert len(hash_value) == 64

        # Verify timestamp is in metadata but not in hashable data
        assert "timestamp" in runner.audit_trail["metadata"]
        assert "timestamp" not in hashable_data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
