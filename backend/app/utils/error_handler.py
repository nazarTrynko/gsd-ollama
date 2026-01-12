"""Centralized error handling utility."""

from fastapi import HTTPException
from ..core.exceptions import (
    OllamaError,
    OllamaConnectionError,
    OllamaServerError,
    OllamaModelError,
    OllamaConfigError,
    OllamaTimeoutError,
)


def handle_error(error: Exception) -> HTTPException:
    """Convert exceptions to appropriate HTTP exceptions.
    
    Args:
        error: Exception to handle
        
    Returns:
        HTTPException with appropriate status code and message
    """
    # Handle Ollama-specific errors
    if isinstance(error, OllamaConnectionError):
        return HTTPException(
            status_code=503,
            detail={
                "error": str(error),
                "code": "OLLAMA_CONNECTION_ERROR",
                "server_url": getattr(error, 'server_url', None)
            }
        )
    
    if isinstance(error, OllamaServerError):
        return HTTPException(
            status_code=502,
            detail={
                "error": str(error),
                "code": "OLLAMA_SERVER_ERROR",
                "server_url": getattr(error, 'server_url', None),
                "status_code": getattr(error, 'status_code', None)
            }
        )
    
    if isinstance(error, OllamaModelError):
        return HTTPException(
            status_code=400,
            detail={
                "error": str(error),
                "code": "OLLAMA_MODEL_ERROR",
                "model": getattr(error, 'model', None),
                "available_models": getattr(error, 'available_models', None)
            }
        )
    
    if isinstance(error, OllamaConfigError):
        return HTTPException(
            status_code=500,
            detail={
                "error": str(error),
                "code": "OLLAMA_CONFIG_ERROR",
                "config_path": getattr(error, 'config_path', None)
            }
        )
    
    if isinstance(error, OllamaTimeoutError):
        return HTTPException(
            status_code=504,
            detail={
                "error": str(error),
                "code": "OLLAMA_TIMEOUT_ERROR",
                "timeout": getattr(error, 'timeout', None)
            }
        )
    
    if isinstance(error, OllamaError):
        return HTTPException(
            status_code=500,
            detail={
                "error": str(error),
                "code": "OLLAMA_ERROR"
            }
        )
    
    # Handle ValueError (usually validation errors)
    if isinstance(error, ValueError):
        return HTTPException(
            status_code=400,
            detail={
                "error": str(error),
                "code": "VALIDATION_ERROR"
            }
        )
    
    # Handle HTTPException (re-raise as-is)
    if isinstance(error, HTTPException):
        # Convert to standard format if needed
        if isinstance(error.detail, str):
            return HTTPException(
                status_code=error.status_code,
                detail={
                    "error": error.detail,
                    "code": f"HTTP_{error.status_code}"
                }
            )
        return error
    
    # Generic exception handler
    return HTTPException(
        status_code=500,
        detail={
            "error": str(error),
            "code": "INTERNAL_SERVER_ERROR"
        }
    )


def handle_async_error(error: Exception) -> HTTPException:
    """Handle errors in async context (same as handle_error for now).
    
    Args:
        error: Exception to handle
        
    Returns:
        HTTPException with appropriate status code and message
    """
    return handle_error(error)
