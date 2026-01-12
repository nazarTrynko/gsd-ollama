# GSD Ollama Architecture

## Overview

GSD Ollama is a full-stack application with a FastAPI backend and React frontend.

## Backend Architecture

### Core Components

- **OllamaClient**: Wraps Ollama API calls
- **ProjectManager**: Manages project state and `.planning/` files
- **RoadmapEngine**: Generates roadmaps from project descriptions
- **PhasePlanner**: Creates XML-formatted task plans
- **TaskExecutor**: Executes tasks using Ollama
- **CodebaseMapper**: Analyzes existing codebases

### API Structure

- FastAPI application with REST endpoints
- Pydantic models for request/response validation
- File-based storage in `.planning/` directory

## Frontend Architecture

### Components

- **Project**: Project creation and management
- **Roadmap**: Roadmap visualization and phase management
- **Tasks**: Task planning and execution
- **Ollama**: Connection status and model selection

### State Management

- Zustand for global state
- React hooks for component state
- API service layer for backend communication

## Data Flow

1. User creates project → Backend generates PROJECT.md
2. User creates roadmap → Backend generates ROADMAP.md
3. User plans phase → Backend generates XML task plan
4. User executes phase → Backend executes tasks via Ollama
5. Results saved to SUMMARY.md
