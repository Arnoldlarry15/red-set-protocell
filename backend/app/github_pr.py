"""GitHub Pull Request management utilities.

Provides functions to list, close, and merge pull requests
via the GitHub REST API using a personal access token.
"""

import logging
from typing import Any, Dict, List, Optional

import requests

logger = logging.getLogger(__name__)

GITHUB_API_BASE = "https://api.github.com"


def _get_headers(token: str) -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def _raise_for_github_error(response: requests.Response, action: str) -> None:
    if not response.ok:
        try:
            detail = response.json().get("message", response.text)
        except Exception:
            detail = response.text
        raise ValueError(f"GitHub API error while {action}: {response.status_code} – {detail}")


def list_pull_requests(
    owner: str,
    repo: str,
    token: str,
    state: str = "open",
    per_page: int = 30,
    page: int = 1,
) -> List[Dict[str, Any]]:
    """Return pull requests for *owner/repo* matching *state* ('open', 'closed', 'all')."""
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/pulls"
    params: Dict[str, str | int] = {"state": state, "per_page": per_page, "page": page}
    response = requests.get(url, headers=_get_headers(token), params=params, timeout=15)
    _raise_for_github_error(response, "listing pull requests")
    raw: List[Dict[str, Any]] = response.json()
    return [
        {
            "number": pr["number"],
            "title": pr["title"],
            "state": pr["state"],
            "draft": pr.get("draft", False),
            "merged": pr.get("merged", False),
            "html_url": pr["html_url"],
            "body": pr.get("body") or "",
            "user": pr["user"]["login"] if pr.get("user") else None,
            "head": pr["head"]["ref"] if pr.get("head") else None,
            "base": pr["base"]["ref"] if pr.get("base") else None,
            "created_at": pr.get("created_at"),
            "updated_at": pr.get("updated_at"),
            "mergeable": pr.get("mergeable"),
        }
        for pr in raw
    ]


def close_pull_request(owner: str, repo: str, pr_number: int, token: str) -> Dict[str, Any]:
    """Close the pull request identified by *pr_number* without merging."""
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/pulls/{pr_number}"
    response = requests.patch(url, headers=_get_headers(token), json={"state": "closed"}, timeout=15)
    _raise_for_github_error(response, f"closing PR #{pr_number}")
    pr = response.json()
    return {
        "number": pr["number"],
        "title": pr["title"],
        "state": pr["state"],
        "html_url": pr["html_url"],
    }


def merge_pull_request(
    owner: str,
    repo: str,
    pr_number: int,
    token: str,
    commit_title: Optional[str] = None,
    commit_message: Optional[str] = None,
    merge_method: str = "merge",
) -> Dict[str, Any]:
    """Merge the pull request identified by *pr_number*.

    *merge_method* must be one of: 'merge', 'squash', 'rebase'.
    """
    if merge_method not in ("merge", "squash", "rebase"):
        raise ValueError(f"Invalid merge_method '{merge_method}'. Must be merge, squash, or rebase.")

    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/pulls/{pr_number}/merge"
    payload: Dict[str, Any] = {"merge_method": merge_method}
    if commit_title:
        payload["commit_title"] = commit_title
    if commit_message:
        payload["commit_message"] = commit_message

    response = requests.put(url, headers=_get_headers(token), json=payload, timeout=15)
    _raise_for_github_error(response, f"merging PR #{pr_number}")
    return response.json()
