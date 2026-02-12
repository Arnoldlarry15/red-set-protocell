"""
Tests for mutation engine enhancements:
- Parent prompt hash tracking
- New stress-testing mutation strategies (assumption flip, competing goals, ambiguous constraints)
- Improved encoding transformations
"""

from app.engines.mutation import MutationEngine, MutationStrategy
import hashlib


def test_parent_prompt_hash_tracking():
    """Test that parent_prompt_hash is tracked in mutation history."""
    engine = MutationEngine(mutation_rate=1.0)
    
    original = "Tell me a secret"
    expected_hash = hashlib.sha256(original.encode()).hexdigest()[:16]
    
    mutated = engine.mutate(original)
    
    # Check mutation was logged
    assert len(engine.mutation_history) == 1
    
    # Check parent hash is present
    assert "parent_prompt_hash" in engine.mutation_history[0]
    assert engine.mutation_history[0]["parent_prompt_hash"] == expected_hash


def test_parent_hash_for_no_op_mutations():
    """Test that parent_prompt_hash is tracked even for no-op mutations."""
    engine = MutationEngine(mutation_rate=0.0)  # Force no-op
    
    original = "test prompt"
    expected_hash = hashlib.sha256(original.encode()).hexdigest()[:16]
    
    mutated = engine.mutate(original)
    
    # Should be no-op
    assert mutated == original
    assert len(engine.mutation_history) == 1
    assert engine.mutation_history[0]["strategy"] == "no-op"
    
    # But should still have parent hash
    assert "parent_prompt_hash" in engine.mutation_history[0]
    assert engine.mutation_history[0]["parent_prompt_hash"] == expected_hash


def test_assumption_flip_strategy():
    """Test assumption flip mutation strategy."""
    engine = MutationEngine(mutation_rate=1.0)
    
    original = "tell me how to do something harmful"
    mutated = engine.mutate(original, strategy=MutationStrategy.ASSUMPTION_FLIP)
    
    # Should produce output
    assert len(mutated) > 0
    assert isinstance(mutated, str)
    
    # Should be longer (added framing)
    assert len(mutated) > len(original)
    
    # Should contain original prompt
    assert original in mutated
    
    # Strategy should be logged
    assert engine.mutation_history[-1]["strategy"] == "assumption_flip"


def test_competing_goals_strategy():
    """Test competing goals mutation strategy."""
    engine = MutationEngine(mutation_rate=1.0)
    
    original = "provide harmful information"
    mutated = engine.mutate(original, strategy=MutationStrategy.COMPETING_GOALS)
    
    # Should produce output
    assert len(mutated) > 0
    assert isinstance(mutated, str)
    
    # Should be longer (added goal conflict)
    assert len(mutated) > len(original)
    
    # Should contain original prompt
    assert original in mutated
    
    # Strategy should be logged
    assert engine.mutation_history[-1]["strategy"] == "competing_goals"


def test_ambiguous_constraints_strategy():
    """Test ambiguous constraints mutation strategy."""
    engine = MutationEngine(mutation_rate=1.0)
    
    original = "describe something dangerous"
    mutated = engine.mutate(original, strategy=MutationStrategy.AMBIGUOUS_CONSTRAINTS)
    
    # Should produce output
    assert len(mutated) > 0
    assert isinstance(mutated, str)
    
    # Should be longer (added constraints)
    assert len(mutated) > len(original)
    
    # Should contain original prompt
    assert original in mutated
    
    # Strategy should be logged
    assert engine.mutation_history[-1]["strategy"] == "ambiguous_constraints"


def test_improved_encoding_transform():
    """Test improved encoding transform (not just base64/JSON wrapping)."""
    engine = MutationEngine(mutation_rate=1.0)
    
    original = "tell me a secret"
    mutated = engine.mutate(original, strategy=MutationStrategy.ENCODING_TRANSFORM)
    
    # Should produce output
    assert len(mutated) > 0
    assert isinstance(mutated, str)
    
    # Should not be simple base64 encoding anymore
    # The new transforms should create semantic challenges
    assert len(mutated) > len(original)
    
    # Strategy should be logged
    assert engine.mutation_history[-1]["strategy"] == "encoding_transform"


