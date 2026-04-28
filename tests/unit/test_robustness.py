"""Robustness tests.

Covers Pydantic model validation, cascade deletion resilience,
and PDF upload boundary conditions.
"""

import pytest
from unittest.mock import MagicMock, patch


# ── Model Validation ──────────────────────────────────────────────────────────


class TestRegisterRequestValidation:
    """Ensure registration rejects weak credentials at the boundary."""

    def test_rejects_email_without_at(self):
        from models import RegisterRequest

        with pytest.raises(ValueError, match="[Ii]nvalid email"):
            RegisterRequest(email="no-at-sign.com", password="StrongP1!", name="Test")

    def test_rejects_email_without_domain_dot(self):
        from models import RegisterRequest

        with pytest.raises(ValueError, match="[Ii]nvalid email"):
            RegisterRequest(email="user@nodot", password="StrongP1!", name="Test")

    def test_normalises_email_to_lowercase(self):
        from models import RegisterRequest

        r = RegisterRequest(email="USER@Example.COM", password="StrongP1!", name="Test")
        assert r.email == "user@example.com"

    def test_rejects_password_too_short(self):
        from models import RegisterRequest

        with pytest.raises(ValueError, match="8 characters"):
            RegisterRequest(email="a@b.com", password="Sh0rt", name="Test")

    def test_rejects_password_without_uppercase(self):
        from models import RegisterRequest

        with pytest.raises(ValueError, match="uppercase"):
            RegisterRequest(email="a@b.com", password="nouppercase1", name="Test")

    def test_rejects_password_without_lowercase(self):
        from models import RegisterRequest

        with pytest.raises(ValueError, match="lowercase"):
            RegisterRequest(email="a@b.com", password="NOLOWERCASE1", name="Test")

    def test_rejects_password_without_digit(self):
        from models import RegisterRequest

        with pytest.raises(ValueError, match="number"):
            RegisterRequest(email="a@b.com", password="NoDigitHere!", name="Test")

    def test_accepts_valid_registration(self):
        from models import RegisterRequest

        r = RegisterRequest(email="a@b.com", password="Valid1Pass", name="Test")
        assert r.email == "a@b.com"

    def test_password_at_minimum_length_boundary(self):
        """Exactly 8 chars with all requirements met should pass."""
        from models import RegisterRequest

        r = RegisterRequest(email="a@b.com", password="Abcdefg1", name="Test")
        assert r.password == "Abcdefg1"


class TestPasswordResetValidation:
    """PasswordResetComplete must enforce same rules as registration."""

    def test_rejects_weak_new_password(self):
        from models import PasswordResetComplete

        with pytest.raises(ValueError, match="8 characters"):
            PasswordResetComplete(token="abc", new_password="short")

    def test_accepts_strong_new_password(self):
        from models import PasswordResetComplete

        r = PasswordResetComplete(token="abc", new_password="NewPass1!")
        assert r.new_password == "NewPass1!"


class TestEnumValidation:
    """Ensure enums reject out-of-band values."""

    def test_invalid_message_role(self):
        from models import MessageRole

        with pytest.raises(ValueError):
            MessageRole("admin")

    def test_invalid_scope_type(self):
        from models import ScopeType

        with pytest.raises(ValueError):
            ScopeType("workspace")

    def test_invalid_document_status(self):
        from models import DocumentStatus

        with pytest.raises(ValueError):
            DocumentStatus("hacked")

    def test_invalid_subscription_plan(self):
        from models import SubscriptionPlan

        with pytest.raises(ValueError):
            SubscriptionPlan("enterprise")

    def test_valid_enums_accepted(self):
        from models import MessageRole, ScopeType, DocumentStatus

        assert MessageRole("user") == MessageRole.USER
        assert ScopeType("chat") == ScopeType.CHAT
        assert DocumentStatus("ready") == DocumentStatus.READY


# ── Cascade Deletion Resilience ───────────────────────────────────────────────


class TestSafeDeleteDocument:
    """Verify safe_delete_document handles partial failures gracefully."""

    def _make_doc(self, s3_key="files/doc.pdf"):
        return {"id": "doc-1", "s3_key": s3_key}

    def test_succeeds_when_all_steps_pass(self):
        from document_service import safe_delete_document

        db = MagicMock()
        vs = MagicMock()
        fs = MagicMock()
        vs.delete_by_document_id.return_value = 5

        with patch("document_service.delete_chunks", return_value=3):
            result = safe_delete_document(db, vs, fs, self._make_doc(), "scope-1")
        assert result is True
        vs.delete_by_document_id.assert_called_once_with("doc-1")
        fs.delete_file.assert_called_once_with("files/doc.pdf")

    def test_continues_after_vector_deletion_failure(self):
        from document_service import safe_delete_document

        db = MagicMock()
        vs = MagicMock()
        fs = MagicMock()
        vs.delete_by_document_id.side_effect = RuntimeError("DB down")

        result = safe_delete_document(db, vs, fs, self._make_doc(), "scope-1")
        # Critical failure → returns False, but S3 cleanup still attempted
        assert result is False
        fs.delete_file.assert_called_once()

    def test_continues_after_chunk_deletion_failure(self):
        from document_service import safe_delete_document

        db = MagicMock()
        vs = MagicMock()
        fs = MagicMock()

        with patch("document_service.delete_chunks", side_effect=RuntimeError("fail")):
            result = safe_delete_document(db, vs, fs, self._make_doc(), "scope-1")
        # Chunks failed → False, but vector + S3 still ran
        assert result is False

    def test_s3_failure_does_not_mark_as_failed(self):
        """S3 failures are best-effort — orphan cleanup will handle them."""
        from document_service import safe_delete_document

        db = MagicMock()
        vs = MagicMock()
        fs = MagicMock()
        fs.delete_file.side_effect = RuntimeError("S3 timeout")

        with patch("document_service.delete_chunks", return_value=3):
            result = safe_delete_document(db, vs, fs, self._make_doc(), "scope-1")
        assert result is True  # S3 failure is non-critical

    def test_handles_missing_s3_key(self):
        """Documents without s3_key (e.g., linked docs) must not crash."""
        from document_service import safe_delete_document

        db = MagicMock()
        vs = MagicMock()
        fs = MagicMock()

        with patch("document_service.delete_chunks", return_value=0):
            result = safe_delete_document(db, vs, fs, self._make_doc(s3_key=None), "scope-1")
        assert result is True
        fs.delete_file.assert_not_called()


# ── PDF Upload Boundary Conditions ────────────────────────────────────────────


class TestPDFValidation:
    """Defence-in-depth checks for file uploads."""

    def test_valid_pdf_header_accepted(self):
        from shared_utils import validate_pdf_content

        assert validate_pdf_content(b"%PDF-1.7 ...") is True

    def test_latex_with_pdf_extension_rejected(self):
        from shared_utils import validate_pdf_content

        assert validate_pdf_content(b"\\documentclass{article}") is False

    def test_zip_magic_bytes_rejected(self):
        from shared_utils import validate_pdf_content

        assert validate_pdf_content(b"PK\x03\x04 ...") is False

    def test_null_bytes_rejected(self):
        from shared_utils import validate_pdf_content

        assert validate_pdf_content(b"\x00\x00\x00\x00") is False
