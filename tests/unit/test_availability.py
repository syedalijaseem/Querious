"""Availability tests.

Covers fail-fast configuration validation, graceful degradation on
external-service failures, and rate-limiter correctness.
"""

import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock


# ── Configuration Fail-Fast ───────────────────────────────────────────────────


class TestConfigurationValidation:
    """App must refuse to start when required environment is incomplete."""

    def test_missing_required_field_raises(self, monkeypatch):
        from pydantic import ValidationError
        from config import Settings

        # Remove MONGODB_URI so Settings can't find it anywhere
        monkeypatch.delenv("MONGODB_URI", raising=False)

        with pytest.raises(ValidationError):
            Settings(
                JWT_SECRET_KEY="x" * 32,
                OPENAI_API_KEY="x",
                DEEPSEEK_API_KEY="x",
                R2_ACCESS_KEY_ID="x",
                R2_SECRET_ACCESS_KEY="x",
                R2_ENDPOINT="https://r2.example.com",
                R2_BUCKET_NAME="b",
                _env_file=None,
            )

    def test_valid_config_creates_instance(self):
        from config import Settings

        s = Settings(
            MONGODB_URI="mongodb://localhost",
            JWT_SECRET_KEY="x" * 32,
            OPENAI_API_KEY="x",
            DEEPSEEK_API_KEY="x",
            R2_ACCESS_KEY_ID="x",
            R2_SECRET_ACCESS_KEY="x",
            R2_ENDPOINT="https://r2.example.com",
            R2_BUCKET_NAME="b",
        )
        assert s.MONGODB_URI == "mongodb://localhost"

    def test_is_production_reflects_environment(self):
        from config import Settings

        prod = Settings(
            ENVIRONMENT="production",
            MONGODB_URI="mongodb://localhost",
            JWT_SECRET_KEY="x" * 32,
            OPENAI_API_KEY="x",
            DEEPSEEK_API_KEY="x",
            R2_ACCESS_KEY_ID="x",
            R2_SECRET_ACCESS_KEY="x",
            R2_ENDPOINT="https://r2.example.com",
            R2_BUCKET_NAME="b",
        )
        dev = Settings(
            ENVIRONMENT="development",
            MONGODB_URI="mongodb://localhost",
            JWT_SECRET_KEY="x" * 32,
            OPENAI_API_KEY="x",
            DEEPSEEK_API_KEY="x",
            R2_ACCESS_KEY_ID="x",
            R2_SECRET_ACCESS_KEY="x",
            R2_ENDPOINT="https://r2.example.com",
            R2_BUCKET_NAME="b",
        )
        assert prod.is_production is True
        assert dev.is_production is False

    def test_defaults_are_safe_for_development(self, monkeypatch):
        """Sensitive defaults like COOKIE_SECURE should be False in dev."""
        from config import Settings

        # Remove test ENVIRONMENT so default kicks in
        monkeypatch.delenv("ENVIRONMENT", raising=False)

        s = Settings(
            MONGODB_URI="mongodb://localhost",
            JWT_SECRET_KEY="x" * 32,
            OPENAI_API_KEY="x",
            DEEPSEEK_API_KEY="x",
            R2_ACCESS_KEY_ID="x",
            R2_SECRET_ACCESS_KEY="x",
            R2_ENDPOINT="https://r2.example.com",
            R2_BUCKET_NAME="b",
            _env_file=None,
        )
        assert s.COOKIE_SECURE is False
        assert s.ENVIRONMENT == "development"


# ── Graceful Degradation ─────────────────────────────────────────────────────


class TestGracefulDegradation:
    """Critical paths must not crash on external-service failures."""

    def test_verify_password_never_raises(self):
        """Bad hashes must return False, not an unhandled exception."""
        from auth_service import verify_password

        assert verify_password("pwd", "") is False
        assert verify_password("pwd", "x" * 200) is False
        assert verify_password("", "validhash") is False

    def test_ownership_helper_handles_none_db_result(self, mock_db, sample_user):
        """If DB returns None (connection issue or missing data), 404 is raised."""
        from helpers.ownership import get_user_chat
        from fastapi import HTTPException

        mock_db.chats.find_one.return_value = None
        with pytest.raises(HTTPException) as exc:
            get_user_chat(mock_db, "id", sample_user["id"])
        assert exc.value.status_code == 404

    def test_get_token_expiry_handles_garbage(self):
        """get_token_expiry must return None for invalid tokens, not raise."""
        from auth_service import get_token_expiry

        assert get_token_expiry("garbage") is None
        assert get_token_expiry("") is None


# ── Rate Limiter ──────────────────────────────────────────────────────────────


class TestRateLimiter:
    """Verify rate-limiter correctness — essential for brute-force prevention."""

    @pytest.fixture
    def limiter(self):
        from auth_service import RateLimiter
        return RateLimiter()

    def test_allows_under_limit(self, limiter):
        for _ in range(4):
            limiter.record_attempt("ip-1")
        assert limiter.is_allowed("ip-1", max_attempts=5) is True

    def test_blocks_at_limit(self, limiter):
        for _ in range(5):
            limiter.record_attempt("ip-1")
        assert limiter.is_allowed("ip-1", max_attempts=5) is False

    def test_blocks_over_limit(self, limiter):
        for _ in range(10):
            limiter.record_attempt("ip-1")
        assert limiter.is_allowed("ip-1", max_attempts=5) is False

    def test_different_keys_are_independent(self, limiter):
        for _ in range(5):
            limiter.record_attempt("ip-1")
        assert limiter.is_allowed("ip-2", max_attempts=5) is True

    def test_clear_resets_attempts(self, limiter):
        for _ in range(10):
            limiter.record_attempt("ip-1")
        assert limiter.is_allowed("ip-1", max_attempts=5) is False

        limiter.clear("ip-1")
        assert limiter.is_allowed("ip-1", max_attempts=5) is True

    def test_expired_attempts_are_not_counted(self, limiter):
        """Old attempts outside the window must be pruned."""
        old = datetime.now(timezone.utc) - timedelta(minutes=20)
        limiter._attempts["ip-1"] = [old] * 10  # All expired

        assert limiter.is_allowed("ip-1", max_attempts=5, window_minutes=15) is True

    def test_mixed_recent_and_expired_attempts(self, limiter):
        """Only recent attempts within the window count."""
        old = datetime.now(timezone.utc) - timedelta(minutes=20)
        recent = datetime.now(timezone.utc) - timedelta(minutes=1)
        limiter._attempts["ip-1"] = [old] * 5 + [recent] * 3

        assert limiter.is_allowed("ip-1", max_attempts=5, window_minutes=15) is True

    def test_window_prunes_internal_storage(self, limiter):
        """After is_allowed, expired entries should be removed from memory."""
        old = datetime.now(timezone.utc) - timedelta(minutes=60)
        limiter._attempts["ip-1"] = [old] * 100

        limiter.is_allowed("ip-1", max_attempts=5, window_minutes=15)
        assert len(limiter._attempts["ip-1"]) == 0

    def test_clear_unknown_key_does_not_raise(self, limiter):
        """Clearing a key that was never used must not crash."""
        limiter.clear("never-seen-key")  # Should not raise
