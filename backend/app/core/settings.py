"""Application settings using pydantic-settings."""

import json
from pathlib import Path
from typing import Optional, Dict, Any
from pydantic_settings import BaseSettings, SettingsConfigDict


class OllamaSettings(BaseSettings):
    """Ollama configuration settings."""
    
    # Server settings
    ollama_base_url: str = "http://localhost:11434"
    ollama_timeout: int = 120  # Reduced from 300 to 120 seconds (2 minutes)
    
    # Model settings
    ollama_default_model: str = "llama3.2"
    
    # Retry settings
    ollama_max_attempts: int = 3
    ollama_backoff_ms: int = 1000
    ollama_exponential_backoff: bool = True
    
    # Model parameters (JSON string or will be loaded from config file)
    ollama_model_params: Optional[str] = None
    
    model_config = SettingsConfigDict(
        env_prefix="OLLAMA_",
        case_sensitive=False,
        extra="ignore"
    )
    
    def load_from_json(self, config_path: Optional[Path] = None) -> Dict[str, Any]:
        """Load additional settings from JSON config file.
        
        Args:
            config_path: Path to config file. If None, uses default.
            
        Returns:
            Dictionary with config values
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "config" / "ollama-config.json"
        
        if not config_path.exists():
            return {}
        
        try:
            with open(config_path) as f:
                return json.load(f)
        except (json.JSONDecodeError, Exception):
            return {}


# Global settings instance
_settings: Optional[OllamaSettings] = None


def get_settings() -> OllamaSettings:
    """Get or create settings instance.
    
    Returns:
        OllamaSettings instance
    """
    global _settings
    if _settings is None:
        _settings = OllamaSettings()
    return _settings
