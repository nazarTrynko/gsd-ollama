# GSD Ollama User Guide

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 18+
- Ollama server running (default: http://localhost:11434)
- At least one model pulled (e.g., `ollama pull llama3.2`)

### Installation

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

5. **Open Browser**: Navigate to `http://localhost:5173` (or the port shown by Vite)

### Verify Installation

1. Check backend is running: Visit http://localhost:8000/health
2. Check Ollama connection: Visit http://localhost:8000/api/ollama/status
3. Verify frontend loads: Open http://localhost:5173

---

## Usage

### Creating a Project

1. Click "New Project" in the sidebar
2. Enter project name and description
3. Optionally add an initial task to guide project generation
4. Click "Create Project"

**Example:**
- **Name**: "Todo App"
- **Description**: "A simple todo application with React frontend and Node.js backend"
- **Initial Task**: "Set up project structure with frontend and backend folders"

The system will:
- Generate a `PROJECT.md` file using Ollama
- Create a project directory
- Save the project for future use

**Tips:**
- Be specific in your description for better roadmap generation
- Include technology stack in the description
- Initial tasks help guide the project structure

---

### Generating a Roadmap

1. Open your project from the project list
2. Click "Create Roadmap" or "Generate Roadmap" button
3. Wait for roadmap generation (this uses Ollama and may take a minute)
4. Review the generated roadmap with phases

**What happens:**
- The system analyzes your PROJECT.md
- Generates a structured roadmap with multiple phases
- Each phase contains milestones and goals
- Roadmap is saved as `ROADMAP.md` in your project directory

**Example Roadmap Structure:**
```
# Roadmap

## Phase 1: Setup
- Initialize project structure
- Set up development environment
- Configure build tools

## Phase 2: Core Features
- Implement authentication
- Create API endpoints
- Build UI components

## Phase 3: Testing & Polish
- Write tests
- Add error handling
- Improve UI/UX
```

---

### Planning a Phase

1. Find a phase in the roadmap (e.g., "Phase 1: Setup")
2. Click "Plan" button next to the phase
3. Review the generated task plan
4. Tasks are displayed with details and IDs

**What happens:**
- System generates an XML-formatted task plan
- Each task has an ID, description, and dependencies
- Plan is saved as `PLAN.md` in your project directory
- Tasks are ready for execution

**Example Task Plan:**
```xml
<tasks>
  <task id="1">
    <description>Initialize project structure</description>
    <dependencies></dependencies>
  </task>
  <task id="2">
    <description>Set up development environment</description>
    <dependencies>1</dependencies>
  </task>
</tasks>
```

**Tips:**
- Review tasks before executing
- Tasks are executed in order based on dependencies
- You can modify the plan manually if needed

---

### Executing Tasks

1. After planning a phase, click "Execute" button
2. Tasks will be executed using Ollama
3. Progress is tracked and displayed in real-time
4. Results are saved to `SUMMARY.md`

**What happens:**
- Each task is sent to Ollama for execution
- Ollama generates code, documentation, or other outputs
- Progress is tracked (completed tasks / total tasks)
- Results are accumulated and saved

**Progress Tracking:**
- Status: `idle`, `running`, or `complete`
- Completed tasks count
- Total tasks count
- Execution logs

**Tips:**
- Execution may take time depending on task complexity
- Monitor progress in the UI
- Review SUMMARY.md after execution
- You can execute specific tasks by providing task_id

---

### Codebase Mapping

For existing projects, you can map and analyze the codebase:

1. Open your project
2. Navigate to "Codebase" section
3. Enter the path to your existing codebase
4. Click "Map Codebase"
5. Review the generated codebase documentation

**What happens:**
- System analyzes the codebase structure
- Generates documentation about files and components
- Creates a mapping of the codebase architecture
- Saves documentation for reference

**Use Cases:**
- Understanding existing codebases
- Planning refactoring
- Documenting legacy systems
- Onboarding new developers

---

## Project Structure

Each project creates a directory structure:

```
projects/
└── My_Project/
    ├── PROJECT.md      # Project description and goals
    ├── ROADMAP.md      # Generated roadmap with phases
    ├── PLAN.md         # Task plan (XML format)
    ├── STATE.md        # Current project state
    └── SUMMARY.md      # Execution results and summaries
```

---

## Features

### Project Management
- Create and manage multiple projects
- List all projects
- View project details
- Delete projects

### Roadmap Generation
- Automatically generate project roadmaps
- Structured phases with milestones
- AI-powered planning using Ollama

### Task Planning
- Create detailed task plans for each phase
- XML-formatted task definitions
- Dependency management
- Task prioritization

### Task Execution
- Execute tasks automatically using Ollama
- Real-time progress tracking
- Result accumulation
- Error handling

### Codebase Mapping
- Analyze existing codebases
- Generate codebase documentation
- Understand project structure
- Plan refactoring

---

## Troubleshooting

### Ollama Connection Issues

**Problem**: "Ollama server not connected"

**Solutions:**
1. Ensure Ollama is running: `ollama serve`
2. Check Ollama URL in settings (default: http://localhost:11434)
3. Verify at least one model is pulled: `ollama list`
4. Check backend logs for connection errors

### Project Creation Fails

**Problem**: "Failed to create project"

**Solutions:**
1. Check Ollama is running and connected
2. Verify you have write permissions in the projects directory
3. Check backend logs for detailed error messages
4. Ensure project name doesn't contain invalid characters

### Roadmap Generation Takes Too Long

**Problem**: Roadmap generation is slow

**Solutions:**
1. This is normal - Ollama generation can take 30-60 seconds
2. Use a faster model if available (e.g., `llama3.2:1b`)
3. Check Ollama server resources (CPU/RAM)
4. Consider breaking large projects into smaller ones

### Tasks Not Executing

**Problem**: Task execution fails or hangs

**Solutions:**
1. Ensure phase is planned before execution
2. Check PLAN.md exists and is valid XML
3. Verify Ollama is running and responsive
4. Review backend logs for execution errors
5. Try executing a single task first

---

## Best Practices

### Project Creation
- Use descriptive project names
- Include detailed descriptions
- Specify technology stack
- Add initial tasks for guidance

### Roadmap Planning
- Review generated roadmaps before proceeding
- Adjust phases if needed
- Break large phases into smaller ones
- Consider dependencies between phases

### Task Execution
- Plan phases before executing
- Review task plans
- Execute phases sequentially
- Monitor progress
- Review summaries after execution

### Code Organization
- Keep project descriptions up to date
- Review and update roadmaps as needed
- Document decisions in STATE.md
- Keep SUMMARY.md for reference

---

## Advanced Usage

### Custom Project Paths

You can specify custom project paths when creating projects:

```json
{
  "name": "My Project",
  "description": "...",
  "project_path": "/custom/path/to/project"
}
```

### Executing Specific Tasks

You can execute a specific task instead of all tasks:

```json
{
  "task_id": "1"
}
```

### API Integration

The frontend uses the REST API. You can also use the API directly:

```bash
# Create project
curl -X POST http://localhost:8000/api/projects/new \
  -H "Content-Type: application/json" \
  -d '{"name": "My Project", "description": "..."}'

# Generate roadmap
curl -X POST http://localhost:8000/api/projects/./projects/My_Project/roadmap \
  -H "Content-Type: application/json" \
  -d '{}'
```

See [API Documentation](API.md) for complete API reference.

---

## Next Steps

1. **Explore the UI**: Familiarize yourself with the interface
2. **Create a Test Project**: Try creating a simple project
3. **Generate a Roadmap**: See how roadmaps are generated
4. **Plan and Execute**: Try planning and executing a phase
5. **Review Documentation**: Check generated files in project directory

For more information, see:
- [API Documentation](API.md)
- [Architecture Guide](ARCHITECTURE.md)
- [Code Review](CODE_REVIEW.md)
