"""Document deletion service.

Provides safe_delete_document() as the ONLY way to delete document data.
All route handlers must use this - no inline deletion allowed.

Design Notes:
- Documents are scoped 1:1 to chats/projects (no dedup today)
- If deduplication is added later, enable reference counting below
- Counter represents documents that currently exist
- Failed deletions do not decrement the counter
"""
import logging
from chunk_service import delete_chunks

logger = logging.getLogger(__name__)


def safe_delete_document(
    db,
    vector_store,
    file_storage,
    doc: dict,
    scope_id: str
) -> bool:
    """Safely delete a document and all derived data.
    
    Follows strict deletion order:
    1. Vector embeddings (by document_id)
    2. Chunks (by document_id)
    3. S3 file (by s3_key)
    
    Document metadata deletion and counter decrement are handled by caller
    after all documents are processed (bulk operations).
    
    Args:
        db: MongoDB database connection
        vector_store: MongoDBStorage instance
        file_storage: S3 file storage instance
        doc: Document dict with id, s3_key, etc.
        scope_id: The chat_id or project_id being deleted
        
    Returns:
        True if critical deletions (vectors and chunks) succeeded.
        S3 failures are logged and handled by orphan cleanup.
    """
    doc_id = doc["id"]
    success = True
    
    # FUTURE: Enable when deduplication exists
    # remaining_refs = db.documents.count_documents({
    #     "id": doc_id,
    #     "scope_id": {"$ne": scope_id}
    # })
    # if remaining_refs > 0:
    #     logger.info("Document %s still referenced, skipping delete", doc_id)
    #     return True  # Not an error, just skip
    
    # 1. Delete vector embeddings (by document_id)
    try:
        deleted_vectors = vector_store.delete_by_document_id(doc_id)
        logger.debug("Deleted %d vector entries for document %s", deleted_vectors, doc_id)
    except Exception as e:
        logger.error("Failed to delete vectors for document %s: %s", doc_id, e)
        success = False
    
    # 2. Delete chunks (by document_id)
    try:
        deleted_chunks = delete_chunks(doc_id)
        logger.debug("Deleted %d chunks for document %s", deleted_chunks, doc_id)
    except Exception as e:
        logger.error("Failed to delete chunks for document %s: %s", doc_id, e)
        success = False
    
    # 3. Delete S3 file (best effort - orphan cleanup handles failures)
    if doc.get("s3_key"):
        try:
            file_storage.delete_file(doc["s3_key"])
            logger.debug("Deleted S3 file %s", doc["s3_key"])
        except Exception as e:
            logger.warning("Failed to delete S3 file %s: %s (orphan cleanup will handle)", 
                          doc["s3_key"], e)
            # Don't mark as failure - S3 cleanup job will catch orphans
    
    return success
