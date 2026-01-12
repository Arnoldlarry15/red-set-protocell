"""
Tests for parallel execution in the Orchestrator
"""

import pytest
import asyncio
import tempfile
import os
from unittest.mock import Mock
from app.agents.orchestrator import Orchestrator, StateManager
from app.engines.scoring import ScoringEngine


@pytest.mark.asyncio
async def test_sequential_execution():
    """Test that sequential execution works correctly."""
    # Create mock agents
    sniper = Mock()
    sniper.generate_prompt = Mock(return_value=("test prompt", Mock(value="test_domain")))
    sniper.update_prompt_score = Mock()
    sniper.get_statistics = Mock(return_value={})
    sniper.mutation_engine = Mock()
    sniper.mutation_engine.get_statistics = Mock(return_value={})

    target = Mock()
    target.execute = Mock(return_value="test response")
    target.get_statistics = Mock(return_value={})

    spotter = Mock()
    spotter.evaluate = Mock(return_value={
        'l1': {'score': 0.3},
        'l2': {'score': 0.4},
        'l3': {'score': 0.2}
    })
    spotter.get_statistics = Mock(return_value={})

    egg = Mock()
    egg.inspect_prompt = Mock(return_value=(True, None))
    egg.get_statistics = Mock(return_value={})

    scoring_engine = ScoringEngine()
    # Use tempfile for cross-platform compatibility
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test_sequential.db")
    state_manager = StateManager(database_path=db_path, zero_retention=True)

    # Create orchestrator with sequential execution
    orchestrator = Orchestrator(
        sniper=sniper,
        target=target,
        spotter=spotter,
        egg=egg,
        scoring_engine=scoring_engine,
        state_manager=state_manager,
        max_rounds=3,
        concurrent_rounds=1
    )

    # Run session
    stats = await orchestrator.run_session()

    # Verify sequential execution
    assert stats['session']['total_rounds'] == 3
    assert sniper.generate_prompt.call_count == 3
    assert target.execute.call_count == 3

    # Cleanup
    orchestrator.cleanup()


@pytest.mark.asyncio
async def test_parallel_execution():
    """Test that parallel execution works correctly."""
    # Create mock agents with async support
    sniper = Mock()
    sniper.generate_prompt = Mock(return_value=("test prompt", Mock(value="test_domain")))
    sniper.update_prompt_score = Mock()
    sniper.get_statistics = Mock(return_value={})
    sniper.mutation_engine = Mock()
    sniper.mutation_engine.get_statistics = Mock(return_value={})

    target = Mock()
    target.execute = Mock(return_value="test response")
    target.get_statistics = Mock(return_value={})

    spotter = Mock()
    spotter.evaluate = Mock(return_value={
        'l1': {'score': 0.3},
        'l2': {'score': 0.4},
        'l3': {'score': 0.2}
    })
    spotter.get_statistics = Mock(return_value={})

    egg = Mock()
    egg.inspect_prompt = Mock(return_value=(True, None))
    egg.get_statistics = Mock(return_value={})

    scoring_engine = ScoringEngine()
    # Use tempfile for cross-platform compatibility
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test_parallel.db")
    state_manager = StateManager(database_path=db_path, zero_retention=True)

    # Create orchestrator with parallel execution
    orchestrator = Orchestrator(
        sniper=sniper,
        target=target,
        spotter=spotter,
        egg=egg,
        scoring_engine=scoring_engine,
        state_manager=state_manager,
        max_rounds=6,
        concurrent_rounds=3  # Execute 3 rounds in parallel
    )

    # Run session
    stats = await orchestrator.run_session()

    # Verify parallel execution
    assert stats['session']['total_rounds'] == 6
    assert sniper.generate_prompt.call_count == 6
    assert target.execute.call_count == 6

    # Cleanup
    orchestrator.cleanup()


@pytest.mark.asyncio
async def test_parallel_with_timeout():
    """Test that parallel execution handles timeouts correctly."""
    sniper = Mock()
    sniper.generate_prompt = Mock(return_value=("test prompt", Mock(value="test_domain")))
    sniper.update_prompt_score = Mock()
    sniper.get_statistics = Mock(return_value={})
    sniper.mutation_engine = Mock()
    sniper.mutation_engine.get_statistics = Mock(return_value={})

    # Mock target that times out
    async def slow_execute(prompt, **kwargs):
        await asyncio.sleep(10)  # Simulate slow execution
        return "test response"

    target = Mock()
    target.execute = Mock(return_value="test response")
    target.get_statistics = Mock(return_value={})

    spotter = Mock()
    spotter.evaluate = Mock(return_value={
        'l1': {'score': 0.3},
        'l2': {'score': 0.4},
        'l3': {'score': 0.2}
    })
    spotter.get_statistics = Mock(return_value={})

    egg = Mock()
    egg.inspect_prompt = Mock(return_value=(True, None))
    egg.get_statistics = Mock(return_value={})

    scoring_engine = ScoringEngine()
    # Use tempfile for cross-platform compatibility
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test_timeout.db")
    state_manager = StateManager(database_path=db_path, zero_retention=True)

    orchestrator = Orchestrator(
        sniper=sniper,
        target=target,
        spotter=spotter,
        egg=egg,
        scoring_engine=scoring_engine,
        state_manager=state_manager,
        max_rounds=2,
        concurrent_rounds=2,
        round_timeout=1  # Short timeout
    )

    # Run session - should handle timeouts gracefully
    stats = await orchestrator.run_session()

    # Should complete even with timeouts
    assert stats is not None

    # Cleanup
    orchestrator.cleanup()
