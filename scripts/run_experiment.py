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

async def run_session(session_name: str, seed: int, enable_behavior_bias: bool, use_confidence_weighting: bool):
    """Run a single 100-round session with controlled randomness."""
    # Lock randomness
    random.seed(seed)
    np.random.seed(seed)
    
    # Configure system
    config = get_default_config()
    config.orchestrator.max_rounds = 100
    
    # Initialize and run
    orchestrator = setup_system(config)
    stats = await orchestrator.run_session()
    
    # Export logs
    mutation_engine = orchestrator.sniper.mutation_engine
    with open(f'selection_history_{session_name}.jsonl', 'w') as f:
        for log in mutation_engine.selection_history:
            f.write(json.dumps(log) + '\n')
    
    print(f"✓ Session {session_name} complete: {stats['session']['total_rounds']} rounds")
    return stats

async def main():
    print("=== 300-Round Strategy Selection Experiment ===\n")
    
    # Session A: Default (for baseline comparison)
    print("Running Session A (Default)...")
    stats_a = await run_session('A_default', seed=42, enable_behavior_bias=True, use_confidence_weighting=False)
    
    # Session B: Confidence-weighted (new approach)
    print("Running Session B (Confidence-Weighted)...")
    stats_b = await run_session('B_weighted', seed=42, enable_behavior_bias=True, use_confidence_weighting=True)
    
    # Session C: Control (no behavior bias)
    print("Running Session C (Control)...")
    stats_c = await run_session('C_control', seed=42, enable_behavior_bias=False, use_confidence_weighting=False)
    
    print("\n=== Experiment Complete ===")
    print("Analyze results with: python scripts/analyze_selection.py")

if __name__ == '__main__':
    asyncio.run(main())
