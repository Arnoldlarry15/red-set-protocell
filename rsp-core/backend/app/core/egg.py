"""
Red Set ProtoCell - Ethical Guardrail Governor (EGG)

Mandatory middleware layer that inspects and blocks disallowed content.
EGG decisions are final and not overridable by any agent.
"""

import re
import logging
from typing import Tuple, Optional, List
from dataclasses import dataclass

from app.core.security import hash_prompt


logger = logging.getLogger(__name__)


@dataclass
class BlockedContent:
    """Information about blocked content."""
    reason: str
    category: str
    fingerprint: str


class EthicalGuardrailGovernor:
    """
    The Ethical Guardrail Governor (EGG) is a mandatory middleware layer
    that inspects generated prompts and blocks disallowed content.
    
    EGG decisions are final and cannot be overridden by any agent.
    """
    
    # Patterns for content that must be blocked
    BLOCKED_PATTERNS = {
        'csam': [
            r'\b(child|minor|underage).{0,20}(sexual|explicit|nude)',
            r'\b(cp|child porn)',
        ],
        'bioweapons': [
            r'\b(weaponi[sz]e).{0,30}(anthrax|ricin|botulinum)',
            r'\banthrax.{0,30}weaponi[sz]e',
            r'\b(bioweapon|biological weapon).{0,30}(create|make|build)',
            r'\b(pathogen|virus|bacteria).{0,30}(engineer|modify).{0,30}(lethal|deadly)',
            r'weaponize anthrax',
        ],
        'real_exploits': [
            r'\b(exploit|payload).{0,30}(execute|run).{0,30}(system|server)',
            r'\b(shell|cmd|bash).{0,30}(injection|execution).{0,30}(real|actual|live)',
            r'\bzero.?day.{0,30}(actual|real|working|code)',
            r'\bactual zero.?day',
            r'\b(malware|ransomware|trojan).{0,30}(code|implementation|actual)',
        ],
        'real_hacking': [
            r'\b(hack|breach|penetrate).{0,30}(actual|real).{0,30}(system|network|server)',
            r'\b(credit card|ssn|social security).{0,30}(steal|extract|harvest).{0,30}(actual|real)',
        ]
    }
    
    def __init__(self, enabled: bool = True, log_fingerprints: bool = True,
                 block_csam: bool = True, block_bioweapons: bool = True,
                 block_real_exploits: bool = True):
        """
        Initialize the Ethical Guardrail Governor.
        
        Args:
            enabled: Whether EGG is enabled (should always be True in production)
            log_fingerprints: Whether to log hashed fingerprints of blocked content
            block_csam: Block child safety violations
            block_bioweapons: Block biological weapon instructions
            block_real_exploits: Block real exploit payloads
        """
        self.enabled = enabled
        self.log_fingerprints = log_fingerprints
        self.block_csam = block_csam
        self.block_bioweapons = block_bioweapons
        self.block_real_exploits = block_real_exploits
        
        self.blocked_count = 0
        self.blocked_fingerprints: List[str] = []
        
    def inspect_prompt(self, prompt: str) -> Tuple[bool, Optional[BlockedContent]]:
        """
        Inspect a prompt for disallowed content.
        
        Args:
            prompt: The prompt to inspect
            
        Returns:
            Tuple of (is_allowed, blocked_info)
            - is_allowed: True if prompt passes, False if blocked
            - blocked_info: BlockedContent object if blocked, None if allowed
        """
        if not self.enabled:
            return True, None
        
        # Normalize prompt for matching
        prompt_lower = prompt.lower()
        
        # Check each category
        if self.block_csam:
            for pattern in self.BLOCKED_PATTERNS['csam']:
                if re.search(pattern, prompt_lower, re.IGNORECASE):
                    return False, self._block_prompt(
                        prompt, 'csam', 'CSAM content detected'
                    )
        
        if self.block_bioweapons:
            for pattern in self.BLOCKED_PATTERNS['bioweapons']:
                if re.search(pattern, prompt_lower, re.IGNORECASE):
                    return False, self._block_prompt(
                        prompt, 'bioweapons', 'Bioweapon instructions detected'
                    )
        
        if self.block_real_exploits:
            for pattern in self.BLOCKED_PATTERNS['real_exploits']:
                if re.search(pattern, prompt_lower, re.IGNORECASE):
                    return False, self._block_prompt(
                        prompt, 'real_exploits', 'Real exploit payload detected'
                    )
            
            for pattern in self.BLOCKED_PATTERNS['real_hacking']:
                if re.search(pattern, prompt_lower, re.IGNORECASE):
                    return False, self._block_prompt(
                        prompt, 'real_hacking', 'Real hacking attempt detected'
                    )
        
        return True, None
    
    def _block_prompt(self, prompt: str, category: str, reason: str) -> BlockedContent:
        """
        Block a prompt and log the event.
        
        Args:
            prompt: The blocked prompt
            category: The category of violation
            reason: Human-readable reason for blocking
            
        Returns:
            BlockedContent object with details
        """
        fingerprint = hash_prompt(prompt)
        
        if self.log_fingerprints:
            self.blocked_fingerprints.append(fingerprint)
            logger.warning(
                f"EGG blocked prompt - Category: {category}, "
                f"Reason: {reason}, Fingerprint: {fingerprint}"
            )
        
        self.blocked_count += 1
        
        return BlockedContent(
            reason=reason,
            category=category,
            fingerprint=fingerprint
        )
    
    def get_blocked_replacement(self) -> str:
        """
        Get the replacement string for blocked prompts.
        
        Returns:
            The blocked prompt replacement marker
        """
        return "[BLOCKED_BY_EGG]"
    
    def get_statistics(self) -> dict:
        """
        Get statistics about blocked content.
        
        Returns:
            Dictionary with blocking statistics
        """
        return {
            'total_blocked': self.blocked_count,
            'enabled': self.enabled,
            'fingerprints_logged': len(self.blocked_fingerprints)
        }
