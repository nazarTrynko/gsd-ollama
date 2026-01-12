# GSD Ollama API Documentation

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, no authentication is required. The API is designed for local use.

## Error Responses

All endpoints may return error responses in the following format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

Common HTTP status codes:
- `400` - Bad Request (invalid input)
- `404` - Not Found (resource doesn't exist)
- `500` - Internal Server Error
- `502` - Bad Gateway (Ollama server error)
- `503` - Service Unavailable (Ollama connection error)

---

## Endpoints

### Health & Status

#### GET /

Get API information.

**Response:**
```json
{
  "message": "GSD Ollama API",
  "version": "0.1.0",
  "docs": "/docs"
}
```

#### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy"
}
```

---

### Ollama

#### GET /api/ollama/status

Get Ollama server status and available models.

**Response:**
```json
{
  "connected": true,
  "server_url": "http://localhost:11434",
  "default_model": "llama3.2",
  "models": ["llama3.2", "mistral", "codellama"]
}
```

**Example:**
```bash
curl http://localhost:8000/api/ollama/status
```

**Error Responses:**
- `500` - Internal server error

---

#### GET /api/ollama/models

List available Ollama models.

**Response:**
```json
{
  "models": ["llama3.2", "mistral", "codellama"],
  "default": "llama3.2"
}
```

**Example:**
```bash
curl http://localhost:8000/api/ollama/models
```

**Error Responses:**
- `502` - Bad Gateway (Ollama server error)
- `503` - Service Unavailable (Ollama connection error)
- `500` - Internal server error

---

### Projects

#### POST /api/projects/new

Create a new project.

**Request Body:**
```json
{
  "name": "My Project",
  "description": "Project description",
  "initial_task": "Optional initial task",
  "project_path": "Optional custom path"
}
```

**Response:**
```json
{
  "id": "./projects/My_Project",
  "name": "My_Project",
  "path": "./projects/My_Project",
  "description": "Project description"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/projects/new \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Project",
    "description": "A new project",
    "initial_task": "Set up the project"
  }'
