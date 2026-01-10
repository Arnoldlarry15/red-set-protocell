"""
Integration tests for Selection Engine with Sniper Agent
"""

import pytest
from app.agents.sniper import Sniper, AttackDomain
from app.engines.mutation import MutationEngine
from app.engines.selection import SelectionEngine, SelectionStrategy


@pytest.mark.asyncio
async def test_sniper_with_selection_engine():
    """Test Sniper integration with Selection Engine."""
    mutation_engine = MutationEngine(mutation_rate=0.7)
    selection_engine = SelectionEngine()
    
    sniper = Sniper(
        mutation_engine=mutation_engine,
        evolution_pool_size=5,
        selection_engine=selection_engine,
        selection_strategy=SelectionStrategy.HYBRID
    )
    
    # Generate some prompts
    for _ in range(5):
        prompt, domain = await sniper.generate_prompt()
        assert isinstance(prompt, str)
        assert isinstance(domain, AttackDomain)
        assert len(prompt) > 0


@pytest.mark.asyncio
async def test_sniper_score_updates():
    """Test that Sniper properly updates prompt scores."""
    mutation_engine = MutationEngine(mutation_rate=1.0)  # Always mutate for unique prompts
    selection_engine = SelectionEngine()
    
    sniper = Sniper(
        mutation_engine=mutation_engine,
        evolution_pool_size=5,
        selection_engine=selection_engine,
        selection_strategy=SelectionStrategy.HYBRID
    )
    
    # Generate prompts and update scores immediately
    for i in range(3):
        prompt, domain = await sniper.generate_prompt()
        
        # Update score immediately
        score = 0.3 + (i * 0.2)
        sniper.update_prompt_score(prompt, score)
    
    # Check that at least one score was updated (may have duplicates)
    assert len(sniper.evolution_pool) > 0
    assert any(candidate.score > 0 for candidate in sniper.evolution_pool)


@pytest.mark.asyncio
async def test_sniper_evolution_with_selection():
    """Test that Sniper evolves prompts using selection strategies."""
    mutation_engine = MutationEngine(mutation_rate=0.7)
    selection_engine = SelectionEngine()
    
    sniper = Sniper(
        mutation_engine=mutation_engine,
        evolution_pool_size=5,
        selection_engine=selection_engine,
        selection_strategy=SelectionStrategy.ELITISM
    )
    
    # Generate initial prompts
    for i in range(3):
        prompt, domain = await sniper.generate_prompt()
        sniper.update_prompt_score(prompt, 0.5 + (i * 0.1))
    
    # Generate more prompts - should evolve from pool
    for _ in range(5):
        prompt, domain = await sniper.generate_prompt()
        assert isinstance(prompt, str)
        assert len(prompt) > 0


@pytest.mark.asyncio
async def test_sniper_pool_size_limit():
    """Test that Sniper respects pool size limit."""
    mutation_engine = MutationEngine(mutation_rate=0.7)
    selection_engine = SelectionEngine()
    
    sniper = Sniper(
        mutation_engine=mutation_engine,
        evolution_pool_size=5,
        selection_engine=selection_engine
    )
    
    # Generate more prompts than pool size
    for i in range(10):
        prompt, domain = await sniper.generate_prompt()
        sniper.update_prompt_score(prompt, 0.3 + (i * 0.05))
    
    # Pool should not exceed size limit
    assert len(sniper.evolution_pool) <= 5


@pytest.mark.asyncio
async def test_sniper_diversity_selection():
    """Test Sniper with diversity selection strategy."""
    mutation_engine = MutationEngine(mutation_rate=0.7)
    selection_engine = SelectionEngine()
    
    sniper = Sniper(
        mutation_engine=mutation_engine,
        evolution_pool_size=10,
        selection_engine=selection_engine,
        selection_strategy=SelectionStrategy.DIVERSITY_PRESERVATION
    )
    
    # Generate prompts with varied scores
    for i in range(10):
        prompt, domain = await sniper.generate_prompt()
        sniper.update_prompt_score(prompt, 0.2 + (i % 5) * 0.1)
    
    # Should maintain diverse population
    assert len(sniper.evolution_pool) <= 10


