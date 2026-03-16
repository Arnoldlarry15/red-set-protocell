"""
Tests for core security module.
"""

import pytest

from app.core.security import (
    TrustBoundary,
    generate_session_id,
    hash_prompt,
    sanitize_metadata,
    validate_prompt_length,
)


class TestHashPrompt:
    def test_returns_hex_string(self):
        result = hash_prompt("test prompt")
        assert isinstance(result, str)
        assert len(result) == 64  # SHA-256 hex = 64 chars

    def test_deterministic(self):
        assert hash_prompt("hello") == hash_prompt("hello")

    def test_different_prompts_different_hashes(self):
        assert hash_prompt("hello") != hash_prompt("world")


class TestGenerateSessionId:
    def test_returns_hex_string(self):
        sid = generate_session_id()
        assert isinstance(sid, str)
        assert len(sid) == 32

    def test_unique_ids(self):
        ids = {generate_session_id() for _ in range(10)}
        assert len(ids) == 10


class TestSanitizeMetadata:
    def test_removes_api_key(self):
        meta = {"model": "gpt-4", "api_key": "sk-secret"}
        result = sanitize_metadata(meta)
        assert "api_key" not in result
        assert result["model"] == "gpt-4"

    def test_removes_password(self):
        meta = {"user": "test", "password": "hunter2"}
        result = sanitize_metadata(meta)
        assert "password" not in result
        assert result["user"] == "test"

    def test_removes_token(self):
        meta = {"name": "x", "token": "abc123"}
        result = sanitize_metadata(meta)
        assert "token" not in result

    def test_removes_api_secret(self):
        meta = {"api_secret": "secret", "ok_field": "value"}
        result = sanitize_metadata(meta)
        assert "api_secret" not in result
        assert result["ok_field"] == "value"

    def test_keeps_safe_fields(self):
        meta = {"model": "gpt-4", "version": "1.0", "user": "researcher"}
        result = sanitize_metadata(meta)
        assert result == meta

    def test_empty_metadata(self):
        assert sanitize_metadata({}) == {}


class TestValidatePromptLength:
    def test_valid_short_prompt(self):
        assert validate_prompt_length("short") is True

    def test_valid_prompt_at_limit(self):
        prompt = "x" * 10000
        assert validate_prompt_length(prompt, max_length=10000) is True

    def test_invalid_prompt_over_limit(self):
        prompt = "x" * 10001
        assert validate_prompt_length(prompt, max_length=10000) is False

    def test_custom_max_length(self):
        assert validate_prompt_length("hello world", max_length=5) is False
        assert validate_prompt_length("hi", max_length=5) is True


class TestTrustBoundary:
    def test_mark_untrusted(self):
        result = TrustBoundary.mark_untrusted("some data")
        assert result["data"] == "some data"
        assert result["trusted"] is False
        assert result["requires_validation"] is True

    def test_mark_untrusted_with_dict(self):
        data = {"key": "value"}
        result = TrustBoundary.mark_untrusted(data)
        assert result["data"] == data

    def test_verify_agent_output_valid_string(self):
        assert TrustBoundary.verify_agent_output("valid response") is True

    def test_verify_agent_output_valid_dict(self):
        assert TrustBoundary.verify_agent_output({"key": "value"}) is True

    def test_verify_agent_output_none(self):
        assert TrustBoundary.verify_agent_output(None) is False

    def test_verify_agent_output_empty_string(self):
        assert TrustBoundary.verify_agent_output("") is False

    def test_verify_agent_output_empty_dict(self):
        assert TrustBoundary.verify_agent_output({}) is False
