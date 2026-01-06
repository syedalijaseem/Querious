"""Ownership validation helpers.

Reusable functions ensuring users can only access their own resources.
All functions raise HTTPException 404 if resource doesn't exist or user doesn't own it.
"""

from fastapi import HTTPException


def get_user_chat(db, chat_id: str, user_id: str):
    """Get a chat that belongs to the specified user.
    
    Args:
        db: MongoDB database instance
        chat_id: ID of the chat to retrieve
        user_id: ID of the user who should own the chat
        
    Returns:
        Chat document if found and owned by user
        
    Raises:
        HTTPException 404 if chat not found or not owned by user
    """
    chat = db.chats.find_one({"id": chat_id, "user_id": user_id})
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat


def get_user_project(db, project_id: str, user_id: str):
    """Get a project that belongs to the specified user.
    
    Args:
        db: MongoDB database instance
        project_id: ID of the project to retrieve
        user_id: ID of the user who should own the project
        
    Returns:
        Project document if found and owned by user
        
    Raises:
        HTTPException 404 if project not found or not owned by user
    """
    project = db.projects.find_one({"id": project_id, "user_id": user_id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


def verify_document_ownership(db, document_id: str, user_id: str):
    """Verify a document belongs to a scope (chat/project) owned by the user.
    
    Args:
        db: MongoDB database instance
        document_id: ID of the document to verify
        user_id: ID of the user who should own the parent scope
        
    Returns:
        Document if found and parent scope is owned by user
        
    Raises:
        HTTPException 404 if document not found or parent scope not owned by user
    """
    doc = db.documents.find_one({"id": document_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Verify parent scope belongs to user
    if doc.get("scope_type") == "chat":
        parent = db.chats.find_one({"id": doc["scope_id"], "user_id": user_id})
    else:
        parent = db.projects.find_one({"id": doc["scope_id"], "user_id": user_id})
    
    if not parent:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return doc


def verify_scope_ownership(db, scope_type: str, scope_id: str, user_id: str):
    """Verify a scope (chat or project) belongs to the user.
    
    Args:
        db: MongoDB database instance
        scope_type: Either "chat" or "project"
        scope_id: ID of the scope to verify
        user_id: ID of the user who should own the scope
        
    Returns:
        Scope document if found and owned by user
        
    Raises:
        HTTPException 404 if scope not found or not owned by user
    """
    if scope_type == "chat":
        return get_user_chat(db, scope_id, user_id)
    else:
        return get_user_project(db, scope_id, user_id)
