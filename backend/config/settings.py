"""Backend configuration settings."""
from pydantic_settings import BaseSettings, SettingsConfigDict


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

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()