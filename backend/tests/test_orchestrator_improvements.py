"""
Tests for orchestrator improvements: async StateManager, evolution modes,
EGG auditor, and zero-retention cleanup.
"""

import pytest
import tempfile
import os
import shutil
from app.agents.orchestrator import Orchestrator, StateManager, RoundResult
from app.engines.scoring import ScoringEngine
from app.core.egg_auditor import EGGAuditor


@pytest.fixture
def temp_db():
    """Create a temporary database file for testing."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    # Cleanup
    try:
        os.unlink(path)
    except Exception:
        pass


@pytest.fixture
def temp_artifacts_dir():
    """Create a temporary artifacts directory for testing."""
    path = tempfile.mkdtemp(prefix="rsp_test_artifacts_")
    yield path
    # Cleanup
    try:
        shutil.rmtree(path)
    except Exception:
        pass


class MockAgent:
    """Mock agent for testing."""

    def __init__(self):
        self.statistics = {"total": 0}

    def get_statistics(self):
        return self.statistics


class MockSniper(MockAgent):
    """Mock Sniper agent."""

    def __init__(self):
        super().__init__()
        self.mutation_engine = MockMutationEngine()

    async def generate_prompt(self, prior_metadata):
        from app.agents.sniper import AttackDomain

        return "test prompt", AttackDomain.PROMPT_INJECTION

    def update_prompt_score(self, prompt, score, structured_feedback=None):
        """Update prompt score with optional structured feedback."""
        pass


class MockMutationEngine:
    """Mock mutation engine."""

    def get_statistics(self):
        return {"total_mutations": 0}


class MockTarget(MockAgent):
    """Mock Target agent."""

    async def execute(self, prompt, metadata=None):
        return "test response"


class MockSpotter(MockAgent):
    """Mock Spotter agent."""

    async def evaluate(self, response, attack_domain=None, prompt=None):
        return {"l1": {"score": 0.2}, "l2": {"score": 0.3}, "l3": {"score": 0.1}}


class MockEGG(MockAgent):
    """Mock EGG agent."""

    def __init__(self, block=False):
        super().__init__()
        self.block = block

    def inspect_prompt(self, prompt):
        from dataclasses import dataclass

        @dataclass
        class BlockedInfo:
            category: str = "test_category"

        if self.block:
            return False, BlockedInfo()
        return True, None

    def get_blocked_replacement(self):
        return "[BLOCKED]"


# Test Issue 1: Async StateManager

@pytest.mark.asyncio
async def test_state_manager_async_save_round(temp_db):
    """Test async save_round method."""
    state_manager = StateManager(database_path=temp_db, zero_retention=False)

    round_result = RoundResult(
        round_number=1,
        prompt="test prompt",
        attack_domain="prompt_injection",
        target_response="test response",
        evaluation={"l1": {"score": 0.2}, "l2": {"score": 0.3}, "l3": {"score": 0.1}},
        global_score=0.25,
        blocked_by_egg=False,
        timestamp="2024-01-01T00:00:00Z",
        model_version="test",
        session_start_time="2024-01-01T00:00:00Z"
    )

    # Should not raise
    await state_manager.save_round_async(round_result)

    # Verify it was saved
    stats = await state_manager.get_statistics_async()
    assert stats["total_rounds"] == 1


@pytest.mark.asyncio
async def test_state_manager_async_get_prior_rounds(temp_db):
    """Test async get_prior_rounds method."""
    state_manager = StateManager(database_path=temp_db, zero_retention=False)

    # Save a round first
    round_result = RoundResult(
        round_number=1,
        prompt="test prompt",
        attack_domain="prompt_injection",
        target_response="test response",
        evaluation={},
        global_score=0.5,
        blocked_by_egg=False,
        timestamp="2024-01-01T00:00:00Z"
    )
    await state_manager.save_round_async(round_result)

    # Get prior rounds
    prior_rounds = await state_manager.get_prior_rounds_async(limit=10)
    assert len(prior_rounds) == 1
    assert prior_rounds[0]["round_number"] == 1
    assert prior_rounds[0]["global_score"] == 0.5


# Test Issue 2: Evolution Modes

def test_orchestrator_sequential_evolution_mode(temp_db):
    """Test orchestrator with sequential evolution mode."""
    sniper = MockSniper()
    target = MockTarget()
    spotter = MockSpotter()
    egg = MockEGG()
    scoring_engine = ScoringEngine()
    state_manager = StateManager(database_path=temp_db, zero_retention=False)

    orchestrator = Orchestrator(
        sniper=sniper,
        target=target,
        spotter=spotter,
        egg=egg,
        scoring_engine=scoring_engine,
        state_manager=state_manager,
        evolution_mode="sequential",
        concurrent_rounds=4  # Even with concurrent_rounds > 1, should use sequential
    )

    assert orchestrator.evolution_mode == "sequential"
    assert orchestrator.concurrent_rounds == 4


def test_orchestrator_batched_evolution_mode(temp_db):
    """Test orchestrator with batched evolution mode."""
    sniper = MockSniper()
    target = MockTarget()
    spotter = MockSpotter()
    egg = MockEGG()
    scoring_engine = ScoringEngine()
    state_manager = StateManager(database_path=temp_db, zero_retention=False)

    orchestrator = Orchestrator(
        sniper=sniper,
        target=target,
        spotter=spotter,
        egg=egg,
        scoring_engine=scoring_engine,
        state_manager=state_manager,
        evolution_mode="batched",
        concurrent_rounds=4
    )

    assert orchestrator.evolution_mode == "batched"


def test_orchestrator_invalid_evolution_mode(temp_db):
    """Test orchestrator rejects invalid evolution mode."""
    sniper = MockSniper()
    target = MockTarget()
    spotter = MockSpotter()
    egg = MockEGG()
    scoring_engine = ScoringEngine()
    state_manager = StateManager(database_path=temp_db, zero_retention=False)

    with pytest.raises(AssertionError):
        Orchestrator(
            sniper=sniper,
            target=target,
            spotter=spotter,
            egg=egg,
            scoring_engine=scoring_engine,
            state_manager=state_manager,
            evolution_mode="invalid_mode"
        )


# Test Issue 3: EGG Auditor

def test_egg_auditor_initialization():
    """Test EGG auditor initializes correctly."""
    auditor = EGGAuditor(enabled=True)
    assert auditor.enabled is True
    assert auditor.audit_count == 0
    assert auditor.flagged_count == 0


def test_egg_auditor_disabled():
    """Test EGG auditor when disabled."""
    auditor = EGGAuditor(enabled=False)
    result = auditor.audit_decision("test prompt", egg_allowed=True)
    assert result.confidence == 0.0
    assert result.audit_flags == []
    assert auditor.audit_count == 0


def test_egg_auditor_clean_prompt():
    """Test EGG auditor with clean prompt."""
    auditor = EGGAuditor(enabled=True)
    result = auditor.audit_decision("Hello, how are you?", egg_allowed=True)
    assert result.egg_decision is True
    assert result.confidence == 0.0
    assert result.audit_flags == []


def test_egg_auditor_suspicious_prompt():
    """Test EGG auditor detects suspicious characteristics."""
    auditor = EGGAuditor(enabled=True)

    # Prompt with evasion techniques
    suspicious_prompt = "h4ck the system with exploit payload"
    result = auditor.audit_decision(suspicious_prompt, egg_allowed=True)

    assert result.egg_decision is True
    assert len(result.audit_flags) > 0
    assert result.confidence > 0.0
    assert auditor.flagged_count == 1


def test_egg_auditor_blocked_prompt():
    """Test EGG auditor doesn't flag already blocked prompts."""
    auditor = EGGAuditor(enabled=True)
    result = auditor.audit_decision("bad prompt", egg_allowed=False, egg_blocked_category="csam")

    assert result.egg_decision is False
    assert result.confidence == 0.0
    assert len(result.audit_flags) == 0


