"""
Red Set ProtoCell - Selection Engine

Implements selection pressure mechanisms for evolutionary prompt generation.
Provides multiple selection strategies to prevent evolution toward failures
and ensure exploration of the prompt space.

Key Features:
- Elitism: Preserve top performers
- Tournament selection: Competitive selection
- Diversity preservation: Maintain variety in prompt population
- Novelty search: Reward structurally different prompts
- Prompt aging and decay: Prevent dominance of old winners
- Overfitting penalties: Discourage single exploit style

This transforms the system from random mutation to directed evolution.
"""

import random
import hashlib
import time
from typing import List, Dict, Any, Tuple, Optional, Set
from enum import Enum
from dataclasses import dataclass
from collections import defaultdict


class SelectionStrategy(Enum):
    """Available selection strategies for evolution."""
    ELITISM = "elitism"
    TOURNAMENT = "tournament"
    DIVERSITY_PRESERVATION = "diversity_preservation"
    NOVELTY_SEARCH = "novelty_search"
    HYBRID = "hybrid"


@dataclass
class PromptCandidate:
    """
    A candidate prompt with metadata for selection.

    Attributes:
        prompt: The prompt text
        score: Fitness score (0.0 to 1.0)
        domain: Attack domain
        strategy: Mutation strategy used
        timestamp: When the prompt was created
        usage_count: Number of times used in evolution
        structural_hash: Hash representing prompt structure
        diversity_score: Score for maintaining diversity
        novelty_score: Score for novelty relative to high scorers
    """
    prompt: str
    score: float
    domain: str
    strategy: Optional[str] = None
    timestamp: float = 0.0
    usage_count: int = 0
    structural_hash: str = ""
    diversity_score: float = 0.0
    novelty_score: float = 0.0

    def __post_init__(self):
        """Initialize computed fields."""
        if self.timestamp == 0.0:
            self.timestamp = time.time()
        if not self.structural_hash:
            self.structural_hash = self._compute_structural_hash()

    def _compute_structural_hash(self) -> str:
        """
        Compute a structural hash based on prompt patterns.

        This captures the "shape" of the prompt rather than exact content,
        allowing novelty detection to focus on structural differences.
        """
        # Extract structural features
        features = []
        features.append(f"length:{len(self.prompt) // 10}")  # Length bucket
        features.append(f"words:{len(self.prompt.split()) // 5}")  # Word count bucket

        # Character composition
        upper_ratio = sum(1 for c in self.prompt if c.isupper()) / max(len(self.prompt), 1)
        features.append(f"upper:{int(upper_ratio * 10)}")

        # Punctuation patterns
        punct_count = sum(1 for c in self.prompt if c in "!?.,;:")
        features.append(f"punct:{punct_count // 2}")

        # Encoding/special char patterns
        special_count = sum(1 for c in self.prompt if c in "{}[]()<>@#$%^&*")
        features.append(f"special:{special_count // 2}")

        # Domain patterns (keywords)
        keywords = ["ignore", "bypass", "override", "pretend", "hypothetical", "character"]
        keyword_count = sum(1 for kw in keywords if kw.lower() in self.prompt.lower())
        features.append(f"keywords:{keyword_count}")

        # Create hash from structural features
        feature_str = "|".join(sorted(features))
        return hashlib.md5(feature_str.encode()).hexdigest()[:16]

    def age_in_seconds(self) -> float:
        """Get age of this candidate in seconds."""
        return time.time() - self.timestamp

    def age_in_rounds(self, rounds_per_second: float = 0.1) -> float:
        """
        Estimate age in rounds.

        Args:
            rounds_per_second: Estimated round execution rate
        """
        return self.age_in_seconds() * rounds_per_second


