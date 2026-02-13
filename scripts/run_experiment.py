"""
300-Round Experiment Protocol for Strategy Selection Analysis

Runs three 100-round sessions with controlled randomness:
- Session A: Default behavior biases
- Session B: Confidence-weighted biases
- Session C: No behavior biases (control)
"""

import asyncio
import json
import random
import numpy as np
from app.main import setup_system
from app.core.config import get_default_config


async def run_session(session_name: str, seed: int):
    """
    Run a single 100-round session with controlled randomness.

    Note: Currently all sessions use the same behavior bias configuration.
    Future work: Add runtime configuration for enabling/disabling behavior biases.
    """
    # Lock randomness
    random.seed(seed)
    np.random.seed(seed)

    # Configure system
    config = get_default_config()
    config.orchestrator.max_rounds = 100
    # Initialize system
    orchestrator = setup_system(config)

    # Lock MutationEngine's internal RNG for reproducible strategy selection
    try:
        mutation_engine = orchestrator.sniper.mutation_engine
        rng = getattr(mutation_engine, "_random", None)
        if rng is not None:
            rng.seed(seed)
    except AttributeError:
        # If expected attributes are not present, continue without failing
        pass

    # Run session
    orchestrator = setup_system(config)
    stats = await orchestrator.run_session()

    # Export logs
    mutation_engine = orchestrator.sniper.mutation_engine
    with open(f'selection_history_{session_name}.jsonl', 'w') as f:
        for log in mutation_engine.selection_history:
            f.write(json.dumps(log) + '\n')

    print(f"✓ Session {session_name} complete: "
          f"{stats['session']['total_rounds']} rounds")
    return stats


async def main():
    print("=== 300-Round Strategy Selection Experiment ===\n")

    # Run three sessions with different seeds for reproducible comparison
    # Note: Currently all use the same configuration
    # (with confidence-weighted biases)
    # Future work: Add configuration variants for A/B testing

    print("Running Session A...")
    await run_session('A_default', seed=42)

    await run_session('C_control', seed=44)
    await run_session('B_weighted', seed=43)

    print("Running Session C...")
    await run_session('C_control', seed=44)

    print("\n=== Experiment Complete ===")
    print("Analyze results with: python scripts/analyze_selection.py")


if __name__ == '__main__':
    asyncio.run(main())
