"""FastAPI main application."""

import logging
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import projects, roadmap, phases, tasks, codebase, ollama

# Configure logging
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level, logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="GSD Ollama API",
    description="Get Shit Done with Ollama - Spec-driven development system",
    version="0.1.0"
)

logger.info("Starting GSD Ollama API")

# CORS middleware
cors_origins_env = os.getenv("CORS_ORIGINS", "*")
if cors_origins_env == "*":
    allow_origins = ["*"]
else:
    allow_origins = [origin.strip() for origin in cors_origins_env.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info(f"CORS configured with origins: {allow_origins}")

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
    logger.debug("Root endpoint accessed")
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
