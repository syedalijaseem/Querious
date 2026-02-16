
import pytest
from unittest.mock import MagicMock
import os

# Set ALL required environment variables BEFORE any config.py imports.
# config.py uses pydantic-settings which validates on import.
os.environ["ENVIRONMENT"] = "test"
os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-testing-only-32chars!"
os.environ["MONGODB_URI"] = "mongodb://localhost:27017"
os.environ["OPENAI_API_KEY"] = "test-openai-key"
os.environ["DEEPSEEK_API_KEY"] = "test-deepseek-key"
os.environ["R2_ACCESS_KEY_ID"] = "test-r2-access"
os.environ["R2_SECRET_ACCESS_KEY"] = "test-r2-secret"
os.environ["R2_ENDPOINT"] = "https://test.r2.cloudflarestorage.com"
os.environ["R2_BUCKET_NAME"] = "test-bucket"

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
