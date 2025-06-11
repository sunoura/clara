# Tests

This directory contains comprehensive test suites for the personal assistant agent's database models and API routes.

## Test Structure

```
tests/
├── conftest.py                    # Pytest configuration and fixtures
├── test_memory_collection.py     # Tests for memory collections
├── test_memory_document.py       # Tests for memory documents
├── test_interaction_session.py   # Tests for chat sessions
├── test_interaction_payload.py   # Tests for chat messages
└── README.md                     # This file
```

## Test Coverage

### Memory Collection Tests (`test_memory_collection.py`)
- **Operations (Ops) Tests**: Database operations via `MemoryCollectionOps`
  - Create, read, update, archive collections
  - Get collections with documents
  - Pagination and filtering
- **API Route Tests**: HTTP endpoints via FastAPI
  - All CRUD operations
  - Error handling (404s)
  - Request/response validation

### Memory Document Tests (`test_memory_document.py`)
- **Operations Tests**: Database operations via `MemoryDocumentOps`
  - Document creation with metadata
  - ChromaDB ID lookups
  - Content search functionality
  - Collection-based filtering
- **API Route Tests**: RESTful endpoints
  - Metadata JSON handling
  - Search functionality
  - Collection relationships

### Interaction Session Tests (`test_interaction_session.py`)
- **Operations Tests**: Chat session management
  - UUID generation for sessions
  - Recent session retrieval
  - Session updates
- **API Route Tests**: Session endpoints
  - Session creation with optional fields
  - Chronological ordering
  - Payload relationships

### Interaction Payload Tests (`test_interaction_payload.py`)
- **Operations Tests**: Message handling
  - User/model message distinction
  - Failed payload tracking
  - Session-based message retrieval
- **API Route Tests**: Message endpoints
  - Complete conversation flows
  - Enum validation (user/model)
  - Error state handling

## Fixtures

The `conftest.py` provides shared fixtures:

- `session`: In-memory SQLite database session
- `client`: FastAPI test client with database override
- `sample_memory_collection`: Pre-created test collection
- `sample_memory_document`: Pre-created test document
- `sample_interaction_session`: Pre-created test session
- `sample_interaction_payload`: Pre-created test message

## Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_memory_collection.py

# Run with verbose output
pytest -v

# Run specific test class
pytest tests/test_memory_collection.py::TestMemoryCollectionOps

# Run specific test method
pytest tests/test_memory_collection.py::TestMemoryCollectionOps::test_create_collection
```

## Test Categories

Each test file contains two main test classes:

1. **`Test<Model>Ops`**: Tests the database operations layer
   - Direct testing of ops classes
   - Database state verification
   - Business logic validation

2. **`Test<Model>Routes`**: Tests the API endpoints
   - HTTP request/response testing
   - Status code validation
   - JSON serialization/deserialization
   - End-to-end API workflows

## Key Test Features

- **In-Memory Database**: Tests use SQLite in-memory database for speed
- **Isolation**: Each test gets a fresh database state
- **Comprehensive Coverage**: Tests cover both happy path and error scenarios
- **Real API Testing**: Uses FastAPI's TestClient for authentic HTTP testing
- **Relationship Testing**: Verifies foreign keys and model relationships work correctly
- **Metadata Handling**: Tests JSON metadata storage and retrieval
- **Enum Validation**: Ensures type safety for user/model message types
- **Pagination**: Tests query parameter handling for large datasets

All tests pass and provide confidence in the system's reliability for your personal assistant agent! 🎉 