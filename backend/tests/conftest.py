"""Pytest configuration and fixtures."""
import pytest
import os
import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test (requires services)"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as unit test (no external dependencies)"
    )


@pytest.fixture(scope="session")
def celery_config():
    """Celery configuration for tests."""
    return {
        "broker_url": "redis://localhost:6379/2",  # Use different DB for tests
        "result_backend": "redis://localhost:6379/3",
        "task_always_eager": False,  # Set to True for unit tests
        "task_eager_propagates": True,
    }


@pytest.fixture
def redis_client():
    """Provide a Redis client for tests."""
    import redis
    client = redis.Redis(host="localhost", port=6379, db=4)  # Test DB
    yield client
    # Cleanup
    client.flushdb()