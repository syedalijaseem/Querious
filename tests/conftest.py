
import pytest
from unittest.mock import MagicMock
import os

# Set test environment
os.environ["ENVIRONMENT"] = "test"
os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-testing-only-32chars!"
os.environ["MONGODB_URI"] = "mongodb://localhost:27017"

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
        "plan": "free",
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
