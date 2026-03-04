"""Pytest configuration for promptosaurus tests."""

import pytest


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "unit: marks tests as unit tests (fast, isolated)")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "slow: marks tests as slow running")
    config.addinivalue_line("markers", "security: marks tests as security focused")


# Mark all tests in tests/unit/ as unit tests by default
def pytest_collection_modifyitems(config, items):
    """Automatically mark unit tests."""
    for item in items:
        if "unit" in item.nodeid:
            item.add_marker(pytest.mark.unit)
