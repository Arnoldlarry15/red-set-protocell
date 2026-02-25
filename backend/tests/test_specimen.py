"""
Tests for Failure Specimen functionality.

Verifies preserved adversarial discovery structure and serialization.
"""

import json
import os
import tempfile

from app.core.specimen import (
    Evaluation,
    FailureSpecimen,
    Lineage,
    PromptGenome,
    batch_save_specimens,
    create_specimen_from_evaluation,
    load_specimens_from_directory,
)


class TestSpecimenDataclasses:
    """Test specimen dataclass structures."""

    def test_lineage_creation(self):
        """Test Lineage tracks evolutionary history."""
        lineage = Lineage(
            generation=5,
            parent_ids=["fsp-123", "fsp-456"],
            mutation_operator="instruction_conflict",
        )

        assert lineage.generation == 5
        assert len(lineage.parent_ids) == 2
        assert lineage.mutation_operator == "instruction_conflict"

    def test_prompt_genome_structure(self):
        """Test PromptGenome preserves attack structure."""
        genome = PromptGenome(
            structure=[
                {"type": "system", "gene": "authority_shift"},
                {"type": "user", "gene": "policy_pressure"},
            ]
        )

        assert len(genome.structure) == 2
        assert genome.structure[0]["type"] == "system"
        assert genome.structure[1]["gene"] == "policy_pressure"

    def test_evaluation_structure(self):
        """Test Evaluation contains complete assessment."""
        evaluation = Evaluation(
            fitness_score=0.85,
            failure_class="policy_override",
            severity="critical",
            spotter_rationale="Model bypassed safety controls",
        )

        assert evaluation.fitness_score == 0.85
        assert evaluation.failure_class == "policy_override"
        assert evaluation.severity == "critical"
        assert "bypassed" in evaluation.spotter_rationale


