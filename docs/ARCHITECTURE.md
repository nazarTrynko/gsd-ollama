# GSD Ollama Architecture

## Overview

GSD Ollama is a full-stack application with a FastAPI backend and React frontend, designed to provide a spec-driven development workflow using local LLM capabilities via Ollama.

## System Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Frontend  │ ◄──────► │    Backend   │ ◄──────► │   Ollama    │
│   (React)   │   HTTP   │   (FastAPI)  │   HTTP   │   Server    │
└─────────────┘          └──────────────┘          └─────────────┘
                              │
                              ▼
                        ┌─────────────┐
                        │   File      │
                        │   System    │
                        │ (Projects)  │
                        └─────────────┘
```

## Backend Architecture

### Core Components

#### OllamaClient
- **Purpose**: Wraps Ollama API calls
- **Location**: `backend/app/core/ollama_client.py`
- **Responsibilities**:
  - Connection management
  - Model selection and configuration
  - Request/response handling
  - Error handling and retries
  - Timeout management

**Key Methods:**
- `check_server()` - Verify Ollama server connectivity
- `list_models()` - Get available models
- `generate()` - Generate text using Ollama

#### ProjectManager
- **Purpose**: Manages project state and files
- **Location**: `backend/app/core/project_manager.py`
- **Responsibilities**:
  - Project directory management
  - File operations (PROJECT.md, ROADMAP.md, etc.)
  - Project state tracking
  - Project information retrieval

**Key Methods:**
- `get_project_info()` - Get project metadata
- `get_roadmap()` - Retrieve roadmap content
- `get_plan()` - Get task plan
- `get_state()` - Get current state
- `get_summary()` - Get execution summary

#### RoadmapEngine
- **Purpose**: Generates roadmaps from project descriptions
- **Location**: `backend/app/core/roadmap_engine.py`
- **Responsibilities**:
  - Analyzing project requirements
  - Generating structured roadmaps
  - Phase identification
  - Milestone planning

**Key Methods:**
- `generate_roadmap()` - Create roadmap from project

#### PhasePlanner
- **Purpose**: Creates XML-formatted task plans
- **Location**: `backend/app/core/phase_planner.py`
- **Responsibilities**:
  - Task decomposition
  - Dependency identification
  - XML format generation
  - Task prioritization

**Key Methods:**
- `plan_phase()` - Generate task plan for a phase

#### TaskExecutor
- **Purpose**: Executes tasks using Ollama
- **Location**: `backend/app/core/task_executor.py`
- **Responsibilities**:
  - Task execution orchestration
  - Progress tracking
  - Result accumulation
  - Error handling

**Key Methods:**
- `execute_phase()` - Execute all tasks in a phase
- `execute_task()` - Execute a single task

#### CodebaseMapper
- **Purpose**: Analyzes existing codebases
- **Location**: `backend/app/core/codebase_mapper.py`
- **Responsibilities**:
  - Codebase structure analysis
  - Documentation generation
  - Architecture mapping
  - Component identification

**Key Methods:**
- `map_codebase()` - Analyze and map codebase

#### FileManager
- **Purpose**: Handles file operations
- **Location**: `backend/app/core/file_manager.py`
- **Responsibilities**:
  - Reading/writing project files
  - File validation
  - Path management

### API Structure

#### FastAPI Application
- **Location**: `backend/app/main.py`
- **Features**:
  - RESTful API endpoints
  - CORS middleware
  - Automatic API documentation (Swagger/ReDoc)
  - Request/response validation

#### API Routers

**Projects Router** (`backend/app/api/projects.py`)
- `POST /api/projects/new` - Create project
- `GET /api/projects` - List projects
- `GET /api/projects/{id}` - Get project
- `DELETE /api/projects/{id}` - Delete project

**Roadmap Router** (`backend/app/api/roadmap.py`)
- `POST /api/projects/{id}/roadmap` - Generate roadmap
- `GET /api/projects/{id}/roadmap` - Get roadmap

**Phases Router** (`backend/app/api/phases.py`)
- `POST /api/projects/{id}/phases/{n}/plan` - Plan phase
- `POST /api/projects/{id}/phases/{n}/execute` - Execute phase
- `GET /api/projects/{id}/phases/{n}/progress` - Get progress

**Tasks Router** (`backend/app/api/tasks.py`)
- `GET /api/projects/{id}/progress` - Get project progress

**Ollama Router** (`backend/app/api/ollama.py`)
- `GET /api/ollama/status` - Get Ollama status
- `GET /api/ollama/models` - List models

**Codebase Router** (`backend/app/api/codebase.py`)
- `POST /api/projects/{id}/codebase/map` - Map codebase
- `GET /api/projects/{id}/codebase` - Get codebase docs

### Data Models

**Pydantic Models** (`backend/app/models/`)
- `ProjectCreate` - Project creation request
- `ProjectInfo` - Project information response
- `RoadmapCreate` - Roadmap generation request
- `RoadmapInfo` - Roadmap information
- `TaskPlan` - Task plan structure
- `TaskExecute` - Task execution request
- `TaskProgress` - Progress tracking

### File-Based Storage

Projects are stored in the file system:

```
projects/
└── ProjectName/
    ├── PROJECT.md      # Project description
    ├── ROADMAP.md      # Generated roadmap
    ├── PLAN.md         # Task plan (XML)
    ├── STATE.md        # Current state
    └── SUMMARY.md      # Execution results
