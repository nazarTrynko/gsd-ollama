# E2E Tests

End-to-end tests for the GSD Ollama project covering backend API workflows, frontend UI interactions, and full-stack integration.

## Test Structure

### Backend E2E Tests
- **Location**: `tests/backend/test_e2e_api.py`
- **Framework**: pytest
- **Coverage**:
  - Complete workflow (create → roadmap → plan → execute)
  - Error handling scenarios
  - Edge cases (special characters, multiple projects)
  - Progress tracking verification
  - File persistence verification
  - Path validation

### Frontend E2E Tests
- **Location**: `frontend/tests/e2e/`
- **Framework**: Playwright
- **Coverage**:
  - Project creation flow
  - Project listing and navigation
  - Roadmap generation UI
  - Phase planning UI
  - Task execution UI
  - Error state handling
  - Loading states
  - Form validation

### Full Stack E2E Tests
- **Location**: `frontend/tests/e2e/full-workflow.spec.ts`
- **Framework**: Playwright
- **Coverage**:
  - Complete user journey
  - API-frontend integration
  - Error propagation
  - State synchronization

## Running Tests

### Backend E2E Tests

```bash
# From project root
cd backend
source venv/bin/activate
pytest tests/backend/test_e2e_api.py -v -m "e2e or api_e2e"

# Run specific test
pytest tests/backend/test_e2e_api.py::test_complete_workflow_e2e -v
```

### Frontend E2E Tests

```bash
# From frontend directory
cd frontend
npm run test:e2e

# Run with UI mode
npm run test:e2e:ui

# Run in headed mode (see browser)
npm run test:e2e:headed

# Run specific test file
npx playwright test project-workflow.spec.ts
```

### Full Stack E2E Tests

```bash
# Requires both servers running
# Terminal 1: Start backend
cd backend
source venv/bin/activate
uvicorn app.main:app --port 8000

# Terminal 2: Start frontend
cd frontend
npm run dev

# Terminal 3: Run tests
cd frontend
npm run test:e2e -- tests/e2e/full-workflow.spec.ts
```

## Test Markers

Backend tests use pytest markers:
- `@pytest.mark.e2e` - All e2e tests
- `@pytest.mark.api_e2e` - API e2e tests

Run tests by marker:
```bash
pytest -m e2e
pytest -m api_e2e
```

## Page Object Models

Frontend tests use page object models for maintainability:
- `ProjectListPage` - Project list page interactions
- `NewProjectPage` - New project form
- `ProjectViewPage` - Project detail view
- `RoadmapPage` - Roadmap and phase interactions

## CI/CD Integration

Tests run automatically on:
- Push to main/develop branches
- Pull requests
- Manual workflow dispatch

See `.github/workflows/e2e-tests.yml` for CI configuration.

## Test Data

Tests use:
- Temporary directories for project storage
- Mocked Ollama client (no real Ollama server required)
- Isolated test environments
- Automatic cleanup

## Debugging

### Backend Tests
```bash
# Run with verbose output
pytest tests/backend/test_e2e_api.py -v -s

# Run with debugger
pytest tests/backend/test_e2e_api.py --pdb
```

### Frontend Tests
```bash
# Run with UI mode (interactive)
npm run test:e2e:ui

# Run in headed mode
npm run test:e2e:headed

# Debug specific test
npx playwright test project-workflow.spec.ts --debug
```

## Notes

- Backend e2e tests use mocked Ollama client
- Frontend e2e tests mock API responses
- Full stack tests require both servers running
- All tests are isolated and can run in parallel
- Test results are saved as artifacts in CI
