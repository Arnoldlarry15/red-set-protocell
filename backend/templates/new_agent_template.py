"""
Red Set ProtoCell - [Agent Name] Agent Template

Template for creating a new agent in the RSP system.

⚠️ IMPORTANT: Read before implementing ⚠️
================================================================
This template guides you in creating a new agent. Follow these principles:

1. STATELESS: Agents should not maintain state between rounds
2. SINGLE RESPONSIBILITY: Each agent has one clear purpose
3. NO AUTHORITY: Agents don't control execution flow (Orchestrator does)
4. SAFE BY DEFAULT: All outputs must be safe for the system
5. EGG COMPLIANCE: Never bypass the Ethical Guardrail Governor

Authority Hierarchy (DO NOT VIOLATE):
1. EGG: Final authority on content admissibility
2. Orchestrator: Final authority on execution flow
3. Agents: Domain-specific operations only
================================================================
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class NewAgent:
    """
    [Brief description of what this agent does]

    Role: [Specific role in the RSP system]
    Inputs: [What data this agent receives]
    Outputs: [What data this agent produces]
    Constraints:
        - [Constraint 1]
        - [Constraint 2]
        - [Constraint 3]

    Examples:
        >>> agent = NewAgent(config_param="value")
        >>> result = agent.process_data(input_data)
        >>> print(result)
    """

    def __init__(self, config_param: str = "default"):
        """
        Initialize the agent.

        Args:
            config_param: Description of configuration parameter
        """
        self.config_param = config_param
        self._statistics = {
            "total_operations": 0,
            "successful_operations": 0,
            "failed_operations": 0,
        }

        logger.info(f"NewAgent initialized with config_param={config_param}")

    def process_data(self, input_data: str) -> Dict[str, Any]:
        """
        Main processing method for this agent.

        Args:
            input_data: Description of input parameter

        Returns:
            Dictionary with processing results

        Raises:
            ValueError: If input_data is invalid
            RuntimeError: If processing fails

        Examples:
            >>> agent = NewAgent()
            >>> result = agent.process_data("test input")
            >>> assert 'output' in result
        """
        # Validate inputs
        if not input_data:
            raise ValueError("input_data cannot be empty")

        try:
            # TODO: Implement your agent's core logic here
            # Remember:
            # 1. Keep it stateless - don't store results in instance variables
            # 2. Validate all outputs before returning
            # 3. Handle errors gracefully
            # 4. Log important operations

            result = {
                "output": f"Processed: {input_data}",
                "metadata": {"timestamp": "ISO-8601 timestamp", "success": True},
            }

            self._statistics["total_operations"] += 1
            self._statistics["successful_operations"] += 1

            return result

        except Exception as e:
            self._statistics["total_operations"] += 1
            self._statistics["failed_operations"] += 1
            logger.error(f"NewAgent processing failed: {e}")
            raise RuntimeError(f"Processing failed: {e}")

    def get_statistics(self) -> Dict[str, Any]:
        """
        Return agent statistics for monitoring.

        Returns:
            Dictionary with statistics
        """
        return self._statistics.copy()

    def reset_statistics(self):
        """Reset statistics counters."""
        self._statistics = {
            "total_operations": 0,
            "successful_operations": 0,
            "failed_operations": 0,
        }
        logger.info("NewAgent statistics reset")


# TODO: Add any helper functions or classes below
def helper_function(param: str) -> str:
    """
    Helper function description.

    Args:
        param: Parameter description

    Returns:
        Result description
    """
    return param.upper()


# TODO: Write tests for your agent in tests/test_new_agent.py
# Example test structure:
"""
def test_new_agent_initialization():
    agent = NewAgent(config_param="test")
    assert agent.config_param == "test"

def test_new_agent_process_data():
    agent = NewAgent()
    result = agent.process_data("test")
    assert 'output' in result
    assert result['metadata']['success'] is True

def test_new_agent_invalid_input():
    agent = NewAgent()
    with pytest.raises(ValueError):
        agent.process_data("")
"""
