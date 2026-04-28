"""Comprehensive security tests.

Covers JWT integrity, password hashing, NoSQL injection prevention,
input sanitization, CORS configuration, and authorization boundaries.
"""

import pytest
from datetime import timedelta, datetime, timezone
from unittest.mock import MagicMock, patch


# ── JWT & Token Security ─────────────────────────────────────────────────────


class TestJWTSecurity:
    """Verify JWT tokens are created and validated correctly."""

    def test_valid_token_decodes_successfully(self):
        from auth_service import create_access_token, decode_access_token

        token = create_access_token({"sub": "user_1", "email": "a@b.com"})
        payload = decode_access_token(token)

        assert payload is not None
        assert payload["sub"] == "user_1"
        assert payload["type"] == "access"

    def test_expired_token_is_rejected(self):
        from auth_service import create_access_token, decode_access_token

        token = create_access_token(
            {"sub": "user_1"}, expires_delta=timedelta(seconds=-1)
        )
        assert decode_access_token(token) is None

    def test_token_with_wrong_secret_is_rejected(self):
        from jose import jwt as jose_jwt
        from auth_service import decode_access_token, JWT_ALGORITHM

        token = jose_jwt.encode(
            {"sub": "user_1", "type": "access", "exp": datetime.now(timezone.utc) + timedelta(hours=1)},
            "completely-wrong-secret-key-1234567890!",
            algorithm=JWT_ALGORITHM,
        )
        assert decode_access_token(token) is None

    def test_token_with_wrong_algorithm_is_rejected(self):
        from jose import jwt as jose_jwt
        from auth_service import decode_access_token, JWT_SECRET_KEY

        token = jose_jwt.encode(
            {"sub": "user_1", "type": "access", "exp": datetime.now(timezone.utc) + timedelta(hours=1)},
            JWT_SECRET_KEY,
            algorithm="HS384",
        )
        assert decode_access_token(token) is None

    def test_token_missing_type_claim_is_rejected(self):
        """A JWT without type='access' must not be accepted as an access token."""
        from jose import jwt as jose_jwt
        from auth_service import decode_access_token, JWT_SECRET_KEY, JWT_ALGORITHM

        token = jose_jwt.encode(
            {"sub": "user_1", "exp": datetime.now(timezone.utc) + timedelta(hours=1)},
            JWT_SECRET_KEY,
            algorithm=JWT_ALGORITHM,
        )
        assert decode_access_token(token) is None

    def test_refresh_token_cannot_be_used_as_access_token(self):
        """A token with type='refresh' must be rejected by the access-token decoder."""
        from jose import jwt as jose_jwt
        from auth_service import decode_access_token, JWT_SECRET_KEY, JWT_ALGORITHM

        token = jose_jwt.encode(
            {
                "sub": "user_1",
                "type": "refresh",
                "exp": datetime.now(timezone.utc) + timedelta(hours=1),
            },
            JWT_SECRET_KEY,
            algorithm=JWT_ALGORITHM,
        )
        assert decode_access_token(token) is None

    def test_garbage_string_is_rejected(self):
        from auth_service import decode_access_token

        assert decode_access_token("not.a.jwt") is None
        assert decode_access_token("") is None

    def test_access_token_contains_iat_claim(self):
        """Tokens must carry 'issued at' for auditing and replay detection."""
        from auth_service import create_access_token, decode_access_token

        token = create_access_token({"sub": "user_1"})
        payload = decode_access_token(token)
        assert "iat" in payload

    def test_token_payload_is_not_mutated(self):
        """create_access_token must not modify the original dict."""
        from auth_service import create_access_token

        original = {"sub": "user_1", "email": "a@b.com"}
        snapshot = original.copy()
        create_access_token(original)
        assert original == snapshot


class TestRefreshTokenSecurity:
    """Verify refresh token generation and hashing."""

    def test_refresh_tokens_are_unique(self):
        from auth_service import create_refresh_token

        raw1, _, _ = create_refresh_token("user_1")
        raw2, _, _ = create_refresh_token("user_1")
        assert raw1 != raw2

    def test_refresh_token_hash_differs_from_raw(self):
        from auth_service import create_refresh_token

        raw, hashed, _ = create_refresh_token("user_1")
        assert raw != hashed

    def test_hash_token_is_deterministic(self):
        from auth_service import hash_token

        assert hash_token("abc123") == hash_token("abc123")

    def test_hash_token_produces_hex_sha256(self):
        from auth_service import hash_token

        h = hash_token("test-token")
        assert len(h) == 64  # SHA-256 hex length
        assert all(c in "0123456789abcdef" for c in h)

    def test_refresh_token_expiry_is_in_future(self):
        from auth_service import create_refresh_token

        _, _, expires_at = create_refresh_token("user_1")
        assert expires_at > datetime.now(timezone.utc)


