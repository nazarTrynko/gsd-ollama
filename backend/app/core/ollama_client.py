"""Ollama Client for GSD Ollama Backend."""

import json
import time
from pathlib import Path
from typing import Optional, Dict, Any, List
import requests

from .exceptions import (
    OllamaError,
    OllamaServerError,
    OllamaConnectionError,
    OllamaModelError,
    OllamaConfigError,
    OllamaTimeoutError,
)


class OllamaClient:
    """Client for interacting with Ollama API."""
    
    def __init__(self, config_path: Optional[str] = None) -> None:
        """Initialize Ollama client with configuration.
        
        Args:
            config_path: Path to ollama-config.json. If None, uses default.
        """
        if config_path is None:
            # Default to backend/config/ollama-config.json
            config_path = Path(__file__).parent.parent.parent / "config" / "ollama-config.json"
        else:
            config_path = Path(config_path)
        
        self.config_path = config_path
        self.config: Dict[str, Any] = self._load_config()
        self.base_url: str = self.config['server']['baseUrl']
        self.default_model: str = self.config.get('defaultModel', 'llama3.2')
        
    def _load_config(self) -> Dict[str, Any]:
        """Load and validate configuration from JSON file."""
        try:
            if not self.config_path.exists():
                raise OllamaConfigError(
                    f"Configuration file not found: {self.config_path}",
                    config_path=str(self.config_path)
                )
            
            with open(self.config_path) as f:
                config = json.load(f)
            
            # Basic validation
            if 'server' not in config or 'baseUrl' not in config.get('server', {}):
                raise OllamaConfigError(
                    "Invalid configuration: missing 'server.baseUrl'",
                    config_path=str(self.config_path)
                )
            
            return config
        except json.JSONDecodeError as e:
            raise OllamaConfigError(
                f"Invalid JSON in config file: {e}",
                config_path=str(self.config_path)
            ) from e
        except Exception as e:
            if isinstance(e, OllamaConfigError):
                raise
            raise OllamaConfigError(
                f"Failed to load config: {e}",
                config_path=str(self.config_path)
            ) from e
    
    def _get_model_params(self, model: str) -> Dict[str, Any]:
        """Get parameters for a specific model."""
        models = self.config.get('models', {})
        if model in models:
            return models[model].get('parameters', {})
        return {}
    
    def check_server(self) -> bool:
        """Check if Ollama server is running.
        
        Returns:
            True if server is accessible, False otherwise.
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5
            )
            response.raise_for_status()
            return True
        except (requests.RequestException, Exception):
            return False
    
    def list_models(self) -> List[str]:
        """List available models.
        
        Returns:
            List of model names.
            
        Raises:
            OllamaConnectionError: If server is not accessible
            OllamaServerError: If server returns an error
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            models = [model['name'] for model in data.get('models', [])]
            return models
        except requests.exceptions.ConnectionError as e:
            raise OllamaConnectionError(
                f"Cannot connect to Ollama server at {self.base_url}. "
                f"Is the server running? Start it with: ollama serve",
                server_url=self.base_url
            ) from e
        except requests.exceptions.Timeout as e:
            raise OllamaTimeoutError(
                f"Request to Ollama server timed out after 10 seconds.",
                timeout=10.0
            ) from e
        except requests.exceptions.HTTPError as e:
            raise OllamaServerError(
                f"Ollama server returned an error: {e}",
                server_url=self.base_url,
                status_code=e.response.status_code if hasattr(e, 'response') else None
            ) from e
        except requests.RequestException as e:
            raise OllamaServerError(
                f"Failed to list models from Ollama server: {e}",
                server_url=self.base_url
            ) from e
    
    def generate(
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
        
        # Check server
        if not self.check_server():
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
                    time.sleep(wait_time / 1000.0)
                
                response = requests.post(
                    f"{self.base_url}/api/generate",
                    json=body,
                    timeout=timeout
                )
                response.raise_for_status()
                data = response.json()
                
                # Check for model errors in response
                if 'error' in data:
                    error_msg = data.get('error', 'Unknown error')
                    if 'model' in error_msg.lower() or 'not found' in error_msg.lower():
                        available_models = []
                        try:
                            available_models = self.list_models()
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
                return result
            except OllamaModelError:
                # Don't retry model errors
                raise
            except requests.exceptions.ConnectionError as e:
                last_error = OllamaConnectionError(
                    f"Cannot connect to Ollama server at {self.base_url}. "
                    f"Is the server running? Start it with: ollama serve",
                    server_url=self.base_url
                )
            except requests.exceptions.Timeout as e:
                last_error = OllamaTimeoutError(
                    f"Request to Ollama server timed out after {timeout} seconds.",
                    timeout=float(timeout)
                )
            except requests.exceptions.HTTPError as e:
                status_code = e.response.status_code if hasattr(e, 'response') else None
                if status_code == 404:
                    # Model not found
                    available_models = []
                    try:
                        available_models = self.list_models()
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
            except requests.RequestException as e:
                last_error = OllamaServerError(
                    f"Request to Ollama server failed: {e}",
                    server_url=self.base_url
                )
        
        # All retries exhausted
        raise OllamaError(
            f"Failed to generate response after {max_attempts} attempts. "
            f"Last error: {last_error}"
        ) from last_error
