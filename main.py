import logging
from fastapi import FastAPI
import inngest.fast_api
from inngest.experimental import ai
from config import settings
import uuid
import os
import datetime
from data_loader import load_and_chunk_pdf, embed_texts
from vector_db import MongoDBStorage
from models import (
    IngestPdfEventData,
    QueryPdfEventData,
    RAGChunkAndSrc,
    RAGUpsertResult,
    SearchResult,
    QueryResult,
    ChunkWithPage,
)

# Config validation happens automatically on import via pydantic-settings


logger = logging.getLogger(__name__)

# --- History Sliding Window Configuration ---
HISTORY_CONFIG = {
    "max_messages": 10,      # 5 user + 5 assistant pairs
    "max_tokens": 4000,      # Hard cap as safety net
}

def estimate_tokens(messages: list[dict]) -> int:
    """Rough estimate: 1 token ≈ 4 characters."""
    text = "".join(m.get("content", "") for m in messages)
    return len(text) // 4

def get_recent_history(
    messages: list[dict],
    max_messages: int = HISTORY_CONFIG["max_messages"],
    max_tokens: int = HISTORY_CONFIG["max_tokens"]
) -> list[dict]:
    """Get recent conversation history with sliding window.
    
    Args:
        messages: Full conversation history
        max_messages: Maximum number of messages to keep
        max_tokens: Hard cap on total tokens in history
    
    Returns:
        Truncated history with most recent messages
    """
    if not messages:
        return []
    
    # Take last N messages
    recent = messages[-max_messages:] if len(messages) > max_messages else messages[:]
    
    # Safety: trim if still over token limit
    token_count = estimate_tokens(recent)
    
    while token_count > max_tokens and len(recent) > 2:
        recent = recent[2:]  # Remove oldest pair
        token_count = estimate_tokens(recent)
    
    return recent

# Use centralized config for environment detection
is_production = settings.is_production

inngest_client = inngest.Inngest(
    app_id="querious",
    logger=logging.getLogger("uvicorn"),
    is_production=is_production,
    serializer=inngest.PydanticSerializer()
)

@inngest_client.create_function(
    fn_id="RAG: Ingest PDF",
    trigger=inngest.TriggerEvent(event="rag/ingest_pdf"),
    throttle=inngest.Throttle(
        limit=1, count=2, period=datetime.timedelta(minutes=1)
    ),
    rate_limit=inngest.RateLimit(
        limit=1,
        period=datetime.timedelta(hours=4),
        key="event.data.pdf_path",
    ),
)
async def rag_ingest_pdf(ctx: inngest.Context):
    """Ingest a PDF document into the RAG system.
    
    M2 Refactored:
    - Uses chunk_service to save to chunks collection
    - References document_id instead of duplicating scope info
    - Updates Document status to 'ready' after completion
    """
    # Validate event data with Pydantic
    event_data = IngestPdfEventData(**ctx.event.data)
    document_id = event_data.document_id
    
    logger.info("========== Starting ingestion ==========")
    logger.info("Document ID: %s", document_id)
    logger.info("Filename: %s", event_data.filename)
    logger.info("PDF Path (S3 Key): %s", event_data.pdf_path)
    logger.info("Scope: %s / %s", event_data.scope_type, event_data.scope_id)
    
    def _load() -> RAGChunkAndSrc:
        import file_storage
        import os
        from chunk_service import update_document_status
        from models import DocumentStatus
        
        logger.info("Step 1: Downloading PDF from S3...")
        # Download PDF from S3 to temp file
        temp_path = file_storage.download_to_temp(event_data.pdf_path)
        logger.info("Downloaded to: %s", temp_path)
        
        try:
            # load_and_chunk_pdf extracts text chunks
            logger.info("Step 2: Parsing PDF and chunking...")
            chunks = load_and_chunk_pdf(temp_path)
            logger.info("Extracted %d chunks from PDF", len(chunks))
            
            # Validate we got content
            if not chunks:
                raise ValueError("PDF appears to be empty or unreadable")

            # Attach page info (for now assume sequential pages for each chunk)
            chunk_with_page = [
                ChunkWithPage(text=chunk, page=i + 1) for i, chunk in enumerate(chunks)
            ]
            logger.info("Step 2 complete: %d chunks with page info", len(chunk_with_page))
            return RAGChunkAndSrc(chunks=chunk_with_page, source_id=event_data.filename)
        except Exception as e:
            # Log error and leave status as pending for retry
            # In production, could set status to 'error' after max retries
            logger.error("PDF parsing failed for %s: %s", event_data.filename, e)
            raise
        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def _embed_and_save(chunks_and_src: RAGChunkAndSrc) -> RAGUpsertResult:
        """Embed chunks and save to chunks collection using chunk_service."""
        from chunk_service import save_chunks, update_document_status
        from models import DocumentStatus
        
        chunks = chunks_and_src.chunks
        logger.info("Step 3: Embedding %d chunks...", len(chunks))
        
        # Get text for embedding
        texts = [c.text for c in chunks]
        embeddings = embed_texts(texts)
        logger.info("Generated %d embeddings, dim=%d", len(embeddings), len(embeddings[0]) if embeddings else 0)
        
        # Prepare chunk data for chunk_service
        chunks_data = [
            {
                "text": chunks[i].text,
                "page_number": chunks[i].page,
                "chunk_index": i
            }
            for i in range(len(chunks))
        ]
        
        # Save chunks to chunks collection
        logger.info("Step 4: Saving chunks to MongoDB...")
        saved_count = save_chunks(document_id, chunks_data, embeddings)
        logger.info("Saved %d chunks to chunks collection", saved_count)
        
        # Update document status to ready
        logger.info("Step 5: Updating document status to READY...")
        update_document_status(document_id, DocumentStatus.READY)
        logger.info("========== Ingestion complete ==========")
        
        return RAGUpsertResult(ingested=saved_count)

    chunks_and_src = await ctx.step.run(
        "load-and-chunk", _load, output_type=RAGChunkAndSrc
    )
    ingested = await ctx.step.run(
        "embed-and-save", lambda: _embed_and_save(chunks_and_src), output_type=RAGUpsertResult
    )
    return ingested.model_dump()

