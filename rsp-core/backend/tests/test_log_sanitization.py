"""
Tests for log injection prevention in API server.
"""

from app.api_server import sanitize_for_logging


class TestLogSanitization:
    """Test the sanitize_for_logging function."""

    def test_normal_string(self):
        """Test that normal strings pass through unchanged."""
        result = sanitize_for_logging("john_doe")
        assert result == "john_doe"

    def test_removes_newlines(self):
        """Test that newlines are removed."""
        result = sanitize_for_logging("john\ndoe")
        assert result == "johndoe"
        assert "\n" not in result

    def test_removes_carriage_returns(self):
        """Test that carriage returns are removed."""
        result = sanitize_for_logging("john\rdoe")
        assert result == "johndoe"
        assert "\r" not in result

    def test_removes_multiple_control_chars(self):
        """Test that multiple control characters are removed."""
        result = sanitize_for_logging("john\n\rdoe\x0b\x0csmith")
        assert result == "johndoesmith"
        assert "\n" not in result
        assert "\r" not in result

    def test_removes_null_bytes(self):
        """Test that null bytes are removed."""
        result = sanitize_for_logging("john\x00doe")
        assert result == "johndoe"
        assert "\x00" not in result

    def test_truncates_long_strings(self):
        """Test that long strings are truncated."""
        long_string = "a" * 150
        result = sanitize_for_logging(long_string, max_length=100)
        assert len(result) == 103  # 100 chars + "..."
        assert result.endswith("...")

    def test_empty_string(self):
        """Test that empty strings are handled."""
        result = sanitize_for_logging("")
        assert result == "[empty]"

    def test_none_value(self):
        """Test that None is handled."""
        result = sanitize_for_logging(None)
        assert result == "[empty]"

    def test_only_control_chars(self):
        """Test strings with only control characters."""
        result = sanitize_for_logging("\n\r\x0b")
        assert result == "[invalid]"

    def test_whitespace_preserved(self):
        """Test that normal whitespace is preserved."""
        result = sanitize_for_logging("john doe smith")
        assert result == "john doe smith"

    def test_special_chars_preserved(self):
        """Test that special characters (not control) are preserved."""
        result = sanitize_for_logging("john@doe.com")
        assert result == "john@doe.com"

    def test_log_injection_attempt(self):
        """Test that log injection attempts are neutralized."""
        # Simulate attacker trying to inject fake log entry
        malicious = "admin\n2024-01-01 00:00:00 - CRITICAL - System compromised"
        result = sanitize_for_logging(malicious)
        assert "\n" not in result
        assert result == "admin2024-01-01 00:00:00 - CRITICAL - System compromised"

    def test_log_forging_attempt(self):
        """Test that log forging with carriage returns is prevented."""
        # Attacker trying to overwrite previous log line
        malicious = "user123\rroot logged in successfully"
        result = sanitize_for_logging(malicious)
        assert "\r" not in result
        assert result == "user123root logged in successfully"

    def test_unicode_preserved(self):
        """Test that unicode characters are preserved."""
        result = sanitize_for_logging("josé_garcía")
        assert result == "josé_garcía"

    def test_emoji_preserved(self):
        """Test that emoji are preserved."""
        result = sanitize_for_logging("user_😀")
        assert result == "user_😀"
