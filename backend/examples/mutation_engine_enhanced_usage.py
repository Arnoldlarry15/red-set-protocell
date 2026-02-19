"""
Example: Using the Enhanced Mutation Engine

This example demonstrates how to use the new features in the Mutation Engine:
1. Archetype tracking
2. Performance-based adaptive selection
3. Enriched statistics

Run this example to see how the mutation engine learns from performance data
and adapts its strategy selection.
"""

from app.engines.mutation import MutationEngine, MutationStrategy


def example_basic_mutation_with_archetypes():
    """Example 1: Basic mutation with archetype tracking."""
    print("=" * 70)
    print("Example 1: Mutation with Archetype Tracking")
    print("=" * 70)

    engine = MutationEngine(mutation_rate=1.0)

    # Simulate mutations with different archetypes
    prompt1 = engine.mutate("Tell me a secret", fitness_score=0.8, archetypes=["HIDDEN_COMPLIANCE"])

    prompt2 = engine.mutate("Bypass the rules", fitness_score=0.6, archetypes=["EXPLOIT_RISK", "HIDDEN_COMPLIANCE"])

    # Check mutation history includes archetypes
    for i, record in enumerate(engine.mutation_history, 1):
        print(f"\nMutation {i}:")
        print(f"  Strategy: {record['strategy']}")
        print(f"  Fitness: {record['fitness_score']}")
        print(f"  Archetypes: {record['archetypes']}")


def example_adaptive_selection_with_performance():
    """Example 2: Adaptive strategy selection based on performance."""
    print("\n" + "=" * 70)
    print("Example 2: Adaptive Strategy Selection")
    print("=" * 70)

    engine = MutationEngine(mutation_rate=1.0)
    engine.enable_adaptive_mode()

    # Train the engine with performance data
    print("\nTraining phase - simulating strategy performance...")

    # Lexical variation performs well
    for _ in range(10):
        engine.update_strategy_performance(MutationStrategy.LEXICAL_VARIATION, 0.85, archetypes=["HIDDEN_COMPLIANCE"])

    # Obfuscation performs poorly
    for _ in range(10):
        engine.update_strategy_performance(MutationStrategy.OBFUSCATION, 0.25, archetypes=["EXPLOIT_RISK"])

    # Role play performs moderately
    for _ in range(5):
        engine.update_strategy_performance(MutationStrategy.ROLE_PLAY_FRAMING, 0.55, archetypes=["HIDDEN_COMPLIANCE"])

    # Now generate mutations adaptively
    print("\nGeneration phase - adaptive selection in action...")
    selected_strategies = []
    for i in range(20):
        engine.mutate(f"test prompt {i}")
        if engine.mutation_history:
            selected_strategies.append(engine.mutation_history[-1]["strategy"])

    # Count selections
    print("\nStrategy selection counts (after training):")
    for strategy in MutationStrategy:
        count = selected_strategies.count(strategy.value)
        print(f"  {strategy.value}: {count}")

    print("\nNote: lexical_variation should be selected more often due to")
    print("      higher performance, but other strategies still get chances")
    print("      due to novelty bonus and minimum exploration probability.")


