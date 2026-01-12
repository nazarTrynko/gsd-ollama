# Backend Integration Tests

Integration tests for the GSD Ollama backend API.

## Setup

Install test dependencies:

```bash
cd backend
pip install -e ".[dev]"
# OR
pip install pytest pytest-asyncio pytest-mock httpx
```

## Running Tests

From the project root:

```bash
# Run all tests
pytest tests/backend/

# Run specific test file
pytest tests/backend/test_api_projects.py

# Run with verbose output
pytest tests/backend/ -v

# Run with coverage
pytest tests/backend/ --cov=app --cov-report=html
```

## Test Structure

- `conftest.py` - Shared fixtures and test configuration
- `test_api_health.py` - Health check and root endpoint tests
- `test_api_projects.py` - Project management API tests
- `test_api_ollama.py` - Ollama integration API tests
- `test_api_roadmap.py` - Roadmap generation API tests
- `test_api_phases.py` - Phase planning and execution API tests
- `test_workflow_integration.py` - End-to-end workflow tests

## Test Coverage

The tests cover:
- ✅ API health endpoints
- ✅ Project CRUD operations
- ✅ Ollama connection and model management
- ✅ Roadmap generation
- ✅ Phase planning
- ✅ Task execution
- ✅ Complete workflow integration

## Notes

- Tests use mocks for Ollama client to avoid requiring a running Ollama server
- Tests use temporary directories for project storage
- All tests are isolated and can run in parallel
