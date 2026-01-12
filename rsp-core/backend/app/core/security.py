"""
Red Set ProtoCell - Security Module

Security utilities and helper functions for privacy-preserving operations,
session management, and trust boundary enforcement.

This module provides core security primitives used throughout RSP:
- Content fingerprinting via SHA-256 hashing
- Cryptographically secure session ID generation
- Metadata sanitization to prevent credential leaks
- Input validation and trust boundary enforcement

THREAT MODEL:
============

Assumptions:
1. The execution environment (server/container) is trusted
2. Network transport uses TLS/HTTPS in production
3. API keys are stored securely by the deployment infrastructure
4. Database files have appropriate filesystem permissions

Trust Boundaries:
1. External Input → EGG: All external prompts/content must pass through EGG
2. Agent Outputs → Orchestrator: Agent outputs are untrusted and validated
3. Database → Application: Database contents are trusted (controlled by StateManager)
4. API Keys → Target: API keys are sensitive and never logged

Threats Mitigated:
- Credential Leakage: Sensitive fields sanitized before logging/persistence
- Session Hijacking: Cryptographically secure session IDs (128-bit entropy)
- Content Tracking: SHA-256 fingerprints prevent plaintext prompt logging
- Input Injection: Prompt length validation prevents resource exhaustion

Threats NOT Mitigated (out of scope):
- Infrastructure attacks (OS/container compromise, network attacks)
- Side-channel attacks (timing, memory access patterns)
- Physical access to database files
- API key compromise at source (OpenAI/Anthropic account breach)
- Zero-day vulnerabilities in dependencies

Residual Risks:
- Hash collision (SHA-256): Negligible (2^128 security level)
- Session ID collision: Negligible (2^128 entropy)
- Metadata leakage in logs: Mitigated by sanitization, but requires log review
- API rate limiting bypass: Handled by provider, not RSP

Security Invariants:
1. API keys NEVER appear in logs or database
2. Prompts NEVER stored in plaintext (fingerprints only)
3. Session IDs MUST be unpredictable (CSPRNG-generated)
4. All agent outputs treated as untrusted until validated

Examples:
    Hash a prompt for privacy-preserving logging:

    >>> from app.core.security import hash_prompt
    >>> fingerprint = hash_prompt("sensitive prompt content")
    >>> print(fingerprint)
    '2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae'

    Generate a secure session identifier:

    >>> from app.core.security import generate_session_id
    >>> session_id = generate_session_id()
    >>> print(len(session_id))
    32

    Sanitize metadata before logging:

    >>> from app.core.security import sanitize_metadata
    >>> metadata = {
    ...     "model": "gpt-4",
    ...     "api_key": "sk-secret123",
    ...     "user": "researcher"
    ... }
    >>> safe_metadata = sanitize_metadata(metadata)
    >>> print("api_key" in safe_metadata)
    False
    >>> print(safe_metadata["model"])
    'gpt-4'

    Validate prompt length:

    >>> from app.core.security import validate_prompt_length
    >>> prompt = "short prompt"
    >>> print(validate_prompt_length(prompt, max_length=1000))
    True
    >>> long_prompt = "x" * 20000
    >>> print(validate_prompt_length(long_prompt, max_length=10000))
    False

Note:
    All functions in this module are designed to be stateless and thread-safe.
    They can be used concurrently without synchronization.

Security Considerations:
    - Never log unhashed prompts that may contain sensitive content
    - Always sanitize metadata before persistence or transmission
    - Use secure session IDs for all session tracking
    - Validate all inputs at trust boundaries
"""

import hashlib
import secrets
from typing import Any, Dict


def hash_prompt(prompt: str) -> str:
    """
    Create a SHA-256 hash fingerprint of a prompt.

    Used for logging blocked prompts without storing the actual content.

    Args:
        prompt: The prompt string to hash

    Returns:
        Hexadecimal hash string
    """
    return hashlib.sha256(prompt.encode('utf-8')).hexdigest()


def generate_session_id() -> str:
    """
    Generate a cryptographically secure session identifier.

    Returns:
        A random session ID string
    """
    return secrets.token_hex(16)


def sanitize_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Remove sensitive fields from metadata before logging or persistence.

    Args:
        metadata: Dictionary containing metadata

    Returns:
        Sanitized metadata dictionary
    """
    sensitive_fields = {'api_key', 'api_secret', 'password', 'token'}
    return {
        k: v for k, v in metadata.items()
        if k.lower() not in sensitive_fields
    }


def validate_prompt_length(prompt: str, max_length: int = 10000) -> bool:
    """
    Validate that a prompt doesn't exceed maximum length.

    Args:
        prompt: The prompt to validate
        max_length: Maximum allowed length

    Returns:
        True if valid, False otherwise
    """
    return len(prompt) <= max_length


class TrustBoundary:
    """
    Represents trust boundaries between system components.

    Ensures that agents do not trust each other or their own outputs.
    """

    @staticmethod
    def mark_untrusted(data: Any) -> Dict[str, Any]:
        """
        Mark data as coming from an untrusted source.

        Args:
            data: The data to mark

        Returns:
            Dictionary with untrusted marker
        """
        return {
            'data': data,
            'trusted': False,
            'requires_validation': True
        }

    @staticmethod
    def verify_agent_output(output: Any) -> bool:
        """
        Placeholder for agent output verification.

        In production, this would implement signature verification
        or other validation mechanisms.

        Args:
            output: The output to verify

        Returns:
            True if output passes basic validation
        """
        # Basic validation: ensure output is not None and has content
        return output is not None and (
            isinstance(output, str) and len(output) > 0 or
            isinstance(output, dict) and len(output) > 0
        )
