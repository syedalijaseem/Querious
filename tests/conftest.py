# Test Configuration and Shared Fixtures
import pytest
import os
from unittest.mock import MagicMock, patch

# Set test environment before importing app modules
os.environ["ENVIRONMENT"] = "test"
os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-testing-only-32chars!"
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
        "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.VTtYq.",  # hashed
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
def valid_access_token():
    """Generate a valid access token for testing."""
    from auth_service import create_access_token
    return create_access_token({"sub": "test-user-123", "email": "test@example.com"})


@pytest.fixture
def expired_token():
    """Generate an expired token for testing."""
    from jose import jwt
    from datetime import datetime, timedelta, timezone
    payload = {
        "sub": "test-user-123",
        "email": "test@example.com",
        "type": "access",
        "exp": datetime.now(timezone.utc) - timedelta(hours=1),
        "iat": datetime.now(timezone.utc) - timedelta(hours=2)
    }
    return jwt.encode(payload, "test-secret-key-for-testing-only-32chars!", algorithm="HS256")


@pytest.fixture
def invalid_signature_token():
    """Generate a token signed with wrong key."""
    from jose import jwt
    from datetime import datetime, timedelta, timezone
    payload = {
        "sub": "test-user-123",
        "email": "test@example.com",
        "type": "access",
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        "iat": datetime.now(timezone.utc)
    }
    return jwt.encode(payload, "wrong-secret-key", algorithm="HS256")
