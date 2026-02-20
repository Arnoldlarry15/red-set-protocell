"""
Tests for time-based analytics features.

Tests fatigue tracking, regression detection, and score drift analysis.
"""

import sqlite3
import tempfile
from datetime import datetime, timedelta

import pytest

from app.analytics.time_tracking import (
    DriftDirection,
    FatigueReport,
    FatigueTracker,
    RegressionDetector,
    RegressionReport,
    ScoreDriftAnalyzer,
    TimeSeriesMetrics,
)


@pytest.fixture
def temp_database():
    """Create a temporary database for testing."""
    temp_file = tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".db")
    db_path = temp_file.name
    temp_file.close()

    # Initialize database schema
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE rounds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            round_number INTEGER NOT NULL,
            prompt TEXT NOT NULL,
            attack_domain TEXT NOT NULL,
            target_response TEXT NOT NULL,
            evaluation TEXT NOT NULL,
            global_score REAL NOT NULL,
            blocked_by_egg INTEGER NOT NULL,
            timestamp TEXT NOT NULL,
            model_version TEXT DEFAULT 'unknown',
            session_start_time TEXT
        )
    """)

    conn.commit()
    conn.close()

    yield db_path

    # Cleanup
    import os

    os.unlink(db_path)


def insert_test_rounds(db_path, session_id, scores, model_version="test-model-v1"):
    """Helper to insert test rounds with increasing timestamps."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    base_time = datetime(2026, 1, 9, 10, 0, 0)

    for i, score in enumerate(scores):
        timestamp = (base_time + timedelta(minutes=i * 2)).isoformat()
        cursor.execute(
            """
            INSERT INTO rounds (
                session_id, round_number, prompt, attack_domain,
                target_response, evaluation, global_score,
                blocked_by_egg, timestamp, model_version
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                session_id,
                i + 1,
                f"test prompt {i}",
                "injection",
                f"test response {i}",
                "{}",
                score,
                0,
                timestamp,
                model_version,
            ),
        )

    conn.commit()
    conn.close()


def test_fatigue_tracker_no_fatigue(temp_database):
    """Test fatigue detection when scores remain stable."""
    session_id = "test_session_stable"
    # Stable scores around 0.3
    scores = [0.3, 0.31, 0.29, 0.32, 0.28, 0.30, 0.31, 0.29]
    insert_test_rounds(temp_database, session_id, scores)

    tracker = FatigueTracker(temp_database)
    report = tracker.analyze_fatigue(session_id)

    assert isinstance(report, FatigueReport)
    assert not report.is_fatigued
    assert report.fatigue_score < 0.5
    assert report.rounds_analyzed == len(scores)
    assert "No significant fatigue" in report.recommendation


def test_fatigue_tracker_with_fatigue(temp_database):
    """Test fatigue detection when scores increase over time."""
    session_id = "test_session_fatigued"
    # Scores increasing from 0.2 to 0.6 (degradation)
    scores = [0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6]
    insert_test_rounds(temp_database, session_id, scores)

    tracker = FatigueTracker(temp_database)
    report = tracker.analyze_fatigue(session_id)

    assert report.is_fatigued
    assert report.degradation_rate > 0
    assert report.late_mean > report.early_mean
    assert "fatigue" in report.recommendation.lower()


def test_fatigue_tracker_insufficient_data(temp_database):
    """Test fatigue tracker with insufficient rounds."""
    session_id = "test_session_small"
    scores = [0.3, 0.4]  # Only 2 rounds
    insert_test_rounds(temp_database, session_id, scores)

    tracker = FatigueTracker(temp_database)
    report = tracker.analyze_fatigue(session_id)

    assert not report.is_fatigued
    assert "Insufficient data" in report.recommendation


def test_regression_detector_improvement(temp_database):
    """Test regression detector with improved model."""
    # Baseline model with higher scores (worse)
    baseline_scores = [0.5, 0.52, 0.48, 0.51, 0.49, 0.50]
    insert_test_rounds(temp_database, "session1", baseline_scores, "model-v1")

    # New model with lower scores (better)
    comparison_scores = [0.3, 0.32, 0.28, 0.31, 0.29, 0.30]
    insert_test_rounds(temp_database, "session2", comparison_scores, "model-v2")

    detector = RegressionDetector(temp_database)
    report = detector.compare_versions("model-v1", "model-v2")

    assert isinstance(report, RegressionReport)
    assert not report.is_regression
    assert report.verdict == "IMPROVEMENT"
    assert report.score_delta < 0  # Negative means improvement
    assert report.comparison_mean < report.baseline_mean


def test_regression_detector_regression(temp_database):
    """Test regression detector with regressed model."""
    # Baseline model with lower scores (better)
    baseline_scores = [0.3, 0.32, 0.28, 0.31, 0.29, 0.30]
    insert_test_rounds(temp_database, "session1", baseline_scores, "model-v1")

    # New model with higher scores (worse)
    comparison_scores = [0.5, 0.52, 0.48, 0.51, 0.49, 0.50]
    insert_test_rounds(temp_database, "session2", comparison_scores, "model-v2")

    detector = RegressionDetector(temp_database)
    report = detector.compare_versions("model-v1", "model-v2")

    assert report.is_regression
    assert report.verdict == "REGRESSION"
    assert report.score_delta > 0.05  # Significant regression


def test_regression_detector_neutral(temp_database):
    """Test regression detector with neutral change."""
    # Very similar scores
    baseline_scores = [0.3, 0.32, 0.31, 0.30]
    insert_test_rounds(temp_database, "session1", baseline_scores, "model-v1")

    comparison_scores = [0.305, 0.315, 0.295, 0.305]
    insert_test_rounds(temp_database, "session2", comparison_scores, "model-v2")

    detector = RegressionDetector(temp_database)
    report = detector.compare_versions("model-v1", "model-v2")

    assert not report.is_regression
    assert report.verdict in ["NEUTRAL", "SHIFT"]


def test_score_drift_analyzer_stable(temp_database):
    """Test drift analyzer with stable scores."""
    session_id = "test_drift_stable"
    scores = [0.3] * 10  # Perfectly stable
    insert_test_rounds(temp_database, session_id, scores)

    analyzer = ScoreDriftAnalyzer(temp_database)
    metrics = analyzer.analyze_drift(session_id)

    assert isinstance(metrics, TimeSeriesMetrics)
    assert metrics.drift_direction == DriftDirection.STABLE
    assert abs(metrics.trend_slope) < 0.005
    assert metrics.mean_score == pytest.approx(0.3, abs=0.01)


def test_score_drift_analyzer_degrading(temp_database):
    """Test drift analyzer with degrading scores."""
    session_id = "test_drift_degrading"
    # Scores increasing linearly
    scores = [0.2 + i * 0.05 for i in range(10)]
    insert_test_rounds(temp_database, session_id, scores)

    analyzer = ScoreDriftAnalyzer(temp_database)
    metrics = analyzer.analyze_drift(session_id)

    assert metrics.drift_direction == DriftDirection.DEGRADING
    assert metrics.trend_slope > 0.005
    assert metrics.max_score > metrics.min_score


def test_score_drift_analyzer_improving(temp_database):
    """Test drift analyzer with improving scores."""
    session_id = "test_drift_improving"
    # Scores decreasing linearly
    scores = [0.6 - i * 0.05 for i in range(10)]
    insert_test_rounds(temp_database, session_id, scores)

    analyzer = ScoreDriftAnalyzer(temp_database)
    metrics = analyzer.analyze_drift(session_id)

    assert metrics.drift_direction == DriftDirection.IMPROVING
    assert metrics.trend_slope < -0.005


def test_score_drift_analyzer_volatile(temp_database):
    """Test drift analyzer with volatile scores."""
    session_id = "test_drift_volatile"
    # High variance, no clear trend
    scores = [0.3, 0.6, 0.2, 0.7, 0.25, 0.65, 0.3, 0.6, 0.28, 0.62]
    insert_test_rounds(temp_database, session_id, scores)

    analyzer = ScoreDriftAnalyzer(temp_database)
    metrics = analyzer.analyze_drift(session_id)

    assert metrics.drift_direction == DriftDirection.VOLATILE
    assert metrics.std_deviation > 0.15


def test_score_drift_analyzer_multiple_sessions(temp_database):
    """Test comparing drift across multiple sessions."""
    # Session 1: Stable
    insert_test_rounds(temp_database, "session1", [0.3] * 10)

    # Session 2: Degrading
    insert_test_rounds(temp_database, "session2", [0.2 + i * 0.05 for i in range(10)])

    analyzer = ScoreDriftAnalyzer(temp_database)
    results = analyzer.analyze_session_comparison(["session1", "session2"])

    assert len(results) == 2
    assert "session1" in results
    assert "session2" in results
    assert results["session1"].drift_direction == DriftDirection.STABLE
    assert results["session2"].drift_direction == DriftDirection.DEGRADING


def test_time_series_metrics_to_dict(temp_database):
    """Test TimeSeriesMetrics serialization."""
    session_id = "test_serialization"
    scores = [0.3, 0.32, 0.31, 0.30]
    insert_test_rounds(temp_database, session_id, scores)

    analyzer = ScoreDriftAnalyzer(temp_database)
    metrics = analyzer.analyze_drift(session_id)

    data = metrics.to_dict()
    assert isinstance(data, dict)
    assert "mean_score" in data
    assert "trend_slope" in data
    assert "drift_direction" in data
    assert data["drift_direction"] in ["improving", "degrading", "stable", "volatile"]


def test_fatigue_report_to_dict(temp_database):
    """Test FatigueReport serialization."""
    session_id = "test_fatigue_dict"
    scores = [0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55]
    insert_test_rounds(temp_database, session_id, scores)

    tracker = FatigueTracker(temp_database)
    report = tracker.analyze_fatigue(session_id)

    data = report.to_dict()
    assert isinstance(data, dict)
    assert "is_fatigued" in data
    assert "fatigue_score" in data
    assert "degradation_rate" in data
    assert isinstance(data["is_fatigued"], bool)


def test_regression_report_to_dict(temp_database):
    """Test RegressionReport serialization."""
    baseline_scores = [0.5, 0.52, 0.48]
    insert_test_rounds(temp_database, "s1", baseline_scores, "v1")

    comparison_scores = [0.3, 0.32, 0.28]
    insert_test_rounds(temp_database, "s2", comparison_scores, "v2")

    detector = RegressionDetector(temp_database)
    report = detector.compare_versions("v1", "v2")

    data = report.to_dict()
    assert isinstance(data, dict)
    assert "verdict" in data
    assert "score_delta" in data
    assert "is_regression" in data
    assert isinstance(data["is_regression"], bool)


def test_edge_case_empty_session(temp_database):
    """Test analytics with empty session."""
    tracker = FatigueTracker(temp_database)
    report = tracker.analyze_fatigue("nonexistent_session")

    assert not report.is_fatigued
    assert report.rounds_analyzed == 0


def test_edge_case_single_round(temp_database):
    """Test analytics with only one round."""
    session_id = "single_round"
    insert_test_rounds(temp_database, session_id, [0.5])

    analyzer = ScoreDriftAnalyzer(temp_database)
    metrics = analyzer.analyze_drift(session_id)

    assert metrics.total_rounds == 1
    assert metrics.trend_slope == 0.0


def test_blocked_rounds_excluded(temp_database):
    """Test that blocked rounds are excluded from analysis."""
    conn = sqlite3.connect(temp_database)
    cursor = conn.cursor()

    session_id = "test_blocked"
    base_time = datetime(2026, 1, 9, 10, 0, 0)

    # Insert mix of blocked and unblocked rounds
    for i in range(6):
        blocked = 1 if i % 2 == 0 else 0  # Every other round blocked
        timestamp = (base_time + timedelta(minutes=i * 2)).isoformat()
        cursor.execute(
            """
            INSERT INTO rounds (
                session_id, round_number, prompt, attack_domain,
                target_response, evaluation, global_score,
                blocked_by_egg, timestamp, model_version
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (session_id, i + 1, f"prompt {i}", "injection", f"response {i}", "{}", 0.3, blocked, timestamp, "test"),
        )

    conn.commit()
    conn.close()

    tracker = FatigueTracker(temp_database)
    report = tracker.analyze_fatigue(session_id)

    # Should only count unblocked rounds (3 rounds)
    assert report.rounds_analyzed == 3
