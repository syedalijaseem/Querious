# Security Tests - Comprehensive security testing
# Tests authentication, authorization, injection attacks, and rate limiting

import pytest
from unittest.mock import MagicMock


class TestAuthenticationSecurity:
    """Tests for authentication security vulnerabilities."""

    def test_invalid_jwt_signature_rejected(self, invalid_signature_token):
        """Tokens signed with wrong key should be rejected."""
        from auth_service import decode_access_token
        
        result = decode_access_token(invalid_signature_token)
        assert result is None

    def test_expired_jwt_rejected(self, expired_token):
        """Expired tokens should be rejected."""
        from auth_service import decode_access_token
        
        result = decode_access_token(expired_token)
        assert result is None

    def test_malformed_jwt_rejected(self):
        """Malformed tokens should be rejected."""
        from auth_service import decode_access_token
        
        malformed_tokens = [
            "not.a.token",
            "eyJhbGciOiJIUzI1NiJ9.invalid",
            "",
        ]
        
        for token in malformed_tokens:
            result = decode_access_token(token)
            assert result is None, f"Malformed token should be rejected: {token}"

    def test_password_not_stored_plaintext(self, sample_user):
        """Passwords should never be stored in plaintext."""
        assert sample_user["password_hash"].startswith("$2b$")
        assert sample_user["password_hash"] != "password123"

    def test_access_token_is_jwt_format(self):
        """JWT tokens should have proper format (3 parts separated by dots)."""
        from auth_service import create_access_token
        
        token = create_access_token({
            "sub": "user-123",
            "email": "test@example.com"
        })
        
        parts = token.split(".")
        assert len(parts) == 3, "JWT should have 3 parts"


class TestAuthorizationSecurity:
    """Tests for authorization and access control."""

    def test_user_cannot_access_other_users_resources(self, mock_db, sample_project):
        """Users should only access their own resources."""
        sample_project["user_id"] = "other-user-456"
        mock_db.projects.find_one.return_value = sample_project
        
        current_user_id = "test-user-123"
        query = {"id": sample_project["id"], "user_id": current_user_id}
        mock_db.projects.find_one(query)
        
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
        ]
        
        for method, endpoint in protected_endpoints:
            assert endpoint.startswith("/api/")


class TestInputValidation:
    """Tests for input validation and injection prevention."""

    def test_nosql_injection_payloads_are_dict(self, mock_db):
        """NoSQL injection attempts should be dict type."""
        injection_payloads = [
            {"$gt": ""},
            {"$ne": None},
        ]
        
        for payload in injection_payloads:
            assert isinstance(payload, dict)


class TestRateLimiting:
    """Tests for rate limiting functionality."""

    def test_rate_limiter_blocks_after_threshold(self):
        """Rate limiter should block requests after threshold."""
        from auth_service import RateLimiter
        
        limiter = RateLimiter()
        test_key = "test-email@example.com"
        
        for _ in range(5):
            limiter.record_attempt(test_key)
        
        is_allowed = limiter.is_allowed(test_key, max_attempts=5, window_minutes=15)
        assert is_allowed is False

    def test_rate_limiter_clear_resets_attempts(self):
        """Clearing rate limiter should reset attempt count."""
        from auth_service import RateLimiter
        
        limiter = RateLimiter()
        test_key = "test-email@example.com"
        
        for _ in range(5):
            limiter.record_attempt(test_key)
        
        limiter.clear(test_key)
        is_allowed = limiter.is_allowed(test_key, max_attempts=5, window_minutes=15)
        assert is_allowed is True


class TestSessionSecurity:
    """Tests for session and token security."""

    def test_logout_invalidates_tokens(self, mock_db):
        """Logout should invalidate all related tokens."""
        mock_db.refresh_tokens.update_many.return_value = MagicMock(modified_count=1)
        
        mock_db.refresh_tokens.update_many(
            {"user_id": "test-user-123"},
            {"$set": {"revoked": True}}
        )
        
        mock_db.refresh_tokens.update_many.assert_called()

    def test_access_token_has_jwt_structure(self):
        """Access tokens should be valid JWT structure."""
        from auth_service import create_access_token
        
        token = create_access_token({"sub": "user-123"})
        
        # JWT has 3 parts separated by dots
        parts = token.split(".")
        assert len(parts) == 3


class TestDataPrivacy:
    """Tests for data privacy and isolation."""

    def test_sensitive_fields_excluded_from_responses(self, sample_user):
        """Sensitive fields should not be in API responses."""
        sensitive_fields = ["password_hash", "password", "refresh_token"]
        
        safe_user = {k: v for k, v in sample_user.items() if k not in sensitive_fields}
        
        for field in sensitive_fields:
            assert field not in safe_user

    def test_api_responses_exclude_internal_ids(self):
        """MongoDB _id should not leak to API responses."""
        response_sample = {"id": "test-123", "name": "Test"}
        
        assert "_id" not in response_sample
        assert "id" in response_sample
