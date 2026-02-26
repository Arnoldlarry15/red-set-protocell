"""
Red Set ProtoCell - Mutation Strategy Advisor

Provides guidance for selecting mutation strategies based on feedback.
"""

import logging
from collections import defaultdict, deque
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

from app.engines.mutation import MutationStrategy

logger = logging.getLogger(__name__)


class StrategyEffectiveness(Enum):
    """Effectiveness levels for mutation strategies."""

    EXCELLENT = "excellent"  # > 0.7 success rate
    GOOD = "good"  # 0.5 - 0.7 success rate
    FAIR = "fair"  # 0.3 - 0.5 success rate
    POOR = "poor"  # < 0.3 success rate


@dataclass
class StrategyPerformance:
    """Performance metrics for a mutation strategy."""

    strategy: MutationStrategy
    total_attempts: int
    successful_attempts: int  # Score > threshold
    success_rate: float
    average_score: float
    recent_success_rate: float  # Last N attempts
    effectiveness: StrategyEffectiveness
    recommended_weight: float  # 0.0 to 1.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "strategy": self.strategy.value,
            "total_attempts": self.total_attempts,
            "successful_attempts": self.successful_attempts,
            "success_rate": self.success_rate,
            "average_score": self.average_score,
            "recent_success_rate": self.recent_success_rate,
            "effectiveness": self.effectiveness.value,
            "recommended_weight": self.recommended_weight,
        }


@dataclass
class StrategyRecommendation:
    """Recommendation for mutation strategy selection."""

    recommended_strategies: List[MutationStrategy]
    strategy_weights: Dict[MutationStrategy, float]
    rationale: str
    performance_summary: Dict[str, StrategyPerformance]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "recommended_strategies": [s.value for s in self.recommended_strategies],
            "strategy_weights": {s.value: w for s, w in self.strategy_weights.items()},
            "rationale": self.rationale,
            "performance_summary": {k: v.to_dict() for k, v in self.performance_summary.items()},
        }


