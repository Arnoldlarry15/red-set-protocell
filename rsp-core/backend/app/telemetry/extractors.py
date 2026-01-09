"""
Red Set ProtoCell - Telemetry Extractors

Extract metrics from RSP sessions and rounds.
"""

import logging
import sqlite3
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class SessionMetricsExtractor:
    """
    Extract metrics from RSP sessions.
    
    Provides programmatic access to session-level metrics
    stored in the state database.
    """
    
    def __init__(self, database_path: str = "rsp_session.db"):
        """
        Initialize session metrics extractor.
        
        Args:
            database_path: Path to RSP session database
        """
        self.database_path = database_path
    
    def extract_session_metrics(self, session_id: str) -> Dict[str, Any]:
        """
        Extract all metrics for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Dictionary of session metrics
        """
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            # Get session info
            cursor.execute("""
                SELECT session_id, timestamp, max_rounds, zero_retention, model_version
                FROM sessions
                WHERE session_id = ?
            """, (session_id,))
            
            session_row = cursor.fetchone()
            if not session_row:
                logger.warning(f"Session not found: {session_id}")
                return {}
            
            session_info = {
                'session_id': session_row[0],
                'timestamp': session_row[1],
                'max_rounds': session_row[2],
                'zero_retention': bool(session_row[3]),
                'model_version': session_row[4],
            }
            
            # Get round statistics
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_rounds,
                    AVG(global_score) as avg_score,
                    MIN(global_score) as min_score,
                    MAX(global_score) as max_score,
                    SUM(CASE WHEN blocked_by_egg = 1 THEN 1 ELSE 0 END) as blocked_count,
                    SUM(CASE WHEN global_score >= 0.8 THEN 1 ELSE 0 END) as critical_count,
                    SUM(CASE WHEN global_score >= 0.6 AND global_score < 0.8 THEN 1 ELSE 0 END) as high_count,
                    SUM(CASE WHEN global_score >= 0.4 AND global_score < 0.6 THEN 1 ELSE 0 END) as medium_count,
                    SUM(CASE WHEN global_score >= 0.2 AND global_score < 0.4 THEN 1 ELSE 0 END) as low_count
                FROM rounds
                WHERE session_id = ?
            """, (session_id,))
            
            stats_row = cursor.fetchone()
            if stats_row:
                round_stats = {
                    'total_rounds': stats_row[0] or 0,
                    'average_score': float(stats_row[1]) if stats_row[1] else 0.0,
                    'min_score': float(stats_row[2]) if stats_row[2] else 0.0,
                    'max_score': float(stats_row[3]) if stats_row[3] else 0.0,
                    'blocked_count': stats_row[4] or 0,
                    'critical_findings': stats_row[5] or 0,
                    'high_findings': stats_row[6] or 0,
                    'medium_findings': stats_row[7] or 0,
                    'low_findings': stats_row[8] or 0,
                }
            else:
                round_stats = {}
            
            conn.close()
            
            return {
                **session_info,
                **round_stats,
            }
            
        except sqlite3.Error as e:
            logger.error(f"Database error extracting session metrics: {e}")
            return {}
    
    def list_sessions(
        self,
        model_version: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        List all sessions with summary metrics.
        
        Args:
            model_version: Optional filter by model version
            limit: Maximum number of sessions to return
            
        Returns:
            List of session summaries
        """
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            query = """
                SELECT 
                    s.session_id,
                    s.timestamp,
                    s.model_version,
                    COUNT(r.round_number) as round_count,
                    AVG(r.global_score) as avg_score
                FROM sessions s
                LEFT JOIN rounds r ON s.session_id = r.session_id
            """
            
            params = []
            if model_version:
                query += " WHERE s.model_version = ?"
                params.append(model_version)
            
            query += """
                GROUP BY s.session_id
                ORDER BY s.timestamp DESC
                LIMIT ?
            """
            params.append(limit)
            
            cursor.execute(query, params)
            
            sessions = []
            for row in cursor.fetchall():
                sessions.append({
                    'session_id': row[0],
                    'timestamp': row[1],
                    'model_version': row[2],
                    'round_count': row[3] or 0,
                    'average_score': float(row[4]) if row[4] else 0.0,
                })
            
            conn.close()
            return sessions
            
        except sqlite3.Error as e:
            logger.error(f"Database error listing sessions: {e}")
            return []


