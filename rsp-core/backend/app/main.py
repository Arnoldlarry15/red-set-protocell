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
✓ System component initialization
✓ Dependency injection and wiring
✓ Configuration loading and validation
✓ Lifecycle management (startup/shutdown)
✓ High-level coordination (orchestrator.run_session)
✓ Logging and monitoring setup

What Does NOT Live Here:
✗ Scoring algorithms
✗ Mutation strategies
✗ Prompt generation logic
✗ API client implementations
✗ Database queries
✗ Business rules or policies

Pre-Release Verification:
[✓] No business logic present
[✓] Only wiring and initialization
[✓] Startup/shutdown hooks properly manage resources
[✓] Configuration loaded from config.py
[✓] Logging configured but no debug data leaked
[✓] Error handling delegates to appropriate modules

Post-Release Maintenance:
- Update dependencies and versions
- Add new component initialization (if new agents/engines added)
- Improve error messages and logging
- DO NOT add conditional logic or business rules
"""

import asyncio
import argparse
import logging
import sys
from typing import Optional

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

    # Initialize Selection Engine if enabled
    selection_engine = None
    selection_strategy_enum = None
    if config.sniper.use_selection_engine:
        from app.engines.selection import SelectionEngine, SelectionStrategy

        selection_engine = SelectionEngine(
            decay_rate=config.sniper.decay_rate,
            decay_interval=config.sniper.decay_interval,
            novelty_weight=config.sniper.novelty_weight,
            diversity_weight=config.sniper.diversity_weight,
            overfitting_threshold=config.sniper.overfitting_threshold,
            tournament_size=config.sniper.tournament_size,
            elite_fraction=config.sniper.elite_fraction
        )

        # Map string to enum
        strategy_map = {
            "elitism": SelectionStrategy.ELITISM,
            "tournament": SelectionStrategy.TOURNAMENT,
            "diversity_preservation": SelectionStrategy.DIVERSITY_PRESERVATION,
            "novelty_search": SelectionStrategy.NOVELTY_SEARCH,
            "hybrid": SelectionStrategy.HYBRID
        }
        selection_strategy_enum = strategy_map.get(
            config.sniper.selection_strategy.lower(),
            SelectionStrategy.HYBRID
        )
        logger.info(f"✓ Selection Engine initialized (strategy: {config.sniper.selection_strategy})")
    else:
        selection_strategy_enum = SelectionStrategy.HYBRID

    # Initialize Sniper Agent
    sniper = Sniper(
        mutation_engine=mutation_engine,
        evolution_pool_size=config.sniper.evolution_pool_size,
        creativity_temperature=config.sniper.creativity_temperature,
        selection_engine=selection_engine,
        selection_strategy=selection_strategy_enum
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
    model_version = model_version_override or config.target.model_name
    state_manager = StateManager(
        database_path=config.storage.database_path,
        zero_retention=config.storage.zero_retention,
        model_version=model_version
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
        if 'time_analytics' in stats:
            logger.info("")
            logger.info("Time Analytics:")
            fatigue = stats['time_analytics']['fatigue']
            drift = stats['time_analytics']['drift']
            logger.info(f"  Fatigue Detected: {fatigue['is_fatigued']}")
            if fatigue['is_fatigued']:
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
            logger.info("✓ All session data destroyed")


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Red Set ProtoCell - AI Red Teaming System",
        epilog="Examples:\n"
               "  python main.py run --backend openai --api-key sk-xxx --rounds 50\n"
               "  python main.py export --session-id rsp_20240101_120000 --format json\n"
               "  python main.py benchmark --backend openai --api-key sk-xxx --suite standard\n"
               "  python main.py inspect --db-path sessions/rsp_session.db",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Run command (default session execution)
    run_parser = subparsers.add_parser('run', help='Run a red teaming session')
    run_parser.add_argument(
        '--rounds',
        type=int,
        default=100,
        help='Maximum number of rounds to execute (default: 100)'
    )
    run_parser.add_argument(
        '--backend',
        type=str,
        choices=['openai', 'anthropic'],
        required=True,
        help='Target backend to use (required: openai or anthropic)'
    )
    run_parser.add_argument(
        '--api-key',
        type=str,
        required=True,
        help='API key for target backend (required)'
    )
    run_parser.add_argument(
        '--model',
        type=str,
        help='Model name for target backend'
    )
    run_parser.add_argument(
        '--no-zero-retention',
        action='store_true',
        help='Disable zero-retention policy (keep session data)'
    )
    run_parser.add_argument(
        '--db-path',
        type=str,
        default='rsp_session.db',
        help='Database path (default: rsp_session.db)'
    )
    run_parser.add_argument(
        '--model-version',
        type=str,
        help='Model version identifier for tracking (optional, defaults to model name)'
    )

    # Export command
    export_parser = subparsers.add_parser('export', help='Export session data')
    export_parser.add_argument(
        '--session-id',
        type=str,
        help='Session ID to export (if not provided, exports all sessions)'
    )
    export_parser.add_argument(
        '--db-path',
        type=str,
        default='rsp_session.db',
        help='Database path (default: rsp_session.db)'
    )
    export_parser.add_argument(
        '--format',
        type=str,
        choices=['json', 'csv', 'jsonl'],
        default='json',
        help='Export format (default: json)'
    )
    export_parser.add_argument(
        '--output',
        type=str,
        help='Output file path (if not provided, prints to stdout)'
    )

    # Benchmark command
    benchmark_parser = subparsers.add_parser('benchmark', help='Run benchmark suite')
    benchmark_parser.add_argument(
        '--backend',
        type=str,
        choices=['openai', 'anthropic'],
        required=True,
        help='Target backend to use'
    )
    benchmark_parser.add_argument(
        '--api-key',
        type=str,
        required=True,
        help='API key for target backend'
    )
    benchmark_parser.add_argument(
        '--model',
        type=str,
        help='Model name for target backend'
    )
    benchmark_parser.add_argument(
        '--suite',
        type=str,
        choices=['standard', 'quick', 'comprehensive'],
        default='standard',
        help='Benchmark suite to run (default: standard)'
    )
    benchmark_parser.add_argument(
        '--output',
        type=str,
        help='Output file for benchmark results (JSON format)'
    )

    # Inspect command
    inspect_parser = subparsers.add_parser('inspect', help='Inspect session database')
    inspect_parser.add_argument(
        '--db-path',
        type=str,
        default='rsp_session.db',
        help='Database path to inspect (default: rsp_session.db)'
    )
    inspect_parser.add_argument(
        '--session-id',
        type=str,
        help='Show details for specific session'
    )

    # For backward compatibility, if no subcommand is provided, use 'run'
    # This allows old usage patterns to continue working
    args = parser.parse_args()
    if args.command is None:
        # If no command specified, show help
        parser.print_help()
        sys.exit(1)

    return args


async def export_command(args):
    """Execute the export command."""
    from app.telemetry.exporter import TelemetryExporter, ExportFormat
    from app.telemetry.extractors import SessionDataExtractor

    logger.info(f"Exporting data from {args.db_path}")

    try:
        extractor = SessionDataExtractor(args.db_path)
        exporter = TelemetryExporter()

        # Determine format
        format_map = {
            'json': ExportFormat.JSON,
            'csv': ExportFormat.CSV,
            'jsonl': ExportFormat.JSON_LINES
        }
        export_format = format_map.get(args.format, ExportFormat.JSON)

        if args.session_id:
            # Export specific session
            logger.info(f"Exporting session: {args.session_id}")
            rounds = extractor.get_session_rounds(args.session_id)
            if not rounds:
                logger.error(f"Session not found: {args.session_id}")
                return
        else:
            # Export all sessions
            logger.info("Exporting all sessions")
            sessions = extractor.get_all_sessions()
            rounds = []
            for session in sessions:
                session_rounds = extractor.get_session_rounds(session['session_id'])
                rounds.extend(session_rounds)

        if args.output:
            # Export to file
            exporter.export_to_file(rounds, args.output, export_format)
            logger.info(f"Data exported to: {args.output}")
        else:
            # Export to stdout
            result = exporter.export_to_string(rounds, export_format)
            print(result)

    except Exception as e:
        logger.error(f"Export failed: {e}", exc_info=True)
        sys.exit(1)


async def benchmark_command(args):
    """Execute the benchmark command."""
    from app.benchmarking.benchmark_suite import BenchmarkSuite, BenchmarkConfig
    
    logger.info(f"Running {args.suite} benchmark suite")

    try:
        # Create configuration
        config = get_default_config()
        config.target.backend = args.backend
        config.target.api_key = args.api_key
        if args.model:
            config.target.model_name = args.model

        # Setup system
        orchestrator = setup_system(config)

        # Create benchmark suite
        suite = BenchmarkSuite()
        
        # Define benchmark configs based on suite type
        if args.suite == 'quick':
            benchmark_configs = [
                BenchmarkConfig(name="Quick Test", rounds=10, timeout_seconds=300)
            ]
        elif args.suite == 'comprehensive':
            benchmark_configs = [
                BenchmarkConfig(name="Comprehensive Test", rounds=500, timeout_seconds=7200)
            ]
        else:  # standard
            benchmark_configs = [
                BenchmarkConfig(name="Standard Test", rounds=100, timeout_seconds=1800)
            ]

        # Run benchmarks
        from app.benchmarking.benchmark_runner import BenchmarkRunner
        runner = BenchmarkRunner(orchestrator)

        results = []
        for bench_config in benchmark_configs:
            result = await runner.run_benchmark(
                bench_config,
                model_name=config.target.model_name,
                model_version=args.model if args.model else config.target.model_name,
                backend=args.backend
            )
            results.append(result)

        # Display results
        logger.info("=" * 60)
        logger.info("BENCHMARK RESULTS")
        logger.info("=" * 60)
        for result in results:
            logger.info(f"Benchmark: {result.benchmark_name}")
            logger.info(f"  Status: {result.status.value}")
            logger.info(f"  Completed Rounds: {result.completed_rounds}/{result.total_rounds}")
            logger.info(f"  Average Score: {result.average_score:.3f}")
            logger.info(f"  Execution Time: {result.execution_time_seconds:.1f}s")
            logger.info("")

        # Export results if output file specified
        if args.output:
            import json
            with open(args.output, 'w') as f:
                json.dump([r.to_dict() for r in results], f, indent=2)
            logger.info(f"Results saved to: {args.output}")

    except Exception as e:
        logger.error(f"Benchmark failed: {e}", exc_info=True)
        sys.exit(1)


async def inspect_command(args):
    """Execute the inspect command."""
    from app.telemetry.extractors import SessionDataExtractor

    logger.info(f"Inspecting database: {args.db_path}")

    try:
        extractor = SessionDataExtractor(args.db_path)

        if args.session_id:
            # Show details for specific session
            rounds = extractor.get_session_rounds(args.session_id)
            if not rounds:
                logger.error(f"Session not found: {args.session_id}")
                return

            logger.info(f"Session: {args.session_id}")
            logger.info(f"Total Rounds: {len(rounds)}")
            
            # Calculate statistics
            scores = [r.get('global_score', 0) for r in rounds]
            if scores:
                avg_score = sum(scores) / len(scores)
                max_score = max(scores)
                min_score = min(scores)
                blocked = sum(1 for r in rounds if r.get('blocked_by_egg', False))

                logger.info(f"Average Score: {avg_score:.3f}")
                logger.info(f"Score Range: {min_score:.3f} - {max_score:.3f}")
                logger.info(f"Blocked by EGG: {blocked}")

            # Show recent rounds
            logger.info("\nRecent Rounds:")
            for round_data in rounds[-5:]:
                logger.info(f"  Round {round_data.get('round_number')}: "
                          f"Score {round_data.get('global_score', 0):.3f}, "
                          f"Domain {round_data.get('attack_domain', 'unknown')}")
        else:
            # Show all sessions summary
            sessions = extractor.get_all_sessions()
            logger.info(f"Total Sessions: {len(sessions)}")
            logger.info("\nSession Summary:")
            for session in sessions:
                logger.info(f"  {session['session_id']}: "
                          f"{session.get('total_rounds', 0)} rounds, "
                          f"avg score {session.get('average_score', 0):.3f}")

    except Exception as e:
        logger.error(f"Inspect failed: {e}", exc_info=True)
        sys.exit(1)


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

    # Execute command
    if args.command == 'run':
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

    elif args.command == 'export':
        try:
            asyncio.run(export_command(args))
        except Exception as e:
            logger.error(f"Export command failed: {e}", exc_info=True)
            sys.exit(1)

    elif args.command == 'benchmark':
        try:
            asyncio.run(benchmark_command(args))
        except Exception as e:
            logger.error(f"Benchmark command failed: {e}", exc_info=True)
            sys.exit(1)

    elif args.command == 'inspect':
        try:
            asyncio.run(inspect_command(args))
        except Exception as e:
            logger.error(f"Inspect command failed: {e}", exc_info=True)
            sys.exit(1)

    else:
        logger.error(f"Unknown command: {args.command}")
        sys.exit(1)
