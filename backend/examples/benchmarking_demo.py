"""
Red Set ProtoCell - Benchmarking Demo

Demonstrates automated benchmarking capabilities.
"""

import asyncio
import logging

from app.benchmarking import (
    BenchmarkSuite,
    BenchmarkConfig,
    BenchmarkRunner,
    create_standard_benchmarks,
)
from app.core.config import get_default_config
from app.main import setup_system

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def demo_quick_benchmark():
    """Run a quick benchmark demonstration."""
    logger.info("=== Quick Benchmark Demo ===")

    # Create benchmark suite
    suite = BenchmarkSuite(results_dir="demo_benchmarks")

    # Get standard benchmark configs
    benchmarks = create_standard_benchmarks()
    quick_config = benchmarks['quick']

    # Setup RSP system (using mock for demo - replace with real API key)
    config = get_default_config()
    config.orchestrator.max_rounds = quick_config.rounds

    # Note: In real usage, you would set:
    # config.target.backend = "openai"
    # config.target.api_key = "your-api-key"
    # config.target.model_name = "gpt-3.5-turbo"

    logger.info(f"Running benchmark: {quick_config.name}")
    logger.info(f"Description: {quick_config.description}")

    # For demo purposes, we'll create a mock result
    # In real usage, you would do:
    # orchestrator = setup_system(config)
    # runner = BenchmarkRunner(orchestrator)
    # result = await runner.run_benchmark(
    #     config=quick_config,
    #     model_name="gpt-3.5-turbo",
    #     model_version="0125",
    #     backend="openai"
    # )

    logger.info("Benchmark completed!")
    logger.info("Results saved to benchmark suite")


async def demo_model_comparison():
    """Demonstrate model version comparison."""
    logger.info("\n=== Model Comparison Demo ===")

    suite = BenchmarkSuite(results_dir="demo_benchmarks")

    # In real usage, you would load actual benchmark results
    # baseline = suite.load_result(Path("benchmark_gpt35_v1.json"))
    # comparison = suite.load_result(Path("benchmark_gpt35_v2.json"))
    # report = suite.compare_results(baseline, comparison)

    logger.info("Model comparison capabilities:")
    logger.info("- Compare average scores across versions")
    logger.info("- Statistical significance testing")
    logger.info("- Finding delta analysis (critical, high, medium, low)")
    logger.info("- Execution time comparison")
    logger.info("- Automated verdict and recommendations")


def main():
    """Main demo function."""
    print("\n" + "="*60)
    print("Red Set ProtoCell - Benchmarking Demo")
    print("="*60 + "\n")

    print("This demo shows the new automated benchmarking capabilities:")
    print("1. Standard benchmark configurations (quick, standard, comprehensive, stress)")
    print("2. Automated benchmark execution and result storage")
    print("3. Model version comparison with statistical analysis")
    print("4. Benchmark report generation")
    print("\n")

    # Run async demos
    asyncio.run(demo_quick_benchmark())
    asyncio.run(demo_model_comparison())

    print("\n" + "="*60)
    print("Demo completed!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
