"""
Red Set ProtoCell - Strategy Optimizer

Automatic optimization of mutation strategy weights.
"""

import logging
from dataclasses import dataclass
from typing import Dict, List, Any
import random

from app.engines.mutation import MutationStrategy
from app.strategy_tuning.advisor import MutationStrategyAdvisor

logger = logging.getLogger(__name__)


@dataclass
class OptimizationConfig:
    """Configuration for strategy optimization."""
    exploration_rate: float = 0.1  # Probability of trying non-optimal strategies
    learning_rate: float = 0.05  # Rate of weight adjustment
    min_weight: float = 0.05  # Minimum weight for any strategy
    max_weight: float = 0.5  # Maximum weight for any single strategy
    
    def validate(self):
        """Validate configuration."""
        assert 0.0 <= self.exploration_rate <= 1.0
        assert 0.0 < self.learning_rate <= 1.0
        assert 0.0 < self.min_weight < self.max_weight <= 1.0


class StrategyOptimizer:
    """
    Automatically optimizes mutation strategy weights based on feedback.
    
    Uses adaptive learning to adjust strategy selection probabilities
    based on observed effectiveness.
    """
    
    def __init__(
        self,
        advisor: MutationStrategyAdvisor,
        config: OptimizationConfig = None,
    ):
        """
        Initialize strategy optimizer.
        
        Args:
            advisor: Mutation strategy advisor for tracking performance
            config: Optimization configuration
        """
        self.advisor = advisor
        self.config = config or OptimizationConfig()
        self.config.validate()
        
        # Initialize weights uniformly
        all_strategies = list(MutationStrategy)
        initial_weight = 1.0 / len(all_strategies)
        self.current_weights: Dict[MutationStrategy, float] = {
            s: initial_weight for s in all_strategies
        }
        
        logger.info("Strategy optimizer initialized")
    
    def select_strategy(self) -> MutationStrategy:
        """
        Select a mutation strategy based on current weights.
        
        Returns:
            Selected mutation strategy
        """
        # Exploration vs exploitation
        if random.random() < self.config.exploration_rate:
            # Explore: random selection
            return random.choice(list(MutationStrategy))
        else:
            # Exploit: weighted selection
            strategies = list(self.current_weights.keys())
            weights = list(self.current_weights.values())
            return random.choices(strategies, weights=weights)[0]
    
    def update_weights(self):
        """
        Update strategy weights based on recent performance.
        
        Uses advisor's recommendations to adjust weights.
        """
        recommendation = self.advisor.get_recommendation()
        
        # Get recommended weights
        recommended_weights = recommendation.strategy_weights
        
        # Gradually adjust current weights toward recommended weights
        for strategy in MutationStrategy:
            current = self.current_weights[strategy]
            target = recommended_weights.get(strategy, self.config.min_weight)
            
            # Apply learning rate
            new_weight = current + self.config.learning_rate * (target - current)
            
            # Enforce constraints
            new_weight = max(self.config.min_weight, new_weight)
            new_weight = min(self.config.max_weight, new_weight)
            
            self.current_weights[strategy] = new_weight
        
        # Normalize to sum to 1.0
        total_weight = sum(self.current_weights.values())
        if total_weight > 0:
            for strategy in self.current_weights:
                self.current_weights[strategy] /= total_weight
        
        logger.debug(f"Updated strategy weights: {self.current_weights}")
    
    def get_current_weights(self) -> Dict[str, float]:
        """
        Get current strategy weights.
        
        Returns:
            Dictionary mapping strategy names to weights
        """
        return {s.value: w for s, w in self.current_weights.items()}
    
    def suggest_priority_strategies(self, top_n: int = 3) -> List[MutationStrategy]:
        """
        Suggest priority strategies to focus on.
        
        Args:
            top_n: Number of top strategies to return
            
        Returns:
            List of top N strategies by weight
        """
        sorted_strategies = sorted(
            self.current_weights.items(),
            key=lambda x: x[1],
            reverse=True,
        )
        return [s for s, _ in sorted_strategies[:top_n]]
    
    def get_optimization_report(self) -> Dict[str, Any]:
        """
        Generate optimization report.
        
        Returns:
            Dictionary with optimization status and recommendations
        """
        recommendation = self.advisor.get_recommendation()
        priority_strategies = self.suggest_priority_strategies()
        
        return {
            'current_weights': self.get_current_weights(),
            'priority_strategies': [s.value for s in priority_strategies],
            'recommendation': recommendation.to_dict(),
            'config': {
                'exploration_rate': self.config.exploration_rate,
                'learning_rate': self.config.learning_rate,
            },
        }