class TestFailureSpecimen:
    """Test FailureSpecimen creation and methods."""

    def test_specimen_creation(self):
        """Test creating a complete Failure Specimen."""
        specimen = FailureSpecimen(
            specimen_id="fsp-test123",
            manifest_id="manifest-456",
            lineage=Lineage(
                generation=10,
                parent_ids=["fsp-parent1"],
                mutation_operator="semantic_twist",
            ),
            prompt_genome=PromptGenome(structure=[{"type": "user", "gene": "test"}]),
            rendered_prompt="Test prompt",
            model_response="Test response",
            evaluation=Evaluation(
                fitness_score=0.7,
                failure_class="test_failure",
                severity="major",
                spotter_rationale="Test reason",
            ),
            replayable=True,
            timestamp_utc="2026-01-21T12:00:00Z",
        )

        assert specimen.specimen_id == "fsp-test123"
        assert specimen.manifest_id == "manifest-456"
        assert specimen.lineage.generation == 10
        assert specimen.replayable is True

    def test_specimen_to_json(self):
        """Test specimen JSON serialization."""
        specimen = FailureSpecimen(
            specimen_id="fsp-json-test",
            manifest_id="manifest-json",
            lineage=Lineage(generation=1, parent_ids=[], mutation_operator="test"),
            prompt_genome=PromptGenome(structure=[]),
            rendered_prompt="Test",
            model_response="Response",
            evaluation=Evaluation(
                fitness_score=0.5,
                failure_class="test",
                severity="minor",
                spotter_rationale="Test",
            ),
            replayable=True,
            timestamp_utc="2026-01-21T12:00:00Z",
        )

        json_str = specimen.to_json()
        data = json.loads(json_str)

        assert data["specimen_id"] == "fsp-json-test"
        assert data["manifest_id"] == "manifest-json"
        assert data["evaluation"]["fitness_score"] == 0.5

    def test_specimen_from_json(self):
        """Test specimen deserialization from JSON."""
        json_data = {
            "specimen_id": "fsp-deserialize",
            "manifest_id": "manifest-test",
            "lineage": {
                "generation": 5,
                "parent_ids": ["fsp-p1", "fsp-p2"],
                "mutation_operator": "test_op",
            },
            "prompt_genome": {"structure": [{"type": "user", "gene": "test"}]},
            "rendered_prompt": "Test prompt",
            "model_response": "Test response",
            "evaluation": {
                "fitness_score": 0.9,
                "failure_class": "critical_test",
                "severity": "critical",
                "spotter_rationale": "Severe issue",
            },
            "replayable": True,
            "timestamp_utc": "2026-01-21T12:00:00Z",
        }

        specimen = FailureSpecimen.from_dict(json_data)

        assert specimen.specimen_id == "fsp-deserialize"
        assert specimen.lineage.generation == 5
        assert specimen.evaluation.fitness_score == 0.9
        assert specimen.is_critical() is True

    def test_specimen_save_and_load(self):
        """Test saving and loading specimen from file."""
        specimen = FailureSpecimen(
            specimen_id="fsp-save-load",
            manifest_id="manifest-save",
            lineage=Lineage(generation=3, parent_ids=[], mutation_operator="test"),
            prompt_genome=PromptGenome(structure=[]),
            rendered_prompt="Save test",
            model_response="Load test",
            evaluation=Evaluation(
                fitness_score=0.6,
                failure_class="test",
                severity="major",
                spotter_rationale="Test",
            ),
            replayable=True,
            timestamp_utc="2026-01-21T12:00:00Z",
        )

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            temp_path = f.name
            specimen.save(temp_path)

        try:
            loaded = FailureSpecimen.load(temp_path)
            assert loaded.specimen_id == "fsp-save-load"
            assert loaded.manifest_id == "manifest-save"
            assert loaded.evaluation.fitness_score == 0.6
        finally:
            os.unlink(temp_path)

    def test_specimen_fingerprint(self):
        """Test specimen fingerprint generation."""
        specimen = FailureSpecimen(
            specimen_id="fsp-fingerprint",
            manifest_id="manifest-test",
            lineage=Lineage(generation=1, parent_ids=[], mutation_operator="test"),
            prompt_genome=PromptGenome(structure=[]),
            rendered_prompt="Fingerprint prompt",
            model_response="Fingerprint response",
            evaluation=Evaluation(
                fitness_score=0.5,
                failure_class="test",
                severity="minor",
                spotter_rationale="Test",
            ),
            replayable=True,
            timestamp_utc="2026-01-21T12:00:00Z",
        )

        fingerprint = specimen.get_fingerprint()
        assert len(fingerprint) == 64  # SHA-256
        assert isinstance(fingerprint, str)

        # Same content should produce same fingerprint
        fingerprint2 = specimen.get_fingerprint()
        assert fingerprint == fingerprint2

    def test_specimen_is_critical(self):
        """Test is_critical detection."""
        critical_specimen = FailureSpecimen(
            specimen_id="fsp-critical",
            manifest_id="manifest-test",
            lineage=Lineage(generation=1, parent_ids=[], mutation_operator="test"),
            prompt_genome=PromptGenome(structure=[]),
            rendered_prompt="Test",
            model_response="Test",
            evaluation=Evaluation(
                fitness_score=0.95,
                failure_class="test",
                severity="critical",
                spotter_rationale="Test",
            ),
            replayable=True,
            timestamp_utc="2026-01-21T12:00:00Z",
        )

        assert critical_specimen.is_critical() is True

        minor_specimen = FailureSpecimen(
            specimen_id="fsp-minor",
            manifest_id="manifest-test",
            lineage=Lineage(generation=1, parent_ids=[], mutation_operator="test"),
            prompt_genome=PromptGenome(structure=[]),
            rendered_prompt="Test",
            model_response="Test",
            evaluation=Evaluation(
                fitness_score=0.4,
                failure_class="test",
                severity="minor",
                spotter_rationale="Test",
            ),
            replayable=True,
            timestamp_utc="2026-01-21T12:00:00Z",
        )

        assert minor_specimen.is_critical() is False

    def test_specimen_summary(self):
        """Test get_summary method."""
        specimen = FailureSpecimen(
            specimen_id="fsp-summary-test",
            manifest_id="manifest-test",
            lineage=Lineage(generation=7, parent_ids=[], mutation_operator="role_injection"),
            prompt_genome=PromptGenome(structure=[]),
            rendered_prompt="Test",
            model_response="Test",
            evaluation=Evaluation(
                fitness_score=0.75,
                failure_class="policy_violation",
                severity="major",
                spotter_rationale="Test",
            ),
            replayable=True,
            timestamp_utc="2026-01-21T12:00:00Z",
        )

        summary = specimen.get_summary()
        assert "fsp-summary" in summary
        assert "policy_violation" in summary
        assert "major" in summary
        assert "0.75" in summary
        assert "role_injection" in summary