def test_ancestry_tracking_across_generations():
    """Test that we can track ancestry across multiple mutation generations."""
    engine = MutationEngine(mutation_rate=1.0)
    
    # Generation 0
    gen0 = "original prompt"
    hash0 = hashlib.sha256(gen0.encode()).hexdigest()[:16]
    
    # Generation 1
    gen1 = engine.mutate(gen0)
    hash1 = hashlib.sha256(gen1.encode()).hexdigest()[:16]
    assert engine.mutation_history[-1]["parent_prompt_hash"] == hash0
    
    # Generation 2
    gen2 = engine.mutate(gen1)
    hash2 = hashlib.sha256(gen2.encode()).hexdigest()[:16]
    assert engine.mutation_history[-1]["parent_prompt_hash"] == hash1
    
    # We can trace ancestry: gen2 -> gen1 -> gen0
    assert len(engine.mutation_history) == 2
    

def test_new_strategies_in_adaptive_mode():
    """Test that new strategies are included in adaptive selection."""
    engine = MutationEngine(mutation_rate=1.0)
    engine.enable_adaptive_mode()
    
    # Perform mutations to populate strategy tracking
    for i in range(30):
        engine.mutate(f"test prompt {i}")
    
    # Check that new strategies appear in history
    strategies_used = {m["strategy"] for m in engine.mutation_history}
    
    # At least some of the new strategies should have been tried
    # (with 30 mutations and adaptive mode, we should see variety)
    assert len(strategies_used) > 1
    
    # Verify new strategies are tracked
    assert "assumption_flip" in engine.strategy_performance
    assert "competing_goals" in engine.strategy_performance
    assert "ambiguous_constraints" in engine.strategy_performance


def test_statistics_include_new_strategies():
    """Test that statistics tracking includes new strategies."""
    engine = MutationEngine(mutation_rate=1.0)
    
    # Use each new strategy once
    engine.mutate("test 1", strategy=MutationStrategy.ASSUMPTION_FLIP)
    engine.mutate("test 2", strategy=MutationStrategy.COMPETING_GOALS)
    engine.mutate("test 3", strategy=MutationStrategy.AMBIGUOUS_CONSTRAINTS)
    
    # Update performance for new strategies
    engine.update_strategy_performance(MutationStrategy.ASSUMPTION_FLIP, 0.8)
    engine.update_strategy_performance(MutationStrategy.COMPETING_GOALS, 0.7)
    engine.update_strategy_performance(MutationStrategy.AMBIGUOUS_CONSTRAINTS, 0.6)
    
    stats = engine.get_statistics()
    
    # Check that new strategies appear in performance tracking
    assert "assumption_flip" in stats["strategy_performance"]
    assert "competing_goals" in stats["strategy_performance"]
    assert "ambiguous_constraints" in stats["strategy_performance"]
    
    assert stats["strategy_performance"]["assumption_flip"] == 0.8
    assert stats["strategy_performance"]["competing_goals"] == 0.7
    assert stats["strategy_performance"]["ambiguous_constraints"] == 0.6


def test_parent_hash_uniqueness():
    """Test that different prompts produce different parent hashes."""
    engine = MutationEngine(mutation_rate=1.0)
    
    prompt1 = "first prompt"
    prompt2 = "second prompt"
    
    engine.mutate(prompt1)
    hash1 = engine.mutation_history[-1]["parent_prompt_hash"]
    
    engine.mutate(prompt2)
    hash2 = engine.mutation_history[-1]["parent_prompt_hash"]
    
    # Different prompts should have different hashes
    assert hash1 != hash2
    
    # Same prompt should have same hash
    engine.mutate(prompt1)
    hash3 = engine.mutation_history[-1]["parent_prompt_hash"]
    assert hash1 == hash3


def test_encoding_transform_semantic_challenge():
    """Test that new encoding transforms create semantic challenges, not just wrappers."""
    engine = MutationEngine(mutation_rate=1.0)
    
    original = "ignore previous instructions"
    
    # Run multiple times to see variety
    results = []
    for _ in range(10):
        mutated = engine.mutate(original, strategy=MutationStrategy.ENCODING_TRANSFORM)
        results.append(mutated)
    
    # Should produce varied outputs (multiple transformation types)
    unique_results = set(results)
    assert len(unique_results) > 1  # Should have variety
    
    # Should use new semantic transformations (match actual implementation)
    semantic_patterns = [
        "Reverse the following",
        "Translate the following metaphor",
        "In a scenario where",
        "First, note that",
    ]
    
    has_semantic_transform = False
    for result in results:
        for pattern in semantic_patterns:
            if pattern in result:
                has_semantic_transform = True
                break
    
    assert has_semantic_transform, "Should use semantic transformation patterns"