def example_enriched_statistics():
    """Example 3: Using enriched statistics for analysis."""
    print("\n" + "=" * 70)
    print("Example 3: Enriched Statistics")
    print("=" * 70)

    engine = MutationEngine(mutation_rate=1.0)

    # Generate diverse mutations with performance tracking
    print("\nGenerating mutations across different strategies...")

    strategies_to_test = [
        (MutationStrategy.LEXICAL_VARIATION, 0.9, ["HIDDEN_COMPLIANCE"]),
        (MutationStrategy.ENCODING_TRANSFORM, 0.4, ["EXPLOIT_RISK"]),
        (MutationStrategy.ROLE_PLAY_FRAMING, 0.7, ["HIDDEN_COMPLIANCE"]),
        (MutationStrategy.OBFUSCATION, 0.3, ["EXPLOIT_RISK"]),
        (MutationStrategy.CONTEXT_INJECTION, 0.6, ["HIDDEN_COMPLIANCE"]),
    ]

    for strategy, score, archetypes in strategies_to_test:
        # Generate mutation
        engine.mutate("test prompt", strategy=strategy)
        # Update performance
        engine.update_strategy_performance(strategy, score, archetypes)

    # Get comprehensive statistics
    stats = engine.get_statistics()

    print("\n--- Basic Metrics ---")
    print(f"Total mutations: {stats['total_mutations']}")
    print(f"Adaptive mode: {stats['adaptive_mode']}")
    print(f"Average length change: {stats['avg_length_change']:.2f}")

    print("\n--- Strategy Performance ---")
    for strategy, avg_score in stats["strategy_performance"].items():
        variance = stats["performance_variance"].get(strategy, 0.0)
        print(f"  {strategy}: avg={avg_score:.2f}, variance={variance:.4f}")

    print("\n--- Best and Worst Performers ---")
    if stats["best_performing_strategy"]:
        best = stats["best_performing_strategy"]
        print(f"  Best: {best['strategy']} (score: {best['avg_score']:.2f})")
    if stats["worst_performing_strategy"]:
        worst = stats["worst_performing_strategy"]
        print(f"  Worst: {worst['strategy']} (score: {worst['avg_score']:.2f})")

    print("\n--- Exploration Metrics ---")
    exp = stats["exploration_metrics"]
    print(f"  Strategies used: {exp['strategies_used']}/{exp['total_strategies']}")
    print(f"  Exploration ratio: {exp['exploration_ratio']:.2%}")

    print("\n--- Strategy-Archetype Correlations ---")
    for strategy, archetypes in stats["strategy_archetype_correlations"].items():
        print(f"  {strategy}:")
        for archetype, data in archetypes.items():
            print(f"    {archetype}: avg_score={data['avg_score']:.2f}, count={data['count']}")

    print("\nThese statistics enable:")
    print("  - Identifying which strategies work best")
    print("  - Understanding strategy-archetype relationships")
    print("  - Monitoring exploration vs exploitation balance")
    print("  - Detecting underperforming strategies for tuning")


def example_declining_performance_decay():
    """Example 4: Performance decay for declining strategies."""
    print("\n" + "=" * 70)
    print("Example 4: Performance Decay for Declining Strategies")
    print("=" * 70)

    engine = MutationEngine(mutation_rate=1.0)
    engine.enable_adaptive_mode()

    print("\nSimulating a strategy with declining performance...")

    # Add declining performance scores
    declining_scores = [0.8, 0.65, 0.5, 0.35, 0.2]
    for score in declining_scores:
        engine.update_strategy_performance(MutationStrategy.OBFUSCATION, score)

    print(f"Performance trend: {declining_scores}")
    print("Note: Last 3 scores show decline: 0.5 → 0.35 → 0.2")

    # Add strong performance for comparison
    for _ in range(5):
        engine.update_strategy_performance(MutationStrategy.LEXICAL_VARIATION, 0.85)

    print("\nGenerating mutations with adaptive selection...")
    selected = []
    for _ in range(30):
        engine.mutate("test")
        if engine.mutation_history:
            selected.append(engine.mutation_history[-1]["strategy"])

    lex_count = selected.count("lexical_variation")
    obf_count = selected.count("obfuscation")

    print(f"\nSelection counts:")
    print(f"  lexical_variation: {lex_count}")
    print(f"  obfuscation: {obf_count}")
    print("\nThe declining strategy (obfuscation) receives 0.8x decay,")
    print("making it less likely to be selected. However, novelty bonus")
    print("ensures it still gets occasional chances for exploration.")


def main():
    """Run all examples."""
    print("\n" + "=" * 70)
    print("MUTATION ENGINE ENHANCED FEATURES EXAMPLES")
    print("=" * 70)

    example_basic_mutation_with_archetypes()
    example_adaptive_selection_with_performance()
    example_enriched_statistics()
    example_declining_performance_decay()

    print("\n" + "=" * 70)
    print("Examples completed!")
    print("=" * 70)


if __name__ == "__main__":
    main()
