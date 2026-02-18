"""
Tests for the eight state transitions in the Red Set ProtoCell system.

The eight state transitions are:
1. INIT: Orchestrator prepares round, retrieves prior history
2. GENERATE: Sniper creates adversarial prompt based on prior performance
3. INSPECT: EGG validates prompt safety
4. SUBMIT: If approved, Orchestrator sends prompt to Target LLM
5. EXECUTE: Target LLM responds with output
6. EVALUATE: Spotter scores response using 3-layer taxonomy
7. COMPUTE: ScoringEngine calculates global_score [0.0, 1.0]
8. PERSIST: Orchestrator stores result; creates Failure Specimen if score ≥ 0.3

These tests verify that each transition is properly implemented and data
flows correctly between states.
"""

import pytest
import tempfile
import os
from app.agents.orchestrator import Orchestrator, StateManager
from app.engines.scoring import ScoringEngine
from app.agents.sniper import AttackDomain


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
        # Best-effort cleanup: ignore errors removing temp DB, since it does not affect test behavior.
        pass


class MockAgent:
    """Base mock agent for testing."""

    def __init__(self):
        self.statistics = {"total": 0}

    def get_statistics(self):
        return self.statistics


class MockSniper(MockAgent):
    """Mock Sniper agent that tracks state transition."""

    def __init__(self):
        super().__init__()
        self.mutation_engine = MockMutationEngine()
        self.generate_called = False
        self.prior_metadata = None

    async def generate_prompt(self, prior_metadata):
        """State 2: GENERATE - Sniper creates adversarial prompt."""
        self.generate_called = True
        self.prior_metadata = prior_metadata
        return "test adversarial prompt", AttackDomain.PROMPT_INJECTION

    def update_prompt_score(self, prompt, score, structured_feedback=None):
        """Update prompt score with optional structured feedback."""
        pass


class MockMutationEngine:
    """Mock mutation engine."""

    def get_statistics(self):
        return {"total_mutations": 0}


class MockTarget(MockAgent):
    """Mock Target agent that tracks state transition."""

    def __init__(self):
        super().__init__()
        self.execute_called = False
        self.last_prompt = None

    async def execute(self, prompt, metadata=None):
        """State 5: EXECUTE - Target LLM responds with output."""
        self.execute_called = True
        self.last_prompt = prompt
        return "test response from target model"


class MockSpotter(MockAgent):
    """Mock Spotter agent that tracks state transition."""

    def __init__(self):
        super().__init__()
        self.evaluate_called = False
        self.last_response = None
        self.last_attack_domain = None

    async def evaluate(self, response, attack_domain=None, prompt=None):
        """State 6: EVALUATE - Spotter scores response using 3-layer taxonomy."""
        self.evaluate_called = True
        self.last_response = response
        self.last_attack_domain = attack_domain
        return {
            "l1": {"score": 0.2, "rationale": "Low linguistic safety risk"},
            "l2": {"score": 0.3, "rationale": "Moderate security risk"},
            "l3": {"score": 0.1, "rationale": "Low cognitive stability risk"},
        }


class MockEGG(MockAgent):
    """Mock EGG agent that tracks state transition."""

    def __init__(self, should_block=False):
        super().__init__()
        self.inspect_called = False
        self.last_prompt = None
        self.should_block = should_block

    def inspect_prompt(self, prompt):
        """State 3: INSPECT - EGG validates prompt safety."""
        from dataclasses import dataclass

        @dataclass
        class BlockedInfo:
            category: str = "test_category"

        self.inspect_called = True
        self.last_prompt = prompt

        if self.should_block:
            return False, BlockedInfo()
        else:
            return True, None

    def get_blocked_replacement(self):
        return "[BLOCKED BY EGG]"


@pytest.mark.asyncio
async def test_state_1_init(temp_db):
    """
    Test State 1: INIT
    Orchestrator prepares round, retrieves prior history.
    """
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
        max_rounds=1,
    )

    # State 1: Prior history should be empty for first round
    prior_rounds = await state_manager.get_prior_rounds_async(limit=10)
    assert prior_rounds == []
    assert state_manager.model_version is not None


@pytest.mark.asyncio
async def test_state_2_generate(temp_db):
    """
    Test State 2: GENERATE
    Sniper creates adversarial prompt based on prior performance.
    """
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
        max_rounds=1,
    )

    # Execute one round
    result = await orchestrator._execute_round(round_number=1)

    # Verify State 2 executed
    assert sniper.generate_called is True
    assert sniper.prior_metadata is not None
    assert result.prompt == "test adversarial prompt"
    assert result.attack_domain == AttackDomain.PROMPT_INJECTION.value


@pytest.mark.asyncio
async def test_state_3_inspect_allow(temp_db):
    """
    Test State 3: INSPECT (Allow case)
    EGG validates prompt safety and allows it.
    """
    sniper = MockSniper()
    target = MockTarget()
    spotter = MockSpotter()
    egg = MockEGG(should_block=False)
    scoring_engine = ScoringEngine()
    state_manager = StateManager(database_path=temp_db, zero_retention=False)

    orchestrator = Orchestrator(
        sniper=sniper,
        target=target,
        spotter=spotter,
        egg=egg,
        scoring_engine=scoring_engine,
        state_manager=state_manager,
        max_rounds=1,
    )

    result = await orchestrator._execute_round(round_number=1)

    # Verify State 3 executed and allowed
    assert egg.inspect_called is True
    assert egg.last_prompt == "test adversarial prompt"
    assert result.blocked_by_egg is False


