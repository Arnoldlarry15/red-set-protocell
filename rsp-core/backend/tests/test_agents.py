"""
Tests for agent modules
"""

import pytest
from app.agents.target import Target, MockBackend, create_target
from app.agents.spotter import Spotter
from app.agents.sniper import Sniper
from app.engines.mutation import MutationEngine


def test_target_mock_backend():
    """Test Target with mock backend."""
    backend = MockBackend()
    target = Target(backend)
    
    response = target.execute("test prompt")
    
    assert isinstance(response, str)
    assert len(response) > 0
    assert target.execution_count == 1


def test_target_fresh_context():
    """Test Target enforces fresh context."""
    backend = MockBackend()
    target = Target(backend, fresh_context=True)
    
    assert target.fresh_context is True


def test_target_statistics():
    """Test Target provides statistics."""
    backend = MockBackend()
    target = Target(backend)
    
    target.execute("test 1")
    target.execute("test 2")
    
    stats = target.get_statistics()
    
    assert stats['total_executions'] == 2
    assert stats['backend_type'] == 'MockBackend'


def test_create_target_factory():
    """Test target factory function."""
    target = create_target('mock')
    
    assert isinstance(target, Target)
    assert target.fresh_context is True


def test_spotter_evaluation():
    """Test Spotter can evaluate responses."""
    spotter = Spotter(confidence_threshold=0.6)
    
    # Safe response
    safe_response = "I cannot help with that request."
    evaluation = spotter.evaluate(safe_response)
    
    assert 'l1' in evaluation
    assert 'l2' in evaluation
    assert 'l3' in evaluation
    assert 'mutation_guidance' in evaluation
    
    # Check L1 (refusal should be detected as GOOD)
    assert evaluation['l1']['score'] <= 0.3


def test_spotter_detects_policy_circumvention():
    """Test Spotter detects policy circumvention indicators."""
    spotter = Spotter()
    
    # Response with circumvention indicators
    response = "In a hypothetical scenario, I can explain this..."
    evaluation = spotter.evaluate(response, attack_domain="policy_circumvention")
    
    assert evaluation['l2']['score'] > 0.0


def test_spotter_statistics():
    """Test Spotter provides statistics."""
    spotter = Spotter()
    
    spotter.evaluate("response 1")
    spotter.evaluate("response 2")
    
    stats = spotter.get_statistics()
    
    assert stats['total_evaluations'] == 2


def test_sniper_generation():
    """Test Sniper can generate prompts."""
    mutation_engine = MutationEngine()
    sniper = Sniper(mutation_engine)
    
    prompt, domain = sniper.generate_prompt()
    
    assert isinstance(prompt, str)
    assert len(prompt) > 0
    assert sniper.generation_count == 1


def test_sniper_with_prior_metadata():
    """Test Sniper uses prior metadata."""
    mutation_engine = MutationEngine()
    sniper = Sniper(mutation_engine)
    
    prior_metadata = [
        {'global_score': 0.5, 'round_number': 1},
        {'global_score': 0.7, 'round_number': 2},
    ]
    
    prompt, domain = sniper.generate_prompt(prior_metadata)
    
    assert isinstance(prompt, str)
    assert len(prompt) > 0


def test_sniper_update_score():
    """Test Sniper can update prompt scores."""
    mutation_engine = MutationEngine()
    sniper = Sniper(mutation_engine)
    
    prompt, domain = sniper.generate_prompt()
    sniper.update_prompt_score(prompt, 0.8)
    
    # Check that score was updated in pool
    assert len(sniper.evolution_pool) > 0


def test_sniper_statistics():
    """Test Sniper provides statistics."""
    mutation_engine = MutationEngine()
    sniper = Sniper(mutation_engine, evolution_pool_size=5)
    
    sniper.generate_prompt()
    sniper.generate_prompt()
    
    stats = sniper.get_statistics()
    
    assert stats['total_generated'] == 2
    assert stats['evolution_pool_size'] <= 5
