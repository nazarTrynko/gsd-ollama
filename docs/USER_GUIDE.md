# GSD Ollama User Guide

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 18+
- Ollama server running
- At least one model pulled (e.g., `ollama pull llama3.2`)

### Installation

1. **Backend Setup**:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
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

5. **Open Browser**: Navigate to `http://localhost:5173`

## Usage

### Creating a Project

1. Click "New Project" in the sidebar
2. Enter project name and description
3. Optionally add an initial task
4. Click "Create Project"

### Generating a Roadmap

1. Open your project
2. Click "Create Roadmap"
3. Wait for roadmap generation
4. Review the generated roadmap with phases

### Planning a Phase

1. Find a phase in the roadmap
2. Click "Plan" button
3. Review the generated task plan
4. Tasks are displayed with details

### Executing Tasks

1. After planning a phase, click "Execute"
2. Tasks will be executed using Ollama
3. Progress is tracked and displayed
4. Results are saved to SUMMARY.md

## Features

- **Project Management**: Create and manage multiple projects
- **Roadmap Generation**: Automatically generate project roadmaps
- **Task Planning**: Create detailed task plans for each phase
- **Task Execution**: Execute tasks automatically using Ollama
- **Codebase Mapping**: Analyze existing codebases
