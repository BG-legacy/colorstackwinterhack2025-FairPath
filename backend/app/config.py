"""
Config stuff - loading env vars and setting defaults
I'm using pydantic-settings to handle this, makes it easier
"""
from pydantic_settings import BaseSettings
from pydantic import ConfigDict, field_validator, computed_field, Field
from typing import List
import json

class Settings(BaseSettings):
    # OpenAI key - required for AI features
    OPENAI_API_KEY: str = ""
    
    # OpenAI model to use
    OPENAI_MODEL: str =  "gpt-4o-mini" # Model name for OpenAI API calls (gpt-4o-mini, gpt-4o, gpt-3.5-turbo)
    
    # Server config
    PORT: int = 8000
    ENV_MODE: str = "development"  # development, production, testing
    
    # CORS - allowing localhost and common frontend ports
    # Add your frontend URL here or in .env
    # Can be set as JSON array or comma-separated string
    # Stored as string to prevent pydantic-settings from trying to parse as JSON automatically
    # The computed field CORS_ORIGINS will parse this and return a List[str]
    _cors_origins_raw: str = Field(default="", validation_alias="CORS_ORIGINS")
    
    @field_validator('_cors_origins_raw', mode='before')
    @classmethod
    def parse_cors_origins_raw(cls, v):
        """Store raw CORS_ORIGINS value as string, handling None and list inputs"""
        if v is None:
            return ""
        if isinstance(v, list):
            # Convert list to comma-separated string
            return ",".join(str(origin) for origin in v)
        return str(v) if v else ""
    
    @computed_field
    @property
    def CORS_ORIGINS(self) -> List[str]:
        """Parse CORS_ORIGINS from JSON string, comma-separated string, or use defaults"""
        default_origins = [
            "https://fair-path.vercel.app",
            "http://localhost:3000",
            "http://localhost:5173",
            "http://localhost:8080",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173",
        ]
        
        # Handle empty or None values
        if not self._cors_origins_raw or not self._cors_origins_raw.strip():
            return default_origins
        
        v = self._cors_origins_raw.strip()
        
        # Try to parse as JSON first (if it looks like JSON)
        if v.startswith('['):
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    # Strip trailing slashes from JSON origins
                    origins = [origin.rstrip('/') if isinstance(origin, str) else str(origin) for origin in parsed]
                    return origins if origins else default_origins
            except (json.JSONDecodeError, ValueError):
                # If JSON parsing fails, fall through to comma-separated parsing
                pass
        
        # Treat as comma-separated string
        # Strip trailing slashes from origins (CORS doesn't accept them)
        origins = [origin.strip().rstrip('/') for origin in v.split(',') if origin.strip()]
        return origins if origins else default_origins
    
    # Database stuff if needed later
    DATABASE_URL: str = "sqlite:///./data/app.db"
    
    # Security settings
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    RATE_LIMIT_PER_DAY: int = 10000
    
    # Request size limits (in bytes)
    MAX_REQUEST_SIZE: int = 1024 * 1024  # 1MB for general requests
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB for file uploads (resumes)
    
    # OpenAI API timeout and retry settings
    OPENAI_TIMEOUT: int = 30  # Timeout in seconds for OpenAI API calls
    OPENAI_MAX_RETRIES: int = 2  # Maximum number of retries for OpenAI API calls
    OPENAI_RETRY_DELAY: float = 1.0  # Initial delay in seconds for retries (exponential backoff)
    
    # Memory optimization: Set to False to disable eager loading at startup (load on first request instead)
    # This is useful for memory-constrained environments like Render free tier
    EAGER_LOAD_MODELS: bool = False  # Default to False to save memory
    
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=True
    )

# creating a singleton instance - I'll use this everywhere
settings = Settings()

