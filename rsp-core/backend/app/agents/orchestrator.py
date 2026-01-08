"""
Red Set ProtoCell - Orchestrator Agent

Control plane that manages the entire RSP lifecycle.

Authority:
- Round lifecycle management
- State persistence
- Agent invocation order
- Async task coordination

All agents are stateless and side-effect free by design.
"""

import asyncio
import logging
import sqlite3
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

from app.core.security import generate_session_id, sanitize_metadata
from app.engines.scoring import ScoringEngine

logger = logging.getLogger(__name__)


@dataclass
class RoundResult:
    """Result of a single round execution."""
    round_number: int
    prompt: str
    attack_domain: str
    target_response: str
    evaluation: Dict[str, Any]
    global_score: float
    blocked_by_egg: bool
    timestamp: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class StateManager:
    """
    Manages state persistence for the Orchestrator.
    
    Supports SQLite (default) and PostgreSQL backends.
    Implements Zero-Retention Policy when enabled.
    """
    
    def __init__(self, database_path: str = "rsp_session.db",
                 zero_retention: bool = True):
        """
        Initialize state manager.
        
        Args:
            database_path: Path to SQLite database
            zero_retention: Enable zero-retention policy
        """
        self.database_path = database_path
        self.zero_retention = zero_retention
        self.session_id = generate_session_id()
        
        # Initialize database
        self._init_database()
        
    def _init_database(self):
        """Initialize database schema."""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        # Create rounds table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rounds (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                round_number INTEGER NOT NULL,
                prompt TEXT NOT NULL,
                attack_domain TEXT NOT NULL,
                target_response TEXT NOT NULL,
                evaluation TEXT NOT NULL,
                global_score REAL NOT NULL,
                blocked_by_egg INTEGER NOT NULL,
                timestamp TEXT NOT NULL
            )
        ''')
        
        # Create metadata table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metadata (
                session_id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                config TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
        
        logger.info(f"State manager initialized - Session: {self.session_id}")
    
    def save_round(self, round_result: RoundResult):
        """Save round result to database."""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO rounds (
                session_id, round_number, prompt, attack_domain,
                target_response, evaluation, global_score, blocked_by_egg, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            self.session_id,
            round_result.round_number,
            round_result.prompt,
            round_result.attack_domain,
            round_result.target_response,
            json.dumps(round_result.evaluation),
            round_result.global_score,
            1 if round_result.blocked_by_egg else 0,
            round_result.timestamp
        ))
        
        conn.commit()
        conn.close()
    
    def get_prior_rounds(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieve prior round metadata.
        
        Args:
            limit: Maximum number of rounds to retrieve
            
        Returns:
            List of round metadata dictionaries
        """
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT round_number, attack_domain, global_score, timestamp
            FROM rounds
            WHERE session_id = ?
            ORDER BY round_number DESC
            LIMIT ?
        ''', (self.session_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                'round_number': row[0],
                'attack_domain': row[1],
                'global_score': row[2],
                'timestamp': row[3]
            }
            for row in rows
        ]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get aggregate statistics."""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        # Total rounds
        cursor.execute(
            'SELECT COUNT(*) FROM rounds WHERE session_id = ?',
            (self.session_id,)
        )
        total_rounds = cursor.fetchone()[0]
        
        # Average score
        cursor.execute(
            'SELECT AVG(global_score) FROM rounds WHERE session_id = ?',
            (self.session_id,)
        )
        avg_score = cursor.fetchone()[0] or 0.0
        
        # Blocked count
        cursor.execute(
            'SELECT COUNT(*) FROM rounds WHERE session_id = ? AND blocked_by_egg = 1',
            (self.session_id,)
        )
        blocked_count = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_rounds': total_rounds,
            'average_score': avg_score,
            'blocked_count': blocked_count,
            'session_id': self.session_id
        }
    
    def cleanup(self):
        """Cleanup session data (Zero-Retention Policy)."""
        if self.zero_retention:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute(
                'DELETE FROM rounds WHERE session_id = ?',
                (self.session_id,)
            )
            
            conn.commit()
            conn.close()
            
            logger.info(f"Zero-retention cleanup completed for session {self.session_id}")


class Orchestrator:
    """
    The Orchestrator is the control plane for the Red Set ProtoCell system.
    
    It has final authority over:
    - Execution flow
    - State persistence
    - Agent coordination
    - Round lifecycle
    """
    
    def __init__(self, sniper, target, spotter, egg, scoring_engine: ScoringEngine,
                 state_manager: StateManager, max_rounds: int = 100,
                 round_timeout: int = 300):
        """
        Initialize Orchestrator.
        
        Args:
            sniper: Sniper agent instance
            target: Target agent instance
            spotter: Spotter agent instance
            egg: Ethical Guardrail Governor instance
            scoring_engine: Scoring engine instance
            state_manager: State manager instance
            max_rounds: Maximum number of rounds
            round_timeout: Timeout per round in seconds
        """
        self.sniper = sniper
        self.target = target
        self.spotter = spotter
        self.egg = egg
        self.scoring_engine = scoring_engine
        self.state_manager = state_manager
        self.max_rounds = max_rounds
        self.round_timeout = round_timeout
        
        self.current_round = 0
        self.session_active = False
        
    async def run_session(self) -> Dict[str, Any]:
        """
        Run a complete RSP session.
        
        Returns:
            Session statistics and results
        """
        self.session_active = True
        logger.info(f"Starting RSP session - Max rounds: {self.max_rounds}")
        
        try:
            for round_num in range(1, self.max_rounds + 1):
                if not self.session_active:
                    logger.info("Session terminated early")
                    break
                
                self.current_round = round_num
                
                try:
                    # Execute round with timeout
                    result = await asyncio.wait_for(
                        self._execute_round(round_num),
                        timeout=self.round_timeout
                    )
                    
                    # Save result
                    self.state_manager.save_round(result)
                    
                    logger.info(
                        f"Round {round_num} completed - "
                        f"Score: {result.global_score:.3f}, "
                        f"Blocked: {result.blocked_by_egg}"
                    )
                    
                except asyncio.TimeoutError:
                    logger.error(f"Round {round_num} timed out")
                    continue
                except Exception as e:
                    logger.error(f"Round {round_num} failed: {e}")
                    continue
        
        finally:
            self.session_active = False
            
        # Get final statistics
        stats = self._compile_statistics()
        
        logger.info(f"Session completed - Total rounds: {self.current_round}")
        
        return stats
    
    async def _execute_round(self, round_number: int) -> RoundResult:
        """
        Execute a single round of the RSP cycle.
        
        Flow:
        1. Sniper generates prompt
        2. EGG inspects prompt
        3. If passed, Target executes prompt
        4. Spotter evaluates response
        5. Update Sniper with score
        
        Args:
            round_number: Current round number
            
        Returns:
            RoundResult with complete round data
        """
        timestamp = datetime.utcnow().isoformat()
        
        # Step 1: Sniper generates adversarial prompt
        prior_metadata = self.state_manager.get_prior_rounds(limit=10)
        prompt, attack_domain = self.sniper.generate_prompt(prior_metadata)
        
        # Step 2: EGG inspects prompt
        is_allowed, blocked_info = self.egg.inspect_prompt(prompt)
        
        if not is_allowed:
            # Prompt blocked by EGG
            logger.warning(
                f"Round {round_number} blocked by EGG - "
                f"Category: {blocked_info.category}"
            )
            
            return RoundResult(
                round_number=round_number,
                prompt=prompt,
                attack_domain=attack_domain.value,
                target_response=self.egg.get_blocked_replacement(),
                evaluation={},
                global_score=0.0,
                blocked_by_egg=True,
                timestamp=timestamp
            )
        
        # Step 3: Target executes prompt
        target_response = self.target.execute(
            prompt,
            metadata={'round': round_number, 'domain': attack_domain.value}
        )
        
        # Step 4: Spotter evaluates response
        evaluation = self.spotter.evaluate(
            target_response,
            attack_domain=attack_domain.value,
            prompt=prompt
        )
        
        # Step 5: Compute global score
        global_score = self.scoring_engine.compute_global_score(
            evaluation['l1']['score'],
            evaluation['l2']['score'],
            evaluation['l3']['score']
        )
        
        # Update Sniper with score for evolution
        self.sniper.update_prompt_score(prompt, global_score)
        
        return RoundResult(
            round_number=round_number,
            prompt=prompt,
            attack_domain=attack_domain.value,
            target_response=target_response,
            evaluation=evaluation,
            global_score=global_score,
            blocked_by_egg=False,
            timestamp=timestamp
        )
    
    def _compile_statistics(self) -> Dict[str, Any]:
        """Compile comprehensive session statistics."""
        state_stats = self.state_manager.get_statistics()
        
        return {
            'session': {
                'session_id': self.state_manager.session_id,
                'total_rounds': self.current_round,
                'max_rounds': self.max_rounds
            },
            'scores': {
                'average_global_score': state_stats['average_score'],
                'total_blocked': state_stats['blocked_count']
            },
            'agents': {
                'sniper': self.sniper.get_statistics(),
                'target': self.target.get_statistics(),
                'spotter': self.spotter.get_statistics(),
                'egg': self.egg.get_statistics()
            },
            'mutation': self.sniper.mutation_engine.get_statistics()
        }
    
    def terminate_session(self):
        """Terminate the current session."""
        self.session_active = False
        logger.info("Session termination requested")
    
    def cleanup(self):
        """Cleanup session data (Zero-Retention Policy)."""
        self.state_manager.cleanup()