```

**Error Responses:**
- `500` - Internal server error (e.g., Ollama connection failed)

---

#### GET /api/projects

List all projects.

**Response:**
```json
{
  "projects": [
    {
      "id": "./projects/My_Project",
      "name": "My_Project",
      "path": "./projects/My_Project",
      "description": "Project description"
    }
  ],
  "total": 1
}
```

**Example:**
```bash
curl http://localhost:8000/api/projects
```

**Error Responses:**
- `500` - Internal server error

---

#### GET /api/projects/{project_id}

Get project details.

**Path Parameters:**
- `project_id` (string) - Project path or ID

**Response:**
```json
{
  "id": "./projects/My_Project",
  "name": "My_Project",
  "path": "./projects/My_Project",
  "description": "Project description"
}
```

**Example:**
```bash
curl http://localhost:8000/api/projects/./projects/My_Project
```

**Error Responses:**
- `404` - Project not found
- `500` - Internal server error

---

#### DELETE /api/projects/{project_id}

Delete a project.

**Path Parameters:**
- `project_id` (string) - Project path or ID

**Response:**
```json
{
  "success": true,
  "message": "Project deleted"
}
```

**Example:**
```bash
curl -X DELETE http://localhost:8000/api/projects/./projects/My_Project
```

**Error Responses:**
- `403` - Forbidden (can only delete projects from projects directory)
- `404` - Project not found
- `500` - Internal server error

---

### Roadmap

#### POST /api/projects/{project_id}/roadmap

Create roadmap for a project.

**Path Parameters:**
- `project_id` (string) - Project path or ID

**Request Body:**
```json
{}
```

**Response:**
```json
{
  "success": true,
  "roadmap": "# Roadmap\n\n## Phase 1: Setup\n...",
  "project_id": "./projects/My_Project"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/projects/./projects/My_Project/roadmap \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Error Responses:**
- `400` - Bad Request (invalid project state)
- `404` - Project not found
- `500` - Internal server error

---

#### GET /api/projects/{project_id}/roadmap

Get roadmap for a project.

**Path Parameters:**
- `project_id` (string) - Project path or ID

**Response:**
```json
{
  "roadmap": "# Roadmap\n\n## Phase 1: Setup\n...",
  "project_id": "./projects/My_Project"
}
```

**Example:**
```bash
curl http://localhost:8000/api/projects/./projects/My_Project/roadmap
```

**Error Responses:**
- `404` - Project not found or roadmap not found (create roadmap first)
- `500` - Internal server error

---

### Phases

#### POST /api/projects/{project_id}/phases/{phase_number}/plan

Plan tasks for a phase.

**Path Parameters:**
- `project_id` (string) - Project path or ID
- `phase_number` (integer) - Phase number (1-indexed)

**Response:**
```json
{
  "phase_number": 1,
  "tasks": [
    {
      "id": "1",
      "description": "Task description",
      "status": "pending"
    }
  ]
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/projects/./projects/My_Project/phases/1/plan
```

**Error Responses:**
- `400` - Bad Request (invalid phase number or project state)
- `404` - Project not found
- `500` - Internal server error

---

#### POST /api/projects/{project_id}/phases/{phase_number}/execute

Execute tasks for a phase.

**Path Parameters:**
- `project_id` (string) - Project path or ID
- `phase_number` (integer) - Phase number (1-indexed)

**Request Body:**
```json
{
  "task_id": "Optional specific task ID to execute"
}
```

**Response:**
```json
{
  "success": true,
  "results": [
    {
      "task_id": "1",
      "status": "completed",
      "output": "Task execution output"
    }
  ],
  "project_id": "./projects/My_Project",
  "phase_number": 1
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/projects/./projects/My_Project/phases/1/execute \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Error Responses:**
- `404` - Project not found or plan not found (plan phase first)
- `500` - Internal server error

---

#### GET /api/projects/{project_id}/phases/{phase_number}/progress

Get execution progress for a phase.

**Path Parameters:**
- `project_id` (string) - Project path or ID
- `phase_number` (integer) - Phase number (1-indexed)

**Response:**
```json
{
  "project_id": "./projects/My_Project",
  "phase_number": 1,
  "completed_tasks": 2,
  "total_tasks": 5,
  "status": "running",
  "logs": [
    "Task 1 completed",
    "Task 2 completed"
  ]
}
```

**Status Values:**
- `idle` - No execution in progress
- `running` - Execution in progress
- `complete` - Execution completed

**Example:**
```bash
curl http://localhost:8000/api/projects/./projects/My_Project/phases/1/progress
```

**Error Responses:**
- `500` - Internal server error

---

### Tasks

#### GET /api/projects/{project_id}/progress

Get overall project progress.

**Path Parameters:**
- `project_id` (string) - Project path or ID

**Response:**
```json
{
  "project_id": "./projects/My_Project",
  "project_info": {
    "name": "My_Project",
    "path": "./projects/My_Project",
    "description": "Project description"
  },
  "has_roadmap": true,
  "has_state": true,
  "has_summary": true,
  "summary_length": 1234
}
```

**Example:**
```bash
curl http://localhost:8000/api/projects/./projects/My_Project/progress
```

**Error Responses:**
- `404` - Project not found
- `500` - Internal server error

---

### Codebase

#### POST /api/projects/{project_id}/codebase/map

Map and analyze an existing codebase.

**Path Parameters:**
- `project_id` (string) - Project path or ID

**Request Body:**
```json
{
  "codebase_path": "/path/to/codebase"
}
```

**Response:**
```json
{
  "success": true,
  "mapping": "Codebase mapping documentation",
  "project_id": "./projects/My_Project"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/projects/./projects/My_Project/codebase/map \
  -H "Content-Type: application/json" \
  -d '{
    "codebase_path": "/path/to/codebase"
  }'
```

**Error Responses:**
- `400` - Bad Request (invalid codebase path)
- `404` - Project not found
- `500` - Internal server error

---

#### GET /api/projects/{project_id}/codebase

Get codebase documentation.

**Path Parameters:**
- `project_id` (string) - Project path or ID

**Response:**
```json
{
  "codebase": "Codebase documentation content",
  "project_id": "./projects/My_Project"
}
```

**Example:**
```bash
curl http://localhost:8000/api/projects/./projects/My_Project/codebase
```

**Error Responses:**
- `404` - Project not found or codebase not mapped
- `500` - Internal server error

---

## Interactive API Documentation

FastAPI provides interactive API documentation at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These interfaces allow you to:
- Browse all available endpoints
- Test endpoints directly from the browser
- View request/response schemas
- See example requests and responses

---

## Rate Limiting

Currently, no rate limiting is implemented. However, Ollama API calls may be rate-limited by the Ollama server itself.

## Notes

- All project paths are relative to the backend working directory
- Project IDs are typically the project path string
- Ollama server must be running for most operations
- File operations are synchronous and may take time for large projects
