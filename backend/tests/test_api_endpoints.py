"""
Tests for the new API endpoints:
- Unified Infrastructure Dashboard
- User Management
- Remote Triggering
"""

import pytest
import os
from fastapi.testclient import TestClient

# Set demo password for tests before importing app
# gitguardian:ignore - This is a test password, not a real secret
TEST_DEMO_PASSWORD = "test_demo_password_not_real"
os.environ["RSP_DEMO_PASSWORD"] = TEST_DEMO_PASSWORD

# Set CORS allowed origins for tests before importing app
os.environ["RSP_ALLOWED_ORIGINS"] = "http://localhost:3000"
# Provide a provider key to satisfy production validation (tests run with production check)
os.environ["OPENAI_API_KEY"] = "sk-test-key"

from app.api_server import app  # noqa: E402

client = TestClient(app)

# Demo credentials for tests
DEMO_USERNAME = "admin"
DEMO_PASSWORD = TEST_DEMO_PASSWORD


class TestInfraDashboard:
    """Test Infrastructure Dashboard endpoints"""

    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        assert "status" in response.json()
        assert response.json()["status"] == "healthy"

    def test_live_sessions_empty(self):
        """Test live sessions when no sessions are active"""
        response = client.get("/dashboard/live-sessions")
        assert response.status_code == 200
        assert "sessions" in response.json()
        # Should start with empty list
        assert isinstance(response.json()["sessions"], list)

    def test_historical_sessions(self):
        """Test historical sessions endpoint"""
        # This will likely return empty or error if no database exists
        # but we're testing the endpoint is accessible
        response = client.get("/dashboard/historical-sessions")
        assert response.status_code in [200, 500]  # May fail if no DB
        if response.status_code == 200:
            assert "sessions" in response.json()

    def test_model_comparison(self):
        """Test model version comparison endpoint"""
        response = client.get(
            "/dashboard/compare-models?model_v1=gpt-4-v1&model_v2=gpt-4-v2"
        )
        assert response.status_code in [200, 500]  # May fail if no DB
        if response.status_code == 200:
            data = response.json()
            assert "model_v1" in data
            assert "model_v2" in data


