"""FastAPI main application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import projects, roadmap, phases, tasks, codebase, ollama

app = FastAPI(
    title="GSD Ollama API",
    description="Get Shit Done with Ollama - Spec-driven development system",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(ollama.router)
app.include_router(projects.router)
app.include_router(roadmap.router)
app.include_router(phases.router)
app.include_router(tasks.router)
app.include_router(codebase.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "GSD Ollama API",
        "version": "0.1.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
