#!/usr/bin/env python3
"""
Verification script for API refactoring.
Tests that all imports work correctly and the API is properly configured.
"""

import sys


def test_new_import():
    """Test new import from apis.main"""
    try:
        from apis.main import app

        assert app.title == "OpsSage"
        print("✓ Import from apis.main works")
        return True
    except Exception as e:
        print(f"✗ Import from apis.main failed: {e}")
        return False


def test_apis_package_import():
    """Test import from apis package"""
    try:
        from apis import app

        assert app.title == "OpsSage"
        print("✓ Import from apis package works")
        return True
    except Exception as e:
        print(f"✗ Import from apis package failed: {e}")
        return False


def test_backward_compatibility():
    """Test backward compatibility with sages.api"""
    try:
        from sages.api import app

        assert app.title == "OpsSage"
        print("✓ Backward compatibility: sages.api still works")
        return True
    except Exception as e:
        print(f"✗ Backward compatibility failed: {e}")
        return False


def test_app_configuration():
    """Test that the app is properly configured"""
    try:
        from apis.main import app

        # Check basic configuration
        assert app.title == "OpsSage"
        assert app.version == "0.1.0"
        assert (
            app.description == "Multi-Agent Incident Analysis & Remediation System"
        )

        # Check routes exist
        routes = [route.path for route in app.routes if hasattr(route, "path")]
        required_routes = [
            "/",
            "/api/v1/alerts",
            "/api/v1/incidents",
            "/api/v1/health",
            "/api/v1/readiness",
        ]

        for route in required_routes:
            assert (
                route in routes
            ), f"Required route {route} not found in {routes}"

        print("✓ App configuration is correct")
        print(f"  - Title: {app.title}")
        print(f"  - Version: {app.version}")
        print(f"  - Routes: {len(routes)} total")
        return True
    except Exception as e:
        print(f"✗ App configuration check failed: {e}")
        return False


def test_agents_import():
    """Test that agents can still be imported"""
    try:
        from sages.subagents.aica import create_aica_agent
        from sages.subagents.krea import create_krea_agent
        from sages.subagents.rcara import create_rcara_agent

        print("✓ All agent imports work")
        return True
    except Exception as e:
        print(f"✗ Agent imports failed: {e}")
        return False


def test_models_import():
    """Test that models can be imported"""
    try:
        from sages.models import (
            AICAOutput,
            AlertInput,
            IncidentContext,
            KREAOutput,
            RCARAOutput,
        )

        print("✓ Model imports work")
        return True
    except Exception as e:
        print(f"✗ Model imports failed: {e}")
        return False


def main():
    """Run all verification tests"""
    print("=" * 60)
    print("OpsSage API Refactoring Verification")
    print("=" * 60)
    print()

    tests = [
        test_new_import,
        test_apis_package_import,
        test_backward_compatibility,
        test_app_configuration,
        test_agents_import,
        test_models_import,
    ]

    results = []
    for test in tests:
        result = test()
        results.append(result)
        print()

    # Summary
    print("=" * 60)
    passed = sum(results)
    total = len(results)

    if passed == total:
        print(f"✓ All {total} tests passed!")
        print()
        print("The API refactoring is successful.")
        print("You can now use: from apis.main import app")
        return 0
    else:
        print(f"✗ {total - passed}/{total} tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
