# GSD Ollama - Get Shit Done with Ollama

A standalone project that replicates the get-shit-done workflow system using Ollama (local LLM) instead of Claude, with a modern React web UI.

## Overview

GSD Ollama is a spec-driven development system that helps you build projects using local LLMs. It provides:

- **Project Management**: Create and manage projects with structured planning
- **Roadmap Generation**: Automatically generate project roadmaps with phases
- **Task Planning**: Create XML-formatted task plans for each phase
- **Task Execution**: Execute tasks using Ollama subagents
- **Codebase Mapping**: Analyze existing codebases for brownfield projects
- **Web UI**: Modern React interface for managing projects

## Quick Start

### Prerequisites

- Python 3.8+
- Node.js 18+
- Ollama server running (default: http://localhost:11434)
- At least one model pulled (e.g., `ollama pull llama3.2`)

### Installation

**Option 1: Using root package.json (Recommended)**

```bash
# Install all dependencies
npm run setup

# Start both backend and frontend
npm run dev

# Or start individually
npm run dev:backend    # Backend only
npm run dev:frontend   # Frontend only
```

**Option 2: Manual Setup**

1. **Backend Setup**:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Frontend Setup**:
```bash
cd frontend
npm install
```

3. **Start Backend**:
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

4. **Start Frontend**:
```bash
cd frontend
npm run dev
```

5. **Open Browser**:
Navigate to `http://localhost:5173` (or the port shown by Vite)

## Project Structure

```
gsd-ollama/
├── backend/          # FastAPI backend
├── frontend/         # React SPA
├── specs/            # Product requirements
├── docs/             # Documentation
└── tests/            # Test files
```

## Features

- ✅ Project creation and management
- ✅ Roadmap generation with phases
- ✅ XML-formatted task planning
- ✅ Task execution with progress tracking
- ✅ Codebase mapping for existing projects
- ✅ Modern React web UI
- ✅ Real-time progress updates

## Testing

### Using Root Scripts (Recommended)

```bash
# Run all tests
npm test

# Run backend tests
npm run test:backend
npm run test:backend:e2e      # E2E tests only
npm run test:backend:unit     # Unit tests only

# Run frontend E2E tests
npm run test:frontend
npm run test:frontend:ui       # Interactive UI mode
npm run test:frontend:headed  # See browser

# Run all E2E tests
npm run test:e2e
```

### Manual Testing

**Backend Integration Tests**

Install test dependencies:

```bash
cd backend
pip install -e ".[dev]"
# OR
pip install pytest pytest-asyncio pytest-mock httpx
```

Run tests:

```bash
# From project root
pytest tests/backend/

# Run specific test file
pytest tests/backend/test_api_projects.py

# Run with verbose output
pytest tests/backend/ -v
```

See [tests/backend/README.md](tests/backend/README.md) for more details.

**Frontend E2E Tests**

```bash
cd frontend
npm run test:e2e
```

See [tests/e2e/README.md](tests/e2e/README.md) for more details.

## Documentation

- [API Documentation](docs/API.md)
- [Architecture Guide](docs/ARCHITECTURE.md)
- [User Guide](docs/USER_GUIDE.md)
- [Code Review Guide](docs/CODE_REVIEW.md)

## License

MIT License