def test_egg_auditor_statistics():
    """Test EGG auditor statistics."""
    auditor = EGGAuditor(enabled=True)

    # Audit some prompts
    auditor.audit_decision("clean prompt", egg_allowed=True)
    # Use a prompt with clear evasion patterns
    auditor.audit_decision("h4ck the system with exploit and payload", egg_allowed=True)
    auditor.audit_decision("blocked", egg_allowed=False, egg_blocked_category="test")

    stats = auditor.get_statistics()
    assert stats["enabled"] is True
    assert stats["total_audited"] == 3
    assert stats["flagged_count"] >= 1


def test_orchestrator_with_egg_auditor(temp_db):
    """Test orchestrator integrates EGG auditor."""
    sniper = MockSniper()
    target = MockTarget()
    spotter = MockSpotter()
    egg = MockEGG()
    scoring_engine = ScoringEngine()
    state_manager = StateManager(database_path=temp_db, zero_retention=False)
    egg_auditor = EGGAuditor(enabled=True)

    orchestrator = Orchestrator(
        sniper=sniper,
        target=target,
        spotter=spotter,
        egg=egg,
        scoring_engine=scoring_engine,
        state_manager=state_manager,
        egg_auditor=egg_auditor
    )

    assert orchestrator.egg_auditor is not None
    assert orchestrator.egg_auditor.enabled is True


# Test Issue 4: Zero-Retention Cleanup

