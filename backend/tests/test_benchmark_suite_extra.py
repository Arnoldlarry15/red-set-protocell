"""
Additional tests for benchmark_suite module - covering missing branches.
"""

import json

import pytest

from app.benchmarking.benchmark_suite import (
    BenchmarkConfig,
    BenchmarkResult,
    BenchmarkStatus,
    BenchmarkSuite,
    ComparisonReport,
)


def make_result(
    name="test",
    model_name="gpt-4",
    model_version="v1",
    average_score=0.5,
    std_deviation=0.1,
    total_rounds=50,
    **kwargs,
):
    defaults = dict(
        benchmark_name=name,
        model_name=model_name,
        model_version=model_version,
        backend="openai",
        timestamp="2024-01-01T00:00:00",
        status=BenchmarkStatus.COMPLETED,
        total_rounds=total_rounds,
        completed_rounds=total_rounds,
        average_score=average_score,
        std_deviation=std_deviation,
        min_score=0.1,
        max_score=0.9,
        blocked_count=2,
        critical_findings=3,
        high_findings=2,
        medium_findings=5,
        low_findings=8,
        execution_time_seconds=120.0,
        config=BenchmarkConfig(name=name, description="test", rounds=total_rounds),
    )
    defaults.update(kwargs)
    return BenchmarkResult(**defaults)


class TestBenchmarkResultMethods:
    def test_to_dict(self):
        result = make_result()
        d = result.to_dict()
        assert d["status"] == "completed"
        assert d["benchmark_name"] == "test"
        assert isinstance(d["config"], dict)

    def test_to_json(self):
        result = make_result()
        j = result.to_json()
        loaded = json.loads(j)
        assert loaded["model_name"] == "gpt-4"


class TestBenchmarkConfigToDict:
    def test_to_dict(self):
        config = BenchmarkConfig(name="quick", description="Quick test", rounds=10)
        d = config.to_dict()
        assert d["name"] == "quick"
        assert d["rounds"] == 10


class TestBenchmarkSuite:
    def test_save_and_load_result(self, tmp_path):
        suite = BenchmarkSuite(results_dir=str(tmp_path))
        result = make_result()
        filepath = suite.save_result(result)
        assert filepath.exists()

        loaded = suite.load_result(filepath)
        assert loaded.benchmark_name == result.benchmark_name
        assert loaded.model_name == result.model_name
        assert loaded.average_score == pytest.approx(result.average_score)
        assert loaded.status == BenchmarkStatus.COMPLETED

    def test_list_results_empty(self, tmp_path):
        suite = BenchmarkSuite(results_dir=str(tmp_path))
        results = suite.list_results()
        assert results == []

    def test_list_results(self, tmp_path):
        suite = BenchmarkSuite(results_dir=str(tmp_path))
        result = make_result()
        suite.save_result(result)
        results = suite.list_results()
        assert len(results) == 1

    def test_list_results_filter_by_benchmark_name(self, tmp_path):
        suite = BenchmarkSuite(results_dir=str(tmp_path))
        suite.save_result(make_result(name="quick"))
        suite.save_result(make_result(name="standard"))
        results = suite.list_results(benchmark_name="quick")
        assert all("quick" in str(r) for r in results)

    def test_list_results_filter_by_model_name(self, tmp_path):
        suite = BenchmarkSuite(results_dir=str(tmp_path))
        suite.save_result(make_result(model_name="gpt-4"))
        suite.save_result(make_result(model_name="claude"))
        results = suite.list_results(model_name="gpt-4")
        assert all("gpt-4" in str(r) for r in results)

    def test_compare_results_improvement(self, tmp_path):
        suite = BenchmarkSuite(results_dir=str(tmp_path))
        baseline = make_result(average_score=0.7, std_deviation=0.05, total_rounds=50)
        comparison = make_result(average_score=0.5, std_deviation=0.05, total_rounds=50, model_version="v2")
        report = suite.compare_results(baseline, comparison)
        assert report.improvement is True
        assert report.regression is False
        assert report.verdict == "IMPROVEMENT"

    def test_compare_results_regression(self, tmp_path):
        suite = BenchmarkSuite(results_dir=str(tmp_path))
        baseline = make_result(average_score=0.3, std_deviation=0.05, total_rounds=50)
        comparison = make_result(average_score=0.5, std_deviation=0.05, total_rounds=50, model_version="v2")
        report = suite.compare_results(baseline, comparison)
        assert report.regression is True
        assert report.verdict == "REGRESSION"

    def test_compare_results_marginal_change(self, tmp_path):
        suite = BenchmarkSuite(results_dir=str(tmp_path))
        # delta=0.03 (no improvement/regression), but very small std→statistically_significant
        baseline = make_result(average_score=0.5, std_deviation=0.001, total_rounds=100)
        comparison = make_result(average_score=0.53, std_deviation=0.001, total_rounds=100, model_version="v2")
        report = suite.compare_results(baseline, comparison)
        assert report.verdict == "MARGINAL CHANGE"

        suite = BenchmarkSuite(results_dir=str(tmp_path))
        # Small difference, high std_deviation
        baseline = make_result(average_score=0.5, std_deviation=0.5, total_rounds=1)
        comparison = make_result(average_score=0.51, std_deviation=0.5, total_rounds=1, model_version="v2")
        report = suite.compare_results(baseline, comparison)
        assert "NO SIGNIFICANT CHANGE" in report.verdict or "MARGINAL" in report.verdict

    def test_compare_results_to_dict(self, tmp_path):
        suite = BenchmarkSuite(results_dir=str(tmp_path))
        baseline = make_result(average_score=0.5)
        comparison = make_result(average_score=0.4, model_version="v2")
        report = suite.compare_results(baseline, comparison)
        d = report.to_dict()
        assert "baseline" in d
        assert "comparison" in d
        assert "verdict" in d

    def test_compare_results_to_json(self, tmp_path):
        suite = BenchmarkSuite(results_dir=str(tmp_path))
        baseline = make_result(average_score=0.5)
        comparison = make_result(average_score=0.4, model_version="v2")
        report = suite.compare_results(baseline, comparison)
        j = report.to_json()
        loaded = json.loads(j)
        assert "verdict" in loaded

    def test_generate_summary_report_empty(self, tmp_path):
        suite = BenchmarkSuite(results_dir=str(tmp_path))
        report = suite.generate_summary_report([])
        assert "error" in report

    def test_generate_summary_report_with_results(self, tmp_path):
        suite = BenchmarkSuite(results_dir=str(tmp_path))
        results = [make_result(average_score=0.3), make_result(average_score=0.5)]
        report = suite.generate_summary_report(results)
        assert report["total_runs"] == 2
