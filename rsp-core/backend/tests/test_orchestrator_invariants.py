"""
Tests for orchestrator invariant assertions.

These tests verify that the invariant checks properly enforce
system contracts and prevent invalid states.
"""

import pytest
import tempfile
import os
from app.agents.orchestrator import Orchestrator, StateManager, RoundResult
from app.engines.scoring import ScoringEngine


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

    def generate_prompt(self, prior_metadata):
        from app.agents.sniper import AttackDomain

        return "test prompt", AttackDomain.PROMPT_INJECTION

    def update_prompt_score(self, prompt, score):
        pass


class MockMutationEngine:
    """Mock mutation engine."""

    def get_statistics(self):
        return {"total_mutations": 0}


class MockTarget(MockAgent):
    """Mock Target agent."""

    def execute(self, prompt, metadata=None):
        return "test response"


class MockSpotter(MockAgent):
    """Mock Spotter agent."""

    def evaluate(self, response, attack_domain=None, prompt=None):
        return {"l1": {"score": 0.2}, "l2": {"score": 0.3}, "l3": {"score": 0.1}}


class MockEGG(MockAgent):
    """Mock EGG agent."""

    def inspect_prompt(self, prompt):
        from dataclasses import dataclass

        @dataclass
        class BlockedInfo:
            category: str = "none"

        return True, BlockedInfo()

    def get_blocked_replacement(self):
        return "[BLOCKED]"


def test_orchestrator_initialization_with_valid_agents(temp_db):
    """Test that orchestrator initializes with valid agents."""
    sniper = MockSniper()
    target = MockTarget()
    spotter = MockSpotter()
    egg = MockEGG()
    scoring_engine = ScoringEngine()
    state_manager = StateManager(database_path=temp_db, zero_retention=False)

    # Should not raise
    orchestrator = Orchestrator(
        sniper=sniper,
        target=target,
        spotter=spotter,
        egg=egg,
        scoring_engine=scoring_engine,
        state_manager=state_manager,
        max_rounds=10,
    )

    assert orchestrator.sniper is sniper
    assert orchestrator.target is target
    assert orchestrator.max_rounds == 10


def test_orchestrator_initialization_fails_with_none_sniper(temp_db):
    """Test that orchestrator fails if sniper is None."""
    target = MockTarget()
    spotter = MockSpotter()
    egg = MockEGG()
    scoring_engine = ScoringEngine()
    state_manager = StateManager(database_path=temp_db, zero_retention=False)

    with pytest.raises(AssertionError, match="Sniper agent must not be None"):
        Orchestrator(
            sniper=None,
            target=target,
            spotter=spotter,
            egg=egg,
            scoring_engine=scoring_engine,
            state_manager=state_manager,
        )


def test_orchestrator_initialization_fails_with_none_target(temp_db):
    """Test that orchestrator fails if target is None."""
    sniper = MockSniper()
    spotter = MockSpotter()
    egg = MockEGG()
    scoring_engine = ScoringEngine()
    state_manager = StateManager(database_path=temp_db, zero_retention=False)

    with pytest.raises(AssertionError, match="Target agent must not be None"):
        Orchestrator(
            sniper=sniper,
            target=None,
            spotter=spotter,
            egg=egg,
            scoring_engine=scoring_engine,
            state_manager=state_manager,
        )


def test_orchestrator_initialization_fails_with_none_spotter(temp_db):
    """Test that orchestrator fails if spotter is None."""
    sniper = MockSniper()
    target = MockTarget()
    egg = MockEGG()
    scoring_engine = ScoringEngine()
    state_manager = StateManager(database_path=temp_db, zero_retention=False)

    with pytest.raises(AssertionError, match="Spotter agent must not be None"):
        Orchestrator(
            sniper=sniper,
            target=target,
            spotter=None,
            egg=egg,
            scoring_engine=scoring_engine,
            state_manager=state_manager,
        )


