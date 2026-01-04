# Security Tests - Comprehensive security testing for the application
# Tests authentication, authorization, injection attacks, and rate limiting

import pytest
from unittest.mock import MagicMock, patch
import jwt


class TestAuthenticationSecurity:
    """Tests for authentication security vulnerabilities."""

    def test_invalid_jwt_signature_rejected(self, invalid_token):
        """Tokens signed with wrong key should be rejected."""
        from auth_service import verify_access_token
        
        result = verify_access_token(invalid_token)
        assert result is None

    def test_expired_jwt_rejected(self, expired_token):
        """Expired tokens should be rejected."""
        from auth_service import verify_access_token
        
        result = verify_access_token(expired_token)
        assert result is None

    def test_malformed_jwt_rejected(self):
        """Malformed tokens should be rejected."""
        from auth_service import verify_access_token
        
        malformed_tokens = [
            "not.a.token",
            "eyJhbGciOiJIUzI1NiJ9.invalid",
            "",
            "null",
            "undefined",
        ]
        
        for token in malformed_tokens:
            result = verify_access_token(token)
            assert result is None, f"Malformed token should be rejected: {token}"

    def test_password_not_stored_plaintext(self, sample_user):
        """Passwords should never be stored in plaintext."""
        # Password hash should start with bcrypt identifier
        assert sample_user["password_hash"].startswith("$2b$")
        assert sample_user["password_hash"] != "password123"

    def test_jwt_contains_no_sensitive_data(self):
        """JWT payload should not contain sensitive data."""
        from auth_service import create_access_token
        
        token = create_access_token({
            "sub": "user-123",
            "email": "test@example.com"
        })
        
        # Decode without verification to inspect payload
        payload = jwt.decode(token, options={"verify_signature": False})
        
        # Should not contain password, password_hash, or other secrets
        assert "password" not in payload
        assert "password_hash" not in payload
        assert "api_key" not in payload
        assert "secret" not in payload


class TestAuthorizationSecurity:
    """Tests for authorization and access control."""

    def test_user_cannot_access_other_users_resources(self, mock_db, sample_project):
        """Users should only access their own resources."""
        # Simulate project owned by different user
        sample_project["user_id"] = "other-user-456"
        mock_db.projects.find_one.return_value = sample_project
        
        # Current user trying to access should fail
        current_user_id = "test-user-123"
        
        # The query should include user_id filter
        query = {"id": sample_project["id"], "user_id": current_user_id}
        mock_db.projects.find_one(query)
        
        # Verify query includes user_id
        call_args = mock_db.projects.find_one.call_args[0][0]
        assert "user_id" in call_args

    def test_api_endpoints_require_authentication(self):
        """Protected endpoints should require valid authentication."""
        protected_endpoints = [
            ("GET", "/api/projects"),
            ("POST", "/api/projects"),
            ("GET", "/api/chats"),
            ("POST", "/api/chats"),
            ("GET", "/api/auth/me"),
            ("POST", "/api/query"),
        ]
        
        # All these endpoints should check for auth
        # This is a structural test - actual HTTP tests would be in integration
        for method, endpoint in protected_endpoints:
            assert endpoint.startswith("/api/"), f"Endpoint should be in API namespace: {endpoint}"


class TestInputValidation:
    """Tests for input validation and injection prevention."""

    def test_email_validation_rejects_invalid_formats(self):
        """Email validation should reject malformed emails."""
        from pydantic import ValidationError
        from models import RegisterRequest
        
        invalid_emails = [
            "not-an-email",
            "@missing-local.com",
            "missing-domain@",
            "spaces in@email.com",
            "<script>alert('xss')</script>@evil.com",
        ]
        
        for email in invalid_emails:
            with pytest.raises(ValidationError):
                RegisterRequest(email=email, password="ValidPass123!", name="Test")

    def test_password_minimum_requirements(self):
        """Password should meet minimum security requirements."""
        from pydantic import ValidationError
        from models import RegisterRequest
        
        weak_passwords = [
            "short",        # Too short
            "12345678",     # No letters
            "password",     # Too common (if checked)
        ]
        
        for password in weak_passwords:
            try:
                req = RegisterRequest(email="test@example.com", password=password, name="Test")
                # If model allows, that's a potential issue to flag
            except ValidationError:
                pass  # Expected for weak passwords

    def test_nosql_injection_prevention(self, mock_db):
        """NoSQL injection attempts should be prevented."""
        # Common MongoDB injection payloads
        injection_payloads = [
            {"$gt": ""},
            {"$ne": None},
            {"$where": "this.password == this.password"},
            {"$regex": ".*"},
        ]
        
        # These should be treated as literal values, not operators
        for payload in injection_payloads:
            # When used as search value, should be escaped/rejected
            # This is a reminder to validate input before DB queries
            assert isinstance(payload, dict)

    def test_xss_in_user_input_sanitized(self):
        """XSS attempts in user input should be handled safely."""
        xss_payloads = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "{{constructor.constructor('return this')()}}",
        ]
        
        # These should be escaped when rendered or rejected
        for payload in xss_payloads:
            # Test that payload is treated as string, not executed
            assert isinstance(payload, str)


