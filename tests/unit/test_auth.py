# Authentication Unit Tests
# Tests for password hashing, token creation and verification

import pytest


class TestPasswordHashing:
    """Tests for password hashing functionality."""

    def test_password_is_hashed(self):
        """Passwords should be hashed, not stored plaintext."""
        from auth_service import hash_password
        
        password = "MySecurePassword123!"
        hashed = hash_password(password)
        
        assert hashed != password
        assert hashed.startswith("$2b$")

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

    def test_access_token_is_string(self):
        """Access tokens should be strings."""
        from auth_service import create_access_token
        
        token = create_access_token({"sub": "user-123", "email": "test@example.com"})
        
        assert isinstance(token, str)
        assert len(token) > 0

    def test_refresh_token_returns_tuple(self):
        """Refresh tokens should return tuple with raw, hash, expiry."""
        from auth_service import create_refresh_token
        
        result = create_refresh_token("user-123")
        
        assert isinstance(result, tuple)
        assert len(result) == 3
        raw_token, hashed_token, expires_at = result
        assert isinstance(raw_token, str)
        assert isinstance(hashed_token, str)


class TestTokenVerification:
    """Tests for JWT token verification."""

    def test_valid_token_verified(self, valid_access_token):
        """Valid tokens should verify successfully."""
        from auth_service import decode_access_token
        
        payload = decode_access_token(valid_access_token)
        
        assert payload is not None
        assert payload["sub"] == "test-user-123"

    def test_invalid_token_rejected(self, invalid_signature_token):
        """Invalid tokens should be rejected."""
        from auth_service import decode_access_token
        
        payload = decode_access_token(invalid_signature_token)
        assert payload is None

    def test_expired_token_rejected(self, expired_token):
        """Expired tokens should be rejected."""
        from auth_service import decode_access_token
        
        payload = decode_access_token(expired_token)
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