class TestSpecimenCreation:
    """Test specimen creation helpers."""

    def test_create_specimen_from_evaluation(self):
        """Test creating specimen from evaluation results."""
        specimen = create_specimen_from_evaluation(
            manifest_id="manifest-test",
            generation=5,
            prompt="Test adversarial prompt",
            response="Model response",
            score=0.8,
            classification="jailbreak",
            rationale="Successfully bypassed controls",
            parent_ids=["fsp-parent1", "fsp-parent2"],
            mutation_operator="instruction_conflict",
        )

        assert specimen.manifest_id == "manifest-test"
        assert specimen.lineage.generation == 5
        assert specimen.rendered_prompt == "Test adversarial prompt"
        assert specimen.model_response == "Model response"
        assert specimen.evaluation.fitness_score == 0.8
        assert specimen.evaluation.failure_class == "jailbreak"
        assert specimen.lineage.mutation_operator == "instruction_conflict"
        assert len(specimen.lineage.parent_ids) == 2
        assert specimen.replayable is True

    def test_severity_classification(self):
        """Test automatic severity classification."""
        # Critical
        critical = create_specimen_from_evaluation(
            manifest_id="test",
            generation=1,
            prompt="test",
            response="test",
            score=0.90,
            classification="test",
            rationale="test",
        )
        assert critical.evaluation.severity == "critical"

        # Major
        major = create_specimen_from_evaluation(
            manifest_id="test",
            generation=1,
            prompt="test",
            response="test",
            score=0.65,
            classification="test",
            rationale="test",
        )
        assert major.evaluation.severity == "major"

        # Minor
        minor = create_specimen_from_evaluation(
            manifest_id="test",
            generation=1,
            prompt="test",
            response="test",
            score=0.35,
            classification="test",
            rationale="test",
        )
        assert minor.evaluation.severity == "minor"

    def test_deterministic_specimen_id(self):
        """Test specimen IDs are deterministic based on content."""
        specimen1 = create_specimen_from_evaluation(
            manifest_id="test",
            generation=1,
            prompt="same prompt",
            response="same response",
            score=0.5,
            classification="test",
            rationale="test",
        )

        specimen2 = create_specimen_from_evaluation(
            manifest_id="test",
            generation=1,
            prompt="same prompt",
            response="same response",
            score=0.5,
            classification="test",
            rationale="test",
        )

        # Same content should produce same ID
        assert specimen1.specimen_id == specimen2.specimen_id

    def test_custom_genome_structure(self):
        """Test specimen with custom genome structure."""
        specimen = create_specimen_from_evaluation(
            manifest_id="test",
            generation=1,
            prompt="test",
            response="test",
            score=0.5,
            classification="test",
            rationale="test",
            genome_structure=[
                {"type": "system", "gene": "custom_authority"},
                {"type": "user", "gene": "custom_instruction"},
            ],
        )

        assert len(specimen.prompt_genome.structure) == 2
        assert specimen.prompt_genome.structure[0]["gene"] == "custom_authority"


class TestSpecimenBatchOperations:
    """Test batch operations on specimens."""

    def test_batch_save_specimens(self):
        """Test saving multiple specimens to directory."""
        specimens = [
            create_specimen_from_evaluation(
                manifest_id="test",
                generation=i,
                prompt=f"prompt{i}",
                response=f"response{i}",
                score=0.5 + i * 0.1,
                classification="test",
                rationale="test",
            )
            for i in range(3)
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            batch_save_specimens(specimens, temp_dir)

            # Verify files were created
            files = os.listdir(temp_dir)
            assert len(files) == 3
            assert all(f.endswith(".json") for f in files)

    def test_load_specimens_from_directory(self):
        """Test loading multiple specimens from directory."""
        specimens = [
            create_specimen_from_evaluation(
                manifest_id="test",
                generation=i,
                prompt=f"prompt{i}",
                response=f"response{i}",
                score=0.5,
                classification="test",
                rationale="test",
            )
            for i in range(5)
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            batch_save_specimens(specimens, temp_dir)
            loaded = load_specimens_from_directory(temp_dir)

            assert len(loaded) == 5
            # Verify all specimens were loaded correctly
            loaded_ids = {s.specimen_id for s in loaded}
            original_ids = {s.specimen_id for s in specimens}
            assert loaded_ids == original_ids
