"""
Pytest configuration and fixtures for Whyis tests.

This module provides common fixtures and configuration for all tests.
"""

import os
import pytest
from flask import Flask


# Set test environment variables
os.environ['FLASK_ENV'] = 'testing'


@pytest.fixture(scope='session')
def test_config():
    """Provide test configuration."""
    try:
        import config
    except ImportError:
        from whyis import config_defaults as config
    
    test_config = config.Test.copy() if hasattr(config, 'Test') else {}
    test_config['TESTING'] = True
    test_config['WTF_CSRF_ENABLED'] = False
    test_config['DEFAULT_ANONYMOUS_READ'] = False
    
    return test_config


@pytest.fixture(scope='function')
def app(test_config):
    """Create and configure a test Flask application instance."""
    from whyis.app_factory import app_factory
    
    if 'ADMIN_ENDPOINT' in test_config:
        del test_config['ADMIN_ENDPOINT']
        del test_config['KNOWLEDGE_ENDPOINT']
    
    test_config['NANOPUB_ARCHIVE'] = {
        'depot.backend': 'depot.io.memory.MemoryFileStorage'
    }
    test_config['FILE_ARCHIVE'] = {
        'depot.backend': 'depot.io.memory.MemoryFileStorage'
    }
    test_config['LIVESERVER_PORT'] = 8943
    test_config['LIVESERVER_TIMEOUT'] = 10
    
    try:
        import config
        project_name = config.project_name
    except (ImportError, AttributeError):
        project_name = 'whyis'
    
    application = app_factory(test_config, project_name)
    
    yield application


@pytest.fixture(scope='function')
def client(app):
    """Create a test client for the Flask application."""
    return app.test_client()


@pytest.fixture(scope='function')
def runner(app):
    """Create a test CLI runner for the Flask application."""
    return app.test_cli_runner()


# Check if full whyis environment is available
def has_whyis_environment():
    """Check if the full Whyis environment with config is available."""
    try:
        try:
            import config
            return True
        except ImportError:
            from whyis import config_defaults
            return True
    except (ImportError, AttributeError):
        return False

WHYIS_ENV_AVAILABLE = has_whyis_environment()

# Add markers for CI environment
def pytest_configure(config):
    """Configure pytest with custom settings."""
    config.addinivalue_line(
        "markers", "skipif_ci: skip test if running in CI environment"
    )
    config.addinivalue_line(
        "markers", "requires_whyis_env: test requires full Whyis environment with config"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to handle CI-specific skips."""
    if os.environ.get("CI") == "true":
        skip_ci = pytest.mark.skip(reason="Skipped in CI environment")
        for item in items:
            if "skipif_ci" in item.keywords:
                item.add_marker(skip_ci)
    
    # Skip tests that require full Whyis environment if it's not available
    if not WHYIS_ENV_AVAILABLE:
        skip_no_env = pytest.mark.skip(reason="Requires full Whyis environment with config module")
        for item in items:
            # Skip tests in whyis_test directories that use the test infrastructure
            if "whyis_test" in str(item.fspath):
                item.add_marker(skip_no_env)
