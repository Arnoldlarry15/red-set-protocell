"""
Red Set ProtoCell - Automated Benchmarking

Shows automated benchmarking capabilities.
"""

import asyncio
import logging

from app.benchmarking import BenchmarkConfig, BenchmarkRunner, BenchmarkSuite, create_standard_benchmarks
from app.core.config import load_config_from_env
from app.main import setup_system

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def run_quick_benchmark():
    """Run a quick benchmark example."""
    logger.info("=== Quick Benchmark Example ===")

    # Create benchmark suite
    suite = BenchmarkSuite(results_dir="example_benchmarks")

    # Get standard benchmark configs
    benchmarks = create_standard_benchmarks()
    quick_config = benchmarks["quick"]

    # Setup RSP system - load from environment to respect BACKEND_TYPE and API keys
    config = load_config_from_env()
    config.orchestrator.max_rounds = quick_config.rounds

    # Verify API key is available
    import os

    if not config.target.api_key:
        logger.error("No API key found in configuration.")
        logger.info("Set appropriate environment variables:")
        logger.info("  - For OpenRouter: BACKEND_TYPE=openrouter and OPENROUTER_API_KEY")
        logger.info("  - For OpenAI: OPENAI_API_KEY (default backend)")
        logger.info("  - For Anthropic: BACKEND_TYPE=anthropic and ANTHROPIC_API_KEY")
        return

    backend_name = config.target.backend.value
    logger.info(f"Running benchmark: {quick_config.name}")
    logger.info(f"Description: {quick_config.description}")
    logger.info(f"Backend: {backend_name}")
    logger.info(f"Model: {config.target.model_name}")

    # Run real benchmark
    orchestrator = setup_system(config)
    runner = BenchmarkRunner(orchestrator)
    result = await runner.run_benchmark(
        config=quick_config, model_name=config.target.model_name, model_version="latest", backend=backend_name
    )

    logger.info("Benchmark completed!")
    logger.info(f"Average score: {result.average_score:.3f}")
    logger.info(f"Total rounds: {result.total_rounds}")
    logger.info("Results saved to benchmark suite")


async def run_model_comparison():
    """Show model version comparison."""
    logger.info("\n=== Model Comparison Example ===")

    suite = BenchmarkSuite(results_dir="example_benchmarks")

    # Load actual benchmark results for comparison
    import os
    from pathlib import Path

    results_dir = Path("example_benchmarks")
    if not results_dir.exists() or len(list(results_dir.glob("*.json"))) < 2:
        logger.warning("Not enough benchmark results found for comparison.")
        logger.info("Run benchmarks first to generate results, then compare them.")
        logger.info("\nModel comparison capabilities:")
        logger.info("- Compare average scores across versions")
        logger.info("- Statistical significance testing")
        logger.info("- Finding delta analysis (critical, high, medium, low)")
        logger.info("- Execution time comparison")
        logger.info("- Automated verdict and recommendations")
        return

    # Load two most recent results
    result_files = sorted(results_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    baseline = suite.load_result(result_files[1])
    comparison = suite.load_result(result_files[0])

    # Generate comparison report
    report = suite.compare_results(baseline, comparison)

    logger.info(f"Baseline: {baseline.model_name} v{baseline.model_version}")
    logger.info(f"Comparison: {comparison.model_name} v{comparison.model_version}")
    logger.info(f"Verdict: {report.verdict}")
    logger.info(f"Average score delta: {report.average_score_delta:.3f}")


def main():
    """Main function."""
    print("\n" + "=" * 60)
    print("Red Set ProtoCell - Automated Benchmarking")
    print("=" * 60 + "\n")

    print("This shows the automated benchmarking capabilities:")
    print("1. Standard benchmark configurations (quick, standard, comprehensive, stress)")
    print("2. Automated benchmark execution and result storage")
    print("3. Model version comparison with statistical analysis")
    print("4. Benchmark report generation")
    print("\n")

    # Run async examples
    asyncio.run(run_quick_benchmark())
    asyncio.run(run_model_comparison())

    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
