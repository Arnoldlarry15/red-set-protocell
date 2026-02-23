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

import hashlib
import random
import time
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Set


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
        semantic_hash: Hash representing prompt semantics
        diversity_score: Score for maintaining diversity
        novelty_score: Score for novelty relative to high scorers
        performance_history: List of recent scores for performance-based decay
    """

    prompt: str
    score: float
    domain: str
    strategy: Optional[str] = None
    timestamp: float = 0.0
    usage_count: int = 0
    structural_hash: str = ""
    semantic_hash: str = ""
    diversity_score: float = 0.0
    novelty_score: float = 0.0
    performance_history: List[float] = None

    def __post_init__(self):
        """Initialize computed fields."""
        if self.timestamp == 0.0:
            self.timestamp = time.time()
        if not self.structural_hash:
            self.structural_hash = self._compute_structural_hash()
        if not self.semantic_hash:
            self.semantic_hash = self._compute_semantic_hash()
        if self.performance_history is None:
            self.performance_history = []

    def _compute_structural_hash(self) -> str:
        """
        Compute a structural hash based on prompt patterns.

        This captures the "shape" of the prompt rather than exact content,
        allowing novelty detection to focus on structural differences.

        Enhanced with finer granularity to reduce bucket collisions.
        """
        # Extract structural features with finer buckets
        features = []
        features.append(
            f"length:{len(self.prompt) // 5}"
        )  # Finer length bucket (was // 10)
        features.append(
            f"words:{len(self.prompt.split()) // 3}"
        )  # Finer word count bucket (was // 5)

        # Character composition with more precision
        upper_ratio = sum(1 for c in self.prompt if c.isupper()) / max(
            len(self.prompt), 1
        )
        features.append(f"upper:{int(upper_ratio * 20)}")  # More precision (was * 10)

        lower_ratio = sum(1 for c in self.prompt if c.islower()) / max(
            len(self.prompt), 1
        )
        features.append(f"lower:{int(lower_ratio * 20)}")

        digit_ratio = sum(1 for c in self.prompt if c.isdigit()) / max(
            len(self.prompt), 1
        )
        features.append(f"digits:{int(digit_ratio * 20)}")

        # Punctuation patterns with categories
        punct_count = sum(1 for c in self.prompt if c in "!?.,;:")
        features.append(f"punct:{punct_count // 2}")

        # Different punctuation types
        exclamation_count = self.prompt.count("!")
        question_count = self.prompt.count("?")
        features.append(f"exclaim:{exclamation_count}")
        features.append(f"question:{question_count}")

        # Encoding/special char patterns
        special_count = sum(1 for c in self.prompt if c in "{}[]()<>@#$%^&*")
        features.append(f"special:{special_count // 2}")

        # Bracket patterns
        bracket_count = sum(1 for c in self.prompt if c in "{}[]()<>")
        features.append(f"brackets:{bracket_count}")

        # Domain patterns (keywords)
        keywords = [
            "ignore",
            "bypass",
            "override",
            "pretend",
            "hypothetical",
            "character",
        ]
        keyword_count = sum(1 for kw in keywords if kw.lower() in self.prompt.lower())
        features.append(f"keywords:{keyword_count}")

        # Sentence structure
        sentences = self.prompt.split(".")
        features.append(f"sentences:{len(sentences) // 2}")

        # Newline patterns (multi-line structure)
        newline_count = self.prompt.count("\n")
        features.append(f"newlines:{newline_count}")

        # Quote patterns
        quote_count = self.prompt.count('"') + self.prompt.count("'")
        features.append(f"quotes:{quote_count // 2}")

        # Create hash from structural features
        feature_str = "|".join(sorted(features))
        return hashlib.md5(feature_str.encode()).hexdigest()[:16]

    def _compute_semantic_hash(self) -> str:
        """
        Compute a semantic hash based on content keywords and meaning.

        This captures the semantic intent rather than just structure,
        allowing detection of clever rewordings that maintain meaning.
        """
        # Extract semantic features
        features = []

        # Normalize text for semantic analysis
        normalized = self.prompt.lower()
        words = normalized.split()

        # Semantic keyword categories
        instruction_keywords = [
            "ignore",
            "disregard",
            "forget",
            "bypass",
            "override",
            "skip",
        ]
        roleplay_keywords = [
            "pretend",
            "act",
            "character",
            "role",
            "persona",
            "imagine",
        ]
        hypothetical_keywords = [
            "hypothetical",
            "suppose",
            "assume",
            "imagine",
            "what if",
        ]
        system_keywords = ["system", "admin", "root", "developer", "mode", "setting"]
        extraction_keywords = ["reveal", "show", "tell", "extract", "display", "output"]
        encoding_keywords = [
            "base64",
            "encode",
            "decode",
            "translate",
            "cipher",
            "rot13",
        ]

        # Count presence in each semantic category
        for category, keywords in [
            ("instruction", instruction_keywords),
            ("roleplay", roleplay_keywords),
            ("hypothetical", hypothetical_keywords),
            ("system", system_keywords),
            ("extraction", extraction_keywords),
            ("encoding", encoding_keywords),
        ]:
            count = sum(1 for kw in keywords if kw in normalized)
            if count > 0:
                features.append(f"{category}:{count}")

        # Detect common patterns
        if "previous" in normalized and "instruction" in normalized:
            features.append("previous_instruction_pattern")
        if "new" in normalized and (
            "instruction" in normalized or "directive" in normalized
        ):
            features.append("new_instruction_pattern")
        if "you are" in normalized or "you're" in normalized:
            features.append("identity_assertion")
        if "now" in normalized and ("you" in normalized or "we" in normalized):
            features.append("state_transition")

        # Linguistic complexity
        avg_word_length = sum(len(w) for w in words) / max(len(words), 1)
        features.append(f"avg_word_len:{int(avg_word_length)}")

        # Unique word ratio (vocabulary richness)
        unique_ratio = len(set(words)) / max(len(words), 1)
        features.append(f"unique_ratio:{int(unique_ratio * 10)}")

        # Create hash from semantic features
        if not features:
            features.append("neutral")  # Fallback for neutral content

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

    # Constants for single-selection scoring
    SINGLE_SELECT_FITNESS_WEIGHT = (
        0.7  # Weight for fitness in balanced single selection
    )

    def __init__(
        self,
        decay_rate: float = 0.95,
        decay_interval: float = 60.0,
        novelty_weight: float = 0.3,
        diversity_weight: float = 0.2,
        overfitting_threshold: int = 3,
        tournament_size: int = 3,
        elite_fraction: float = 0.2,
        performance_decay_weight: float = 0.5,
        single_select_strategy: str = "balanced",
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
            performance_decay_weight: Weight for performance-based decay (0.0 = time-only, 1.0 = performance-only)
            single_select_strategy: Strategy for num_select==1: 'balanced', 'elite', or 'novelty'
        """
        self.decay_rate = decay_rate
        self.decay_interval = decay_interval
        self.novelty_weight = novelty_weight
        self.diversity_weight = diversity_weight
        self.overfitting_threshold = overfitting_threshold
        self.tournament_size = tournament_size
        self.elite_fraction = elite_fraction
        self.performance_decay_weight = performance_decay_weight
        self.single_select_strategy = single_select_strategy

        # Track high-scoring prompt structures for novelty calculation
        self.high_scorer_structures: Set[str] = set()
        self.high_scorer_threshold = 0.6  # Score threshold for "high scorer"

        # Track pattern usage for overfitting detection (both structural and semantic)
        self.pattern_usage: Dict[str, int] = defaultdict(int)
        self.semantic_pattern_usage: Dict[str, int] = defaultdict(int)

        # Track strategy performance
        self.strategy_stats: Dict[str, List[float]] = defaultdict(list)

    def select(
        self,
        candidates: List[PromptCandidate],
        strategy: SelectionStrategy = SelectionStrategy.HYBRID,
        num_select: int = 1,
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
            self.semantic_pattern_usage[candidate.semantic_hash] += 1

            # Track high scorers for novelty calculation
            if candidate.score >= self.high_scorer_threshold:
                self.high_scorer_structures.add(candidate.structural_hash)

            # Update performance history
            candidate.performance_history.append(candidate.score)
            # Keep only last 5 scores for performance tracking
            if len(candidate.performance_history) > 5:
                candidate.performance_history = candidate.performance_history[-5:]

        return selected

    def _apply_decay(self, candidates: List[PromptCandidate]) -> List[PromptCandidate]:
        """
        Apply time-based and performance-based decay to candidate scores.

        Old "winning" prompts lose dominance over time, and prompts with
        declining performance decay faster, encouraging exploration of new patterns.
        """
        # Modify scores in-place to preserve object identity
        for candidate in candidates:
            age_seconds = candidate.age_in_seconds()
            decay_periods = int(age_seconds / self.decay_interval)

            if decay_periods > 0:
                # Apply exponential time-based decay
                time_decay_factor = self.decay_rate**decay_periods

                # Calculate performance-based decay
                performance_decay_factor = 1.0
                if (
                    candidate.performance_history
                    and len(candidate.performance_history) >= 2
                ):
                    # Check if performance is declining
                    recent_scores = candidate.performance_history[-3:]
                    recent_avg = sum(recent_scores) / len(recent_scores)
                    overall_avg = sum(candidate.performance_history) / len(
                        candidate.performance_history
                    )

                    MIN_AVG_SCORE = 0.01  # Guard against division by zero
                    if recent_avg < overall_avg:
                        # Performance is declining - apply additional decay
                        decline_ratio = recent_avg / max(overall_avg, MIN_AVG_SCORE)
                        performance_decay_factor = 0.5 + (
                            0.5 * decline_ratio
                        )  # Range: 0.5 to 1.0

                # Combine time and performance decay as weighted average
                combined_decay = (
                    time_decay_factor * (1 - self.performance_decay_weight)
                    + performance_decay_factor * self.performance_decay_weight
                )

                candidate.score = candidate.score * combined_decay

        return candidates

    def _update_novelty_scores(
        self, candidates: List[PromptCandidate]
    ) -> List[PromptCandidate]:
        """
        Update novelty scores based on structural distance from high scorers.

        Uses gradient-based distance measure instead of binary 0/1 scoring.
        Prompts that are more different from previous high scorers get higher
        novelty scores, with a continuous gradient.
        """
        for candidate in candidates:
            if not self.high_scorer_structures:
                # No high scorers yet, all novel
                candidate.novelty_score = 1.0
            else:
                # Calculate minimum distance to any high scorer
                min_distance = float("inf")

                for high_scorer_hash in self.high_scorer_structures:
                    distance = self._hash_distance(
                        candidate.structural_hash, high_scorer_hash
                    )
                    min_distance = min(min_distance, distance)

                # Normalize distance to 0-1 range
                # Max distance between 16-char hex hashes is 16 (all chars different)
                max_possible_distance = 16
                normalized_distance = min(min_distance / max_possible_distance, 1.0)

                # Use sigmoid-like curve for smoother gradient
                # Maps [0, 1] to [0, 1] with smooth transition
                candidate.novelty_score = normalized_distance

        return candidates

    def _hash_distance(self, hash1: str, hash2: str) -> float:
        """
        Calculate distance between two hashes.

        Uses Hamming distance on hex strings to measure structural difference.
        Returns a value between 0 (identical) and len(hash) (completely different).
        """
        if len(hash1) != len(hash2):
            return max(len(hash1), len(hash2))

        # Hamming distance - count differing characters
        distance = sum(c1 != c2 for c1, c2 in zip(hash1, hash2))
        return float(distance)

    def _update_diversity_scores(
        self, candidates: List[PromptCandidate]
    ) -> List[PromptCandidate]:
        """
        Update diversity scores based on uniqueness within current population.
        """
        # Count structural hash occurrences
        hash_counts: dict[Any, int] = defaultdict(int)
        for candidate in candidates:
            hash_counts[candidate.structural_hash] += 1

        # Score inversely proportional to frequency
        for candidate in candidates:
            count = hash_counts[candidate.structural_hash]
            candidate.diversity_score = 1.0 / count

        return candidates

    def _apply_overfitting_penalties(
        self, candidates: List[PromptCandidate]
    ) -> List[PromptCandidate]:
        """
        Penalize patterns that have been used too frequently.

        This prevents overfitting to a single exploit style.
        Now tracks both structural and semantic patterns to catch clever rewordings.
        """
        # Modify scores in-place to preserve object identity
        for candidate in candidates:
            structural_usage = self.pattern_usage[candidate.structural_hash]
            semantic_usage = self.semantic_pattern_usage[candidate.semantic_hash]

            # Use the maximum usage count (most restrictive)
            max_usage = max(structural_usage, semantic_usage)

            if max_usage >= self.overfitting_threshold:
                # Apply penalty that increases with usage
                penalty_factor = 0.5 ** (max_usage - self.overfitting_threshold + 1)
                candidate.score = candidate.score * penalty_factor

        return candidates

    def _elitism_select(
        self, candidates: List[PromptCandidate], num_select: int
    ) -> List[PromptCandidate]:
        """
        Elitism selection: Select top performers by score.

        Preserves the best candidates to ensure quality doesn't degrade.
        """
        sorted_candidates = sorted(candidates, key=lambda c: c.score, reverse=True)
        return sorted_candidates[:num_select]

    def _tournament_select(
        self, candidates: List[PromptCandidate], num_select: int
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
        self, candidates: List[PromptCandidate], num_select: int
    ) -> List[PromptCandidate]:
        """
        Diversity selection: Prioritize unique structures.

        Maintains variety in the population to prevent premature convergence.
        """
        # Score combining fitness and diversity
        scored = [(c, c.score * 0.5 + c.diversity_score * 0.5) for c in candidates]
        scored.sort(key=lambda x: x[1], reverse=True)

        return [c for c, _ in scored[:num_select]]

    def _novelty_select(
        self, candidates: List[PromptCandidate], num_select: int
    ) -> List[PromptCandidate]:
        """
        Novelty selection: Reward structural differences from high scorers.

        Prevents local maxima by exploring different structural patterns.
        """
        # Score combining fitness and novelty
        scored = [
            (
                c,
                c.score * (1 - self.novelty_weight)
                + c.novelty_score * self.novelty_weight,
            )
            for c in candidates
        ]
        scored.sort(key=lambda x: x[1], reverse=True)

        return [c for c, _ in scored[:num_select]]

    def _hybrid_select(
        self, candidates: List[PromptCandidate], num_select: int
    ) -> List[PromptCandidate]:
        """
        Hybrid selection: Combine multiple strategies.

        Balances exploitation (elitism), exploration (novelty),
        and diversity preservation.
        """
        if num_select == 1:
            # For single selection, use configurable strategy to avoid drift
            if self.single_select_strategy == "balanced":
                # Balanced: combine elite fitness with novelty
                # Use complementary weights to ensure they sum to 1.0
                novelty_component_weight = 1.0 - self.SINGLE_SELECT_FITNESS_WEIGHT
                scored = [
                    (
                        c,
                        c.score * self.SINGLE_SELECT_FITNESS_WEIGHT
                        + c.novelty_score * novelty_component_weight,
                    )
                    for c in candidates
                ]
                scored.sort(key=lambda x: x[1], reverse=True)
                return [scored[0][0]]
            elif self.single_select_strategy == "elite":
                # Pure elitism for single selection
                return self._elitism_select(candidates, 1)
            else:  # "novelty"
                # Pure novelty for single selection
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
        selected_set: set[Any] = set()  # Track IDs for O(1) lookup

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
            diverse = self._diversity_select(
                remaining, min(num_diverse, len(remaining))
            )
            selected.extend(diverse)

        return selected[:num_select]

    def get_statistics(self) -> Dict[str, Any]:
        """Get selection statistics."""
        return {
            "high_scorer_count": len(self.high_scorer_structures),
            "pattern_usage_count": len(self.pattern_usage),
            "semantic_pattern_usage_count": len(self.semantic_pattern_usage),
            "most_used_pattern_count": (
                max(self.pattern_usage.values()) if self.pattern_usage else 0
            ),
            "most_used_semantic_pattern_count": (
                max(self.semantic_pattern_usage.values())
                if self.semantic_pattern_usage
                else 0
            ),
            "decay_rate": self.decay_rate,
            "novelty_weight": self.novelty_weight,
            "diversity_weight": self.diversity_weight,
            "performance_decay_weight": self.performance_decay_weight,
            "single_select_strategy": self.single_select_strategy,
        }

    def reset_pattern_tracking(self):
        """Reset pattern usage tracking (e.g., for new session)."""
        self.pattern_usage.clear()
        self.semantic_pattern_usage.clear()
        self.high_scorer_structures.clear()