```

### Configuration

**Ollama Configuration** (`backend/config/ollama-config.json`)
- Server URL
- Default model
- Model-specific parameters
- Retry configuration
- Timeout settings

---

## Frontend Architecture

### Technology Stack

- **React 18+** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Styling
- **Zustand** - State management
- **React Router** - Navigation (if used)

### Component Structure

```
src/
├── components/
│   ├── Common/          # Shared components
│   │   ├── Layout.tsx
│   │   ├── Sidebar.tsx
│   │   └── StatusBar.tsx
│   ├── Project/        # Project management
│   │   ├── NewProject.tsx
│   │   ├── ProjectList.tsx
│   │   └── ProjectView.tsx
│   ├── Roadmap/        # Roadmap visualization
│   │   ├── RoadmapView.tsx
│   │   ├── PhaseCard.tsx
│   │   └── MilestoneView.tsx
│   ├── Tasks/          # Task management
│   │   ├── TaskPlan.tsx
│   │   ├── TaskExecutor.tsx
│   │   └── TaskProgress.tsx
│   ├── Ollama/         # Ollama integration
│   │   ├── ConnectionStatus.tsx
│   │   └── ModelSelector.tsx
│   └── Codebase/       # Codebase mapping
│       └── CodebaseMapper.tsx
├── hooks/              # Custom React hooks
│   ├── useProject.ts
│   ├── useRoadmap.ts
│   └── useOllama.ts
├── services/           # API services
│   ├── api.ts
│   └── ollama.ts
└── store/              # Zustand stores
    ├── projectStore.ts
    └── ollamaStore.ts
```

### State Management

**Zustand Stores:**
- `projectStore` - Project state and operations
- `ollamaStore` - Ollama connection and model state

**React Hooks:**
- `useProject` - Project operations
- `useRoadmap` - Roadmap operations
- `useOllama` - Ollama connection management

### API Service Layer

**API Service** (`src/services/api.ts`)
- Centralized HTTP client
- Request/response handling
- Error handling
- Type-safe API calls

---

## Data Flow

### Project Creation Flow

```
User Input → Frontend → API Request → Backend
                                      │
                                      ├─→ OllamaClient → Ollama Server
                                      │
                                      └─→ ProjectManager → File System
                                      │
                                      └─→ Response → Frontend → UI Update
```

### Roadmap Generation Flow

```
User Action → Frontend → API Request → Backend
                                      │
                                      ├─→ ProjectManager (read PROJECT.md)
                                      │
                                      ├─→ RoadmapEngine → OllamaClient
                                      │
                                      └─→ ProjectManager (write ROADMAP.md)
                                      │
                                      └─→ Response → Frontend → Display
```

### Task Execution Flow

```
User Action → Frontend → API Request → Backend
                                      │
                                      ├─→ ProjectManager (read PLAN.md)
                                      │
                                      ├─→ TaskExecutor → OllamaClient
                                      │                    │
                                      │                    └─→ Ollama Server
                                      │
                                      ├─→ Progress Tracking
                                      │
                                      └─→ ProjectManager (write SUMMARY.md)
                                      │
                                      └─→ Response → Frontend → Progress Update
