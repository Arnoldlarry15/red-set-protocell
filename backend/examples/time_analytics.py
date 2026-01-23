"""
Time Analytics Examples for Red Set ProtoCell

Shows the time-based analytics features:
- Fatigue tracking
- Regression detection
- Score drift analysis

This shows how to use RSP's time analytics to answer questions like:
- "Does this model get worse after sustained pressure?"
- "Did yesterday's model actually improve, or just shift failure modes?"
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import RSPConfig, get_default_config
from app.core.egg import EthicalGuardrailGovernor
from app.engines.scoring import ScoringEngine
from app.engines.mutation import MutationEngine
from app.agents.sniper import Sniper
from app.agents.target import create_target
from app.agents.spotter import Spotter
from app.agents.orchestrator import Orchestrator, StateManager
from app.analytics.time_tracking import (
    FatigueTracker,
    RegressionDetector,
    ScoreDriftAnalyzer
)


async def run_test_session(model_version: str, rounds: int = 30) -> str:
    """
    Run a test session and return the session ID.

    Args:
        model_version: Model version identifier
        rounds: Number of rounds to run

    Returns:
        Session ID
    """
    print(f"\n{'='*60}")
    print(f"Running session with {model_version}")
    print(f"{'='*60}")

    # Create configuration
    config = get_default_config()
    config.orchestrator.max_rounds = rounds
    config.storage.zero_retention = False  # Keep data for analysis
    config.storage.database_path = "time_analytics_example.db"

    # Initialize components
    egg = EthicalGuardrailGovernor()
    scoring_engine = ScoringEngine()
    mutation_engine = MutationEngine()

    sniper = Sniper(
        mutation_engine=mutation_engine,
        evolution_pool_size=5,
        creativity_temperature=0.8
    )

    # Create real target with API
    import os
    from app.factories import TargetFactory
    
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: No API key found.")
        print("Set OPENAI_API_KEY or ANTHROPIC_API_KEY environment variable.")
        print("Example: export OPENAI_API_KEY=sk-your-key-here")
        raise ValueError("API key required for live execution")

    # Use OpenAI by default, or Anthropic if available
    if os.getenv("OPENAI_API_KEY"):
        target = TargetFactory.create(
            "openai",
            api_key=os.getenv("OPENAI_API_KEY"),
            model_name="gpt-3.5-turbo",
            max_tokens=500
        )
        print(f"Using OpenAI backend: gpt-3.5-turbo")
    else:
        target = TargetFactory.create(
            "anthropic",
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            model_name="claude-3-haiku-20240307",
            max_tokens=500
        )
        print(f"Using Anthropic backend: claude-3-haiku-20240307")

    spotter = Spotter()

    state_manager = StateManager(
        database_path="time_analytics_example.db",
        zero_retention=False,
        model_version=model_version
    )

    orchestrator = Orchestrator(
        sniper=sniper,
        target=target,
        spotter=spotter,
        egg=egg,
        scoring_engine=scoring_engine,
        state_manager=state_manager,
        max_rounds=rounds
    )

    # Run session
    stats = await orchestrator.run_session()

    print(f"✓ Session completed: {state_manager.session_id}")
    print(f"  Total rounds: {stats['session']['total_rounds']}")
    print(f"  Average score: {stats['scores']['average_global_score']:.3f}")

    return state_manager.session_id


def analyze_fatigue(session_id: str):
    """
    Analyze fatigue for a session.

    Args:
        session_id: Session to analyze
    """
    print(f"\n{'='*60}")
    print("FATIGUE ANALYSIS")
    print(f"{'='*60}")

    tracker = FatigueTracker("time_analytics_example.db")
    report = tracker.analyze_fatigue(session_id)

    print(f"Session: {session_id}")
    print(f"Rounds analyzed: {report.rounds_analyzed}")
    print(f"Time span: {report.time_span_seconds:.1f} seconds")
    print()
    print(f"Fatigue detected: {report.is_fatigued}")
    print(f"Fatigue score: {report.fatigue_score:.3f}")
    print(f"Degradation rate: {report.degradation_rate:+.4f} per round")
    print()
    print(f"Early rounds mean: {report.early_mean:.3f}")
    print(f"Late rounds mean: {report.late_mean:.3f}")
    print(f"Score change: {report.late_mean - report.early_mean:+.3f}")
    print()
    print(f"Recommendation: {report.recommendation}")


def analyze_regression(baseline: str, comparison: str):
    """
    Analyze regression between two model versions.

    Args:
        baseline: Baseline model version
        comparison: Comparison model version
    """
    print(f"\n{'='*60}")
    print("REGRESSION ANALYSIS")
    print(f"{'='*60}")

    detector = RegressionDetector("time_analytics_example.db")
    report = detector.compare_versions(baseline, comparison)

    print(f"Baseline: {report.baseline_version}")
    print(f"  Mean score: {report.baseline_mean:.3f}")
    print(f"  Rounds: {report.details['baseline_rounds']}")
    print()
    print(f"Comparison: {report.comparison_version}")
    print(f"  Mean score: {report.comparison_mean:.3f}")
    print(f"  Rounds: {report.details['comparison_rounds']}")
    print()
    print(f"Verdict: {report.verdict}")
    print(f"Score delta: {report.score_delta:+.3f}")
    print(f"Is regression: {report.is_regression}")
    print(f"Statistical significance: {report.statistical_significance:.3f}")
    print(f"Failure mode shift: {report.failure_mode_shift}")


def analyze_drift(session_id: str):
    """
    Analyze score drift for a session.

    Args:
        session_id: Session to analyze
    """
    print(f"\n{'='*60}")
    print("SCORE DRIFT ANALYSIS")
    print(f"{'='*60}")

    analyzer = ScoreDriftAnalyzer("time_analytics_example.db")
    metrics = analyzer.analyze_drift(session_id)

    print(f"Session: {session_id}")
    print(f"Total rounds: {metrics.total_rounds}")
    print(f"Time span: {metrics.time_span_seconds:.1f} seconds")
    print()
    print(f"Mean score: {metrics.mean_score:.3f}")
    print(f"Std deviation: {metrics.std_deviation:.3f}")
    print(f"Variance: {metrics.variance:.4f}")
    print()
    print(f"Score range: {metrics.min_score:.3f} to {metrics.max_score:.3f}")
    print(f"Range span: {metrics.score_range:.3f}")
    print()
    print(f"Trend slope: {metrics.trend_slope:+.4f}")
    print(f"Drift direction: {metrics.drift_direction.value}")


async def main():
    """Main function."""
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║         RSP Time Analytics Examples                           ║
    ║         Time as a First-Class Dimension                   ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)

    print("\nThis showcases RSP's time-based analytics:")
    print("1. Fatigue tracking - Does the model degrade over rounds?")
    print("2. Regression detection - Did the new version improve?")
    print("3. Score drift - What are the performance trends?")

    # Run multiple sessions with different model versions
    print("\n" + "="*60)
    print("STEP 1: Running test sessions")
    print("="*60)

    session1 = await run_test_session("model-v1.0", rounds=20)
    session2 = await run_test_session("model-v2.0", rounds=20)
    session3 = await run_test_session("model-v2.1", rounds=30)

    # Analyze fatigue for the longest session
    analyze_fatigue(session3)

    # Compare model versions for regression
    analyze_regression("model-v1.0", "model-v2.0")
    analyze_regression("model-v2.0", "model-v2.1")

    # Analyze drift for each session
    analyze_drift(session1)
    analyze_drift(session2)
    analyze_drift(session3)

    print("\n" + "="*60)
    print("EXAMPLE COMPLETE")
    print("="*60)
    print("\nKey Insights:")
    print("• Time analytics provide quantitative measures of model behavior")
    print("• Fatigue detection identifies degradation under sustained pressure")
    print("• Regression analysis compares model versions objectively")
    print("• Drift analysis reveals performance trends over time")
    print()
    print("Database saved at: time_analytics_example.db")
    print("You can run additional queries on this database for further analysis.")


if __name__ == "__main__":
    asyncio.run(main())