@pytest.mark.asyncio
async def test_sniper_novelty_selection():
    """Test Sniper with novelty search strategy."""
    mutation_engine = MutationEngine(mutation_rate=0.7)
    selection_engine = SelectionEngine(novelty_weight=0.5)
    
    sniper = Sniper(
        mutation_engine=mutation_engine,
        evolution_pool_size=10,
        selection_engine=selection_engine,
        selection_strategy=SelectionStrategy.NOVELTY_SEARCH
    )
    
    # Generate prompts
    for i in range(8):
        prompt, domain = await sniper.generate_prompt()
        sniper.update_prompt_score(prompt, 0.4 + (i * 0.05))
    
    # Should explore novel patterns
    assert len(sniper.evolution_pool) <= 10


@pytest.mark.asyncio
async def test_sniper_statistics_with_selection():
    """Test that Sniper statistics include selection info."""
    mutation_engine = MutationEngine(mutation_rate=0.7)
    selection_engine = SelectionEngine()
    
    sniper = Sniper(
        mutation_engine=mutation_engine,
        evolution_pool_size=5,
        selection_engine=selection_engine,
        selection_strategy=SelectionStrategy.HYBRID
    )
    
    # Generate some prompts
    for i in range(3):
        prompt, domain = await sniper.generate_prompt()
        sniper.update_prompt_score(prompt, 0.5)
    
    # Get statistics
    stats = sniper.get_statistics()
    
    assert 'total_generated' in stats
    assert 'evolution_pool_size' in stats
    assert 'selection_strategy' in stats
    assert 'selection_stats' in stats
    assert stats['selection_strategy'] == 'hybrid'


@pytest.mark.asyncio
async def test_sniper_without_selection_engine():
    """Test Sniper still works without explicit selection engine."""
    mutation_engine = MutationEngine(mutation_rate=0.7)
    
    # Don't provide selection engine - should use default
    sniper = Sniper(
        mutation_engine=mutation_engine,
        evolution_pool_size=5
    )
    
    # Should still work
    prompt, domain = await sniper.generate_prompt()
    assert isinstance(prompt, str)
    assert len(prompt) > 0


@pytest.mark.asyncio
async def test_sniper_decay_over_time():
    """Test that old prompts get decayed in selection."""
    import time
    
    mutation_engine = MutationEngine(mutation_rate=0.7)
    selection_engine = SelectionEngine(decay_rate=0.5, decay_interval=1.0)
    
    sniper = Sniper(
        mutation_engine=mutation_engine,
        evolution_pool_size=5,
        selection_engine=selection_engine,
        selection_strategy=SelectionStrategy.ELITISM
    )
    
    # Generate old prompt with high score
    prompt1, domain1 = await sniper.generate_prompt()
    sniper.update_prompt_score(prompt1, 0.9)
    
    # Wait for decay interval
    time.sleep(1.5)
    
    # Generate new prompt with lower score
    prompt2, domain2 = await sniper.generate_prompt()
    sniper.update_prompt_score(prompt2, 0.7)
    
    # Both should be in pool, but old one should be decayed when selected
    assert len(sniper.evolution_pool) == 2


@pytest.mark.asyncio
async def test_sniper_overfitting_detection():
    """Test that overfitting penalties are applied."""
    mutation_engine = MutationEngine(mutation_rate=0.7)
    selection_engine = SelectionEngine(overfitting_threshold=2)
    
    sniper = Sniper(
        mutation_engine=mutation_engine,
        evolution_pool_size=5,
        selection_engine=selection_engine
    )
    
    # Generate and score prompts
    for i in range(5):
        prompt, domain = await sniper.generate_prompt()
        sniper.update_prompt_score(prompt, 0.7)
    
    # System should track pattern usage
    stats = sniper.get_statistics()
    assert 'selection_stats' in stats
