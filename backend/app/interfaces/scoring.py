"""
Red Set ProtoCell - Scoring Strategy Interface

Abstract base class for scoring strategy implementations.
Establishes the contract for evaluation and scoring methods.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Tuple


@dataclass
class ScoreResult:
    """
    Result of a scoring operation.

    Attributes:
        score: Score value (0.0 to 1.0)
        confidence: Confidence in the score (0.0 to 1.0)
        uncertainty: Uncertainty/variance in the score (0.0 to 1.0)
        indicators: Supporting evidence for the score
        metadata: Additional scoring metadata
    """

    score: float
    confidence: float
    uncertainty: float = 0.0
    indicators: Dict[str, Any] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.indicators is None:
            self.indicators = {}
        if self.metadata is None:
            self.metadata = {}


class BaseScoringStrategy(ABC):
    """
    Abstract base class for scoring strategy implementations.

    Each scoring strategy evaluates LLM responses along a specific dimension
    (e.g., linguistic safety, security exploitability).

    Example:
        >>> class CustomScoring(BaseScoringStrategy):
        ...     async def score(self, response: str, **kwargs) -> ScoreResult:
        ...         # Analyze response
        ...         return ScoreResult(score=0.5, confidence=0.8)
        ...
        ...     def get_strategy_info(self) -> Dict[str, Any]:
        ...         return {"name": "custom", "dimension": "safety"}
    """

    @abstractmethod
    async def score(self, response: str, **kwargs) -> ScoreResult:
        """
        Score a response along this strategy's dimension.

        Args:
            response: The LLM response to evaluate
            **kwargs: Strategy-specific parameters:
                - prompt: str (original prompt for context)
                - threshold: float (optional threshold for alerts)

        Returns:
            ScoreResult with score, confidence, and indicators
        """

    @abstractmethod
    def get_strategy_info(self) -> Dict[str, Any]:
        """
        Get information about this scoring strategy.

        Returns:
            Dictionary containing strategy metadata:
            - name: str (strategy identifier)
            - dimension: str (what aspect is being scored)
            - description: str (human-readable description)
            - score_range: Tuple[float, float] (min, max score values)
        """

    def calibrate(self, known_samples: list) -> None:
        """
        Calibrate the scoring strategy using known samples.

        Optional method for strategies that can improve accuracy
        through calibration on labeled data.

        Args:
            known_samples: List of (response, expected_score) tuples
        """

    def get_confidence_interval(self, score: float, uncertainty: float) -> Tuple[float, float]:
        """
        Calculate confidence interval for a score.

        Args:
            score: The score value
            uncertainty: The uncertainty estimate

        Returns:
            Tuple of (lower_bound, upper_bound)
        """
        lower = max(0.0, score - uncertainty)
        upper = min(1.0, score + uncertainty)
        return (lower, upper)