def test_zero_retention_cleanup_removes_artifacts(temp_db, temp_artifacts_dir):
    """Test that zero-retention cleanup removes artifacts directory."""
    sniper = MockSniper()
    target = MockTarget()
    spotter = MockSpotter()
    egg = MockEGG()
    scoring_engine = ScoringEngine()
    state_manager = StateManager(database_path=temp_db, zero_retention=True)

    orchestrator = Orchestrator(
        sniper=sniper,
        target=target,
        spotter=spotter,
        egg=egg,
        scoring_engine=scoring_engine,
        state_manager=state_manager,
        artifacts_dir=temp_artifacts_dir
    )

    # Create a manifest directory to simulate a run
    from app.core.manifest import AttackManifest, TargetDefinition, IterationLimits, FitnessFunctionConfig, DeterminismConfig, MutationPolicyConfig, ResourceLimits, AgentBoundaries

    orchestrator.current_manifest = AttackManifest(
        manifest_id="test-manifest-123",
        protocell_version="1.0.0",
        policy_version="test",
        timestamp_utc="2024-01-01T00:00:00Z",
        operator_intent="test",
        target=TargetDefinition(
            provider="test",
            model="test",
            model_revision="test",
            endpoint="test",
            provider_metadata={},
            scope="test"
        ),
        determinism=DeterminismConfig(seed=42, rng="pcg64"),
        iteration_limits=IterationLimits(max_generations=10, population_size=10, max_evaluations=100),
        mutation_policy=MutationPolicyConfig(policy_id="test", version="1.0.0", operators=[]),
        fitness_function=FitnessFunctionConfig(function_id="test", version="1.0.0", code_fingerprint="test"),
        agent_boundaries=AgentBoundaries(),
        resource_limits=ResourceLimits(max_runtime_seconds=3600, max_concurrency=1)
    )

    run_dir = os.path.join(temp_artifacts_dir, "test-manifest-123")
    os.makedirs(run_dir, exist_ok=True)

    # Create some artifacts
    specimen_dir = os.path.join(run_dir, "specimens")
    os.makedirs(specimen_dir, exist_ok=True)
    test_file = os.path.join(specimen_dir, "test_specimen.json")
    with open(test_file, "w") as f:
        f.write("{}")

    # Verify artifacts exist before cleanup
    assert os.path.exists(run_dir)
    assert os.path.exists(test_file)

    # Run cleanup
    orchestrator.cleanup()

    # Verify artifacts were deleted
    assert not os.path.exists(run_dir)


def test_zero_retention_disabled_preserves_artifacts(temp_db, temp_artifacts_dir):
    """Test that artifacts are preserved when zero_retention is False."""
    sniper = MockSniper()
    target = MockTarget()
    spotter = MockSpotter()
    egg = MockEGG()
    scoring_engine = ScoringEngine()
    state_manager = StateManager(database_path=temp_db, zero_retention=False)

    orchestrator = Orchestrator(
        sniper=sniper,
        target=target,
        spotter=spotter,
        egg=egg,
        scoring_engine=scoring_engine,
        state_manager=state_manager,
        artifacts_dir=temp_artifacts_dir
    )

    # Create a manifest directory to simulate a run
    from app.core.manifest import AttackManifest, TargetDefinition, IterationLimits, FitnessFunctionConfig, DeterminismConfig, MutationPolicyConfig, ResourceLimits, AgentBoundaries

    orchestrator.current_manifest = AttackManifest(
        manifest_id="test-manifest-456",
        protocell_version="1.0.0",
        policy_version="test",
        timestamp_utc="2024-01-01T00:00:00Z",
        operator_intent="test",
        target=TargetDefinition(
            provider="test",
            model="test",
            model_revision="test",
            endpoint="test",
            provider_metadata={},
            scope="test"
        ),
        determinism=DeterminismConfig(seed=42, rng="pcg64"),
        iteration_limits=IterationLimits(max_generations=10, population_size=10, max_evaluations=100),
        mutation_policy=MutationPolicyConfig(policy_id="test", version="1.0.0", operators=[]),
        fitness_function=FitnessFunctionConfig(function_id="test", version="1.0.0", code_fingerprint="test"),
        agent_boundaries=AgentBoundaries(),
        resource_limits=ResourceLimits(max_runtime_seconds=3600, max_concurrency=1)
    )

    run_dir = os.path.join(temp_artifacts_dir, "test-manifest-456")
    os.makedirs(run_dir, exist_ok=True)

    # Create some artifacts
    specimen_dir = os.path.join(run_dir, "specimens")
    os.makedirs(specimen_dir, exist_ok=True)
    test_file = os.path.join(specimen_dir, "test_specimen.json")
    with open(test_file, "w") as f:
        f.write("{}")

    # Verify artifacts exist before cleanup
    assert os.path.exists(run_dir)
    assert os.path.exists(test_file)

    # Run cleanup
    orchestrator.cleanup()

    # Verify artifacts were NOT deleted (zero_retention=False)
    assert os.path.exists(run_dir)
    assert os.path.exists(test_file)
