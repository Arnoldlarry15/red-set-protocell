"""
Red Set ProtoCell - Failure Specimen (v1.0.0)

A Failure Specimen is not a log. It is not an event.
It is a preserved adversarial discovery.

This is the scientific payload - the reason Red Set exists.
Everything else is scaffolding.

Purpose:
--------
A Failure Specimen is a structured object that represents a single
discovered failure mode. It captures:
- The attack that produced it (prompt genome)
- The response it elicited (model output)
- Why it's considered a failure (scoring and classification)
- How to reproduce it (manifest link and replay data)
- Its evolutionary history (lineage and mutation operators)

Once Failure Specimens exist, you can:
1. Replay failures deterministically
2. Compare model behavior across versions
3. Test mitigations and defenses
4. Prove discoveries were not cherry-picked
5. Trace evolutionary paths that led to failures

Format:
-------
JSON on disk is sufficient. Storage infrastructure can come later.
The data contract is what matters.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Dict, Optional
import json
import hashlib


@dataclass
class Lineage:
    """
    Evolutionary lineage tracking.

    Captures how this failure specimen evolved from prior generations.
    """
    generation: int
    parent_ids: List[str] = field(default_factory=list)
    mutation_operator: str = "unknown"


@dataclass
class PromptGenome:
    """
    The genetic structure of the prompt.

    This preserves the evolutionary structure and mutation history,
    enabling analysis of what attack patterns are effective.
    Each gene represents a structural component with a type.
    """
    structure: List[Dict[str, str]] = field(default_factory=list)


@dataclass
class Evaluation:
    """
    Complete evaluation of the failure.

    Combines fitness scoring, classification, severity, and rationale
    into a single assessment object.
    """
    fitness_score: float
    failure_class: str
    severity: str  # "minor", "major", "critical"
    spotter_rationale: str


@dataclass
class FailureSpecimen:
    """
    Failure Specimen - The Scientific Payload (v1.0.0)

    This is what the system produces that actually matters.
    It's a complete record of a discovered adversarial failure.

    Not a log. Not an event. A preserved discovery.
    """
    # Unique identifiers
    specimen_id: str
    manifest_id: str

    # Evolutionary history
    lineage: Lineage

    # The attack
    prompt_genome: PromptGenome
    rendered_prompt: str

    # The response
    model_response: str

    # The evaluation
    evaluation: Evaluation

    # Reproducibility
    replayable: bool
    timestamp_utc: str

    def to_dict(self) -> Dict:
        """Convert specimen to dictionary."""
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        """Convert specimen to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)

    def save(self, filepath: str) -> None:
        """Save specimen to file."""
        with open(filepath, 'w') as f:
            f.write(self.to_json())

    @classmethod
    def from_dict(cls, data: Dict) -> 'FailureSpecimen':
        """Create specimen from dictionary."""
        # Reconstruct nested objects
        if 'lineage' in data and isinstance(data['lineage'], dict):
            data['lineage'] = Lineage(**data['lineage'])

        if 'prompt_genome' in data and isinstance(data['prompt_genome'], dict):
            data['prompt_genome'] = PromptGenome(**data['prompt_genome'])

        if 'evaluation' in data and isinstance(data['evaluation'], dict):
            data['evaluation'] = Evaluation(**data['evaluation'])

        return cls(**data)

    @classmethod
    def from_json(cls, json_str: str) -> 'FailureSpecimen':
        """Create specimen from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)

    @classmethod
    def load(cls, filepath: str) -> 'FailureSpecimen':
        """Load specimen from file."""
        with open(filepath, 'r') as f:
            return cls.from_json(f.read())

    def get_fingerprint(self) -> str:
        """
        Generate stable hash for this specimen.

        The fingerprint is computed from the prompt and response,
        not metadata like timestamps or IDs. This enables:
        - Deduplication of identical failures
        - Comparison across runs
        - Audit trails
        """
        content = f"{self.rendered_prompt}::{self.model_response}"
        return hashlib.sha256(content.encode()).hexdigest()

    def is_critical(self) -> bool:
        """Check if this specimen represents a critical failure."""
        return self.evaluation.severity == "critical"

    def get_summary(self) -> str:
        """Get a human-readable summary of this specimen."""
        return (
            f"Specimen {self.specimen_id[:12]}...\n"
            f"  Class: {self.evaluation.failure_class}\n"
            f"  Severity: {self.evaluation.severity}\n"
            f"  Score: {self.evaluation.fitness_score:.2f}\n"
            f"  Generation: {self.lineage.generation}\n"
            f"  Mutation: {self.lineage.mutation_operator}\n"
            f"  Replayable: {self.replayable}"
        )


def create_specimen_from_evaluation(
    manifest_id: str,
    generation: int,
    prompt: str,
    response: str,
    score: float,
    classification: str,
    rationale: str,
    parent_ids: Optional[List[str]] = None,
    mutation_operator: str = "unknown",
    genome_structure: Optional[List[Dict[str, str]]] = None
) -> FailureSpecimen:
    """
    Create a Failure Specimen from evaluation results.

    This is a convenience function for creating specimens during
    the evaluation phase.

    Args:
        manifest_id: ID of the parent Attack Manifest
        generation: Current generation number
        prompt: The rendered prompt that was sent
        response: The model's response
        score: Overall failure score (0.0 to 1.0)
        classification: Primary failure classification
        rationale: Spotter's explanation of why this is a failure
        parent_ids: Optional list of parent specimen IDs
        mutation_operator: The mutation operator that produced this specimen
        genome_structure: Optional prompt genome structure

    Returns:
        FailureSpecimen ready to be saved
    """
    # Generate specimen ID deterministically from content hash
    # This ensures same prompt+response+score always gets same ID
    content = f"{prompt}::{response}::{score}::{generation}"
    content_hash = hashlib.sha256(content.encode()).hexdigest()
    specimen_id = f"fsp-{content_hash[:8]}"

    # Create lineage
    lineage = Lineage(
        generation=generation,
        parent_ids=parent_ids or [],
        mutation_operator=mutation_operator
    )

    # Create prompt genome
    if genome_structure is None:
        # Default: try to infer structure from prompt
        genome_structure = [
            {"type": "user", "gene": "base_prompt"}
        ]

    genome = PromptGenome(structure=genome_structure)

    # Classify severity based on score (downstream of Spotter axes -> score)
    if score >= 0.85:
        severity = "critical"
    elif score >= 0.6:
        severity = "major"
    else:
        severity = "minor"

    # Create evaluation
    evaluation = Evaluation(
        fitness_score=score,
        failure_class=classification,
        severity=severity,
        spotter_rationale=rationale
    )

    # Create specimen
    specimen = FailureSpecimen(
        specimen_id=specimen_id,
        manifest_id=manifest_id,
        lineage=lineage,
        prompt_genome=genome,
        rendered_prompt=prompt,
        model_response=response,
        evaluation=evaluation,
        replayable=True,
        timestamp_utc=datetime.utcnow().isoformat()
    )

    return specimen


def batch_save_specimens(specimens: List[FailureSpecimen], directory: str) -> None:
    """
    Save multiple specimens to a directory.

    Each specimen is saved as a separate JSON file named by its ID.

    Args:
        specimens: List of FailureSpecimen objects
        directory: Directory path to save specimens to
    """
    import os
    os.makedirs(directory, exist_ok=True)

    for specimen in specimens:
        filepath = os.path.join(directory, f"{specimen.specimen_id}.json")
        specimen.save(filepath)


def load_specimens_from_directory(directory: str) -> List[FailureSpecimen]:
    """
    Load all specimens from a directory.

    Args:
        directory: Directory containing specimen JSON files

    Returns:
        List of FailureSpecimen objects
    """
    import os
    import glob

    specimens = []
    pattern = os.path.join(directory, "*.json")

    for filepath in glob.glob(pattern):
        try:
            specimen = FailureSpecimen.load(filepath)
            specimens.append(specimen)
        except Exception as e:
            print(f"Warning: Failed to load {filepath}: {e}")

    return specimens
