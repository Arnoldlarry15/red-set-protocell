"""
Red Set ProtoCell - Main Entry Point

Autonomous, evolutionary AI red teaming system for LLM safety testing.

This is a defense-only system with:
- No real malware generation
- No real-world exploit payloads
- Zero-Retention Policy enabled by default
"""

import asyncio
import argparse
import logging
import sys
from pathlib import Path

from app.core.config import RSPConfig, get_default_config
from app.core.egg import EthicalGuardrailGovernor
from app.engines.scoring import ScoringEngine
from app.engines.mutation import MutationEngine
from app.agents.sniper import Sniper
from app.agents.target import create_target
from app.agents.spotter import Spotter
from app.agents.orchestrator import Orchestrator, StateManager


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('rsp.log')
    ]
)

logger = logging.getLogger(__name__)


def setup_system(config: RSPConfig) -> Orchestrator:
    """
    Setup and initialize the RSP system.
    
    Args:
        config: RSP configuration
        
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
        block_real_exploits=config.egg.block_real_exploits
    )
    logger.info("✓ EGG initialized")
    
    # Initialize Scoring Engine
    scoring_engine = ScoringEngine(
        l1_weight=config.scoring.l1_weight,
        l2_weight=config.scoring.l2_weight,
        l3_weight=config.scoring.l3_weight
    )
    logger.info("✓ Scoring Engine initialized")
    
    # Initialize Mutation Engine
    mutation_engine = MutationEngine(
        mutation_rate=config.sniper.mutation_rate
    )
    logger.info("✓ Mutation Engine initialized")
    
    # Initialize Sniper Agent
    sniper = Sniper(
        mutation_engine=mutation_engine,
        evolution_pool_size=config.sniper.evolution_pool_size,
        creativity_temperature=config.sniper.creativity_temperature
    )
    logger.info("✓ Sniper Agent initialized")
    
    # Initialize Target Agent
    backend_value = config.target.backend.value if hasattr(config.target.backend, 'value') else config.target.backend
    target = create_target(
        backend_type=backend_value,
        api_key=config.target.api_key,
        model_name=config.target.model_name,
        max_tokens=config.target.max_tokens,
        temperature=config.target.temperature,
        fresh_context=config.target.fresh_context
    )
    logger.info(f"✓ Target Agent initialized ({backend_value})")
    
    # Initialize Spotter Agent
    spotter = Spotter(
        confidence_threshold=config.spotter.confidence_threshold,
        use_auxiliary_classifiers=config.spotter.use_auxiliary_classifiers
    )
    logger.info("✓ Spotter Agent initialized")
    
    # Initialize State Manager
    state_manager = StateManager(
        database_path=config.storage.database_path,
        zero_retention=config.storage.zero_retention
    )
    logger.info(f"✓ State Manager initialized (zero_retention={config.storage.zero_retention})")
    
    # Initialize Orchestrator
    orchestrator = Orchestrator(
        sniper=sniper,
        target=target,
        spotter=spotter,
        egg=egg,
        scoring_engine=scoring_engine,
        state_manager=state_manager,
        max_rounds=config.orchestrator.max_rounds,
        round_timeout=config.orchestrator.round_timeout_seconds
    )
    logger.info("✓ Orchestrator initialized")
    
    logger.info("=" * 60)
    logger.info("Red Set ProtoCell system ready")
    logger.info(f"Session ID: {state_manager.session_id}")
    logger.info(f"Max Rounds: {config.orchestrator.max_rounds}")
    logger.info(f"Zero Retention: {config.storage.zero_retention}")
    logger.info("=" * 60)
    
    return orchestrator


async def main(config: RSPConfig):
    """
    Main execution function.
    
    Args:
        config: RSP configuration
    """
    logger.info("Starting Red Set ProtoCell...")
    
    # Setup system
    orchestrator = setup_system(config)
    
    try:
        # Run session
        logger.info("Beginning red teaming session...")
        stats = await orchestrator.run_session()
        
        # Display results
        logger.info("=" * 60)
        logger.info("SESSION COMPLETED")
        logger.info("=" * 60)
        logger.info(f"Total Rounds: {stats['session']['total_rounds']}")
        logger.info(f"Average Score: {stats['scores']['average_global_score']:.3f}")
        logger.info(f"Blocked by EGG: {stats['scores']['total_blocked']}")
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
            logger.info("✓ All session data destroyed")


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Red Set ProtoCell - AI Red Teaming System"
    )
    
    parser.add_argument(
        '--rounds',
        type=int,
        default=100,
        help='Maximum number of rounds to execute (default: 100)'
    )
    
    parser.add_argument(
        '--backend',
        type=str,
        choices=['mock', 'openai', 'anthropic'],
        default='mock',
        help='Target backend to use (default: mock)'
    )
    
    parser.add_argument(
        '--api-key',
        type=str,
        help='API key for target backend'
    )
    
    parser.add_argument(
        '--model',
        type=str,
        help='Model name for target backend'
    )
    
    parser.add_argument(
        '--no-zero-retention',
        action='store_true',
        help='Disable zero-retention policy (keep session data)'
    )
    
    parser.add_argument(
        '--db-path',
        type=str,
        default='rsp_session.db',
        help='Database path (default: rsp_session.db)'
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
    
    # Run main
    try:
        asyncio.run(main(config))
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
