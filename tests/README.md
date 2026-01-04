# Tests

Comprehensive test suite for the Querious application.

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures (mock db, sample data, tokens)
├── unit/
│   ├── test_auth.py         # Password hashing, token creation/verification
│   └── test_models.py       # Pydantic model validation
├── integration/
│   └── test_api.py          # API endpoint behavior with mocked DB
└── security/
    └── test_security.py     # Authentication, authorization, injection, rate limiting
```

## Test Coverage

### Security Tests (Priority)

- JWT signature validation
- Token expiration handling
- Password hashing verification
- Authorization/access control
- NoSQL injection prevention
- XSS input handling
- Rate limiting functionality
- Data privacy and isolation

### Unit Tests

- Password hashing and verification
- Token creation with expiry
- Email validation
- Model field validation
- Plan limit definitions

### Integration Tests

- Project CRUD operations
- Chat CRUD operations
- Document upload validation
- Query authorization
- Waitlist functionality

## Running Tests

```bash
# Install test dependencies
uv add pytest pytest-asyncio --dev

# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/security/test_security.py

# Run with coverage
uv run pytest --cov=. --cov-report=html
```

## Test Database

Tests use mocked database connections to avoid affecting development data.
No external database connection required for unit tests.

## Writing New Tests

1. Add fixtures to `conftest.py` for reusable test data
2. Security-critical tests go in `tests/security/`
3. Pure function tests go in `tests/unit/`
4. Endpoint behavior tests go in `tests/integration/`
