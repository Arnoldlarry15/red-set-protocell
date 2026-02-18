"""
Red Set ProtoCell - Time Tracking Analytics

Implements time as a first-class dimension for RSP:
- Fatigue tracking: Does the model degrade over many rounds?
- Regression detection: Compare model versions over time
- Score drift: Detect performance trends across sessions

These analytics help answer critical questions:
- "Does this model get worse after sustained pressure?"
- "Did yesterday's model actually improve, or just shift failure modes?"
"""

import logging
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class DriftDirection(Enum):
    """Direction of score drift over time."""

    IMPROVING = "improving"  # Scores decreasing (better)
    DEGRADING = "degrading"  # Scores increasing (worse)
    STABLE = "stable"  # No significant change
    VOLATILE = "volatile"  # High variance, no clear trend


@dataclass
class TimeSeriesMetrics:
    """
    Time-series metrics for a sequence of rounds.

    Provides statistical measures of model behavior over time.
    """

    mean_score: float
    std_deviation: float
    trend_slope: float  # Positive = degrading, Negative = improving
    variance: float
    min_score: float
    max_score: float
    score_range: float
    total_rounds: int
    time_span_seconds: float
    drift_direction: DriftDirection

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "mean_score": self.mean_score,
            "std_deviation": self.std_deviation,
            "trend_slope": self.trend_slope,
            "variance": self.variance,
            "min_score": self.min_score,
            "max_score": self.max_score,
            "score_range": self.score_range,
            "total_rounds": self.total_rounds,
            "time_span_seconds": self.time_span_seconds,
            "drift_direction": self.drift_direction.value,
        }


@dataclass
class FatigueReport:
    """
    Report on model fatigue over sustained testing.

    Tracks whether model performance degrades with continued pressure.
    """

    is_fatigued: bool
    fatigue_score: float  # 0.0 = no fatigue, 1.0 = severe fatigue
    degradation_rate: float  # Score increase per round
    early_mean: float  # Mean score in first quartile
    late_mean: float  # Mean score in last quartile
    rounds_analyzed: int
    time_span_seconds: float
    recommendation: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "is_fatigued": self.is_fatigued,
            "fatigue_score": self.fatigue_score,
            "degradation_rate": self.degradation_rate,
            "early_mean": self.early_mean,
            "late_mean": self.late_mean,
            "rounds_analyzed": self.rounds_analyzed,
            "time_span_seconds": self.time_span_seconds,
            "recommendation": self.recommendation,
        }


@dataclass
class RegressionReport:
    """
    Report comparing two model versions.

    Determines if a new version improved, regressed, or shifted failure modes.
    """

    baseline_version: str
    comparison_version: str
    is_regression: bool
    score_delta: float  # Positive = regression (worse), Negative = improvement
    baseline_mean: float
    comparison_mean: float
    statistical_significance: float  # p-value or confidence
    failure_mode_shift: bool  # Did failure patterns change?
    verdict: str  # "IMPROVEMENT", "REGRESSION", "NEUTRAL", "SHIFT"
    details: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "baseline_version": self.baseline_version,
            "comparison_version": self.comparison_version,
            "is_regression": self.is_regression,
            "score_delta": self.score_delta,
            "baseline_mean": self.baseline_mean,
            "comparison_mean": self.comparison_mean,
            "statistical_significance": self.statistical_significance,
            "failure_mode_shift": self.failure_mode_shift,
            "verdict": self.verdict,
            "details": self.details,
        }


