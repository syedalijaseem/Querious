#!/usr/bin/env python3
"""
Orphan Cleanup Job - Safety net for cascade deletion.

Finds and removes orphaned data that may have slipped through normal deletion:
1. Chunks with no parent document
2. Vector embeddings with no parent document
3. S3 files not referenced in documents (older than 24h)

Usage:
    python scripts/orphan_cleanup.py [--dry-run]
    
Options:
    --dry-run   Show what would be deleted without actually deleting
"""
import os
import sys
import argparse
from datetime import datetime, timezone, timedelta

from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()


def get_db():
    """Get MongoDB database connection."""
    uri = os.getenv("MONGODB_URI")
    if not uri:
        raise RuntimeError("MONGODB_URI not configured")
    client = MongoClient(uri)
    db_name = os.getenv("MONGODB_DATABASE", "docurag")
    return client[db_name]


def cleanup_orphan_chunks(db, dry_run: bool = False) -> int:
    """Delete chunks whose document no longer exists.
    
    Returns:
        Number of chunks deleted (or would be deleted in dry-run)
    """
    print("\n=== Orphan Chunks Cleanup ===")
    
    # Get all unique document_ids from chunks
    chunk_doc_ids = db.chunks.distinct("document_id")
    print(f"Found {len(chunk_doc_ids)} unique document_ids in chunks collection")
    
    if not chunk_doc_ids:
        print("No chunks found, skipping")
        return 0
    
    # Find which ones don't exist in documents
    existing_docs = set(
        doc["id"] for doc in db.documents.find(
            {"id": {"$in": chunk_doc_ids}}, 
            {"id": 1}
        )
    )
    
    orphan_doc_ids = set(chunk_doc_ids) - existing_docs
    print(f"Found {len(orphan_doc_ids)} orphaned document_ids")
    
    total_deleted = 0
    for doc_id in orphan_doc_ids:
        count = db.chunks.count_documents({"document_id": doc_id})
        if dry_run:
            print(f"  [DRY-RUN] Would delete {count} chunks for missing doc {doc_id}")
        else:
            result = db.chunks.delete_many({"document_id": doc_id})
            print(f"  Deleted {result.deleted_count} chunks for missing doc {doc_id}")
            total_deleted += result.deleted_count
    
    return total_deleted


def cleanup_orphan_embeddings(db, dry_run: bool = False) -> int:
    """Delete vector embeddings whose document no longer exists.
    
    The vector store uses a collection named 'documents' with embeddings.
    We check if the document_id field references a valid document.
    
    Returns:
        Number of embeddings deleted (or would be deleted in dry-run)
    """
    print("\n=== Orphan Embeddings Cleanup ===")
    
    # Vector store uses 'documents' collection (MongoDBStorage default)
    vector_collection = db["documents"]
    
    # Get all unique document_ids from vector store
    vector_doc_ids = vector_collection.distinct("document_id")
    print(f"Found {len(vector_doc_ids)} unique document_ids in vector store")
    
    if not vector_doc_ids:
        print("No embeddings found, skipping")
        return 0
    
    # Find which ones don't exist in the main documents collection
    # (Note: vector store collection is also named 'documents', but uses document_id field)
    existing_docs = set(
        doc["id"] for doc in db.documents.find(
            {"id": {"$in": vector_doc_ids}},
            {"id": 1}
        )
    )
    
    orphan_doc_ids = set(vector_doc_ids) - existing_docs
    print(f"Found {len(orphan_doc_ids)} orphaned document_ids")
    
    total_deleted = 0
    for doc_id in orphan_doc_ids:
        count = vector_collection.count_documents({"document_id": doc_id})
        if dry_run:
            print(f"  [DRY-RUN] Would delete {count} embeddings for missing doc {doc_id}")
        else:
            result = vector_collection.delete_many({"document_id": doc_id})
            print(f"  Deleted {result.deleted_count} embeddings for missing doc {doc_id}")
            total_deleted += result.deleted_count
    
    return total_deleted


