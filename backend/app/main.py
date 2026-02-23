"""
Red Set ProtoCell - Main Entry Point

Autonomous, evolutionary AI red teaming system for LLM safety testing.

This is a defense-only system with:
- No real malware generation
- No real-world exploit payloads
- Zero-Retention Policy enabled by default

PRODUCTION DEPLOYMENT:
=====================

This file is in the correct shape for production. Treat it as sacred ground.
Do NOT add business logic here post-release.

Architecture:
- Main.py is WIRING ONLY (dependency injection and orchestration)
- Business logic lives in agents, engines, and core modules
- Configuration comes from config.py (single source of truth)
- Security primitives come from security.py

Sacred Ground Rules:
1. NO business logic in this file (only system setup and wiring)
2. NO direct API calls or I/O operations
3. NO conditional logic based on runtime state
4. ONLY initialization, coordination, and cleanup

What Lives Here:
[OK] System component initialization
[OK] Dependency injection and wiring
[OK] Configuration loading and validation
[OK] Lifecycle management (startup/shutdown)
[OK] High-level coordination (orchestrator.run_session)
[OK] Logging and monitoring setup

What Does NOT Live Here:
✗ Scoring algorithms
✗ Mutation strategies
✗ Prompt generation logic
✗ API client implementations
✗ Database queries
✗ Business rules or policies

Pre-Release Verification:
[OK] No business logic present
[OK] Only wiring and initialization
[OK] Startup/shutdown hooks properly manage resources
[OK] Configuration loaded from config.py
[OK] Logging configured but no debug data leaked
[OK] Error handling delegates to appropriate modules

Post-Release Maintenance:
- Update dependencies and versions
- Add new component initialization (if new agents/engines added)
- Improve error messages and logging
- DO NOT add conditional logic or business rules
"""

import argparse
import asyncio
import logging
import sys
from typing import Optional

from app.agents.orchestrator import Orchestrator, StateManager
from app.agents.sniper import Sniper
from app.agents.spotter import Spotter
from app.agents.target import create_target
from app.core.config import RSPConfig, get_default_config
from app.core.egg import EthicalGuardrailGovernor
from app.engines.mutation import MutationEngine
from app.engines.scoring import ScoringEngine
from app.engines.selection import SelectionStrategy

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler("rsp.log")],
)

logger = logging.getLogger(__name__)


