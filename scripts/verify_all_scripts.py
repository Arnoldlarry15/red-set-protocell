#!/usr/bin/env python3
"""
Comprehensive verification script for all RSP scripts.

This script verifies that all scripts properly use load_config_from_env()
and respect environment variables for backend selection.
"""

import os
import sys

def check_script(filepath, script_name):
    """Check if a script properly uses load_config_from_env."""
    print(f"\n{'='*70}")
    print(f"Checking: {script_name}")
    print(f"{'='*70}")
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Check imports
    has_load_config = 'load_config_from_env' in content
    has_get_default = 'get_default_config' in content
    
    # Count usages
    load_count = content.count('load_config_from_env()')
    default_count = content.count('get_default_config()')
    
    print(f"✓ Imports load_config_from_env: {'YES' if has_load_config else 'NO'}")
    print(f"✓ Does NOT import get_default_config: {'YES' if not has_get_default else 'NO'}")
    print(f"✓ Calls to load_config_from_env(): {load_count}")
    print(f"✓ Calls to get_default_config(): {default_count}")
    
    # Verdict
    if has_load_config and not has_get_default and load_count > 0 and default_count == 0:
        print(f"\n✅ PASS: {script_name} correctly uses load_config_from_env()")
        return True
    else:
        print(f"\n❌ FAIL: {script_name} needs fixing")
        return False


def verify_config_loader():
    """Verify the config loader works correctly with different backends."""
    print(f"\n{'='*70}")
    print("Verifying Config Loader")
    print(f"{'='*70}")
    
    sys.path.insert(0, '/home/runner/work/red-set-protocell/red-set-protocell/backend')
    from app.core.config import load_config_from_env, ModelBackend
    
    tests_passed = 0
    tests_total = 3
    
    # Test 1: OpenRouter
    print("\n1. Testing OpenRouter backend...")
    os.environ['BACKEND_TYPE'] = 'openrouter'
    os.environ['OPENROUTER_API_KEY'] = 'test-key'
    config = load_config_from_env()
    if config.target.backend == ModelBackend.OPENROUTER:
        print("   ✅ OpenRouter backend loaded correctly")
        tests_passed += 1
    else:
        print(f"   ❌ Expected OPENROUTER, got {config.target.backend}")
    
    # Test 2: OpenAI (default)
    print("\n2. Testing OpenAI backend (default)...")
    del os.environ['BACKEND_TYPE']
    os.environ['OPENAI_API_KEY'] = 'test-key'
    if 'OPENROUTER_API_KEY' in os.environ:
        del os.environ['OPENROUTER_API_KEY']
    config = load_config_from_env()
    if config.target.backend == ModelBackend.OPENAI:
        print("   ✅ OpenAI backend loaded correctly")
        tests_passed += 1
    else:
        print(f"   ❌ Expected OPENAI, got {config.target.backend}")
    
    # Test 3: Anthropic
    print("\n3. Testing Anthropic backend...")
    os.environ['BACKEND_TYPE'] = 'anthropic'
    os.environ['ANTHROPIC_API_KEY'] = 'test-key'
    config = load_config_from_env()
    if config.target.backend == ModelBackend.ANTHROPIC:
        print("   ✅ Anthropic backend loaded correctly")
        tests_passed += 1
    else:
        print(f"   ❌ Expected ANTHROPIC, got {config.target.backend}")
    
    print(f"\nConfig loader tests: {tests_passed}/{tests_total} passed")
    return tests_passed == tests_total


def main():
    """Main verification function."""
    print("""
    ╔═══════════════════════════════════════════════════════════════════╗
    ║                                                                   ║
    ║       RSP Scripts Verification - Config Loader Fix                ║
    ║       Ensuring all scripts respect environment variables          ║
    ║                                                                   ║
    ╚═══════════════════════════════════════════════════════════════════╝
    """)
    
    base_path = '/home/runner/work/red-set-protocell/red-set-protocell'
    
    scripts_to_check = [
        (f'{base_path}/scripts/run_deterministic_experiment.py', 'run_deterministic_experiment.py'),
        (f'{base_path}/scripts/run_experiment.py', 'run_experiment.py'),
        (f'{base_path}/backend/examples/benchmarking.py', 'examples/benchmarking.py'),
        (f'{base_path}/backend/examples/time_analytics.py', 'examples/time_analytics.py'),
    ]
    
    # Check all scripts
    results = []
    for filepath, name in scripts_to_check:
        result = check_script(filepath, name)
        results.append((name, result))
    
    # Verify config loader
    config_ok = verify_config_loader()
    
    # Summary
    print(f"\n{'='*70}")
    print("VERIFICATION SUMMARY")
    print(f"{'='*70}")
    
    print("\nScript Checks:")
    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}: {name}")
        if not passed:
            all_passed = False
    
    print(f"\nConfig Loader: {'✅ PASS' if config_ok else '❌ FAIL'}")
    
    if all_passed and config_ok:
        print(f"\n{'='*70}")
        print("🎉 ALL VERIFICATION CHECKS PASSED!")
        print(f"{'='*70}")
        print("\nAll scripts now properly:")
        print("  ✓ Import load_config_from_env")
        print("  ✓ Call load_config_from_env() to get configuration")
        print("  ✓ Respect BACKEND_TYPE environment variable")
        print("  ✓ Respect backend-specific API keys")
        print("\nUsers can now use any backend with all scripts:")
        print("  export BACKEND_TYPE=openrouter")
        print("  export OPENROUTER_API_KEY='sk-or-v1-...'")
        print("  python scripts/run_deterministic_experiment.py")
        return 0
    else:
        print(f"\n{'='*70}")
        print("❌ SOME CHECKS FAILED")
        print(f"{'='*70}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
