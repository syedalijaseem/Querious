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
            RegisterRequest(email="test@example.com")

    def test_login_request_valid(self):
        """Valid login data should be accepted."""
        from models import LoginRequest
        
        req = LoginRequest(
            email="test@example.com",
            password="password123"
        )
        assert req.email == "test@example.com"


class TestQueryModels:
    """Tests for query model validation."""

    def test_query_pdf_event_data_valid(self):
        """Valid query data should be accepted."""
        from models import QueryPdfEventData, ScopeType
        
        req = QueryPdfEventData(
            question="What is the main topic?",
            chat_id="chat-123",
            scope_type=ScopeType.CHAT,
            scope_id="chat-123",
            top_k=5
        )
        assert req.question == "What is the main topic?"
        assert req.top_k == 5

    def test_query_top_k_has_default(self):
        """Top K should have a default value."""
        from models import QueryPdfEventData, ScopeType
        
        req = QueryPdfEventData(
            question="Test?",
            chat_id="chat-123",
            scope_type=ScopeType.CHAT,
            scope_id="chat-123"
        )
        assert req.top_k is not None


class TestPlanLimitsExist:
    """Tests for plan limits configuration."""

    def test_plan_limits_defined_in_api_routes(self):
        """Plan limits should be defined in api_routes."""
        from api_routes import PLAN_LIMITS
        
        assert "free" in PLAN_LIMITS
        assert "pro" in PLAN_LIMITS
        assert "premium" in PLAN_LIMITS

    def test_free_plan_has_limits(self):
        """Free plan should have defined limits."""
        from api_routes import PLAN_LIMITS
        
        free = PLAN_LIMITS["free"]
        assert "projects" in free
        assert "chats" in free
        assert "documents" in free
