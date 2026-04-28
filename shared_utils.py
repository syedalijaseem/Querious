"""Shared utilities and constants.

Extracted from api_routes.py to allow testing without triggering
heavy dependencies (like inngest).
"""

# --- Plan Limits Configuration ---
PLAN_LIMITS = {
    "free": {"projects": 1, "chats": 3, "documents": 3, "docs_per_scope": 3, "token_limit": 10000},
    "pro": {"projects": 10, "chats": None, "documents": 30, "docs_per_scope": 5, "token_limit": 500000},  # None = unlimited
    "premium": {"projects": None, "chats": None, "documents": None, "docs_per_scope": 10, "token_limit": 2000000},
}

# --- PDF Validation ---
PDF_MAGIC_BYTES = [b'%PDF', b'\x25\x50\x44\x46']

def validate_pdf_content(content: bytes) -> bool:
    """Validate that file content starts with PDF magic bytes."""
    if len(content) < 4:
        return False
    header = content[:4]
    return any(header.startswith(magic) for magic in PDF_MAGIC_BYTES)
