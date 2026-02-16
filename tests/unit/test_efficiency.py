"""Efficiency tests.

Covers token-estimation accuracy, rate-limiter memory hygiene,
and sliding-window token-budget adherence.
"""

import pytest
from datetime import datetime, timedelta, timezone


# ── Token Estimation ──────────────────────────────────────────────────────────


class TestTokenEstimation:
    """Verify the 1 token ≈ 4 chars heuristic used for budget enforcement."""

    def test_plain_text_approximation(self):
        from main import estimate_tokens

        msgs = [{"content": "a" * 400}]
        assert estimate_tokens(msgs) == 100  # 400 / 4

    def test_empty_messages_returns_zero(self):
        from main import estimate_tokens

        assert estimate_tokens([]) == 0

    def test_missing_content_key_ignored(self):
        from main import estimate_tokens

        msgs = [{"role": "user"}, {"content": "a" * 40}]
        assert estimate_tokens(msgs) == 10  # Only second message counts

    def test_multiple_messages_summed(self):
        from main import estimate_tokens

        msgs = [{"content": "a" * 40}, {"content": "b" * 60}]
        assert estimate_tokens(msgs) == 25  # (40 + 60) / 4


# ── Rate Limiter Memory Hygiene ───────────────────────────────────────────────


class TestRateLimiterMemory:
    """Ensure the in-memory rate limiter doesn't leak memory."""

    @pytest.fixture
    def limiter(self):
        from auth_service import RateLimiter
        return RateLimiter()

    def test_pruned_entries_are_removed(self, limiter):
        """After all attempts expire, the internal list should be empty."""
        old = datetime.now(timezone.utc) - timedelta(minutes=60)
        limiter._attempts["key"] = [old] * 50

        limiter.is_allowed("key", max_attempts=5, window_minutes=15)
        assert len(limiter._attempts["key"]) == 0

    def test_clear_removes_key_entirely(self, limiter):
        limiter.record_attempt("key")
        limiter.clear("key")
        assert "key" not in limiter._attempts

    def test_record_does_not_duplicate_keys(self, limiter):
        limiter.record_attempt("key")
        limiter.record_attempt("key")
        assert len(limiter._attempts["key"]) == 2  # Two entries, one key


# ── Sliding Window Token Budget ───────────────────────────────────────────────


class TestSlidingWindowTokenBudget:
    """Verify the sliding window respects the token cap."""

    @staticmethod
    def _msgs(n, chars_per_msg=100):
        return [{"role": "user", "content": "x" * chars_per_msg} for _ in range(n)]

    def test_output_fits_within_token_budget(self):
        from main import get_recent_history, estimate_tokens

        result = get_recent_history(self._msgs(20, 500), max_messages=20, max_tokens=200)
        assert estimate_tokens(result) <= 200 or len(result) <= 2

    def test_does_not_trim_when_under_budget(self):
        from main import get_recent_history

        msgs = self._msgs(4, 10)  # 4 msgs × 10 chars = ~10 tokens
        result = get_recent_history(msgs, max_messages=10, max_tokens=4000)
        assert len(result) == 4

    def test_returns_copy_not_reference(self):
        """Modifications to the result must not affect the original list."""
        from main import get_recent_history

        original = self._msgs(3)
        result = get_recent_history(original, max_messages=10)
        result.pop()
        assert len(original) == 3  # Original unchanged


# ── Unique ID Generation ─────────────────────────────────────────────────────


class TestUniqueIdGeneration:
    """Verify model IDs are unique and properly prefixed."""

    def test_user_ids_are_unique(self):
        from models import generate_id

        ids = {generate_id("user_") for _ in range(100)}
        assert len(ids) == 100

    def test_ids_carry_prefix(self):
        from models import generate_id

        assert generate_id("user_").startswith("user_")
        assert generate_id("doc_").startswith("doc_")

    def test_empty_prefix_is_valid(self):
        from models import generate_id

        assert len(generate_id("")) > 0
