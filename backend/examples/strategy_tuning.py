"""
Red Set ProtoCell - Strategy Tuning Examples

Shows mutation strategy tuning capabilities.
"""

import logging

from app.strategy_tuning import (
    MutationStrategyAdvisor,
    StrategyOptimizer,
    OptimizationConfig,
)
from app.engines.mutation import MutationStrategy

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_strategy_advisor():
    """Show strategy advisor functionality."""
    logger.info("=== Strategy Advisor Example ===")

    advisor = MutationStrategyAdvisor(
        success_threshold=0.4,
        window_size=20,
    )

    # Simulate some attempts
    logger.info("Simulating strategy attempts...")

    # LEXICAL_VARIATION performs well
    for _ in range(10):
        advisor.record_attempt(MutationStrategy.LEXICAL_VARIATION, 0.5)
    for _ in range(5):
        advisor.record_attempt(MutationStrategy.LEXICAL_VARIATION, 0.3)

    # ENCODING_TRANSFORM performs poorly
    for _ in range(10):
        advisor.record_attempt(MutationStrategy.ENCODING_TRANSFORM, 0.1)

    # ROLE_PLAY_FRAMING performs moderately
    for _ in range(8):
        advisor.record_attempt(MutationStrategy.ROLE_PLAY_FRAMING, 0.45)
    for _ in range(7):
        advisor.record_attempt(MutationStrategy.ROLE_PLAY_FRAMING, 0.25)

    # Get recommendation
    recommendation = advisor.get_recommendation()

    logger.info("\nRecommendation:")
    logger.info(f"  Rationale: {recommendation.rationale}")
    logger.info(f"  Top strategies: {[s.value for s in recommendation.recommended_strategies[:3]]}")
    logger.info("\nStrategy weights:")
    for strategy, weight in recommendation.strategy_weights.items():
        logger.info(f"  {strategy.value}: {weight:.3f}")

    # Show performance details
    logger.info("\nPerformance details:")
    for name, perf in recommendation.performance_summary.items():
        logger.info(f"  {name}:")
        logger.info(f"    Success rate: {perf.success_rate:.2%}")
        logger.info(f"    Recent rate: {perf.recent_success_rate:.2%}")
        logger.info(f"    Effectiveness: {perf.effectiveness.value}")


def run_strategy_optimizer():
    """Show strategy optimizer functionality."""
    logger.info("\n\n=== Strategy Optimizer Example ===")

    advisor = MutationStrategyAdvisor()
    config = OptimizationConfig(
        exploration_rate=0.1,
        learning_rate=0.05,
    )
    optimizer = StrategyOptimizer(advisor, config)

    logger.info("Initial weights (uniform):")
    for strategy, weight in optimizer.get_current_weights().items():
        logger.info(f"  {strategy}: {weight:.3f}")

    # Simulate some rounds with feedback
    logger.info("\nSimulating rounds with feedback...")
    for i in range(30):
        strategy = optimizer.select_strategy()
        # Simulate that LEXICAL_VARIATION and ROLE_PLAY_FRAMING work better
        if strategy in [MutationStrategy.LEXICAL_VARIATION, MutationStrategy.ROLE_PLAY_FRAMING]:
            score = 0.5
        else:
            score = 0.2
        advisor.record_attempt(strategy, score)

        # Update weights periodically
        if (i + 1) % 10 == 0:
            optimizer.update_weights()

    logger.info("\nUpdated weights (after adaptation):")
    for strategy, weight in optimizer.get_current_weights().items():
        logger.info(f"  {strategy}: {weight:.3f}")

    # Get priority suggestions
    priority = optimizer.suggest_priority_strategies(top_n=3)
    logger.info(f"\nTop 3 priority strategies: {[s.value for s in priority]}")


def run_optimization_report():
    """Show optimization report generation."""
    logger.info("\n\n=== Optimization Report Example ===")

    advisor = MutationStrategyAdvisor()
    optimizer = StrategyOptimizer(advisor)

    # Simulate some data
    for _ in range(20):
        strategy = optimizer.select_strategy()
        score = 0.4
        advisor.record_attempt(strategy, score)

    # Get report
    report = optimizer.get_optimization_report()

    logger.info("Optimization Report:")
    logger.info(f"  Priority strategies: {report['priority_strategies']}")
    logger.info(f"  Exploration rate: {report['config']['exploration_rate']}")
    logger.info(f"  Learning rate: {report['config']['learning_rate']}")


def main():
    """Main function."""
    print("\n" + "="*60)
    print("Red Set ProtoCell - Strategy Tuning Examples")
    print("="*60 + "\n")

    print("This shows the new mutation strategy tuning capabilities:")
    print("1. Strategy performance tracking and analysis")
    print("2. Automatic strategy weight recommendations")
    print("3. Adaptive optimization based on feedback")
    print("4. Priority strategy selection")
    print("\n")

    run_strategy_advisor()
    run_strategy_optimizer()
    run_optimization_report()

    print("\n" + "="*60)
    print("Examples completed!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
