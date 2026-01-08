"""
Red Set ProtoCell - Security Module

Security utilities and helper functions.
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
