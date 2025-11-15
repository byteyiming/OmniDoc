"""
Pytest configuration and fixtures
"""
import os
import pytest

# Set test environment variables
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("DATABASE_URL", "postgresql://localhost/omnidoc_test")
os.environ.setdefault("ALLOWED_ORIGINS", "http://localhost:3000")


@pytest.fixture(scope="session")
def test_client():
    """Create a test client for the FastAPI app"""
    from fastapi.testclient import TestClient
    from src.web.app import app
    return TestClient(app)