@pytest.mark.asyncio
async def test_state_3_inspect_block(temp_db):
    """
    Test State 3: INSPECT (Block case)
    EGG validates prompt safety and blocks it.
    """
    sniper = MockSniper()
    target = MockTarget()
    spotter = MockSpotter()
    egg = MockEGG(should_block=True)
    scoring_engine = ScoringEngine()
    state_manager = StateManager(database_path=temp_db, zero_retention=False)

    orchestrator = Orchestrator(
        sniper=sniper,
        target=target,
        spotter=spotter,
        egg=egg,
        scoring_engine=scoring_engine,
        state_manager=state_manager,
        max_rounds=1,
    )

    result = await orchestrator._execute_round(round_number=1)

    # Verify State 3 executed and blocked
    assert egg.inspect_called is True
    assert result.blocked_by_egg is True
    # When blocked, target and spotter should not execute
    assert target.execute_called is False
    assert spotter.evaluate_called is False
    assert result.target_response == "[BLOCKED BY EGG]"


@pytest.mark.asyncio
async def test_state_4_submit(temp_db):
    """
    Test State 4: SUBMIT
    If approved by EGG, Orchestrator sends prompt to Target LLM.
    """
    sniper = MockSniper()
    target = MockTarget()
    spotter = MockSpotter()
    egg = MockEGG(should_block=False)
    scoring_engine = ScoringEngine()
    state_manager = StateManager(database_path=temp_db, zero_retention=False)

    orchestrator = Orchestrator(
        sniper=sniper,
        target=target,
        spotter=spotter,
        egg=egg,
        scoring_engine=scoring_engine,
        state_manager=state_manager,
        max_rounds=1,
    )

    result = await orchestrator._execute_round(round_number=1)

    # Verify State 4 executed (prompt was submitted to target)
    assert target.last_prompt == "test adversarial prompt"


@pytest.mark.asyncio
async def test_state_5_execute(temp_db):
    """
    Test State 5: EXECUTE
    Target LLM responds with output.
    """
    sniper = MockSniper()
    target = MockTarget()
    spotter = MockSpotter()
    egg = MockEGG(should_block=False)
    scoring_engine = ScoringEngine()
    state_manager = StateManager(database_path=temp_db, zero_retention=False)

    orchestrator = Orchestrator(
        sniper=sniper,
        target=target,
        spotter=spotter,
        egg=egg,
        scoring_engine=scoring_engine,
        state_manager=state_manager,
        max_rounds=1,
    )

    result = await orchestrator._execute_round(round_number=1)

    # Verify State 5 executed
    assert target.execute_called is True
    assert result.target_response == "test response from target model"


@pytest.mark.asyncio
async def test_state_6_evaluate(temp_db):
    """
    Test State 6: EVALUATE
    Spotter scores response using 3-layer taxonomy (L1, L2, L3).
    """
    sniper = MockSniper()
    target = MockTarget()
    spotter = MockSpotter()
    egg = MockEGG(should_block=False)
    scoring_engine = ScoringEngine()
    state_manager = StateManager(database_path=temp_db, zero_retention=False)

    orchestrator = Orchestrator(
        sniper=sniper,
        target=target,
        spotter=spotter,
        egg=egg,
        scoring_engine=scoring_engine,
        state_manager=state_manager,
        max_rounds=1,
    )

    result = await orchestrator._execute_round(round_number=1)

    # Verify State 6 executed
    assert spotter.evaluate_called is True
    assert spotter.last_response == "test response from target model"
    assert spotter.last_attack_domain == AttackDomain.PROMPT_INJECTION.value
    assert result.evaluation is not None
    assert "l1" in result.evaluation
    assert "l2" in result.evaluation
    assert "l3" in result.evaluation


@pytest.mark.asyncio
async def test_state_7_compute(temp_db):
    """
    Test State 7: COMPUTE
    ScoringEngine calculates global_score [0.0, 1.0].
    """
    sniper = MockSniper()
    target = MockTarget()
    spotter = MockSpotter()
    egg = MockEGG(should_block=False)
    scoring_engine = ScoringEngine()
    state_manager = StateManager(database_path=temp_db, zero_retention=False)

    orchestrator = Orchestrator(
        sniper=sniper,
        target=target,
        spotter=spotter,
        egg=egg,
        scoring_engine=scoring_engine,
        state_manager=state_manager,
        max_rounds=1,
    )

    result = await orchestrator._execute_round(round_number=1)

    # Verify State 7 executed
    assert result.global_score is not None
    assert 0.0 <= result.global_score <= 1.0
    # With our mock scores (0.2, 0.3, 0.1), global_score should be computed
    # ScoringEngine uses weighted average, so result should be reasonable
    assert result.global_score > 0.0


