"""Custom exception classes for GSD Ollama."""


class OllamaError(Exception):
    """Base exception for all Ollama-related errors."""
    pass


class OllamaServerError(OllamaError):
    """Raised when Ollama server is unavailable or returns an error."""
    
    def __init__(self, message: str, server_url: str = None, status_code: int = None):
        super().__init__(message)
        self.server_url = server_url
        self.status_code = status_code


class OllamaConnectionError(OllamaError):
    """Raised when connection to Ollama server fails."""
    
    def __init__(self, message: str, server_url: str = None):
        super().__init__(message)
        self.server_url = server_url


class OllamaModelError(OllamaError):
    """Raised when model-related errors occur."""
    
    def __init__(self, message: str, model: str = None, available_models: list = None):
        super().__init__(message)
        self.model = model
        self.available_models = available_models


class OllamaConfigError(OllamaError):
    """Raised when configuration errors occur."""
    
    def __init__(self, message: str, config_path: str = None):
        super().__init__(message)
        self.config_path = config_path


class OllamaTimeoutError(OllamaError):
    """Raised when request times out."""
    
    def __init__(self, message: str, timeout: float = None):
        super().__init__(message)
        self.timeout = timeout
