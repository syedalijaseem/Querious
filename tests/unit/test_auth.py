# Authentication Unit Tests
# Tests for registration, login, logout, token refresh, and password operations

import pytest
from unittest.mock import MagicMock, patch


class TestPasswordHashing:
    """Tests for password hashing functionality."""

    def test_password_is_hashed(self):
        """Passwords should be hashed, not stored plaintext."""
        from auth_service import hash_password
        
        password = "MySecurePassword123!"
        hashed = hash_password(password)
        
        assert hashed != password
        assert hashed.startswith("$2b$")  # bcrypt identifier

    def test_password_verification_correct(self):
        """Correct password should verify successfully."""
        from auth_service import hash_password, verify_password
        
        password = "MySecurePassword123!"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True

    def test_password_verification_incorrect(self):
        """Incorrect password should fail verification."""
        from auth_service import hash_password, verify_password
        
        password = "MySecurePassword123!"
        wrong_password = "WrongPassword456!"
        hashed = hash_password(password)
        
        assert verify_password(wrong_password, hashed) is False


class TestTokenCreation:
    """Tests for JWT token creation."""

    def test_access_token_created_with_expiry(self):
        """Access tokens should have expiration."""
        from auth_service import create_access_token
        import jwt
        
        token = create_access_token({"sub": "user-123", "email": "test@example.com"})
        payload = jwt.decode(token, options={"verify_signature": False})
        
        assert "exp" in payload
        assert "sub" in payload
        assert payload["sub"] == "user-123"

    def test_refresh_token_created_with_expiry(self):
        """Refresh tokens should have longer expiration."""
        from auth_service import create_refresh_token
        import jwt
        
        token = create_refresh_token({"sub": "user-123"})
        payload = jwt.decode(token, options={"verify_signature": False})
        
        assert "exp" in payload


class TestTokenVerification:
    """Tests for JWT token verification."""

    def test_valid_token_verified(self):
        """Valid tokens should verify successfully."""
        from auth_service import create_access_token, verify_access_token
        
        token = create_access_token({"sub": "user-123", "email": "test@example.com"})
        payload = verify_access_token(token)
        
        assert payload is not None
        assert payload["sub"] == "user-123"

    def test_invalid_token_rejected(self, invalid_token):
        """Invalid tokens should be rejected."""
        from auth_service import verify_access_token
        
        payload = verify_access_token(invalid_token)
        assert payload is None

    def test_expired_token_rejected(self, expired_token):
        """Expired tokens should be rejected."""
        from auth_service import verify_access_token
        
        payload = verify_access_token(expired_token)
        assert payload is None


class TestEmailValidation:
    """Tests for email validation."""

    def test_valid_emails_accepted(self):
        """Valid email formats should be accepted."""
        from models import RegisterRequest
        
        valid_emails = [
            "test@example.com",
            "user.name@domain.org",
            "user+tag@example.co.uk",
        ]
        
        for email in valid_emails:
            req = RegisterRequest(email=email, password="ValidPass123!", name="Test")
            assert req.email == email

    def test_invalid_emails_rejected(self):
        """Invalid email formats should be rejected."""
        from pydantic import ValidationError
        from models import RegisterRequest
        
        invalid_emails = [
            "not-an-email",
            "@no-local.com",
            "no-at-sign.com",
        ]
        
        for email in invalid_emails:
            with pytest.raises(ValidationError):
                RegisterRequest(email=email, password="ValidPass123!", name="Test")
