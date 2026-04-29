"""Backend configuration settings."""
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings from environment."""

    # API Keys
    deepseek_api_key: str = ""
    openai_api_key: str = ""

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # MinIO
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "yaeteaching"

    # App
    app_name: str = "YaeTeaching API"
    debug: bool = False

    class Config:
        env_file = ".env"


settings = Settings()