def test_orchestrator_initialization_fails_with_none_egg(temp_db):
    """Test that orchestrator fails if EGG is None."""
    sniper = MockSniper()
    target = MockTarget()
    spotter = MockSpotter()
    scoring_engine = ScoringEngine()
    state_manager = StateManager(database_path=temp_db, zero_retention=False)

    with pytest.raises(AssertionError, match="EGG .* must not be None"):
        Orchestrator(
            sniper=sniper,
            target=target,
            spotter=spotter,
            egg=None,
            scoring_engine=scoring_engine,
            state_manager=state_manager,
        )


def test_orchestrator_initialization_fails_with_zero_max_rounds(temp_db):
    """Test that orchestrator fails if max_rounds is 0."""
    sniper = MockSniper()
    target = MockTarget()
    spotter = MockSpotter()
    egg = MockEGG()
    scoring_engine = ScoringEngine()
    state_manager = StateManager(database_path=temp_db, zero_retention=False)

    with pytest.raises(AssertionError, match="max_rounds must be > 0"):
        Orchestrator(
            sniper=sniper,
            target=target,
            spotter=spotter,
            egg=egg,
            scoring_engine=scoring_engine,
            state_manager=state_manager,
            max_rounds=0,
        )


def test_orchestrator_initialization_fails_with_negative_max_rounds(temp_db):
    """Test that orchestrator fails if max_rounds is negative."""
    sniper = MockSniper()
    target = MockTarget()
    spotter = MockSpotter()
    egg = MockEGG()
    scoring_engine = ScoringEngine()
    state_manager = StateManager(database_path=temp_db, zero_retention=False)

    with pytest.raises(AssertionError, match="max_rounds must be > 0"):
        Orchestrator(
            sniper=sniper,
            target=target,
            spotter=spotter,
            egg=egg,
            scoring_engine=scoring_engine,
            state_manager=state_manager,
            max_rounds=-5,
        )


def test_orchestrator_initialization_fails_with_zero_round_timeout(temp_db):
    """Test that orchestrator fails if round_timeout is 0."""
    sniper = MockSniper()
    target = MockTarget()
    spotter = MockSpotter()
    egg = MockEGG()
    scoring_engine = ScoringEngine()
    state_manager = StateManager(database_path=temp_db, zero_retention=False)

    with pytest.raises(AssertionError, match="round_timeout must be > 0"):
        Orchestrator(
            sniper=sniper,
            target=target,
            spotter=spotter,
            egg=egg,
            scoring_engine=scoring_engine,
            state_manager=state_manager,
            round_timeout=0,
        )


def test_orchestrator_initialization_validates_egg_has_inspect_method(temp_db):
    """Test that orchestrator validates EGG has required methods."""
    sniper = MockSniper()
    target = MockTarget()
    spotter = MockSpotter()

    # Create mock without inspect_prompt method
    class InvalidEGG:
        def get_statistics(self):
            return {}

    egg = InvalidEGG()
    scoring_engine = ScoringEngine()
    state_manager = StateManager(database_path=temp_db, zero_retention=False)

    with pytest.raises(AssertionError, match="EGG must implement inspect_prompt"):
        Orchestrator(
            sniper=sniper,
            target=target,
            spotter=spotter,
            egg=egg,
            scoring_engine=scoring_engine,
            state_manager=state_manager,
        )


@pytest.mark.asyncio
async def test_execute_round_validates_positive_round_number(temp_db):
    """Test that _execute_round requires positive round number."""
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
    )

    # Round 0 should fail
    with pytest.raises(AssertionError, match="Round number must be > 0"):
        await orchestrator._execute_round(0)

    # Negative round should fail
    with pytest.raises(AssertionError, match="Round number must be > 0"):
        await orchestrator._execute_round(-1)


