"""
Red Set ProtoCell - Benchmark Runner

Executes benchmarks and manages benchmark lifecycle.
"""

import asyncio
import logging
import time
from datetime import datetime, timezone
from typing import Dict, Optional

from app.agents.orchestrator import Orchestrator
from app.benchmarking.benchmark_suite import BenchmarkConfig, BenchmarkResult, BenchmarkStatus

logger = logging.getLogger(__name__)


class BenchmarkRunner:
    """
    Executes benchmarks using the RSP orchestrator.

    Provides functionality for:
    - Running benchmarks with specific configurations
    - Tracking benchmark execution progress
    - Collecting and aggregating results
    """

    def __init__(self, orchestrator: Orchestrator):
        """
        Initialize benchmark runner.

        Args:
            orchestrator: Configured RSP orchestrator
        """
        self.orchestrator = orchestrator
        self.current_benchmark: Optional[BenchmarkConfig] = None

    async def run_benchmark(
        self,
        config: BenchmarkConfig,
        model_name: str,
        model_version: str,
        backend: str,
    ) -> BenchmarkResult:
        """
        Run a benchmark with the given configuration.

        Args:
            config: Benchmark configuration
            model_name: Name of model being tested
            model_version: Version identifier for the model
            backend: Backend type (openai, anthropic, etc.)

        Returns:
            Benchmark result
        """
        logger.info(f"Starting benchmark: {config.name}")
        logger.info(f"Model: {model_name} {model_version}")
        logger.info(f"Rounds: {config.rounds}")

        self.current_benchmark = config
        start_time = time.time()
        timestamp = datetime.now(timezone.utc).isoformat()

        try:
            # Update orchestrator configuration
            self.orchestrator.max_rounds = config.rounds
            if config.concurrent_rounds > 1:
                self.orchestrator.concurrent_rounds = config.concurrent_rounds

            # Run the session
            stats = await asyncio.wait_for(self.orchestrator.run_session(), timeout=config.timeout_seconds)

            # Extract metrics from stats
            session_stats = stats.get("session", {})
            score_stats = stats.get("scores", {})

            total_rounds = session_stats.get("total_rounds", 0)
            average_score = score_stats.get("average_global_score", 0.0)
            std_deviation = score_stats.get("std_deviation", 0.0)
            min_score = score_stats.get("min_score", 0.0)
            max_score = score_stats.get("max_score", 1.0)
            blocked_count = score_stats.get("total_blocked", 0)

            # Categorize findings by severity
            critical_findings = score_stats.get("critical_count", 0)
            high_findings = score_stats.get("high_count", 0)
            medium_findings = score_stats.get("medium_count", 0)
            low_findings = score_stats.get("low_count", 0)

            execution_time = time.time() - start_time

            result = BenchmarkResult(
                benchmark_name=config.name,
                model_name=model_name,
                model_version=model_version,
                backend=backend,
                timestamp=timestamp,
                status=BenchmarkStatus.COMPLETED,
                total_rounds=total_rounds,
                completed_rounds=total_rounds,
                average_score=average_score,
                std_deviation=std_deviation,
                min_score=min_score,
                max_score=max_score,
                blocked_count=blocked_count,
                critical_findings=critical_findings,
                high_findings=high_findings,
                medium_findings=medium_findings,
                low_findings=low_findings,
                execution_time_seconds=execution_time,
                config=config,
            )

            logger.info(f"Benchmark completed: {config.name}")
            logger.info(f"Average score: {average_score:.3f}")
            logger.info(f"Execution time: {execution_time:.1f}s")

            return result

        except asyncio.TimeoutError:
            logger.error(f"Benchmark timeout after {config.timeout_seconds}s")
            execution_time = time.time() - start_time

            # Return partial result
            return BenchmarkResult(
                benchmark_name=config.name,
                model_name=model_name,
                model_version=model_version,
                backend=backend,
                timestamp=timestamp,
                status=BenchmarkStatus.FAILED,
                total_rounds=config.rounds,
                completed_rounds=0,
                average_score=0.0,
                std_deviation=0.0,
                min_score=0.0,
                max_score=0.0,
                blocked_count=0,
                critical_findings=0,
                high_findings=0,
                medium_findings=0,
                low_findings=0,
                execution_time_seconds=execution_time,
                config=config,
            )

        except Exception as e:
            logger.error(f"Benchmark failed with error: {e}")
            execution_time = time.time() - start_time

            # Return failed result
            return BenchmarkResult(
                benchmark_name=config.name,
                model_name=model_name,
                model_version=model_version,
                backend=backend,
                timestamp=timestamp,
                status=BenchmarkStatus.FAILED,
                total_rounds=config.rounds,
                completed_rounds=0,
                average_score=0.0,
                std_deviation=0.0,
                min_score=0.0,
                max_score=0.0,
                blocked_count=0,
                critical_findings=0,
                high_findings=0,
                medium_findings=0,
                low_findings=0,
                execution_time_seconds=execution_time,
                config=config,
            )

        finally:
            self.current_benchmark = None


def create_standard_benchmarks() -> Dict[str, BenchmarkConfig]:
    """
    Create standard benchmark configurations.

    Returns:
        Dictionary of benchmark name to configuration
    """
    return {
        "quick": BenchmarkConfig(
            name="quick",
            description="Quick benchmark for rapid testing (10 rounds)",
            rounds=10,
            concurrent_rounds=1,
            timeout_seconds=600,
        ),
        "standard": BenchmarkConfig(
            name="standard",
            description="Standard benchmark for routine evaluation (50 rounds)",
            rounds=50,
            concurrent_rounds=1,
            timeout_seconds=1800,
        ),
        "comprehensive": BenchmarkConfig(
            name="comprehensive",
            description="Comprehensive benchmark for thorough evaluation (100 rounds)",
            rounds=100,
            concurrent_rounds=1,
            timeout_seconds=3600,
        ),
        "stress": BenchmarkConfig(
            name="stress",
            description="Stress test with high concurrency (200 rounds)",
            rounds=200,
            concurrent_rounds=5,
            timeout_seconds=7200,
        ),
    }
