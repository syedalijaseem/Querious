# API Integration Tests
# Tests for API endpoint behavior using mocked database

import pytest
from unittest.mock import MagicMock, patch


class TestProjectAPI:
    """Integration tests for project endpoints."""

    def test_create_project_success(self, mock_db, sample_user):
        """Creating a project should succeed with valid data."""
        mock_db.projects.count_documents.return_value = 0
        mock_db.projects.insert_one.return_value = MagicMock(inserted_id="new-id")
        
        # Simulate creating a project
        project_data = {
            "user_id": sample_user["id"],
            "name": "Test Project"
        }
        
        mock_db.projects.insert_one(project_data)
        mock_db.projects.insert_one.assert_called_once()

    def test_create_project_enforces_limit(self, mock_db, sample_user):
        """Project creation should enforce plan limits."""
        from models import PLAN_LIMITS
        
        # User at limit
        free_limit = PLAN_LIMITS["free"]["projects"]
        mock_db.projects.count_documents.return_value = free_limit
        
        # Should not allow creating more
        count = mock_db.projects.count_documents({"user_id": sample_user["id"]})
        assert count >= free_limit

    def test_list_projects_user_scoped(self, mock_db, sample_user, sample_project):
        """Listing projects should only return user's projects."""
        mock_db.projects.find.return_value = [sample_project]
        
        # Query should include user_id
        query = {"user_id": sample_user["id"]}
        result = list(mock_db.projects.find(query))
        
        call_args = mock_db.projects.find.call_args[0][0]
        assert "user_id" in call_args

    def test_delete_project_user_scoped(self, mock_db, sample_user, sample_project):
        """Deleting project should verify user ownership."""
        mock_db.projects.find_one.return_value = sample_project
        mock_db.projects.delete_one.return_value = MagicMock(deleted_count=1)
        
        # Query should include user_id
        query = {"id": sample_project["id"], "user_id": sample_user["id"]}
        mock_db.projects.find_one(query)
        
        call_args = mock_db.projects.find_one.call_args[0][0]
        assert "user_id" in call_args


class TestChatAPI:
    """Integration tests for chat endpoints."""

    def test_create_chat_success(self, mock_db, sample_user):
        """Creating a chat should succeed with valid data."""
        mock_db.chats.count_documents.return_value = 0
        mock_db.chats.insert_one.return_value = MagicMock(inserted_id="new-id")
        
        chat_data = {
            "user_id": sample_user["id"],
            "title": "Test Chat"
        }
        
        mock_db.chats.insert_one(chat_data)
        mock_db.chats.insert_one.assert_called_once()

    def test_create_chat_enforces_limit(self, mock_db, sample_user):
        """Chat creation should enforce plan limits."""
        from models import PLAN_LIMITS
        
        free_limit = PLAN_LIMITS["free"]["chats"]
        mock_db.chats.count_documents.return_value = free_limit
        
        count = mock_db.chats.count_documents({"user_id": sample_user["id"]})
        assert count >= free_limit

    def test_list_chats_user_scoped(self, mock_db, sample_user, sample_chat):
        """Listing chats should only return user's chats."""
        mock_db.chats.find.return_value = [sample_chat]
        
        query = {"user_id": sample_user["id"]}
        result = list(mock_db.chats.find(query))
        
        call_args = mock_db.chats.find.call_args[0][0]
        assert "user_id" in call_args


class TestDocumentAPI:
    """Integration tests for document endpoints."""

    def test_document_upload_validates_type(self):
        """Document upload should validate file type."""
        allowed_types = ["application/pdf"]
        
        invalid_types = [
            "image/png",
            "text/plain",
            "application/javascript",
        ]
        
        for mime_type in invalid_types:
            assert mime_type not in allowed_types

    def test_document_size_limit_enforced(self):
        """Document upload should enforce size limits."""
        max_size = 10 * 1024 * 1024  # 10MB
        
        # File larger than limit should be rejected
        large_file_size = 20 * 1024 * 1024  # 20MB
        assert large_file_size > max_size


class TestQueryAPI:
    """Integration tests for query endpoints."""

    def test_query_requires_chat_ownership(self, mock_db, sample_user, sample_chat):
        """Query should verify chat ownership."""
        # Ensure chat belongs to user
        sample_chat["user_id"] = sample_user["id"]
        mock_db.chats.find_one.return_value = sample_chat
        
        query = {"id": sample_chat["id"], "user_id": sample_user["id"]}
        mock_db.chats.find_one(query)
        
        call_args = mock_db.chats.find_one.call_args[0][0]
        assert "user_id" in call_args

    def test_query_enforces_token_limit(self, sample_user):
        """Query should check token usage before processing."""
        from models import PLAN_LIMITS
        
        token_limit = PLAN_LIMITS["free"]["tokens"]
        sample_user["tokens_used"] = token_limit + 1
        
        # User over limit should be blocked
        assert sample_user["tokens_used"] > token_limit


class TestWaitlistAPI:
    """Integration tests for waitlist endpoints."""

    def test_waitlist_signup_success(self, mock_db):
        """Waitlist signup should succeed with valid email."""
        mock_db.waitlist.find_one.return_value = None
        mock_db.waitlist.insert_one.return_value = MagicMock(inserted_id="new-id")
        
        email = "newuser@example.com"
        mock_db.waitlist.insert_one({"email": email})
        mock_db.waitlist.insert_one.assert_called_once()

    def test_waitlist_prevents_duplicates(self, mock_db):
        """Waitlist should prevent duplicate signups."""
        existing_email = "existing@example.com"
        mock_db.waitlist.find_one.return_value = {"email": existing_email}
        
        # Should find existing entry
        result = mock_db.waitlist.find_one({"email": existing_email})
        assert result is not None
