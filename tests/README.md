# Tests

This directory will contain tests for the Querious application.

## Planned Test Structure

```
tests/
├── conftest.py           # Shared fixtures (db, auth, etc.)
├── test_auth.py          # Registration, login, logout, refresh
├── test_api_projects.py  # Project CRUD
├── test_api_chats.py     # Chat CRUD
├── test_api_documents.py # Document upload, list, delete
├── test_api_query.py     # Query endpoint + RAG pipeline
├── test_waitlist.py      # Waitlist signup
└── test_limits.py        # Plan-based limits enforcement
```

## Running Tests

```bash
# Install test dependencies
uv add pytest pytest-asyncio httpx --dev

# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=. --cov-report=html
```

## Test Database

Tests should use a separate MongoDB database to avoid affecting development data.
Set `MONGODB_DATABASE=docurag_test` in your test environment.