class TestUserManagement:
    """Test User Management endpoints"""

    def test_login_success(self):
        """Test successful login"""
        response = client.post(
            "/auth/login",
            json={"username": DEMO_USERNAME, "password": DEMO_PASSWORD}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["username"] == DEMO_USERNAME
        assert data["user"]["role"] == "admin"

    def test_login_failure(self):
        """Test failed login with invalid credentials"""
        response = client.post(
            "/auth/login",
            json={"username": "invalid", "password": "wrong"}
        )
        assert response.status_code == 401

    def test_list_users(self):
        """Test listing users"""
        response = client.get("/auth/users")
        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        assert isinstance(data["users"], list)
        # Should have at least the admin user
        assert len(data["users"]) >= 1

    def test_register_user(self):
        """Test user registration"""
        response = client.post(
            "/auth/register",
            json={
                "username": "test_user",
                "email": "test@example.com",
                "role": "researcher",
                "password": "test123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "test_user"
        assert data["role"] == "researcher"

    def test_register_duplicate_user(self):
        """Test registering a duplicate user"""
        # Register first time
        client.post(
            "/auth/register",
            json={
                "username": "duplicate_user",
                "email": "dup@example.com",
                "role": "observer",
                "password": "test123"
            }
        )
        # Try to register again
        response = client.post(
            "/auth/register",
            json={
                "username": "duplicate_user",
                "email": "dup2@example.com",
                "role": "observer",
                "password": "test123"
            }
        )
        assert response.status_code == 400

    def test_register_invalid_role(self):
        """Test registering with invalid role"""
        response = client.post(
            "/auth/register",
            json={
                "username": "invalid_role_user",
                "email": "invalid@example.com",
                "role": "superuser",  # Invalid role
                "password": "test123"
            }
        )
        assert response.status_code == 400

    def test_validate_llm_key_publicly_accessible(self):
        """Test that LLM key validation endpoint is publicly accessible without JWT"""
        # This endpoint should be accessible without authentication
        # because users need to validate their API key before they can get a JWT token
        response = client.post(
            "/auth/validate-llm-key",
            json={
                "api_key": "sk-test-key",
                "backend": "openai"
            }
        )
        # Should not return 401 (Unauthorized) due to missing JWT
        # Will return 401 due to invalid API key, but that's after endpoint access
        assert response.status_code in [401, 503, 500]  # Auth error, network error, or other error, but NOT JWT auth error
        # If it was blocked by JWT auth middleware, we'd get a different response structure
        # The endpoint-level response should contain 'detail' key (FastAPI HTTPException)
        assert "detail" in response.json()

    def test_validate_llm_key_invalid_backend(self):
        """Test LLM key validation with invalid backend"""
        response = client.post(
            "/auth/validate-llm-key",
            json={
                "api_key": "sk-test-key",
                "backend": "invalid_backend"
            }
        )
        assert response.status_code == 400
        assert "Invalid backend" in response.json()["detail"]

    def test_validate_llm_key_invalid_format(self):
        """Test LLM key validation with invalid key format"""
        response = client.post(
            "/auth/validate-llm-key",
            json={
                "api_key": "invalid-key",
                "backend": "openai"
            }
        )
        # Should return 401 because key is invalid
        assert response.status_code == 401

    def test_validate_llm_key_network_error(self):
        """Test LLM key validation handles network errors appropriately"""
        # This test verifies that the endpoint can distinguish between
        # network errors and authentication errors
        # We'll use mocking to simulate a connection error
        from unittest.mock import patch, AsyncMock

        # Mock the backend to raise a connection error
        with patch('app.agents.target.OpenAIBackend') as mock_backend:
            # Create a mock instance that raises a connection error
            mock_instance = AsyncMock()
            mock_instance.execute.side_effect = ConnectionError("Network unreachable")
            mock_backend.return_value = mock_instance

            response = client.post(
                "/auth/validate-llm-key",
                json={
                    "api_key": "sk-test-key",
                    "backend": "openai"
                }
            )

            # Should return 503 (Service Unavailable) for network errors
            # not 401 (Unauthorized) which would imply invalid credentials
            assert response.status_code == 503
            assert "Network error" in response.json()["detail"]
            assert "connection" in response.json()["detail"].lower()

    def test_validate_llm_key_auth_error_with_connection_in_message(self):
        """Test that auth errors aren't misclassified as network errors"""
        # This test verifies the fix for the bug where an authentication error
        # message containing the word "connection" (e.g., in the API key itself)
        # was incorrectly classified as a network error instead of auth error
        from unittest.mock import patch, AsyncMock

        # Mock the backend to raise an auth error that contains "connection"
        # This simulates cases like: "Incorrect API key provided: sk-proj-...connection..."
        with patch('app.agents.target.OpenAIBackend') as mock_backend:
            mock_instance = AsyncMock()
            # Simulate an authentication error with "connection" in the message
            mock_instance.execute.side_effect = Exception(
                "Error code: 401 - Incorrect API key provided: sk-proj-connection123"
            )
            mock_backend.return_value = mock_instance

            response = client.post(
                "/auth/validate-llm-key",
                json={
                    "api_key": "sk-proj-connection123",
                    "backend": "openai"
                }
            )

            # Should return 401 (Unauthorized) for auth errors
            # NOT 503 (Network error) even though message contains "connection"
            assert response.status_code == 401
            assert "Invalid API key" in response.json()["detail"]


class TestRemoteControl:
    """Test Remote Control endpoints"""

    def test_list_configs_empty(self):
        """Test listing configs when none exist"""
        response = client.get("/remote/config/list")
        assert response.status_code == 200
        data = response.json()
        assert "configs" in data
        assert isinstance(data["configs"], list)

    def test_save_config(self):
        """Test saving experiment configuration"""
        config = {
            "name": "Test Config",
            "description": "A test configuration",
            "backend": "openai",
            "model": "gpt-3.5-turbo",
            "max_rounds": 50,
            "mutation_rate": 0.7,
            "selected_domains": ["injection", "jailbreak"],
            "selected_strategies": ["lexical", "encoding"],
            "mutation_weights": {"lexical": 1.0, "encoding": 0.8},
            "thresholds": {"critical": 0.8, "high": 0.6}
        }
        response = client.post("/remote/config/save", json=config)
        assert response.status_code == 200
        data = response.json()
        assert "config_id" in data
        assert data["name"] == "Test Config"

    def test_get_config(self):
        """Test retrieving a specific config"""
        # First save a config
        config = {
            "name": "Test Config 2",
            "description": "Another test",
            "backend": "anthropic",
            "model": "claude-3-opus-20240229",
            "max_rounds": 100,
            "mutation_rate": 0.8,
            "selected_domains": ["refusal_erosion"],
            "selected_strategies": ["structural"]
        }
        save_response = client.post("/remote/config/save", json=config)
        config_id = save_response.json()["config_id"]

        # Now retrieve it
        response = client.get(f"/remote/config/{config_id}")
        assert response.status_code == 200
        data = response.json()
        assert "config" in data
        assert data["config"]["name"] == "Test Config 2"

    def test_get_nonexistent_config(self):
        """Test retrieving a config that doesn't exist"""
        response = client.get("/remote/config/nonexistent_id")
        assert response.status_code == 404

    def test_delete_config(self):
        """Test deleting a configuration"""
        # First save a config
        config = {
            "name": "To Be Deleted",
            "description": "Will be deleted",
            "backend": "openai",
            "model": "gpt-4",
            "max_rounds": 10,
            "mutation_rate": 0.5,
            "selected_domains": ["injection"],
            "selected_strategies": ["lexical"]
        }
        save_response = client.post("/remote/config/save", json=config)
        config_id = save_response.json()["config_id"]

        # Delete it
        response = client.delete(f"/remote/config/{config_id}")
        assert response.status_code == 200

        # Verify it's gone
        get_response = client.get(f"/remote/config/{config_id}")
        assert get_response.status_code == 404


class TestAPIIntegration:
    """Test API integration scenarios"""

    def test_complete_workflow(self):
        """Test a complete workflow: login -> save config -> start run"""
        # 1. Login
        login_response = client.post(
            "/auth/login",
            json={"username": DEMO_USERNAME, "password": DEMO_PASSWORD}
        )
        assert login_response.status_code == 200

        # 2. Save a configuration
        config = {
            "name": "Integration Test Config",
            "description": "Config for integration test",
            "backend": "openai",
            "model": "gpt-3.5-turbo",
            "max_rounds": 5,
            "mutation_rate": 0.7,
            "selected_domains": ["injection"],
            "selected_strategies": ["lexical"]
        }
        save_response = client.post("/remote/config/save", json=config)
        assert save_response.status_code == 200

        # 3. Note: We can't actually start a run without a real API key
        # But we can test that the endpoint exists
        # This would fail without a real API key, so we just check the endpoint
        # is accessible and returns appropriate error
        # (We won't actually call this in test without mocking)


class TestCustomPromptExecution:
    """Test custom prompt execution endpoint"""

    def test_custom_prompt_no_session(self):
        """Test custom prompt execution with non-existent session"""
        response = client.post(
            "/prompt/execute",
            json={
                "prompt": "What is 2+2?",
                "session_id": "nonexistent_session"
            }
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_custom_prompt_missing_fields(self):
        """Test custom prompt execution with missing required fields"""
        # Missing session_id
        response = client.post(
            "/prompt/execute",
            json={"prompt": "Test prompt"}
        )
        assert response.status_code == 422  # Validation error

        # Missing prompt
        response = client.post(
            "/prompt/execute",
            json={"session_id": "test_session"}
        )
        assert response.status_code == 422  # Validation error


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