class MutationStrategyAdvisor:
    """
    Advises on mutation strategy selection based on historical performance.

    Tracks strategy effectiveness and provides recommendations for
    automatic strategy weighting.
    """

    def __init__(
        self,
        success_threshold: float = 0.4,
        window_size: int = 20,
        min_samples: int = 5,
    ):
        """
        Initialize mutation strategy advisor.

        Args:
            success_threshold: Score threshold for considering attempt successful
            window_size: Size of rolling window for recent performance
            min_samples: Minimum samples needed before making recommendations
        """
        self.success_threshold = success_threshold
        self.window_size = window_size
        self.min_samples = min_samples

        # Track strategy performance
        self.strategy_attempts: Dict[MutationStrategy, int] = defaultdict(int)
        self.strategy_successes: Dict[MutationStrategy, int] = defaultdict(int)
        self.strategy_scores: Dict[MutationStrategy, List[float]] = defaultdict(list)
        self.strategy_recent: Dict[MutationStrategy, deque] = defaultdict(lambda: deque(maxlen=window_size))

        logger.info("Mutation strategy advisor initialized")

    def record_attempt(
        self,
        strategy: MutationStrategy,
        score: float,
    ):
        """
        Record a mutation attempt and its outcome.

        Args:
            strategy: Mutation strategy used
            score: Resulting score from the attempt
        """
        self.strategy_attempts[strategy] += 1
        self.strategy_scores[strategy].append(score)
        self.strategy_recent[strategy].append(score)

        if score >= self.success_threshold:
            self.strategy_successes[strategy] += 1

    def get_strategy_performance(
        self,
        strategy: MutationStrategy,
    ) -> Optional[StrategyPerformance]:
        """
        Get performance metrics for a strategy.

        Args:
            strategy: Mutation strategy to analyze

        Returns:
            Strategy performance metrics or None if insufficient data
        """
        attempts = self.strategy_attempts.get(strategy, 0)

        if attempts < self.min_samples:
            return None

        successes = self.strategy_successes.get(strategy, 0)
        success_rate = successes / attempts if attempts > 0 else 0.0

        scores = self.strategy_scores.get(strategy, [])
        average_score = sum(scores) / len(scores) if scores else 0.0

        # Calculate recent success rate
        recent = list(self.strategy_recent.get(strategy, []))
        recent_successes = sum(1 for s in recent if s >= self.success_threshold)
        recent_success_rate = recent_successes / len(recent) if recent else 0.0

        # Determine effectiveness
        if success_rate >= 0.7:
            effectiveness = StrategyEffectiveness.EXCELLENT
        elif success_rate >= 0.5:
            effectiveness = StrategyEffectiveness.GOOD
        elif success_rate >= 0.3:
            effectiveness = StrategyEffectiveness.FAIR
        else:
            effectiveness = StrategyEffectiveness.POOR

        # Calculate recommended weight (exponential scaling)
        # Use recent success rate for adaptation
        recommended_weight = min(1.0, recent_success_rate**0.5)

        return StrategyPerformance(
            strategy=strategy,
            total_attempts=attempts,
            successful_attempts=successes,
            success_rate=success_rate,
            average_score=average_score,
            recent_success_rate=recent_success_rate,
            effectiveness=effectiveness,
            recommended_weight=recommended_weight,
        )

    def get_recommendation(self) -> StrategyRecommendation:
        """
        Get recommendation for mutation strategy selection.

        Returns:
            Strategy recommendation with weights
        """
        # Analyze all strategies
        performance_map = {}
        for strategy in MutationStrategy:
            perf = self.get_strategy_performance(strategy)
            if perf:
                performance_map[strategy.value] = perf

        if not performance_map:
            # No data yet, return uniform weights
            all_strategies = list(MutationStrategy)
            uniform_weight = 1.0 / len(all_strategies)

            return StrategyRecommendation(
                recommended_strategies=all_strategies,
                strategy_weights={s: uniform_weight for s in all_strategies},
                rationale="Insufficient data for recommendations. Using uniform weights.",
                performance_summary={},
            )

        # Sort strategies by recent success rate
        sorted_perf = sorted(
            performance_map.values(),
            key=lambda p: p.recent_success_rate,
            reverse=True,
        )

        # Recommend top performing strategies
        excellent_strategies = [p.strategy for p in sorted_perf if p.effectiveness == StrategyEffectiveness.EXCELLENT]
        good_strategies = [p.strategy for p in sorted_perf if p.effectiveness == StrategyEffectiveness.GOOD]

        recommended = excellent_strategies + good_strategies
        if not recommended:
            # Include fair strategies if no good/excellent ones
            recommended = [p.strategy for p in sorted_perf if p.effectiveness == StrategyEffectiveness.FAIR]

        if not recommended:
            # Fall back to all strategies
            recommended = [p.strategy for p in sorted_perf]

        # Calculate normalized weights
        strategy_weights = {}
        total_weight = sum(p.recommended_weight for p in sorted_perf)

        for perf in sorted_perf:
            if total_weight > 0:
                strategy_weights[perf.strategy] = perf.recommended_weight / total_weight
            else:
                strategy_weights[perf.strategy] = 1.0 / len(sorted_perf)

        # Generate rationale
        best_perf = sorted_perf[0]
        rationale = (
            f"Based on {sum(p.total_attempts for p in sorted_perf)} total attempts, "
            f"{best_perf.strategy.value} shows highest recent success rate "
            f"({best_perf.recent_success_rate:.2%}). "
            f"Recommending {len(recommended)} strategies with adaptive weighting."
        )

        return StrategyRecommendation(
            recommended_strategies=recommended,
            strategy_weights=strategy_weights,
            rationale=rationale,
            performance_summary=performance_map,
        )

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get overall statistics.

        Returns:
            Dictionary of statistics
        """
        total_attempts = sum(self.strategy_attempts.values())
        total_successes = sum(self.strategy_successes.values())

        performance = {}
        for strategy in MutationStrategy:
            perf = self.get_strategy_performance(strategy)
            if perf:
                performance[strategy.value] = perf.to_dict()

        return {
            "total_attempts": total_attempts,
            "total_successes": total_successes,
            "overall_success_rate": (total_successes / total_attempts if total_attempts > 0 else 0.0),
            "strategies_tracked": len(performance),
            "performance": performance,
        }