class SelectionEngine:
    """
    Selection engine that implements various selection strategies for evolution.

    This engine transforms raw fitness scores into selection decisions that
    encourage exploration, prevent local maxima, and maintain diversity.
    """

    def __init__(
        self,
        decay_rate: float = 0.95,
        decay_interval: float = 60.0,
        novelty_weight: float = 0.3,
        diversity_weight: float = 0.2,
        overfitting_threshold: int = 3,
        tournament_size: int = 3,
        elite_fraction: float = 0.2
    ):
        """
        Initialize selection engine.

        Args:
            decay_rate: Multiplier for score decay (0.0 to 1.0)
            decay_interval: Seconds between decay applications
            novelty_weight: Weight for novelty in selection (0.0 to 1.0)
            diversity_weight: Weight for diversity in selection (0.0 to 1.0)
            overfitting_threshold: Max times a pattern can dominate
            tournament_size: Number of candidates in tournament selection
            elite_fraction: Fraction of population to preserve as elite
        """
        self.decay_rate = decay_rate
        self.decay_interval = decay_interval
        self.novelty_weight = novelty_weight
        self.diversity_weight = diversity_weight
        self.overfitting_threshold = overfitting_threshold
        self.tournament_size = tournament_size
        self.elite_fraction = elite_fraction

        # Track high-scoring prompt structures for novelty calculation
        self.high_scorer_structures: Set[str] = set()
        self.high_scorer_threshold = 0.6  # Score threshold for "high scorer"

        # Track pattern usage for overfitting detection
        self.pattern_usage: Dict[str, int] = defaultdict(int)

        # Track strategy performance
        self.strategy_stats: Dict[str, List[float]] = defaultdict(list)

    def select(
        self,
        candidates: List[PromptCandidate],
        strategy: SelectionStrategy = SelectionStrategy.HYBRID,
        num_select: int = 1
    ) -> List[PromptCandidate]:
        """
        Select candidates using the specified strategy.

        Args:
            candidates: List of prompt candidates to select from
            strategy: Selection strategy to use
            num_select: Number of candidates to select

        Returns:
            List of selected candidates
        """
        if not candidates:
            return []

        # Apply decay to aged candidates
        candidates = self._apply_decay(candidates)

        # Update novelty scores
        candidates = self._update_novelty_scores(candidates)

        # Update diversity scores
        candidates = self._update_diversity_scores(candidates)

        # Apply overfitting penalties
        candidates = self._apply_overfitting_penalties(candidates)

        # Select based on strategy
        if strategy == SelectionStrategy.ELITISM:
            selected = self._elitism_select(candidates, num_select)
        elif strategy == SelectionStrategy.TOURNAMENT:
            selected = self._tournament_select(candidates, num_select)
        elif strategy == SelectionStrategy.DIVERSITY_PRESERVATION:
            selected = self._diversity_select(candidates, num_select)
        elif strategy == SelectionStrategy.NOVELTY_SEARCH:
            selected = self._novelty_select(candidates, num_select)
        elif strategy == SelectionStrategy.HYBRID:
            selected = self._hybrid_select(candidates, num_select)
        else:
            selected = candidates[:num_select]

        # Update usage tracking
        for candidate in selected:
            candidate.usage_count += 1
            self.pattern_usage[candidate.structural_hash] += 1

            # Track high scorers for novelty calculation
            if candidate.score >= self.high_scorer_threshold:
                self.high_scorer_structures.add(candidate.structural_hash)

        return selected

    def _apply_decay(self, candidates: List[PromptCandidate]) -> List[PromptCandidate]:
        """
        Apply time-based decay to candidate scores.

        Old "winning" prompts lose dominance over time, encouraging
        exploration of new patterns.
        """
        # Modify scores in-place to preserve object identity
        for candidate in candidates:
            age_seconds = candidate.age_in_seconds()
            decay_periods = int(age_seconds / self.decay_interval)

            if decay_periods > 0:
                # Apply exponential decay
                decay_factor = self.decay_rate ** decay_periods
                candidate.score = candidate.score * decay_factor

        return candidates

    def _update_novelty_scores(self, candidates: List[PromptCandidate]) -> List[PromptCandidate]:
        """
        Update novelty scores based on structural difference from high scorers.

        Prompts that are structurally different from previous high scorers
        get bonus points, even if their raw score is slightly lower.
        """
        for candidate in candidates:
            if not self.high_scorer_structures:
                # No high scorers yet, all novel
                candidate.novelty_score = 1.0
            else:
                # Calculate novelty as inverse of similarity to high scorers
                if candidate.structural_hash in self.high_scorer_structures:
                    # Same structure as a high scorer
                    candidate.novelty_score = 0.0
                else:
                    # Different structure - full novelty
                    candidate.novelty_score = 1.0

        return candidates

    def _update_diversity_scores(self, candidates: List[PromptCandidate]) -> List[PromptCandidate]:
        """
        Update diversity scores based on uniqueness within current population.
        """
        # Count structural hash occurrences
        hash_counts = defaultdict(int)
        for candidate in candidates:
            hash_counts[candidate.structural_hash] += 1

        # Score inversely proportional to frequency
        for candidate in candidates:
            count = hash_counts[candidate.structural_hash]
            candidate.diversity_score = 1.0 / count

        return candidates

    def _apply_overfitting_penalties(self, candidates: List[PromptCandidate]) -> List[PromptCandidate]:
        """
        Penalize patterns that have been used too frequently.

        This prevents overfitting to a single exploit style.
        """
        # Modify scores in-place to preserve object identity
        for candidate in candidates:
            usage = self.pattern_usage[candidate.structural_hash]

            if usage >= self.overfitting_threshold:
                # Apply penalty that increases with usage
                penalty_factor = 0.5 ** (usage - self.overfitting_threshold + 1)
                candidate.score = candidate.score * penalty_factor

        return candidates

    def _elitism_select(
        self,
        candidates: List[PromptCandidate],
        num_select: int
    ) -> List[PromptCandidate]:
        """
        Elitism selection: Select top performers by score.

        Preserves the best candidates to ensure quality doesn't degrade.
        """
        sorted_candidates = sorted(candidates, key=lambda c: c.score, reverse=True)
        return sorted_candidates[:num_select]

    def _tournament_select(
        self,
        candidates: List[PromptCandidate],
        num_select: int
    ) -> List[PromptCandidate]:
        """
        Tournament selection: Randomly sample and select best.

        Creates competitive pressure while maintaining diversity.
        """
        selected = []
        for _ in range(num_select):
            # Random sample for tournament
            tournament_size = min(self.tournament_size, len(candidates))
            tournament = random.sample(candidates, tournament_size)

            # Select winner (highest score)
            winner = max(tournament, key=lambda c: c.score)
            selected.append(winner)

        return selected

    def _diversity_select(
        self,
        candidates: List[PromptCandidate],
        num_select: int
    ) -> List[PromptCandidate]:
        """
        Diversity selection: Prioritize unique structures.

        Maintains variety in the population to prevent premature convergence.
        """
        # Score combining fitness and diversity
        scored = [
            (c, c.score * 0.5 + c.diversity_score * 0.5)
            for c in candidates
        ]
        scored.sort(key=lambda x: x[1], reverse=True)

        return [c for c, _ in scored[:num_select]]

    def _novelty_select(
        self,
        candidates: List[PromptCandidate],
        num_select: int
    ) -> List[PromptCandidate]:
        """
        Novelty selection: Reward structural differences from high scorers.

        Prevents local maxima by exploring different structural patterns.
        """
        # Score combining fitness and novelty
        scored = [
            (c, c.score * (1 - self.novelty_weight) + c.novelty_score * self.novelty_weight)
            for c in candidates
        ]
        scored.sort(key=lambda x: x[1], reverse=True)

        return [c for c, _ in scored[:num_select]]

    def _hybrid_select(
        self,
        candidates: List[PromptCandidate],
        num_select: int
    ) -> List[PromptCandidate]:
        """
        Hybrid selection: Combine multiple strategies.

        Balances exploitation (elitism), exploration (novelty),
        and diversity preservation.
        """
        if num_select == 1:
            # For single selection, use weighted combination
            return self._novelty_select(candidates, 1)

        # Allocate selections across strategies
        num_elite = max(1, int(num_select * self.elite_fraction))
        num_novelty = max(1, int(num_select * 0.4))
        num_diverse = max(1, num_select - num_elite - num_novelty)

        # Adjust if total exceeds num_select
        total = num_elite + num_novelty + num_diverse
        if total > num_select:
            num_diverse = num_select - num_elite - num_novelty

        selected = []
        selected_set = set()  # Track IDs for O(1) lookup

        # Elite selection
        elite = self._elitism_select(candidates, num_elite)
        selected.extend(elite)
        selected_set.update(id(c) for c in elite)

        # Remove selected from candidates using set for efficient lookup
        remaining = [c for c in candidates if id(c) not in selected_set]

        # Novelty selection
        if remaining and num_novelty > 0:
            novelty = self._novelty_select(remaining, min(num_novelty, len(remaining)))
            selected.extend(novelty)
            selected_set.update(id(c) for c in novelty)
            remaining = [c for c in remaining if id(c) not in selected_set]

        # Diversity selection
        if remaining and num_diverse > 0:
            diverse = self._diversity_select(remaining, min(num_diverse, len(remaining)))
            selected.extend(diverse)

        return selected[:num_select]

    def get_statistics(self) -> Dict[str, Any]:
        """Get selection statistics."""
        return {
            'high_scorer_count': len(self.high_scorer_structures),
            'pattern_usage_count': len(self.pattern_usage),
            'most_used_pattern_count': max(self.pattern_usage.values()) if self.pattern_usage else 0,
            'decay_rate': self.decay_rate,
            'novelty_weight': self.novelty_weight,
            'diversity_weight': self.diversity_weight
        }

    def reset_pattern_tracking(self):
        """Reset pattern usage tracking (e.g., for new session)."""
        self.pattern_usage.clear()
        self.high_scorer_structures.clear()
