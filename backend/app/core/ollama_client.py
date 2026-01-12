"""Ollama Client for GSD Ollama Backend."""

import json
import time
from pathlib import Path
from typing import Optional, Dict, Any, List
import httpx

from .exceptions import (
    OllamaError,
    OllamaServerError,
    OllamaConnectionError,
    OllamaModelError,
    OllamaConfigError,
    OllamaTimeoutError,
)
from .settings import get_settings
import logging

logger = logging.getLogger(__name__)


class OllamaClient:
    """Client for interacting with Ollama API."""
    
    def __init__(self, config_path: Optional[str] = None) -> None:
        """Initialize Ollama client with configuration.
        
        Args:
            config_path: Path to ollama-config.json. If None, uses default.
        """
        # Load settings from environment variables
        settings = get_settings()
        
        if config_path is None:
            # Default to backend/config/ollama-config.json
            config_path = Path(__file__).parent.parent.parent / "config" / "ollama-config.json"
        else:
            config_path = Path(config_path)
        
        self.config_path = config_path
        self.config: Dict[str, Any] = self._load_config(settings)
        
        # Use environment variables if set, otherwise use config file
        self.base_url: str = settings.ollama_base_url or self.config.get('server', {}).get('baseUrl', 'http://localhost:11434')
        self.default_model: str = settings.ollama_default_model or self.config.get('defaultModel', 'llama3.2')
        
    def _load_config(self, settings) -> Dict[str, Any]:
        """Load and validate configuration from JSON file (fallback if env vars not set).
        
        Args:
            settings: Settings instance from pydantic-settings
            
        Returns:
            Configuration dictionary
        """
        # Try to load from JSON file
        json_config = settings.load_from_json(self.config_path)
        
        # If JSON file exists and has content, use it
        if json_config:
            return json_config
        
        # Otherwise, build config from settings
        config = {
            'server': {
                'baseUrl': settings.ollama_base_url,
                'timeout': settings.ollama_timeout
            },
            'defaultModel': settings.ollama_default_model,
            'retry': {
                'maxAttempts': settings.ollama_max_attempts,
                'backoffMs': settings.ollama_backoff_ms,
                'exponentialBackoff': settings.ollama_exponential_backoff
            },
            'models': {}
        }
        
        return config
    
    def _get_model_params(self, model: str) -> Dict[str, Any]:
        """Get parameters for a specific model."""
        models = self.config.get('models', {})
        if model in models:
            return models[model].get('parameters', {})
        return {}
    
    async def check_server(self) -> bool:
        """Check if Ollama server is running.
        
        Returns:
            True if server is accessible, False otherwise.
        """
        logger.debug(f"Checking Ollama server at {self.base_url}")
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                response.raise_for_status()
                logger.debug("Ollama server is accessible")
                return True
        except (httpx.RequestError, httpx.HTTPStatusError, Exception) as e:
            logger.warning(f"Ollama server check failed: {e}")
            return False
    
    async def list_models(self) -> List[str]:
        """List available models.
        
        Returns:
            List of model names.
            
        Raises:
            OllamaConnectionError: If server is not accessible
            OllamaServerError: If server returns an error
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                response.raise_for_status()
                data = response.json()
                models = [model['name'] for model in data.get('models', [])]
                return models
        except httpx.ConnectError as e:
            raise OllamaConnectionError(
                f"Cannot connect to Ollama server at {self.base_url}. "
                f"Is the server running? Start it with: ollama serve",
                server_url=self.base_url
            ) from e
        except httpx.TimeoutException as e:
            raise OllamaTimeoutError(
                f"Request to Ollama server timed out after 10 seconds.",
                timeout=10.0
            ) from e
        except httpx.HTTPStatusError as e:
            raise OllamaServerError(
                f"Ollama server returned an error: {e}",
                server_url=self.base_url,
                status_code=e.response.status_code
            ) from e
        except httpx.RequestError as e:
            raise OllamaServerError(
                f"Failed to list models from Ollama server: {e}",
                server_url=self.base_url
            ) from e
    
    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        stream: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate response from Ollama.
        
        Args:
            prompt: The user prompt.
            model: Model name. If None, uses default.
            system_prompt: Optional system prompt.
            stream: Whether to stream the response.
            **kwargs: Additional parameters (temperature, etc.)
        
        Returns:
            Dictionary with 'response', 'model', 'tokens', etc.
        """
        if model is None:
            model = self.default_model
        
        logger.info(f"Generating response with model: {model}")
        
        # Check server
        if not await self.check_server():
            raise OllamaConnectionError(
                f"Ollama server is not running at {self.base_url}. "
                "Start the server with: ollama serve",
                server_url=self.base_url
            )
        
        # Build full prompt
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        
        # Get model parameters
        model_params = self._get_model_params(model)
        
        # Merge parameters (kwargs override config)
        params = {**model_params, **kwargs}
        
        # Build request body
        body = {
            "model": model,
            "prompt": full_prompt,
            "stream": stream,
            "options": params
        }
        
        # Get timeout from config
        timeout = self.config.get('server', {}).get('timeout', 300)
        
        # Make request with retry logic
        retry_config = self.config.get('retry', {})
        max_attempts = retry_config.get('maxAttempts', 3)
        backoff_ms = retry_config.get('backoffMs', 1000)
        exponential = retry_config.get('exponentialBackoff', True)
        
        last_error = None
        
        for attempt in range(max_attempts):
            try:
                if attempt > 0:
                    wait_time = backoff_ms
                    if exponential:
                        wait_time = backoff_ms * (2 ** attempt)
                    import asyncio
                    await asyncio.sleep(wait_time / 1000.0)
                
                async with httpx.AsyncClient(timeout=float(timeout)) as client:
                    response = await client.post(
                        f"{self.base_url}/api/generate",
                        json=body
                    )
                    response.raise_for_status()
                    data = response.json()
                
                # Check for model errors in response
                if 'error' in data:
                    error_msg = data.get('error', 'Unknown error')
                    if 'model' in error_msg.lower() or 'not found' in error_msg.lower():
                        available_models = []
                        try:
                            available_models = await self.list_models()
                        except Exception:
                            pass
                        raise OllamaModelError(
                            f"Model error: {error_msg}",
                            model=model,
                            available_models=available_models
                        )
                    else:
                        raise OllamaServerError(
                            f"Ollama server error: {error_msg}",
                            server_url=self.base_url
                        )
                
                result = {
                    "response": data.get('response', ''),
                    "model": model,
                    "tokens": {
                        "prompt": data.get('prompt_eval_count', 0),
                        "completion": data.get('eval_count', 0),
                        "total": data.get('prompt_eval_count', 0) + data.get('eval_count', 0)
                    },
                    "done": data.get('done', True)
                }
                logger.info(f"Generation complete. Tokens used: {result['tokens']['total']}")
                return result
            except OllamaModelError:
                # Don't retry model errors
                raise
            except httpx.ConnectError as e:
                last_error = OllamaConnectionError(
                    f"Cannot connect to Ollama server at {self.base_url}. "
                    f"Is the server running? Start it with: ollama serve",
                    server_url=self.base_url
                )
            except httpx.TimeoutException as e:
                last_error = OllamaTimeoutError(
                    f"Request to Ollama server timed out after {timeout} seconds.",
                    timeout=float(timeout)
                )
            except httpx.HTTPStatusError as e:
                status_code = e.response.status_code
                if status_code == 404:
                    # Model not found
                    available_models = []
                    try:
                        available_models = await self.list_models()
                    except Exception:
                        pass
                    raise OllamaModelError(
                        f"Model '{model}' not found on Ollama server",
                        model=model,
                        available_models=available_models
                    )
                last_error = OllamaServerError(
                    f"Ollama server returned HTTP error: {e}",
                    server_url=self.base_url,
                    status_code=status_code
                )
            except httpx.RequestError as e:
                last_error = OllamaServerError(
                    f"Request to Ollama server failed: {e}",
                    server_url=self.base_url
                )
        
        # All retries exhausted
        raise OllamaError(
            f"Failed to generate response after {max_attempts} attempts. "
            f"Last error: {last_error}"
        ) from last_error
