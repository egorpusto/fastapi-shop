from pydantic_settings import BaseSettings
from typing import List, Union
from functools import lru_cache


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
    cors_origins: Union[List[str], str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]

    # Static files
    static_dir: str = "static"
    images_dir: str = "static/images"

    # Pagination
    default_page_size: int = 20
    max_page_size: int = 100

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    Returns cached settings instance.
    Using lru_cache to avoid reading .env file multiple times.
    """
    return Settings()


settings = Settings()
