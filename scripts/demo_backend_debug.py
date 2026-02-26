#!/usr/bin/env python3
"""
Demonstrate backend selection debug logging.

This script shows how the debug logs help diagnose backend selection.
"""

import os
import sys

# Add backend to path
sys.path.insert(0, "/home/runner/work/red-set-protocell/red-set-protocell/backend")


def test_backend(backend_type, api_key_name, api_key_value):
    """Test backend selection with debug logging."""
    print("\n" + "=" * 70)
    print(f"Testing: {backend_type.upper()}")
    print("=" * 70)

    # Set environment
    os.environ["BACKEND_TYPE"] = backend_type
    os.environ[api_key_name] = api_key_value

    print(f"\nEnvironment:")
    print(f"  BACKEND_TYPE = {backend_type}")
    print(f"  {api_key_name} = <set>")

    # Import fresh each time
    from importlib import reload
    from app.core import config as config_module

    reload(config_module)
    from app.core.config import load_config_from_env

    # Load config
    cfg = load_config_from_env()

    print(f"\nConfig Loaded:")
    print(f"  config.target.backend = {cfg.target.backend}")
    print(f"  config.target.backend.value = {cfg.target.backend.value}")

    print(f"\nExpected: {backend_type}")
    print(f"Actual: {cfg.target.backend.value}")

    if cfg.target.backend.value == backend_type:
        print("✅ PASS: Backend correctly selected")
    else:
        print("❌ FAIL: Backend mismatch")
        return False

    # Try to create the backend (will fail due to missing deps, but shows logs)
    print("\nCreating backend (check debug logs below):")
    try:
        from app.main import setup_system

        orchestrator = setup_system(cfg)
        print("  ✅ Setup succeeded")
    except ImportError as e:
        print(f"  ⚠ Import error (expected): {str(e)[:60]}...")
    except Exception as e:
        print(f"  ⚠ Error: {type(e).__name__}: {str(e)[:60]}...")

    # Clean up env
    if "BACKEND_TYPE" in os.environ:
        del os.environ["BACKEND_TYPE"]
    if api_key_name in os.environ:
        del os.environ[api_key_name]

    return True


def main():
    """Test all backends."""
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║           Backend Selection Debug Logging Demonstration             ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝

This script demonstrates the debug logging that helps diagnose backend
selection issues. Watch for the "DEBUG" logs showing exactly which
backend is being selected.
""")

    tests = [
        ("openrouter", "OPENROUTER_API_KEY", "sk-or-test"),
        ("openai", "OPENAI_API_KEY", "sk-test"),
        ("anthropic", "ANTHROPIC_API_KEY", "sk-ant-test"),
    ]

    results = []
    for backend_type, api_key_name, api_key_value in tests:
        passed = test_backend(backend_type, api_key_name, api_key_value)
        results.append((backend_type, passed))

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    for backend_type, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}: {backend_type}")

    all_passed = all(passed for _, passed in results)

    if all_passed:
        print("\n🎉 All backend selections working correctly!")
    else:
        print("\n❌ Some backend selections failed")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
