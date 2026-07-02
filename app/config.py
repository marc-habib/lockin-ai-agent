"""
Configuration management for LockIn AI.

Loads settings from environment variables with sensible defaults.
Uses pydantic-settings for validation and type safety.
"""

from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # LLM Configuration
    llm_provider: Literal["openai", "anthropic", "google"] = "openai"
    llm_model: str | None = None
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    google_api_key: str | None = None
    
    # Application Settings
    app_env: Literal["development", "production"] = "development"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    database_path: str = "data/lockin.db"
    
    # OpenFoodFacts API
    openfoodfacts_api_url: str = "https://world.openfoodfacts.org/api/v2"
    
    # Cache Settings
    cache_expiry_days: int = 30
    
    # Agent Settings
    max_reasoning_steps: int = 5
    enable_reflection: bool = True
    
    # Server Settings
    port: int = 7860
    host: str = "0.0.0.0"
    
    @property
    def api_key(self) -> str | None:
        """Get the API key for the configured LLM provider."""
        if self.llm_provider == "openai":
            return self.openai_api_key
        elif self.llm_provider == "anthropic":
            return self.anthropic_api_key
        elif self.llm_provider == "google":
            return self.google_api_key
        return None
    
    @property
    def default_model(self) -> str:
        """Get the default model for the configured provider."""
        if self.llm_model:
            return self.llm_model
        
        defaults = {
            "openai": "gpt-4o-mini",
            "anthropic": "claude-3-5-haiku-20241022",
            "google": "gemini-2.0-flash-exp"
        }
        return defaults.get(self.llm_provider, "gpt-4o-mini")
    
    @property
    def database_dir(self) -> Path:
        """Get the database directory path."""
        return Path(self.database_path).parent
    
    @property
    def logs_dir(self) -> Path:
        """Get the logs directory path."""
        return Path("logs")
    
    @property
    def data_dir(self) -> Path:
        """Get the data directory path."""
        return Path("data")
    
    def ensure_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        self.database_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
