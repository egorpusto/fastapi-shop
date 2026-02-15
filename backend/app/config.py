from functools import lru_cache
from typing import Union

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application settings
    app_name: str = "FastAPI Shop"
    debug: bool = True

    # Database settings
    database_url: str = "postgresql+asyncpg://fashop_user:fashop_password@localhost:5432/fashop_db"

    # Redis settings
    redis_url: str = "redis://default:fashop_redis_pass@localhost:6379/0"
    cache_ttl: int = 300  # Default cache TTL in seconds

    # CORS settings
    cors_origins: Union[str, list[str]] = "http://localhost:5173,http://localhost:3000"

    # Static files
    static_dir: str = "static"
    images_dir: str = "static/images"

    # Pagination
    default_page_size: int = 20
    max_page_size: int = 100

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "extra": "ignore",
    }


@lru_cache()
def get_settings() -> Settings:
    """
    Returns cached settings instance.
    Using lru_cache to avoid reading .env file multiple times.
    """
    return Settings()


settings = get_settings()