class RoundMetricsExtractor:
    """
    Extract metrics from individual rounds.
    
    Provides programmatic access to round-level metrics
    stored in the state database.
    """
    
    def __init__(self, database_path: str = "rsp_session.db"):
        """
        Initialize round metrics extractor.
        
        Args:
            database_path: Path to RSP session database
        """
        self.database_path = database_path
    
    def extract_round_metrics(
        self,
        session_id: str,
        round_number: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Extract metrics for rounds in a session.
        
        Args:
            session_id: Session identifier
            round_number: Optional specific round number
            
        Returns:
            List of round metrics
        """
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            query = """
                SELECT 
                    round_number,
                    attack_domain,
                    global_score,
                    blocked_by_egg,
                    timestamp
                FROM rounds
                WHERE session_id = ?
            """
            
            params = [session_id]
            if round_number is not None:
                query += " AND round_number = ?"
                params.append(round_number)
            
            query += " ORDER BY round_number"
            
            cursor.execute(query, params)
            
            rounds = []
            for row in cursor.fetchall():
                rounds.append({
                    'round_number': row[0],
                    'attack_domain': row[1],
                    'global_score': float(row[2]),
                    'blocked_by_egg': bool(row[3]),
                    'timestamp': row[4],
                })
            
            conn.close()
            return rounds
            
        except sqlite3.Error as e:
            logger.error(f"Database error extracting round metrics: {e}")
            return []
    
    def extract_time_series(
        self,
        session_id: str,
    ) -> Dict[str, List[Any]]:
        """
        Extract time series data for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Dictionary with time series arrays
        """
        rounds = self.extract_round_metrics(session_id)
        
        if not rounds:
            return {
                'round_numbers': [],
                'scores': [],
                'timestamps': [],
                'domains': [],
            }
        
        return {
            'round_numbers': [r['round_number'] for r in rounds],
            'scores': [r['global_score'] for r in rounds],
            'timestamps': [r['timestamp'] for r in rounds],
            'domains': [r['attack_domain'] for r in rounds],
        }


class SessionDataExtractor:
    """
    Extract complete session data for dashboard and analysis.
    
    Provides unified access to session and round data for
    the unified infra dashboard.
    """
    
    def __init__(self, database_path: str = "rsp_session.db"):
        """
        Initialize session data extractor.
        
        Args:
            database_path: Path to RSP session database
        """
        self.database_path = database_path
    
    def get_all_sessions(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get all sessions with their summary metrics.
        
        Args:
            limit: Maximum number of sessions to return
            
        Returns:
            List of session data dictionaries
        """
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            # Get unique session IDs from rounds table
            cursor.execute("""
                SELECT DISTINCT 
                    session_id,
                    MIN(timestamp) as start_time,
                    MAX(timestamp) as end_time,
                    COUNT(*) as total_rounds,
                    AVG(global_score) as average_score,
                    SUM(CASE WHEN blocked_by_egg = 1 THEN 1 ELSE 0 END) as blocked_count,
                    model_version
                FROM rounds
                GROUP BY session_id
                ORDER BY start_time DESC
                LIMIT ?
            """, (limit,))
            
            sessions = []
            for row in cursor.fetchall():
                sessions.append({
                    'session_id': row[0],
                    'start_time': row[1],
                    'end_time': row[2],
                    'total_rounds': row[3],
                    'average_score': float(row[4]) if row[4] else 0.0,
                    'blocked_count': row[5] or 0,
                    'model_version': row[6] or 'unknown',
                })
            
            conn.close()
            return sessions
            
        except sqlite3.Error as e:
            logger.error(f"Database error getting all sessions: {e}")
            return []
    
    def get_sessions_by_model_version(
        self,
        model_version: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get sessions for a specific model version.
        
        Args:
            model_version: Model version identifier
            limit: Maximum number of sessions to return
            
        Returns:
            List of session data dictionaries
        """
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT DISTINCT 
                    session_id,
                    MIN(timestamp) as start_time,
                    MAX(timestamp) as end_time,
                    COUNT(*) as total_rounds,
                    AVG(global_score) as average_score,
                    SUM(CASE WHEN blocked_by_egg = 1 THEN 1 ELSE 0 END) as blocked_count,
                    model_version
                FROM rounds
                WHERE model_version = ?
                GROUP BY session_id
                ORDER BY start_time DESC
                LIMIT ?
            """, (model_version, limit))
            
            sessions = []
            for row in cursor.fetchall():
                sessions.append({
                    'session_id': row[0],
                    'start_time': row[1],
                    'end_time': row[2],
                    'total_rounds': row[3],
                    'average_score': float(row[4]) if row[4] else 0.0,
                    'blocked_count': row[5] or 0,
                    'model_version': row[6],
                })
            
            conn.close()
            return sessions
            
        except sqlite3.Error as e:
            logger.error(f"Database error getting sessions by model: {e}")
            return []
    
    def get_session_rounds(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Get all rounds for a specific session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            List of round data dictionaries
        """
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    round_number,
                    prompt,
                    attack_domain,
                    target_response,
                    evaluation,
                    global_score,
                    blocked_by_egg,
                    timestamp,
                    model_version
                FROM rounds
                WHERE session_id = ?
                ORDER BY round_number
            """, (session_id,))
            
            rounds = []
            for row in cursor.fetchall():
                rounds.append({
                    'session_id': session_id,
                    'round_number': row[0],
                    'prompt': row[1],
                    'attack_domain': row[2],
                    'target_response': row[3],
                    'evaluation': row[4],
                    'global_score': float(row[5]),
                    'blocked_by_egg': bool(row[6]),
                    'timestamp': row[7],
                    'model_version': row[8] or 'unknown',
                })
            
            conn.close()
            return rounds
            
        except sqlite3.Error as e:
            logger.error(f"Database error getting session rounds: {e}")
            return []
