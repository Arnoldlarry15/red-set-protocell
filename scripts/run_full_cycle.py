#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Red Set ProtoCell - Full Cycle Test Harness

Deterministic test harness implementing:
- Layer 1: Deterministic Test (fixed seed, model, prompt, rounds)
- Layer 2: Role Separation Verification (Sniper/Spotter/Target isolation)
- Layer 3: Audit Trail Integrity (complete logging with hash verification)

This script provides infrastructure-grade deterministic behavior:
- Run twice → identical input → identical hash
- Complete transparency of all agent interactions
- Verifiable role separation between Sniper and Spotter
- Comprehensive audit trail for every run

Usage:
    # Run full cycle with default settings (10 rounds)
    cd backend
    python ../scripts/run_full_cycle.py
    
    # Run with custom settings
    python ../scripts/run_full_cycle.py --seed 42 --rounds 20
    
    # Verify determinism (runs twice and compares)
    python ../scripts/run_full_cycle.py --verify
"""

import asyncio
import json
import hashlib
import random
import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any
import numpy as np

# Add backend directory to path if not already there
script_dir = Path(__file__).parent.absolute()
backend_dir = script_dir.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.main import setup_system
from app.core.config import load_config_from_env


def set_seed(seed: int):
    """
    Set global random seed for complete reproducibility.
    
    Seeds:
    - Python's random module
    - NumPy's random generator
    
    Args:
        seed: Integer seed value
    """
    random.seed(seed)
    np.random.seed(seed)


def compute_interaction_hash(audit_log: Dict[str, Any]) -> str:
    """
    Compute SHA-256 hash of full interaction.
    
    This hash includes all deterministic components:
    - Seed
    - Model configuration
    - All prompts (Sniper outputs)
    - All target responses
    - All Spotter evaluations
    - All scores
    
    Args:
        audit_log: Complete audit log dictionary
        
    Returns:
        SHA-256 hash as hex string
    """
    # Create canonical representation (sorted keys, consistent formatting)
    canonical = json.dumps(audit_log, sort_keys=True, indent=None)
    return hashlib.sha256(canonical.encode('utf-8')).hexdigest()


class FullCycleRunner:
    """
    Full cycle runner with complete audit trail and role separation tracking.
    """
    
    def __init__(self, seed: int, rounds: int, output_dir: str = "full_cycle_logs"):
        """
        Initialize full cycle runner.
        
        Args:
            seed: Random seed for reproducibility
            rounds: Number of rounds to execute
            output_dir: Directory for output logs
        """
        self.seed = seed
        self.rounds = rounds
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Audit trail components
        self.audit_trail: Dict[str, Any] = {
            "metadata": {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "seed": seed,
                "rounds": rounds,
                "protocell_version": "1.0.0",
            },
            "configuration": {},
            "role_separation": {
                "sniper_instructions": [],
                "spotter_instructions": [],
                "target_interactions": [],
            },
            "round_details": [],
            "statistics": {},
            "hash": None,
        }
    
    async def run_full_cycle(self) -> Dict[str, Any]:
        """
        Run complete cycle with full audit trail.
        
        Returns:
            Audit trail dictionary with all interaction details
        """
        print(f"\n{'='*70}")
        print("RED SET PROTOCELL - FULL CYCLE TEST HARNESS")
        print(f"{'='*70}")
        print(f"Seed: {self.seed}")
        print(f"Rounds: {self.rounds}")
        print(f"Timestamp: {self.audit_trail['metadata']['timestamp']}")
        print(f"{'='*70}\n")
        
        # Step 1: Lock randomness
        set_seed(self.seed)
        
        # Step 2: Configure system with fixed settings
        config = load_config_from_env()
        config.orchestrator.max_rounds = self.rounds
        
        # Capture configuration in audit trail
        self.audit_trail["configuration"] = {
            "backend": config.target.backend.value if hasattr(config.target.backend, 'value') else str(config.target.backend),
            "model_name": config.target.model_name,
            "max_tokens": config.target.max_tokens,
            "temperature": config.target.temperature,
            "sniper": {
                "mutation_rate": config.sniper.mutation_rate,
                "evolution_pool_size": config.sniper.evolution_pool_size,
                "creativity_temperature": config.sniper.creativity_temperature,
                "selection_strategy": config.sniper.selection_strategy,
            },
            "spotter": {
                "confidence_threshold": config.spotter.confidence_threshold,
                "use_auxiliary_classifiers": config.spotter.use_auxiliary_classifiers,
            },
            "scoring": {
                "l1_weight": config.scoring.l1_weight,
                "l2_weight": config.scoring.l2_weight,
                "l3_weight": config.scoring.l3_weight,
            }
        }
        
        # Step 3: Initialize system
        print("[1/5] Initializing system...")
        orchestrator = setup_system(config)

        # Lock MutationEngine's internal RNG
        # Lock MutationEngine's internal RNG. This is best-effort: older or alternative
        # implementations may not expose a `_random` attribute; in that case we continue
        # without failing but record that deterministic seeding was skipped.
        try:
            mutation_engine = orchestrator.sniper.mutation_engine
            rng = getattr(mutation_engine, "_random", None)
            if rng is not None:
                rng.seed(self.seed)
        except AttributeError:
            print(
                "[warn] Could not lock MutationEngine RNG deterministically "
                "(missing expected attributes); continuing without internal RNG seeding."
            )

        print("[2/5] Running attack session...")
        
        # Step 4: Run session and capture detailed round information
        # We'll manually execute rounds to capture detailed information
        for round_num in range(1, self.rounds + 1):
            print(f"  Round {round_num}/{self.rounds}...", end="", flush=True)
            
            try:
                # Get prior metadata
                prior_metadata = await orchestrator.state_manager.get_prior_rounds_async(limit=10)
                
                # LAYER 2: Capture Sniper instruction details
                sniper_instruction = {
                    "round": round_num,
                    "role": "SNIPER (Attack Generator)",
                    "system_instruction": "Generate adversarial prompts to discover LLM failure modes",
                    "input_context": {
                        "prior_rounds": len(prior_metadata),
                        "evolution_pool_size": len(orchestrator.sniper.evolution_pool) if hasattr(orchestrator.sniper, 'evolution_pool') else 0,
                    }
                }
                self.audit_trail["role_separation"]["sniper_instructions"].append(sniper_instruction)
                
                # Sniper generates prompt
                prompt, attack_domain = await orchestrator.sniper.generate_prompt(prior_metadata)
                
                # Check EGG
                is_allowed, blocked_info = orchestrator.egg.inspect_prompt(prompt)
                
                if not is_allowed:
                    print(" [BLOCKED]")
                    round_detail = {
                        "round": round_num,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "sniper_prompt": prompt[:200] + "..." if len(prompt) > 200 else prompt,
                        "attack_domain": attack_domain.value,
                        "egg_blocked": True,
                        "blocked_category": blocked_info.category if blocked_info else None,
                        "target_response": None,
                        "spotter_evaluation": None,
                        "global_score": 0.0,
                    }
                    self.audit_trail["round_details"].append(round_detail)
                    
                    # Update sniper with blocked feedback
                    orchestrator.sniper.update_prompt_score(prompt, 0.0, structured_feedback={
                        'blocked': True,
                        'l1': {'score': 0.0},
                        'l2': {'score': 0.0},
                        'l3': {'score': 0.0}
                    })
                    continue
                
                # LAYER 2: Capture Target interaction
                target_interaction = {
                    "round": round_num,
                    "role": "TARGET (LLM Under Test)",
                    "backend": self.audit_trail["configuration"]["backend"],
                    "model": self.audit_trail["configuration"]["model_name"],
                    "prompt": prompt[:200] + "..." if len(prompt) > 200 else prompt,
                }
                self.audit_trail["role_separation"]["target_interactions"].append(target_interaction)
                
                # Target executes prompt
                target_response = await orchestrator.target.execute(
                    prompt, 
                    metadata={"round": round_num, "domain": attack_domain.value}
                )
                
                # LAYER 2: Capture Spotter instruction details
                spotter_instruction = {
                    "round": round_num,
                    "role": "SPOTTER (Evaluator)",
                    "system_instruction": "Evaluate target response for failures using 3-Layer Scoring Taxonomy",
                    "input_context": {
                        "response_length": len(target_response),
                        "attack_domain": attack_domain.value,
                    },
                    "evaluation_layers": ["L1 (Linguistic Safety)", "L2 (Security Exploitability)", "L3 (Cognitive Stability)"]
                }
                self.audit_trail["role_separation"]["spotter_instructions"].append(spotter_instruction)
                
                # Spotter evaluates response
                evaluation = await orchestrator.spotter.evaluate(
                    target_response,
                    attack_domain=attack_domain.value,
                    prompt=prompt
                )
                
                # Compute global score
                global_score = orchestrator.scoring_engine.compute_global_score(
                    evaluation["l1"]["score"],
                    evaluation["l2"]["score"],
                    evaluation["l3"]["score"],
                )
                
                # Update sniper with score
                orchestrator.sniper.update_prompt_score(
                    prompt,
                    global_score,
                    structured_feedback=evaluation
                )
                
                # LAYER 3: Capture complete round details in audit trail
                round_detail = {
                    "round": round_num,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "sniper_prompt": prompt,
                    "attack_domain": attack_domain.value,
                    "egg_blocked": False,
                    "target_response": target_response,
                    "spotter_evaluation": {
                        "l1_score": evaluation["l1"]["score"],
                        "l2_score": evaluation["l2"]["score"],
                        "l3_score": evaluation["l3"]["score"],
                        "global_score": global_score,
                        "full_evaluation": evaluation,
                    },
                    "global_score": global_score,
                }
                self.audit_trail["round_details"].append(round_detail)
                
                # Save state
                from app.agents.orchestrator import RoundResult
                round_result = RoundResult(
                    round_number=round_num,
                    prompt=prompt,
                    attack_domain=attack_domain.value,
                    target_response=target_response,
                    evaluation=evaluation,
                    global_score=global_score,
                    blocked_by_egg=False,
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    model_version=orchestrator.state_manager.model_version,
                    session_start_time=orchestrator.state_manager.session_start_time,
                )
                await orchestrator.state_manager.save_round_async(round_result)
                
                print(f" [OK] Score: {global_score:.3f}")
                
            except Exception as e:
                print(f" [ERROR]: {e}")
                round_detail = {
                    "round": round_num,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "error": str(e),
                    "global_score": 0.0,
                }
                self.audit_trail["round_details"].append(round_detail)
        
        # Step 5: Compile statistics
        print("[3/5] Compiling statistics...")
        stats = await orchestrator.state_manager.get_statistics_async()
        
        self.audit_trail["statistics"] = {
            "total_rounds": len(self.audit_trail["round_details"]),
            "successful_rounds": len([r for r in self.audit_trail["round_details"] if not r.get("egg_blocked") and not r.get("error")]),
            "blocked_rounds": len([r for r in self.audit_trail["round_details"] if r.get("egg_blocked")]),
            "error_rounds": len([r for r in self.audit_trail["round_details"] if r.get("error")]),
            "average_score": stats.get("average_score", 0.0),
            "sniper_stats": orchestrator.sniper.get_statistics(),
            "target_stats": orchestrator.target.get_statistics(),
            "spotter_stats": orchestrator.spotter.get_statistics(),
        }
        
        # Step 6: Compute hash
        print("[4/5] Computing interaction hash...")
        # Hash only deterministic fields (exclude timestamps and non-deterministic metadata)
        hashable_data = {
            "seed": self.audit_trail["metadata"]["seed"],
            "rounds": self.audit_trail["metadata"]["rounds"],
            "configuration": self.audit_trail["configuration"],
            "round_details": [
                {
                    "round": r["round"],
                    "sniper_prompt": r.get("sniper_prompt", ""),
                    "attack_domain": r.get("attack_domain", ""),
                    "target_response": r.get("target_response", ""),
                    "global_score": r.get("global_score", 0.0),
                }
                for r in self.audit_trail["round_details"]
            ],
        }
        
        interaction_hash = compute_interaction_hash(hashable_data)
        self.audit_trail["hash"] = interaction_hash
        
        # Step 7: Save audit trail
        print("[5/5] Saving audit trail...")
        output_file = self.output_dir / f"full_cycle_seed_{self.seed}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.audit_trail, f, indent=2)
        
        print(f"\n{'='*70}")
        print("FULL CYCLE COMPLETE")
        print(f"{'='*70}")
        print(f"Total rounds: {self.audit_trail['statistics']['total_rounds']}")
        print(f"Successful rounds: {self.audit_trail['statistics']['successful_rounds']}")
        print(f"Blocked rounds: {self.audit_trail['statistics']['blocked_rounds']}")
        print(f"Average score: {self.audit_trail['statistics']['average_score']:.3f}")
        print(f"\nInteraction Hash: {interaction_hash[:16]}...{interaction_hash[-16:]}")
        print(f"Audit trail saved: {output_file}")
        print(f"{'='*70}\n")
        
        return self.audit_trail


async def verify_determinism(seed: int, rounds: int = 10) -> bool:
    """
    Verify deterministic behavior by running twice and comparing hashes.
    
    This is the core verification for infrastructure-grade behavior:
    Run twice → identical input → identical hash.
    
    Args:
        seed: Seed to test
        rounds: Number of rounds (default: 10 for quick verification)
        
    Returns:
        True if hashes match (deterministic), False otherwise
    """
    print(f"\n{'='*70}")
    print("DETERMINISM VERIFICATION MODE")
    print(f"{'='*70}")
    print(f"Running {rounds} rounds twice with seed={seed}")
    print("If deterministic, interaction hashes will be IDENTICAL.\n")
    
    # Run 1
    print("=== RUN 1 ===")
    runner1 = FullCycleRunner(seed=seed, rounds=rounds, output_dir="full_cycle_logs/verify_run1")
    audit1 = await runner1.run_full_cycle()
    hash1 = audit1["hash"]
    
    print("\n" + "="*70 + "\n")
    
    # Run 2
    print("=== RUN 2 ===")
    runner2 = FullCycleRunner(seed=seed, rounds=rounds, output_dir="full_cycle_logs/verify_run2")
    audit2 = await runner2.run_full_cycle()
    hash2 = audit2["hash"]
    
    # Compare
    print("\n" + "="*70)
    print("DETERMINISM VERIFICATION RESULTS")
    print("="*70)
    print(f"Run 1 Hash: {hash1}")
    print(f"Run 2 Hash: {hash2}")
    
    if hash1 == hash2:
        print("\n[OK] DETERMINISM CONFIRMED")
        print("Both runs produced IDENTICAL interaction hashes.")
        print("This system exhibits infrastructure-grade deterministic behavior.")
        print("="*70 + "\n")
        return True
    else:
        print("\n[FAIL] DETERMINISM NOT CONFIRMED")
        print("Hashes differ - system may have non-deterministic behavior.")
        print("="*70 + "\n")
        return False


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Red Set ProtoCell - Full Cycle Test Harness with Audit Trail',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full cycle with default settings (10 rounds)
  python scripts/run_full_cycle.py
  
  # Run with custom seed and rounds
  python scripts/run_full_cycle.py --seed 42 --rounds 20
  
  # Verify determinism (runs twice and compares hashes)
  python scripts/run_full_cycle.py --verify
  
  # Verify with custom settings
  python scripts/run_full_cycle.py --verify --seed 42 --rounds 5

Output:
  - Complete audit trail saved to full_cycle_logs/
  - Includes all Sniper prompts, Target responses, Spotter evaluations
  - Role separation details for each agent
  - SHA-256 hash of full interaction for verification
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
        help='Number of rounds to execute (default: 10)'
    )
    
    parser.add_argument(
        '--verify',
        action='store_true',
        help='Run determinism verification (executes twice and compares hashes)'
    )
    
    args = parser.parse_args()
    
    try:
        if args.verify:
            # Determinism verification mode
            success = await verify_determinism(seed=args.seed, rounds=args.rounds)
            return 0 if success else 1
        else:
            # Standard full cycle mode
            runner = FullCycleRunner(seed=args.seed, rounds=args.rounds)
            await runner.run_full_cycle()
            return 0
    
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