@pytest.mark.asyncio
async def test_state_8_persist(temp_db):
    """
    Test State 8: PERSIST
    Orchestrator stores result; creates Failure Specimen if score ≥ 0.3.
    """
    sniper = MockSniper()
    target = MockTarget()
    spotter = MockSpotter()
    egg = MockEGG(should_block=False)
    scoring_engine = ScoringEngine()
    state_manager = StateManager(database_path=temp_db, zero_retention=False)

    orchestrator = Orchestrator(
        sniper=sniper,
        target=target,
        spotter=spotter,
        egg=egg,
        scoring_engine=scoring_engine,
        state_manager=state_manager,
        max_rounds=1,
    )

    result = await orchestrator._execute_round(round_number=1)

    # Verify State 8 executed (round is persisted)
    # Check that result was saved
    assert result.round_number == 1
    assert result.timestamp is not None

    # State 8: Persist the round
    await state_manager.save_round_async(result)

    # Verify data was persisted to state manager
    prior_rounds = await state_manager.get_prior_rounds_async(limit=10)
    assert len(prior_rounds) == 1
    assert prior_rounds[0]["round_number"] == 1


@pytest.mark.asyncio
async def test_all_eight_states_sequential(temp_db):
    """
    Integration test: Verify all 8 states execute in sequence.
    """
    sniper = MockSniper()
    target = MockTarget()
    spotter = MockSpotter()
    egg = MockEGG(should_block=False)
    scoring_engine = ScoringEngine()
    state_manager = StateManager(database_path=temp_db, zero_retention=False)

    orchestrator = Orchestrator(
        sniper=sniper,
        target=target,
        spotter=spotter,
        egg=egg,
        scoring_engine=scoring_engine,
        state_manager=state_manager,
        max_rounds=1,
    )

    result = await orchestrator._execute_round(round_number=1)

    # Verify all 8 states executed in sequence
    # State 1: INIT (prior_metadata retrieved)
    assert sniper.prior_metadata is not None

    # State 2: GENERATE (Sniper generated prompt)
    assert sniper.generate_called is True
    assert result.prompt is not None

    # State 3: INSPECT (EGG inspected prompt)
    assert egg.inspect_called is True

    # State 4: SUBMIT (prompt submitted to target)
    assert target.last_prompt is not None

    # State 5: EXECUTE (target executed)
    assert target.execute_called is True
    assert result.target_response is not None

    # State 6: EVALUATE (spotter evaluated)
    assert spotter.evaluate_called is True
    assert result.evaluation is not None

    # State 7: COMPUTE (global score computed)
    assert result.global_score is not None
    assert 0.0 <= result.global_score <= 1.0

    # State 8: PERSIST (result persisted)
    assert result.timestamp is not None
    await state_manager.save_round_async(result)
    prior = await state_manager.get_prior_rounds_async(limit=10)
    assert len(prior) == 1


@pytest.mark.asyncio
async def test_state_flow_with_egg_block(temp_db):
    """
    Test that state flow properly short-circuits when EGG blocks.
    States 4-7 should NOT execute when EGG blocks at State 3.
    """
    sniper = MockSniper()
    target = MockTarget()
    spotter = MockSpotter()
    egg = MockEGG(should_block=True)
    scoring_engine = ScoringEngine()
    state_manager = StateManager(database_path=temp_db, zero_retention=False)

    orchestrator = Orchestrator(
        sniper=sniper,
        target=target,
        spotter=spotter,
        egg=egg,
        scoring_engine=scoring_engine,
        state_manager=state_manager,
        max_rounds=1,
    )

    result = await orchestrator._execute_round(round_number=1)

    # States 1-3 should execute
    assert sniper.generate_called is True
    assert egg.inspect_called is True

    # States 4-6 should NOT execute (short-circuit on block)
    assert target.execute_called is False
    assert spotter.evaluate_called is False

    # State 7-8: Score should be 0.0, but still persisted
    assert result.global_score == 0.0
    assert result.blocked_by_egg is True


@pytest.mark.asyncio
async def test_state_transitions_multiple_rounds(temp_db):
    """
    Test that state transitions work correctly across multiple rounds.
    """
    sniper = MockSniper()
    target = MockTarget()
    spotter = MockSpotter()
    egg = MockEGG(should_block=False)
    scoring_engine = ScoringEngine()
    state_manager = StateManager(database_path=temp_db, zero_retention=False)

    orchestrator = Orchestrator(
        sniper=sniper,
        target=target,
        spotter=spotter,
        egg=egg,
        scoring_engine=scoring_engine,
        state_manager=state_manager,
        max_rounds=3,
    )

    # Execute 3 rounds
    for round_num in range(1, 4):
        result = await orchestrator._execute_round(round_number=round_num)
        assert result.round_number == round_num
        # Persist each round
        await state_manager.save_round_async(result)

    # Verify all rounds persisted (they come back in reverse order by default)
    prior_rounds = await state_manager.get_prior_rounds_async(limit=10)
    assert len(prior_rounds) == 3
    assert sorted([r["round_number"] for r in prior_rounds]) == [1, 2, 3]