def setup_system(config: RSPConfig, model_version_override: Optional[str] = None) -> Orchestrator:
    """
    Setup and initialize the RSP system.

    Args:
        config: RSP configuration
        model_version_override: Optional override for model version tracking

    Returns:
        Configured Orchestrator instance
    """
    logger.info("Initializing Red Set ProtoCell system...")

    # Initialize Ethical Guardrail Governor (EGG)
    egg = EthicalGuardrailGovernor(
        enabled=config.egg.enabled,
        log_fingerprints=config.egg.log_blocked_fingerprints,
        block_csam=config.egg.block_csam,
        block_bioweapons=config.egg.block_bioweapons,
        block_real_exploits=config.egg.block_real_exploits,
        block_real_hacking=config.egg.block_real_hacking,
    )
    logger.info("[OK] EGG initialized")

    # Initialize Scoring Engine
    scoring_engine = ScoringEngine(
        l1_weight=config.scoring.l1_weight,
        l2_weight=config.scoring.l2_weight,
        l3_weight=config.scoring.l3_weight,
    )
    logger.info("[OK] Scoring Engine initialized")

    # Initialize Mutation Engine
    mutation_engine = MutationEngine(mutation_rate=config.sniper.mutation_rate)
    logger.info("[OK] Mutation Engine initialized")

    # Initialize Selection Engine if enabled
    selection_engine = None
    selection_strategy_enum = None
    if config.sniper.use_selection_engine:
        from app.engines.selection import SelectionEngine

        selection_engine = SelectionEngine(
            decay_rate=config.sniper.decay_rate,
            decay_interval=config.sniper.decay_interval,
            novelty_weight=config.sniper.novelty_weight,
            diversity_weight=config.sniper.diversity_weight,
            overfitting_threshold=config.sniper.overfitting_threshold,
            tournament_size=config.sniper.tournament_size,
            elite_fraction=config.sniper.elite_fraction,
        )

        # Map string to enum
        strategy_map = {
            "elitism": SelectionStrategy.ELITISM,
            "tournament": SelectionStrategy.TOURNAMENT,
            "diversity_preservation": SelectionStrategy.DIVERSITY_PRESERVATION,
            "novelty_search": SelectionStrategy.NOVELTY_SEARCH,
            "hybrid": SelectionStrategy.HYBRID,
        }
        selection_strategy_enum = strategy_map.get(config.sniper.selection_strategy.lower(), SelectionStrategy.HYBRID)
        logger.info(f"[OK] Selection Engine initialized (strategy: {config.sniper.selection_strategy})")
    else:
        selection_strategy_enum = SelectionStrategy.HYBRID

    # Initialize Sniper Agent
    sniper = Sniper(
        mutation_engine=mutation_engine,
        evolution_pool_size=config.sniper.evolution_pool_size,
        creativity_temperature=config.sniper.creativity_temperature,
        selection_engine=selection_engine,
        selection_strategy=selection_strategy_enum,
        domain_selection_temperature=config.sniper.domain_selection_temperature,
        api_key=config.sniper.api_key,
    )
    logger.info("[OK] Sniper Agent initialized")

    # Initialize Target Agent
    backend_value = config.target.backend.value if hasattr(config.target.backend, "value") else config.target.backend

    target = create_target(
        backend_type=str(backend_value),
        api_key=config.target.api_key,
        model_name=config.target.model_name,
        max_tokens=config.target.max_tokens,
        temperature=config.target.temperature,
        fresh_context=config.target.fresh_context,
    )
    logger.info(f"[OK] Target Agent initialized ({backend_value})")

    # Initialize Spotter Agent
    spotter = Spotter(
        confidence_threshold=config.spotter.confidence_threshold,
        use_auxiliary_classifiers=config.spotter.use_auxiliary_classifiers,
        api_key=config.spotter.api_key,
    )
    logger.info("[OK] Spotter Agent initialized")

    # Initialize State Manager
    model_version = model_version_override or config.target.model_name
    state_manager = StateManager(
        database_path=config.storage.database_path,
        zero_retention=config.storage.zero_retention,
        model_version=model_version,
    )
    logger.info(f"[OK] State Manager initialized (zero_retention={config.storage.zero_retention})")

    # Initialize Orchestrator
    orchestrator = Orchestrator(
        sniper=sniper,
        target=target,
        spotter=spotter,
        egg=egg,
        scoring_engine=scoring_engine,
        state_manager=state_manager,
        max_rounds=config.orchestrator.max_rounds,
        round_timeout=config.orchestrator.round_timeout_seconds,
        concurrent_rounds=config.orchestrator.concurrent_rounds,
        config=config,
        artifacts_dir="runs",
    )
    logger.info("[OK] Orchestrator initialized")

    logger.info("=" * 60)
    logger.info("Red Set ProtoCell system ready")
    logger.info(f"Session ID: {state_manager.session_id}")
    logger.info(f"Max Rounds: {config.orchestrator.max_rounds}")
    logger.info(f"Zero Retention: {config.storage.zero_retention}")
    logger.info("=" * 60)

    return orchestrator


