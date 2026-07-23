"""Application settings loaded from environment variables."""

from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def split_origins(value: str | list[str]) -> list[str]:
    """Normalize comma-separated CORS origins into a list."""
    if isinstance(value, list):
        return value
    return [item.strip() for item in value.split(",") if item.strip()]


class Settings(BaseSettings):
    """Runtime configuration for the application."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "AI-Powered Legal Query Assistant"
    environment: str = "development"
    secret_key: str = Field(..., min_length=16)
    access_token_expire_minutes: int = 120
    database_url: str
    redis_url: str
    indian_kanoon_base_url: str = "https://api.indiankanoon.org"
    indian_kanoon_api_token: str = ""
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    chroma_persist_dir: str = "./chroma_data"
    cors_origins: str = "http://localhost:5173,http://localhost:5174"
    log_level: str = "INFO"
    min_confidence: float = 0.62
    min_citations: int = 1
    max_context_chunks: int = 6
    request_timeout_seconds: float = 20.0
    cache_ttl_seconds: int = 3600

    @property
    def cors_origin_list(self) -> list[str]:
        """Return configured CORS origins as a list for FastAPI middleware."""
        return split_origins(self.cors_origins)


@lru_cache
def get_settings() -> Settings:
    """Return a cached settings instance."""
    return Settings()