@pytest.mark.asyncio
async def test_execute_round_validates_sniper_output(temp_db):
    """Test that _execute_round validates Sniper outputs."""

    class BadSniper(MockAgent):
        """Sniper that returns invalid data."""

        def __init__(self):
            super().__init__()
            self.mutation_engine = MockMutationEngine()

        def generate_prompt(self, prior_metadata):
            # Return empty prompt (invalid)
            from app.agents.sniper import AttackDomain

            return "", AttackDomain.PROMPT_INJECTION

        def update_prompt_score(self, prompt, score):
            pass

    sniper = BadSniper()
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
    )

    with pytest.raises(AssertionError, match="non-empty prompt"):
        await orchestrator._execute_round(1)


@pytest.mark.asyncio
async def test_execute_round_validates_egg_output(temp_db):
    """Test that _execute_round validates EGG outputs."""

    class BadEGG(MockAgent):
        """EGG that returns invalid data."""

        def inspect_prompt(self, prompt):
            # Return non-boolean (invalid)
            return "yes", None

        def get_blocked_replacement(self):
            return "[BLOCKED]"

    sniper = MockSniper()
    target = MockTarget()
    spotter = MockSpotter()
    egg = BadEGG()
    scoring_engine = ScoringEngine()
    state_manager = StateManager(database_path=temp_db, zero_retention=False)

    orchestrator = Orchestrator(
        sniper=sniper,
        target=target,
        spotter=spotter,
        egg=egg,
        scoring_engine=scoring_engine,
        state_manager=state_manager,
    )

    with pytest.raises(AssertionError, match="must return boolean"):
        await orchestrator._execute_round(1)


@pytest.mark.asyncio
async def test_execute_round_validates_target_output(temp_db):
    """Test that _execute_round validates Target outputs."""

    class BadTarget(MockAgent):
        """Target that returns invalid data."""

        def execute(self, prompt, metadata=None):
            # Return non-string (invalid)
            return 123

    sniper = MockSniper()
    target = BadTarget()
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
    )

    with pytest.raises(AssertionError, match="must return string response"):
        await orchestrator._execute_round(1)


@pytest.mark.asyncio
async def test_execute_round_validates_spotter_output(temp_db):
    """Test that _execute_round validates Spotter outputs."""

    class BadSpotter(MockAgent):
        """Spotter that returns invalid evaluation."""

        def evaluate(self, response, attack_domain=None, prompt=None):
            # Missing layer scores
            return {"l1": {}}

    sniper = MockSniper()
    target = MockTarget()
    spotter = BadSpotter()
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
    )

    with pytest.raises(AssertionError, match="must contain l1, l2, and l3"):
        await orchestrator._execute_round(1)


@pytest.mark.asyncio
async def test_execute_round_validates_global_score_range(temp_db):
    """Test that _execute_round validates global score is in valid range."""

    class BadScoringEngine:
        """Scoring engine that returns out-of-range scores."""

        def compute_global_score(self, l1, l2, l3):
            return 1.5  # Out of range!

    sniper = MockSniper()
    target = MockTarget()
    spotter = MockSpotter()
    egg = MockEGG()
    scoring_engine = BadScoringEngine()
    state_manager = StateManager(database_path=temp_db, zero_retention=False)

    orchestrator = Orchestrator(
        sniper=sniper,
        target=target,
        spotter=spotter,
        egg=egg,
        scoring_engine=scoring_engine,
        state_manager=state_manager,
    )

    with pytest.raises(AssertionError, match=r"must be in \[0\.0, 1\.0\]"):
        await orchestrator._execute_round(1)


@pytest.mark.asyncio
async def test_execute_round_succeeds_with_valid_data(temp_db):
    """Test that _execute_round succeeds with all valid data."""
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
    )

    # Should succeed without assertions
    result = await orchestrator._execute_round(1)

    assert isinstance(result, RoundResult)
    assert result.round_number == 1
    assert isinstance(result.prompt, str)
    assert isinstance(result.target_response, str)
    assert 0.0 <= result.global_score <= 1.0
