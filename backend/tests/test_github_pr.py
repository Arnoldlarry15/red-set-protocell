"""
Tests for the GitHub Pull Request management endpoints and utility module.
"""

import os
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


def _fake_openai_key(suffix: str = "test-key") -> str:
    return "sk-" + suffix


# Environment setup before importing the app
os.environ.setdefault("RSP_DEMO_PASSWORD", "test_demo_password_not_real")
os.environ.setdefault("RSP_ALLOWED_ORIGINS", "http://localhost:3000")
os.environ.setdefault("OPENAI_API_KEY", _fake_openai_key())

from app.api_server import app  # noqa: E402
import app.github_pr as github_pr_module  # noqa: E402

client = TestClient(app)

FAKE_TOKEN = "ghp_faketoken1234"
FAKE_OWNER = "test-owner"
FAKE_REPO = "test-repo"


# ---------------------------------------------------------------------------
# Unit tests for github_pr module
# ---------------------------------------------------------------------------


class TestGitHubPRModule:
    """Unit tests for the github_pr utility functions."""

    def _make_response(self, status_code: int, json_data: object) -> MagicMock:
        resp = MagicMock()
        resp.status_code = status_code
        resp.ok = status_code < 400
        resp.json.return_value = json_data
        resp.text = str(json_data)
        return resp

    def test_list_pull_requests_success(self):
        """list_pull_requests returns normalised PR dicts on success."""
        raw_prs = [
            {
                "number": 1,
                "title": "Test PR",
                "state": "open",
                "draft": False,
                "merged": False,
                "html_url": "https://github.com/test/1",
                "body": "desc",
                "user": {"login": "alice"},
                "head": {"ref": "feature"},
                "base": {"ref": "main"},
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-02T00:00:00Z",
                "mergeable": True,
            }
        ]
        mock_resp = self._make_response(200, raw_prs)
        with patch("app.github_pr.requests.get", return_value=mock_resp):
            result = github_pr_module.list_pull_requests(FAKE_OWNER, FAKE_REPO, FAKE_TOKEN)
        assert len(result) == 1
        assert result[0]["number"] == 1
        assert result[0]["title"] == "Test PR"
        assert result[0]["user"] == "alice"
        assert result[0]["head"] == "feature"

    def test_list_pull_requests_api_error_raises(self):
        """list_pull_requests raises ValueError on non-2xx response."""
        mock_resp = self._make_response(401, {"message": "Bad credentials"})
        with patch("app.github_pr.requests.get", return_value=mock_resp):
            with pytest.raises(ValueError, match="Bad credentials"):
                github_pr_module.list_pull_requests(FAKE_OWNER, FAKE_REPO, FAKE_TOKEN)

    def test_close_pull_request_success(self):
        """close_pull_request returns PR info on success."""
        raw_pr = {"number": 5, "title": "Close me", "state": "closed", "html_url": "https://github.com/x"}
        mock_resp = self._make_response(200, raw_pr)
        with patch("app.github_pr.requests.patch", return_value=mock_resp):
            result = github_pr_module.close_pull_request(FAKE_OWNER, FAKE_REPO, 5, FAKE_TOKEN)
        assert result["number"] == 5
        assert result["state"] == "closed"

    def test_close_pull_request_api_error_raises(self):
        """close_pull_request raises ValueError on failure."""
        mock_resp = self._make_response(404, {"message": "Not Found"})
        with patch("app.github_pr.requests.patch", return_value=mock_resp):
            with pytest.raises(ValueError, match="Not Found"):
                github_pr_module.close_pull_request(FAKE_OWNER, FAKE_REPO, 999, FAKE_TOKEN)

    def test_merge_pull_request_success(self):
        """merge_pull_request returns merge result on success."""
        raw_result = {"sha": "abc123", "merged": True, "message": "Pull Request successfully merged"}
        mock_resp = self._make_response(200, raw_result)
        with patch("app.github_pr.requests.put", return_value=mock_resp):
            result = github_pr_module.merge_pull_request(FAKE_OWNER, FAKE_REPO, 3, FAKE_TOKEN)
        assert result["merged"] is True

    def test_merge_pull_request_invalid_method_raises(self):
        """merge_pull_request raises ValueError for unknown merge_method."""
        with pytest.raises(ValueError, match="Invalid merge_method"):
            github_pr_module.merge_pull_request(FAKE_OWNER, FAKE_REPO, 1, FAKE_TOKEN, merge_method="invalid")

    def test_merge_pull_request_api_error_raises(self):
        """merge_pull_request raises ValueError on 4xx response."""
        mock_resp = self._make_response(405, {"message": "Pull Request is not mergeable"})
        with patch("app.github_pr.requests.put", return_value=mock_resp):
            with pytest.raises(ValueError, match="not mergeable"):
                github_pr_module.merge_pull_request(FAKE_OWNER, FAKE_REPO, 2, FAKE_TOKEN)


