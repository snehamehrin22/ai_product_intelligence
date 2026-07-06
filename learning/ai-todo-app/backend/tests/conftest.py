"""
Test fixtures for API testing
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def test_user_id():
    """Return the test user ID used throughout tests"""
    return "test-user-001"


@pytest.fixture
def sample_task():
    """Return a sample task for testing"""
    return {
        "user_id": "test-user-001",
        "title": "Test Task",
        "description": "This is a test task",
        "status": "pending",
        "priority": "medium",
        "due_date": "2026-12-31T23:59:59"
    }
