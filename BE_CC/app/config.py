from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_collection: str = "news"
    embedding_model: str = "all-MiniLM-L6-v2"
    scrape_interval_minutes: int = 60
    chunk_size: int = 500
    chunk_overlap: int = 50
    database_url: str = "sqlite:///./news.db"
    log_level: str = "INFO"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