@inngest_client.create_function(
    fn_id="RAG: Query PDF",
    trigger=inngest.TriggerEvent(event="rag/query_pdf_ai")
)
async def rag_query_pdf_ai(ctx: inngest.Context):
    # Validate event data with Pydantic
    event_data = QueryPdfEventData(**ctx.event.data)
    
    logger.info("========== Starting query ==========")
    logger.info("Question: %s...", event_data.question[:100])
    logger.info("Chat ID: %s", event_data.chat_id)
    logger.info("Scope: %s / %s", event_data.scope_type, event_data.scope_id)
    logger.info("Top K: %d", event_data.top_k)
    
    # --- System Prompt ---
    SYSTEM_PROMPT = """You are a helpful document assistant for Querious. Your role is to answer questions based ONLY on the provided context from the user's documents.

Rules:
- Only use information from the provided context
- If the context doesn't contain enough information, say so clearly
- Cite sources using [source: filename, page X] format
- Be concise but thorough
- If asked about something not in the context, don't make things up
- For follow-up questions, use conversation history for context"""
    
    # --- Max tokens by quality preset ---
    MAX_TOKENS_BY_CHUNKS = {
        5: 512,      # Quick
        10: 1024,    # Standard
        20: 2048,    # Thorough
        35: 4096,    # Deep
        50: 4096,    # Max
    }
    max_tokens = MAX_TOKENS_BY_CHUNKS.get(event_data.top_k, 1024)
    
    def _search() -> SearchResult:
        from chunk_search import search_for_scope, get_db
        
        logger.info("Step 1: Embedding question...")
        query_vec = embed_texts([event_data.question])[0]
        logger.info("Embedding generated, dim=%d", len(query_vec))
        
        # M3: Look up project_id for chat scopes to enable inherited search
        project_id = None
        include_project = True
        
        if event_data.scope_type.value == "chat":
            db = get_db()
            logger.info("Step 2: Looking up chat in DB...")
            chat = db.chats.find_one({"id": event_data.scope_id}, {"project_id": 1})
            logger.debug("Chat found: %s", chat)
            if chat and chat.get("project_id"):
                project_id = chat["project_id"]
                logger.info("Chat belongs to project: %s", project_id)
        
        # Use chunk_search with project inheritance (M3)
        logger.info("Step 3: Searching chunks...")
        logger.debug("Search params: scope_type=%s, scope_id=%s, project_id=%s", 
                     event_data.scope_type.value, event_data.scope_id, project_id)
        result = search_for_scope(
            query_vec, 
            scope_type=event_data.scope_type.value,
            scope_id=event_data.scope_id,
            top_k=event_data.top_k,
            include_project=include_project,
            project_id=project_id
        )
        
        logger.info("Search returned %d contexts", len(result.get('contexts', [])))
        logger.debug("Sources: %s", result.get('sources', []))
        logger.debug("Scores: %s", result.get('scores', []))
        
        # Store raw data for improved formatting
        return SearchResult(
            contexts=result.get("contexts", []),
            sources=result.get("sources", []),
            scores=result.get("scores", [])
        )

    # Support chat reset
    if event_data.question.lower() in ("reset", "clear", "new chat"):
        return QueryResult(
            answer="🔄 Chat history cleared.",
            sources=[],
            num_contexts=0,
            history=[]
        ).model_dump()

    result = await ctx.step.run(
        "embed-and-search", 
        _search,
        output_type=SearchResult
    )
    
    contexts = result.contexts
    sources = result.sources
    scores = result.scores

    # --- Handle empty or low quality results ---
    MIN_RELEVANCE_THRESHOLD = 0.3
    if not contexts or (scores and all(s < MIN_RELEVANCE_THRESHOLD for s in scores)):
        no_results_answer = (
            "I couldn't find relevant information in your documents to answer this question. "
            "Try rephrasing or make sure the relevant documents are uploaded."
        )
        history = list(event_data.history)
        history.append({"role": "user", "content": event_data.question})
        history.append({"role": "assistant", "content": no_results_answer})
        
        return QueryResult(
            answer=no_results_answer,
            sources=[],
            num_contexts=0,
            history=history,
            avg_confidence=0.0,
            tokens_used=0
        ).model_dump()

    # --- Improved context formatting with page numbers and scores ---
    context_blocks = []
    documents_used = set()
    for i, text in enumerate(contexts):
        source = sources[i] if i < len(sources) else "Unknown"
        score = scores[i] if i < len(scores) else 0.0
        page = i + 1  # Approximate page number
        documents_used.add(source)
        
        context_blocks.append(
            f"---\nSource: {source} (Page {page})\nRelevance: {score:.0%}\n{text}\n"
        )
    
    context_block = "\n".join(context_blocks)
    
    # --- Improved user prompt ---
    user_content = (
        f"Based on the following excerpts from your documents:\n\n"
        f"{context_block}\n"
        f"---\n"
        f"Question: {event_data.question}\n\n"
        f"Provide a clear, well-structured answer. Cite specific sources when referencing information."
    )

    adapter = ai.openai.Adapter(
        auth_key=settings.DEEPSEEK_API_KEY,
        model="deepseek-chat",
        base_url="https://api.deepseek.com/v1"
    )

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    # Apply sliding window to history
    recent_history = get_recent_history(event_data.history)
    logger.info("History: %d total, using %d recent (%d tokens est.)",
                len(event_data.history), len(recent_history), estimate_tokens(recent_history))
    
    messages.extend(recent_history)
    messages.append({"role": "user", "content": user_content})

    res = await ctx.step.ai.infer(
        "llm-answer",
        adapter=adapter,
        body={
            "max_tokens": max_tokens,
            "temperature": 0.3,  # More deterministic/factual
            "messages": messages
        }
    )

    answer = res["choices"][0]["message"]["content"].strip()
    
    # Track token usage with breakdown
    usage = res.get("usage", {})
    total_tokens = usage.get("total_tokens", 0)
    input_tokens = usage.get("prompt_tokens", 0)
    output_tokens = usage.get("completion_tokens", 0)
    
    logger.info("Tokens: %d input + %d output = %d total", input_tokens, output_tokens, total_tokens)
    
    if event_data.user_id and total_tokens > 0:
        def _update_tokens():
            from pymongo import MongoClient
            import os
            client = MongoClient(settings.MONGODB_URI)
            db_name = settings.MONGODB_DATABASE
            db = client[db_name]
            db.users.update_one(
                {"id": event_data.user_id},
                {"$inc": {"tokens_used": total_tokens}}
            )
            logger.info("Updated tokens_used for user %s: +%d", event_data.user_id, total_tokens)
        
        await ctx.step.run("update-token-usage", _update_tokens)

    # Update history with original question (not wrapped prompt)
    history = list(event_data.history)
    history.append({"role": "user", "content": event_data.question})
    history.append({"role": "assistant", "content": answer})

    # Compute analytics
    avg_conf = round(sum(scores)/len(scores), 3) if scores else 0.0

    return QueryResult(
        answer=answer,
        sources=sources,
        num_contexts=len(contexts),
        history=history,
        avg_confidence=avg_conf,
        tokens_used=total_tokens
    ).model_dump()


app = FastAPI(title="DocuRAG API")

# CORS configuration - permissive in dev, restricted in production
from fastapi.middleware.cors import CORSMiddleware

# Use centralized config for CORS
allowed_origins = settings.cors_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Include API routes
from api_routes import router as api_router
from auth_routes import router as auth_router
from document_routes import router as document_router
app.include_router(api_router)
app.include_router(auth_router)
app.include_router(document_router)

# Inngest integration
inngest.fast_api.serve(app, inngest_client, [rag_ingest_pdf, rag_query_pdf_ai])