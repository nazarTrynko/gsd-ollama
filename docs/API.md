# GSD Ollama API Documentation

## Base URL

```
http://localhost:8000
```

## Endpoints

### Ollama

#### GET /api/ollama/status
Get Ollama server status and available models.

**Response:**
```json
{
  "connected": true,
  "server_url": "http://localhost:11434",
  "default_model": "llama3.2",
  "models": ["llama3.2", "mistral"]
}
```

#### GET /api/ollama/models
List available Ollama models.

### Projects

#### POST /api/projects/new
Create a new project.

**Request:**
```json
{
  "name": "My Project",
  "description": "Project description",
  "initial_task": "Optional initial task"
}
```

#### GET /api/projects
List all projects.

#### GET /api/projects/{id}
Get project details.

#### DELETE /api/projects/{id}
Delete a project.

### Roadmap

#### POST /api/projects/{id}/roadmap
Create roadmap for a project.

#### GET /api/projects/{id}/roadmap
Get roadmap for a project.

### Phases

#### POST /api/projects/{id}/phases/{n}/plan
Plan tasks for a phase.

#### POST /api/projects/{id}/phases/{n}/execute
Execute tasks for a phase.

#### GET /api/projects/{id}/phases/{n}/progress
Get execution progress.

### Codebase

#### POST /api/projects/{id}/codebase/map
Map and analyze an existing codebase.

#### GET /api/projects/{id}/codebase
Get codebase documentation.
