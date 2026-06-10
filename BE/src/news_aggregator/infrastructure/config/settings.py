from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = Field(
        default="postgresql+asyncpg://news:news@localhost:5432/news_aggregator",
        alias="DATABASE_URL",
    )
    embedding_model: str = Field(default="all-MiniLM-L6-v2", alias="EMBEDDING_MODEL")
    sync_interval_minutes: int = Field(default=15, alias="SYNC_INTERVAL_MINUTES")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    search_similarity_threshold: float = Field(default=0.5, alias="SEARCH_SIMILARITY_THRESHOLD")
    chunk_size: int = Field(default=500, alias="CHUNK_SIZE")
    chunk_overlap: int = Field(default=100, alias="CHUNK_OVERLAP")
    search_max_results: int = Field(default=20, alias="SEARCH_MAX_RESULTS")
    embedding_dimension: int = Field(default=384, alias="EMBEDDING_DIMENSION")


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()
