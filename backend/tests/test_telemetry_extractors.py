"""
Tests for telemetry extractors module.
"""

import sqlite3
import tempfile
from pathlib import Path

import pytest

from app.telemetry.extractors import (
    RoundMetricsExtractor,
    SessionDataExtractor,
    SessionMetricsExtractor,
)


def _create_test_db(path: str) -> None:
    """Create a test SQLite database with sample data."""
    conn = sqlite3.connect(path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE sessions (
            session_id TEXT PRIMARY KEY,
            timestamp TEXT,
            max_rounds INTEGER,
            zero_retention INTEGER,
            model_version TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE rounds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            round_number INTEGER,
            attack_domain TEXT,
            global_score REAL,
            blocked_by_egg INTEGER,
            timestamp TEXT,
            prompt TEXT,
            target_response TEXT,
            evaluation TEXT,
            model_version TEXT
        )
    """)

    # Insert test session
    cursor.execute(
        "INSERT INTO sessions VALUES (?, ?, ?, ?, ?)",
        ("sess_001", "2024-01-01T00:00:00", 10, 0, "gpt-4"),
    )
    cursor.execute(
        "INSERT INTO sessions VALUES (?, ?, ?, ?, ?)",
        ("sess_002", "2024-01-02T00:00:00", 5, 1, "claude-3"),
    )

    # Insert test rounds
    rounds_data = [
        ("sess_001", 1, "jailbreak", 0.85, 0, "2024-01-01T00:01:00", "prompt1", "resp1", "eval1", "gpt-4"),
        ("sess_001", 2, "bias", 0.45, 0, "2024-01-01T00:02:00", "prompt2", "resp2", "eval2", "gpt-4"),
        ("sess_001", 3, "harmful", 0.95, 1, "2024-01-01T00:03:00", "prompt3", "resp3", "eval3", "gpt-4"),
        ("sess_001", 4, "jailbreak", 0.25, 0, "2024-01-01T00:04:00", "prompt4", "resp4", "eval4", "gpt-4"),
        ("sess_002", 1, "bias", 0.65, 0, "2024-01-02T00:01:00", "prompt5", "resp5", "eval5", "claude-3"),
        ("sess_002", 2, "harmful", 0.35, 0, "2024-01-02T00:02:00", "prompt6", "resp6", "eval6", "claude-3"),
    ]
    cursor.executemany(
        "INSERT INTO rounds (session_id, round_number, attack_domain, global_score, blocked_by_egg, "
        "timestamp, prompt, target_response, evaluation, model_version) VALUES (?,?,?,?,?,?,?,?,?,?)",
        rounds_data,
    )

    conn.commit()
    conn.close()


# ── SessionMetricsExtractor ──────────────────────────────────────────────────


class TestSessionMetricsExtractor:
    def test_extract_session_metrics(self, tmp_path):
        db_path = str(tmp_path / "test.db")
        _create_test_db(db_path)
        extractor = SessionMetricsExtractor(database_path=db_path)

        metrics = extractor.extract_session_metrics("sess_001")

        assert metrics["session_id"] == "sess_001"
        assert metrics["model_version"] == "gpt-4"
        assert metrics["total_rounds"] == 4
        assert metrics["blocked_count"] == 1
        assert metrics["critical_findings"] == 2  # scores >= 0.8
        assert metrics["average_score"] > 0

    def test_extract_session_metrics_not_found(self, tmp_path):
        db_path = str(tmp_path / "test.db")
        _create_test_db(db_path)
        extractor = SessionMetricsExtractor(database_path=db_path)

        metrics = extractor.extract_session_metrics("nonexistent")
        assert metrics == {}

    def test_extract_session_metrics_db_error(self, tmp_path):
        extractor = SessionMetricsExtractor(database_path="/nonexistent/path/db.sqlite")
        metrics = extractor.extract_session_metrics("sess_001")
        assert metrics == {}

    def test_list_sessions(self, tmp_path):
        db_path = str(tmp_path / "test.db")
        _create_test_db(db_path)
        extractor = SessionMetricsExtractor(database_path=db_path)

        sessions = extractor.list_sessions()
        assert len(sessions) == 2
        # Most recent first
        assert sessions[0]["session_id"] == "sess_002"

    def test_list_sessions_filter_by_model(self, tmp_path):
        db_path = str(tmp_path / "test.db")
        _create_test_db(db_path)
        extractor = SessionMetricsExtractor(database_path=db_path)

        sessions = extractor.list_sessions(model_version="gpt-4")
        assert len(sessions) == 1
        assert sessions[0]["session_id"] == "sess_001"

    def test_list_sessions_with_limit(self, tmp_path):
        db_path = str(tmp_path / "test.db")
        _create_test_db(db_path)
        extractor = SessionMetricsExtractor(database_path=db_path)

        sessions = extractor.list_sessions(limit=1)
        assert len(sessions) == 1

    def test_list_sessions_db_error(self, tmp_path):
        extractor = SessionMetricsExtractor(database_path="/nonexistent/path/db.sqlite")
        sessions = extractor.list_sessions()
        assert sessions == []

    def test_session_metrics_zero_retention(self, tmp_path):
        db_path = str(tmp_path / "test.db")
        _create_test_db(db_path)
        extractor = SessionMetricsExtractor(database_path=db_path)

        metrics = extractor.extract_session_metrics("sess_002")
        assert metrics["zero_retention"] is True

    def test_session_metrics_score_buckets(self, tmp_path):
        db_path = str(tmp_path / "test.db")
        _create_test_db(db_path)
        extractor = SessionMetricsExtractor(database_path=db_path)

        metrics = extractor.extract_session_metrics("sess_001")
        # sess_001 has scores: 0.85, 0.45, 0.95, 0.25
        assert metrics["critical_findings"] == 2  # 0.85, 0.95 >= 0.8
        assert metrics["high_findings"] == 0  # none in [0.6, 0.8)
        assert metrics["medium_findings"] == 1  # 0.45 in [0.4, 0.6)
        assert metrics["low_findings"] == 1  # 0.25 in [0.2, 0.4)

    def test_session_metrics_with_no_rounds(self, tmp_path):
        """Test session metrics when a session has no rounds (round_stats is empty)."""
        import sqlite3

        db_path = str(tmp_path / "empty_rounds.db")
        _create_test_db(db_path)

        # Add a session with no rounds
        conn = sqlite3.connect(db_path)
        conn.execute(
            "INSERT INTO sessions VALUES (?, ?, ?, ?, ?)",
            ("empty_session", "2024-01-03T00:00:00", 5, 0, "gpt-4"),
        )
        conn.commit()
        conn.close()

        extractor = SessionMetricsExtractor(database_path=db_path)
        metrics = extractor.extract_session_metrics("empty_session")

        # Session is found but no round stats
        assert metrics["session_id"] == "empty_session"

        db_path = str(tmp_path / "test.db")
        _create_test_db(db_path)
        extractor = SessionMetricsExtractor(database_path=db_path)

        sessions = extractor.list_sessions()
        for session in sessions:
            assert "session_id" in session
            assert "timestamp" in session
            assert "model_version" in session
            assert "round_count" in session
            assert "average_score" in session


# ── RoundMetricsExtractor ────────────────────────────────────────────────────


class TestRoundMetricsExtractor:
    def test_extract_round_metrics(self, tmp_path):
        db_path = str(tmp_path / "test.db")
        _create_test_db(db_path)
        extractor = RoundMetricsExtractor(database_path=db_path)

        rounds = extractor.extract_round_metrics("sess_001")
        assert len(rounds) == 4
        assert rounds[0]["round_number"] == 1
        assert rounds[0]["attack_domain"] == "jailbreak"
        assert rounds[0]["global_score"] == pytest.approx(0.85)
        assert rounds[0]["blocked_by_egg"] is False

    def test_extract_round_metrics_specific_round(self, tmp_path):
        db_path = str(tmp_path / "test.db")
        _create_test_db(db_path)
        extractor = RoundMetricsExtractor(database_path=db_path)

        rounds = extractor.extract_round_metrics("sess_001", round_number=3)
        assert len(rounds) == 1
        assert rounds[0]["round_number"] == 3
        assert rounds[0]["blocked_by_egg"] is True

    def test_extract_round_metrics_empty(self, tmp_path):
        db_path = str(tmp_path / "test.db")
        _create_test_db(db_path)
        extractor = RoundMetricsExtractor(database_path=db_path)

        rounds = extractor.extract_round_metrics("nonexistent")
        assert rounds == []

    def test_extract_round_metrics_db_error(self):
        extractor = RoundMetricsExtractor(database_path="/nonexistent/path/db.sqlite")
        rounds = extractor.extract_round_metrics("sess_001")
        assert rounds == []

    def test_extract_time_series(self, tmp_path):
        db_path = str(tmp_path / "test.db")
        _create_test_db(db_path)
        extractor = RoundMetricsExtractor(database_path=db_path)

        ts = extractor.extract_time_series("sess_001")
        assert len(ts["round_numbers"]) == 4
        assert len(ts["scores"]) == 4
        assert len(ts["timestamps"]) == 4
        assert len(ts["domains"]) == 4

    def test_extract_time_series_empty(self, tmp_path):
        db_path = str(tmp_path / "test.db")
        _create_test_db(db_path)
        extractor = RoundMetricsExtractor(database_path=db_path)

        ts = extractor.extract_time_series("nonexistent")
        assert ts == {"round_numbers": [], "scores": [], "timestamps": [], "domains": []}


# ── SessionDataExtractor ─────────────────────────────────────────────────────


class TestSessionDataExtractor:
    def test_get_all_sessions(self, tmp_path):
        db_path = str(tmp_path / "test.db")
        _create_test_db(db_path)
        extractor = SessionDataExtractor(database_path=db_path)

        sessions = extractor.get_all_sessions()
        assert len(sessions) == 2

    def test_get_all_sessions_with_limit(self, tmp_path):
        db_path = str(tmp_path / "test.db")
        _create_test_db(db_path)
        extractor = SessionDataExtractor(database_path=db_path)

        sessions = extractor.get_all_sessions(limit=1)
        assert len(sessions) == 1

    def test_get_all_sessions_structure(self, tmp_path):
        db_path = str(tmp_path / "test.db")
        _create_test_db(db_path)
        extractor = SessionDataExtractor(database_path=db_path)

        sessions = extractor.get_all_sessions()
        for s in sessions:
            assert "session_id" in s
            assert "start_time" in s
            assert "end_time" in s
            assert "total_rounds" in s
            assert "average_score" in s
            assert "blocked_count" in s
            assert "model_version" in s

    def test_get_all_sessions_db_error(self):
        extractor = SessionDataExtractor(database_path="/nonexistent/path/db.sqlite")
        sessions = extractor.get_all_sessions()
        assert sessions == []

    def test_get_sessions_by_model_version(self, tmp_path):
        db_path = str(tmp_path / "test.db")
        _create_test_db(db_path)
        extractor = SessionDataExtractor(database_path=db_path)

        sessions = extractor.get_sessions_by_model_version("gpt-4")
        assert len(sessions) == 1
        assert sessions[0]["session_id"] == "sess_001"

    def test_get_sessions_by_model_version_limit(self, tmp_path):
        db_path = str(tmp_path / "test.db")
        _create_test_db(db_path)
        extractor = SessionDataExtractor(database_path=db_path)

        sessions = extractor.get_sessions_by_model_version("gpt-4", limit=1)
        assert len(sessions) == 1

    def test_get_sessions_by_model_version_not_found(self, tmp_path):
        db_path = str(tmp_path / "test.db")
        _create_test_db(db_path)
        extractor = SessionDataExtractor(database_path=db_path)

        sessions = extractor.get_sessions_by_model_version("nonexistent-model")
        assert sessions == []

    def test_get_sessions_by_model_version_db_error(self):
        extractor = SessionDataExtractor(database_path="/nonexistent/path/db.sqlite")
        sessions = extractor.get_sessions_by_model_version("gpt-4")
        assert sessions == []

    def test_get_session_rounds(self, tmp_path):
        db_path = str(tmp_path / "test.db")
        _create_test_db(db_path)
        extractor = SessionDataExtractor(database_path=db_path)

        rounds = extractor.get_session_rounds("sess_001")
        assert len(rounds) == 4
        for r in rounds:
            assert r["session_id"] == "sess_001"
            assert "round_number" in r
            assert "prompt" in r
            assert "attack_domain" in r
            assert "target_response" in r
            assert "evaluation" in r
            assert "global_score" in r
            assert "blocked_by_egg" in r
            assert "timestamp" in r
            assert "model_version" in r

    def test_get_session_rounds_empty(self, tmp_path):
        db_path = str(tmp_path / "test.db")
        _create_test_db(db_path)
        extractor = SessionDataExtractor(database_path=db_path)

        rounds = extractor.get_session_rounds("nonexistent")
        assert rounds == []

    def test_get_session_rounds_db_error(self):
        extractor = SessionDataExtractor(database_path="/nonexistent/path/db.sqlite")
        rounds = extractor.get_session_rounds("sess_001")
        assert rounds == []
