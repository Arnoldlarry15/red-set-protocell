"""
Tests for benchmarking module.
"""

import pytest
from datetime import datetime
from pathlib import Path

from app.benchmarking.benchmark_suite import (
    BenchmarkConfig,
    BenchmarkResult,
    BenchmarkStatus,
    BenchmarkSuite,
)


def test_benchmark_config_creation():
    """Test creating a benchmark configuration."""
    config = BenchmarkConfig(
        name="test",
        description="Test benchmark",
        rounds=10,
    )

    assert config.name == "test"
    assert config.rounds == 10
    assert config.concurrent_rounds == 1


def test_benchmark_result_creation():
    """Test creating a benchmark result."""
    config = BenchmarkConfig(name="test", description="Test", rounds=10)

    result = BenchmarkResult(
        benchmark_name="test",
        model_name="gpt-3.5-turbo",
        model_version="0125",
        backend="openai",
        timestamp=datetime.now().isoformat(),
        status=BenchmarkStatus.COMPLETED,
        total_rounds=10,
        completed_rounds=10,
        average_score=0.35,
        std_deviation=0.12,
        min_score=0.15,
        max_score=0.65,
        blocked_count=1,
        critical_findings=0,
        high_findings=2,
        medium_findings=3,
        low_findings=5,
        execution_time_seconds=120.5,
        config=config,
    )

    assert result.average_score == 0.35
    assert result.status == BenchmarkStatus.COMPLETED
    assert result.config.name == "test"


def test_benchmark_result_to_dict():
    """Test converting benchmark result to dictionary."""
    config = BenchmarkConfig(name="test", description="Test", rounds=10)
    result = BenchmarkResult(
        benchmark_name="test",
        model_name="gpt-3.5-turbo",
        model_version="0125",
        backend="openai",
        timestamp=datetime.now().isoformat(),
        status=BenchmarkStatus.COMPLETED,
        total_rounds=10,
        completed_rounds=10,
        average_score=0.35,
        std_deviation=0.12,
        min_score=0.15,
        max_score=0.65,
        blocked_count=1,
        critical_findings=0,
        high_findings=2,
        medium_findings=3,
        low_findings=5,
        execution_time_seconds=120.5,
        config=config,
    )

    data = result.to_dict()
    assert data['average_score'] == 0.35
    assert data['status'] == 'completed'
    assert 'config' in data


def test_benchmark_suite_save_and_load(tmp_path):
    """Test saving and loading benchmark results."""
    suite = BenchmarkSuite(results_dir=str(tmp_path))

    config = BenchmarkConfig(name="test", description="Test", rounds=10)
    result = BenchmarkResult(
        benchmark_name="test",
        model_name="gpt-3.5-turbo",
        model_version="0125",
        backend="openai",
        timestamp=datetime.now().isoformat(),
        status=BenchmarkStatus.COMPLETED,
        total_rounds=10,
        completed_rounds=10,
        average_score=0.35,
        std_deviation=0.12,
        min_score=0.15,
        max_score=0.65,
        blocked_count=1,
        critical_findings=0,
        high_findings=2,
        medium_findings=3,
        low_findings=5,
        execution_time_seconds=120.5,
        config=config,
    )

    # Save result
    filepath = suite.save_result(result)
    assert filepath.exists()

    # Load result
    loaded = suite.load_result(filepath)
    assert loaded.average_score == result.average_score
    assert loaded.model_name == result.model_name


def test_benchmark_comparison():
    """Test comparing two benchmark results."""
    suite = BenchmarkSuite()
    config = BenchmarkConfig(name="test", description="Test", rounds=50)

    baseline = BenchmarkResult(
        benchmark_name="test",
        model_name="gpt-3.5-turbo",
        model_version="v1",
        backend="openai",
        timestamp=datetime.now().isoformat(),
        status=BenchmarkStatus.COMPLETED,
        total_rounds=50,
        completed_rounds=50,
        average_score=0.45,
        std_deviation=0.10,
        min_score=0.20,
        max_score=0.70,
        blocked_count=2,
        critical_findings=1,
        high_findings=5,
        medium_findings=8,
        low_findings=10,
        execution_time_seconds=300.0,
        config=config,
    )

    comparison = BenchmarkResult(
        benchmark_name="test",
        model_name="gpt-3.5-turbo",
        model_version="v2",
        backend="openai",
        timestamp=datetime.now().isoformat(),
        status=BenchmarkStatus.COMPLETED,
        total_rounds=50,
        completed_rounds=50,
        average_score=0.35,  # Improved (lower)
        std_deviation=0.08,
        min_score=0.15,
        max_score=0.60,
        blocked_count=3,
        critical_findings=0,
        high_findings=3,
        medium_findings=6,
        low_findings=12,
        execution_time_seconds=280.0,
        config=config,
    )

    report = suite.compare_results(baseline, comparison)

    assert report.score_delta < 0  # Lower is better
    assert report.improvement  # Should detect improvement
    assert not report.regression
    assert report.verdict == "IMPROVEMENT"
