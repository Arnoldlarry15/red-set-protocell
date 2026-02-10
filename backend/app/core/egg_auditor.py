"""
Red Set ProtoCell - EGG Auditor (Meta-Guardrail)

Audits EGG (Ethical Guardrail Governor) decisions for potential failures.

RATIONALE:
==========

While EGG uses pattern-based detection, it's not infallible. Pattern matching
has known limitations:
- False negatives: Sophisticated prompt engineering may evade patterns
- Pattern coverage gaps: New attack vectors may not be covered
- Adversarial evasion: Deliberate obfuscation to bypass patterns

The EGGAuditor serves as a meta-guardrail that:
1. Reviews prompts that EGG allowed through
2. Looks for suspicious characteristics that suggest evasion
3. Logs discrepancies for pattern refinement
4. Provides telemetry for continuous improvement

This is NOT a replacement for EGG, but a monitoring layer that helps
identify when EGG's patterns may need updating.

Examples of what EGGAuditor looks for:
- High character substitution (l33t speak, homoglyphs)
- Obfuscation techniques (ROT13, Base64, Unicode tricks)
- Suspicious keyword density even when patterns don't match
- Context that suggests harmful intent despite pattern evasion
"""

import re
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class AuditResult:
    """Result of EGG audit."""
    prompt_fingerprint: str
    egg_decision: bool  # True = allowed, False = blocked
    audit_flags: List[str]  # List of suspicious characteristics detected
    confidence: float  # 0.0 to 1.0, where 1.0 = high confidence EGG may have failed
    notes: str


class EGGAuditor:
    """
    Meta-guardrail that audits EGG decisions.

    Identifies cases where EGG may have incorrectly allowed harmful content.
    """

    # Suspicious patterns that suggest evasion attempts
    EVASION_INDICATORS = {
        'leet_speak': r'[l1][e3][e3][t]|[h4][a@][c]{1,2}[k]|[p][w][n]',
        'homoglyphs': r'[а-яА-Я]',  # Cyrillic characters that look like Latin
        'excessive_spacing': r'\b[a-z]\s+[a-z]\s+[a-z]',  # C h a r a c t e r  s p a c i n g
        'unicode_tricks': r'[\u200b-\u200f\u2060-\u2069]',  # Zero-width and invisible chars
        'base64_like': r'[A-Za-z0-9+/]{16,}={0,2}',  # Base64 encoded content
        'rot13_like': r'\b[nopqrstuvwxyzabcdefghijklm]{8,}\b',  # ROT13 obfuscation
    }

    # High-risk keywords (more generic than EGG patterns)
    RISK_KEYWORDS = {
        'exploit': ['vulnerability', 'exploit', 'payload', 'shellcode', 'overflow'],
        'harmful': ['weapon', 'harm', 'attack', 'illegal', 'unauthorized'],
        'csam': ['child', 'minor', 'underage'],
    }

    def __init__(self, enabled: bool = True, log_audit_failures: bool = True):
        """
        Initialize EGG Auditor.

        Args:
            enabled: Enable auditing
            log_audit_failures: Log cases where audit flags suggest EGG may have failed
        """
        self.enabled = enabled
        self.log_audit_failures = log_audit_failures

        self.audit_count = 0
        self.flagged_count = 0
        self.audit_history: List[AuditResult] = []

        logger.info(f"EGGAuditor initialized - Enabled: {enabled}")

    def audit_decision(
        self,
        prompt: str,
        egg_allowed: bool,
        egg_blocked_category: Optional[str] = None
    ) -> AuditResult:
        """
        Audit an EGG decision.

        Args:
            prompt: The prompt that was evaluated
            egg_allowed: True if EGG allowed, False if blocked
            egg_blocked_category: Category if blocked (None if allowed)

        Returns:
            AuditResult with findings
        """
        if not self.enabled:
            return AuditResult(
                prompt_fingerprint="",
                egg_decision=egg_allowed,
                audit_flags=[],
                confidence=0.0,
                notes="Auditor disabled"
            )

        self.audit_count += 1

        # Compute fingerprint (same as EGG)
        from app.core.security import hash_prompt
        fingerprint = hash_prompt(prompt)

        # Only audit prompts that EGG allowed through
        if not egg_allowed:
            return AuditResult(
                prompt_fingerprint=fingerprint,
                egg_decision=egg_allowed,
                audit_flags=[],
                confidence=0.0,
                notes=f"EGG correctly blocked (category: {egg_blocked_category})"
            )

        # Check for evasion indicators
        flags = []

        prompt_lower = prompt.lower()

        # Check evasion techniques
        for technique, pattern in self.EVASION_INDICATORS.items():
            if re.search(pattern, prompt, re.IGNORECASE):
                flags.append(f"evasion:{technique}")

        # Check for suspicious keyword density
        risk_score = 0
        for category, keywords in self.RISK_KEYWORDS.items():
            matches = sum(1 for kw in keywords if kw in prompt_lower)
            if matches >= 2:  # At least 2 keywords from same category
                flags.append(f"keyword_density:{category}")
                risk_score += matches

        # Calculate confidence that EGG may have failed
        # More flags = higher confidence
        confidence = min(len(flags) * 0.3, 1.0) if flags else 0.0

        # Log if we found concerning flags
        if flags and self.log_audit_failures:
            self.flagged_count += 1
            logger.warning(
                f"⚠️  EGG Audit: Potentially harmful prompt allowed through. "
                f"Fingerprint: {fingerprint}, Flags: {flags}, Confidence: {confidence:.2f}"
            )

        result = AuditResult(
            prompt_fingerprint=fingerprint,
            egg_decision=egg_allowed,
            audit_flags=flags,
            confidence=confidence,
            notes=f"Audited {len(flags)} suspicious characteristics"
        )

        # Store in history (keep last 100)
        self.audit_history.append(result)
        if len(self.audit_history) > 100:
            self.audit_history.pop(0)

        return result

    def get_statistics(self) -> Dict:
        """Get audit statistics."""
        return {
            'enabled': self.enabled,
            'total_audited': self.audit_count,
            'flagged_count': self.flagged_count,
            'flagged_rate': self.flagged_count / self.audit_count if self.audit_count > 0 else 0.0,
        }

    def get_high_confidence_failures(self, min_confidence: float = 0.5) -> List[AuditResult]:
        """
        Get audit results where we have high confidence EGG may have failed.

        Args:
            min_confidence: Minimum confidence threshold (0.0 to 1.0)

        Returns:
            List of AuditResult with confidence >= min_confidence
        """
        return [
            result for result in self.audit_history
            if result.egg_decision and result.confidence >= min_confidence
        ]
