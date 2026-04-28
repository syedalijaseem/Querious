"""Shared utility functions for history management and token estimation.

Extracted from main.py to allow test imports without triggering
heavy dependencies (inngest, data_loader, etc.).
"""


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
        recent = recent[2:]  # Drop oldest pair
        token_count = estimate_tokens(recent)
    
    return recent
