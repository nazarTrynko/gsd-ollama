"""Ollama API endpoints."""

from fastapi import APIRouter, HTTPException
from typing import List
from ..core.ollama_client import OllamaClient
from ..core.exceptions import (
    OllamaConnectionError,
    OllamaServerError,
    OllamaModelError,
)

router = APIRouter(prefix="/api/ollama", tags=["ollama"])

# Global Ollama client instance
ollama_client = OllamaClient()


@router.get("/status")
async def get_status():
    """Get Ollama server status."""
    try:
        connected = ollama_client.check_server()
        models = []
        default_model = ollama_client.default_model
        
        if connected:
            try:
                models = ollama_client.list_models()
            except Exception:
                models = []
        
        return {
            "connected": connected,
            "server_url": ollama_client.base_url,
            "default_model": default_model,
            "models": models
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models")
async def list_models():
    """List available Ollama models."""
    try:
        models = ollama_client.list_models()
        return {
            "models": models,
            "default": ollama_client.default_model
        }
    except OllamaConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except OllamaServerError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