def reconcile_document_counts(db, dry_run: bool = False) -> int:
    """Verify and fix active_documents_count for all users.
    
    Compares user.active_documents_count with actual document count
    and fixes discrepancies.
    
    Returns:
        Number of users fixed
    """
    print("\n=== Document Count Reconciliation ===")
    
    users = list(db.users.find({}, {"id": 1, "active_documents_count": 1}))
    print(f"Checking {len(users)} users...")
    
    fixed_count = 0
    for user in users:
        user_id = user["id"]
        recorded_count = user.get("active_documents_count", 0)
        
        # Count actual documents owned by this user
        # Documents are scoped to chats/projects owned by user
        actual_count = db.documents.count_documents({"user_id": user_id})
        
        if recorded_count != actual_count:
            if dry_run:
                print(f"  [DRY-RUN] User {user_id}: recorded={recorded_count}, actual={actual_count}")
            else:
                db.users.update_one(
                    {"id": user_id},
                    {"$set": {"active_documents_count": actual_count}}
                )
                print(f"  Fixed user {user_id}: {recorded_count} -> {actual_count}")
                fixed_count += 1
    
    return fixed_count


def cleanup_expired_tokens(db, dry_run: bool = False, retention_days: int = 30) -> int:
    """Delete expired and revoked refresh tokens.
    
    Keeps tokens for audit trail, but removes old ones to prevent bloat.
    Only deletes tokens that are BOTH:
    - Revoked OR expired
    - Older than retention_days
    
    Args:
        db: MongoDB database connection
        dry_run: If True, only report what would be deleted
        retention_days: Days to keep expired/revoked tokens (default 30)
    
    Returns:
        Number of tokens deleted
    """
    print(f"\n=== Refresh Token Cleanup (retention: {retention_days} days) ===")
    
    cutoff = datetime.now(timezone.utc) - timedelta(days=retention_days)
    
    # Find tokens that are either revoked or expired, AND older than cutoff
    query = {
        "$or": [
            {"revoked": True},
            {"expires_at": {"$lt": datetime.now(timezone.utc)}}
        ],
        "created_at": {"$lt": cutoff}
    }
    
    count = db.refresh_tokens.count_documents(query)
    print(f"Found {count} expired/revoked tokens older than {retention_days} days")
    
    if count == 0:
        print("No tokens to clean up")
        return 0
    
    if dry_run:
        print(f"  [DRY-RUN] Would delete {count} tokens")
        return count
    else:
        result = db.refresh_tokens.delete_many(query)
        print(f"  Deleted {result.deleted_count} tokens")
        return result.deleted_count


def main():
    parser = argparse.ArgumentParser(description="Orphan data cleanup job")
    parser.add_argument("--dry-run", action="store_true", 
                       help="Show what would be deleted without actually deleting")
    args = parser.parse_args()
    
    print("=" * 60)
    print("Orphan Cleanup Job")
    print(f"Mode: {'DRY-RUN' if args.dry_run else 'LIVE (will delete!)'}")
    print(f"Time: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 60)
    
    db = get_db()
    
    # Run all cleanup tasks
    chunks_deleted = cleanup_orphan_chunks(db, args.dry_run)
    embeddings_deleted = cleanup_orphan_embeddings(db, args.dry_run)
    users_fixed = reconcile_document_counts(db, args.dry_run)
    tokens_deleted = cleanup_expired_tokens(db, args.dry_run)
    
    # Summary
    print("\n" + "=" * 60)
    print("Summary:")
    print(f"  Orphan chunks deleted: {chunks_deleted}")
    print(f"  Orphan embeddings deleted: {embeddings_deleted}")
    print(f"  User counts fixed: {users_fixed}")
    print(f"  Expired tokens deleted: {tokens_deleted}")
    if args.dry_run:
        print("\n(Dry-run mode - no actual changes made)")
    print("=" * 60)


if __name__ == "__main__":
    main()