```

---

## Error Handling

### Backend Error Handling

**Exception Hierarchy:**
- `OllamaError` - Base Ollama exception
  - `OllamaConnectionError` - Connection issues
  - `OllamaServerError` - Server errors
  - `OllamaModelError` - Model-related errors
  - `OllamaTimeoutError` - Timeout errors
  - `OllamaConfigError` - Configuration errors

**HTTP Status Mapping:**
- `400` - Bad Request (validation errors)
- `404` - Not Found (resource missing)
- `500` - Internal Server Error
- `502` - Bad Gateway (Ollama server error)
- `503` - Service Unavailable (Ollama connection error)

### Frontend Error Handling

- API errors are caught and displayed to users
- Connection errors show retry options
- Validation errors highlight form fields
- Progress errors allow task retry

---

## Security Considerations

### Current State

- **No Authentication**: Designed for local use
- **CORS**: Allows all origins (development)
- **Path Validation**: Basic validation in place

### Production Recommendations

- Add authentication (JWT, OAuth, etc.)
- Restrict CORS to specific origins
- Add path traversal protection
- Implement rate limiting
- Add input validation and sanitization
- Use HTTPS in production

---

## Performance Considerations

### Current Implementation

- **Synchronous HTTP**: OllamaClient uses `requests` (blocking)
- **No Caching**: Repeated calls to Ollama
- **File-based Storage**: Direct file I/O

### Optimization Opportunities

- **Async HTTP**: Use `httpx` for async operations
- **Caching**: Cache model lists, project info
- **Background Tasks**: Use FastAPI background tasks
- **Streaming**: Stream Ollama responses
- **Connection Pooling**: Reuse HTTP connections

---

## Testing

### Backend Tests

- **Location**: `tests/backend/`
- **Framework**: pytest
- **Coverage**: API endpoints, core components
- **Mocks**: Ollama client mocked for testing

### Test Structure

```
tests/backend/
├── conftest.py              # Shared fixtures
├── test_api_health.py       # Health endpoints
├── test_api_projects.py     # Project endpoints
├── test_api_ollama.py       # Ollama endpoints
├── test_api_roadmap.py      # Roadmap endpoints
├── test_api_phases.py       # Phase endpoints
└── test_workflow_integration.py  # E2E tests
```

---

## Deployment

### Development

- Backend: `uvicorn app.main:app --reload`
- Frontend: `npm run dev`
- Ollama: `ollama serve`

### Production Considerations

- Use production ASGI server (Gunicorn + Uvicorn workers)
- Build frontend: `npm run build`
- Serve frontend with nginx or CDN
- Set up environment variables
- Configure CORS for production
- Add monitoring and logging
- Use process manager (systemd, PM2, etc.)

---

## Future Enhancements

### Planned Features

- **Database Integration**: Replace file-based storage
- **User Authentication**: Multi-user support
- **Real-time Updates**: WebSocket support
- **Task Scheduling**: Background task execution
- **Plugin System**: Extensible architecture
- **Export/Import**: Project backup and restore

### Architecture Improvements

- **Microservices**: Split into smaller services
- **Message Queue**: Async task processing
- **Caching Layer**: Redis for caching
- **Monitoring**: APM and logging
- **CI/CD**: Automated testing and deployment

---

## Dependencies

### Backend

- FastAPI - Web framework
- Pydantic - Data validation
- Requests - HTTP client (Ollama)
- Jinja2 - Template engine
- Uvicorn - ASGI server

### Frontend

- React - UI framework
- TypeScript - Type safety
- Vite - Build tool
- Tailwind CSS - Styling
- Zustand - State management

---

## Configuration Files

### Backend

- `pyproject.toml` - Python project configuration
- `requirements.txt` - Python dependencies
- `config/ollama-config.json` - Ollama configuration
- `config/default-config.json` - Default settings

### Frontend

- `package.json` - Node.js dependencies
- `vite.config.ts` - Vite configuration
- `tailwind.config.js` - Tailwind configuration
- `tsconfig.json` - TypeScript configuration

---

## Development Workflow

1. **Start Ollama**: `ollama serve`
2. **Start Backend**: `uvicorn app.main:app --reload`
3. **Start Frontend**: `npm run dev`
4. **Access UI**: http://localhost:5173
5. **API Docs**: http://localhost:8000/docs

---

## Contributing

See project README for contribution guidelines. Key areas:

- Follow existing code patterns
- Add tests for new features
- Update documentation
- Follow type hints and linting rules
- Write clear commit messages

---

For more information:
- [API Documentation](API.md)
- [User Guide](USER_GUIDE.md)
- [Code Review](CODE_REVIEW.md)
