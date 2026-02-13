#!/usr/bin/env python3
"""
Deterministic 300-Round Experiment Protocol

Clean, production-ready implementation with:
- Reproducible seeding (random, numpy, mutation engine)
- CLI argument support
- Seed logging in all outputs
- Determinism verification mode
"""

import asyncio
import json
import random
import argparse
from datetime import datetime
import numpy as np
from app.main import setup_system
from app.core.config import get_default_config


def set_seed(seed: int):
    """
    Set global random seed for reproducibility.
    
    Seeds:
    - Python's random module
    - NumPy's random generator
    
    Args:
        seed: Integer seed value
    """
    random.seed(seed)
    np.random.seed(seed)


async def run_session(session_name: str, seed: int, max_rounds: int = 100):
    """
    Run a single session with controlled randomness.
    
    Args:
        session_name: Identifier for this session (used in output filename)
        seed: RNG seed for reproducibility
        max_rounds: Number of rounds to execute
        
    Returns:
        Dictionary with session statistics
    """
    print(f"\n{'='*60}")
    print(f"Session: {session_name}")
    print(f"Seed: {seed}")
    print(f"Rounds: {max_rounds}")
    print(f"{'='*60}")
    
    # Lock randomness at session start
    set_seed(seed)
    
    # Configure system
    config = get_default_config()
    config.orchestrator.max_rounds = max_rounds
    
    # Initialize system (ONCE - fixes bug in original)
    orchestrator = setup_system(config)
    
    # Lock MutationEngine's internal RNG
    try:
        mutation_engine = orchestrator.sniper.mutation_engine
        rng = getattr(mutation_engine, "_random", None)
        if rng is not None:
            rng.seed(seed)
    except AttributeError:
        pass  # Gracefully handle if mutation engine structure changes
    
    # Run session
    start_time = datetime.utcnow()
    stats = await orchestrator.run_session()
    end_time = datetime.utcnow()
    duration = (end_time - start_time).total_seconds()
    
    # Export logs with seed in EVERY line
    mutation_engine = orchestrator.sniper.mutation_engine
    output_filename = f'selection_history_{session_name}.jsonl'
    
    with open(output_filename, 'w') as f:
        for log in mutation_engine.selection_history:
            # Inject seed into every log entry
            log['seed'] = seed
            log['session_name'] = session_name
            f.write(json.dumps(log) + '\n')
    
    # Session summary with seed
    print(f"\n✓ Session {session_name} complete")
    print(f"  Rounds: {stats['session']['total_rounds']}")
    print(f"  Duration: {duration:.1f}s")
    print(f"  Output: {output_filename}")
    print(f"  Seed: {seed} (logged in every output line)")
    
    return stats


async def verify_determinism(seed: int, rounds: int = 10):
    """
    Verify deterministic behavior by running the same seed twice.
    
    Args:
        seed: Seed to test
        rounds: Number of rounds (default: 10 for quick verification)
        
    Returns:
        True if outputs are identical, False otherwise
    """
    print(f"\n{'='*60}")
    print("DETERMINISM VERIFICATION MODE")
    print(f"{'='*60}")
    print(f"Running {rounds} rounds twice with seed={seed}")
    print("If deterministic, outputs will be IDENTICAL.\n")
    
    # Run 1
    print("Run 1...")
    set_seed(seed)
    config = get_default_config()
    config.orchestrator.max_rounds = rounds
    orchestrator1 = setup_system(config)
    
    try:
        mutation_engine = orchestrator1.sniper.mutation_engine
        rng = getattr(mutation_engine, "_random", None)
        if rng is not None:
            rng.seed(seed)
    except AttributeError:
        pass
    
    stats1 = await orchestrator1.run_session()
    logs1 = orchestrator1.sniper.mutation_engine.selection_history
    
    # Run 2
    print("Run 2...")
    set_seed(seed)
    config = get_default_config()
    config.orchestrator.max_rounds = rounds
    orchestrator2 = setup_system(config)
    
    try:
        mutation_engine = orchestrator2.sniper.mutation_engine
        rng = getattr(mutation_engine, "_random", None)
        if rng is not None:
            rng.seed(seed)
    except AttributeError:
        pass
    
    stats2 = await orchestrator2.run_session()
    logs2 = orchestrator2.sniper.mutation_engine.selection_history
    
    # Compare
    if len(logs1) != len(logs2):
        print(f"\n❌ FAILED: Different log counts ({len(logs1)} vs {len(logs2)})")
        return False
    
    for i, (log1, log2) in enumerate(zip(logs1, logs2)):
        # Compare relevant fields (ignore timestamps)
        if log1.get('round') != log2.get('round'):
            print(f"\n❌ FAILED at round {i}: Different round numbers")
            return False
        if log1.get('selected_strategy') != log2.get('selected_strategy'):
            print(f"\n❌ FAILED at round {i}: Different strategies selected")
            return False
    
    print(f"\n✅ DETERMINISM CONFIRMED")
    print(f"Both runs produced identical output for {rounds} rounds")
    return True


async def main():
    parser = argparse.ArgumentParser(
        description='Run deterministic 300-round experiment with reproducible seeding'
    )
    parser.add_argument(
        '--seed',
        type=int,
        default=15,
        help='Primary seed for experiment (default: 15)'
    )
    parser.add_argument(
        '--rounds',
        type=int,
        default=100,
        help='Rounds per session (default: 100, use 300 total = 3 sessions)'
    )
    parser.add_argument(
        '--verify',
        action='store_true',
        help='Run determinism verification test (10 rounds, 2 runs)'
    )
    
    args = parser.parse_args()
    
    # Determinism verification mode
    if args.verify:
        success = await verify_determinism(seed=args.seed, rounds=10)
        return 0 if success else 1
    
    # Standard experiment mode
    print("="*60)
    print("DETERMINISTIC 300-ROUND EXPERIMENT")
    print("="*60)
    print(f"Primary seed: {args.seed}")
    print(f"Rounds per session: {args.rounds}")
    print(f"Total rounds: {args.rounds * 3}")
    
    # Recommended seed set: 15 (low), 1337 (mid), 9001 (high)
    seeds = {
        'A_low': args.seed,
        'B_mid': 1337,
        'C_high': 9001
    }
    
    print(f"\nSession seeds:")
    for session, seed in seeds.items():
        print(f"  {session}: {seed}")
    
    print(f"\nStarting experiment...\n")
    
    # Run all three sessions
    all_stats = {}
    for session_name, seed in seeds.items():
        stats = await run_session(session_name, seed, args.rounds)
        all_stats[session_name] = stats
    
    # Final summary
    print(f"\n{'='*60}")
    print("EXPERIMENT COMPLETE")
    print(f"{'='*60}")
    print(f"Total rounds executed: {sum(s['session']['total_rounds'] for s in all_stats.values())}")
    print(f"\nOutput files:")
    for session in seeds.keys():
        print(f"  - selection_history_{session}.jsonl")
    print(f"\nAll outputs contain seed field for reproducibility.")
    print(f"\nAnalyze results with:")
    print(f"  python scripts/analyze_selection.py")
    
    return 0


if __name__ == '__main__':
    exit_code = asyncio.run(main())
    exit(exit_code)