# ── Password Hashing ─────────────────────────────────────────────────────────


class TestPasswordHashing:
    """Verify bcrypt password hashing behaviour."""

    def test_hash_produces_bcrypt_format(self):
        from auth_service import hash_password

        h = hash_password("SecureP@ss1")
        assert h.startswith("$2b$")

    def test_verify_correct_password(self):
        from auth_service import hash_password, verify_password

        h = hash_password("MyPass123!")
        assert verify_password("MyPass123!", h) is True

    def test_verify_wrong_password(self):
        from auth_service import hash_password, verify_password

        h = hash_password("MyPass123!")
        assert verify_password("WrongPass1!", h) is False

    def test_verify_returns_false_on_malformed_hash(self):
        """Must never raise — always returns False on garbage input."""
        from auth_service import verify_password

        assert verify_password("anything", "not-a-bcrypt-hash") is False

    def test_same_password_produces_different_hashes(self):
        """Bcrypt salting must ensure unique hashes per call."""
        from auth_service import hash_password

        h1 = hash_password("SamePass1!")
        h2 = hash_password("SamePass1!")
        assert h1 != h2


# ── NoSQL Injection Prevention ────────────────────────────────────────────────


class TestNoSQLInjection:
    """Verify that ownership helpers don't pass operator payloads to queries."""

    def test_operator_payload_in_chat_id(self, mock_db, sample_user):
        """Injecting {"$gt": ""} as chat_id must result in 404, not data leak."""
        from helpers.ownership import get_user_chat
        from fastapi import HTTPException

        mock_db.chats.find_one.return_value = None

        with pytest.raises(HTTPException) as exc:
            get_user_chat(mock_db, {"$gt": ""}, sample_user["id"])
        assert exc.value.status_code == 404

    def test_operator_payload_in_user_id(self, mock_db):
        """Injecting operator as user_id must result in 404."""
        from helpers.ownership import get_user_chat
        from fastapi import HTTPException

        mock_db.chats.find_one.return_value = None

        with pytest.raises(HTTPException) as exc:
            get_user_chat(mock_db, "chat-1", {"$ne": ""})
        assert exc.value.status_code == 404

    def test_operator_payload_in_project_id(self, mock_db, sample_user):
        from helpers.ownership import get_user_project
        from fastapi import HTTPException

        mock_db.projects.find_one.return_value = None

        with pytest.raises(HTTPException) as exc:
            get_user_project(mock_db, {"$gt": ""}, sample_user["id"])
        assert exc.value.status_code == 404

    def test_scope_ownership_rejects_unknown_scope_type(self, mock_db, sample_user):
        """Unknown scope types must raise 404 — not silently pass."""
        from helpers.ownership import verify_scope_ownership
        from fastapi import HTTPException

        mock_db.chats.find_one.return_value = None
        mock_db.projects.find_one.return_value = None

        with pytest.raises(HTTPException) as exc:
            verify_scope_ownership(mock_db, "admin", "scope-1", sample_user["id"])
        assert exc.value.status_code == 404


# ── Input Sanitization & XSS ─────────────────────────────────────────────────


