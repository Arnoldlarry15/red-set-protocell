"""
Tests for benchmark_runner module.
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.benchmarking.benchmark_runner import BenchmarkRunner, create_standard_benchmarks
from app.benchmarking.benchmark_suite import BenchmarkConfig, BenchmarkStatus


def make_config(**kwargs):
    defaults = {
        "name": "test_benchmark",
        "description": "Test benchmark",
        "rounds": 5,
        "concurrent_rounds": 1,
        "timeout_seconds": 60,
    }
    defaults.update(kwargs)
    return BenchmarkConfig(**defaults)


def make_mock_orchestrator(stats=None):
    """Create a mock orchestrator that returns given stats."""
    if stats is None:
        stats = {
            "session": {"total_rounds": 5},
            "scores": {
                "average_global_score": 0.65,
                "std_deviation": 0.12,
                "min_score": 0.4,
                "max_score": 0.9,
                "total_blocked": 1,
                "critical_count": 2,
                "high_count": 1,
                "medium_count": 1,
                "low_count": 1,
            },
        }
    orchestrator = MagicMock()
    orchestrator.run_session = AsyncMock(return_value=stats)
    orchestrator.max_rounds = 10
    orchestrator.concurrent_rounds = 1
    return orchestrator


class TestBenchmarkRunner:
    @pytest.mark.asyncio
    async def test_run_benchmark_success(self):
        orchestrator = make_mock_orchestrator()
        runner = BenchmarkRunner(orchestrator)
        config = make_config()

        result = await runner.run_benchmark(config, "gpt-4", "v1", "openai")

        assert result.status == BenchmarkStatus.COMPLETED
        assert result.benchmark_name == "test_benchmark"
        assert result.model_name == "gpt-4"
        assert result.model_version == "v1"
        assert result.backend == "openai"
        assert result.total_rounds == 5
        assert result.average_score == pytest.approx(0.65)
        assert result.blocked_count == 1
        assert result.critical_findings == 2

    @pytest.mark.asyncio
    async def test_run_benchmark_sets_orchestrator_max_rounds(self):
        orchestrator = make_mock_orchestrator()
        runner = BenchmarkRunner(orchestrator)
        config = make_config(rounds=20)

        await runner.run_benchmark(config, "gpt-4", "v1", "openai")

        assert orchestrator.max_rounds == 20

    @pytest.mark.asyncio
    async def test_run_benchmark_sets_concurrent_rounds(self):
        orchestrator = make_mock_orchestrator()
        runner = BenchmarkRunner(orchestrator)
        config = make_config(concurrent_rounds=3)

        await runner.run_benchmark(config, "gpt-4", "v1", "openai")

        assert orchestrator.concurrent_rounds == 3

    @pytest.mark.asyncio
    async def test_run_benchmark_no_concurrent_update_when_single(self):
        orchestrator = make_mock_orchestrator()
        original_concurrent = 1
        orchestrator.concurrent_rounds = original_concurrent
        runner = BenchmarkRunner(orchestrator)
        config = make_config(concurrent_rounds=1)

        await runner.run_benchmark(config, "gpt-4", "v1", "openai")

        # concurrent_rounds=1 should not trigger update
        assert orchestrator.concurrent_rounds == original_concurrent

    @pytest.mark.asyncio
    async def test_run_benchmark_clears_current_benchmark_on_success(self):
        orchestrator = make_mock_orchestrator()
        runner = BenchmarkRunner(orchestrator)
        config = make_config()

        await runner.run_benchmark(config, "gpt-4", "v1", "openai")

        assert runner.current_benchmark is None

    @pytest.mark.asyncio
    async def test_run_benchmark_timeout(self):
        orchestrator = MagicMock()
        orchestrator.run_session = AsyncMock(side_effect=asyncio.TimeoutError())
        runner = BenchmarkRunner(orchestrator)
        config = make_config(timeout_seconds=1)

        result = await runner.run_benchmark(config, "gpt-4", "v1", "openai")

        assert result.status == BenchmarkStatus.FAILED
        assert result.average_score == 0.0
        assert result.completed_rounds == 0

    @pytest.mark.asyncio
    async def test_run_benchmark_exception(self):
        orchestrator = MagicMock()
        orchestrator.run_session = AsyncMock(side_effect=RuntimeError("API error"))
        runner = BenchmarkRunner(orchestrator)
        config = make_config()

        result = await runner.run_benchmark(config, "gpt-4", "v1", "openai")

        assert result.status == BenchmarkStatus.FAILED
        assert result.average_score == 0.0

    @pytest.mark.asyncio
    async def test_run_benchmark_clears_current_benchmark_on_failure(self):
        orchestrator = MagicMock()
        orchestrator.run_session = AsyncMock(side_effect=RuntimeError("fail"))
        runner = BenchmarkRunner(orchestrator)
        config = make_config()

        await runner.run_benchmark(config, "gpt-4", "v1", "openai")

        assert runner.current_benchmark is None

    @pytest.mark.asyncio
    async def test_run_benchmark_result_has_execution_time(self):
        orchestrator = make_mock_orchestrator()
        runner = BenchmarkRunner(orchestrator)
        config = make_config()

        result = await runner.run_benchmark(config, "gpt-4", "v1", "openai")

        assert result.execution_time_seconds >= 0

    @pytest.mark.asyncio
    async def test_run_benchmark_empty_stats(self):
        orchestrator = MagicMock()
        orchestrator.run_session = AsyncMock(return_value={})
        runner = BenchmarkRunner(orchestrator)
        config = make_config()

        result = await runner.run_benchmark(config, "gpt-4", "v1", "openai")

        assert result.status == BenchmarkStatus.COMPLETED
        assert result.total_rounds == 0
        assert result.average_score == 0.0


class TestCreateStandardBenchmarks:
    def test_returns_dict(self):
        benchmarks = create_standard_benchmarks()
        assert isinstance(benchmarks, dict)

    def test_contains_expected_keys(self):
        benchmarks = create_standard_benchmarks()
        assert "quick" in benchmarks
        assert "standard" in benchmarks
        assert "comprehensive" in benchmarks
        assert "stress" in benchmarks

    def test_quick_benchmark_config(self):
        benchmarks = create_standard_benchmarks()
        quick = benchmarks["quick"]
        assert quick.name == "quick"
        assert quick.rounds == 10
        assert quick.concurrent_rounds == 1

    def test_stress_benchmark_has_concurrency(self):
        benchmarks = create_standard_benchmarks()
        stress = benchmarks["stress"]
        assert stress.concurrent_rounds == 5
        assert stress.rounds == 200

    def test_all_configs_are_benchmark_config(self):
        benchmarks = create_standard_benchmarks()
        for name, config in benchmarks.items():
            assert isinstance(config, BenchmarkConfig), f"{name} should be BenchmarkConfig"
