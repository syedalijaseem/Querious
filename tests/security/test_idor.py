# IDOR Security Tests
# Tests to verify users cannot access other users' resources

import pytest
from unittest.mock import MagicMock, patch


class TestChatIDOR:
    """Tests for chat-related IDOR prevention."""

    def test_cannot_view_other_users_chat(self, mock_db, sample_user, sample_chat):
        """User should not be able to view another user's chat."""
        from helpers.ownership import get_user_chat
        from fastapi import HTTPException
        
        # Chat belongs to different user
        sample_chat["user_id"] = "other-user-456"
        mock_db.chats.find_one.return_value = None  # Query with user_id won't find it
        
        with pytest.raises(HTTPException) as exc:
            get_user_chat(mock_db, sample_chat["id"], sample_user["id"])
        
        assert exc.value.status_code == 404
        assert "not found" in exc.value.detail.lower()

    def test_cannot_delete_other_users_chat(self, mock_db, sample_user, sample_chat):
        """User should not be able to delete another user's chat."""
        from helpers.ownership import get_user_chat
        from fastapi import HTTPException
        
        sample_chat["user_id"] = "other-user-456"
        mock_db.chats.find_one.return_value = None
        
        with pytest.raises(HTTPException) as exc:
            get_user_chat(mock_db, sample_chat["id"], sample_user["id"])
        
        assert exc.value.status_code == 404

    def test_cannot_message_other_users_chat(self, mock_db, sample_user, sample_chat):
        """User should not be able to add messages to another user's chat."""
        from helpers.ownership import get_user_chat
        from fastapi import HTTPException
        
        sample_chat["user_id"] = "other-user-456"
        mock_db.chats.find_one.return_value = None
        
        with pytest.raises(HTTPException) as exc:
            get_user_chat(mock_db, sample_chat["id"], sample_user["id"])
        
        assert exc.value.status_code == 404


class TestProjectIDOR:
    """Tests for project-related IDOR prevention."""

    def test_cannot_view_other_users_project(self, mock_db, sample_user, sample_project):
        """User should not be able to view another user's project."""
        from helpers.ownership import get_user_project
        from fastapi import HTTPException
        
        sample_project["user_id"] = "other-user-456"
        mock_db.projects.find_one.return_value = None
        
        with pytest.raises(HTTPException) as exc:
            get_user_project(mock_db, sample_project["id"], sample_user["id"])
        
        assert exc.value.status_code == 404
        assert "not found" in exc.value.detail.lower()

    def test_cannot_delete_other_users_project(self, mock_db, sample_user, sample_project):
        """User should not be able to delete another user's project."""
        from helpers.ownership import get_user_project
        from fastapi import HTTPException
        
        sample_project["user_id"] = "other-user-456"
        mock_db.projects.find_one.return_value = None
        
        with pytest.raises(HTTPException) as exc:
            get_user_project(mock_db, sample_project["id"], sample_user["id"])
        
        assert exc.value.status_code == 404


class TestDocumentIDOR:
    """Tests for document-related IDOR prevention."""

    def test_cannot_view_other_users_documents(self, mock_db, sample_user):
        """User should not be able to view documents in another user's scope."""
        from helpers.ownership import verify_document_ownership
        from fastapi import HTTPException
        
        # Document exists but belongs to scope owned by different user
        mock_db.documents.find_one.return_value = {
            "id": "doc-123",
            "scope_type": "chat",
            "scope_id": "other-chat-456"
        }
        mock_db.chats.find_one.return_value = None  # User doesn't own the parent chat
        
        with pytest.raises(HTTPException) as exc:
            verify_document_ownership(mock_db, "doc-123", sample_user["id"])
        
        assert exc.value.status_code == 404

    def test_cannot_delete_other_users_documents(self, mock_db, sample_user):
        """User should not be able to delete documents in another user's scope."""
        from helpers.ownership import verify_document_ownership
        from fastapi import HTTPException
        
        mock_db.documents.find_one.return_value = {
            "id": "doc-123",
            "scope_type": "project",
            "scope_id": "other-project-456"
        }
        mock_db.projects.find_one.return_value = None
        
        with pytest.raises(HTTPException) as exc:
            verify_document_ownership(mock_db, "doc-123", sample_user["id"])
        
        assert exc.value.status_code == 404


class TestQueryIDOR:
    """Tests for query-related IDOR prevention."""

    def test_cannot_query_other_users_chat(self, mock_db, sample_user, sample_chat):
        """User should not be able to query documents in another user's chat."""
        from helpers.ownership import get_user_chat
        from fastapi import HTTPException
        
        sample_chat["user_id"] = "other-user-456"
        mock_db.chats.find_one.return_value = None
        
        with pytest.raises(HTTPException) as exc:
            get_user_chat(mock_db, sample_chat["id"], sample_user["id"])
        
        assert exc.value.status_code == 404


class TestUploadIDOR:
    """Tests for upload-related IDOR prevention."""

    def test_cannot_upload_to_other_users_scope(self, mock_db, sample_user):
        """User should not be able to upload documents to another user's scope."""
        from helpers.ownership import verify_scope_ownership
        from fastapi import HTTPException
        
        # Chat owned by different user
        mock_db.chats.find_one.return_value = None
        
        with pytest.raises(HTTPException) as exc:
            verify_scope_ownership(mock_db, "chat", "other-chat-456", sample_user["id"])
        
        assert exc.value.status_code == 404


class TestErrorResponseSecurity:
    """Tests to verify error responses don't leak information."""

    def test_nonexistent_resource_returns_404(self, mock_db, sample_user):
        """Non-existent resources should return 404."""
        from helpers.ownership import get_user_chat
        from fastapi import HTTPException
        
        mock_db.chats.find_one.return_value = None
        
        with pytest.raises(HTTPException) as exc:
            get_user_chat(mock_db, "nonexistent-chat", sample_user["id"])
        
        assert exc.value.status_code == 404

    def test_unauthorized_resource_returns_404_not_403(self, mock_db, sample_user):
        """Unauthorized access should return 404, not 403 (avoid info leak)."""
        from helpers.ownership import get_user_chat
        from fastapi import HTTPException
        
        # Resource exists but user doesn't own it
        mock_db.chats.find_one.return_value = None  # Query includes user_id, so no match
        
        with pytest.raises(HTTPException) as exc:
            get_user_chat(mock_db, "existing-but-not-owned", sample_user["id"])
        
        # Should be 404, not 403, to avoid leaking that resource exists
        assert exc.value.status_code == 404
        assert exc.value.status_code != 403
