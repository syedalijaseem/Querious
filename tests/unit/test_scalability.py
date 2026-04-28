"""Scalability tests.

Covers deterministic chunk ID generation, plan-limit enforcement
across tiers, and history sliding-window behaviour.
"""

import pytest


# ── Deterministic Chunk IDs ───────────────────────────────────────────────────


class TestChunkIdGeneration:
    """Idempotent ingestion relies on deterministic chunk IDs."""

    def test_same_inputs_produce_same_id(self):
        from chunk_service import generate_chunk_id

        id1 = generate_chunk_id("doc-A", 0)
        id2 = generate_chunk_id("doc-A", 0)
        assert id1 == id2

    def test_different_index_produces_different_id(self):
        from chunk_service import generate_chunk_id

        id1 = generate_chunk_id("doc-A", 0)
        id2 = generate_chunk_id("doc-A", 1)
        assert id1 != id2

    def test_different_document_produces_different_id(self):
        from chunk_service import generate_chunk_id

        id1 = generate_chunk_id("doc-A", 0)
        id2 = generate_chunk_id("doc-B", 0)
        assert id1 != id2

    def test_id_is_valid_uuid(self):
        import uuid
        from chunk_service import generate_chunk_id

        cid = generate_chunk_id("doc-A", 0)
        parsed = uuid.UUID(cid)  # Raises if invalid
        assert str(parsed) == cid


# ── Plan Limit Enforcement ────────────────────────────────────────────────────


class TestPlanLimits:
    """Verify resource limits scale correctly across subscription tiers."""

    @pytest.fixture(autouse=True)
    def _load_limits(self):
        from shared_utils import PLAN_LIMITS
        self.limits = PLAN_LIMITS

    def test_free_tier_has_finite_project_limit(self):
        assert isinstance(self.limits["free"]["projects"], int)
        assert self.limits["free"]["projects"] > 0

    def test_free_tier_has_finite_chat_limit(self):
        assert isinstance(self.limits["free"]["chats"], int)
        assert self.limits["free"]["chats"] > 0

    def test_free_tier_has_finite_document_limit(self):
        assert isinstance(self.limits["free"]["documents"], int)
        assert self.limits["free"]["documents"] > 0

    def test_pro_limits_exceed_free(self):
        free = self.limits["free"]
        pro = self.limits["pro"]
        assert pro["projects"] > free["projects"]
        assert pro["token_limit"] > free["token_limit"]
        assert pro["docs_per_scope"] > free["docs_per_scope"]

    def test_premium_allows_unlimited_core_resources(self):
        premium = self.limits["premium"]
        assert premium["projects"] is None
        assert premium["chats"] is None
        assert premium["documents"] is None

    def test_token_limits_increase_per_tier(self):
        free_t = self.limits["free"]["token_limit"]
        pro_t = self.limits["pro"]["token_limit"]
        premium_t = self.limits["premium"]["token_limit"]
        assert free_t < pro_t < premium_t

    def test_docs_per_scope_increases_per_tier(self):
        assert (
            self.limits["free"]["docs_per_scope"]
            < self.limits["pro"]["docs_per_scope"]
            < self.limits["premium"]["docs_per_scope"]
        )

    def test_all_plans_have_required_keys(self):
        required = {"projects", "chats", "documents", "docs_per_scope", "token_limit"}
        for plan in ("free", "pro", "premium"):
            assert required.issubset(self.limits[plan].keys()), f"{plan} missing keys"


# ── Sliding Window ────────────────────────────────────────────────────────────


class TestSlidingWindow:
    """Verify history truncation keeps the most recent context."""

    def _msgs(self, n, content="Hello world"):
        return [{"role": "user", "content": content} for _ in range(n)]

    def test_returns_empty_for_empty_input(self):
        from history_utils import get_recent_history

        assert get_recent_history([]) == []

    def test_caps_at_max_messages(self):
        from history_utils import get_recent_history

        result = get_recent_history(self._msgs(20), max_messages=6)
        assert len(result) <= 6

    def test_returns_all_when_under_cap(self):
        from history_utils import get_recent_history

        msgs = self._msgs(4)
        result = get_recent_history(msgs, max_messages=10)
        assert len(result) == 4

    def test_keeps_most_recent_messages(self):
        from history_utils import get_recent_history

        msgs = [{"role": "user", "content": f"msg-{i}"} for i in range(20)]
        result = get_recent_history(msgs, max_messages=4)
        # Should keep the last 4
        assert result[-1]["content"] == "msg-19"

    def test_trims_by_token_budget(self):
        from history_utils import get_recent_history

        # Each message is ~250 tokens (1000 chars / 4)
        big = self._msgs(10, content="x" * 1000)
        result = get_recent_history(big, max_messages=10, max_tokens=500)
        assert len(result) < 10

    def test_preserves_minimum_two_messages(self):
        """Even with a tiny token budget, at least 2 messages remain."""
        from history_utils import get_recent_history

        big = self._msgs(10, content="x" * 5000)
        result = get_recent_history(big, max_messages=10, max_tokens=1)
        assert len(result) >= 2