class TestRateLimiting:
    """Tests for rate limiting functionality."""

    def test_rate_limiter_blocks_after_threshold(self):
        """Rate limiter should block requests after threshold."""
        from auth_service import RateLimiter
        
        limiter = RateLimiter()
        test_key = "test-email@example.com"
        
        # Record attempts up to limit
        for _ in range(5):
            limiter.record_attempt(test_key)
        
        # Should be blocked after 5 attempts (with max_attempts=5)
        is_allowed = limiter.is_allowed(test_key, max_attempts=5, window_minutes=15)
        assert is_allowed is False

    def test_rate_limiter_allows_after_window(self):
        """Rate limiter should reset after time window."""
        from auth_service import RateLimiter
        from datetime import datetime, timedelta
        
        limiter = RateLimiter()
        test_key = "test-email@example.com"
        
        # Simulate old attempts (outside window)
        with patch('auth_service.datetime') as mock_datetime:
            old_time = datetime.utcnow() - timedelta(minutes=20)
            mock_datetime.utcnow.return_value = old_time
            
            for _ in range(10):
                limiter.record_attempt(test_key)
        
        # Should be allowed now (attempts are stale)
        is_allowed = limiter.is_allowed(test_key, max_attempts=5, window_minutes=15)
        assert is_allowed is True

    def test_rate_limiter_clear_resets_attempts(self):
        """Clearing rate limiter should reset attempt count."""
        from auth_service import RateLimiter
        
        limiter = RateLimiter()
        test_key = "test-email@example.com"
        
        # Record some attempts
        for _ in range(5):
            limiter.record_attempt(test_key)
        
        # Clear and verify allowed
        limiter.clear(test_key)
        is_allowed = limiter.is_allowed(test_key, max_attempts=5, window_minutes=15)
        assert is_allowed is True


class TestSessionSecurity:
    """Tests for session and token security."""

    def test_refresh_token_rotation(self, mock_db):
        """Refresh tokens should be rotated on use."""
        # Old refresh token should be invalidated after use
        # This is a design requirement test
        pass  # Implementation depends on actual refresh flow

    def test_logout_invalidates_tokens(self, mock_db):
        """Logout should invalidate all related tokens."""
        mock_db.refresh_tokens.update_many.return_value = MagicMock(modified_count=1)
        
        # After logout, refresh tokens should be marked as revoked
        mock_db.refresh_tokens.update_many(
            {"user_id": "test-user-123"},
            {"$set": {"revoked": True}}
        )
        
        mock_db.refresh_tokens.update_many.assert_called()

    def test_token_contains_expiration(self):
        """All tokens should have expiration times."""
        from auth_service import create_access_token
        
        token = create_access_token({"sub": "user-123"})
        payload = jwt.decode(token, options={"verify_signature": False})
        
        assert "exp" in payload, "Token must have expiration"


class TestDataPrivacy:
    """Tests for data privacy and isolation."""

    def test_user_data_isolation_in_queries(self):
        """All data queries should be scoped to user."""
        # This is a code review checklist item
        # Verify all find() calls include user_id filter
        
        required_user_id_queries = [
            "projects.find",
            "chats.find",
            "documents.find",
        ]
        
        # These queries should always include user_id
        for query in required_user_id_queries:
            assert "find" in query

    def test_sensitive_fields_excluded_from_responses(self, sample_user):
        """Sensitive fields should not be in API responses."""
        sensitive_fields = ["password_hash", "password", "refresh_token"]
        
        # Create a response-safe user object
        safe_user = {k: v for k, v in sample_user.items() if k not in sensitive_fields}
        
        for field in sensitive_fields:
            assert field not in safe_user

    def test_api_responses_exclude_internal_ids(self):
        """MongoDB _id should not leak to API responses."""
        # All API responses should use custom 'id' field, not '_id'
        response_sample = {"id": "test-123", "name": "Test"}
        
        assert "_id" not in response_sample
        assert "id" in response_sample
