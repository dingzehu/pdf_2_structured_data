from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables / .env file."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    gemini_api_key: str
    database_url: str = "postgresql+asyncpg://postgres:password@db:5432/pdf_extractions"
    gemini_model: str = "gemini-2.0-flash"


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance (parsed once, reused everywhere)."""
    return Settings()


settings = get_settings()
