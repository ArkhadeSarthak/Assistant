import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "AURA AI Backend"
    VERSION: str = "4.5.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # LLM & Weather Settings
    GEMINI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    OPENWEATHER_API_KEY: Optional[str] = None
    DEFAULT_MODEL: str = "gemini-2.5-flash"

    # Upstash Redis Configuration
    UPSTASH_REDIS_REST_URL: Optional[str] = None
    UPSTASH_REDIS_REST_TOKEN: Optional[str] = None

    # Security
    SECRET_KEY: str = "aura-super-secret-jwt-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    # Database & Redis
    DATABASE_URL: str = "sqlite+aiosqlite:///./aura_ai.db"
    REDIS_URL: str = "redis://localhost:6379/0"

    # Storage
    STORAGE_DIR: str = "./storage"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