# ---------------------------------------------------------------------------
# API endpoint integration tests
# ---------------------------------------------------------------------------


class TestGitHubPREndpoints:
    """Integration tests for /github/prs API endpoints."""

    def _list_payload(self, **kwargs) -> dict:
        base = {"owner": FAKE_OWNER, "repo": FAKE_REPO, "github_token": FAKE_TOKEN}
        base.update(kwargs)
        return base

    def _action_payload(self) -> dict:
        return {"owner": FAKE_OWNER, "repo": FAKE_REPO, "github_token": FAKE_TOKEN}

    def _make_mock_response(self, status_code: int, json_data: object) -> MagicMock:
        resp = MagicMock()
        resp.status_code = status_code
        resp.ok = status_code < 400
        resp.json.return_value = json_data
        resp.text = str(json_data)
        return resp

    def test_list_prs_success(self):
        """POST /github/prs returns pull_requests list."""
        raw_prs = [
            {
                "number": 10,
                "title": "My PR",
                "state": "open",
                "draft": False,
                "merged": False,
                "html_url": "https://github.com/test/10",
                "body": "",
                "user": {"login": "bob"},
                "head": {"ref": "dev"},
                "base": {"ref": "main"},
                "created_at": None,
                "updated_at": None,
                "mergeable": None,
            }
        ]
        mock_resp = self._make_mock_response(200, raw_prs)
        with patch("app.github_pr.requests.get", return_value=mock_resp):
            response = client.post("/github/prs", json=self._list_payload())
        assert response.status_code == 200
        data = response.json()
        assert "pull_requests" in data
        assert data["count"] == 1
        assert data["pull_requests"][0]["number"] == 10

    def test_list_prs_github_error_returns_422(self):
        """POST /github/prs returns 422 when GitHub API returns an error."""
        mock_resp = self._make_mock_response(401, {"message": "Bad credentials"})
        with patch("app.github_pr.requests.get", return_value=mock_resp):
            response = client.post("/github/prs", json=self._list_payload())
        assert response.status_code == 422

    def test_close_pr_success(self):
        """POST /github/prs/{pr_number}/close returns closed PR info."""
        raw_pr = {"number": 7, "title": "Fix bug", "state": "closed", "html_url": "https://github.com/test/7"}
        mock_resp = self._make_mock_response(200, raw_pr)
        with patch("app.github_pr.requests.patch", return_value=mock_resp):
            response = client.post("/github/prs/7/close", json=self._action_payload())
        assert response.status_code == 200
        assert response.json()["state"] == "closed"

    def test_close_pr_not_found_returns_422(self):
        """POST /github/prs/{pr_number}/close returns 422 for missing PR."""
        mock_resp = self._make_mock_response(404, {"message": "Not Found"})
        with patch("app.github_pr.requests.patch", return_value=mock_resp):
            response = client.post("/github/prs/9999/close", json=self._action_payload())
        assert response.status_code == 422

    def test_merge_pr_success(self):
        """POST /github/prs/{pr_number}/merge returns merge result."""
        raw_result = {"sha": "deadbeef", "merged": True, "message": "Pull Request successfully merged"}
        mock_resp = self._make_mock_response(200, raw_result)
        with patch("app.github_pr.requests.put", return_value=mock_resp):
            response = client.post(
                "/github/prs/4/merge",
                json={**self._action_payload(), "merge_method": "squash"},
            )
        assert response.status_code == 200
        assert response.json()["merged"] is True

    def test_merge_pr_invalid_method_returns_422(self):
        """POST /github/prs/{pr_number}/merge returns 422 for bad merge_method."""
        response = client.post(
            "/github/prs/4/merge",
            json={**self._action_payload(), "merge_method": "bad-value"},
        )
        assert response.status_code == 422

    def test_merge_pr_not_mergeable_returns_422(self):
        """POST /github/prs/{pr_number}/merge returns 422 when GitHub rejects merge."""
        mock_resp = self._make_mock_response(405, {"message": "Pull Request is not mergeable"})
        with patch("app.github_pr.requests.put", return_value=mock_resp):
            response = client.post("/github/prs/5/merge", json=self._action_payload())
        assert response.status_code == 422

    def test_api_prefix_routes_also_work(self):
        """Routes registered under /api prefix also respond correctly."""
        raw_prs: list = []
        mock_resp = self._make_mock_response(200, raw_prs)
        with patch("app.github_pr.requests.get", return_value=mock_resp):
            response = client.post("/api/github/prs", json=self._list_payload())
        assert response.status_code == 200
        assert response.json()["count"] == 0
