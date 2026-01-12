# GSD Ollama Setup Guide

## Quick Start Commands

### Always Activate Virtual Environment First!

**Important**: On macOS with Homebrew Python, you MUST use the virtual environment for all Python commands to avoid the "externally-managed-environment" error.

### Backend Setup (One-time)

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Always do this first!
pip install --upgrade pip
pip install -r requirements.txt
```

### Running the Backend

```bash
cd backend
source venv/bin/activate  # Activate venv first!
uvicorn app.main:app --reload --port 8000
```

### Running the Frontend

```bash
cd frontend
npm install  # Only needed once
npm run dev
```

## Common Issues & Solutions

### Error: "externally-managed-environment"

**Problem**: You tried to install packages without activating the virtual environment.

**Solution**: Always activate the venv first:

```bash
cd backend
source venv/bin/activate  # This is required!
pip install <package>
```

### How to Know if Venv is Active

When the venv is active, your terminal prompt will show `(venv)`:

```bash
(venv) nazartrynko@macbook backend %
```

### If You Forget to Activate Venv

If you get the error, just activate it and try again:

```bash
source venv/bin/activate
```

### Running Commands in Venv

**Correct way:**

```bash
cd backend
source venv/bin/activate
python some_script.py
pip install something
uvicorn app.main:app
```

**Wrong way (will cause error):**

```bash
cd backend
python some_script.py  # ❌ Not in venv!
pip install something  # ❌ Will fail with externally-managed-environment error!
```

## Starting Both Servers

### Terminal 1 - Backend:

```bash
cd /Users/nazartrynko/gsd-ollama/backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

### Terminal 2 - Frontend:

```bash
cd /Users/nazartrynko/gsd-ollama/frontend
npm run dev
```

## Verifying Setup

1. **Check backend**: http://localhost:8000/health
2. **Check frontend**: http://localhost:5173
3. **Check Ollama**: http://localhost:8000/api/ollama/status

## Deactivating Virtual Environment

When you're done, you can deactivate:

```bash
deactivate
```

But you'll need to activate it again next time you work on the backend.
