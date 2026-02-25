#!/usr/bin/env python3
"""
Red Set ProtoCell - Verification Mode

A mode that:
- Locks seed
- Locks iteration count
- Dumps full trace to file
- Asserts identical output hash between runs

If hashes differ under deterministic mode, something is wrong.
This turns Red Set into its own auditor.

Usage:
    python scripts/verification_mode.py --seed 42 --rounds 10
    python scripts/verification_mode.py --seed 42 --rounds 10 --iterations 3
"""

import asyncio
import json
import argparse
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List

# Add backend directory to path
script_dir = Path(__file__).parent.absolute()
backend_dir = script_dir.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Import verification dependencies
scripts_dir = script_dir
if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))

from run_full_cycle import FullCycleRunner


class VerificationMode:
    """
    Verification mode that runs multiple iterations with locked seed
    and verifies identical outputs.
    """

    def __init__(self, seed: int, rounds: int, iterations: int = 2):
        """
        Initialize verification mode.

        Args:
            seed: Locked random seed
            rounds: Locked iteration count
            iterations: Number of verification runs (default: 2)
        """
        self.seed = seed
        self.rounds = rounds
        self.iterations = iterations
        self.verification_results: List[Dict[str, Any]] = []

    async def run_verification(self) -> bool:
        """
        Run verification iterations and check for determinism.

        Returns:
            True if all iterations produce identical hashes, False otherwise
        """
        print(f"\n{'='*70}")
        print("RED SET PROTOCELL - VERIFICATION MODE")
        print(f"{'='*70}")
        print(f"Locked Seed: {self.seed}")
        print(f"Locked Rounds: {self.rounds}")
        print(f"Verification Iterations: {self.iterations}")
        print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
        print(f"{'='*70}\n")

        print("VERIFICATION PROTOCOL:")
        print("1. Lock seed and iteration count")
        print("2. Run multiple iterations with identical configuration")
        print("3. Dump full trace to file for each iteration")
        print("4. Compute SHA-256 hash of each trace")
        print("5. Assert all hashes are identical")
        print(f"\nRunning {self.iterations} iterations...\n")

        hashes = []
        traces = []

        for iteration in range(1, self.iterations + 1):
            print(f"[Iteration {iteration}/{self.iterations}]")

            # Create runner with unique output directory
            output_dir = f"verification_logs/seed_{self.seed}/iteration_{iteration}"
            runner = FullCycleRunner(
                seed=self.seed, rounds=self.rounds, output_dir=output_dir
            )

            # Run full cycle
            try:
                audit = await runner.run_full_cycle()

                # Extract hash and trace
                iteration_hash = audit["hash"]
                hashes.append(iteration_hash)
                traces.append(audit)

                # Save trace to file
                trace_file = Path(output_dir) / f"trace_iteration_{iteration}.json"
                with open(trace_file, "w", encoding="utf-8") as f:
                    json.dump(audit, f, indent=2)

                print(f"  Hash: {iteration_hash}")
                print(f"  Trace: {trace_file}")
                print(
                    f"  Status: {'✓' if len(set(hashes)) == 1 else '✗ HASH MISMATCH'}\n"
                )

                self.verification_results.append(
                    {
                        "iteration": iteration,
                        "hash": iteration_hash,
                        "trace_file": str(trace_file),
                        "statistics": audit["statistics"],
                    }
                )

            except Exception as e:
                print(f"  ERROR: {e}\n")
                return False

        # Verification: Check if all hashes are identical
        unique_hashes = set(hashes)

        print(f"\n{'='*70}")
        print("VERIFICATION RESULTS")
        print(f"{'='*70}")
        print(f"Total Iterations: {len(hashes)}")
        print(f"Unique Hashes: {len(unique_hashes)}")

        if len(unique_hashes) == 1:
            print(f"Result: ✓ PASS - All hashes identical")
            print(f"Hash: {hashes[0]}")
            print(f"\nDeterministic behavior confirmed.")
            print(
                f"Seed {self.seed} produces identical outputs across {self.iterations} runs."
            )
            verification_passed = True
        else:
            print(f"Result: ✗ FAIL - Hash mismatch detected")
            print(f"\nUnique hashes found:")
            for i, h in enumerate(unique_hashes, 1):
                iterations_with_hash = [
                    idx + 1 for idx, hash_val in enumerate(hashes) if hash_val == h
                ]
                print(f"  {i}. {h} (iterations: {iterations_with_hash})")

            print(f"\n⚠️  NON-DETERMINISTIC BEHAVIOR DETECTED")
            print(f"Same seed + same configuration → different outputs")
            print(f"This indicates a bug in determinism implementation.")
            verification_passed = False

        # Save verification report
        report_file = Path(
            f"verification_logs/seed_{self.seed}/verification_report.json"
        )
        report_file.parent.mkdir(parents=True, exist_ok=True)

        report = {
            "metadata": {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "seed": self.seed,
                "rounds": self.rounds,
                "iterations": self.iterations,
            },
            "verification": {
                "passed": verification_passed,
                "total_iterations": len(hashes),
                "unique_hashes": len(unique_hashes),
                "hashes": hashes,
            },
            "iterations": self.verification_results,
        }

        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        print(f"\nVerification report saved: {report_file}")
        print(f"{'='*70}\n")

        return verification_passed


async def main():
    """Main entry point for verification mode."""
    parser = argparse.ArgumentParser(
        description="Red Set ProtoCell Verification Mode - Determinism Auditor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run 2 iterations with seed 42 and 10 rounds
  python scripts/verification_mode.py --seed 42 --rounds 10

  # Run 5 iterations for thorough verification
  python scripts/verification_mode.py --seed 42 --rounds 10 --iterations 5

  # Quick verification (3 rounds, 2 iterations)
  python scripts/verification_mode.py --seed 42 --rounds 3 --iterations 2
        """,
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Locked random seed for deterministic execution (default: 42)",
    )
    parser.add_argument(
        "--rounds",
        type=int,
        default=10,
        help="Locked number of rounds per iteration (default: 10)",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=2,
        help="Number of verification iterations to run (default: 2)",
    )

    args = parser.parse_args()

    # Run verification
    verifier = VerificationMode(
        seed=args.seed, rounds=args.rounds, iterations=args.iterations
    )

    try:
        verification_passed = await verifier.run_verification()

        if verification_passed:
            print("✓ Verification PASSED: Red Set ProtoCell is deterministic")
            sys.exit(0)
        else:
            print("✗ Verification FAILED: Non-deterministic behavior detected")
            sys.exit(1)

    except Exception as e:
        print(f"\n✗ Verification ERROR: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(2)


if __name__ == "__main__":
    asyncio.run(main())
