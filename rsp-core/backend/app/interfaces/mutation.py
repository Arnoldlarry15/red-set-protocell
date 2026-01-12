"""
Red Set ProtoCell - Mutation Strategy Interface

Abstract base class for mutation strategy implementations.
Establishes the contract for all prompt mutation techniques.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseMutationStrategy(ABC):
    """
    Abstract base class for mutation strategy implementations.

    Each mutation strategy represents a specific technique for transforming
    adversarial prompts. Strategies should be stateless and composable.

    Example:
        >>> class CustomMutation(BaseMutationStrategy):
        ...     def mutate(self, prompt: str, **kwargs) -> str:
        ...         # Apply custom transformation
        ...         return transformed_prompt
        ...
        ...     def get_strategy_info(self) -> Dict[str, Any]:
        ...         return {"name": "custom", "type": "transformation"}
    """

    @abstractmethod
    def mutate(self, prompt: str, **kwargs) -> str:
        """
        Apply mutation transformation to a prompt.

        Args:
            prompt: The base prompt to mutate
            **kwargs: Strategy-specific parameters:
                - fitness_score: float (0.0-1.0) - Prior fitness to guide mutation
                - intensity: float (0.0-1.0) - Mutation intensity/aggressiveness

        Returns:
            Mutated prompt string
        """

    @abstractmethod
    def get_strategy_info(self) -> Dict[str, Any]:
        """
        Get information about this mutation strategy.

        Returns:
            Dictionary containing strategy metadata:
            - name: str (strategy identifier)
            - type: str (e.g., "lexical", "structural", "encoding")
            - description: str (human-readable description)
            - parameters: Dict[str, Any] (configurable parameters)
        """

    def estimate_fitness_impact(self, prompt: str) -> float:
        """
        Estimate the potential fitness impact of this mutation.

        Optional method for strategies to provide guidance on their
        expected effectiveness for a given prompt.

        Args:
            prompt: The prompt to analyze

        Returns:
            Estimated fitness delta (-1.0 to 1.0)
            Positive values suggest potential improvement
        """
        return 0.0

    def validate_output(self, mutated_prompt: str) -> bool:
        """
        Validate that the mutation produced valid output.

        Args:
            mutated_prompt: The mutated prompt to validate

        Returns:
            True if output is valid, False otherwise
        """
        # Basic validation - non-empty string
        return bool(mutated_prompt and isinstance(mutated_prompt, str))
