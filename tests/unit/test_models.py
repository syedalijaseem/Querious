# Model Validation Unit Tests
# Tests for Pydantic model validation

import pytest
from pydantic import ValidationError


class TestUserModels:
    """Tests for user-related model validation."""

    def test_register_request_valid(self):
        """Valid registration data should be accepted."""
        from models import RegisterRequest
        
        req = RegisterRequest(
            email="test@example.com",
            password="SecurePass123!",
            name="Test User"
        )
        assert req.email == "test@example.com"
        assert req.name == "Test User"

    def test_register_request_missing_fields(self):
        """Missing required fields should raise error."""
        from models import RegisterRequest
        
        with pytest.raises(ValidationError):
            RegisterRequest(email="test@example.com")  # Missing password and name

    def test_login_request_valid(self):
        """Valid login data should be accepted."""
        from models import LoginRequest
        
        req = LoginRequest(
            email="test@example.com",
            password="password123"
        )
        assert req.email == "test@example.com"


class TestProjectModels:
    """Tests for project model validation."""

    def test_create_project_request_valid(self):
        """Valid project creation data should be accepted."""
        from models import CreateProjectRequest
        
        req = CreateProjectRequest(name="My Project")
        assert req.name == "My Project"

    def test_create_project_empty_name_rejected(self):
        """Empty project name should be rejected."""
        from models import CreateProjectRequest
        
        with pytest.raises(ValidationError):
            CreateProjectRequest(name="")


class TestChatModels:
    """Tests for chat model validation."""

    def test_create_chat_request_valid(self):
        """Valid chat creation data should be accepted."""
        from models import CreateChatRequest
        
        req = CreateChatRequest(title="Test Chat")
        assert req.title == "Test Chat"

    def test_create_chat_with_project(self):
        """Chat can optionally be associated with project."""
        from models import CreateChatRequest
        
        req = CreateChatRequest(title="Test Chat", project_id="project-123")
        assert req.project_id == "project-123"


class TestQueryModels:
    """Tests for query model validation."""

    def test_query_request_valid(self):
        """Valid query data should be accepted."""
        from models import QueryEventData
        
        req = QueryEventData(
            question="What is the main topic?",
            chat_id="chat-123",
            project_id=None,
            top_k=5
        )
        assert req.question == "What is the main topic?"
        assert req.top_k == 5

    def test_query_top_k_range(self):
        """Top K should be within valid range."""
        from models import QueryEventData
        
        # Valid range: 1-50
        req = QueryEventData(
            question="Test?",
            chat_id="chat-123",
            top_k=50
        )
        assert req.top_k == 50
        
        # Out of range should fail
        with pytest.raises(ValidationError):
            QueryEventData(
                question="Test?",
                chat_id="chat-123",
                top_k=100  # Too high
            )


class TestPlanLimits:
    """Tests for plan limit constants."""

    def test_plan_limits_defined(self):
        """Plan limits should be properly defined."""
        from models import PLAN_LIMITS
        
        assert "free" in PLAN_LIMITS
        assert "pro" in PLAN_LIMITS
        assert "premium" in PLAN_LIMITS
        
        # Free plan should have lower limits
        assert PLAN_LIMITS["free"]["tokens"] < PLAN_LIMITS["pro"]["tokens"]
        assert PLAN_LIMITS["pro"]["tokens"] < PLAN_LIMITS["premium"]["tokens"]

    def test_plan_has_required_limits(self):
        """Each plan should have all required limit fields."""
        from models import PLAN_LIMITS
        
        required_fields = ["tokens", "chats", "projects", "documents"]
        
        for plan, limits in PLAN_LIMITS.items():
            for field in required_fields:
                assert field in limits, f"Plan {plan} missing {field}"
