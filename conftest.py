"""Pytest configuration for chaoschain-integrations."""

import pytest


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "unit: Unit tests with mocks")
    config.addinivalue_line("markers", "integration: Integration tests requiring sidecars")
    config.addinivalue_line(
        "markers", "contract: Contract tests for adapter conformance"
    )

