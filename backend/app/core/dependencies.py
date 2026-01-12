"""FastAPI dependency injection for shared resources."""

from functools import lru_cache
from fastapi import Depends
from .ollama_client import OllamaClient
from .roadmap_engine import RoadmapEngine
from .phase_planner import PhasePlanner
from .task_executor import TaskExecutor
from .codebase_mapper import CodebaseMapper


@lru_cache()
def get_ollama_client() -> OllamaClient:
    """Get or create Ollama client instance.
    
    Returns:
        OllamaClient instance (singleton)
    """
    return OllamaClient()


def get_roadmap_engine(
    ollama_client: OllamaClient = Depends(get_ollama_client)
) -> RoadmapEngine:
    """Get or create RoadmapEngine instance.
    
    Args:
        ollama_client: Injected Ollama client
        
    Returns:
        RoadmapEngine instance
    """
    return RoadmapEngine(ollama_client)


def get_phase_planner(
    ollama_client: OllamaClient = Depends(get_ollama_client)
) -> PhasePlanner:
    """Get or create PhasePlanner instance.
    
    Args:
        ollama_client: Injected Ollama client
        
    Returns:
        PhasePlanner instance
    """
    return PhasePlanner(ollama_client)


def get_task_executor(
    ollama_client: OllamaClient = Depends(get_ollama_client)
) -> TaskExecutor:
    """Get or create TaskExecutor instance.
    
    Args:
        ollama_client: Injected Ollama client
        
    Returns:
        TaskExecutor instance
    """
    return TaskExecutor(ollama_client)


def get_codebase_mapper(
    ollama_client: OllamaClient = Depends(get_ollama_client)
) -> CodebaseMapper:
    """Get or create CodebaseMapper instance.
    
    Args:
        ollama_client: Injected Ollama client
        
    Returns:
        CodebaseMapper instance
    """
    return CodebaseMapper(ollama_client)