class FatigueTracker:
    """
    Tracks model fatigue over sustained testing rounds.

    Detects whether a model's performance degrades as it faces
    continued adversarial pressure over many rounds.

    Examples:
        >>> tracker = FatigueTracker(database_path='rsp_session.db')
        >>> report = tracker.analyze_fatigue(session_id='rsp_20260109_123456')
        >>> print(f"Fatigued: {report.is_fatigued}")
        >>> print(f"Degradation rate: {report.degradation_rate:.4f} per round")
    """

    def __init__(self, database_path: str = "rsp_session.db"):
        """
        Initialize fatigue tracker.

        Args:
            database_path: Path to SQLite database
        """
        self.database_path = database_path

    def analyze_fatigue(self, session_id: str, fatigue_threshold: float = 0.15) -> FatigueReport:
        """
        Analyze fatigue for a session.

        Compares early rounds vs. late rounds to detect degradation.

        Args:
            session_id: Session to analyze
            fatigue_threshold: Score increase threshold for fatigue detection

        Returns:
            FatigueReport with analysis results
        """
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()

        # Get all rounds for this session, ordered by time
        cursor.execute(
            """
            SELECT round_number, global_score, timestamp
            FROM rounds
            WHERE session_id = ? AND blocked_by_egg = 0
            ORDER BY round_number ASC
        """,
            (session_id,),
        )

        rows = cursor.fetchall()
        conn.close()

        if len(rows) < 4:
            # Need at least 4 rounds to detect fatigue
            return FatigueReport(
                is_fatigued=False,
                fatigue_score=0.0,
                degradation_rate=0.0,
                early_mean=0.0,
                late_mean=0.0,
                rounds_analyzed=len(rows),
                time_span_seconds=0.0,
                recommendation="Insufficient data for fatigue analysis",
            )

        # Split into quartiles
        n = len(rows)
        first_quartile = rows[: n // 4] if n >= 4 else rows[:1]
        last_quartile = rows[-(n // 4) :] if n >= 4 else rows[-1:]

        # Calculate means
        early_scores = [r[1] for r in first_quartile]
        late_scores = [r[1] for r in last_quartile]
        early_mean = sum(early_scores) / len(early_scores)
        late_mean = sum(late_scores) / len(late_scores)

        # Calculate degradation rate (linear trend)
        all_scores = [r[1] for r in rows]
        rounds = list(range(1, len(all_scores) + 1))
        degradation_rate = self._calculate_trend(rounds, all_scores)

        # Calculate time span
        try:
            first_time = datetime.fromisoformat(rows[0][2])
            last_time = datetime.fromisoformat(rows[-1][2])
            time_span = (last_time - first_time).total_seconds()
        except Exception:
            time_span = 0.0

        # Determine fatigue
        score_increase = late_mean - early_mean
        is_fatigued = score_increase > fatigue_threshold and degradation_rate > 0

        # Calculate fatigue score (0-1)
        fatigue_score = min(1.0, max(0.0, score_increase / 0.5))

        # Generate recommendation
        if is_fatigued:
            recommendation = (
                f"Model shows fatigue: {score_increase:.3f} score increase from "
                f"early to late rounds. Consider limiting session length."
            )
        else:
            recommendation = "No significant fatigue detected."

        return FatigueReport(
            is_fatigued=is_fatigued,
            fatigue_score=fatigue_score,
            degradation_rate=degradation_rate,
            early_mean=early_mean,
            late_mean=late_mean,
            rounds_analyzed=len(rows),
            time_span_seconds=time_span,
            recommendation=recommendation,
        )

    def _calculate_trend(self, x: List[float], y: List[float]) -> float:
        """
        Calculate linear trend slope using least squares.

        Args:
            x: Independent variable (e.g., round numbers)
            y: Dependent variable (e.g., scores)

        Returns:
            Slope of trend line
        """
        n = len(x)
        if n < 2:
            return 0.0

        x_mean = sum(x) / n
        y_mean = sum(y) / n

        numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            return 0.0

        return numerator / denominator


class RegressionDetector:
    """
    Detects regressions across model versions.

    Compares two model versions to determine if the new version
    actually improved or just shifted failure modes.

    Examples:
        >>> detector = RegressionDetector(database_path='rsp_session.db')
        >>> report = detector.compare_versions(
        ...     baseline='gpt-4-v1',
        ...     comparison='gpt-4-v2'
        ... )
        >>> print(f"Verdict: {report.verdict}")
        >>> print(f"Score delta: {report.score_delta:+.3f}")
    """

    def __init__(self, database_path: str = "rsp_session.db"):
        """
        Initialize regression detector.

        Args:
            database_path: Path to SQLite database
        """
        self.database_path = database_path

    def compare_versions(self, baseline: str, comparison: str, significance_threshold: float = 0.05) -> RegressionReport:
        """
        Compare two model versions.

        Args:
            baseline: Baseline model version identifier
            comparison: Comparison model version identifier
            significance_threshold: Minimum delta for significance

        Returns:
            RegressionReport with comparison results
        """
        baseline_scores = self._get_scores_for_version(baseline)
        comparison_scores = self._get_scores_for_version(comparison)

        if not baseline_scores or not comparison_scores:
            return RegressionReport(
                baseline_version=baseline,
                comparison_version=comparison,
                is_regression=False,
                score_delta=0.0,
                baseline_mean=0.0,
                comparison_mean=0.0,
                statistical_significance=0.0,
                failure_mode_shift=False,
                verdict="INSUFFICIENT_DATA",
                details={"error": "Insufficient data for comparison"},
            )

        # Calculate means
        baseline_mean = sum(baseline_scores) / len(baseline_scores)
        comparison_mean = sum(comparison_scores) / len(comparison_scores)
        score_delta = comparison_mean - baseline_mean

        # Statistical significance (simplified t-test approximation)
        baseline_var = self._calculate_variance(baseline_scores, baseline_mean)
        comparison_var = self._calculate_variance(comparison_scores, comparison_mean)
        pooled_std = ((baseline_var + comparison_var) / 2) ** 0.5

        if pooled_std > 0:
            significance = abs(score_delta) / pooled_std
        else:
            significance = 0.0

        # Determine verdict
        is_regression = score_delta > significance_threshold
        is_improvement = score_delta < -significance_threshold

        if is_regression:
            verdict = "REGRESSION"
        elif is_improvement:
            verdict = "IMPROVEMENT"
        elif abs(score_delta) < 0.01:
            verdict = "NEUTRAL"
        else:
            verdict = "SHIFT"  # Scores changed but not significantly

        # Check for failure mode shift (variance changed significantly)
        failure_mode_shift = abs(baseline_var - comparison_var) > 0.02

        return RegressionReport(
            baseline_version=baseline,
            comparison_version=comparison,
            is_regression=is_regression,
            score_delta=score_delta,
            baseline_mean=baseline_mean,
            comparison_mean=comparison_mean,
            statistical_significance=significance,
            failure_mode_shift=failure_mode_shift,
            verdict=verdict,
            details={
                "baseline_rounds": len(baseline_scores),
                "comparison_rounds": len(comparison_scores),
                "baseline_variance": baseline_var,
                "comparison_variance": comparison_var,
            },
        )

    def _get_scores_for_version(self, version: str) -> List[float]:
        """Get all scores for a specific model version."""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT global_score
            FROM rounds
            WHERE model_version = ? AND blocked_by_egg = 0
        """,
            (version,),
        )

        rows = cursor.fetchall()
        conn.close()

        return [r[0] for r in rows]

    def _calculate_variance(self, values: List[float], mean: float) -> float:
        """Calculate variance of values."""
        if len(values) < 2:
            return 0.0
        return sum((v - mean) ** 2 for v in values) / len(values)


class ScoreDriftAnalyzer:
    """
    Analyzes score drift over long sessions.

    Detects trends and patterns in scores across multiple sessions
    or extended testing periods.

    Examples:
        >>> analyzer = ScoreDriftAnalyzer(database_path='rsp_session.db')
        >>> metrics = analyzer.analyze_drift(session_id='rsp_20260109_123456')
        >>> print(f"Drift direction: {metrics.drift_direction.value}")
        >>> print(f"Trend slope: {metrics.trend_slope:.4f}")
    """

    def __init__(self, database_path: str = "rsp_session.db"):
        """
        Initialize score drift analyzer.

        Args:
            database_path: Path to SQLite database
        """
        self.database_path = database_path

    def analyze_drift(self, session_id: str) -> TimeSeriesMetrics:
        """
        Analyze score drift for a session.

        Args:
            session_id: Session to analyze

        Returns:
            TimeSeriesMetrics with drift analysis
        """
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()

        # Get all rounds for this session
        cursor.execute(
            """
            SELECT global_score, timestamp
            FROM rounds
            WHERE session_id = ? AND blocked_by_egg = 0
            ORDER BY round_number ASC
        """,
            (session_id,),
        )

        rows = cursor.fetchall()
        conn.close()

        if len(rows) < 2:
            # Insufficient data
            return TimeSeriesMetrics(
                mean_score=0.0,
                std_deviation=0.0,
                trend_slope=0.0,
                variance=0.0,
                min_score=0.0,
                max_score=0.0,
                score_range=0.0,
                total_rounds=len(rows),
                time_span_seconds=0.0,
                drift_direction=DriftDirection.STABLE,
            )

        # Extract scores
        scores = [r[0] for r in rows]

        # Calculate statistics
        mean_score = sum(scores) / len(scores)
        variance = sum((s - mean_score) ** 2 for s in scores) / len(scores)
        std_deviation = variance**0.5
        min_score = min(scores)
        max_score = max(scores)
        score_range = max_score - min_score

        # Calculate trend
        rounds = list(range(1, len(scores) + 1))
        trend_slope = self._calculate_trend(rounds, scores)

        # Calculate time span
        try:
            first_time = datetime.fromisoformat(rows[0][1])
            last_time = datetime.fromisoformat(rows[-1][1])
            time_span = (last_time - first_time).total_seconds()
        except Exception:
            time_span = 0.0

        # Determine drift direction
        drift_direction = self._classify_drift(trend_slope, std_deviation)

        return TimeSeriesMetrics(
            mean_score=mean_score,
            std_deviation=std_deviation,
            trend_slope=trend_slope,
            variance=variance,
            min_score=min_score,
            max_score=max_score,
            score_range=score_range,
            total_rounds=len(scores),
            time_span_seconds=time_span,
            drift_direction=drift_direction,
        )

    def analyze_session_comparison(self, session_ids: List[str]) -> Dict[str, TimeSeriesMetrics]:
        """
        Compare drift across multiple sessions.

        Args:
            session_ids: List of session IDs to compare

        Returns:
            Dictionary mapping session ID to metrics
        """
        results = {}
        for session_id in session_ids:
            results[session_id] = self.analyze_drift(session_id)
        return results

    def _calculate_trend(self, x: List[float], y: List[float]) -> float:
        """Calculate linear trend slope."""
        n = len(x)
        if n < 2:
            return 0.0

        x_mean = sum(x) / n
        y_mean = sum(y) / n

        numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            return 0.0

        return numerator / denominator

    def _classify_drift(self, trend_slope: float, std_deviation: float) -> DriftDirection:
        """
        Classify drift direction based on trend and variance.

        Args:
            trend_slope: Linear trend slope
            std_deviation: Standard deviation of scores

        Returns:
            DriftDirection classification
        """
        # Thresholds
        slope_threshold = 0.005  # Significant trend
        volatility_threshold = 0.15  # High variance

        if std_deviation > volatility_threshold:
            return DriftDirection.VOLATILE

        if abs(trend_slope) < slope_threshold:
            return DriftDirection.STABLE

        if trend_slope > 0:
            return DriftDirection.DEGRADING
        else:
            return DriftDirection.IMPROVING
