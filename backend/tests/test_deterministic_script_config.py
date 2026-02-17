"""
Test that run_deterministic_experiment.py uses load_config_from_env().

This test ensures that the script respects environment variables for
backend selection and API keys.
"""

import os
from pathlib import Path

from app.core.config import ModelBackend


def test_deterministic_script_imports_load_config_from_env():
    """Verify the script imports load_config_from_env, not get_default_config."""
    # Get script path relative to this test file (platform-independent)
    test_dir = Path(__file__).parent
    repo_root = test_dir.parent.parent
    script_path = repo_root / "scripts" / "run_deterministic_experiment.py"

    # Read the script content
    with open(script_path, 'r') as f:
        content = f.read()

    # Verify it imports load_config_from_env
    assert "from app.core.config import load_config_from_env" in content, \
        "Script must import load_config_from_env"

    # Verify it doesn't import get_default_config
    assert "from app.core.config import get_default_config" not in content, \
        "Script should not import get_default_config"


def test_deterministic_script_uses_load_config_from_env():
    """Verify the script calls load_config_from_env() to get config."""
    # Get script path relative to this test file (platform-independent)
    test_dir = Path(__file__).parent
    repo_root = test_dir.parent.parent
    script_path = repo_root / "scripts" / "run_deterministic_experiment.py"

    # Read the script content
    with open(script_path, 'r') as f:
        content = f.read()

    # Verify it calls load_config_from_env()
    assert "load_config_from_env()" in content, \
        "Script must call load_config_from_env() to get configuration"

    # Count occurrences to ensure all config creations use it
    load_config_count = content.count("load_config_from_env()")

    # Should have at least 3 calls (run_session, verify_determinism run1, verify_determinism run2)
    assert load_config_count >= 3, \
        f"Expected at least 3 calls to load_config_from_env(), found {load_config_count}"


def test_config_respects_openrouter_environment_variable(monkeypatch):
    """Verify that load_config_from_env() respects OPENROUTER_API_KEY when BACKEND_TYPE=openrouter."""
    from app.core.config import load_config_from_env

    # Clear any existing backend env vars
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    # Set OpenRouter backend and API key
    monkeypatch.setenv("BACKEND_TYPE", "openrouter")
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-openrouter-key")

    # Load config
    config = load_config_from_env()

    # Verify backend is set to OpenRouter
    assert config.target.backend == ModelBackend.OPENROUTER, \
        "Backend should be OPENROUTER when BACKEND_TYPE=openrouter"

    # Verify API key is loaded
    assert config.target.api_key == "test-openrouter-key", \
        "API key should be loaded from OPENROUTER_API_KEY"

    assert config.target.openrouter_api_key == "test-openrouter-key", \
        "openrouter_api_key should also be set"
