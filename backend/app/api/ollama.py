"""Ollama API endpoints."""

from fastapi import APIRouter, HTTPException, Depends
from typing import List
from ..core.ollama_client import OllamaClient
from ..core.dependencies import get_ollama_client
from ..core.cache import get_cache
from ..core.exceptions import (
    OllamaConnectionError,
    OllamaServerError,
    OllamaModelError,
)
from ..utils.error_handler import handle_error

router = APIRouter(prefix="/api/ollama", tags=["ollama"])


@router.get("/status")
async def get_status(
    ollama_client: OllamaClient = Depends(get_ollama_client)
):
    """Get Ollama server status."""
    try:
        connected = await ollama_client.check_server()
        models = []
        default_model = ollama_client.default_model
        
        if connected:
            try:
                # Check cache first (5 minute TTL)
                cache = get_cache()
                models = cache.get("ollama_models", 300.0)
                if models is None:
                    models = await ollama_client.list_models()
                    cache.set("ollama_models", models)
            except Exception:
                models = []
        
        return {
            "connected": connected,
            "server_url": ollama_client.base_url,
            "default_model": default_model,
            "models": models
        }
    except Exception as e:
        raise handle_error(e)


@router.get("/models")
async def list_models(
    ollama_client: OllamaClient = Depends(get_ollama_client)
):
    """List available Ollama models."""
    try:
        # Check cache first (5 minute TTL)
        cache = get_cache()
        models = cache.get("ollama_models", 300.0)
        if models is None:
            models = await ollama_client.list_models()
            cache.set("ollama_models", models)
        return {
            "models": models,
            "default": ollama_client.default_model
        }
    except Exception as e:
        raise handle_error(e)
