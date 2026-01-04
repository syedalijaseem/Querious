# Test Configuration and Shared Fixtures
import pytest
import os
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

# Set test environment before importing app
os.environ["ENVIRONMENT"] = "test"
os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-testing-only"
os.environ["MONGODB_URI"] = "mongodb://localhost:27017"
os.environ["FRONTEND_URL"] = "http://localhost:5173"


@pytest.fixture
def mock_db():
    """Mock MongoDB database for unit tests."""
    db = MagicMock()
    db.users = MagicMock()
    db.projects = MagicMock()
    db.chats = MagicMock()
    db.documents = MagicMock()
    db.refresh_tokens = MagicMock()
    db.waitlist = MagicMock()
    return db


@pytest.fixture
def sample_user():
    """Sample user data for testing."""
    return {
        "id": "test-user-123",
        "email": "test@example.com",
        "name": "Test User",
        "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.VTtYq.",  # hashed "password123"
        "email_verified": True,
        "plan": "free",
        "tokens_used": 0,
        "created_at": "2024-01-01T00:00:00Z"
    }


@pytest.fixture
def sample_project():
    """Sample project data for testing."""
    return {
        "id": "test-project-123",
        "user_id": "test-user-123",
        "name": "Test Project",
        "created_at": "2024-01-01T00:00:00Z"
    }


@pytest.fixture
def sample_chat():
    """Sample chat data for testing."""
    return {
        "id": "test-chat-123",
        "user_id": "test-user-123",
        "project_id": None,
        "title": "Test Chat",
        "messages": [],
        "created_at": "2024-01-01T00:00:00Z"
    }


@pytest.fixture
def auth_headers():
    """Generate valid auth headers for testing."""
    from auth_service import create_access_token
    token = create_access_token({"sub": "test-user-123", "email": "test@example.com"})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def expired_token():
    """Generate an expired token for testing."""
    import jwt
    from datetime import datetime, timedelta
    payload = {
        "sub": "test-user-123",
        "email": "test@example.com",
        "exp": datetime.utcnow() - timedelta(hours=1)
    }
    return jwt.encode(payload, "test-secret-key-for-testing-only", algorithm="HS256")


@pytest.fixture
def invalid_token():
    """Generate a token signed with wrong key."""
    import jwt
    payload = {"sub": "test-user-123", "email": "test@example.com"}
    return jwt.encode(payload, "wrong-secret-key", algorithm="HS256")