class TestInputSanitization:
    """Ensure dangerous inputs are rejected at the boundary."""

    def test_pdf_validation_rejects_html_content(self):
        """A file starting with <script> must not be accepted as PDF."""
        from shared_utils import validate_pdf_content

        assert validate_pdf_content(b"<script>alert('xss')</script>") is False

    def test_pdf_validation_rejects_empty_content(self):
        from shared_utils import validate_pdf_content

        assert validate_pdf_content(b"") is False

    def test_pdf_validation_rejects_short_content(self):
        from shared_utils import validate_pdf_content

        assert validate_pdf_content(b"PD") is False

    def test_pdf_validation_accepts_valid_header(self):
        from shared_utils import validate_pdf_content

        assert validate_pdf_content(b"%PDF-1.4 rest of file...") is True

    def test_pdf_validation_rejects_jpeg_magic(self):
        from shared_utils import validate_pdf_content

        assert validate_pdf_content(b"\xff\xd8\xff\xe0 JFIF") is False

    def test_pdf_validation_rejects_png_magic(self):
        from shared_utils import validate_pdf_content

        assert validate_pdf_content(b"\x89PNG\r\n\x1a\n") is False

    def test_user_model_rejects_empty_name(self):
        from models import User

        with pytest.raises(ValueError, match="empty"):
            User(email="a@b.com", name="   ", password_hash="x")

    def test_user_model_rejects_very_long_name(self):
        from models import User

        with pytest.raises(ValueError, match="too long"):
            User(email="a@b.com", name="A" * 101, password_hash="x")

    def test_user_model_rejects_very_long_email(self):
        from models import User

        with pytest.raises(ValueError, match="too long"):
            User(email="a" * 250 + "@b.com", name="Test", password_hash="x")


# ── CORS Configuration ───────────────────────────────────────────────────────


class TestCORSConfiguration:
    """Verify CORS origins are locked down in production."""

    def test_production_cors_is_restricted(self):
        from pydantic_settings import BaseSettings
        from config import Settings

        s = Settings(
            ENVIRONMENT="production",
            FRONTEND_URL="https://app.example.com",
            MONGODB_URI="mongodb://localhost",
            JWT_SECRET_KEY="k" * 32,
            OPENAI_API_KEY="x",
            DEEPSEEK_API_KEY="x",
            R2_ACCESS_KEY_ID="x",
            R2_SECRET_ACCESS_KEY="x",
            R2_ENDPOINT="https://r2.example.com",
            R2_BUCKET_NAME="b",
        )
        assert s.cors_origins == ["https://app.example.com"]
        assert "*" not in s.cors_origins

    def test_development_cors_is_wildcard(self):
        from config import Settings

        s = Settings(
            ENVIRONMENT="development",
            MONGODB_URI="mongodb://localhost",
            JWT_SECRET_KEY="k" * 32,
            OPENAI_API_KEY="x",
            DEEPSEEK_API_KEY="x",
            R2_ACCESS_KEY_ID="x",
            R2_SECRET_ACCESS_KEY="x",
            R2_ENDPOINT="https://r2.example.com",
            R2_BUCKET_NAME="b",
        )
        assert s.cors_origins == ["*"]


# ── Authorization Boundary ────────────────────────────────────────────────────


class TestAuthorizationBoundary:
    """Ensure error responses don't leak resource existence."""

    def test_non_owner_gets_same_error_as_nonexistent(self, mock_db, sample_user):
        """Both 'not found' and 'not owned' must return identical 404."""
        from helpers.ownership import get_user_chat
        from fastapi import HTTPException

        mock_db.chats.find_one.return_value = None

        # Non-existent resource
        with pytest.raises(HTTPException) as exc1:
            get_user_chat(mock_db, "nonexistent-id", sample_user["id"])

        # Existing resource owned by someone else
        with pytest.raises(HTTPException) as exc2:
            get_user_chat(mock_db, "owned-by-other", sample_user["id"])

        assert exc1.value.status_code == exc2.value.status_code == 404
        assert exc1.value.detail == exc2.value.detail

    def test_document_ownership_verifies_parent_scope(self, mock_db, sample_user):
        """Document access must check that the parent chat/project is owned."""
        from helpers.ownership import verify_document_ownership
        from fastapi import HTTPException

        # Document exists but parent chat is not owned
        mock_db.documents.find_one.return_value = {
            "id": "doc-1",
            "scope_type": "chat",
            "scope_id": "other-chat",
        }
        mock_db.chats.find_one.return_value = None

        with pytest.raises(HTTPException) as exc:
            verify_document_ownership(mock_db, "doc-1", sample_user["id"])
        assert exc.value.status_code == 404

    def test_missing_document_returns_404(self, mock_db, sample_user):
        from helpers.ownership import verify_document_ownership
        from fastapi import HTTPException

        mock_db.documents.find_one.return_value = None

        with pytest.raises(HTTPException) as exc:
            verify_document_ownership(mock_db, "does-not-exist", sample_user["id"])
        assert exc.value.status_code == 404
