"""
Config stuff - loading env vars and setting defaults
I'm using pydantic-settings to handle this, makes it easier
"""
from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import List
import os

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
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]
    
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

# adding custom origins from env if they exist
# This way you can override in .env without changing code
if os.getenv("CORS_ORIGINS"):
    custom_origins = os.getenv("CORS_ORIGINS").split(",")
    settings.CORS_ORIGINS.extend([origin.strip() for origin in custom_origins])

