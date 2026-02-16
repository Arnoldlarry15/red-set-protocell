#!/usr/bin/env python3
"""
Red Set ProtoCell - Determinism Verification Script

Runs multiple iterations with the same seed and verifies that:
1. All interaction hashes are identical
2. All scores are identical
3. All round details match exactly

This demonstrates infrastructure-grade deterministic behavior:
    Run N times → same seed → identical hashes

Usage:
    # Run 20 iterations with default settings
    python scripts/verify_determinism.py
    
    # Run with custom iterations and seed
    python scripts/verify_determinism.py --iterations 30 --seed 15
    
    # Quick test (5 iterations, 5 rounds each)
    python scripts/verify_determinism.py --iterations 5 --rounds 5
"""

import asyncio
import argparse
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Add backend directory to path if not already there
script_dir = Path(__file__).parent.absolute()
backend_dir = script_dir.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Import the FullCycleRunner from run_full_cycle
# First import run_full_cycle to make sure it's available
scripts_dir = script_dir
if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))

from run_full_cycle import FullCycleRunner


class DeterminismVerifier:
    """
    Verifies deterministic behavior across multiple runs.
    """
    
    def __init__(self, seed: int, rounds: int, iterations: int):
        """
        Initialize determinism verifier.
        
        Args:
            seed: Random seed to use for all runs
            rounds: Number of rounds per run
            iterations: Number of runs to perform
        """
        self.seed = seed
        self.rounds = rounds
        self.iterations = iterations
        self.results: List[Dict[str, Any]] = []
    
    async def run_verification(self) -> bool:
        """
        Run verification across multiple iterations.
        
        Returns:
            True if all hashes match, False otherwise
        """
        print(f"\n{'='*70}")
        print("RED SET PROTOCELL - DETERMINISM VERIFICATION")
        print(f"{'='*70}")
        print(f"Seed: {self.seed}")
        print(f"Rounds per iteration: {self.rounds}")
        print(f"Total iterations: {self.iterations}")
        print(f"Started: {datetime.utcnow().isoformat()}")
        print(f"{'='*70}\n")
        
        print(f"Running {self.iterations} iterations...\n")
        
        hashes = []
        
        for i in range(1, self.iterations + 1):
            print(f"[Iteration {i}/{self.iterations}]")
            
            # Create runner with unique output directory
            output_dir = f"full_cycle_logs/determinism_verify/iteration_{i}"
            runner = FullCycleRunner(seed=self.seed, rounds=self.rounds, output_dir=output_dir)
            
            # Run full cycle
            audit = await runner.run_full_cycle()
            
            # Extract key data
            result = {
                "iteration": i,
                "hash": audit["hash"],
                "total_rounds": audit["statistics"]["total_rounds"],
                "successful_rounds": audit["statistics"]["successful_rounds"],
                "blocked_rounds": audit["statistics"]["blocked_rounds"],
                "average_score": audit["statistics"]["average_score"],
                "round_scores": [r.get("global_score", 0.0) for r in audit["round_details"]],
            }
            
            self.results.append(result)
            hashes.append(audit["hash"])
            
            print(f"  Hash: {audit['hash'][:16]}...{audit['hash'][-16:]}")
            print(f"  Score: {audit['statistics']['average_score']:.3f}")
            print()
        
        # Verification Analysis
        print(f"\n{'='*70}")
        print("DETERMINISM VERIFICATION ANALYSIS")
        print(f"{'='*70}\n")
        
        # Check hash consistency
        unique_hashes = set(hashes)
        
        print(f"Total iterations: {self.iterations}")
        print(f"Unique hashes: {len(unique_hashes)}")
        
        if len(unique_hashes) == 1:
            print(f"\n[OK] ALL HASHES IDENTICAL")
            print(f"Hash: {hashes[0]}")
            print(f"\nDeterminism confirmed across {self.iterations} iterations.")
            success = True
        else:
            print(f"\n[FAIL] HASHES DIFFER")
            print(f"\nHash distribution:")
            for i, h in enumerate(hashes):
                print(f"  Iteration {i+1}: {h[:32]}...")
            success = False
        
        # Check score consistency
        print(f"\n{'='*70}")
        print("SCORE CONSISTENCY CHECK")
        print(f"{'='*70}\n")
        
        scores = [r["average_score"] for r in self.results]
        unique_scores = set(scores)
        
        if len(unique_scores) == 1:
            print(f"[OK] ALL SCORES IDENTICAL: {scores[0]:.6f}")
        else:
            print(f"[WARN] SCORES VARY")
            print(f"Score range: {min(scores):.6f} to {max(scores):.6f}")
            for i, s in enumerate(scores):
                print(f"  Iteration {i+1}: {s:.6f}")
        
        # Check round-by-round consistency
        print(f"\n{'='*70}")
        print("ROUND-BY-ROUND CONSISTENCY")
        print(f"{'='*70}\n")
        
        round_scores_consistent = True
        for round_idx in range(self.rounds):
            round_scores = [r["round_scores"][round_idx] if round_idx < len(r["round_scores"]) else None 
                          for r in self.results]
            unique_round_scores = set([s for s in round_scores if s is not None])
            
            if len(unique_round_scores) == 1:
                print(f"  Round {round_idx + 1}: [OK] Identical ({list(unique_round_scores)[0]:.3f})")
            else:
                print(f"  Round {round_idx + 1}: [FAIL] Varies: {unique_round_scores}")
                round_scores_consistent = False
        
        # Final verdict
        print(f"\n{'='*70}")
        print("FINAL VERDICT")
        print(f"{'='*70}\n")
        
        if success and len(unique_scores) == 1 and round_scores_consistent:
            print("[OK] SYSTEM IS DETERMINISTIC")
            print("\nAll iterations produced:")
            print("  - Identical interaction hashes")
            print("  - Identical average scores")
            print("  - Identical round-by-round scores")
            print("\nThis system exhibits infrastructure-grade deterministic behavior.")
        elif success:
            print("[PARTIAL] HASHES MATCH BUT SCORES VARY")
            print("\nInteraction hashes are identical, but scores show variation.")
            print("This may indicate non-deterministic scoring logic.")
        else:
            print("[FAIL] SYSTEM IS NOT DETERMINISTIC")
            print("\nDifferent iterations produced different results.")
            print("This system does not exhibit deterministic behavior.")
        
        print(f"{'='*70}\n")
        
        return success and len(unique_scores) == 1 and round_scores_consistent


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Red Set ProtoCell - Determinism Verification (Multiple Iterations)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run 20 iterations with default settings
  python scripts/verify_determinism.py
  
  # Run 30 iterations with custom seed
  python scripts/verify_determinism.py --iterations 30 --seed 15
  
  # Quick test (5 iterations, 5 rounds each)
  python scripts/verify_determinism.py --iterations 5 --rounds 5

Output:
  - Detailed comparison of all iterations
  - Hash consistency verification
  - Score consistency verification
  - Round-by-round comparison
  - Final determinism verdict
        """
    )
    
    parser.add_argument(
        '--seed',
        type=int,
        default=42,
        help='Random seed for reproducibility (default: 42)'
    )
    
    parser.add_argument(
        '--rounds',
        type=int,
        default=10,
        help='Number of rounds per iteration (default: 10)'
    )
    
    parser.add_argument(
        '--iterations',
        type=int,
        default=20,
        help='Number of iterations to run (default: 20)'
    )
    
    args = parser.parse_args()
    
    try:
        verifier = DeterminismVerifier(
            seed=args.seed,
            rounds=args.rounds,
            iterations=args.iterations
        )
        
        success = await verifier.run_verification()
        
        return 0 if success else 1
    
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
        return 130
    
    except Exception as e:
        print(f"\n\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