async def main(config: RSPConfig, model_version_override: Optional[str] = None):
    """
    Main execution function.

    Args:
        config: RSP configuration
        model_version_override: Optional override for model version tracking
    """
    logger.info("Starting Red Set ProtoCell...")

    # Setup system
    orchestrator = setup_system(config, model_version_override)

    try:
        # Run session
        logger.info("Beginning red teaming session...")
        stats = await orchestrator.run_session()

        # Display results
        logger.info("=" * 60)
        logger.info("SESSION COMPLETED")
        logger.info("=" * 60)
        logger.info(f"Total Rounds: {stats['session']['total_rounds']}")
        logger.info(f"Model Version: {stats['session']['model_version']}")
        logger.info(f"Average Score: {stats['scores']['average_global_score']:.3f}")
        logger.info(f"Blocked by EGG: {stats['scores']['total_blocked']}")

        # Display time analytics if available
        if "time_analytics" in stats:
            logger.info("")
            logger.info("Time Analytics:")
            fatigue = stats["time_analytics"]["fatigue"]
            drift = stats["time_analytics"]["drift"]
            logger.info(f"  Fatigue Detected: {fatigue['is_fatigued']}")
            if fatigue["is_fatigued"]:
                logger.info(f"  Fatigue Score: {fatigue['fatigue_score']:.3f}")
                logger.info(f"  Degradation Rate: {fatigue['degradation_rate']:.4f} per round")
            logger.info(f"  Score Drift: {drift['drift_direction']}")
            logger.info(f"  Trend Slope: {drift['trend_slope']:+.4f}")

        logger.info("")
        logger.info("Agent Statistics:")
        logger.info(f"  Sniper: {stats['agents']['sniper']['total_generated']} prompts generated")
        logger.info(f"  Target: {stats['agents']['target']['total_executions']} executions")
        logger.info(f"  Spotter: {stats['agents']['spotter']['total_evaluations']} evaluations")
        logger.info(f"  EGG: {stats['agents']['egg']['total_blocked']} blocked")
        logger.info("")
        logger.info("Mutation Statistics:")
        logger.info(f"  Total: {stats['mutation']['total_mutations']}")
        logger.info("=" * 60)

    except KeyboardInterrupt:
        logger.info("\nSession interrupted by user")
        orchestrator.terminate_session()
    except Exception as e:
        logger.error(f"Session failed: {e}", exc_info=True)
    finally:
        # Cleanup (Zero-Retention Policy)
        if config.storage.zero_retention:
            logger.info("Executing Zero-Retention cleanup...")
            orchestrator.cleanup()
            logger.info("[OK] All session data destroyed")


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Red Set ProtoCell - AI Red Teaming System")

    parser.add_argument(
        "--rounds",
        type=int,
        default=100,
        help="Maximum number of rounds to execute (default: 100)",
    )

    parser.add_argument(
        "--backend",
        type=str,
        choices=["openai", "anthropic", "openrouter", "llama_cpp", "custom_http"],
        required=True,
        help="Target backend to use (required: openai, anthropic, openrouter, llama_cpp, or custom_http)",
    )

    parser.add_argument(
        "--api-key",
        type=str,
        required=True,
        help="API key for target backend (required)",
    )

    parser.add_argument("--model", type=str, help="Model name for target backend")

    parser.add_argument(
        "--no-zero-retention",
        action="store_true",
        help="Disable zero-retention policy (keep session data)",
    )

    parser.add_argument(
        "--db-path",
        type=str,
        default="rsp_session.db",
        help="Database path (default: rsp_session.db)",
    )

    parser.add_argument(
        "--model-version",
        type=str,
        help="Model version identifier for tracking (optional, defaults to model name)",
    )

    return parser.parse_args()


if __name__ == "__main__":
    # Display banner
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║         RED SET PROTOCELL (RSP)                           ║
    ║         Autonomous AI Red Teaming System                  ║
    ║                                                           ║
    ║         Defense-Only | Zero-Retention | Ethical           ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)

    # Parse arguments
    args = parse_arguments()

    # Create configuration
    config = get_default_config()
    config.orchestrator.max_rounds = args.rounds
    config.target.backend = args.backend
    config.storage.zero_retention = not args.no_zero_retention
    config.storage.database_path = args.db_path

    if args.api_key:
        config.target.api_key = args.api_key

    if args.model:
        config.target.model_name = args.model

    # Run main with model_version override if provided
    try:
        asyncio.run(main(config, model_version_override=args.model_version))
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
